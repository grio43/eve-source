#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\entity.py
from ballpark.helpers.aggression import get_kill_owner_id
from ccpProfile import TimedFunction
from collections import defaultdict
import math
import evetypes
from ballpark.entities.entitywrapper import EntityWrapper
from ballpark.messenger.const import MESSAGE_ON_BALL_MODE_CHANGED, MESSAGE_ON_ADDITIONAL_LOOT_REMOVED
from ballpark.messenger.const import MESSAGE_ON_UNSPAWNED_WITH_ADDITIONAL_LOOT
from ballpark.messenger.const import MESSAGE_ON_DROPPED_ADDITIONAL_LOOT
from ballpark.warpDisruptionBalls import IsBallIntersectingAnyWarpDisruptionField
from inventorycommon.const import groupSolarSystem, ownerUnknown
import logging
from ballpark.const import DESTINY_MODE_WARP
from eveexceptions import UserError
from inventorycommon.const import ownerNone
from inventorycommon.util import IsNPC
from spacecomponents.common.helper import HasCargoBayComponent
logger = logging.getLogger(__name__)
INVULNERABLE_LABEL = 'BehaviorWarp'

class NPCWarpError(Exception):
    pass


class NpcWarpScrambledError(NPCWarpError):
    pass


class NpcWarpBubbledError(NPCWarpError):
    pass


class NpcWarpPathBubbledError(NPCWarpError):
    pass


