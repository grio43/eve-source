#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\combattargets.py
import logging
import random
from collections import defaultdict
import evetypes
from ballpark.messenger.const import MESSAGE_TARGET_ADDED
from behaviors.blackboards import BlackboardDeletedError
from behaviors.const.combat import COMBAT_MAX_EFFECTIVE_FALLOFF_DISTANCE_FACTOR, COMBAT_MAX_EFFECTIVE_DISTANCE_FACTOR
from behaviors.utility.ballparks import is_ball_in_park, get_slim_item, is_ball_in_range, is_invulnerable, get_ball_type_id
from behaviors.utility.ballparks import get_specific_globals
from behaviors.utility.ballparks import is_target_valid, is_ball_cloaked, get_distance_between
from behaviors.utility.dogmatic import get_default_effect_id_for_type, get_my_attribute_value, type_has_effect
from behaviors.utility.dogmatic import get_entity_max_missile_range
from behaviors.utility.dogmatic import remove_my_target
from behaviors.utility.dogmatic import get_my_locked_targets, try_stop_effect
from behaviors.utility.inventory import get_inventory_item
from behaviors.utility.math import get_normalized_dict
from behaviors.utility.standings import is_hostile_towards
from dogma.const import attributeFalloff
from dogma.const import effectTargetAttack
from dogma.const import attributeMaxRange, effectMissileLaunchingForEntity
from dogma.effects.restricted.util import get_effect_range_with_falloff_multiplier
from dogma.effects.restricted.util import get_effect_range_and_falloff_values_for_item
from inventorycommon.const import categoryShip, categoryStructure
import uthread2
from behaviors.const.behaviorroles import COMBAT_DISTRIBUTE_EFFECTS_BY_ROLE, COMBAT_IGNORE_PRIMARY_BY_ROLE
from behaviors.const.blackboardchannels import MY_COMBAT_TARGET
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.targetEvaluation import targetEvaluationRegistry, ThreatTargetEvaluator
from behaviors.tasks import Task
from behaviors.trees.role import ROLE_ADDRESS
from eve.common.script.sys import idCheckers
from evemath import weighted_choice
from ccpProfile import TimedFunction
from eveexceptions import UserError
logger = logging.getLogger(__name__)

