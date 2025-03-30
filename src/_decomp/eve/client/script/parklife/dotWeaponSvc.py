#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\dotWeaponSvc.py
from carbon.common.script.sys.service import CoreService
from dotWeapons.client.incomingDotTracker import IncomingDotTracker

class DotWeaponSvc(CoreService):
    __guid__ = 'svc.dotWeaponSvc'

    def Run(self, memStream = None):
        self.incomingDotTracker = IncomingDotTracker()
