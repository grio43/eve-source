#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\Alliances\all_ui_applications.py
import localization
import log
import utillib
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.util import uix
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from appConst import allianceApplicationRejected, allianceApplicationNew, allianceApplicationAccepted, allianceApplicationEffective
from eve.client.script.ui.control import eveIcon, eveLabel, eveScroll
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eveexceptions import UserError
STATUSDICT = {allianceApplicationNew: 'UI/Corporations/CorporationWindow/Alliances/Applications/New',
 allianceApplicationAccepted: 'UI/Corporations/CorporationWindow/Alliances/Applications/Accepted',
 allianceApplicationEffective: 'UI/Corporations/CorporationWindow/Alliances/Applications/Effective',
 allianceApplicationRejected: 'UI/Corporations/CorporationWindow/Alliances/Applications/Rejected'}

def _GetApplicationStatusStr(status):
    try:
        label = STATUSDICT[status]
    except KeyError:
        return ''

    return localization.GetByLabel(label)


class FormAlliancesApplications(Container):
    __guid__ = 'form.AlliancesApplications'
    __nonpersistvars__ = []
    is_loaded = False

    def Load(self, *args):
        if self.is_loaded:
            return
        self.is_loaded = True
        self.sr.rejectedContainer = Container(name='rejectedContainer', align=uiconst.TOTOP, parent=self, pos=(0, 0, 0, 18))
        showRejectedLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/ShowRejected')
        self.sr.viewRejected = Checkbox(text=showRejectedLabel, parent=self.sr.rejectedContainer, settingsKey='viewRejected', checked=0, callback=self.CheckBoxChecked, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         const.defaultPadding,
         200,
         0))
        self.sr.scroll = eveScroll.Scroll(name='applications', parent=self, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.tabs = ToggleButtonGroup(parent=self, idx=0, align=uiconst.TOTOP, callback=self.OnTabgroup)
        self.sr.tabs.AddButton('alliance', localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Alliance'))
        self.sr.tabs.AddButton('myApplications', localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/MyApplications'))
        self.sr.tabs.SelectByID('alliance')
        corpUISignals.on_alliance_application_changed.connect(self.OnAllianceApplicationChanged)

    def OnTabgroup(self, tab_id, old_tab_id):
        self.SetHint()
        if tab_id == 'alliance':
            self.ShowAllianceApplications(self.sr.viewRejected.checked)
        elif tab_id == 'myApplications':
            self.ShowMyApplications()

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def ShowAllianceApplications(self, viewRejected):
        log.LogInfo('ShowAllianceApplications')
        try:
            sm.GetService('corpui').ShowLoad()
            scrolllist = []
            headers = []
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/NoApplicationsFound')
            if eve.session.allianceid is None:
                hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/CorporationNotInAlliance', corpName=cfg.eveowners.Get(eve.session.corpid).ownerName)
            elif const.corpRoleDirector & eve.session.corprole != const.corpRoleDirector:
                log.LogInfo('ShowAllianceApplications Invalid Callee')
                hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/RequireDirectorHint')
            elif self is None or self.destroyed:
                log.LogInfo('ShowAllianceApplications Destroyed or None')
            else:
                nameLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Name')
                statusLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Status')
                headers = [nameLabel, statusLabel]
                applications = sm.GetService('alliance').GetApplications(viewRejected)
                log.LogInfo('ShowAllianceApplications len(applications):', len(applications))
                owners = []
                for application in applications.itervalues():
                    if application.corporationID not in owners:
                        owners.append(application.corporationID)

                if len(owners):
                    cfg.eveowners.Prime(owners)
                for application in applications.itervalues():
                    self.__AddApplicationToList(application, scrolllist, 0)

            self.sr.rejectedContainer.state = uiconst.UI_PICKCHILDREN
            self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=headers, noContentHint=hint)
        finally:
            sm.GetService('corpui').HideLoad()

    def CheckBoxChecked(self, checkbox):
        self.ShowAllianceApplications(checkbox.checked)

    def ShowMyApplications(self):
        log.LogInfo('ShowMyApplications')
        try:
            sm.GetService('corpui').ShowLoad()
            scrolllist = []
            headers = []
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/NoApplicationsFound')
            if const.corpRoleDirector & eve.session.corprole != const.corpRoleDirector:
                log.LogInfo('ShowAllianceApplications Invalid Callee')
                hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/RequireDirectorHint')
            elif self is None or self.destroyed:
                log.LogInfo('ShowMyApplications Destroyed or None')
            else:
                nameLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Name')
                statusLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Status')
                headers = [nameLabel, statusLabel]
                applications = sm.GetService('corp').GetAllianceApplications()
                log.LogInfo('ShowMyApplications len(applications):', len(applications))
                owners = []
                for application in applications.itervalues():
                    if application.allianceID not in owners:
                        owners.append(application.allianceID)

                if len(owners):
                    cfg.eveowners.Prime(owners)
                for application in applications.itervalues():
                    self.__AddApplicationToList(application, scrolllist, 1)

            self.sr.rejectedContainer.state = uiconst.UI_HIDDEN
            self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=headers, noContentHint=hint)
        finally:
            sm.GetService('corpui').HideLoad()

    def __AddApplicationToList(self, application, scrolllist, myApplications):
        data = utillib.KeyVal()
        status = _GetApplicationStatusStr(application.state)
        if myApplications:
            data.label = '%s<t>%s' % (cfg.eveowners.Get(application.allianceID).ownerName, status)
            data.OnDblClick = self._ViewApplication
            data.GetMenu = self.GetApplicationMenu
        else:
            data.label = '%s<t>%s' % (cfg.eveowners.Get(application.corporationID).ownerName, status)
            data.OnDblClick = self.AllianceViewApplication
            data.GetMenu = self.GetAllianceMenu
        data.application = application
        scrolllist.append(GetFromClass(Generic, data))

    def GetAllianceMenu(self, entry):
        viewLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/View')
        ret = [(viewLabel, self.AllianceViewApplication, (entry,))]
        if session.role & ROLE_GML == ROLE_GML:
            ret += [('GM: Accept Application', sm.GetService('alliance').GMAcceptApplication, (entry.sr.node.application.corporationID,))]
        return ret

    def GetApplicationMenu(self, entry):
        application = entry.sr.node.application
        viewLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/View')
        data = [(viewLabel, self._ViewApplication, (entry,))]
        if application.state in (allianceApplicationRejected, allianceApplicationNew):
            deleteLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Delete')
            data.append((deleteLabel, self.DeleteApplication, (application,)))
        return data

    def GetEntry(self, allianceID, corporationID):
        for entry in self.sr.scroll.GetNodes():
            if entry is None or entry is None:
                continue
            if entry.panel is None or entry.panel.destroyed:
                continue
            if entry.application.allianceID == allianceID and entry.application.corporationID == corporationID:
                return entry

    def OnAllianceApplicationChanged(self, allianceID, corporationID, change):
        log.LogInfo('OnAllianceApplicationChanged allianceID', allianceID, 'corporationID', corporationID, 'change', change)
        if self.sr.scroll is None:
            log.LogInfo('OnAllianceApplicationChanged no scroll')
            return
        bAdd = 1
        bRemove = 1
        for old, new in change.itervalues():
            if old is not None:
                bAdd = 0
            if new is not None:
                bRemove = 0

        if bAdd and bRemove:
            raise RuntimeError('applications::OnAllianceApplicationChanged WTF')
        if bAdd:
            log.LogInfo('OnAllianceApplicationChanged adding application')
            activeTab = self.sr.tabs.GetSelected()
            myApplications = 0
            if eve.session.corpid == corporationID:
                if activeTab != 'myApplications':
                    return
                application = sm.GetService('corp').GetAllianceApplications()[allianceID]
                myApplications = 1
            else:
                if activeTab != 'alliance':
                    return
                application = sm.GetService('alliance').GetApplications()[corporationID]
            self.SetHint()
            scrolllist = []
            self.__AddApplicationToList(application, scrolllist, myApplications)
            if len(self.sr.scroll.sr.headers) > 0:
                self.sr.scroll.AddEntries(-1, scrolllist)
            else:
                self.sr.scroll.Load(contentList=scrolllist, headers=self.sr.headers)
        elif bRemove:
            log.LogInfo('OnAllianceApplicationChanged removing application')
            entry = self.GetEntry(allianceID, corporationID)
            if entry is not None:
                self.sr.scroll.RemoveEntries([entry])
            else:
                log.LogWarn('OnAllianceApplicationChanged application not found')
        else:
            log.LogInfo('OnAllianceApplicationChanged updating application')
            entry = self.GetEntry(allianceID, corporationID)
            if entry is None:
                log.LogWarn('OnAllianceApplicationChanged application not found')
            if entry is not None:
                if 'state' in change:
                    oldStatus, newStatus = change['state']
                    activeTab = self.sr.tabs.GetSelected()
                    if activeTab == 'alliance' and not self.sr.viewRejected.checked and newStatus == allianceApplicationRejected:
                        self.sr.scroll.RemoveEntries([entry])
                        return
                    status = _GetApplicationStatusStr(newStatus)
                    if corporationID == eve.session.corpid:
                        label = '%s<t>%s' % (cfg.eveowners.Get(allianceID).ownerName, status)
                    else:
                        label = '%s<t>%s' % (cfg.eveowners.Get(corporationID).ownerName, status)
                    entry.panel.sr.node.label = label
                    entry.panel.sr.label.text = label

    def DeleteApplication(self, application, *args):
        try:
            sm.GetService('corpui').ShowLoad()
            sm.GetService('corp').DeleteAllianceApplication(application.allianceID)
        finally:
            sm.GetService('corpui').HideLoad()

    def _ViewApplication(self, entry, *args):
        self.ViewApplication(entry.sr.node.application.allianceID, entry.sr.node.application)

    def ViewApplication(self, allianceID, application = None):
        if application is None:
            application = sm.GetService('corp').GetAllianceApplications()[allianceID]
        if application is None:
            return
        wnd = MyAllianceApplicationWnd.Open(allianceID=allianceID, application=application)
        wnd.ShowModal()

    def CheckApplication(self, retval):
        if retval.has_key('appltext'):
            applicationText = retval['appltext']
            textLength = len(applicationText)
            if textLength > 1000:
                return localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/ApplicationTooLong', textLength=textLength)
        return ''

    def AllianceViewApplication(self, entry, *args):
        corporationID = entry.sr.node.application.corporationID
        if const.corpRoleDirector & eve.session.corprole != const.corpRoleDirector:
            return
        application = entry.sr.node.application
        canEditStatus = 0
        canAppendNote = 0
        stati = {}
        status = _GetApplicationStatusStr(application.state)
        format = []
        if application.state == allianceApplicationNew:
            canEditStatus = 1
            canAppendNote = 1
            rejectLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Reject')
            acceptLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Accept')
            stati[allianceApplicationRejected] = (rejectLabel, 0)
            stati[allianceApplicationAccepted] = (acceptLabel, 1)
        elif application.state == allianceApplicationAccepted:
            canEditStatus = 0
            canAppendNote = 0
        elif application.state == allianceApplicationEffective:
            canEditStatus = 0
            canAppendNote = 0
        elif application.state == allianceApplicationRejected:
            canEditStatus = 0
            canAppendNote = 0
        statusLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Status')
        fromLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/From')
        termsAndConditionsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/TermsAndConditions')
        format.append({'type': 'header',
         'text': fromLabel,
         'frame': 1})
        format.append({'type': 'text',
         'text': cfg.eveowners.Get(application.corporationID).ownerName,
         'frame': 1})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'header',
         'text': statusLabel,
         'frame': 1})
        format.append({'type': 'text',
         'text': status,
         'frame': 1})
        format.append({'type': 'push',
         'frame': 1})
        format.append({'type': 'header',
         'text': termsAndConditionsLabel,
         'frame': 1})
        if canEditStatus == 0:
            format.append({'type': 'labeltext',
             'label': statusLabel,
             'text': status,
             'frame': 1})
            format.append({'type': 'bbline'})
        else:
            i = 1
            for key in stati:
                if i == 1:
                    lbl = 'Status'
                else:
                    lbl = ''
                text, selected = stati[key]
                format.append({'type': 'checkbox',
                 'setvalue': selected,
                 'key': key,
                 'label': lbl,
                 'text': text,
                 'frame': 1,
                 'group': 'stati'})
                i = 0

            format.append({'type': 'bbline'})
        if canAppendNote == 1:
            allianceApplicationTextLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/AllianceApplicationText')
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'textedit',
             'setvalue': application.applicationText,
             'key': 'appltext',
             'label': allianceApplicationTextLabel,
             'required': 0,
             'frame': 1,
             'height': 96,
             'maxLength': 1000})
            format.append({'type': 'errorcheck',
             'errorcheck': self.CheckApplication})
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'bbline'})
        else:
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'textedit',
             'setvalue': application.applicationText,
             'readonly': 1,
             'frame': 1,
             'height': 96,
             'maxLength': 1000})
            format.append({'type': 'push',
             'frame': 1})
            format.append({'type': 'bbline'})
        if canEditStatus == 1 and canAppendNote == 1:
            btn = uiconst.OKCANCEL
        else:
            btn = uiconst.OK
        viewApplicationDetailsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/ViewApplicationDetails')
        left = uicore.desktop.width / 2 - 400 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        if application.state == allianceApplicationEffective:
            return uix.HybridWnd(format, viewApplicationDetailsLabel, 'applicationDetails', 0, btn, [left, top], 400, minH=320, unresizeAble=1)
        retval = uix.HybridWnd(format, viewApplicationDetailsLabel, 'applicationDetails', 1, btn, [left, top], 400, minH=320, unresizeAble=1)
        if retval is not None and canEditStatus == 1 and canAppendNote == 1:
            applicationText = retval['appltext']
            status = retval['stati']
            if status == allianceApplicationAccepted:
                wars = sm.GetService('war').GetWars(corporationID, 1)
                if len(wars):
                    warningLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Warning')
                    warsWillBeAdoptedLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/WarsWillBeAdopted')
                    format = [{'type': 'header',
                      'text': warningLabel}, {'type': 'text',
                      'text': warsWillBeAdoptedLabel}, {'type': 'push'}]
                    for war in wars.itervalues():
                        aggressor = cfg.eveowners.Get(war.declaredByID)
                        defender = cfg.eveowners.Get(war.againstID)
                        text = '%s vs %s' % (GetShowInfoLink(aggressor.typeID, aggressor.name, war.declaredByID), GetShowInfoLink(defender.typeID, defender.name, war.againstID))
                        format.append({'type': 'text',
                         'text': text})

                    confirmAcceptLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/ConfirmAccept')
                    format.append({'type': 'text',
                     'text': confirmAcceptLabel,
                     'frame': 0})
                    adoptWarsLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/AdoptWars')
                    retval = uix.HybridWnd(format, adoptWarsLabel, 'adoptWars', 1, uiconst.OKCANCEL, [left, top], 400, minH=310, unresizeAble=1)
                    if retval is None:
                        return
            sm.GetService('alliance').UpdateApplication(corporationID, applicationText, status)
            if status == allianceApplicationAccepted:
                raise UserError('AcceptedApplicationsTake24HoursToBecomeEffective')

    def GMAcceptApplication(self, corporationID):
        sm.GetService('alliance').GMAcceptApplication(corporationID)


