#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\enlistmentFlow\enlistCont.py
import uthread2
from carbonui import TextAlign, TextBody
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
import eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.enlistmentUtil as enlistmentUtil
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.infoIcon import MoreInfoIconBeta
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsPlayerCorporation
from eve.common.script.util.facwarCommon import IsPirateFWFaction
from factionwarfare.client.enlistmentChecks import EnlistmentChecksObject
from jobboard.client import get_fw_enlistment_job, job_board_signals
from localization import GetByLabel
import eve.common.lib.appConst as appConst
import factionwarfare.client.enrollmentConst as enrollmentConst

class EnlistCont(ContainerAutoSize):
    default_name = 'enlistCont'
    default_align = uiconst.TOBOTTOM
    default_alignMode = uiconst.TOTOP
    default_minHeight = 130
    __notifyevents__ = ['OnSessionChanged', 'OnEnlistmentStateUpdated_Local']

    def ApplyAttributes(self, attributes):
        super(EnlistCont, self).ApplyAttributes(attributes)
        self.factionID = None
        self.currentLoadingID = 0
        self.warningChecks = EnlistmentChecksObject()
        self.facWarSvc = sm.GetService('facwar')
        self.warningsCont = ContainerAutoSize(name='warningsCont', parent=self, align=uiconst.TOTOP, padBottom=10)
        self.btnCont = ContainerAutoSize(name='btnCont', parent=self, align=uiconst.TOTOP)
        self.enlistBtns = ButtonGroup(parent=self.btnCont, align=uiconst.CENTERTOP, orientation=uiconst.Axis.VERTICAL, button_size_mode=ButtonSizeMode.EQUAL, padLeft=20, padRight=20)
        sm.RegisterNotify(self)
        job_board_signals.on_tracked_jobs_changed.connect(self.OnTrackedJobsChanged)

    def Close(self):
        job_board_signals.on_tracked_jobs_changed.disconnect(self.OnTrackedJobsChanged)
        super(EnlistCont, self).Close()

    def LoadEnlist(self, factionID):
        loadingID = self.currentLoadingID + 1
        self.currentLoadingID = loadingID
        self.warningsCont.Flush()
        self.enlistBtns.Flush()
        self.factionID = factionID
        warningsToAdd = []
        btnsToAdd = []
        if session.warfactionid:
            if session.warfactionid != self.factionID:
                warningsToAdd = self._GetWarningsToLoad()
            btnsToAdd += self._GetAlreadyListedBtns()
        else:
            warningsToAdd = self._GetWarningsToLoad()
            btnsToAdd += self._GetNotEnlistedBtns()
        if self.currentLoadingID != loadingID:
            return
        for warningID in warningsToAdd:
            self._AddWarning(warningID)

        for btnData in btnsToAdd:
            self._AddButton(btnData)

    def _GetAlreadyListedBtns(self):
        btnsToAdd = []
        inThisFaction = session.warfactionid and session.warfactionid == self.factionID
        if inThisFaction:
            btnsToAdd += self._GetRetireBtns()
        elif self.factionID == self.facWarSvc.GetCurrentStationFactionID():
            btnsToAdd.append(BtnToAddData('UI/FactionWarfare/Enlistment/JoinNow', None, True))
        else:
            btnsToAdd.append(BtnToAddData('UI/FactionWarfare/Enlistment/InitiateEnlistment', self.InitiateEnlistment, True))
        return btnsToAdd

    def _GetRetireBtns(self):
        btnsToAdd = []
        if idCheckers.IsNPC(session.corpid) and session.warfactionid:
            btnsToAdd.append(BtnToAddData('UI/FactionWarfare/Retire', enlistmentUtil.Retire))
        elif sm.GetService('fwEnlistmentSvc').IsEnlistedDirectly():
            btnsToAdd.append(BtnToAddData('UI/FactionWarfare/Retire', enlistmentUtil.RemoveDirectEnlistment))
        else:
            hasReqCorporationRole = session.corprole & appConst.corpRoleDirector == appConst.corpRoleDirector
            if hasReqCorporationRole:
                factionalWarStatus = self.facWarSvc.GetCorpFactionalWarStatus()
                fwStatus = factionalWarStatus.status
                if fwStatus == appConst.facwarCorporationActive:
                    if session.allianceid:
                        btnsToAdd.append(BtnToAddData('UI/FactionWarfare/RetireAlliance', enlistmentUtil.RetireAlliance))
                    else:
                        btnsToAdd.append(BtnToAddData('UI/FactionWarfare/RetireCorporation', enlistmentUtil.RetireCorp))
                elif fwStatus == appConst.facwarCorporationLeaving:
                    btnsToAdd.append(BtnToAddData('UI/FactionWarfare/CancelRetirement', enlistmentUtil.CancelRetirement))
        return btnsToAdd

    def _AddButton(self, btnData):

        def CallFuncAndReload(*args):
            btnData.func()
            self.LoadEnlist(self.factionID)

        b = Button(parent=self.enlistBtns, align=uiconst.TOTOP, label=GetByLabel(btnData.labelPath), func=CallFuncAndReload, hint=btnData.hint)
        if btnData.isDisabled:
            b.Disable()
        return b

    def _GetNotEnlistedBtns(self):
        btnsToAdd = []
        if self.warningChecks.HasCorpApplicationPendingWithFactionWarning(self.factionID):
            hasReqCorporationRole = session.corprole & appConst.corpRoleDirector == appConst.corpRoleDirector
            if hasReqCorporationRole:
                btnsToAdd.append(BtnToAddData('UI/FactionWarfare/WithdrawApplication', self.CancelApplication))
        elif self.warningChecks.HasCorpApplicationPendingWithDifferentFactionWarning(self.factionID):
            pass
        elif not self.warningChecks.HasWrongLocationWarning(self.factionID):
            btnsToAdd += self._AddEnlistButtons()
        else:
            btnsToAdd += self._AddInitiateEnlistmentBtn()
        return btnsToAdd

    def JoinMilitia(self, *args):
        uthread2.StartTasklet(self.JoinMilitia_thread)

    def JoinMilitia_thread(self, *args):
        warFactionnIdBefore = session.warfactionid
        self.facWarSvc.JoinFactionAsCharacter(self.factionID, session.warfactionid)
        if not warFactionnIdBefore:
            for x in xrange(3):
                if session.warfactionid:
                    if IsPirateFWFaction(session.warfactionid):
                        sm.GetService('cmd').OpenInsurgencyDashboard()
                    else:
                        sm.GetService('cmd').OpenMilitia()
                    from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.fwEnlistmentWnd import FwEnlistmentWnd
                    FwEnlistmentWnd.CloseIfOpen()
                    break
                uthread2.sleep(1)

    def EnlistDirectly(self, *args):
        warFactionIdBefore = session.warfactionid
        sm.GetService('fwEnlistmentSvc').OnEnlistMeDirectly(self.factionID)
        if not warFactionIdBefore and session.warfactionid:
            if IsPirateFWFaction(session.warfactionid):
                sm.GetService('cmd').OpenInsurgencyDashboard()
            else:
                sm.GetService('cmd').OpenMilitia()
            from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.fwEnlistmentWnd import FwEnlistmentWnd
            FwEnlistmentWnd.CloseIfOpen()

    def _AddEnlistButtons(self):
        hasReqCorporationRole = session.corprole & appConst.corpRoleDirector == appConst.corpRoleDirector
        hasReqAllianceRole = hasReqCorporationRole and session.allianceid and sm.GetService('alliance').GetAlliance().executorCorpID == session.corpid
        characterBtnDisabled = self.IsButtonDisabled()
        charEnlistmentFunc = self.JoinMilitia
        if IsPlayerCorporation(session.corpid):
            charEnlistmentFunc = self.EnlistDirectly
            characterBtnDisabled = characterBtnDisabled or bool(self.warningChecks.HasDisallowedByCorpWarning(self.factionID))
        btnsToAdd = []
        btnsToAdd.append(BtnToAddData('UI/FactionWarfare/EnlistMe', charEnlistmentFunc, characterBtnDisabled))
        if hasReqCorporationRole:
            btnsToAdd.append(BtnToAddData('UI/FactionWarfare/EnlistCorporation', lambda *args: self.facWarSvc.JoinFactionAsCorporation(self.factionID, session.warfactionid), not hasReqCorporationRole))
        if hasReqAllianceRole:
            btnsToAdd.append(BtnToAddData('UI/FactionWarfare/EnlistAlliance', lambda *args: self.facWarSvc.JoinFactionAsAlliance(self.factionID, session.warfactionid), not hasReqAllianceRole))
        return btnsToAdd

    def _AddInitiateEnlistmentBtn(self):
        job = get_fw_enlistment_job(self.factionID)
        if job and job.is_tracked:
            buttonDisabled = True
        else:
            buttonDisabled = self.IsButtonDisabled()
        btnData = BtnToAddData('UI/FactionWarfare/Enlistment/InitiateEnlistment', self.InitiateEnlistment, buttonDisabled)
        jumpsToNearestStation, nearestStationID = self.facWarSvc.GetNearestFactionWarfareStationData(preferredFaction=self.factionID)
        if nearestStationID and session.stationid != nearestStationID:
            stationAndJumps = GetByLabel('UI/Corporations/CorpUIHome/StationAndJumps', station=nearestStationID, jumpCount=jumpsToNearestStation, jumps=jumpsToNearestStation)
            hint = '%s<br>%s' % (GetByLabel('UI/Agency/FactionWarfare/nearestMilitiaOffice'), stationAndJumps)
            btnData.hint = hint
        return [btnData]

    def IsButtonDisabled(self):
        buttonDisabled = self.warningChecks.HasAlreadyInFwWarning(self.factionID) or self.warningChecks.HasDisallowedByCorpWarning(self.factionID) or self.warningChecks.HasStandingWarning(self.factionID) or self.warningChecks.HasCooldownWarning(self.factionID)
        return buttonDisabled

    def LoadCharBtnTooltip(self, tooltipPanel, factionID, *args):
        tooltipPanel.state = uiconst.UI_NORMAL
        factionName = cfg.eveowners.Get(factionID).name
        linkUrl = '<a href=localsvc:method=ShowCorpDetails>'
        characterHint = GetByLabel('UI/FactionWarfare/CorpRestrictionsPreventDirectEnrollment', factionName=factionName, urlStart=linkUrl, urlEnd='</a>')
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=characterHint, wrapWidth=200, state=uiconst.UI_NORMAL)

    def CancelApplication(self, *args):
        enlistmentUtil.CancelApplication()

    def InitiateEnlistment(self, *args):
        job = get_fw_enlistment_job(self.factionID)
        if job is None:
            raise UserError('CustomNotify', {'notify': "Couldn't find the job to start"})
        if not job.is_tracked:
            job.toggle_tracked_by_player()
        else:
            job.add_tracked()
        from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.fwEnlistmentWnd import FwEnlistmentWnd
        FwEnlistmentWnd.CloseIfOpen()

    def _GetWarningsToLoad(self):
        warningsToAdd = []
        warningChecks = self.warningChecks
        if warningChecks.HasCorpApplicationPendingWithFactionWarning(self.factionID):
            warningsToAdd.append(enrollmentConst.WARNING_PENDING_SAME_FACTION)
        elif warningChecks.HasCorpApplicationPendingWithDifferentFactionWarning(self.factionID):
            warningsToAdd.append(enrollmentConst.WARNING_PENDING_ANOTHER_FACTION)
        else:
            if warningChecks.HasAlreadyInFwWarning(self.factionID):
                warningsToAdd.append(enrollmentConst.WARNING_ALREADY_IN_FW)
            if warningChecks.HasDisallowedByCorpWarning(self.factionID):
                warningsToAdd.append(enrollmentConst.WARNING_DISALLOWED_BY_CORP)
            if warningChecks.HasStandingWarning(self.factionID):
                warningsToAdd.append(enrollmentConst.WARNING_PENDING_STANDING)
            if warningChecks.HasTrackingThisFactionWarning(self.factionID) and warningChecks.HasWrongLocationWarning(self.factionID):
                warningsToAdd.append(enrollmentConst.WARNING_TRACKING_SAME_FACTION)
            if warningChecks.HasTrackingAnotherFactionWarning(self.factionID):
                warningsToAdd.append(enrollmentConst.WARNING_TRACKING_ANOTHER_FACTION)
            if warningChecks.HasWrongLocationWarning(self.factionID):
                warningsToAdd.append(enrollmentConst.WARNING_PENDING_WRONG_LOCATION)
            if warningChecks.HasCooldownWarning(self.factionID):
                warningsToAdd.append(enrollmentConst.WARNING_DIRECT_ENLISTMENT_COOLDOWN)
        return warningsToAdd

    def _AddWarning(self, warningValue):
        warningCont = ContainerAutoSize(parent=self.warningsCont, align=uiconst.TOTOP, alignMode=uiconst.CENTERTOP, minHeight=16, state=uiconst.UI_NORMAL, padTop=6)
        innerWarningCont = ContainerAutoSize(parent=warningCont, align=uiconst.CENTERTOP, alignMode=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        icon = MoreInfoIconBeta(parent=innerWarningCont, align=uiconst.CENTERLEFT, circleColor=eveColor.WARNING_ORANGE, questionMarkTexturePath='res:/UI/Texture/Classes/Enlistment/attention.png', state=uiconst.UI_DISABLED)
        text = enlistmentUtil.GetTextForWarning(warningValue)
        TextBody(text=text, parent=innerWarningCont, align=uiconst.TOPLEFT, left=20, color=eveColor.WARNING_ORANGE, maxWidth=200)
        innerWarningCont.GetHint = lambda *args: self.GetWarningHint(warningValue)

    def GetWarningHint(self, warningValue):
        if warningValue == enrollmentConst.WARNING_PENDING_STANDING:
            if IsPirateFWFaction(self.factionID):
                return GetByLabel('UI/FactionWarfare/Enlistment/WarningStandingPiratesLong')
        return enlistmentUtil.GetHintForWarning(warningValue)

    def OnSessionChanged(self, _isremote, _session, change):
        if 'stationid' in change:
            self.LoadEnlist(self.factionID)

    def OnTrackedJobsChanged(self, *args):
        self.LoadEnlist(self.factionID)

    def OnEnlistmentStateUpdated_Local(self, *args):
        self.LoadEnlist(self.factionID)


class BtnToAddData(object):

    def __init__(self, labelPath, func, isDisabled = False, hint = ''):
        self.labelPath = labelPath
        self.func = func
        self.isDisabled = isDisabled
        self.hint = hint
