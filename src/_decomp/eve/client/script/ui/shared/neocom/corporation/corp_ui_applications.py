#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_applications.py
from math import pi
import localization
import eve.common.lib.appConst as const
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util import timerstuff
from carbonui import uiconst
from carbonui.control.basicDynamicScroll import BasicDynamicScroll
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveIcon, eveLabel, eveScroll
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.services.corporation.corp_util import HasRole
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.shared.neocom.wallet.walletUtil import FmtWalletCurrency
from eve.common.lib import appConst
from evewar.warPermitUtil import GetLabelPathForAllowWar
from menu import MenuLabel
APPLICATION_STATUS_LABELNAMES = {const.crpApplicationAppliedByCharacter: 'UI/Corporations/CorpApplications/ApplicationUnprocessed',
 const.crpApplicationAcceptedByCorporation: 'UI/Corporations/CorpApplications/ApplicationStatusInvited',
 const.crpApplicationRejectedByCorporation: 'UI/Corporations/CorpApplications/ApplicationStatusRejected',
 const.crpApplicationAcceptedByCharacter: 'UI/Corporations/CorpApplications/ApplicationStatusAccepted',
 const.crpApplicationRejectedByCharacter: 'UI/Corporations/CorpApplications/ApplicationStatusInvitationRejected',
 const.crpApplicationWithdrawnByCharacter: 'UI/Corporations/CorpApplications/ApplicationStatusWithdrawn',
 const.crpApplicationInvitedByCorporation: 'UI/Corporations/CorpApplications/ApplicationStatusDirectlyInvited'}
STATUS_SETTING_NAME = 'applicationStatus_%d'