class ApplyToAllianceWnd(Window):
    __guid__ = 'form.ApplyToAllianceWnd'
    default_width = 400
    default_height = 350
    default_minSize = (default_width, default_height)
    default_windowID = 'ApplyToAllianceWindow'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Confirm, cancelFunc=self.Cancel)
        self.allianceID = attributes.get('allianceID')
        wndCaption = localization.GetByLabel('UI/Corporations/BaseCorporationUI/AllianceApplication')
        self.SetCaption(wndCaption)
        self.MakeUnResizeable()
        self.ConstructLayout()

    def ConstructLayout(self):
        allianceName = cfg.eveowners.Get(self.allianceID).name
        allianceInfoCont = Container(name='allianceInfo', parent=self.sr.main, align=uiconst.TOTOP, height=68, padding=const.defaultPadding)
        allianceLogoCont = Container(name='allianceLogo', parent=allianceInfoCont, align=uiconst.TOLEFT, width=68)
        allianceTextCont = Container(name='allianceName', parent=allianceInfoCont, align=uiconst.TOALL)
        applicationCont = Container(name='allianceInfo', parent=self.sr.main, align=uiconst.TOALL, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding))
        eveIcon.GetOwnerLogo(allianceLogoCont, self.allianceID, size=64, noServerCall=True)
        allianceText = localization.GetByLabel('UI/Corporations/BaseCorporationUI/ApplyForMembership', corporation=allianceName)
        allianceNameLabel = eveLabel.EveLabelLarge(parent=allianceTextCont, text=allianceText, top=12, align=uiconst.TOPLEFT, width=270)
        alliance = sm.GetService('alliance').GetAlliance(self.allianceID)
        corp = sm.GetService('corp').GetCorporation(alliance.executorCorpID)
        myCorpName = cfg.eveowners.Get(session.corpid).ownerName
        stdText = localization.GetByLabel('UI/Corporations/BaseCorporationUI/AskJoinAlliance', ceo='-----', ceoID=corp.ceoID, mycorp=myCorpName, alliancename=allianceName, sender=session.charid, mycorpname=myCorpName)
        editText = localization.GetByLabel('UI/Corporations/BaseCorporationUI/CorporationApplicationText')
        editLabel = eveLabel.EveLabelSmall(parent=applicationCont, text=editText, height=16, align=uiconst.TOTOP)
        self.applicationText = EditPlainText(setvalue=stdText, parent=applicationCont, align=uiconst.TOTOP, maxLength=1000, height=100)
        appText = localization.GetByLabel('UI/Corporations/BaseCorporationUI/ThisApplicationOverwritesOlderOnes')
        appLabel = eveLabel.EveLabelMedium(parent=applicationCont, text=appText, align=uiconst.TOTOP, top=8)

    def Confirm(self, *args):
        applicationText = self.applicationText.GetValue()
        self.result = applicationText
        self.SetModalResult(1)

    def Cancel(self, *args):
        self.result = None
        self.SetModalResult(0)


