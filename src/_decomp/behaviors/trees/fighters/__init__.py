#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\fighters\__init__.py
from behaviors.actions import WaitAction
from behaviors.actions.ballparks import AlignToCoordinatesAction
from behaviors.actions.blackboards import BlackboardSetMessageAsNoneAction
from behaviors.actions.combat import KamikazeAttack
from behaviors.actions.fighterabilities import StopAbilityEffectOnTarget, NotifyAbilityActivationFailure, ActivateAbilityEffectOnPoint
from behaviors.behaviortree import BehaviorTree
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.composites import PrioritySelector, Sequence
from behaviors.conditions.blackboards import IsBlackboardValueNotNone, IsBlackboardValue3dVector
from behaviors.conditions.effects import IsEffectByAddressActive
from behaviors.decorators.modifiers import ForceSuccess, Uninterruptible
from behaviors.monitors.blackboards import BlackboardMessageMonitor
from brennivin.itertoolsext import Bundle
import ccpProfile
from fighters import ABILITY_SLOT_0, ABILITY_SLOT_1, ABILITY_SLOT_2
KAMIKAZE_ADDRESS = (ScopeTypes.Item, 'KAMIKAZE_ADDRESS')
KAMIKAZE_ABORT_ADDRESS = (ScopeTypes.Item, 'KAMIKAZE_ABORT_ADDRESS')
ABILITY_TARGET_SLOT0_ADDRESS = (ScopeTypes.Item, 'ABILITY_TARGET_SLOT0_ADDRESS')
ABILITY_START_EFFECTID_SLOT0_ADDRESS = (ScopeTypes.Item, 'ABILITY_START_EFFECTID_SLOT0_ADDRESS')
ABILITY_STOP_EFFECTID_SLOT0_ADDRESS = (ScopeTypes.Item, 'ABILITY_STOP_EFFECTID_SLOT0_ADDRESS')
ABILITY_TARGET_SLOT1_ADDRESS = (ScopeTypes.Item, 'ABILITY_TARGET_SLOT1_ADDRESS')
ABILITY_START_EFFECTID_SLOT1_ADDRESS = (ScopeTypes.Item, 'ABILITY_START_EFFECTID_SLOT1_ADDRESS')
ABILITY_STOP_EFFECTID_SLOT1_ADDRESS = (ScopeTypes.Item, 'ABILITY_STOP_EFFECTID_SLOT1_ADDRESS')
ABILITY_TARGET_SLOT2_ADDRESS = (ScopeTypes.Item, 'ABILITY_TARGET_SLOT2_ADDRESS')
ABILITY_START_EFFECTID_SLOT2_ADDRESS = (ScopeTypes.Item, 'ABILITY_START_EFFECTID_SLOT2_ADDRESS')
ABILITY_STOP_EFFECTID_SLOT2_ADDRESS = (ScopeTypes.Item, 'ABILITY_STOP_EFFECTID_SLOT2_ADDRESS')
ADDRESSES_BY_SLOT_ID = {ABILITY_SLOT_0: (ABILITY_TARGET_SLOT0_ADDRESS, ABILITY_START_EFFECTID_SLOT0_ADDRESS, ABILITY_STOP_EFFECTID_SLOT0_ADDRESS),
 ABILITY_SLOT_1: (ABILITY_TARGET_SLOT1_ADDRESS, ABILITY_START_EFFECTID_SLOT1_ADDRESS, ABILITY_STOP_EFFECTID_SLOT1_ADDRESS),
 ABILITY_SLOT_2: (ABILITY_TARGET_SLOT2_ADDRESS, ABILITY_START_EFFECTID_SLOT2_ADDRESS, ABILITY_STOP_EFFECTID_SLOT2_ADDRESS)}
ACTIVATION_FAILURE_REASON_ADDRESSES = {ABILITY_SLOT_0: (ScopeTypes.Item, 'ABILITY_FAILURE_REASON_SLOT0_ADDRESS'),
 ABILITY_SLOT_1: (ScopeTypes.Item, 'ABILITY_FAILURE_REASON_SLOT1_ADDRESS'),
 ABILITY_SLOT_2: (ScopeTypes.Item, 'ABILITY_FAILURE_REASON_SLOT2_ADDRESS')}

