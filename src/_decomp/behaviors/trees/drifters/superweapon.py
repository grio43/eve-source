#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\drifters\superweapon.py
from behaviors.actions.ballparks import FullStopAction, GetBallsInBubbleByOwnerIds, StoreSlimItemAttributeToBlackboard
from behaviors.actions.blackboards import BlackboardSetMessageAsNoneAction, BlackboardSetMessageToBooleanValueAction
from behaviors.actions.effects import SetDogmaAttributeValue, ResetDogmaAttributeValue, ActivateTargetedEffect
from behaviors.blackboards.scopes import ScopeTypes
from behaviors.composites import PrioritySelector, Sequence
from behaviors.conditions.blackboards import IsBlackboardValueTrue
from behaviors.conditions.entities import OwnerIsNpcCondition
from behaviors.const.combat import THREAT_TARGET_EVALUATOR
from behaviors.decorators.modifiers import Uninterruptible, ForceFailure
from behaviors.decorators.repeaters import RepeatWhileFailing
from behaviors.actions.combat import ActivateSuperWeaponOnTarget, StopCombatEffectsOnTarget, AddCharacterForPodding
from behaviors.monitors.superweapon import WaitForTurboShieldState
from brennivin.itertoolsext import Bundle
from behaviors.actions.combattargets import FindTarget, AcquireTargetLock
from behaviors.trees.combat import COMBAT_TARGETS_SET, COMBAT_EFFECTS
from dogma.const import attributeScanResolution, effectWarpScrambleForEntity
from inventorycommon.const import categoryShip, categoryEntity
from spacecomponents.common.components.turboshield import TURBO_SHIELD_STATE_RESISTIVE, TURBO_SHIELD_STATE_ACTIVE
SUPER_WEAPON_TARGET = (ScopeTypes.Item, 'SUPER_WEAPON_TARGET')
SUPER_WEAPON_READY = (ScopeTypes.Item, 'SUPER_WEAPON_READY')
SUPER_WEAPON_TARGET_OWNER = (ScopeTypes.Item, 'SUPER_WEAPON_TARGET_OWNER')
PODDING_TARGET_LIST = (ScopeTypes.EntityGroup, 'PODDING_TARGET_LIST')
OVERRIDE_SUPER_WEAPON_RESET = (ScopeTypes.Item, 'OVERRIDE_SUPER_WEAPON_RESET')

def CreateSuperWeaponBehavior():
    return PrioritySelector(Bundle(name='Super Weapon')).AddSubTask(ForceFailure().AddSubTask(PrioritySelector().AddSubTask(IsBlackboardValueTrue(Bundle(name='Should override Weapon Reset?', valueAddress=OVERRIDE_SUPER_WEAPON_RESET))).AddSubTask(Sequence(Bundle(name='Reset Weapon')).AddSubTask(WaitForTurboShieldState(Bundle(turboShieldState=TURBO_SHIELD_STATE_ACTIVE))).AddSubTask(BlackboardSetMessageToBooleanValueAction(Bundle(messageAddress=SUPER_WEAPON_READY, value=False)))))).AddSubTask(Sequence(Bundle(name='Enable Weapon')).AddSubTask(IsBlackboardValueTrue(Bundle(valueAddress=SUPER_WEAPON_READY))).AddSubTask(Uninterruptible().AddSubTask(Sequence(Bundle(name='Destroy someone')).AddSubTask(RepeatWhileFailing(Bundle(maxRepetitions=5)).AddSubTask(Sequence(Bundle(name='Pick target and lock quickly')).AddSubTask(BlackboardSetMessageAsNoneAction(Bundle(messageAddress=SUPER_WEAPON_TARGET))).AddSubTask(FindTarget(Bundle(potentialTargetListAddress=COMBAT_TARGETS_SET, selectedTargetAddress=SUPER_WEAPON_TARGET, includedCategories=[categoryShip, categoryEntity], onlyCheckLocalBubble=True, targetEvaluationFunction=THREAT_TARGET_EVALUATOR, primaryTargetIdAddress=COMBAT_TARGETS_SET))).AddSubTask(SetDogmaAttributeValue(Bundle(attributeId=attributeScanResolution, value=10000.0))).AddSubTask(AcquireTargetLock(Bundle(selectedTargetAddress=SUPER_WEAPON_TARGET))).AddSubTask(ResetDogmaAttributeValue(Bundle(attributeId=attributeScanResolution))))).AddSubTask(ActivateTargetedEffect(Bundle(selectedTargetAddress=SUPER_WEAPON_TARGET, effectId=effectWarpScrambleForEntity, repeats=None, shouldResetBehaviorOnEffectStopped=False))).AddSubTask(StopCombatEffectsOnTarget(Bundle(effectIds=COMBAT_EFFECTS))).AddSubTask(FullStopAction()).AddSubTask(StoreSlimItemAttributeToBlackboard(Bundle(targetAddress=SUPER_WEAPON_TARGET, messageAddress=SUPER_WEAPON_TARGET_OWNER, attributeName='ownerID'))).AddSubTask(ActivateSuperWeaponOnTarget(Bundle(selectedTargetAddress=SUPER_WEAPON_TARGET))).AddSubTask(PrioritySelector().AddSubTask(OwnerIsNpcCondition(Bundle(name='Skipping NPC owners', ownerIdAddress=SUPER_WEAPON_TARGET_OWNER))).AddSubTask(Sequence(Bundle(name='Add owner to pod list')).AddSubTask(AddCharacterForPodding(Bundle(characterAddress=SUPER_WEAPON_TARGET_OWNER, poddingTargetListAddress=PODDING_TARGET_LIST))).AddSubTask(GetBallsInBubbleByOwnerIds(Bundle(objectListAddress=COMBAT_TARGETS_SET, ownerListAddress=PODDING_TARGET_LIST))))).AddSubTask(BlackboardSetMessageToBooleanValueAction(Bundle(messageAddress=SUPER_WEAPON_READY, value=False)))))).AddSubTask(WaitForTurboShieldState(Bundle(turboShieldState=TURBO_SHIELD_STATE_RESISTIVE, messageAddress=SUPER_WEAPON_READY)))
