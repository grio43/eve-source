#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charactersheet.py
from caching.memoize import Memoize
from carbon.common.script.sys.service import Service
from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow

class CharacterSheet(Service):
    __exportedcalls__ = {'Show': []}
    __update_on_reload__ = 0
    __guid__ = 'svc.charactersheet'
    __notifyevents__ = ['ProcessSessionChange',
     'OnRankChange',
     'OnKillNotification',
     'OnSessionReset']
    __servicename__ = 'charactersheet'
    __displayname__ = 'Character Sheet Client Service'
    __dependencies__ = []
    __startupdependencies__ = ['settings', 'skills', 'neocom']

    def __init__(self):
        super(CharacterSheet, self).__init__()
        self.daysLeft = -1

    def Run(self, memStream = None):
        self.LogInfo('Starting Character Sheet')

    def Stop(self, memStream = None):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.Close()

    def OnSessionReset(self):
        self.Reset()

    def Reset(self):
        self.daysLeft = -1
        self._GetHomeStationInfo.clear_memoized()

    def ProcessSessionChange(self, isremote, session, change):
        if session.charid is None:
            self.Stop()
            self.Reset()

    @Memoize
    def _GetHomeStationInfo(self):
        return sm.RemoteSvc('charMgr').GetHomeStationRow()

    def GetHomeStationRow(self):
        return self._GetHomeStationInfo()

    def GetHomeStation(self):
        return self._GetHomeStationInfo().stationID

    @staticmethod
    def OnRankChange(oldrank, newrank):
        if not session.warfactionid:
            return
        rankLabel, _ = sm.GetService('facwar').GetRankLabel(session.warfactionid, newrank)
        if newrank > oldrank:
            blinkMsg = cfg.GetMessage('RankGained', {'rank': rankLabel}).text
        else:
            blinkMsg = cfg.GetMessage('RankLost', {'rank': rankLabel}).text
        sm.GetService('neocom').Blink('militia', blinkMsg)

    @staticmethod
    def ForceShowSkillHistoryHighlighting(skillTypeIds):
        CharacterSheetWindow.OpenSkillHistoryHilightSkills(skillTypeIds)

    @staticmethod
    def OpenPlexPanel():
        CharacterSheetWindow.OpenPLEX()

    @staticmethod
    def OnKillNotification():
        sm.StartService('objectCaching').InvalidateCachedMethodCall('charMgr', 'GetRecentShipKillsAndLosses', 25, None)

    def Show(self):
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
            return wnd

    @staticmethod
    def GetWnd(getnew = 0):
        if not getnew:
            return CharacterSheetWindow.GetIfOpen()
        else:
            return CharacterSheetWindow.ToggleOpenClose()