class FindTarget(Task, GroupTaskMixin):

    def __init__(self, attributes = None):
        super(FindTarget, self).__init__(attributes)
        self.filterFunctions = None

    @TimedFunction('behaviors::actions::combattargets::FindTarget::OnEnter')
    def OnEnter(self):
        self.SetTargetEvaluator()
        targetList = self._GetPotentialTargets()
        selectedTargetId = self.GetLastBlackboardValue(self.attributes.selectedTargetAddress)
        self.filterFunctions = self._GetFilterFunctions()
        targetList = self.FilterValidTargets(targetList)
        if self.ShouldPickNewTarget(selectedTargetId, targetList):
            pickedTarget = self.PickTarget(targetList)
            self._update_picked_target(pickedTarget)
            self.SendBlackboardValue(self.attributes.selectedTargetAddress, pickedTarget)
            self.SetStatusToSuccess()
        else:
            if selectedTargetId is not None:
                self.SendBlackboardValue(self.attributes.selectedTargetAddress, None)
            self.SetStatusToFailed()

    def SetTargetEvaluator(self):
        if not self.HasContextValue('targetEvaluator'):
            evaluatorClass = self._GetTargetEvaluatorClass()
            targetEvaluator = evaluatorClass(self.context, self.attributes)
            self.SetContextValue('targetEvaluator', targetEvaluator)

    def _GetTargetEvaluatorClass(self):
        return targetEvaluationRegistry[self.attributes.targetEvaluationFunction]

    def _GetPotentialTargets(self):
        return self.GetLastBlackboardValue(self.attributes.potentialTargetListAddress)

    def _GetFilterFunctions(self):
        return [self._GetFilterBubbleFunction(),
         self._FilterTargetCategory,
         self._FilterCloaked,
         self._FilterProtected,
         self._FilterMaxRangeFromGuardObject]

    def PickTarget(self, targetList):
        evaluateTarget = self.GetTargetEvaluator().EvaluateTarget
        sortedList = sorted(targetList, key=evaluateTarget)
        return sortedList[-1]

    def GetTargetEvaluator(self):
        return self.GetContextValue('targetEvaluator')

    @TimedFunction('behaviors::actions::combattargets::FindTarget::FilterValidTargets')
    def FilterValidTargets(self, targetList):
        if targetList is None:
            return []
        validTargets = self._GetValidTargets(targetList)
        validTargets = self._filter_valid_targets_for_fleet_spread(validTargets)
        validTargets = self._FilterValidTargetsForBehaviorRole(validTargets)
        return validTargets

    @TimedFunction('behaviors::actions::combattargets::FindTarget::_GetValidTargets')
    def _GetValidTargets(self, targetList):
        validTargets = []
        for targetId in targetList:
            if self._IsTargetValid(targetId):
                validTargets.append(targetId)

        return validTargets

    def _GetBubbleIdAndBubbleCheckRestriction(self):
        bubbleId = None
        if getattr(self.attributes, 'bubbleIdAddress', None) is not None:
            bubbleId = self.GetLastBlackboardValue(self.attributes.bubbleIdAddress)
            onlyCheckLocalBubble = True
        else:
            onlyCheckLocalBubble = self.attributes.onlyCheckLocalBubble
            if onlyCheckLocalBubble:
                bubbleId = self.context.myBall.newBubbleId
        return (bubbleId, onlyCheckLocalBubble)

    def _IsTargetValid(self, targetId):
        ballpark = self.context.ballpark
        ball = ballpark.balls.get(targetId)
        if ball is None:
            return False
        return all((filterfunction(ballpark, ball) for filterfunction in self.filterFunctions))

    def _GetFilterBubbleFunction(self):
        bubbleId, onlyCheckLocalBubble = self._GetBubbleIdAndBubbleCheckRestriction()

        def _FilterBubble(_, ball):
            if onlyCheckLocalBubble and ball.newBubbleId != bubbleId:
                return False
            return True

        return _FilterBubble

    def _FilterTargetCategory(self, ballpark, ball):
        if self.attributes.includedCategories:
            slimItem = ballpark.slims.get(ball.id)
            if slimItem is None:
                return False
            if slimItem.categoryID not in self.attributes.includedCategories:
                return False
        return True

    def _FilterCloaked(self, ballpark, ball):
        if ball.isCloaked:
            return False
        return not ballpark.HasPendingCloak(ball.id)

    def _FilterProtected(self, ballpark, ball):
        return not ballpark.IsBallProtected(ball.id)

    def _FilterMaxRangeFromGuardObject(self, ballpark, ball):
        if not self.HasAttribute('guardObjectIdAddress'):
            return True
        guardObjectMaxRange = getattr(self.attributes, 'maxDistanceFromGuardObject', None)
        if guardObjectMaxRange is not None:
            guardObjectId = self.GetLastBlackboardValue(self.attributes.guardObjectIdAddress)
            distanceBetween = get_distance_between(self, ball.id, guardObjectId)
            if distanceBetween is not None and distanceBetween >= guardObjectMaxRange:
                return False
        return True

    def ShouldPickNewTarget(self, selectedTarget, targetList):
        if not targetList:
            shouldPickNewTarget = False
        elif selectedTarget is not None and selectedTarget in targetList:
            shouldPickNewTarget = False
        else:
            shouldPickNewTarget = True
        return shouldPickNewTarget

    @TimedFunction('behaviors::actions::combattargets::FindTarget::_FilterValidTargetsForBehaviorRole')
    def _FilterValidTargetsForBehaviorRole(self, validTargets):
        myRoleAddress = getattr(self.attributes, 'roleAddress', None)
        if not myRoleAddress:
            return validTargets
        myRole = self.GetLastBlackboardValue(self.attributes.roleAddress)
        if not myRole:
            return validTargets
        validTargets = self._FilterPrimary(myRole, validTargets)
        validTargets = self._FilterValidTargetsForEffectDistribution(myRole, validTargets)
        return validTargets

    @TimedFunction('behaviors::actions::combattargets::FindTarget::_FilterPrimary')
    def _FilterPrimary(self, myRole, validTargets):
        if len(validTargets) <= 1:
            return validTargets
        if self._ShouldIgnorePrimary(myRole):
            if getattr(self.attributes, 'primaryTargetIdAddress', None):
                primaryTargetId = self.GetLastBlackboardValue(self.attributes.primaryTargetIdAddress)
                if primaryTargetId and primaryTargetId in validTargets:
                    validTargets.remove(primaryTargetId)
        return validTargets

    def _ShouldIgnorePrimary(self, myRole):
        return myRole in COMBAT_IGNORE_PRIMARY_BY_ROLE

    @TimedFunction('behaviors::actions::combattargets::FindTarget::_FilterValidTargetsForEffectDistribution')
    def _FilterValidTargetsForEffectDistribution(self, myRole, validTargets):
        if not self._ShouldDistributeEffects(myRole):
            return validTargets
        alreadyEffectedTargets = self._GetAllTargetsForGroupMembersWithRole(myRole)
        availableTargets = list(set(validTargets) - alreadyEffectedTargets)
        return availableTargets or validTargets

    def _ShouldDistributeEffects(self, myRole):
        return myRole in COMBAT_DISTRIBUTE_EFFECTS_BY_ROLE

    def _GetAllTargetsForGroupMembersWithRole(self, role):
        memberIds = self.GetMemberIdList()
        alreadyEffectedTargets = set()
        for groupMemberId in memberIds:
            if groupMemberId == self.context.myItemId:
                continue
            targetId = self._GetTargetIdForGroupMemberWithRole(groupMemberId, role)
            if targetId:
                alreadyEffectedTargets.add(targetId)

        return alreadyEffectedTargets

    def _GetTargetIdForGroupMemberWithRole(self, groupMemberId, role):
        try:
            memberRole = self._GetChannelValueForGroupMemberId(groupMemberId, ROLE_ADDRESS[1])
            if memberRole == role:
                return self._GetChannelValueForGroupMemberId(groupMemberId, MY_COMBAT_TARGET[1])
        except BlackboardDeletedError:
            return None

    def _GetChannelValueForGroupMemberId(self, groupMemberId, channelAddressName):
        return self.GetMessageChannelForItemId(groupMemberId, channelAddressName).GetLastMessageValue()

    @TimedFunction('behaviors::actions::combattargets::FindTarget::_filter_valid_targets_for_fleet_spread')
    def _filter_valid_targets_for_fleet_spread(self, valid_targets):
        if not self._should_spread_targets_in_fleet():
            return valid_targets
        available_targets = valid_targets[:]
        fleet_targets_by_group = self.GetLastBlackboardValue(self.attributes.fleetTargetsByGroupAddress) or {}
        for entity_group_id, fleet_target_id in fleet_targets_by_group.iteritems():
            if entity_group_id == self.context.myEntityGroupId:
                continue
            if fleet_target_id in available_targets:
                available_targets.remove(fleet_target_id)

        return available_targets or valid_targets

    def _should_spread_targets_in_fleet(self):
        return self.HasAttribute('shouldSpreadTargetsInFleet') and self.attributes.shouldSpreadTargetsInFleet is True and self.HasAttribute('fleetTargetsByGroupAddress')

    def _update_picked_target(self, picked_target_id):
        self.SendBlackboardValue(self.attributes.selectedTargetAddress, picked_target_id)
        if self.HasAttribute('fleetTargetsByGroupAddress'):
            fleet_targets_by_group = self.GetLastBlackboardValue(self.attributes.fleetTargetsByGroupAddress) or {}
            fleet_targets_by_group[self.context.myEntityGroupId] = picked_target_id
            self.SendBlackboardValue(self.attributes.fleetTargetsByGroupAddress, fleet_targets_by_group)


