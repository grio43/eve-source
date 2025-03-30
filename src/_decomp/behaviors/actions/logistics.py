#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\logistics.py
from evemath import get_center_point
from behaviors.blackboards import BlackboardDeletedError
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task
from behaviors.utility.ballparks import get_ball_position, is_ball_in_park, get_distance_between
from behaviors.utility.dogmatic import get_my_attribute_value, is_assistance_disallowed, get_range_falloff_multiplier_at_distance
from behaviors.utility.logistics import get_logistics_priority, get_remote_repair_effect_id, get_damage_state_function_by_effect_id
from behaviors.utility.math import compute_rear_fleet_position, compute_forward_fleet_position
from ccpProfile import TimedFunction
from collections import Counter
from dogma.const import attributeNPCAssistanceRange, effectBehaviorNPCRemoteArmorRepair
from dogma.const import attributeMaxTargetRange, attributeMaxLockedTargets
from dogma.effects.restricted.util import get_effect_max_effective_range_with_falloff
from eveexceptions import UserError
from inventorycommon.const import categoryEntity, categoryDrone, categoryShip
from inventorycommon import const as invConst, WrongInventoryLocation, FakeItemNotHere
import logging
from threadutils.be_nice import be_nice
import uthread2
logger = logging.getLogger(__name__)
LOGISTICS_CATEGORIES_TO_CONSIDER = [categoryEntity, categoryShip, categoryDrone]
LOGISTICS_GROUPS_TO_IGNORE = {invConst.groupSpawnContainer,
 invConst.groupSpewContainer,
 invConst.groupBillboard,
 invConst.groupAgentsinSpace,
 invConst.groupCapturePointTower,
 invConst.groupControlBunker,
 invConst.groupLargeCollidableShip,
 invConst.groupLargeCollidableObject,
 invConst.groupLargeCollidableStructure,
 invConst.groupTemporaryCollidableStructure,
 invConst.groupMissionContainer,
 invConst.groupTemporaryCloud,
 invConst.groupSentryGun,
 invConst.groupIndustrialSupportFacility}
LOGISTICS_EFFECTS = (effectBehaviorNPCRemoteArmorRepair,)

class SelectDesiredAnchorPosition(Task, GroupTaskMixin):

    @TimedFunction('behaviors::actions::logistics::SelectDesiredAnchorPosition::OnEnter')
    def OnEnter(self):
        friendlyPositionList, hostilePositionList = self.CollectFriendlyAndHostilePositions()
        try:
            if not hostilePositionList:
                desiredPosition = get_center_point(friendlyPositionList)
            else:
                desiredPosition = self.ComputeDesiredPosition(friendlyPositionList, hostilePositionList)
            self.SendBlackboardValue(self.attributes.desiredPositionAddress, tuple(desiredPosition))
            self.SetStatusToSuccess()
        except ValueError:
            self.SendBlackboardValue(self.attributes.desiredPositionAddress, None)
            self.SetStatusToFailed()

    @TimedFunction('behaviors::actions::logistics::SelectDesiredAnchorPosition::OnEnter::CollectFriendlyAndHostilePositions')
    def CollectFriendlyAndHostilePositions(self):
        ballIds = self.GetBallIdsToConsider()
        friendlyPositionList = []
        hostilePositionList = []
        slims = self.context.ballpark.slims
        balls = self.context.ballpark.balls
        for itemId in ballIds:
            self.ClassifyItemIdAndCollect(itemId, balls, slims, friendlyPositionList, hostilePositionList)

        return (friendlyPositionList, hostilePositionList)

    def ClassifyItemIdAndCollect(self, itemId, balls, slims, friendlyPositionList, hostilePositionList):
        slimItem = slims.get(itemId)
        if not slimItem:
            return
        if slimItem.categoryID not in LOGISTICS_CATEGORIES_TO_CONSIDER:
            return
        if slimItem.groupID in LOGISTICS_GROUPS_TO_IGNORE:
            return
        if slimItem.ownerID in self.attributes.friendlyOwners:
            ball = balls[itemId]
            friendlyPositionList.append((ball.x, ball.y, ball.z))
        if slimItem.ownerID in self.attributes.hostileOwners:
            ball = balls[itemId]
            hostilePositionList.append((ball.x, ball.y, ball.z))

    def GetBallIdsToConsider(self):
        ballpark = self.context.ballpark
        ballIds = [ ballId for ballId in ballpark.bubbles[ballpark.balls[self.context.myItemId].newBubbleId] if ballId > 0 ]
        return ballIds

    @TimedFunction('behaviors::actions::logistics::SelectDesiredAnchorPosition::OnEnter::ComputeDesiredPosition')
    def ComputeDesiredPosition(self, friendlyPositionList, hostilePositionList):
        friendlyCentroid = get_center_point(friendlyPositionList)
        hostileCentroid = get_center_point(hostilePositionList)
        logisticsRange = self.GetLogisticsRange()
        desiredRearPosition = compute_rear_fleet_position(friendlyCentroid, hostileCentroid, logisticsRange * self.attributes.proximityFraction)
        return desiredRearPosition

    def GetLogisticsRange(self):
        ranges = self.GetGroupLogisticsRanges()
        if not ranges:
            raise ValueError('no valid logistics range found')
        return min(ranges)

    @TimedFunction('behaviors::actions::logistics::SelectDesiredAnchorPosition::OnEnter::GetGroupLogisticsRanges')
    def GetGroupLogisticsRanges(self):
        ranges = []
        for memberId in self.GetMemberIdList():
            repairRange = self.GetRepairRange(memberId)
            if repairRange > 0:
                ranges.append(repairRange)

        return ranges

    def GetRepairRange(self, memberId):
        return self.context.dogmaLM.GetAttributeValue(memberId, attributeNPCAssistanceRange)


