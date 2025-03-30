#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\GenericMultiEffect.py
import blue
import trinity
from carbon.common.lib.const import MSEC
from eve.client.script.environment.effects.GenericEffect import GenericEffect
from eve.client.script.environment.effects.GenericEffect import STOP_REASON_DEFAULT
import logging
from fsdBuiltData.client.effectSequences import GetSequence, GetStops
from evegraphics.graphicEffects.effectPhasePlayer import PhasePlayer, GetStepsToPlayForPhase
log = logging.getLogger(__name__)

class GenericMultiEffect(GenericEffect):
    __guid__ = 'effects.GenericMultiEffect'

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(GenericMultiEffect, self).__init__(trigger, effect, graphicFile)
        self.graphicFile = 'res:/fisfx/cloaking/multieffect/mf_cloakedobject_01a.red'
        self.effect = trinity.Load(self.graphicFile)

    def GetEffectTarget(self, target):
        if target == 'SELF':
            return self.GetEffectShipBall().model
        if target == 'POSTPROCESS':
            return self.fxSequencer.GetScene().postprocess
        if target == 'PLAYER_SHIP':
            pass
        elif target == 'NEAREST_SHIP':
            pass
        elif target == 'NEAREST_STATION':
            pass
        elif target == 'SUN':
            pass
        elif target == 'NEAREST_PLANET':
            pass

    def Start(self, duration):
        trinity.WaitForResourceLoads()
        for index, target in self.graphicInfo['effectTargets'].items():
            self.effect.parameters[index].object = self.GetEffectTarget(target)

        scene = self.fxSequencer.GetScene()
        scene.objects.append(self.effect)
        self.effect.StartControllers()

    def Stop(self, reason = STOP_REASON_DEFAULT):
        for each in self.effect.parameters:
            each.object = None

        scene = self.fxSequencer.GetScene()
        scene.objects.fremove(self.effect)

    def UpdateGraphicInfo(self, newGraphicInfo):
        pass
