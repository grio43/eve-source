#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\deathzoneSvc.py
import gametime
from carbon.common.script.sys.service import Service
from enum import Enum
from eve.client.script.ui.services.deathzone.deathzoneUIController import DeathZoneUIController

class DeathzoneSvc(Service):
    __guid__ = 'svc.deathzoneSvc'
    __displayname__ = 'Deathzone client service'
    __exportedcalls__ = {'InDeathZone': [],
     'GetHullDamageFraction': []}
    __startupdependencies__ = ['machoNet', 'heroNotification', 'sceneManager']
    __notifyevents__ = ['OnSessionChanged', 'OnDeathzoneStateUpdate']
    placeholderDeathzoneUITasklet = None
    trackingData = None

    def Run(self, *args, **kwargs):
        super(DeathzoneSvc, self).Run(*args, **kwargs)
        self.deathZoneUIController = DeathZoneUIController(self.heroNotification, self.sceneManager)
        self.trackingData = None

    def InDeathZone(self):
        return self.trackingData is not None

    def GetHullDamageFraction(self):
        if self.trackingData:
            return self.trackingData.GetHullDamageFractionPerTick(gametime.GetSimTime())
        return 0.0

    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid2' in change:
            self.trackingData = None
            self.deathZoneUIController.Remove()

    def OnDeathzoneStateUpdate(self, solarsystemID, shipID, trackingData):
        if solarsystemID != session.solarsystemid2 or shipID != session.shipid:
            return
        self.trackingData = trackingData
        if trackingData is None:
            self.deathZoneUIController.EnterSafeZoneState()
        else:
            self.deathZoneUIController.EnterDeathZoneState(trackingData)
