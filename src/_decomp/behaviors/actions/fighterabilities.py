#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\fighterabilities.py
from ballpark.const import DESTINY_MODE_FOLLOW, DESTINY_MODE_WARP
from behaviors.actions.effects import logger
from behaviors.behaviortree import UnrecoverableBehaviorError
from behaviors.entity import NPCWarpError
from behaviors.tasks import Task
from ccpProfile import TimedFunction
from eve.common.lib.appConst import ACT_IDX_START, ACT_IDX_DURATION
from eve.common.script.mgt.fighterConst import TUBE_STATE_INSPACE
from eve.server.script.mgt.fighters import GetAbilityRegistryForSolarsystem, GetControlledFighterRegistryForSolarsystem, GetTubeLoaderForSolarsystem, GetFighterClientNotifierSingleton
from eve.server.script.mgt.fighters.abilities.activators import StartFighterAbilityDogmaEffect
from eveexceptions import UserError
from fighters import MAX_SCOOP_DISTANCE, FIGHTER_MIN_WARP_DISTANCE

class ActivateAbilityEffectBaseTask(Task):

    def GetSelfAsItem(self):
        return self.context.ballpark.inventory2.GetItem(self.context.myItemId)

    def GetTargetAsItem(self, targetId):
        return self.context.ballpark.inventory2.GetItem(targetId)

    @TimedFunction('behaviors::actions::fighterAbilities::ActivateAbilityEffectBaseTask::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        self.SendBlackboardValue(self.attributes.failureReasonAddress, None)
        if self.ActivateAbility():
            self.SetStatusToSuccess()
            startTime, durationMs = self._GetEffectCycleTiming()
            abilityRegistry = GetAbilityRegistryForSolarsystem(self.context.ballpark.solarsystemID)
            abilityRegistry.OnAbilityActivationSucceeded(self.context.myItemId, self.attributes.abilitySlotID, startTime, durationMs)

    def ActivateAbility(self):
        raise NotImplementedError()

    def _GetEffectCycleTiming(self):
        effectID = self.GetLastBlackboardValue(self.attributes.effectIDAddress)
        activationData = self.context.dogmaLM.GetActiveEffectData(self.context.myItemId, effectID)
        startTime = activationData[ACT_IDX_START]
        durationMs = activationData[ACT_IDX_DURATION]
        return (startTime, durationMs)

    @TimedFunction('behaviors::actions::fighterAbilities::ActivateAbilityEffectBaseTask::TryActivateEffect')
    def TryActivateEffect(self, targetID):
        activated = False
        selfItem = self.GetSelfAsItem()
        if selfItem is None:
            return False
        effectID = self.GetAbilityEffectID()
        if effectID is None:
            return False
        if targetID is not None:
            targetItem = self.GetTargetAsItem(targetID)
            if targetItem is None:
                return False
            if not self.IsTargetWithinEffectRange(effectID, targetID):
                return False
        try:
            abilityRegistry = GetAbilityRegistryForSolarsystem(self.context.ballpark.solarsystemID)
            activationContext = abilityRegistry.GetActivationContext(self.context.myItemId, self.attributes.abilitySlotID)
            if activationContext is not None:
                StartFighterAbilityDogmaEffect(effectID, activationContext, targetID)
                activated = True
        except UserError as e:
            logger.debug('Entity: %s - failed to activate effect: %s', self.context.myItemId, effectID)
            self.SendBlackboardValue(self.attributes.failureReasonAddress, e)

        return activated

    def GetAbilityEffectID(self):
        selfItem = self.GetSelfAsItem()
        typeID = selfItem.typeID
        effectID = self.GetLastBlackboardValue(self.attributes.effectIDAddress)
        if effectID is None:
            return
        if not self.context.ballpark.dogmaLM.dogmaStaticMgr.TypeHasEffect(typeID, effectID):
            return
        return effectID

    @TimedFunction('behaviors::actions::fighterAbilities::ActivateAbilityEffectBaseTask::IsTargetWithinEffectRange')
    def IsTargetWithinEffectRange(self, effectID, targetId):
        effect = self.context.ballpark.dogmaLM.dogmaStaticMgr.GetEffect(effectID)
        if not effect.falloffAttributeID and effect.rangeAttributeID is not None:
            distance = self.context.ballpark.GetSurfaceDist(self.context.myItemId, targetId)
            typeEffectRange = self.context.ballpark.dogmaLM.GetAttributeValue(self.context.myItemId, effect.rangeAttributeID)
            if distance > typeEffectRange:
                return False
        return True


class ActivateAbilityEffectOnPoint(ActivateAbilityEffectBaseTask):

    def ActivateAbility(self):
        targetPoint = self.GetLastBlackboardValue(self.attributes.targetPoint)
        if targetPoint is None:
            return False
        return self.TryActivateEffect(None)


class StopAbilityEffectOnTarget(Task):

    @TimedFunction('behaviors::actions::fighterAbilities::StopAbilityEffectOnTarget::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        fighterID = self.context.myItemId
        item = self.context.ballpark.inventory2.GetItem(fighterID)
        effectID = self.GetLastBlackboardValue(self.attributes.effectIDAddress)
        if effectID is not None:
            if self.context.dogmaLM.dogmaStaticMgr.TypeHasEffect(item.typeID, effectID):
                self.TryStopEffect(fighterID, effectID)

    @TimedFunction('behaviors::actions::fighterAbilities::StopAbilityEffectOnTarget::TryStopEffect')
    def TryStopEffect(self, fighterID, effectID):
        try:
            if self.context.dogmaLM.GetActiveEffectData(fighterID, effectID) is None:
                failureReason = self.GetLastBlackboardValue(self.attributes.failureReasonAddress)
                abilityRegistry = GetAbilityRegistryForSolarsystem(self.context.ballpark.solarsystemID)
                abilityRegistry.OnAbilityDeactivated(fighterID, self.attributes.abilitySlotID, failureReason)
            else:
                self.context.dogmaLM.StopEffect(effectID, fighterID)
        except UserError:
            pass


class NotifyAbilityActivationFailure(Task):

    @TimedFunction('behaviors::actions::fighterAbilities::NotifyAbilityActivationFailure::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        abilityRegistry = GetAbilityRegistryForSolarsystem(self.context.ballpark.solarsystemID)
        abilityRegistry.OnAbilityActivationFailed(self.context.myItemId, self.attributes.abilitySlotID)