class FindTargetForModule(FindTarget):

    def __init__(self, attributes = None):
        FindTarget.__init__(self, attributes)

    def _GetPotentialTargets(self):
        if self.HasAttribute('potentialTargetDictionaryAddress'):
            primary_targets_by_entity = self.GetLastBlackboardValue(self.attributes.potentialTargetDictionaryAddress)
            if primary_targets_by_entity:
                return [ primary_target_id for primary_target_id in primary_targets_by_entity.itervalues() if primary_target_id is not None ]
        return super(FindTargetForModule, self)._GetPotentialTargets()

    def _GetFilterFunctions(self):
        return [self._GetFilterBubbleFunction(),
         self._FilterTargetCategory,
         self._FilterCloaked,
         self._FilterMaxRangeFromGuardObject,
         self._get_module_range_filter_function()]

    @TimedFunction('behaviors::actions::combattargets::FindTargetForModule::FilterValidTargets')
    def FilterValidTargets(self, targetList):
        if not targetList:
            return []
        validTargets = self._GetValidTargets(targetList)
        validTargets = self._FilterValidTargetsForBehaviorRole(validTargets)
        validTargets = self._filter_valid_targets_for_module_distribution(validTargets)
        return validTargets

    def _get_module_range_filter_function(self):
        module_item_id = self.GetLastBlackboardValue(self.attributes.moduleAddress)
        module_type_id = get_inventory_item(self, module_item_id).typeID
        effect_id = get_default_effect_id_for_type(self, module_type_id)
        minimum_range = get_effect_range_with_falloff_multiplier(self.context.dogmaLM, effect_id, module_item_id, COMBAT_MAX_EFFECTIVE_FALLOFF_DISTANCE_FACTOR)

        def _filter_module_range(_, ball):
            return is_ball_in_range(self, self.context.myBall.id, ball.id, minimum_range)

        return _filter_module_range

    @TimedFunction('behaviors::actions::combattargets::FindTargetForModule::_filter_valid_targets_for_module_distribution')
    def _filter_valid_targets_for_module_distribution(self, valid_targets):
        targets_already_affected = self._get_my_already_affected_targets(valid_targets)
        if not targets_already_affected:
            return valid_targets
        not_affected_targets = list(set(valid_targets).difference(targets_already_affected))
        if not_affected_targets:
            return not_affected_targets
        return [random.choice([min(targets_already_affected.keys(), key=targets_already_affected.get)])]

    def _get_my_already_affected_targets(self, valid_targets):
        targets_already_affected = defaultdict(int)
        non_stackable_module_list = self._get_my_non_stackable_module_list()
        if not non_stackable_module_list:
            return targets_already_affected
        my_targets_by_modules = self._get_my_targets_by_modules() or {}
        for module_id, target_id in my_targets_by_modules.iteritems():
            if target_id is None or target_id not in valid_targets:
                continue
            module_type_id = get_inventory_item(self, module_id).typeID
            if module_type_id in non_stackable_module_list:
                targets_already_affected[target_id] += 1

        return targets_already_affected

    def _get_my_non_stackable_module_list(self):
        eve_type_list_id = self.attributes.nonStackableEveTypeListId
        if not eve_type_list_id:
            return None
        return evetypes.GetTypeIDsByListID(eve_type_list_id)

    def _get_my_targets_by_modules(self):
        return self.GetLastBlackboardValue(self.attributes.targetsByModulesAddress)


