#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\combatnavigation.py
import random
import math
from behaviors.const.behaviorroles import ROLE_COMMANDER, ROLE_DPS, ROLE_TACKLER
from behaviors.exceptions import BehaviorAuthoringException
from behaviors.tasks import Task
from behaviors.utility.dogmatic import get_my_attribute_value
from ccpProfile import TimedFunction
import logging
from dogma.const import attributeBehaviorCombatOrbitRange
logger = logging.getLogger(__name__)
DEFAULT_COMBAT_ORBIT_RANGE = 10000.0
DEFAULT_COMBAT_ATTACK_RANGE = 30000.0
COMBAT_ATTACK_RANGE_FACTOR = 3.0
DEFAULT_MAXIMUM_ORBIT_RANGE = 100000.0
FALLOFF_ORBIT_DISTANCE_FACTOR = 0.25
MISSILE_RANGE_ORBIT_DISTANCE_FACTOR = 0.75
OPTIMAL_ORBIT_DISTANCE_FACTOR = 0.75
COMBAT_WARP_AT_DISTANCE_FACTOR = 50000.0
DEFAULT_ANCHOR_ORBIT_RANGE = (1000.0, 4000.0)
FLEET_NAVIGATION_BY_ROLE = {ROLE_DPS: {'orbitTarget': ROLE_COMMANDER,
            'orbitRange': DEFAULT_ANCHOR_ORBIT_RANGE},
 ROLE_TACKLER: {'orbitTarget': 'target'}}

class GetCombatOrbitAndAttackRange(Task):

    @TimedFunction('behaviors::actions::combatnavigation::GetCombatOrbitRange::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        if not self._should_calculate_orbit_and_attack_range():
            return
        orbit_range, attack_range = self._get_desired_orbit_and_attack_range()
        if orbit_range > attack_range:
            raise BehaviorAuthoringException('Behavior=%s for entity_type=%s has less attack range than orbit range', self.behaviorTree.GetBehaviorId(), self.context.mySlimItem.typeID)
        self.SendBlackboardValue(self.attributes.orbitRangeAddress, orbit_range)
        self.SendBlackboardValue(self.attributes.attackRangeAddress, attack_range)

    def _should_calculate_orbit_and_attack_range(self):
        return self.GetLastBlackboardValue(self.attributes.orbitRangeAddress) is None

    def _get_desired_orbit_and_attack_range(self):
        behavior_orbit_range = getattr(self.attributes, 'orbitRange', 0)
        attack_range = getattr(self.attributes, 'attackRange', 0)
        if behavior_orbit_range and attack_range:
            return (behavior_orbit_range, attack_range)
        calculated_orbit_range, calculated_attack_range = self._calculate_orbit_and_attack_range()
        if not calculated_orbit_range and not behavior_orbit_range:
            raise BehaviorAuthoringException('Behavior=%s for entity_type=%s missing orbitRange or optimalRange from address, might be missing task=GetMyMinOptimalAndFalloff', self.behaviorTree.GetBehaviorId(), self.context.mySlimItem.typeID)
        orbit_range = behavior_orbit_range or min(calculated_orbit_range, DEFAULT_MAXIMUM_ORBIT_RANGE)
        dogma_orbit_range = get_my_attribute_value(self, attributeBehaviorCombatOrbitRange)
        if dogma_orbit_range > 0:
            orbit_range = min(orbit_range, dogma_orbit_range)
        return (orbit_range, attack_range or calculated_attack_range)

    def _calculate_orbit_and_attack_range(self):
        min_optimal, min_falloff = self._get_min_optimal_and_falloff_from_addresses()
        if not min_falloff:
            orbit_range = min_optimal * OPTIMAL_ORBIT_DISTANCE_FACTOR
            attack_range = min_optimal
        else:
            orbit_range = min_optimal + min_falloff * FALLOFF_ORBIT_DISTANCE_FACTOR
            attack_range = min_optimal + min_falloff * COMBAT_ATTACK_RANGE_FACTOR
        return (orbit_range or DEFAULT_COMBAT_ORBIT_RANGE, attack_range or DEFAULT_COMBAT_ATTACK_RANGE)

    def _get_min_optimal_and_falloff_from_addresses(self):
        min_optimal = min_falloff = 0.0
        if self.HasAttribute('minOptimalAddress'):
            min_optimal = self.GetLastBlackboardValue(self.attributes.minOptimalAddress)
        if self.HasAttribute('minFalloffAddress'):
            min_falloff = self.GetLastBlackboardValue(self.attributes.minFalloffAddress)
        return (min_optimal, min_falloff)


class GetTargetToOrbit(Task):

    @TimedFunction('behaviors::actions::combatnavigation::GetTargetToOrbit::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        commanderId = self.GetLastBlackboardValue(self.attributes.commanderAddress)
        if self._ShouldOrbitCommander(commanderId):
            self.SendBlackboardValue(self.attributes.orbitTargetAddress, commanderId)
        else:
            combatTargetId = self.GetLastBlackboardValue(self.attributes.combatTargetAddress)
            self.SendBlackboardValue(self.attributes.orbitTargetAddress, combatTargetId)

    def _ShouldOrbitCommander(self, commanderId):
        if commanderId is None:
            return False
        if self.context.myItemId == commanderId:
            return False
        role = self.GetLastBlackboardValue(self.attributes.roleAddress)
        if not role:
            return False
        if role not in FLEET_NAVIGATION_BY_ROLE or FLEET_NAVIGATION_BY_ROLE[role]['orbitTarget'] != ROLE_COMMANDER:
            return False
        return True


class GetFleetCombatOrbitRangeByRole(Task):

    @TimedFunction('behaviors::actions::combatnavigation::GetFleetCombatOrbitAndAttackRangeByRole::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        orbitRange = self._GetCommanderOrbitRangeByRole()
        self.SendBlackboardValue(self.attributes.orbitRangeAddress, orbitRange)

    def _GetCommanderOrbitRangeByRole(self):
        role = self.GetLastBlackboardValue(self.attributes.roleAddress)
        if role in FLEET_NAVIGATION_BY_ROLE:
            minOrbitRange, maxOrbitRange = FLEET_NAVIGATION_BY_ROLE[role]['orbitRange']
        else:
            minOrbitRange, maxOrbitRange = DEFAULT_ANCHOR_ORBIT_RANGE
        return random.randrange(minOrbitRange, maxOrbitRange)


class GetCombatWarpAtDistance(Task):

    @TimedFunction('behaviors::actions::combatnavigation::GetCombatWarpAtDistance::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        if self._already_has_combat_warp_at_distance():
            return
        combat_warp_at_distance = self._get_combat_warp_at_distance()
        self.SendBlackboardValue(self.attributes.combatWarpAtDistanceAddress, combat_warp_at_distance)

    def _already_has_combat_warp_at_distance(self):
        return self.GetLastBlackboardValue(self.attributes.combatWarpAtDistanceAddress) is not None

    def _get_combat_warp_at_distance(self):
        combat_orbit_range = self._get_combat_orbit_range()
        if not combat_orbit_range:
            raise BehaviorAuthoringException('Behavior=%s for entity=%s has no combat_orbit_range for GetCombatWarpAtDistance' % (self.behaviorTree.GetBehaviorId(), self.context.myItemId))
        factor = 1.0 - 1.0 / math.exp((combat_orbit_range / COMBAT_WARP_AT_DISTANCE_FACTOR) ** 2.0)
        return factor * combat_orbit_range

    def _get_combat_orbit_range(self):
        return self.GetLastBlackboardValue(self.attributes.combatOrbitRangeAddress)
