#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\damage.py
import logging
import math
from behaviors.tasks import Task
from behaviors.utility.ballparks import get_distance_between
from dogma.attributes import health
from dogma.const import attributeEmDamage, attributeKineticDamage, attributeThermalDamage, attributeExplosiveDamage
logger = logging.getLogger(__name__)

class SetArmorRatio(Task):

    def OnEnter(self):
        health.SetArmorRatio(self.context.dogmaLM, self.context.myItemId, self.attributes.armorRatio)
        self.SetStatusToSuccess()


class SetShieldRatio(Task):

    def OnEnter(self):
        health.SetShieldRatio(self.context.dogmaLM, self.context.myItemId, self.attributes.shieldRatio)
        self.SetStatusToSuccess()


class SetStructureRatio(Task):

    def OnEnter(self):
        health.SetStructureRatio(self.context.dogmaLM, self.context.myItemId, self.attributes.structureRatio)
        self.SetStatusToSuccess()


class SetArmorRatioForItem(Task):

    def OnEnter(self):
        itemId = self.GetLastBlackboardValue(self.attributes.itemIdAddress)
        if itemId:
            health.SetArmorRatio(self.context.dogmaLM, itemId, self.attributes.armorRatio)
        self.SetStatusToSuccess()


class SetShieldRatioForItem(Task):

    def OnEnter(self):
        itemId = self.GetLastBlackboardValue(self.attributes.itemIdAddress)
        if itemId:
            health.SetShieldRatio(self.context.dogmaLM, itemId, self.attributes.shieldRatio)
        self.SetStatusToSuccess()


class SetStructureRatioForItem(Task):

    def OnEnter(self):
        itemId = self.GetLastBlackboardValue(self.attributes.itemIdAddress)
        if itemId:
            health.SetStructureRatio(self.context.dogmaLM, itemId, self.attributes.structureRatio)
        self.SetStatusToSuccess()


class DealDamageOutsideOfArea(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        ships_in_bubble = self._get_ships_in_same_bubble()
        self._deal_damage_to_ships_in_bubble(ships_in_bubble)

    def _get_ships_in_same_bubble(self):
        return self.context.ballpark.GetShipsInSameBubble(self.context.myItemId)

    def _deal_damage_to_ships_in_bubble(self, ships_in_bubble):
        ships_within_damage_distance = self._get_ships_within_damage_distance(ships_in_bubble)
        for ship_id, distance in ships_within_damage_distance:
            damage_multiplier = self._get_damage_based_on_distance(distance)
            self._deal_damage_to_ship(ship_id, damage_multiplier)
            self._show_damage_effect_on_ship(ship_id)

    def _show_damage_effect_on_ship(self, ship_id):
        self.context.ballpark.specialEffects.StartShipEffect(ship_id, 'effects.DrifterControlled', 5000, 0)

    def _get_ships_within_damage_distance(self, ships_in_bubble):
        ships_within_damage_distance = []
        for ship_id in ships_in_bubble:
            distance = get_distance_between(self, self.context.myItemId, ship_id)
            if self.attributes.minDamageDistance < distance:
                ships_within_damage_distance.append((ship_id, distance))

        return ships_within_damage_distance

    def _get_damage_based_on_distance(self, distance):
        distance_from_min = distance - self.attributes.minDamageDistance
        area_distance = self.attributes.maxDamageDistance - self.attributes.minDamageDistance
        return math.pow(math.exp(distance_from_min / area_distance), self.attributes.areaDamageFactor)

    def _deal_damage_to_ship(self, ship_id, damage_multiplier):
        if self.context.ballpark.IsWarping(ship_id):
            logger.debug('Behavior=%s did not deal area damage to item=%s - possibly still in warp', self.behaviorTree.GetBehaviorId(), ship_id)
            return
        damage_amount_by_damage_type = self._get_damage_amount_by_damage_type()
        sm.GetService('dogma').ApplyDamage(None, self.context.myItemId, ship_id, damageMultiplier=damage_multiplier, indirectDogmaLM=self.context.dogmaLM, weaponDamages=damage_amount_by_damage_type)
        logger.debug('Behavior=%s dealing area damage to item=%s with damage multiplier=%s and damage by type=%s', self.behaviorTree.GetBehaviorId(), ship_id, damage_multiplier, damage_amount_by_damage_type)

    def _get_damage_amount_by_damage_type(self):
        return {attributeEmDamage: self.attributes.emDamage,
         attributeKineticDamage: self.attributes.explosiveDamage,
         attributeThermalDamage: self.attributes.kineticDamage,
         attributeExplosiveDamage: self.attributes.thermalDamage}


class DisplayCholesterolField(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        sm.GetService('machoNet').SinglecastBySolarSystemID(self.context.ballpark.solarsystemID, 'OnCholesterolFieldActivated', self.context.myItemId, self._get_distance())

    def _get_distance(self):
        if getattr(self.attributes, 'distanceAddress', None):
            return self.GetLastBlackboardValue(self.attributes.distanceAddress)
        else:
            return self.attributes.defaultDistance
