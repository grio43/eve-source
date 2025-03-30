#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\modules.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT

class VisualModuleEffect(GenericEffect):
    __guid__ = 'effects.VisualModuleEffect'

    def __init__(self, trigger, *args):
        super(VisualModuleEffect, self).__init__(trigger, *args)
        self.moduleTypeID = trigger.moduleTypeID
        self.shipBall = None
        self.shipBall = None
        self.module = None

    def Start(self, duration):
        super(VisualModuleEffect, self).Start(duration)
        self.shipBall = self.GetEffectShipBall()
        if self.shipBall is None:
            RuntimeError('VisualModuleEffect: no ship ball')
        self.shipBall.FitHardpoints(blocking=True)
        self.module = self.shipBall.modules.get(self.moduleID)
        if self.module is not None:
            self.module.StartShooting(True)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        super(VisualModuleEffect, self).Stop(reason)
        if self.module is not None:
            self.module.StopShooting()
        self.shipBall = None
        self.module = None