class ApplicationsWindow(Container):
    is_loaded = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.ownerID = attributes.ownerID
        if self.ownerID == session.charid:
            self.myView = True
        else:
            self.myView = False
        self.quickFilterSetting = 'applicationsQuickFilter_OwnerID%s' % self.ownerID
        self.filteringBy = settings.char.ui.Get(self.quickFilterSetting, '')
        self.showingOld = settings.char.ui.Get('applicationsShowOld_%s' % self.ownerID, False)
        self.InitViewingStatus()

    def Load(self, *args):
        if not self.is_loaded:
            self.is_loaded = True
            self.ConstructLayout()
            corpUISignals.on_corporation_application_changed.connect(self.OnCorporationApplicationChanged)
        self.LoadApplications()

    def ConstructLayout(self):
        self.topContainer = Container(parent=self, name='topContainer', align=uiconst.TOTOP, height=20, padding=const.defaultPadding)
        self.quickFilter = QuickFilterEdit(parent=self.topContainer, align=uiconst.CENTERRIGHT, setvalue=self.filteringBy, isCharacterField=True)
        self.quickFilter.ReloadFunction = self.OnSearchFieldChanged
        self.quickFilter.OnReturn = self.SearchByCharacterName
        self.statusFilter = UtilMenu(parent=self.topContainer, align=uiconst.CENTERRIGHT, padding=(1, 1, 1, 1), left=103, GetUtilMenu=self.StatusFilterMenu, texturePath='res:/ui/texture/icons/38_16_205.png', hint=localization.GetByLabel('UI/Corporations/CorpApplications/FilterByStatus'))
        buttonGroup = ButtonGroup(parent=self)
        self.inviteButton = buttonGroup.AddButton(label=localization.GetByLabel('UI/Corporations/CorpApplications/InviteToCorp'), func=self.OpenInviteWindow)
        if self.myView or not HasRole(appConst.corpRolePersonnelManager):
            self.inviteButton.display = False
        if self.myView:
            self.topContainer.display = False
        self.applicationContainer = Container(name='applications', parent=self, align=uiconst.TOALL, padding=const.defaultPadding)
        self.applicationScroll = BasicDynamicScroll(name='applicationsScroll', parent=self.applicationContainer, align=uiconst.TOALL, noContentHint=localization.GetByLabel('UI/Corporations/CorpApplications/NoApplicationsFound'))
        self.applicationScroll.multiSelect = 0

    def OpenInviteWindow(self, *args):
        InviteToCorpWnd.CloseIfOpen('InviteToCorpWnd')
        InviteToCorpWnd.Open()

    def GetApplications(self, statusList = None):
        if statusList is None:
            statusList = self.sr.viewingStatus
        filteredApplications = []
        if self.ownerID == session.corpid:
            if const.corpRolePersonnelManager & session.corprole != const.corpRolePersonnelManager:
                return []
            if self.showingOld:
                applications = sm.GetService('corp').GetOldApplicationsWithStatus(statusList)
            else:
                applications = sm.GetService('corp').GetApplicationsWithStatus(statusList)
            if len(self.filteringBy):
                ownersToPrime = set()
                for application in applications:
                    ownersToPrime.add(application.characterID)

                if len(ownersToPrime) > 0:
                    cfg.eveowners.Prime(ownersToPrime)
                for application in applications:
                    if cfg.eveowners.Get(application.characterID).name.lower().find(self.filteringBy.lower()) > -1:
                        filteredApplications.append(application)

            else:
                filteredApplications = applications
        elif self.showingOld:
            filteredApplications = sm.GetService('corp').GetMyOldApplicationsWithStatus(None)
        else:
            filteredApplications = sm.GetService('corp').GetMyApplicationsWithStatus(None)
        return filteredApplications

    def GetCorpApplicationEntries(self, applications):
        ownersToPrime = set()
        scrolllist = []
        if self.myView:
            ownerKey = 'corporationID'
        else:
            ownerKey = 'characterID'
        validApplications = set()
        for application in applications:
            ownerID = getattr(application, ownerKey, None)
            if ownerID is None:
                continue
            ownersToPrime.add(ownerID)
            validApplications.add(application)

        if len(ownersToPrime):
            cfg.eveowners.Prime(ownersToPrime)
        expandedApp = settings.char.ui.Get('corporation_applications_expanded', {})
        for application in validApplications:
            entry = GetFromClass(CorpApplicationEntry, {'myView': self.myView,
             'application': application,
             'sort_%s' % localization.GetByLabel('UI/Common/Date'): application.applicationDateTime,
             'charID': application.characterID,
             'isExpanded': expandedApp.get(self.myView, None) == application.applicationID})
            scrolllist.append(entry)

        return scrolllist

    def OnSearchFieldChanged(self):
        myFilter = self.quickFilter.GetValue().strip()
        if myFilter == '':
            self.filteringBy = myFilter
            settings.char.ui.Set(self.quickFilterSetting, self.filteringBy)
            applications = self.GetApplications()
            scrolllist = self.GetCorpApplicationEntries(applications)
            self.RefreshApplicationScroll(addNodes=scrolllist, forceClear=True)

    def SearchByCharacterName(self, *args):
        myFilter = self.quickFilter.GetValue().strip()
        if len(myFilter) == 0:
            return
        self.filteringBy = myFilter
        applications = self.GetApplications()
        scrolllist = self.GetCorpApplicationEntries(applications)
        self.RefreshApplicationScroll(addNodes=scrolllist, forceClear=True)

    def StatusFilterMenu(self, menuParent):
        for applicationStatusID in APPLICATION_STATUS_LABELNAMES:
            if applicationStatusID == const.crpApplicationRejectedByCharacter:
                continue
            isChecked = _LoadApplicationFilterSetting(applicationStatusID, False)
            menuParent.AddCheckBox(_GetApplicationStatusLabel(applicationStatusID), checked=isChecked, callback=(self.ToggleStatusFilter, applicationStatusID, isChecked))

        menuParent.AddDivider()
        menuParent.AddCheckBox(localization.GetByLabel('UI/Corporations/CorpApplications/ShowOldApplications'), checked=self.showingOld, callback=(self.SetShowOld, not self.showingOld))

    def SetShowOld(self, value):
        settings.char.ui.Set('applicationsShowOld_%s' % self.ownerID, value)
        self.showingOld = value
        applications = self.GetApplications()
        scrolllist = self.GetCorpApplicationEntries(applications)
        self.RefreshApplicationScroll(addNodes=scrolllist, forceClear=True)

    def ToggleStatusFilter(self, applicationStatusID, isChecked):
        viewingStatus = []
        if isChecked:
            removeNodes = []
            _SaveApplicationFilterSetting(applicationStatusID, False)
            for status in self.sr.viewingStatus:
                if status != applicationStatusID:
                    viewingStatus.append(status)

            for applicationNode in self.applicationScroll.GetNodes():
                if applicationNode.application.status not in viewingStatus:
                    removeNodes.append(applicationNode)

            self.RefreshApplicationScroll(removeNodes=removeNodes)
        else:
            _SaveApplicationFilterSetting(applicationStatusID, True)
            viewingStatus.append(applicationStatusID)
            viewingStatus.extend(self.sr.viewingStatus)
            applications = self.GetApplications([applicationStatusID])
            scrolllist = self.GetCorpApplicationEntries(applications)
            if len(scrolllist) > 0:
                self.RefreshApplicationScroll(addNodes=scrolllist)
        self.sr.viewingStatus = viewingStatus

    def InitViewingStatus(self):
        viewingStatus = []
        for applicationStatusID in APPLICATION_STATUS_LABELNAMES:
            if self.ownerID == session.charid:
                viewingStatus.append(applicationStatusID)
            elif _LoadApplicationFilterSetting(applicationStatusID, False):
                viewingStatus.append(applicationStatusID)

        if len(viewingStatus) == 0:
            viewingStatus = [const.crpApplicationAppliedByCharacter]
            _SaveApplicationFilterSetting(const.crpApplicationAppliedByCharacter, True)
        self.sr.viewingStatus = viewingStatus

    def LoadApplications(self):
        if self.destroyed:
            return
        try:
            myFilter = self.quickFilter.GetValue()
            if len(myFilter):
                self.filteringBy = myFilter
            sm.GetService('corpui').ShowLoad()
            applications = self.GetApplications()
            scrolllist = self.GetCorpApplicationEntries(applications)
            if len(scrolllist) > 0:
                self.HideNoContentHint()
                self.RefreshApplicationScroll(addNodes=scrolllist, forceClear=True)
            else:
                self.ShowNoContentHint()
        except:
            pass
        finally:
            sm.GetService('corpui').HideLoad()

    def RefreshApplicationScroll(self, addNodes = [], removeNodes = [], reloadNodes = [], forceClear = False):
        if forceClear:
            self.applicationScroll.Clear()
        elif len(removeNodes):
            self.applicationScroll.RemoveNodes(removeNodes, updateScroll=True)
        if len(reloadNodes):
            self.applicationScroll.ReloadNodes(reloadNodes)
        if len(addNodes):
            self.applicationScroll.AddNodes(0, addNodes, updateScroll=True)
        toSort = self.applicationScroll.GetNodes()
        if toSort:
            self.HideNoContentHint()
            sortedNodes = sorted(toSort, key=lambda x: x.application.applicationDateTime, reverse=True)
            self.applicationScroll.SetOrderedNodes(sortedNodes)
        else:
            self.ShowNoContentHint()

    def ShowNoContentHint(self):
        self.applicationScroll.ShowHint(localization.GetByLabel('UI/Corporations/CorpApplications/NoApplicationsFound'))

    def HideNoContentHint(self):
        self.applicationScroll.ShowHint('')

    def OnCorporationApplicationChanged(self, corpID, applicantID, applicationID, newApplication):
        if self.destroyed:
            return
        for applicationNode in self.applicationScroll.GetNodes():
            if applicationNode.application.applicationID == applicationID:
                applicationNode.application = newApplication
                if newApplication.status in self.sr.viewingStatus:
                    self.RefreshApplicationScroll(reloadNodes=[applicationNode])
                else:
                    self.RefreshApplicationScroll(removeNodes=[applicationNode])
                break
        else:
            if newApplication.status in self.sr.viewingStatus:
                scrolllist = self.GetCorpApplicationEntries([newApplication])
                self.RefreshApplicationScroll(addNodes=scrolllist)


