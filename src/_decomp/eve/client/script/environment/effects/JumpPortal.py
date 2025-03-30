#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\JumpPortal.py
from eve.client.script.environment.effects.GenericEffect import ShipEffect

class JumpPortal(ShipEffect):
    __guid__ = 'effects.JumpPortal'

    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('JumpPortal: no effect defined')

    def Repeat(self, duration):
        if self.gfx is None:
            raise RuntimeError('JumpPortal: no effect defined')


class JumpPortalBO(JumpPortal):
    __guid__ = 'effects.JumpPortalBO'
