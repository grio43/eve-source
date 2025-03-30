#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_recruitment.py
import localization
import utillib
from carbonui import uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.basicDynamicScroll import BasicDynamicScroll
from carbonui.control.checkbox import Checkbox
from carbonui.control.tabGroup import TabGroup, GetTabData
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.shared.neocom.corporation.recruitment.corpRecruitmentContainer import CorpRecruitmentAdCreationAndEdit
from eve.client.script.ui.shared.neocom.corporation.recruitment.recruitmentEntry import HasAccess, RecruitmentEntry
from eve.client.script.ui.shared.neocom.corporation.recruitment.welcomeMailWindow import WelcomeMailWindow
from eve.common.script.sys import idCheckers
from evecorporation.recruitment import get_recruitment_groups, get_recruitment_types, get_recruitment_types_by_group_id
from eveservices.menu import GetMenuService
from globalConfig.getFunctions import IsContentComplianceControlSystemActive
from menu import MenuLabel
RECRUITMENT_ADVERTS = 'corp'

class CorpRecruitment(Container):
    __notifyevents__ = ['OnCorporationChanged']
    is_loaded = False
    corpAdvertsInited = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.corpSvc = sm.GetService('corp')
        self.applicationsEnabled = None
        corpUISignals.on_corporation_recruitment_ad_changed.connect(self.OnCorporationRecruitmentAdChanged)

    def Load(self, panel_id, *args):
        if not self.is_loaded:
            self.is_loaded = True
            self.ConstructLayout()
        self.LoadAdverts()

    def GetCorpRecruitmentAds(self, *args):
        ads = self.corpSvc.GetRecruitmentAdsForCorporation()
        ownersToPrime = set()
        for ad in ads:
            if ad.corporationID:
                ownersToPrime.add(ad.corporationID)
            if ad.allianceID:
                ownersToPrime.add(ad.allianceID)

        if ownersToPrime:
            cfg.eveowners.Prime(list(ownersToPrime))
        return ads

    def ConstructLayout(self, *args):
        self.corpAdvertContainer = Container(parent=self, name='corpAdvertContainer', align=uiconst.TOALL)
        self.corpAdvertContentContainer = Container(parent=self.corpAdvertContainer, name='corpAdvertContentContainer', align=uiconst.TOALL)
        self.corpAdvertContentContainer.Show()
        self.corpAdvertContentContainer.Flush()
        self.ConstructButtonGroup()
        self.ConstructApplicationCheckbox()
        self.corpAdvertsScroll = BasicDynamicScroll(parent=self.corpAdvertContentContainer, padding=const.defaultPadding)

    def ConstructApplicationCheckbox(self):
        if HasAccess(session.corpid):
            checkboxCont = ContainerAutoSize(parent=self.corpAdvertContentContainer, name='checkboxCont', align=uiconst.TOBOTTOM, padding=(0, 8, 0, 8))
            self.applicationsEnabled = Checkbox(text=localization.GetByLabel('UI/Corporations/CorpDetails/MembershipApplicationEnabled'), parent=checkboxCont, align=uiconst.CENTERTOP, wrapLabel=False, settingsKey='applicationsEnabled', checked=sm.GetService('corp').GetCorporation().isRecruiting, callback=self.OnCheckboxRecruitmentChange)

    def ConstructButtonGroup(self):
        if HasAccess(session.corpid):
            buttonGroup = ButtonGroup(parent=self.corpAdvertContentContainer, align=uiconst.TOBOTTOM)
            if not IsContentComplianceControlSystemActive(sm.GetService('machoNet')):
                buttonGroup.AddButton(localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/CreateRecruitmentAdButtonLabel'), self.CreateCorpAdvertClick)
                buttonGroup.AddButton(localization.GetByLabel('UI/Corporations/Applications/EditWelcomeMail'), self.OpenWelcomeMailWnd)

    def OnCheckboxRecruitmentChange(self, cb, *args):
        corp = sm.GetService('corp').GetCorporation()
        appEnabled = cb.checked
        sm.GetService('corp').UpdateCorporation(corp.description, corp.url, corp.taxRate, appEnabled, corp.loyaltyPointTaxRate)

    def UpdateCreateButton(self):
        if HasAccess(session.corpid):
            btn = getattr(self, 'createButton', None)
            if btn is None:
                return
            if len(self.GetCorpRecruitmentAds()) >= const.corporationMaxRecruitmentAds:
                btn.Disable()
            else:
                btn.Enable()

    def OnCorporationChanged(self, corpID, change, *args):
        if 'isRecruiting' in change:
            cb = self.applicationsEnabled
            if cb is None or cb.destroyed:
                return
            isChecked = change['isRecruiting'][1]
            cb.SetChecked(isChecked, report=0)

    def LoadAdverts(self):
        adverts = self.GetCorpRecruitmentAds()
        scrolllist = self.GetCorpAdvertScrollEntries(adverts)
        self.corpAdvertsScroll.Clear()
        self.corpAdvertsScroll.AddNodes(0, scrolllist)
        if len(adverts):
            self.corpAdvertsScroll.ShowHint(None)
        else:
            corpName = cfg.eveowners.Get(session.corpid).name
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/CorpHasNoRecruitmentAdvertisements', corpName=corpName)
            self.corpAdvertsScroll.ShowHint(hint)

    def CreateCorpAdvertClick(self, clickObj):
        windowID = 'newCorpAd'
        wnd = CorpRecruitmentAdCreationAndEdit.GetIfOpen(windowID=windowID)
        if wnd:
            wnd.Maximize()
        else:
            caption = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/CreateNewAdvert')
            CorpRecruitmentAdCreationAndEdit(windowID=windowID, caption=caption)

    def OpenWelcomeMailWnd(self, *args):
        WelcomeMailWindow()

    def OnCorporationRecruitmentAdChanged(self):
        if self.IsHidden():
            return
        self.LoadAdverts()
        self.UpdateCreateButton()

    def GetCorpAdvertScrollEntries(self, adverts, *args):
        scrolllist = []
        if adverts:
            corpIDs = []
            for advert in adverts:
                corpIDs.append(advert.corporationID)

            corpIDs = list(set(corpIDs))
            cfg.eveowners.Prime(corpIDs)
            cfg.corptickernames.Prime(corpIDs)
            expandedAd = settings.char.ui.Get('corporation_recruitmentad_expanded', {})
            adGroups = get_recruitment_groups()
            adTypesByTypeID = get_recruitment_types()
            adTypesByGroupID = get_recruitment_types_by_group_id()
            for advert in adverts:
                data = utillib.KeyVal()
                data.advert = advert
                data.corporationID = advert.corporationID
                data.allianceID = advert.allianceID
                data.editFunc = self.OpenEditWindow
                data.corpView = True
                data.standaloneMode = False
                data.advertGroups = adGroups
                data.advertTypesByGroupID = adTypesByGroupID
                data.advertTypesByTypeID = adTypesByTypeID
                data.adTitle = advert.title
                data.timeZoneMask1 = advert.hourMask1
                data.minSP = advert.minSP
                data.expandedView = expandedAd.get(data.corpView, None) == advert.adID
                if data.expandedView:
                    data.recruiters = self.corpSvc.GetRecruiters(advert.adID)
                aggressionSettings = self.corpSvc.GetAggressionSettings(advert.corporationID)
                data.friendlyFireStatus = self.corpSvc.GetCorpFriendlyFireStatus(aggressionSettings)
                data.memberCount = len(self.corpSvc.GetMemberIDs())
                scrolllist.append(GetFromClass(RecruitmentEntry, data))

        return scrolllist

    def CorpViewRecruitmentMenu(self, entry, *args):
        if self.destroyed:
            return
        m = []
        if entry.sr.node.advert:
            if idCheckers.IsCorporation(entry.sr.node.corporationID):
                m += [(MenuLabel('UI/Common/Corporation'), GetMenuService().GetMenuFromItemIDTypeID(entry.sr.node.corporationID, const.typeCorporation))]
            if idCheckers.IsAlliance(entry.sr.node.allianceID):
                m += [(MenuLabel('UI/Common/Alliance'), GetMenuService().GetMenuFromItemIDTypeID(entry.sr.node.allianceID, const.typeAlliance))]
            if m:
                m += [None]
            return m

    def OpenEditWindow(self, advertData, *args):
        windowID = 'advert_%s' % advertData.adID
        wnd = CorpRecruitmentAdCreationAndEdit.GetIfOpen(windowID=windowID)
        if wnd:
            wnd.Maximize()
        else:
            caption = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/EditAdvert', adTitle=advertData.title)
            CorpRecruitmentAdCreationAndEdit(windowID=windowID, advertData=advertData, caption=caption)