class ViewCorpApplicationWnd(Window):
    __guid__ = 'form.ViewCorpApplicationWnd'
    default_width = 400
    default_height = 255
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Confirm, cancelFunc=self.Cancel)
        self.charID = attributes.get('characterID')
        self.appText = attributes.get('applicationText')
        self.status = attributes.get('status')
        wndCaption = localization.GetByLabel('UI/Corporations/CorpApplications/ViewApplicationDetailCaption')
        self.SetCaption(wndCaption)
        self.MakeUnResizeable()
        self.ConstructLayout()

    def ConstructLayout(self):
        charInfoCont = Container(name='charInfo', parent=self.sr.main, align=uiconst.TOTOP, height=68, padding=const.defaultPadding)
        charLogoCont = Container(name='charLogo', parent=charInfoCont, align=uiconst.TOLEFT, width=68)
        charTextCont = Container(name='charName', parent=charInfoCont, align=uiconst.TOALL)
        applicationCont = Container(name='charInfo', parent=self.sr.main, align=uiconst.TOALL, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding))
        eveIcon.GetOwnerLogo(charLogoCont, self.charID, size=64, noServerCall=True)
        charText = localization.GetByLabel('UI/Corporations/CorpApplications/ApplicationSubjectLine', player=self.charID)
        charNameLabel = eveLabel.EveLabelLarge(parent=charTextCont, text=charText, top=12, align=uiconst.TOPLEFT, width=270)
        editText = localization.GetByLabel('UI/Corporations/BaseCorporationUI/CorporationApplicationText')
        editLabel = eveLabel.EveLabelSmall(parent=applicationCont, text=editText, align=uiconst.TOTOP)
        self.rejectRb = RadioButton(text=localization.GetByLabel('UI/Corporations/CorpApplications/RejectApplication'), parent=applicationCont, settingsKey='reject', retval=1, checked=False, groupname='state', align=uiconst.TOBOTTOM)
        self.acceptRb = RadioButton(text=localization.GetByLabel('UI/Corporations/CorpApplications/ApplicationInviteApplicant'), parent=applicationCont, settingsKey='accept', retval=0, checked=True, groupname='state', align=uiconst.TOBOTTOM)
        if self.status not in const.crpApplicationActiveStatuses:
            self.rejectRb.state = uiconst.UI_HIDDEN
            self.acceptRb.state = uiconst.UI_HIDDEN
        self.applicationText = EditPlainText(setvalue=self.appText, parent=applicationCont, maxLength=1000, readonly=True)

    def Confirm(self, *args):
        if self.status not in const.crpApplicationActiveStatuses:
            self.Cancel()
        applicationText = self.applicationText.GetValue()
        if len(applicationText) > 1000:
            error = localization.GetByLabel('UI/Corporations/CorpApplications/ApplicationTextTooLong', length=len(applicationText))
            eve.Message('CustomInfo', {'info': error})
        else:
            if self.rejectRb.checked:
                rejected = const.crpApplicationRejectedByCorporation
            else:
                rejected = const.crpApplicationAcceptedByCorporation
            self.result = rejected
            self.SetModalResult(1)

    def Cancel(self, *args):
        self.result = None
        self.SetModalResult(0)