class AcquireTargetLock(Task):

    def __init__(self, *args):
        super(AcquireTargetLock, self).__init__(*args)
        self._targetingThread = None

    @TimedFunction('behaviors::actions::combattargets::AcquireTargetLock::OnEnter')
    def OnEnter(self):
        pass

    @TimedFunction('behaviors::actions::combattargets::AcquireTargetLock::Update')
    def Update(self):
        self._AttemptToAcquireTargetLock()

    def _AttemptToAcquireTargetLock(self):
        selectedTarget = self.GetLastBlackboardValue(self.attributes.selectedTargetAddress)
        if not self._IsTargetValid(selectedTarget):
            self.SetStatusToFailed()
        elif is_invulnerable(self, self.context.myItemId):
            self._SetStatusWhileLockPending()
        elif self.context.dogmaLM.IsTargeting(self.context.myItemId, selectedTarget):
            self.SetStatusToSuccess()
        elif self.context.dogmaLM.HasPendingTarget(self.context.myItemId, selectedTarget):
            if self._targetingThread is None:
                self._SetStatusWhileLockPending()
            else:
                self._SetStatusWhileWaitingForLock()
        else:
            self._SetStatusWhileWaitingForLock()
            self._targetingThread = uthread2.start_tasklet(self._TryTargetLock, selectedTarget)

    def _IsTargetValid(self, selectedTarget):
        if selectedTarget is None:
            return False
        if not is_ball_in_park(self, selectedTarget):
            return False
        if is_ball_cloaked(self, selectedTarget):
            return False
        return True

    def _SetStatusWhileWaitingForLock(self):
        self.SubscribeItem(self.context.myItemId, MESSAGE_TARGET_ADDED, self.OnTargetAdded)
        self.SetStatusToSuspended()

    def _SetStatusWhileLockPending(self):
        self.SubscribeItem(self.context.myItemId, MESSAGE_TARGET_ADDED, self.OnTargetAdded)
        self.SetStatusToRunning()

    @TimedFunction('behaviors::actions::combattargets::AcquireTargetLock::_TryTargetLock')
    def _TryTargetLock(self, selectedTarget):
        try:
            self._LockTarget(selectedTarget)
        except (UserError, RuntimeError) as e:
            logger.debug('unable to acquire target lock: %s', e)
        except TaskletExit:
            logger.debug('The target locking thread got killed prematurely.')
        finally:
            if self.IsSuspended():
                self.SetStatusToRunning()
                self.status.OnUpdated(self)
            self._targetingThread = None

    def _LockTarget(self, selectedTarget):
        self.context.dogmaLM.AddTargetEx(self.context.myItemId, selectedTarget)

    def OnTargetAdded(self, target_id):
        self.SetStatusToSuccess()
        self.status.OnUpdated(self)

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeItem(self.context.myItemId, MESSAGE_TARGET_ADDED, self.OnTargetAdded)
        super(AcquireTargetLock, self).CleanUp()


class AcquireTargetLockNonBlocking(AcquireTargetLock):

    def _SetStatusWhileWaitingForLock(self):
        self.SetStatusToSuccess()

    def _SetStatusWhileLockPending(self):
        self.SetStatusToSuccess()


class UnlockTarget(Task):

    @TimedFunction('behaviors::actions::combattargets::UnlockTarget::OnEnter')
    def OnEnter(self):
        targetList = self.GetTargetList()
        if targetList:
            targetId = targetList[0]
            self.UnlockTarget(targetId)
        self.SetStatusToSuccess()

    def GetTargetList(self):
        return self.context.dogmaLM.GetTargetsEx(self.context.myItemId)

    def UnlockTarget(self, targetId):
        self.context.dogmaLM.RemoveTarget(self.context.myItemId, targetId)


