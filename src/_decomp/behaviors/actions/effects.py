#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\effects.py
import logging
import random
from ballpark.messenger.const import MESSAGE_ON_EFFECT_STOPPED
from behaviors import status
from behaviors.tasks import Task
from behaviors.utility.ballparks import get_slim_item, get_ship_balls_in_bubble
from behaviors.utility.dogmatic import type_has_effect, try_stop_effect, get_default_effect_id_for_type
from ccpProfile import TimedFunction
from dogma.const import attributeRateOfFire
from eveexceptions import UserError
logger = logging.getLogger(__name__)
TARGET_ATTACK_GRAPHIC_EFFECT = 'effects.Laser'

class PlayOneShotStretchEffectAction(Task):

    @TimedFunction('behaviors::actions::effects::PlayOneShotStretchEffectAction::OnEnter')
    def OnEnter(self):
        sourceId = self._GetEffectSourceId()
        targetId = self.GetLastBlackboardValue(self.attributes.effectTargetAddress)
        if sourceId is None or targetId is None:
            self.status = status.TaskFailureStatus
        else:
            sfx = self.context.ballpark.specialEffects
            moduleId = None
            if getattr(self.attributes, 'useEntityAsModule', False):
                moduleId = sourceId
            sfx.StartStretchEffect(sourceId, targetId, self.attributes.effectName, self._GetEffectDuration(), 1, moduleId)
            self.status = status.TaskSuccessStatus

    def _GetEffectSourceId(self):
        if self.HasAttribute('effectSourceAddress'):
            return self.GetLastBlackboardValue(self.attributes.effectSourceAddress)
        return self.context.myItemId

    def _GetEffectDuration(self):
        if self.HasAttribute('effectDurationAddress'):
            return self.GetLastBlackboardValue(self.attributes.effectDurationAddress)
        return self.attributes.effectDuration


class PlayOneShotTargetedShipEffectAction(Task):

    @TimedFunction('behaviors::actions::effects::PlayOneShotTargetedShipEffectAction::OnEnter')
    def OnEnter(self):
        targetId = self.GetLastBlackboardValue(self.attributes.effectTargetAddress)
        if targetId is None:
            self.status = status.TaskFailureStatus
        else:
            sfx = self.context.ballpark.specialEffects
            sfx.StartShipEffect(targetId, self.attributes.effectName, self.attributes.effectDuration, 1)
            self.status = status.TaskSuccessStatus


class PlayOneShotShipEffectAction(Task):

    @TimedFunction('behaviors::actions::effects::PlayOneShotShipEffectAction::OnEnter')
    def OnEnter(self):
        ballId = self.context.myItemId
        if getattr(self.attributes, 'effectTargetAddress', None):
            ballId = self.GetLastBlackboardValue(self.attributes.effectTargetAddress)
        sfx = self.context.ballpark.specialEffects
        sfx.StartShipEffect(ballId, self.attributes.effectName, self.attributes.effectDuration, 1, graphicInfo=getattr(self.attributes, 'graphicInfo', None))
        self.status = status.TaskSuccessStatus


class PlayStretchEffectAction(Task):

    def OnEnter(self):
        self.SetStatusToFailed()
        targetId = self.GetLastBlackboardValue(self.attributes.effectTargetAddress)
        graphicInfoAddress = self.attributes.graphicInfoAddress
        if graphicInfoAddress:
            graphicInfo = self.GetLastBlackboardValue(graphicInfoAddress)
        else:
            graphicInfo = None
        repeats = self.attributes.effectRepeats
        if targetId is not None:
            sfx = self.context.ballpark.specialEffects
            moduleId = None
            if getattr(self.attributes, 'useEntityAsModule', False):
                moduleId = self.context.myItemId
            sfx.StartStretchEffect(self.context.myItemId, targetId, self.attributes.effectName, self.get_effect_duration(), repeats, moduleId, graphicInfo=graphicInfo)
            self.SetStatusToSuccess()

    def get_effect_duration(self):
        if self.HasAttribute('effectDurationRandomVariance'):
            variance = self.attributes.effectDurationRandomVariance
            if variance > 0:
                difference = random.random() * variance - variance * 0.5
                return self.attributes.effectDuration + difference
        return self.attributes.effectDuration