class MyCorpApplicationWnd(Window):
    __guid__ = 'form.MyCorpApplicationWnd'
    default_width = 400
    default_height = 300
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.corpid = attributes.get('corpid')
        self.application = attributes.get('application')
        self.status = attributes.get('status')
        self.windowID = 'viewApplicationWindow'
        if self.status in const.crpApplicationActiveStatuses:
            self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Confirm, cancelFunc=self.Cancel)
        else:
            self.DefineButtons(uiconst.OK, okFunc=self.Cancel)
        wndCaption = localization.GetByLabel('UI/Corporations/CorpApplications/ViewApplicationDetailCaption')
        self.SetCaption(wndCaption)
        self.MakeUnResizeable()
        self.ConstructLayout()

    def ConstructLayout(self):
        self.acceptRb = None
        self.withdrawRb = None
        corpName = cfg.eveowners.Get(self.corpid).name
        corpInfoCont = Container(name='corpInfo', parent=self.sr.main, align=uiconst.TOTOP, height=68, padding=const.defaultPadding)
        corpLogoCont = Container(name='corpLogo', parent=corpInfoCont, align=uiconst.TOLEFT, width=68)
        corpTextCont = Container(name='corpName', parent=corpInfoCont, align=uiconst.TOALL)
        controlCont = Container(name='buttons', parent=self.sr.main, align=uiconst.TOBOTTOM, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding))
        controlContHeight = 0
        applicationCont = Container(name='applicationCont', parent=self.sr.main, align=uiconst.TOALL, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding))
        eveIcon.GetOwnerLogo(corpLogoCont, self.corpid, size=64, noServerCall=True)
        corpText = localization.GetByLabel('UI/Corporations/CorpApplications/YourApplicationToJoin', corpName=corpName)
        corpNameLabel = eveLabel.EveLabelLarge(parent=corpTextCont, text=corpText, top=12, align=uiconst.TOPLEFT, width=270)
        if self.status == const.crpApplicationAppliedByCharacter:
            statusText = localization.GetByLabel('UI/Corporations/CorpApplications/ApplicationNotProcessed')
            statusLabel = eveLabel.EveLabelSmall(parent=applicationCont, text=statusText, align=uiconst.TOTOP, padBottom=const.defaultPadding)
        else:
            statusText = statusLabel = ''
        editText = localization.GetByLabel('UI/Corporations/BaseCorporationUI/CorporationApplicationText')
        editLabel = eveLabel.EveLabelSmall(parent=applicationCont, text=editText, align=uiconst.TOTOP)
        if self.application.applicationText is not None:
            appText = self.application.applicationText
        else:
            appText = ''
        self.applicationText = EditPlainText(setvalue=appText, parent=applicationCont, maxLength=1000, readonly=True)
        if self.status in const.crpApplicationActiveStatuses:
            isWithdrawChecked = True
            if self.status in (const.crpApplicationAcceptedByCorporation, const.crpApplicationInvitedByCorporation):
                isWithdrawChecked = False
                self.acceptRb = RadioButton(text=localization.GetByLabel('UI/Corporations/CorpApplications/AcceptApplication'), parent=controlCont, settingsKey='accept', retval=1, checked=True, groupname='stateGroup', align=uiconst.TOBOTTOM)
                controlContHeight += 40
            self.withdrawRb = RadioButton(text=localization.GetByLabel('UI/Corporations/CorpApplications/WithdrawApplication'), parent=controlCont, settingsKey='accept', retval=3, checked=isWithdrawChecked, groupname='stateGroup', align=uiconst.TOBOTTOM)
            controlContHeight += 20
        controlCont.height = controlContHeight

    def Confirm(self, *args):
        self.result = None
        if self.withdrawRb.checked:
            self.result = const.crpApplicationWithdrawnByCharacter
        elif self.acceptRb.checked:
            self.result = const.crpApplicationAcceptedByCharacter
        self.SetModalResult(1)

    def Cancel(self, *args):
        self.result = None
        self.SetModalResult(0)

    def WithdrawApplication(self, *args):
        try:
            sm.GetService('corpui').ShowLoad()
            application = self.application
            sm.GetService('corpui').ShowLoad()
            sm.GetService('corp').UpdateApplicationOffer(application.applicationID, application.characterID, application.corporationID, application.applicationText, const.crpApplicationWithdrawnByCharacter)
        finally:
            sm.GetService('corpui').HideLoad()
            Window.CloseIfOpen(windowID='viewApplicationWindow')