class MyAllianceApplicationWnd(Window):
    __guid__ = 'form.MyAllianceApplicationWnd'
    default_width = 400
    default_height = 270
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.DefineButtons(uiconst.OK, okFunc=self.Confirm)
        self.allianceID = attributes.get('allianceID')
        self.application = attributes.get('application')
        self.windowID = 'viewApplicationWindow'
        wndCaption = localization.GetByLabel('UI/Corporations/CorpApplications/ViewApplicationDetailCaption')
        self.SetCaption(wndCaption)
        self.MakeUnResizeable()
        self.ConstructLayout()

    def ConstructLayout(self):
        allianceName = cfg.eveowners.Get(self.allianceID).name
        allianceInfoCont = Container(name='allianceInfo', parent=self.sr.main, align=uiconst.TOTOP, height=68, padding=const.defaultPadding)
        allianceLogoCont = Container(name='allianceLogo', parent=allianceInfoCont, align=uiconst.TOLEFT, width=68)
        allianceTextCont = Container(name='allianceName', parent=allianceInfoCont, align=uiconst.TOALL)
        applicationCont = Container(name='allianceInfo', parent=self.sr.main, align=uiconst.TOALL, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding))
        eveIcon.GetOwnerLogo(allianceLogoCont, self.allianceID, size=64, noServerCall=True)
        allianceText = localization.GetByLabel('UI/Corporations/CorpApplications/YourApplicationToJoin', corpName=allianceName)
        allianceNameLabel = eveLabel.EveLabelLarge(parent=allianceTextCont, text=allianceText, top=12, align=uiconst.TOPLEFT, width=270)
        editText = localization.GetByLabel('UI/Corporations/BaseCorporationUI/CorporationApplicationText')
        editLabel = eveLabel.EveLabelSmall(parent=applicationCont, text=editText, height=16, align=uiconst.TOTOP)
        if self.application.applicationText is not None:
            appText = self.application.applicationText
        else:
            appText = ''
        self.applicationText = EditPlainText(setvalue=appText, parent=applicationCont, align=uiconst.TOTOP, maxLength=1000, height=100, readonly=True)
        status = eveLabel.EveLabelSmall(parent=applicationCont, text=localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Applications/Status'), align=uiconst.TOTOP, top=6)
        statusLabel = eveLabel.EveLabelSmallBold(parent=applicationCont, text=_GetApplicationStatusStr(self.application.state), height=12, align=uiconst.TOTOP)

    def Confirm(self, *args):
        self.result = None
        self.SetModalResult(0)