class UnlockModuleTarget(UnlockTarget):

    @TimedFunction('behaviors::actions::combattargets::UnlockTarget::OnEnter')
    def OnEnter(self):
        target_list = self.GetTargetList()
        target_id = self._get_target_id()
        if target_list and target_id and target_id in target_list:
            self.UnlockTarget(target_id)
        self.SetStatusToSuccess()

    def _get_target_id(self):
        module_id = self.GetLastBlackboardValue(self.attributes.moduleAddress)
        targets_by_modules = self.GetLastBlackboardValue(self.attributes.targetsByModulesAddress)
        if targets_by_modules is None:
            return
        if module_id not in targets_by_modules:
            return
        target_id = targets_by_modules[module_id]
        if target_id is None or self._is_also_targeted_by_other_module(module_id, target_id, targets_by_modules):
            return
        return target_id

    def _is_also_targeted_by_other_module(self, module_id, target_id, targets_by_modules):
        for other_module_id, other_target_id in targets_by_modules.iteritems():
            if other_module_id == module_id:
                continue
            if other_target_id == target_id:
                return True

        return False


class PruneNpcsFromTargetSet(Task, GroupTaskMixin):

    def OnEnter(self):
        self.SetStatusToSuccess()
        targetSet = self.GetLastBlackboardValue(self.attributes.targetSetAddress)
        if not targetSet:
            return
        removedSet = set()
        destinyBalls = self.context.ballpark.balls
        for targetId in targetSet:
            if idCheckers.IsFakeItem(targetId) and targetId not in destinyBalls:
                removedSet.add(targetId)

        if removedSet:
            targetSet.difference_update(removedSet)
            self.SendBlackboardValue(self.attributes.targetSetAddress, targetSet)


class ClearTargetSet(Task, GroupTaskMixin):

    def OnEnter(self):
        self.SetStatusToSuccess()
        targetSet = self.GetLastBlackboardValue(self.attributes.targetSetAddress)
        if not targetSet:
            return
        self._UpdateTargetSet(set())
        entityGroupMembers = self.GetMemberIdList()
        uthread2.start_tasklet(self._LogKilledAndFledTargets, targetSet, entityGroupMembers)

    def _LogKilledAndFledTargets(self, targetSet, entityGroupMembers):
        self.context.eventLogger.log_killed_and_fled_players(self.GetGroupOwnerId(), self.behaviorTree.GetBehaviorId(), targetSet, entityGroupMembers)

    def _UpdateTargetSet(self, targetSet):
        self.SendBlackboardValue(self.attributes.targetSetAddress, targetSet)


