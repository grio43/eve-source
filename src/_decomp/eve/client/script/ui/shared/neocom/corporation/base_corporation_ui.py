#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\base_corporation_ui.py
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING, SERVICE_START_PENDING
import uthread
import carbonui.const as uiconst
import localization
import log
from eve.client.script.ui.shared.dockedUI.lobbyWnd import LobbyWnd
from eve.client.script.ui.shared.neocom.Alliances.all_ui_applications import ApplyToAllianceWnd
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.shared.neocom.corporation.corp_ui_bulletins import EditCorpBulletin
from eve.client.script.ui.shared.neocom.corporation.corpVotingWindow import CorpVotingWindow
from eve.client.script.ui.shared.neocom.corporation.corporationWindow import CorporationWindow
from eve.client.script.ui.shared.neocom.corporation.memberDetails import OpenMemberDetails
from eve.common.script.sys import idCheckers
from eveexceptions import UserError
from locks import TempLock

class _ShowLoad(object):

    def __init__(self, corpUI, windowKey):
        self.corpUI = corpUI
        self.wnd = None
        self.loadKey = windowKey
        self.loadLock = TempLock(self.loadKey)

    def __enter__(self):
        self.wnd = self.corpUI.GetWnd()
        if self.wnd is not None and not self.wnd.destroyed:
            self.wnd.ShowLoad()
        self.loadLock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.wnd is not None and not self.wnd.destroyed:
            self.wnd.HideLoad()
        self.loadLock.release()
        if exc_type is not None:
            log.LogException()


class CorporationUI(Service):
    __exportedcalls__ = {'Show': [],
     'ShowLoad': [],
     'HideLoad': [],
     'ResetWindow': [],
     'GetMemberDetails': [],
     'ApplyToJoinAlliance': []}
    __guid__ = 'svc.corpui'
    __notifyevents__ = ['ProcessSessionChange',
     'OnSessionChanged',
     'DoSessionChanging',
     'ProcessUIRefresh']
    __servicename__ = 'corpui'
    __displayname__ = 'Corporation UI Client Service'
    __dependencies__ = ['corp']
    __update_on_reload__ = 0

    def __init__(self):
        Service.__init__(self)
        self.wasVisible = 0
        corpUISignals.on_vote_case_changed.connect(self.OnVoteCaseChanged)
        corpUISignals.on_vote_cast.connect(self.OnVoteCast)
        corpUISignals.on_corporation_application_changed.connect(self.OnCorporationApplicationChanged)

    def Run(self, memStream = None):
        self.LogInfo('Starting Corporation')
        self.state = SERVICE_START_PENDING
        self.locks = {}
        self.ResetWindow()
        self.state = SERVICE_RUNNING

    def Stop(self, memStream = None):
        wnd = self.GetWnd()
        if wnd and not wnd.destroyed:
            wnd.Close()

    def ProcessUIRefresh(self):
        wnd = CorporationWindow.GetIfOpen()
        showWindow = False
        if wnd and not wnd.IsHidden():
            showWindow = True
        self.Stop()
        self.ResetWindow(bShowIfVisible=showWindow)

    def DoSessionChanging(self, isRemote, session, change):
        self.wasVisible = 0
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed and wnd.state != uiconst.UI_HIDDEN:
            self.wasVisible = 1
        if 'charid' in change and change['charid'][0] or 'userid' in change and change['userid'][0]:
            sm.StopService(self.__guid__[4:])

    def ProcessSessionChange(self, isRemote, session, change):
        if 'corpid' in change and bool(session.charid):
            sm.StartService('objectCaching').InvalidateCachedMethodCall('corporationSvc', 'GetEmploymentRecord', session.charid)

    def OnSessionChanged(self, isremote, sess, change):
        if 'corpid' in change or 'corprole' in change or 'allianceid' in change:
            self.ResetWindow(self.wasVisible)
        if 'corpid' in change or 'allianceid' in change:
            bulletinWnd = EditCorpBulletin.GetIfOpen()
            if bulletinWnd and ('corpid' in change or bulletinWnd.IsAlliance()):
                bulletinWnd.Close()

    def GetWnd(self, haveto = 0, panel_id = None, sub_panel_id = None):
        wnd = CorporationWindow.GetIfOpen()
        if not wnd and haveto:
            wnd = CorporationWindow.Open(panel_id=panel_id)
        return wnd

    def ResetWindow(self, bShowIfVisible = 0):
        uthread.Lock(self)
        try:
            wnd = self.GetWnd()
            if wnd and not wnd.destroyed:
                wnd.Close()
            if bShowIfVisible:
                self.Show()
        finally:
            uthread.UnLock(self)

    def Show(self, panel_id = None, sub_panel_id = None):
        wnd = self.GetWnd(0)
        if not wnd:
            wnd = self.GetWnd(1, panel_id)
        if not wnd or wnd.destroyed:
            return
        wnd.Maximize()
        wnd.SelectPanel(panel_id)

    def ShowLoad(self, lockKey = None):
        if lockKey:
            return _ShowLoad(self, lockKey)
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.ShowLoad()
            return 1

    def HideLoad(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.HideLoad()
            return 1

    def GetMemberDetails(self, charid):
        OpenMemberDetails(charid)

    def GetMemberHangarsData(self):
        hangars = {}
        corpMemberIDs = sm.GetService('corp').GetMemberIDs()
        cfg.eveowners.Prime(corpMemberIDs)
        for charID in corpMemberIDs:
            hangars[charID, charID] = localization.GetByLabel('UI/Station/Hangar/MembersHangarLabel', charID=charID)

        return hangars

    def ApplyToJoinAlliance(self, allianceID):
        if session.allianceid is not None:
            self.LogError('ApplyToJoinAlliance called by player already in an alliance.')
            return False
        if not session.corprole & const.corpRoleDirector or session.charid != sm.GetService('corp').GetCorporation().ceoID:
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/AccessRestrictions/OnlyForActiveCEO')})
        if not sm.GetService('corp').CheckCanApplyToJoinAlliance(allianceID):
            return
        wnd = ApplyToAllianceWnd.Open(allianceID=allianceID)
        if wnd.ShowModal() == 1:
            applicationText = wnd.result
        else:
            applicationText = None
        if applicationText is not None:
            sm.GetService('corp').ApplyToJoinAlliance(allianceID, applicationText)

    def OnVoteCaseChanged(self, corporationID, voteCaseID):
        if not self.GetWnd():
            corpVW = CorpVotingWindow.GetIfOpen(windowID='%s_%d' % (CorpVotingWindow.default_name, corporationID))
            if corpVW:
                corpVW.corpVotesPanel.OnVoteCaseChanged(corporationID, voteCaseID)

    def OnVoteCast(self, corporationID, voteCaseID):
        if not self.GetWnd():
            corpVW = CorpVotingWindow.GetIfOpen(windowID='%s_%d' % (CorpVotingWindow.default_name, corporationID))
            if corpVW:
                corpVW.corpVotesPanel.OnVoteCast(corporationID, voteCaseID)

    def OnCorporationApplicationChanged(self, corpID, applicantID, applicationID, newApplication):
        if applicantID == session.charid and idCheckers.IsStation(session.locationid):
            lobby = LobbyWnd.GetIfOpen()
            if lobby:
                lobby.ShowOffices()