class StopStretchEffectAction(Task):

    def OnEnter(self):
        self.SetStatusToFailed()
        targetId = self.GetLastBlackboardValue(self.attributes.effectTargetAddress)
        if targetId is not None:
            sfx = self.context.ballpark.specialEffects
            moduleId = None
            if getattr(self.attributes, 'useEntityAsModule', False):
                moduleId = self.context.myItemId
            sfx.StopStretchEffect(self.context.myItemId, targetId, self.attributes.effectName, moduleId)
            self.SetStatusToSuccess()


class SetDogmaAttributeValue(Task):

    def OnEnter(self):
        self.context.dogmaLM.SetAttributeValue(self.context.myItemId, self.attributes.attributeId, self.attributes.value)
        self.SetStatusToSuccess()


class SendDogmaAttributeValueAsMessage(Task):

    def OnEnter(self):
        attributeValue = self.context.dogmaLM.GetAttributeValue(self.context.myItemId, self.attributes.attributeId)
        scalar = getattr(self.attributes, 'scalar', None) or 1.0
        self.SendBlackboardValue(self.attributes.valueAddress, attributeValue * scalar)
        self.SetStatusToSuccess()


class ResetDogmaAttributeValue(Task):

    @TimedFunction('behaviors::actions::effects::ResetDogmaAttributeValue::OnEnter')
    def OnEnter(self):
        typeValue = self.context.dogmaLM.dogmaStaticMgr.GetTypeAttribute2(self.context.mySlimItem.typeID, self.attributes.attributeId)
        self.context.dogmaLM.SetAttributeValue(self.context.myItemId, self.attributes.attributeId, typeValue)
        self.status = status.TaskSuccessStatus


class ActivateTargetedEffect(Task):

    @TimedFunction('behaviors::actions::effects::ActivateTargetedEffect::OnEnter')
    def OnEnter(self):
        selectedTarget = self.GetLastBlackboardValue(self.attributes.selectedTargetAddress)
        self.SetStatusToSuccess()
        item = self.context.ballpark.inventory2.GetItem(self.context.myItemId)
        if selectedTarget:
            if self.context.dogmaLM.dogmaStaticMgr.TypeHasEffect(item.typeID, self.attributes.effectId):
                self.TryActivateEffect(item.ownerID, selectedTarget)

    @TimedFunction('behaviors::actions::effects::ActivateTargetedEffect::TryActivateEffect')
    def TryActivateEffect(self, ownerID, targetID):
        try:
            self.context.dogmaLM.ActivateWithContext(ownerID, self.context.myItemId, self.attributes.effectId, targetid=targetID, repeat=self.attributes.repeats)
            self.StartMonitoringEffectStoppedIfRequired()
            logger.debug('ActivateTargetedEffect: %s: start attacking target %s with effect %s', self.context.myItemId, targetID, self.attributes.effectId)
        except (UserError,) as e:
            if e.msg == 'EffectAlreadyActive2':
                self.StartMonitoringEffectStoppedIfRequired()
                logger.debug('ActivateTargetedEffect: %s: effect already active', self.context.myItemId)
            else:
                logger.debug('ActivateTargetedEffect: %s: failed to activate on target %s with effect %s: %s', self.context.myItemId, targetID, self.attributes.effectId, e)

    def CleanUp(self):
        if self.IsInvalid():
            return
        self.StopMonitoringEffectStopped()
        self.SetStatusToInvalid()

    def StartMonitoringEffectStopped(self):
        self.SubscribeItem(self.context.myItemId, MESSAGE_ON_EFFECT_STOPPED, self.OnStopEffect)

    def StopMonitoringEffectStopped(self):
        self.UnsubscribeItem(self.context.myItemId, MESSAGE_ON_EFFECT_STOPPED, self.OnStopEffect)

    def StartMonitoringEffectStoppedIfRequired(self):
        if self.attributes.shouldResetBehaviorOnEffectStopped:
            self.StartMonitoringEffectStopped()

    def OnStopEffect(self, effectId):
        if self.IsInvalid():
            return
        if effectId == self.attributes.effectId:
            self.behaviorTree.RequestReset(requestedBy=self)


