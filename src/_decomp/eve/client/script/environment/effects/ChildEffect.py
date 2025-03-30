#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\ChildEffect.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT, STOP_REASON_BALL_REMOVED
import trinity
import os.path as path

class ChildEffect(GenericEffect):
    __guid__ = 'effects.ChildEffect'

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(ChildEffect, self).__init__(trigger, effect, graphicFile)
        self.ball = self.GetEffectShipBall()
        fileName = path.basename(self.graphicFile)
        self.fxName = path.splitext(fileName)[0].lower()
        self.effect = trinity.Load(self.graphicFile)

    def Start(self, duration):
        self._AddEffectToTarget()
        self.effect.StartControllers()

    def Stop(self, reason = STOP_REASON_DEFAULT):
        self._RemoveEffectFromTarget()
        self.effect = None
        self.ball = None

    def Repeat(self, duration):
        self._RemoveEffectFromTarget()
        self._AddEffectToTarget()

    def _AddEffectToTarget(self):
        if not hasattr(self.ball, 'model') or self.ball.model is None:
            return False
        if len(self.ball.model.effectChildren) > 0:
            for child in self.ball.model.effectChildren:
                if child.name.lower() == self.fxName:
                    return False

        try:
            self.ball.AddChildEffect(self.effect)
            return True
        except AttributeError:
            return False

    def _RemoveEffectFromTarget(self):
        self.ball.RemoveChildEffect(self.effect)