class ApplyToCorpWnd(Window):
    __guid__ = 'form.ApplyToCorpWnd'
    default_width = 500
    default_height = 450
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Confirm, cancelFunc=self.Cancel)
        self.corpid = attributes.get('corpid')
        self.corporation = attributes.get('corporation')
        wndCaption = localization.GetByLabel('UI/Corporations/BaseCorporationUI/JoinCorporation')
        self.SetCaption(wndCaption)
        self.MakeUnResizeable()
        self.ConstructLayout()

    def ConstructLayout(self):
        corpName = cfg.eveowners.Get(self.corpid).name
        corpInfoCont = Container(name='corpInfo', parent=self.sr.main, align=uiconst.TOTOP, height=68, padding=const.defaultPadding)
        corpLogoCont = Container(name='corpLogo', parent=corpInfoCont, align=uiconst.TOLEFT, width=68)
        corpTextCont = Container(name='corpName', parent=corpInfoCont, align=uiconst.TOALL)
        applicationCont = Container(name='corpInfo', parent=self.sr.main, align=uiconst.TOALL, padding=(2 * const.defaultPadding,
         0,
         2 * const.defaultPadding,
         const.defaultPadding))
        eveIcon.GetOwnerLogo(corpLogoCont, self.corpid, size=64, noServerCall=True)
        corpText = localization.GetByLabel('UI/Corporations/BaseCorporationUI/ApplyForMembership', corporation=corpName)
        corpNameLabel = eveLabel.EveLabelLarge(parent=corpTextCont, text=corpText, top=12, align=uiconst.TOPLEFT, width=270)
        editText = localization.GetByLabel('UI/Corporations/BaseCorporationUI/CorporationApplicationText')
        editLabel = eveLabel.EveLabelSmall(parent=applicationCont, text=editText, align=uiconst.TOTOP)
        self._construct_lp_tax(parent_container=applicationCont, corpName=corpName)
        self._construct_isk_tax(parent_container=applicationCont, corpName=corpName)
        corpService = sm.GetService('corp')
        aggressionSettings = corpService.GetAggressionSettings(self.corpid)
        statusText = corpService.GetCorpFriendlyFireStatus(aggressionSettings)
        ffText = localization.GetByLabel('UI/Corporations/FriendlyFire/FriendlyFireStatus', ffStatus=statusText)
        ffCont = Container(parent=applicationCont, align=uiconst.TOBOTTOM, height=16)
        friendlyFireLabel = eveLabel.EveLabelSmall(parent=ffCont, text=ffText, align=uiconst.CENTERLEFT)
        helpIcon = MoreInfoIcon(parent=ffCont, align=uiconst.TORIGHT, hint=localization.GetByLabel('UI/Corporations/FriendlyFire/Description'))
        ffCont.height = max(ffCont.height, friendlyFireLabel.textheight + 4, helpIcon.height)
        warPermitStatus = sm.GetService('warPermit').GetWarPermitStatusForCorp(self.corpid)
        warPermitStatusText = localization.GetByLabel(GetLabelPathForAllowWar(warPermitStatus))
        warPermitText = localization.GetByLabel('UI/WarPermit/WarPermitWithStatus', warPermitStatus=warPermitStatusText)
        warPermitCont = Container(name='warpPermitCont', parent=applicationCont, align=uiconst.TOBOTTOM, height=16)
        warPermitLabel = eveLabel.EveLabelSmall(name='warPermitLabel', parent=warPermitCont, text=warPermitText, align=uiconst.CENTERLEFT)
        warHelpIcon = MoreInfoIcon(parent=warPermitCont, align=uiconst.TORIGHT, hint=localization.GetByLabel('UI/WarPermit/WarPermitExplanation'))
        warPermitCont.height = max(warPermitCont.height, warPermitLabel.textheight + 4, warHelpIcon.height)
        if self.corporation and not self.corporation.isRecruiting:
            notRecruitingText = localization.GetByLabel('UI/Corporations/BaseCorporationUI/RecruitmentMayBeClosed')
            notRecruiting = eveLabel.EveLabelSmall(parent=applicationCont, text=notRecruitingText, align=uiconst.TOBOTTOM, idx=0)
            self.SetMinSize((self.default_width, self.default_height + notRecruiting.textheight), refresh=True)
        self.applicationText = EditPlainText(setvalue='', parent=applicationCont, align=uiconst.TOALL, maxLength=1000, padBottom=4)

    def _construct_isk_tax(self, parent_container, corpName):
        container = Container(name='isk_tax_container', parent=parent_container, align=uiconst.TOBOTTOM, height=16)
        isk_tax_rate = self.corporation.taxRate * 100
        tax_text = localization.GetByLabel('UI/Corporations/BaseCorporationUI/CurrentISKTaxRateForCorporation', corporation=corpName, taxRate=isk_tax_rate)
        label = eveLabel.EveLabelSmall(name='isk_tax_label', parent=container, text=tax_text, align=uiconst.TOALL)
        minimum_isk_amount_text = FmtWalletCurrency(amt=const.minCorporationTaxAmount, currency=const.creditsISK)
        icon = MoreInfoIcon(parent=container, align=uiconst.CENTERRIGHT, hint=localization.GetByLabel('UI/Corporations/BaseCorporationUI/ISKTaxRateDescription', min_isk_amount=minimum_isk_amount_text))
        container.height = max(container.height, label.textheight + 4, icon.height)

    def _construct_lp_tax(self, parent_container, corpName):
        container = Container(name='lp_tax_container', parent=parent_container, align=uiconst.TOBOTTOM, height=16)
        lp_tax_rate = self.corporation.loyaltyPointTaxRate * 100
        tax_text = localization.GetByLabel('UI/Corporations/BaseCorporationUI/CurrentLPTaxRateForCorporation', corporation=corpName, taxRate=lp_tax_rate)
        label = eveLabel.EveLabelSmall(name='lp_tax_label', parent=container, text=tax_text, align=uiconst.TOALL)
        icon = MoreInfoIcon(parent=container, align=uiconst.CENTERRIGHT, hint=localization.GetByLabel('UI/Corporations/BaseCorporationUI/LPTaxRateDescription'))
        container.height = max(container.height, label.textheight + 4, icon.height)

    def Confirm(self, *args):
        applicationText = self.applicationText.GetValue()
        if len(applicationText) > const.crpApplicationMaxSize:
            error = localization.GetByLabel('UI/Corporations/BaseCorporationUI/ApplicationTextTooLong', length=len(applicationText))
            eve.Message('CustomInfo', {'info': error})
        else:
            self.result = applicationText
            self.SetModalResult(1)

    def Cancel(self, *args):
        self.result = None
        self.SetModalResult(0)


def get_display_text_for_application(application):
    if application.status == const.crpApplicationRejectedByCorporation:
        display_text = application.responseText or ''
    else:
        display_text = application.applicationText
    return display_text.strip()


