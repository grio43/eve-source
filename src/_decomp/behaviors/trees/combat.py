#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\combat.py
from behaviors import composites
from behaviors.actions import WaitAction
from behaviors.actions.ballparks import OrbitAtDistanceAction, ManageMicroWarpDriveToTarget, ModifyOrbitVelocity
from behaviors.actions.blackboards import BlackboardCopyMessageAction
from behaviors.actions.combat import ActivateCombatEffectsOnTarget, OwnerListFilterAction
from behaviors.actions.combat import StopCombatEffectsOnTarget, GetCombatEffectsForRole
from behaviors.actions.combatnavigation import GetCombatOrbitAndAttackRange, GetFleetCombatOrbitRangeByRole
from behaviors.actions.combatnavigation import GetTargetToOrbit
from behaviors.actions.combattargets import FindTarget, UnlockTarget, AcquireTargetLock, GetMyMinOptimalAndFalloff
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.conditions.ballparks import IsBallPresentInMyBubbleCondition
from behaviors.conditions.blackboards import BlackboardMessagesEqualCondition, IsBlackboardValueInCollectionCondition
from behaviors.conditions.blackboards import IsBlackboardValueNotNone
from behaviors.conditions.combat import HasAvailableTargetCapacity
from behaviors.conditions.effects import HasAnyEffectCondition
from behaviors.const.blackboardchannels import GROUP_PRIMARY_TARGET, MY_COMBAT_TARGET, COMMANDER_ADDRESS
from behaviors.const.blackboardchannels import COMBAT_TARGETS_SET_ADDRESS, COMBAT_MIN_FALLOFF_ADDRESS
from behaviors.const.blackboardchannels import COMBAT_MIN_OPTIMAL_ADDRESS
from behaviors.const.combat import THREAT_TARGET_EVALUATOR
from behaviors.decorators import modifiers
from behaviors.decorators.modifiers import ForceSuccess
from behaviors.decorators.repeaters import RepeatWhileFailing
from behaviors.decorators.timers import CooldownTimer
from behaviors.monitors.ballparks import MonitorProximitySensors, MonitorInvulnerabilityCanceledInBubble
from behaviors.monitors.ballparks import TargetChangingBubbleMonitor, TargetLeavingParkMonitor
from behaviors.monitors.ballparks import TargetWithOwnerEnteredBubbleMonitor
from behaviors.monitors.blackboards import BlackboardMessageMonitor
from behaviors.monitors.combat import MaxLockedTargetsChangedMonitor, MonitorAssistanceToTargets
from behaviors.monitors.combat import WaitForAggressiveAct, ClearValueAndResetIfTargetCloaks
from behaviors.monitors.targeting import TargetLostMonitor
from behaviors.trees.role import ROLE_ADDRESS
from brennivin.itertoolsext import Bundle
from dogma.const import effectModifyTargetSpeed2, effectEntityCapacitorDrain, effectWarpScrambleForEntity, effectBehaviorWarpDisrupt, effectNpcBehaviorWebifier, effectNpcBehaviorMicroJumpAttack, effectNpcBehaviorSmartBomb, effectEntityChainLightning
from dogma.const import effectBehaviorWarpScramble, effectBehaviorTargetPainter, effectNpcBehaviorGuidanceDisruptor, effectNpcBehaviorTrackingDisruptor
from dogma.const import effectNpcBehaviorEnergyNeutralizer, effectBehaviorSensorDampener, effectBehaviorECM
from dogma.const import effectTargetAttack, effectMissileLaunchingForEntity, effectNpcBehaviorEnergyNosferatu
from dogma.const import effectWarpScrambleTargetMWDBlockActivationForEntity, effectEntityTargetPaint
from inventorycommon.const import categoryShip, categoryDrone, groupCapsule, categoryFighter
from npcs.server.tags import DRIFTER_TAG
COMBAT_TARGETS_SET = COMBAT_TARGETS_SET_ADDRESS
TARGETS_MONITORED_FOR_ASSISTANCE_SET = (ScopeTypes.EntityGroup, 'TARGETS_MONITORED_FOR_ASSISTANCE_SET')
COMBAT_WARP_TO_LOCATION = (ScopeTypes.EntityGroup, 'COMBAT_WARP_TO_LOCATION')
POTENTIAL_TARGET = (ScopeTypes.Item, 'POTENTIAL_TARGET')
GROUP_TARGET_SWITCH_TIMER = (ScopeTypes.EntityGroup, 'GROUP_TARGET_SWITCH_TIMER')
TARGET_SWITCH_TIMER = (ScopeTypes.Item, 'TARGET_SWITCH_TIMER')
COMBAT_ORBIT_RANGE = (ScopeTypes.Item, 'COMBAT_ORBIT_RANGE')
COMBAT_ATTACK_RANGE = (ScopeTypes.Item, 'COMBAT_ATTACK_RANGE')
COMBAT_ORBIT_TARGET = (ScopeTypes.Item, 'COMBAT_ORBIT_TARGET')
COMBAT_WARP_AT_DISTANCE = (ScopeTypes.Item, 'COMBAT_WARP_AT_DISTANCE')
COMBAT_EFFECTS_ADDRESS = (ScopeTypes.Item, 'COMBAT_EFFECTS')
COMBAT_EFFECTS = (effectEntityCapacitorDrain,
 effectEntityTargetPaint,
 effectMissileLaunchingForEntity,
 effectModifyTargetSpeed2,
 effectTargetAttack,
 effectWarpScrambleForEntity,
 effectWarpScrambleTargetMWDBlockActivationForEntity,
 effectBehaviorECM,
 effectNpcBehaviorEnergyNeutralizer,
 effectNpcBehaviorEnergyNosferatu,
 effectNpcBehaviorGuidanceDisruptor,
 effectBehaviorSensorDampener,
 effectBehaviorTargetPainter,
 effectNpcBehaviorTrackingDisruptor,
 effectBehaviorWarpDisrupt,
 effectBehaviorWarpScramble,
 effectNpcBehaviorWebifier,
 effectNpcBehaviorMicroJumpAttack,
 effectNpcBehaviorSmartBomb,
 effectEntityChainLightning)