class SelectGroupMemberBasedOnLowestAttributeValue(Task, GroupTaskMixin):

    @TimedFunction('behaviors::actions::logistics::SelectGroupMemberBasedOnLowestAttributeValue::OnEnter')
    def OnEnter(self):
        memberList = self.GetLogisticsMembers()
        if memberList:
            self.SortMemberByAttributeValue(memberList)
            self.SendBlackboardValue(self.attributes.selectedIdAddress, memberList[0])
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    @TimedFunction('behaviors::actions::logistics::SelectGroupMemberBasedOnLowestAttributeValue::SortMemberByAttributeValue')
    def SortMemberByAttributeValue(self, memberList):
        GetAttributeValue = self.context.dogmaLM.GetAttributeValue
        attributeId = self.attributes.attributeId
        memberList.sort(key=lambda memberId: GetAttributeValue(memberId, attributeId))

    @TimedFunction('behaviors::actions::logistics::SelectGroupMemberBasedOnLowestAttributeValue::GetLogisticsMembers')
    def GetLogisticsMembers(self):
        return [ memberId for memberId in self.GetMemberIdList() if self.HasLogisticsEffects(memberId) ]

    def HasLogisticsEffects(self, memberId):
        slimItem = self.context.ballpark.slims.get(memberId)
        if not slimItem:
            return False
        else:
            return self.HasAnyLogisticsEffects(slimItem.typeID)

    def HasAnyLogisticsEffects(self, typeID):
        for effectId in LOGISTICS_EFFECTS:
            if self.HasEffect(typeID, effectId):
                return True

        return False

    def HasEffect(self, typeID, effectId):
        return self.context.dogmaLM.dogmaStaticMgr.TypeHasEffect(typeID, effectId)