class CorpApplicationEntry(SE_BaseClassCore):
    __guid__ = 'listentry.CorpApplicationEntry'
    __notifyevents__ = []
    LOGOPADDING = 70
    TEXTPADDING = 18
    CORPNAMEPAD = (LOGOPADDING,
     0,
     0,
     0)
    EXTENDEDPAD = (LOGOPADDING,
     const.defaultPadding,
     const.defaultPadding,
     const.defaultPadding)
    CORPNAMECLASS = eveLabel.EveLabelLarge
    EXTENDEDCLASS = eveLabel.EveLabelMedium
    APPHEADERHEIGHT = 53

    def PreLoad(node):
        application = node.application

    def Startup(self, *args):
        node = self.sr.node
        self.corpSvc = sm.GetService('corp')
        self.viewButton = None
        self.removeButton = None
        self.rejectButton = None
        self.acceptButton = None
        self.ownerID = None
        if node.myView:
            self.ownerID = node.application.corporationID
        else:
            self.ownerID = node.application.characterID
        self.entryContainer = Container(parent=self)
        self.headerContainer = Container(parent=self.entryContainer, align=uiconst.TOTOP, name='applicationHeaderContainer', height=self.APPHEADERHEIGHT)
        self.expander = Sprite(parent=self.headerContainer, state=uiconst.UI_DISABLED, name='expander', pos=(0, 0, 16, 16), texturePath='res:/UI/Texture/Shared/getMenuIcon.png', align=uiconst.CENTERLEFT)
        if node.isExpanded:
            self.expander.rotation = -pi * 0.5
        logoParent = Container(parent=self.headerContainer, align=uiconst.TOPLEFT, pos=(16, 2, 48, 48))
        eveIcon.GetOwnerLogo(logoParent, self.ownerID, size=48, noServerCall=True)
        logoParent.children[0].OnMouseEnter = self.OnMouseEnter
        logoParent.children[0].OnClick = self.ShowOwnerInfo
        self.buttonCont = Container(name='buttonCont', parent=self.headerContainer, align=uiconst.TORIGHT)
        self.nameCont = Container(name='nameCont', parent=self.headerContainer, align=uiconst.TOALL, padding=self.CORPNAMEPAD)
        self.nameLabel = self.CORPNAMECLASS(parent=self.nameCont, name='nameLabel', state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, autoFadeSides=32)
        self.expandedParent = Container(parent=self.entryContainer, name='expandedParent', height=0)
        label_text = get_display_text_for_application(node.application)
        self.expandedLabel = self.EXTENDEDCLASS(parent=self.expandedParent, name='applicationText', text=label_text, padding=self.EXTENDEDPAD, align=uiconst.TOALL)
        self.hilite = Fill(bgParent=self.headerContainer, color=(1, 1, 1, 0))
        Fill(bgParent=self.expandedParent, color=(0, 0, 0, 0.2))

    def Load(self, node):
        ownerName = cfg.eveowners.Get(self.ownerID).ownerName
        applicationDate = localization.GetByLabel('UI/Corporations/Applications/ApplicationDate', applicationDateTime=node.application.applicationDateTime)
        statusText = '<fontsize=12>%s</fontsize>' % _GetApplicationStatusLabel(node.application.status)
        nameStatusAndDate = '<b>%s - %s</b><br>%s' % (ownerName, statusText, applicationDate)
        self.nameLabel.text = nameStatusAndDate
        addPadding = const.defaultPadding
        if node.myView:
            if node.application.status not in const.crpApplicationEndStatuses:
                if self.removeButton is not None and not self.removeButton.destroyed:
                    self.removeButton.left = addPadding
                else:
                    if node.application.status == const.crpApplicationInvitedByCorporation:
                        label = localization.GetByLabel('UI/Corporations/CorpApplications/DeclineInvitation')
                        rejectFunc = self.RejectCorpInvitation
                    else:
                        label = localization.GetByLabel('UI/Corporations/CorpApplications/WithdrawApplication')
                        rejectFunc = self.WithdrawMyApplication
                    self.removeButton = Button(name='removeButton', parent=self.buttonCont, label=label, align=uiconst.CENTERRIGHT, left=addPadding, func=rejectFunc)
                addPadding += self.removeButton.width + const.defaultPadding
            elif self.removeButton is not None:
                self.removeButton.Close()
                self.removeButton = None
            if node.myView and node.application.status in (const.crpApplicationAcceptedByCorporation, const.crpApplicationInvitedByCorporation):
                if self.acceptButton is not None and not self.acceptButton.destroyed:
                    self.acceptButton.left = addPadding
                else:
                    self.acceptButton = Button(name='acceptButton', parent=self.buttonCont, label=localization.GetByLabel('UI/Corporations/CorpApplications/AcceptApplication'), align=uiconst.CENTERRIGHT, left=addPadding, func=self.AcceptInvitation)
                addPadding += self.acceptButton.width + const.defaultPadding
            elif self.acceptButton is not None:
                self.acceptButton.Close()
                self.acceptButton = None
        else:
            if node.application.status == const.crpApplicationAppliedByCharacter:
                if self.acceptButton is not None and not self.acceptButton.destroyed:
                    self.acceptButton.left = addPadding
                else:
                    self.acceptButton = Button(name='acceptButton', parent=self.buttonCont, label=localization.GetByLabel('UI/Corporations/CorpApplications/ApplicationInviteApplicant'), align=uiconst.CENTERRIGHT, left=addPadding, func=self.AcceptCorpApplication)
                addPadding += self.acceptButton.width + const.defaultPadding
            elif self.acceptButton is not None:
                self.acceptButton.Close()
                self.acceptButton = None
            if node.application.status not in const.crpApplicationEndStatuses:
                if self.rejectButton is not None and not self.rejectButton.destroyed:
                    self.rejectButton.left = addPadding
                else:
                    self.rejectButton = Button(name='rejectButton', parent=self.buttonCont, label=localization.GetByLabel('UI/Corporations/CorpApplications/RejectApplication'), align=uiconst.CENTERRIGHT, left=addPadding, func=self.RejectCorpApplication)
                addPadding += self.rejectButton.width + const.defaultPadding
            elif self.rejectButton is not None:
                self.rejectButton.Close()
                self.rejectButton = None
        if node.fadeSize is not None:
            toHeight, fromHeight = node.fadeSize
            self.expandedParent.opacity = 0.0
            uicore.animations.MorphScalar(self, 'height', startVal=fromHeight, endVal=toHeight, duration=0.3)
            uicore.animations.FadeIn(self.expandedParent, duration=0.3)
        node.fadeSize = None
        if node.isExpanded:
            self.expandedParent.display = True
            rotValue = -pi * 0.5
        else:
            rotValue = 0.0
            self.expandedParent.display = False
        uicore.animations.MorphScalar(self.expander, 'rotation', self.expander.rotation, rotValue, duration=0.15)
        self.expandedLabel.text = get_display_text_for_application(node.application)
        self.buttonCont.width = addPadding

    def OnClick(self):
        node = self.sr.node
        reloadNodes = [node]
        if node.isExpanded:
            PlaySound(uiconst.SOUND_COLLAPSE)
            uicore.animations.Tr2DRotateTo(self.expander, -pi * 0.5, 0.0, duration=0.15)
            node.isExpanded = False
            allNodes = settings.char.ui.Get('corporation_applications_expanded', {})
            allNodes[node.myView] = None
            settings.char.ui.Set('corporation_applications_expanded', allNodes)
        else:
            PlaySound(uiconst.SOUND_EXPAND)
            for otherNode in node.scroll.sr.nodes:
                if otherNode.isExpanded and otherNode != node:
                    otherNode.isExpanded = False
                    reloadNodes.append(otherNode)

            uicore.animations.Tr2DRotateTo(self.expander, 0.0, -pi * 0.5, duration=0.15)
            node.isExpanded = True
            node.fadeSize = (CorpApplicationEntry.GetDynamicHeight(node, self.width), self.height)
            allNodes = settings.char.ui.Get('corporation_applications_expanded', {})
            allNodes[node.myView] = node.application.applicationID
            settings.char.ui.Set('corporation_applications_expanded', allNodes)
        self.sr.node.scroll.ReloadNodes(reloadNodes, updateHeight=True)

    def GetMenu(self):
        node = self.sr.node
        menu = [(MenuLabel('UI/Commands/ShowInfo'), self.ShowOwnerInfo)]
        if node.myView:
            if node.application.status not in const.crpApplicationEndStatuses:
                if node.application.status == const.crpApplicationInvitedByCorporation:
                    label = MenuLabel('UI/Corporations/CorpApplications/DeclineInvitation')
                else:
                    label = MenuLabel('UI/Corporations/CorpApplications/WithdrawApplication')
                menu.append((label, self.WithdrawMyApplication))
            if node.application.status in (const.crpApplicationAcceptedByCorporation, const.crpApplicationInvitedByCorporation):
                menu.append((MenuLabel('UI/Corporations/CorpApplications/AcceptApplication'), self.AcceptInvitation))
        elif const.corpRolePersonnelManager & session.corprole == const.corpRolePersonnelManager:
            if node.application.status == const.crpApplicationAppliedByCharacter:
                menu.append((MenuLabel('UI/Corporations/CorpApplications/ApplicationInviteApplicant'), self.AcceptCorpApplication))
            if node.application.status not in const.crpApplicationEndStatuses:
                menu.append((MenuLabel('UI/Corporations/CorpApplications/RejectApplication'), self.RejectCorpApplication))
        return menu

    def GetDynamicHeight(node, width):
        text = get_display_text_for_application(node.application)
        entryClass = CorpApplicationEntry
        if node.isExpanded:
            lp, tp, rp, bp = entryClass.EXTENDEDPAD
            textWidth, textHeight = entryClass.EXTENDEDCLASS.MeasureTextSize(text, width=width - (lp + rp))
            textHeight = textHeight + entryClass.APPHEADERHEIGHT + tp + bp
            return textHeight
        else:
            return entryClass.APPHEADERHEIGHT

    def ShowOwnerInfo(self):
        owner = cfg.eveowners.Get(self.ownerID)
        sm.GetService('info').ShowInfo(owner.typeID, owner.ownerID)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        uicore.animations.FadeIn(self.hilite, 0.05, duration=0.1)
        self.hiliteTimer = timerstuff.AutoTimer(1, self._CheckIfStillHilited)

    def _CheckIfStillHilited(self):
        if uicore.uilib.mouseOver.IsUnder(self) or uicore.uilib.mouseOver is self:
            return
        uicore.animations.FadeOut(self.hilite, duration=0.3)
        self.hiliteTimer = None

    def _UpdateCurrentApplicationWithStatus(self, newStatus):
        try:
            sm.GetService('corpui').ShowLoad()
            application = self.sr.node.application
            sm.GetService('corp').UpdateApplicationOffer(application.applicationID, application.characterID, application.corporationID, application.applicationText, newStatus)
        finally:
            sm.GetService('corpui').HideLoad()
            Window.CloseIfOpen(windowID='viewApplicationWindow')

    def AcceptInvitation(self, *args):
        self._UpdateCurrentApplicationWithStatus(const.crpApplicationAcceptedByCharacter)

    def WithdrawMyApplication(self, *args):
        if eve.Message('WithdrawApplication', buttons=uiconst.YESNO) == uiconst.ID_YES:
            self._UpdateCurrentApplicationWithStatus(const.crpApplicationWithdrawnByCharacter)

    def RejectCorpInvitation(self, *args):
        self._UpdateCurrentApplicationWithStatus(const.crpApplicationRejectedByCharacter)

    def AcceptCorpApplication(self, *args):
        self._UpdateCurrentApplicationWithStatus(const.crpApplicationAcceptedByCorporation)

    def RejectCorpApplication(self, *args):
        RejectCorpApplicationWnd.CloseIfOpen(windowID='rejectCorpApplication')
        application = self.sr.node.application
        RejectCorpApplicationWnd.Open(application=application)