def CreateTargetSwitchingBehavior(targetEvaluationFunction = THREAT_TARGET_EVALUATOR, preferredModuleGroups = [], targetAddress = GROUP_PRIMARY_TARGET, groupPrimaryAddress = GROUP_PRIMARY_TARGET, targetSwitchTimerAddress = GROUP_TARGET_SWITCH_TIMER):
    return modifiers.ForceFailure(Bundle(name='Target Switching')).AddSubTask(CooldownTimer(Bundle(timerAddress=targetSwitchTimerAddress, timeoutSeconds=60)).AddSubTask(composites.Sequence().AddSubTask(FindTarget(Bundle(name='Get A Target', selectedTargetAddress=POTENTIAL_TARGET, potentialTargetListAddress=COMBAT_TARGETS_SET, includedCategories=[], onlyCheckLocalBubble=True, targetEvaluationFunction=targetEvaluationFunction, roleAddress=ROLE_ADDRESS, preferredModuleGroups=preferredModuleGroups, primaryTargetIdAddress=groupPrimaryAddress))).AddSubTask(modifiers.Not().AddSubTask(BlackboardMessagesEqualCondition(Bundle(firstMessageAddress=targetAddress, secondMessageAddress=POTENTIAL_TARGET)))).AddSubTask(BlackboardCopyMessageAction(Bundle(sourceMessageAddress=POTENTIAL_TARGET, targetMessageAddress=targetAddress))).AddSubTask(StopCombatEffectsOnTarget(Bundle(name='Stop All Combat Effects', effectIds=COMBAT_EFFECTS)))))


def CreateCombatBehavior(validOwnerIds = [], orbitVelocity = None, orbitRange = None, attackRange = None, targetAddress = GROUP_PRIMARY_TARGET, groupPrimaryAddress = GROUP_PRIMARY_TARGET, targetEvaluationFunction = THREAT_TARGET_EVALUATOR, preferredModuleGroups = [], proximitySensorTags = (DRIFTER_TAG,)):
    return composites.Sequence(Bundle(name='Combat')).AddSubTask(WaitForAggressiveAct(Bundle(name='Aggression Monitor', combatTargetsAddress=COMBAT_TARGETS_SET))).AddSubTask(MonitorAssistanceToTargets(Bundle(name='Monitor Enemy Assistance', combatTargetsAddress=COMBAT_TARGETS_SET))).AddSubTask(MonitorProximitySensors(Bundle(objectListAddress=COMBAT_TARGETS_SET, includedCategories=[categoryShip, categoryDrone, categoryFighter], excludedGroups=[groupCapsule], validOwnerIds=validOwnerIds, invalidOwnerIds=None, tags=proximitySensorTags))).AddSubTask(MonitorInvulnerabilityCanceledInBubble(Bundle(targetIdListAddress=COMBAT_TARGETS_SET))).AddSubTask(MaxLockedTargetsChangedMonitor()).AddSubTask(BlackboardMessageMonitor(Bundle(messageAddress=COMBAT_TARGETS_SET))).AddSubTask(CreateSelectTargetBehavior(targetAddress, targetEvaluationFunction, preferredModuleGroups, groupPrimaryAddress)).AddSubTask(CreateGetCombatNavigationBehavior(orbitRange, attackRange, targetAddress)).AddSubTask(CreateAttackTargetBehavior(orbitVelocity, targetAddress))