class BehaviorEntity(EntityWrapper):
    __destiny_ball_class_id__ = 58

    def DoSetup(self, entitySettings):
        self.additionalLoot = defaultdict(int)
        self.additionalLootTables = []

    def OnAddedToPark(self):
        pass

    @TimedFunction('behaviors::entity::BehaviorEntity::NPCWarpTo')
    def NPCWarpTo(self, destination, jitterRadius = 20000, warpAtRange = 0.0, warpSpeed = 6):
        if hasattr(self, 'ballpark') and self.ballpark is not None:
            if self.ballpark.IsWarpScrambled(self.id):
                raise NpcWarpScrambledError('Warp Scrambled')
            if self.mode == DESTINY_MODE_WARP:
                raise NPCWarpError('Already Warping')
            destination = self.ballpark.AdjustDstByJitter(destination, jitterRadius)
            if IsBallIntersectingAnyWarpDisruptionField(self.ballpark, self.id):
                raise NpcWarpBubbledError('Warp bubble disruptor')
            try:
                destination = self.ballpark.ApplyWarpDisruptors(self.id, self.GetPosition(), destination, warpAtRange)
            except UserError:
                raise NpcWarpPathBubbledError('Warp path too short due to bubble disruptor')

            self.ballpark.bubbleKeepAliveController.add_bubble_keep_alive_ball_at_coordinates(self.id, destination)
            self.ballpark.EntityWarpStart(self.id, pos=destination, makeItReal=True, notWarpingException=NPCWarpError, minRange=warpAtRange, warpSpeed=warpSpeed)
        else:
            raise NPCWarpError('No ballpark')

    @TimedFunction('behaviors::entity::BehaviorEntity::NPCEndWarp')
    def NPCEndWarp(self):
        if hasattr(self, 'ballpark') and self.ballpark is not None:
            self.ballpark.bubbleKeepAliveController.remove_bubble_keep_alive_ball(self.id)
        else:
            raise NPCWarpError()

    def _GetKillOwner(self):
        return get_kill_owner_id(self.ballpark, self.id)

    def _GetWreckID(self, item):
        return evetypes.GetWreckTypeIDOrNone(item.typeID)

    def _GetShipAccess(self, item):
        shipAccess = self.ballpark.broker.ship.GetShipAccessEx(item.locationID, groupSolarSystem)
        shipAccess.Bind()
        return shipAccess

    def OnExplode(self):
        item = self.ballpark.inventory2.GetItem(self.id)
        if HasCargoBayComponent(item.typeID):
            logger.debug('Entity %s of type %s has cargo bay component which is managing dropped loot.', self.id, item.typeID)
            return
        offenderOwnerID = self._GetKillOwner()
        wreckTypeID = self._GetWreckID(item)
        shipAccess = self._GetShipAccess(item)
        itemList = self.GetLootForEntity(item.typeID, item.ownerID)
        if wreckTypeID is not None:
            shipAccess.Jettison_DropWreck_Ex(offenderOwnerID, self.id, item.typeID, self.GetPosition(), wreckTypeID, itemList, npcLoot=True)
        super(BehaviorEntity, self).OnExplode()

    def OnUnspawn(self):
        additionalLoot = self.GetAdditionalLoot()
        if additionalLoot:
            self.SendMessage(self.id, MESSAGE_ON_UNSPAWNED_WITH_ADDITIONAL_LOOT, additionalLoot)

    def DoModeChange(self, oldMode, newMode):
        self.SendMessage(self.id, MESSAGE_ON_BALL_MODE_CHANGED, oldMode, newMode)
        if oldMode == DESTINY_MODE_WARP:
            self.NPCEndWarp()

    def _GetAdditionalLootForWreck(self):
        additionalLoot = []
        for lootTableId in self.additionalLootTables:
            additionalLoot.extend(self.ballpark.broker.lootSvc.GetLootFromTable(lootTableId))

        for typeId, amount in self.additionalLoot.iteritems():
            additionalLoot.append((typeId, amount, None))

        return additionalLoot

    def AddTypeAndAmountToAdditionalLoot(self, typeId, amount = 1, overload = True):
        if not overload:
            amount = self._GetAvailableAmountForTypeInAdditionalLoot(typeId, amount)
        self.additionalLoot[typeId] += amount

    def RemoveTypeFromAdditionalLoot(self, typeId):
        if typeId in self.additionalLoot:
            del self.additionalLoot[typeId]

    def HasTypeInAdditionalLoot(self, typeId):
        return typeId in self.additionalLoot

    def GetLootForEntity(self, typeId, ownerId):
        itemDict = self.ballpark.broker.lootSvc.GetLootForEntity(typeId, self.id, ownerId)
        itemList = []
        for typeID, pickList in itemDict.iteritems():
            for quantity, customInfo in pickList:
                itemList.append((typeID, quantity, customInfo))

        additionalLoot = self._GetAdditionalLootForWreck()
        if additionalLoot:
            self.SendMessage(self.id, MESSAGE_ON_DROPPED_ADDITIONAL_LOOT, {(typeId, amount) for typeId, amount, _ in additionalLoot})
        itemList.extend(additionalLoot)
        return itemList

    def AddLootTableToAdditionalLoot(self, lootTableId):
        self.additionalLootTables.append(lootTableId)

    def HasLootTableInAdditionalLoot(self, lootTableId):
        return lootTableId in self.additionalLootTables

    def HasEnoughAdditionalCargoCapacityForType(self, typeId, quantity = 1):
        requiredCargoCapacity = evetypes.GetAttributeForType(typeId, 'volume') * quantity
        return self.GetAvailableAdditionalCargoCapacity() - requiredCargoCapacity >= 0

    def GetAvailableAdditionalCargoCapacity(self):
        selfTypeId = self.ballpark.inventory2.GetItem(self.id).typeID
        cargoCapacity = evetypes.GetAttributeForType(selfTypeId, 'capacity')
        usedCargoCapacity = self._GetUsedAdditionalCargoCapacity()
        return cargoCapacity - usedCargoCapacity

    def _GetUsedAdditionalCargoCapacity(self):
        usedCapacity = 0
        for typeId, amount in self.additionalLoot.iteritems():
            usedCapacity += evetypes.GetAttributeForType(typeId, 'volume') * amount

        return usedCapacity

    def _GetAvailableAmountForTypeInAdditionalLoot(self, typeId, amount):
        availabeCargoCapacity = self.GetAvailableAdditionalCargoCapacity()
        totalVolumeNeeded = evetypes.GetAttributeForType(typeId, 'volume') * amount
        if availabeCargoCapacity < totalVolumeNeeded:
            return math.floor(amount * (availabeCargoCapacity / totalVolumeNeeded))
        return amount

    def RemoveAdditionalLoot(self):
        additionalLoot = self.additionalLoot.copy()
        self.additionalLoot.clear()
        self.SendMessage(self.id, MESSAGE_ON_ADDITIONAL_LOOT_REMOVED)
        return additionalLoot

    def GetAdditionalLoot(self):
        return self.additionalLoot.copy()
