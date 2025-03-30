#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\shipcasterSvc.py
from carbon.common.script.sys.service import Service
from eve.client.script.ui.inflight.selectedItemWnd import SelectedItemWnd

class ShipcasterSvc(Service):
    __guid__ = 'svc.shipcaster'
    __servicename__ = 'Shipcaster'
    __displayname__ = 'Shipcaster service'
    __startupdependencies__ = ['sessionMgr']
    __notifyevents__ = ['OnShipcasterTargetStateChanged']

    def JumpThroughShipcaster(self, shipcasterID, toSolarsystemID, toLandingPadID):
        self.LogNotice('Jump through Shipcaster', shipcasterID, toSolarsystemID, toLandingPadID)
        self.sessionMgr.PerformSessionChange('jump', sm.RemoteSvc('shipcasterTravelMgr').CmdJumpThroughShipcaster, shipcasterID, toSolarsystemID, toLandingPadID)

    def GetFactionLandingPads(self, factionID):
        return sm.RemoteSvc('shipCasterLandingPadMgr').GetFactionLandingPads(factionID)

    def GetAllLandingPads(self):
        return sm.RemoteSvc('shipCasterLandingPadMgr').GetAllLandingPads()

    def GetFactionsWithShipcaster(self):
        return sm.RemoteSvc('shipCasterLauncherMgr').GetFactionsWithShipcaster()

    def OnShipcasterTargetStateChanged(self, itemID):
        selectedItemWnd = SelectedItemWnd.GetIfOpen()
        if selectedItemWnd and selectedItemWnd.itemID == itemID:
            selectedItemWnd.OnItemIDSelected(itemID)