def CreateOwnerAggressionBehavior(ownerIds):
    return modifiers.ForceFailure(Bundle(name='Owner Aggression')).AddSubTask(TargetWithOwnerEnteredBubbleMonitor(Bundle(targetSetAddress=COMBAT_TARGETS_SET, ownerIds=ownerIds)))


def CreateFriendlyTargetFilterBehavior(friendlyOwnerIds):
    return modifiers.ForceFailure(Bundle(name='Friendly Target Filter')).AddSubTask(OwnerListFilterAction(Bundle(ownerIdSet=friendlyOwnerIds, itemIdSetAddress=COMBAT_TARGETS_SET)))


def CreateEntityCombatBehavior(orbitVelocity = None, orbitRange = None, attackRange = None, targetAddress = GROUP_PRIMARY_TARGET, groupPrimaryAddress = GROUP_PRIMARY_TARGET, targetEvaluationFunction = THREAT_TARGET_EVALUATOR, preferredModuleGroups = []):
    root = composites.Sequence(Bundle(name='Combat'))
    root.AddSubTask(WaitForAggressiveAct(Bundle(name='Aggression Monitor', combatTargetsAddress=COMBAT_TARGETS_SET)))
    root.AddSubTask(HasAnyEffectCondition(Bundle(name='Can I fight?', effectIds=COMBAT_EFFECTS)))
    root.AddSubTask(MaxLockedTargetsChangedMonitor())
    root.AddSubTask(BlackboardMessageMonitor(Bundle(messageAddress=COMBAT_TARGETS_SET)))
    root.AddSubTask(CreateSelectTargetBehavior(targetAddress, targetEvaluationFunction, preferredModuleGroups, groupPrimaryAddress))
    root.AddSubTask(CreateGetCombatNavigationBehavior(orbitRange, attackRange, targetAddress))
    root.AddSubTask(CreateAttackTargetBehavior(orbitVelocity, targetAddress=targetAddress))
    return root


def CreateSelectTargetBehavior(selectedTargetAddress, targetEvaluationFunction, preferredModuleGroups, groupPrimaryAddress):
    return composites.PrioritySelector(Bundle(name='Select Target')).AddSubTask(composites.Sequence().AddSubTask(IsBlackboardValueNotNone(Bundle(valueAddress=selectedTargetAddress))).AddSubTask(IsBlackboardValueInCollectionCondition(Bundle(valueAddress=selectedTargetAddress, collectionAddress=COMBAT_TARGETS_SET))).AddSubTask(IsBallPresentInMyBubbleCondition(Bundle(ballIdAddress=selectedTargetAddress)))).AddSubTask(FindTarget(Bundle(name='Get A Target', selectedTargetAddress=selectedTargetAddress, potentialTargetListAddress=COMBAT_TARGETS_SET, includedCategories=[], onlyCheckLocalBubble=True, targetEvaluationFunction=targetEvaluationFunction, roleAddress=ROLE_ADDRESS, preferredModuleGroups=preferredModuleGroups, primaryTargetIdAddress=groupPrimaryAddress)))