@ccpProfile.TimedFunction('behaviour::fighters::CreateFighterBehavior')
def CreateFighterBehavior():
    root = Sequence()
    root.AddSubTask(_CreateAbilitySlotBehavior(ABILITY_SLOT_0))
    root.AddSubTask(_CreateAbilitySlotBehavior(ABILITY_SLOT_1))
    root.AddSubTask(_CreateAbilitySlotBehavior(ABILITY_SLOT_2))
    root.AddSubTask(Sequence(Bundle(name='Kamikaze')).AddSubTask(BlackboardMessageMonitor(Bundle(messageAddress=KAMIKAZE_ADDRESS))).AddSubTask(ForceSuccess().AddSubTask(PrioritySelector().AddSubTask(Sequence(Bundle(name='Kamikaze')).AddSubTask(IsBlackboardValueNotNone(Bundle(valueAddress=KAMIKAZE_ADDRESS))).AddSubTask(KamikazeAttack(Bundle(name='Kamikaze', selectedTargetAddress=KAMIKAZE_ADDRESS, shouldAbortAddress=KAMIKAZE_ABORT_ADDRESS))).AddSubTask(BlackboardSetMessageAsNoneAction(Bundle(messageAddress=KAMIKAZE_ADDRESS)))))))
    root.AddSubTask(WaitAction(Bundle()))
    return root


@ccpProfile.TimedFunction('behaviour::fighters::_CreateAbilitySlotBehavior')
def _CreateAbilitySlotBehavior(abilitySlotID):
    description = 'Slot %s' % (abilitySlotID,)
    targetAddress, startEffectIDAddress, stopEffectIDAddress = ADDRESSES_BY_SLOT_ID[abilitySlotID]
    failureReasonAddress = ACTIVATION_FAILURE_REASON_ADDRESSES[abilitySlotID]
    root = Sequence(Bundle(name='Ability effect [%s]' % description))
    root.AddSubTask(BlackboardMessageMonitor(Bundle(messageAddress=startEffectIDAddress)))
    root.AddSubTask(BlackboardMessageMonitor(Bundle(messageAddress=stopEffectIDAddress)))
    root.AddSubTask(ForceSuccess().AddSubTask(PrioritySelector().AddSubTask(Sequence(Bundle(name='Start point-targeted-effect ability')).AddSubTask(IsBlackboardValueNotNone(Bundle(valueAddress=startEffectIDAddress))).AddSubTask(IsBlackboardValue3dVector(Bundle(valueAddress=targetAddress))).AddSubTask(PrioritySelector().AddSubTask(Uninterruptible().AddSubTask(Sequence().AddSubTask(AlignToCoordinatesAction(Bundle(coordinateAddress=targetAddress, timeoutSeconds=10, acceptableAngleDeviationDegrees=1))).AddSubTask(PrioritySelector().AddSubTask(IsEffectByAddressActive(Bundle(effectIDAddress=startEffectIDAddress))).AddSubTask(ActivateAbilityEffectOnPoint(Bundle(effectIDAddress=startEffectIDAddress, targetPoint=targetAddress, abilitySlotID=abilitySlotID, failureReasonAddress=failureReasonAddress)))))).AddSubTask(NotifyAbilityActivationFailure(Bundle(abilitySlotID=abilitySlotID)))).AddSubTask(BlackboardSetMessageAsNoneAction(Bundle(messageAddress=startEffectIDAddress)))).AddSubTask(Sequence(Bundle(name='Stop effect ability')).AddSubTask(IsBlackboardValueNotNone(Bundle(valueAddress=stopEffectIDAddress))).AddSubTask(StopAbilityEffectOnTarget(Bundle(effectIDAddress=stopEffectIDAddress, abilitySlotID=abilitySlotID, failureReasonAddress=failureReasonAddress))).AddSubTask(BlackboardSetMessageAsNoneAction(Bundle(messageAddress=stopEffectIDAddress))))))
    return root


def CreateFighterBehaviorTree():
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(CreateFighterBehavior())
    return behaviorTree