def _GetApplicationStatusLabel(applicationStatusID):
    return localization.GetByLabel(APPLICATION_STATUS_LABELNAMES[applicationStatusID])


def _LoadApplicationFilterSetting(applicationStatusID, default):
    return settings.char.ui.Get(_GetSettingsKeyName(applicationStatusID), default)


def _SaveApplicationFilterSetting(applicationStatusID, value):
    settings.char.ui.Set(_GetSettingsKeyName(applicationStatusID), value)


def _GetSettingsKeyName(applicationStatusID):
    return STATUS_SETTING_NAME % applicationStatusID


class RejectCorpApplicationWnd(Window):
    __guid__ = 'form.RejectCorpApplicationWnd'
    default_width = 400
    default_height = 400
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.application = attributes.application
        self.windowID = 'rejectCorpApplication'
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Reject, cancelFunc=self.Cancel, okLabel=localization.GetByLabel('UI/Corporations/CorpApplications/RejectApplication'))
        wndCaption = localization.GetByLabel('UI/Corporations/Applications/ApplicationRejection')
        self.SetCaption(wndCaption)
        self.MakeUnResizeable()
        topCont = Container(parent=self.sr.main, align=uiconst.TOTOP, height=58)
        textCont = Container(parent=self.sr.main, align=uiconst.TOALL, padding=8)
        charName = cfg.eveowners.Get(self.application.characterID).name
        corpName = cfg.eveowners.Get(self.application.corporationID).name
        logoParent = Container(parent=topCont, align=uiconst.TOPLEFT, pos=(8, 6, 48, 48))
        eveIcon.GetOwnerLogo(logoParent, self.application.characterID, size=48, noServerCall=True)
        characterLink = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=charName, info=('showinfo', const.typeCharacter, self.application.characterID))
        nameLabel = EveLabelMedium(parent=topCont, left=64, top=12, text=characterLink, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        applicationDate = localization.GetByLabel('UI/Corporations/Applications/ApplicationDate', applicationDateTime=self.application.applicationDateTime)
        dateLabel = EveLabelMedium(parent=topCont, left=64, top=2, text=applicationDate, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        messageLabel = EveLabelMedium(parent=textCont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Corporations/CorpApplications/ApplicationRejectionText', charName=charName, corpName=corpName))
        regardsLabel = EveLabelMedium(parent=textCont, align=uiconst.TOBOTTOM, text=localization.GetByLabel('UI/Corporations/CorpApplications/ApplicationRejectionRegards', corpName=corpName), padTop=4)
        self.messageTextEdit = EditPlainText(parent=textCont, maxLength=1000, hintText=localization.GetByLabel('UI/Corporations/CorpApplications/CorpRejectionMessage'), top=4)

    def Reject(self, *args):
        try:
            sm.GetService('corpui').ShowLoad()
            customMessage = self.messageTextEdit.GetValue()
            sm.GetService('corp').UpdateApplicationOffer(self.application.applicationID, self.application.characterID, self.application.corporationID, self.application.applicationText, const.crpApplicationRejectedByCorporation, customMessage=customMessage)
        finally:
            sm.GetService('corpui').HideLoad()
            Window.CloseIfOpen(windowID='viewApplicationWindow')
            self.Close()

    def Cancel(self, *args):
        self.Close()


class InviteToCorpWnd(Window):
    __guid__ = 'form.InviteToCorpWnd'
    default_minSize = (320, 300)
    default_width = 320
    default_height = 400
    default_windowID = 'InviteToCorpWnd'
    default_iconNum = 'res:/ui/Texture/WindowIcons/corporation.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.searchStr = ''
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=70, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=self.topParent, state=uiconst.UI_DISABLED, pos=(0, -3, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.scroll = eveScroll.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.scroll.Startup()
        self.scroll.multiSelect = 0
        self.standardBtns = ButtonGroup(btns=[[localization.GetByLabel('UI/Ship/ShipConfig/Invite'),
          self.InviteToCorp,
          (),
          81], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.OnCancel,
          (),
          81]])
        self.inviteButton = self.standardBtns.buttons[0]
        self.inviteButton.Disable()
        self.sr.main.children.insert(0, self.standardBtns)
        self.SetCaption(localization.GetByLabel('UI/Messages/1527/SelectCharacterTitle'))
        self.label = eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Shared/TypeSearchString'), parent=self.topParent, left=70, top=16, state=uiconst.UI_NORMAL)
        self.nameInput = SingleLineEditText(name='edit', parent=self.topParent, pos=(70,
         self.label.top + self.label.height + 2,
         86,
         0), align=uiconst.TOPLEFT, maxLength=32)
        self.nameInput.OnReturn = self.Search
        Button(parent=self.topParent, label=localization.GetByLabel('UI/Wallet/WalletWindow/WalletSearch'), pos=(self.nameInput.left + self.nameInput.width + 2,
         self.nameInput.top,
         0,
         0), func=self.Search, btn_default=1)
        self.SetHint(localization.GetByLabel('UI/Common/TypeInSearch'))

    def Search(self, *args):
        scrolllist = []
        self.inviteButton.Disable()
        self.ShowLoad()
        try:
            self.searchStr = self.GetSearchStr()
            self.SetHint()
            if len(self.searchStr) < 1:
                self.SetHint(localization.GetByLabel('UI/Shared/PleaseTypeSomething'))
                return
            result = sm.RemoteSvc('lookupSvc').LookupEvePlayerCharacters(self.searchStr, 0)
            if result is None or not len(result):
                self.SetHint(localization.GetByLabel('EVE/UI/Wallet/WalletWindow/SearchNoResults'))
                return
            cfg.eveowners.Prime([ each.characterID for each in result ])
            for each in result:
                owner = cfg.eveowners.Get(each.characterID)
                scrolllist.append(GetFromClass(Item, {'label': owner.name,
                 'typeID': owner.typeID,
                 'itemID': each.characterID,
                 'OnClick': self.EnableInviteButton,
                 'OnDblClick': self.InviteToCorp}))

        finally:
            self.scroll.Load(fixedEntryHeight=18, contentList=scrolllist, noContentHint=localization.GetByLabel('UI/Wallet/WalletWindow/SearchNoResults'))
            self.HideLoad()

    def EnableInviteButton(self, *args):
        if self.GetSelected:
            self.inviteButton.Enable()

    def GetSearchStr(self):
        return self.nameInput.GetValue().strip()

    def SetHint(self, hintstr = None):
        if self.scroll:
            self.scroll.ShowHint(hintstr)

    def InviteToCorp(self, *args):
        sel = self.GetSelected()
        if sel:
            charID = sel[0].itemID
            sm.StartService('corp').InviteToJoinCorp(charID)
            self.CloseByUser()

    def GetSelected(self):
        sel = self.scroll.GetSelected()
        return sel

    def OnCancel(self, *args):
        self.CloseByUser()