def CreateAttackTargetBehavior(orbitVelocity, targetAddress = GROUP_PRIMARY_TARGET):
    root = composites.Sequence()
    root.AddSubTask(modifiers.ForceSuccess(Bundle(name='Disengage obsolete targets')).AddSubTask(composites.Sequence().AddSubTask(modifiers.Not().AddSubTask(BlackboardMessagesEqualCondition(Bundle(firstMessageAddress=MY_COMBAT_TARGET, secondMessageAddress=targetAddress)))).AddSubTask(StopCombatEffectsOnTarget(Bundle(name='Stop All Combat Effects', effectIds=COMBAT_EFFECTS)))))
    root.AddSubTask(ClearValueAndResetIfTargetCloaks(Bundle(targetAddress=targetAddress, valueAddress=targetAddress)))
    root.AddSubTask(TargetLeavingParkMonitor(Bundle(targetAddress=targetAddress, clearValue=True)))
    root.AddSubTask(BlackboardCopyMessageAction(Bundle(sourceMessageAddress=targetAddress, targetMessageAddress=MY_COMBAT_TARGET)))
    root.AddSubTask(BlackboardMessageMonitor(Bundle(messageAddress=targetAddress)))
    root.AddSubTask(TargetLostMonitor(Bundle(targetAddress=targetAddress)))
    root.AddSubTask(TargetChangingBubbleMonitor(Bundle(targetAddress=targetAddress, resetOnEnter=False)))
    root.AddSubTask(ModifyOrbitVelocity(Bundle(orbitVelocity=orbitVelocity)))
    root.AddSubTask(OrbitAtDistanceAction(Bundle(orbitTargetAddress=COMBAT_ORBIT_TARGET, orbitRangeAddress=COMBAT_ORBIT_RANGE, blocking=False, blockUntilRange=COMBAT_ATTACK_RANGE)))
    root.AddSubTask(ManageMicroWarpDriveToTarget(Bundle(targetAddress=targetAddress, orbitRangeAddress=COMBAT_ORBIT_RANGE, microWarpDriveDuration=5000, microWarpDriveChance=1.0)))
    root.AddSubTask(composites.PrioritySelector(Bundle(name='Release target if required')).AddSubTask(HasAvailableTargetCapacity()).AddSubTask(UnlockTarget()))
    root.AddSubTask(RepeatWhileFailing(Bundle(name='Retry', maxRepetitions=7)).AddSubTask(AcquireTargetLock(Bundle(selectedTargetAddress=targetAddress))))
    root.AddSubTask(ActivateCombatEffectsOnTarget(Bundle(name='Start all Combat Effects on Target', effectIds=COMBAT_EFFECTS, selectedTargetAddress=targetAddress, repeat=1000))).AddSubTask(WaitAction(Bundle()))
    return root


def CreateGetCombatNavigationBehavior(orbitRange = None, attackRange = None, targetAddress = GROUP_PRIMARY_TARGET):
    return composites.Sequence().AddSubTask(GetTargetToOrbit(Bundle(name='Get Target To Orbit In Combat', commanderAddress=COMMANDER_ADDRESS, combatTargetAddress=targetAddress, orbitTargetAddress=COMBAT_ORBIT_TARGET, roleAddress=ROLE_ADDRESS))).AddSubTask(composites.Sequence().AddSubTask(ForceSuccess().AddSubTask(composites.Sequence(Bundle(name='Get Combat Effects & Orbit Range')).AddSubTask(GetCombatEffectsForRole(Bundle(combatEffectsAddress=COMBAT_EFFECTS_ADDRESS, roleAddress=ROLE_ADDRESS))).AddSubTask(GetMyMinOptimalAndFalloff(Bundle(minOptimalAddress=COMBAT_MIN_OPTIMAL_ADDRESS, minFalloffAddress=COMBAT_MIN_FALLOFF_ADDRESS, combatEffectsAddress=COMBAT_EFFECTS_ADDRESS))).AddSubTask(GetCombatOrbitAndAttackRange(Bundle(orbitRangeAddress=COMBAT_ORBIT_RANGE, attackRangeAddress=COMBAT_ATTACK_RANGE, orbitRange=orbitRange, attackRange=attackRange, minOptimalAddress=COMBAT_MIN_OPTIMAL_ADDRESS, minFalloffAddress=COMBAT_MIN_FALLOFF_ADDRESS))))).AddSubTask(ForceSuccess().AddSubTask(composites.Sequence(Bundle(name='Overwriting Orbit Range if Orbiting Commander')).AddSubTask(BlackboardMessagesEqualCondition(Bundle(firstMessageAddress=COMBAT_ORBIT_TARGET, secondMessageAddress=COMMANDER_ADDRESS))).AddSubTask(GetFleetCombatOrbitRangeByRole(Bundle(roleAddress=ROLE_ADDRESS, orbitRangeAddress=COMBAT_ORBIT_RANGE))))))