class SelectPilotedShips(Task):

    @TimedFunction('behaviors::actions::combattargets::SelectPilotedShips::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        target_ids = self.GetLastBlackboardValue(self.attributes.sourceSetAddress)
        if not target_ids:
            return
        piloted_ship_set = self.get_piloted_ship_set(target_ids)
        self.SendBlackboardValue(self.attributes.targetSetAddress, piloted_ship_set)

    def get_piloted_ship_set(self, target_ids):
        result_set = set()
        for target_id in target_ids:
            if self.is_valid(target_id):
                result_set.add(target_id)

        return result_set

    def is_valid(self, target_id):
        if not is_ball_in_park(self, target_id):
            return False
        slim_item = get_slim_item(self, target_id)
        if slim_item is None:
            return False
        if slim_item.categoryID != categoryShip:
            return False
        if not self.context.dogmaLM.IsShipPiloted(target_id):
            return False
        return True


class GetMyMinOptimalAndFalloff(Task):

    @TimedFunction('behaviors::actions::combattargets::GetMyMinOptimalAndFalloff::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        min_optimal, min_falloff = self._get_my_min_optimal_and_falloff()
        self.SendBlackboardValue(self.attributes.minOptimalAddress, min_optimal)
        self.SendBlackboardValue(self.attributes.minFalloffAddress, min_falloff)

    def _get_my_min_optimal_and_falloff(self):
        effect_optimal, effect_falloff = self._get_my_min_effect_range()
        weapon_optimal, weapon_falloff = self._get_my_min_weapon_range()
        if not weapon_optimal or effect_optimal and effect_optimal < weapon_optimal:
            logger.debug('Behavior=%s for entity_type=%s setting min optimal=%s and falloff=%s from combat effect', self.behaviorTree.GetBehaviorId(), self.context.mySlimItem.typeID, effect_optimal, effect_falloff)
            return (effect_optimal, effect_falloff)
        logger.debug('Behavior=%s for entity_type=%s setting min optimal=%s and falloff=%s from weapons', self.behaviorTree.GetBehaviorId(), self.context.mySlimItem.typeID, weapon_optimal, weapon_falloff)
        return (weapon_optimal, weapon_falloff)

    def _get_my_min_effect_range(self):
        minimum_optimal = 0.0
        minimum_falloff = 0.0
        my_combat_effects = self._get_my_combat_effects()
        for effect_id in my_combat_effects:
            if type_has_effect(self, self.context.mySlimItem.typeID, effect_id):
                effect_optimal, effect_falloff = self._get_effect_optimal_and_falloff(effect_id)
                if effect_optimal == 0.0:
                    logger.error('Badly authored effect: %s for behavior NPC range picks - no range assigned to it.', effect_id)
                    continue
                if effect_optimal < minimum_optimal or minimum_optimal == 0.0:
                    minimum_optimal = effect_optimal
                    minimum_falloff = effect_falloff

        return (minimum_optimal, minimum_falloff)

    def _get_my_combat_effects(self):
        return self.GetLastBlackboardValue(self.attributes.combatEffectsAddress) or []

    def _get_effect_optimal_and_falloff(self, effect_id):
        effect_optimal, effect_falloff = get_effect_range_and_falloff_values_for_item(self.context.dogmaLM, self.context.myItemId, effect_id)
        return (effect_optimal or 0.0, effect_falloff or 0.0)

    def _get_my_min_weapon_range(self):
        weapon_optimal, weapon_falloff = turret_optimal, turret_falloff = self._get_turret_range()
        if type_has_effect(self, self.context.mySlimItem.typeID, effectMissileLaunchingForEntity):
            missile_range = self._get_missile_range()
            if not turret_optimal or missile_range < turret_optimal:
                weapon_optimal = missile_range
                weapon_falloff = 0.0
        return (weapon_optimal or 0.0, weapon_falloff or 0.0)

    def _get_turret_range(self):
        weapon_optimal = get_my_attribute_value(self, attributeMaxRange)
        weapon_falloff = get_my_attribute_value(self, attributeFalloff)
        if weapon_falloff == 1.0:
            weapon_falloff = 0.0
        return (weapon_optimal, weapon_falloff)

    def _get_missile_range(self):
        return get_entity_max_missile_range(self, self.context.mySlimItem.typeID)


class GetMaxEffectiveRange(Task):

    @TimedFunction('behaviors::actions::combattargets::GetMaxEffectiveRange::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        max_effective_range = self._get_max_effective_range()
        self.SendBlackboardValue(self.attributes.maxEffectiveRangeAddress, max_effective_range)

    def _get_max_effective_range(self):
        optimal_range = self.GetLastBlackboardValue(self.attributes.minOptimalAddress)
        falloff_range = self.GetLastBlackboardValue(self.attributes.minFalloffAddress) or 0
        if falloff_range:
            max_effective_range = optimal_range + falloff_range * COMBAT_MAX_EFFECTIVE_FALLOFF_DISTANCE_FACTOR
            return max_effective_range * COMBAT_MAX_EFFECTIVE_DISTANCE_FACTOR
        else:
            return optimal_range


class GenerateTargetSetsByCombatRangesInGroup(Task):

    @TimedFunction('behaviors::actions::combattargets::GenerateTargetSetsByCombatRangesInGroup::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        targets_by_entity_type = self._get_targets_by_entity_type()
        logger.debug('Behavior=%s for task=%s generated target_set=%s', self.behaviorTree.GetBehaviorId(), self.GetTaskName(), targets_by_entity_type)
        self.SendBlackboardValue(self.attributes.targetsByEntityTypeAddress, targets_by_entity_type)

    def _get_targets_by_entity_type(self):
        range_by_entity_type = self._get_range_by_entity_type()
        balls_in_range = self._get_ball_ids_and_distance_in_range(range_by_entity_type)
        targets_by_entity_type = defaultdict(set)
        threat_target_set = self._get_threat_target_set()
        for distance_squared, ball_id in balls_in_range:
            if not is_target_valid(self, ball_id, target_list=threat_target_set, required_categories=[categoryShip]):
                continue
            self._add_target(targets_by_entity_type, range_by_entity_type, ball_id, distance_squared)

        return targets_by_entity_type

    def _get_range_by_entity_type(self):
        return self.GetLastBlackboardValue(self.attributes.rangeByEntityTypeAddress)

    def _get_ball_ids_and_distance_in_range(self, range_by_entity_type):
        if range_by_entity_type is None:
            return []
        commander = self._get_commander()
        if commander is None or not is_ball_in_park(self, commander):
            logger.warn('Behavior=%s for task=% is missing commander', self.behaviorTree.GetBehaviorId(), self.GetTaskName())
            return []
        max_effective_range_of_group = max(range_by_entity_type.values())
        return self.context.ballpark.GetBallIdsAndDistInRange(commander, max_effective_range_of_group)

    def _get_commander(self):
        return self.GetLastBlackboardValue(self.attributes.commanderAddress)

    def _get_threat_target_set(self):
        if self.HasAttribute('threatTargetSetAddres'):
            return self.GetLastBlackboardValue(self.attributes.threatTargetSetAddress)

    def _add_target(self, targets_by_entity_type, range_by_entity_type, ball_id, distance_squared):
        for entity_type_id, max_effective_range in range_by_entity_type.iteritems():
            if max_effective_range ** 2 > distance_squared:
                targets_by_entity_type[entity_type_id].add(ball_id)


class GetPrimaryAndNonPrimaryTargetsByEntityTypes(Task):

    @TimedFunction('behaviors::actions::combattargets::GetTargetsByRanges::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        primary_targets, non_primary_targets = self._get_targets_by_entity_type()
        self.SetStatusToSuccess()
        self._post_targets_by_entity_type(primary_targets, non_primary_targets)

    def _get_targets_by_entity_type(self):
        all_targets = self._get_all_targets()
        if not all_targets:
            return (None, None)
        primary_evaluator = self._get_primary_evaluator()
        primary_targets = {}
        non_primary_evaluator = self._get_non_primary_evaluator()
        non_primary_targets = {}
        for entity_type, targets_set in all_targets.iteritems():
            self._get_primary_target(primary_targets, primary_evaluator, entity_type, targets_set)
            primary = primary_targets[entity_type]
            self._get_non_primary_targets(non_primary_targets, non_primary_evaluator, entity_type, targets_set, primary)

        return (primary_targets, non_primary_targets)

    def _get_all_targets(self):
        return self.GetLastBlackboardValue(self.attributes.targetsAddress)

    def _get_primary_evaluator(self):
        evaluator_class = targetEvaluationRegistry[self.attributes.primaryTargetEvaluationFunction]
        return evaluator_class(self.context, self.attributes)

    def _get_non_primary_evaluator(self):
        evaluator_class = targetEvaluationRegistry[self.attributes.nonPrimaryTargetEvaluationFunction]
        return evaluator_class(self.context, self.attributes)

    def _get_primary_target(self, primary_targets, primary_target_evaluator, entity_type, targets_set):
        type_list_id = getattr(self.attributes, 'primaryTypeListId', None)
        filtered_targets_set = self._filter_targets_set_by_type_list(type_list_id, targets_set)
        if filtered_targets_set:
            primary_targets[entity_type] = sorted(filtered_targets_set, key=primary_target_evaluator.EvaluateTarget)[-1]
        else:
            primary_targets[entity_type] = None

    def _get_non_primary_targets(self, non_primary_targets, non_primary_evaluator, entity_type, targets_set, primary):
        type_list_id = getattr(self.attributes, 'nonPrimaryTypeListId', None)
        filtered_targets_set = self._filter_targets_set_by_type_list(type_list_id, targets_set)
        if primary and primary in filtered_targets_set:
            filtered_targets_set.remove(primary)
        non_primary_targets[entity_type] = set()
        for target_id in filtered_targets_set:
            weight = non_primary_evaluator.EvaluateTarget(target_id)
            non_primary_targets[entity_type].add((target_id, weight))

    def _filter_targets_set_by_type_list(self, type_list_id, targets_set):
        if type_list_id is None:
            return targets_set
        types_of_interest = evetypes.GetTypeIDsByListID(type_list_id)
        filtered_targets_set = set()
        for target_id in targets_set:
            if get_slim_item(self, target_id).typeID in types_of_interest:
                filtered_targets_set.add(target_id)

        return filtered_targets_set

    def _post_targets_by_entity_type(self, primary_targets, non_primary_targets):
        logger.debug('Behavior=%s for task=%s found and posting primary_targets=%s and non_primary=%s', self.behaviorTree.GetBehaviorId(), self.GetTaskName(), primary_targets, non_primary_targets)
        self.SendBlackboardValue(self.attributes.primaryTargetsByEntityTypesAddress, primary_targets)
        self.SendBlackboardValue(self.attributes.nonPrimaryTargetsByEntityTypesAddress, non_primary_targets)


class GetWeightedTargetFromTargetsSet(Task):

    @TimedFunction('behaviors::actions::combattargets::GetWeightedTargetFromTargetsSet::OnEnter')
    def OnEnter(self):
        target_weight_set = self._get_target_weight_set()
        target_id = self._get_target(target_weight_set)
        if target_id is None:
            self.SetStatusToFailed()
            return
        self.SetStatusToSuccess()
        logger.debug('Behavior=%s for task=%s and entity=%s received new target=%s', self.behaviorTree.GetBehaviorId(), self.GetTaskName(), self.context.myItemId, target_id)
        self._post_target(target_id)

    def _get_target(self, target_weight_set):
        if not target_weight_set:
            return None
        return weighted_choice(target_weight_set)

    def _get_target_weight_set(self):
        return self.GetLastBlackboardValue(self.attributes.targetWeightSetAddress)

    def _post_target(self, target_id):
        self.SendBlackboardValue(self.attributes.targetIdAddress, target_id)


class DisengageObsoleteTargets(Task):

    @TimedFunction('behaviors::actions::combattargets::DisengageObsoleteTargets::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        my_target_is = self.GetLastBlackboardValue(self.attributes.myTargetAddress)
        my_locked_targets = get_my_locked_targets(self)
        my_combat_effects = self._get_my_combat_effects()
        for target_id in my_locked_targets:
            if target_id != my_target_is:
                self._stop_combat_effects_on_target(my_combat_effects)
                remove_my_target(self, target_id)

    def _get_my_combat_effects(self):
        my_combat_effects = [effectTargetAttack, effectMissileLaunchingForEntity]
        my_combat_effects_from_address = self.GetLastBlackboardValue(self.attributes.myCombatEffectsAddress) or []
        my_combat_effects.extend(my_combat_effects_from_address)
        return my_combat_effects

    def _stop_combat_effects_on_target(self, my_combat_effects):
        for effect_id in my_combat_effects:
            try_stop_effect(self, effect_id)


class FindHostileStructureInRange(Task):

    @TimedFunction('behaviors::actions::combattargets::FindHostileStructureInRange::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        hostile_global_structures = self._get_hostile_structures()
        if hostile_global_structures:
            current_hostiles = self.GetLastBlackboardValue(self.attributes.targetsAddress) or set()
            current_hostiles = current_hostiles.union(hostile_global_structures)
            self.SendBlackboardValue(self.attributes.targetsAddress, current_hostiles)
            self.SetStatusToSuccess()
            logger.debug('Behavior=%s found hostile_structures=%s', self.context.myItemId, hostile_global_structures)

    def _get_hostile_structures(self):
        hostile_global_structures = set()
        for global_ball_id, global_ball in get_specific_globals(self, category_id=categoryStructure).iteritems():
            if self._is_valid(global_ball_id, global_ball):
                hostile_global_structures.add(global_ball_id)

        return hostile_global_structures

    def _is_valid(self, global_ball_id, global_ball):
        if not global_ball.IsVulnerable():
            return False
        if not is_hostile_towards(self, global_ball.ownerID):
            return False
        return is_ball_in_range(self, self.context.myItemId, global_ball_id, self.attributes.minDistance)


class FindTargetWithPolarizedPreference(FindTarget):

    def __init__(self, attributes = None):
        super(FindTargetWithPolarizedPreference, self).__init__(attributes)

    def OnEnter(self):
        super(FindTargetWithPolarizedPreference, self).OnEnter()

    def _GetTargetEvaluatorClass(self):
        return ThreatTargetEvaluator

    def PickTarget(self, target_list):
        weightByItemId = {itemId:self._EvaluateTarget(itemId) for itemId in target_list}
        if self._IsPreferenceEnabled():
            weightByItemId = get_normalized_dict(weightByItemId)
            biasAmount = self._GetPreferredTypeBiasAmount()
            if self._IsPreferringType():
                self._UpdateWeights(weightByItemId, biasAmount)
            else:
                self._UpdateWeights(weightByItemId, -biasAmount)
        sortedTargetIds = sorted(weightByItemId.keys(), key=lambda itemId: weightByItemId[itemId])
        return sortedTargetIds[-1]

    def _UpdateWeights(self, weightByItemId, biasAmount):
        preferredTypeList = self._GetPreferredTypeList()
        for itemId in weightByItemId:
            if self._GetBallTypeId(itemId) in preferredTypeList:
                weightByItemId[itemId] += biasAmount

    def _GetBallTypeId(self, itemId):
        return get_ball_type_id(self, itemId)

    def _GetPreferredTypeList(self):
        preferredTypeList = evetypes.GetTypeIDsByListID(self.attributes.preferredTypeListID)
        return preferredTypeList

    def _IsPreferenceEnabled(self):
        return self.GetLastBlackboardValue(self.attributes.isPreferenceEnabledAddress)

    def _IsPreferringType(self):
        isPreferringType = self._GetIsPreferringType()
        if isPreferringType is None:
            isPreferringType = self._GetChanceOfPreferringType() >= random.random() * 100
            self._SendIsPreferringType(isPreferringType)
        return isPreferringType

    def _GetChanceOfPreferringType(self):
        return self.GetLastBlackboardValue(self.attributes.chanceOfPreferringTypesAddress)

    def _SendIsPreferringType(self, isPreferringType):
        self.SendBlackboardValue(self.attributes.isPreferringTypeAddress, isPreferringType)

    def _GetIsPreferringType(self):
        return self.GetLastBlackboardValue(self.attributes.isPreferringTypeAddress)

    def _EvaluateTarget(self, itemId):
        return self.GetTargetEvaluator().EvaluateTarget(itemId)

    def _GetPreferredTypeBiasAmount(self):
        return self.GetLastBlackboardValue(self.attributes.preferredTypeBiasAmountAddress)
