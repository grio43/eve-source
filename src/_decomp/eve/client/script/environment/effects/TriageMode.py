#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\TriageMode.py
from eve.client.script.environment.effects.GenericEffect import STOP_REASON_DEFAULT
from eve.client.script.environment.effects.shipRenderEffect import ShipRenderEffect

class TriageMode(ShipRenderEffect):
    __guid__ = 'effects.TriageMode'

    def Stop(self, reason = STOP_REASON_DEFAULT):
        ShipRenderEffect.Stop(self, reason)
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        shipBall.SetControllerVariable('InSiegeMode', False)

    def Start(self, duration):
        ShipRenderEffect.Start(self, duration)
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        shipBall.SetControllerVariable('InSiegeMode', True)

    def Repeat(self, duration):
        ShipRenderEffect.Repeat(self, duration)