class SetRearFleetPosition(Task):

    @TimedFunction('behaviors::actions::logistics::SetRearFleetPosition::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        hostilePosition = self.GetLastBlackboardValue(self.attributes.hostilePositionAddress)
        if not hostilePosition:
            return
        anchorBallId = self.GetLastBlackboardValue(self.attributes.anchorBallIdAddress)
        if not anchorBallId or not is_ball_in_park(self, anchorBallId):
            return
        friendlyPosition = get_ball_position(self, anchorBallId)
        distance = self.GetLastBlackboardValue(self.attributes.distanceAddress)
        rear_position = self.GetTargetPosition(friendlyPosition, hostilePosition, distance)
        self.SendBlackboardValue(self.attributes.targetPositionAddress, rear_position)
        self.SetStatusToSuccess()

    def GetTargetPosition(self, friendlyPosition, hostilePosition, distance):
        return compute_rear_fleet_position(friendlyPosition, hostilePosition, distance)


class SetForwardFleetPosition(SetRearFleetPosition):

    def GetTargetPosition(self, friendlyPosition, hostilePosition, distance):
        return compute_forward_fleet_position(friendlyPosition, hostilePosition, distance)


class PrioritizeLogisticsWatchlist(Task, GroupTaskMixin):

    def __init__(self, attributes = None):
        super(PrioritizeLogisticsWatchlist, self).__init__(attributes=attributes)

    @TimedFunction('behaviors::actions::logistics::PrioritizeLogisticsWatchlist::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        damage_state_function = self.get_damage_state_function()
        if damage_state_function is None:
            return
        watchlist = self.GetLastBlackboardValue(self.attributes.watchlistAddress)
        if watchlist:
            prioritized_watchlist = self._GetPrioritizedWatchlist(watchlist)
        else:
            prioritized_watchlist = []
        self.SendBlackboardValue(self.attributes.prioritizedWatchlistAddress, prioritized_watchlist)

    def get_repair_effect_id(self):
        remote_repair_effect_by_type = self.GetLastBlackboardValue(self.attributes.remoteRepairEffectRegistryAddress)
        if not remote_repair_effect_by_type:
            return None
        most_common = Counter(remote_repair_effect_by_type.values()).most_common(1)[0]
        return most_common[0]

    @TimedFunction('behaviors::actions::logistics::PrioritizeLogisticsWatchlist::_GetPrioritizedWatchlist')
    def _GetPrioritizedWatchlist(self, watchlist):
        repair_effect_id = self.get_repair_effect_id()
        if repair_effect_id is None:
            return []
        get_damage_state = get_damage_state_function_by_effect_id(repair_effect_id)
        prioritized_watchlist = []
        for item_id in watchlist:
            self.try_add_item_with_priority(item_id, prioritized_watchlist, get_damage_state)

        prioritized_watchlist.sort(reverse=True)
        return prioritized_watchlist

    def try_add_item_with_priority(self, item_id, prioritized_watchlist, get_damage_state):
        if not is_ball_in_park(self, item_id):
            return
        if is_assistance_disallowed(self, item_id):
            return
        try:
            priority = get_logistics_priority(self, item_id, get_damage_state)
            prioritized_watchlist.append([priority, item_id])
        except (WrongInventoryLocation,
         FakeItemNotHere,
         ZeroDivisionError,
         BlackboardDeletedError) as e:
            logger.debug('Behavior=%s for group=%s error while getting logistic priority: %s', self.behaviorTree.GetBehaviorId, self.context.myEntityGroupId, e)

    def get_damage_state_function(self):
        if not self.HasContextValue('get_damage_state'):
            remote_repair_effect_id = self.get_repair_effect_id()
            if remote_repair_effect_id is not None:
                self.SetContextValue('get_damage_state', get_damage_state_function_by_effect_id(remote_repair_effect_id))
        return self.GetContextValue('get_damage_state')


class LockPrioritizedWatchlistMembers(Task):

    def __init__(self, attributes = None):
        super(LockPrioritizedWatchlistMembers, self).__init__(attributes=attributes)
        self.is_updating_locks = False

    def _initialize(self):
        if not self.HasContextValue('remote_repair_effect_id'):
            if self.HasAttribute('remoteRepairEffectIdAddress'):
                remote_repair_effect_id = self.GetLastBlackboardValue(self.attributes.remoteRepairEffectIdAddress)
            else:
                remote_repair_effect_id = get_remote_repair_effect_id(self)
            self.SetContextValue('remote_repair_effect_id', remote_repair_effect_id)
        if self._has_combat_target():
            self.SetContextValue('reserved_combat_target_count', 1)
        else:
            self.SetContextValue('reserved_combat_target_count', 0)

    @TimedFunction('behaviors::actions::logistics::LockPrioritizedWatchlistMembers::OnEnter')
    def OnEnter(self):
        self._initialize()
        self.SetStatusToSuccess()
        prioritized_watchlist = self.GetLastBlackboardValue(self.attributes.prioritizedWatchlistAddress)
        if not prioritized_watchlist:
            return
        best_candidates_in_range = self._FilterItemsInTargetingRange(prioritized_watchlist)
        self._UpdateLockedTargets(best_candidates_in_range)

    def _get_effective_range(self):
        return get_effect_max_effective_range_with_falloff(self.context.dogmaLM, self.GetContextValue('remote_repair_effect_id'), self.context.myItemId)

    def get_max_targets(self):
        max_total_targets = int(get_my_attribute_value(self, attributeMaxLockedTargets))
        available_logistic_target_count = max_total_targets - self.GetContextValue('reserved_combat_target_count')
        return max(0, available_logistic_target_count)

    def _get_current_combat_target(self):
        if self._has_combat_target():
            return self.GetLastBlackboardValue(self.attributes.combatTargetAddress)

    def _has_combat_target(self):
        return self.HasAttribute('combatTargetAddress')

    @TimedFunction('behaviors::actions::logistics::LockPrioritizedWatchlistMembers::_FilterItemsInTargetingRange')
    def _FilterItemsInTargetingRange(self, prioritized_watchlist):
        my_item_id = self.context.myItemId
        target_range = get_my_attribute_value(self, attributeMaxTargetRange)
        effective_range = self._get_effective_range()
        useful_range = min(target_range, effective_range)
        new_prioritized_watchlist = []
        for p, item_id in prioritized_watchlist:
            if item_id == my_item_id:
                continue
            distance = get_distance_between(self, self.context.myItemId, item_id)
            if distance < useful_range:
                falloff_multiplier = get_range_falloff_multiplier_at_distance(self, self.GetContextValue('remote_repair_effect_id'), distance)
                new_prioritized_watchlist.append((p * falloff_multiplier, item_id))

        new_prioritized_watchlist.sort(reverse=True)
        max_targets = self.get_max_targets()
        return [ item_id for _, item_id in new_prioritized_watchlist[:max_targets] ]

    @TimedFunction('behaviors::actions::logistics::LockPrioritizedWatchlistMembers::_UpdateLockedTargets')
    def _UpdateLockedTargets(self, items_to_target):
        locked_targets = set(self.context.dogmaLM.GetTargets(self.context.myItemId))
        self._remove_combat_target(locked_targets)
        targets_to_unlock = locked_targets.difference(items_to_target)
        targets_to_lock = set(items_to_target).difference(locked_targets)
        uthread2.start_tasklet(self._UnlockAndLockTargets_Thread, targets_to_unlock, targets_to_lock)

    def _remove_combat_target(self, locked_targets):
        combat_target = self._get_current_combat_target()
        if combat_target:
            locked_targets.discard(combat_target)

    @TimedFunction('behaviors::actions::logistics::LockPrioritizedWatchlistMembers::_UnlockAndLockTargets_Thread')
    def _UnlockAndLockTargets_Thread(self, targets_to_unlock, targets_to_lock):
        if self.is_updating_locks:
            return
        try:
            self.is_updating_locks = True
            for item_id in targets_to_unlock:
                self.context.dogmaLM.RemoveTarget(self.context.myItemId, item_id)
                be_nice()

            for item_id in targets_to_lock:
                if not self.context.dogmaLM.HasPendingTarget(self.context.myItemId, item_id):
                    self._TryLockTarget(item_id)
                be_nice()

        finally:
            self.is_updating_locks = False

    def _TryLockTarget(self, item_id):
        try:
            self.context.dogmaLM.AddTargetEx(self.context.myItemId, item_id, tasklet=True)
        except (UserError, RuntimeError) as e:
            logger.debug('LockPrioritizedWatchlistMembers: %s targeting %s: Unable to acquire target lock: %s', self.context.myItemId, item_id, e)
        except TaskletExit:
            logger.debug('LockPrioritizedWatchlistMembers: %s targeting %s: The target locking thread got killed prematurely', self.context.myItemId, item_id)
        except Exception as e:
            logger.debug('LockPrioritizedWatchlistMembers: %s targeting %s: something else happened: %s', self.context.myItemId, item_id, e)


class RegisterRepairEffectForType(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        remote_repair_effect_registry = self.GetLastBlackboardValue(self.attributes.remoteRepairEffectRegistryAddress) or {}
        type_id = self.context.mySlimItem.typeID
        if type_id in remote_repair_effect_registry:
            return
        remote_repair_effect_id = get_remote_repair_effect_id(self)
        remote_repair_effect_registry[type_id] = remote_repair_effect_id
        self.SendBlackboardValue(self.attributes.remoteRepairEffectRegistryAddress, remote_repair_effect_registry)