class ActivateEffect(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        item = self.context.ballpark.inventory2.GetItem(self.context.myItemId)
        self.TryActivateEffect(item.ownerID)

    def TryActivateEffect(self, ownerID):
        effect_id = self.GetEffectId()
        try:
            self.context.dogmaLM.ActivateWithContext(ownerID, self.context.myItemId, effectID=effect_id, repeat=self.GetRepeats(), context=self.GetContext())
            logger.debug('ActivateEffect: %s: start attacking effect %s', self.context.myItemId, effect_id)
        except (UserError,) as e:
            logger.debug('ActivateEffect: %s: failed to activate effect %s: %s', self.context.myItemId, effect_id, e)

    def GetContext(self):
        return getattr(self.attributes, 'contextDict', None)

    def GetEffectId(self):
        return self.attributes.effectId

    def GetRepeats(self):
        return self.attributes.repeats


class ActivateDefaultEffect(ActivateEffect):

    def GetEffectId(self):
        return get_default_effect_id_for_type(self, self.context.mySlimItem.typeID)


class MockTargetAttack(Task):

    def OnEnter(self):
        self.SetStatusToFailed()
        targetId = self.GetLastBlackboardValue(self.attributes.targetIdAddress)
        if targetId is not None:
            duration = self.context.dogmaLM.GetAttributeValue(self.context.myItemId, attributeRateOfFire)
            sfx = self.context.ballpark.specialEffects
            sfx.StartStretchEffect(self.context.myItemId, targetId, TARGET_ATTACK_GRAPHIC_EFFECT, duration, 99, self.context.myItemId)
            self.SetStatusToSuccess()


class StopMockTargetAttack(Task):

    def OnEnter(self):
        self.SetStatusToFailed()
        targetId = self.GetLastBlackboardValue(self.attributes.targetIdAddress)
        if targetId is not None:
            sfx = self.context.ballpark.specialEffects
            sfx.StopStretchEffect(self.context.myItemId, targetId, TARGET_ATTACK_GRAPHIC_EFFECT, self.context.myItemId)
            self.SetStatusToSuccess()


class SendDogmaEffectIdAsMessage(Task):

    def OnEnter(self):
        self.SendBlackboardValue(self.attributes.effectIdAddress, self.attributes.effectId)
        self.SetStatusToSuccess()


class StopEffect(Task):

    @TimedFunction('behaviors::actions::effects::StopEffect::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        effect_id = self._get_effect_id()
        if not effect_id:
            logger.warn('Behavior=%s does not have effect=%s authored for task=%s', self.behaviorTree.GetBehaviorId(), effect_id)
            return
        if not type_has_effect(self, self.context.mySlimItem.typeID, effect_id):
            logger.warn('Behavior=%s entity=%s is missing effect=%s', self.behaviorTree.GetBehaviorId(), self.context.mySlimItem.typeID, effect_id)
            return
        self.SetStatusToSuccess()
        self._stop_effect(effect_id)

    def _get_effect_id(self):
        return self.attributes.effectId

    def _stop_effect(self, effect_id):
        try_stop_effect(self, effect_id, forced=self._is_stop_forced())

    def _is_stop_forced(self):
        return self.attributes.forcedStop


class ReplaceNebulaForPlayersInBubble(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        nebula_path = 'res:/dx9/scene/abyssal/ad01_a_cube.dds'
        for ball_id in get_ship_balls_in_bubble(self, self.context.myBall.newBubbleId):
            slim_item = get_slim_item(self, ball_id)
            sm.GetService('machoNet').SinglecastByCharID(slim_item.charID, 'OnReplaceNebula', nebula_path)
