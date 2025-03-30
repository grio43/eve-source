#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\accelerationGate.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect

class AccelerationGate(GenericEffect):
    __guid__ = 'effects.WarpGateEffect'

    def Start(self, duration):
        gateID = self.GetEffectShipID()
        targetID = self.GetEffectTargetID()
        gateBall = self.GetEffectShipBall()
        slimItem = self.fxSequencer.GetItem(gateID)
        if slimItem.dunMusicUrl is not None and targetID == eve.session.shipid:
            sm.GetService('dynamicMusic').SendMusicEvent(slimItem.dunMusicUrl.lower())
        self.PlayNamedChildAnimations(gateBall.model, 'Activation')
