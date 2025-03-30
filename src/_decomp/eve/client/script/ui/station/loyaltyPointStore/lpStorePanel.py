#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\loyaltyPointStore\lpStorePanel.py
import evetypes
import localization
import uthread
from carbon.client.script.util.misc import RunOnceMethod, Despammer
from carbonui import ButtonVariant, uiconst
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveScroll, eveLabel
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.station.loyaltyPointStore.lpOfferEntry2 import LPOfferEntry2
from eve.client.script.ui.station.loyaltyPointStore.lpStoreFilters import LPStoreFilters
from eve.client.script.ui.station.loyaltyPointStore.lpStoreSignals import on_corp_lp_purchases_killswitch_changed
from eve.client.script.ui.station.lpstoreRequirement import LpRequirement, ISKRequirement
from eve.common.lib import appConst
from inventorycommon import typeHelpers

class LPStorePanel(Container):
    __notifyevents__ = ['OnLPStoreFilterChange',
     'OnLPStoreCurrentPresetChange',
     'OnLPStorePresetsChange',
     'OnSessionChanged',
     'OnAccountChange_Local']

    def ApplyAttributes(self, attributes):
        super(LPStorePanel, self).ApplyAttributes(attributes)
        self.lpSvc = sm.GetService('lpstore')
        self.loyaltyPointsWalletSvc = sm.GetService('loyaltyPointsWalletSvc')
        self.corpID = attributes.corpID
        self.lpStoreWindow = attributes.lpStoreWindow
        self.hasStandingsRequirement = self._HasStandingsRequirement()
        self.offerRefreshDespammerInitiated = False
        self.ConstructTopParent()
        self.ConstructHeader()
        self.ConstructScroll()
        self.ConstructLoadingWheel()
        sm.RegisterNotify(self)
        on_corp_lp_purchases_killswitch_changed.connect(self._on_corp_lp_purchases_killswitch_changed)

    def ConstructLoadingWheel(self):
        self._loadingWheel = LoadingWheel(parent=self.scroll, align=uiconst.CENTER, width=64, height=64, state=uiconst.UI_HIDDEN)

    def ShowLoad(self):
        if self._loadingWheel:
            self._loadingWheel.state = uiconst.UI_NORMAL
        self.lpStoreWindow.ShowLoad()

    def HideLoad(self):
        if self._loadingWheel:
            self._loadingWheel.state = uiconst.UI_HIDDEN
        self.lpStoreWindow.HideLoad()

    def ConstructTopParent(self):
        self.topParent = ContainerAutoSize(name='topParent', align=uiconst.TOTOP, parent=self)

    def ConstructHeader(self):
        self.ConstructInfoCont()
        self.ConstructFilterCont()

    def ConstructInfoCont(self):
        self.corpInfoCont = ContainerAutoSize(name='corpInfoCont', parent=self.topParent, align=uiconst.TOTOP, alignMode=uiconst.CENTERLEFT)
        self.ConstructCorpIcon()
        self.ConstructCorpLabelCont()

    def ConstructCorpIcon(self):
        corpIconCont = Container(name='corpIconCont', parent=self.corpInfoCont, align=uiconst.CENTERLEFT, width=64, height=64)
        corpIcon = GetLogoIcon(itemID=self.corpID, parent=corpIconCont, acceptNone=False, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, pos=(0, 0, 64, 64))
        corpIcon.OnClick = self.ShowCorpInfo
        corpIcon.SetSize(64, 64)

    def ConstructCorpLabelCont(self):
        lpBalanceCont = ContainerAutoSize(name='lpBalanceCont', parent=self.corpInfoCont, align=uiconst.TOLEFT, left=80, width=300)
        self.corpLPsLabel = eveLabel.EveCaptionSmall(parent=lpBalanceCont, name='corpLPsLabel', align=uiconst.TOTOP)
        self.useCorpWalletsCb = Checkbox(parent=lpBalanceCont, name='useCorpWalletsCb', align=uiconst.TOTOP, text=localization.GetByLabel('UI/LPStore/UseCorpWallets'), hint=localization.GetByLabel('UI/LPStore/UseCorpWalletsTooltip'), checked=self.lpSvc.IsUsingCorpWallets(self.corpID), callback=self.OnUseCorpWalletsCheckboxChange)
        self.useCorpWalletsCb.display = self.lpSvc.CanCharacterUseCorpWallets(self.corpID)
        self.exchangeButton = Button(parent=self.corpInfoCont, name='exchangeBtn', label=localization.GetByLabel('UI/LPStore/ConcordExchange'), variant=ButtonVariant.GHOST, align=uiconst.CENTERRIGHT)
        if self.lpSvc.IsRWCorp(self.corpID):
            self.exchangeButton.display = False

    def OnUseCorpWalletsCheckboxChange(self, cb):
        if cb.checked:
            self.lpSvc.UseCorporationWallets(self.corpID)
        else:
            self.lpSvc.UseCharacterWallets(self.corpID)

    def ShowCorpInfo(self):
        sm.GetService('info').ShowInfo(appConst.typeCorporation, self.corpID)

    def ConstructFilterCont(self):
        self.filters = LPStoreFilters(parent=self.topParent, name='filters', align=uiconst.TOTOP, height=HEIGHT_NORMAL, padding=(0, 8, 0, 8), filterEditClearedCallback=self.RefreshOffers, filterEditCallback=self.RefreshOffers, corpID=self.corpID)

    def ConstructScroll(self):
        self.scroll = eveScroll.Scroll(parent=self, name='lpStoreScroll', align=uiconst.TOALL)
        self.scroll.sr.id = 'lpStoreScroll'

    def RefreshIfNotAlready(self):
        self.InitOfferRefreshDespammer()
        self.Refresh()
        self.filters.Refresh()

    RefreshIfNotAlready = RunOnceMethod(RefreshIfNotAlready)

    def Refresh(self):
        self.ShowLoad()
        try:
            self.factionID = sm.GetService('map').GetItem(eve.session.solarsystemid2).factionID
            self.RefreshPresets()
            lpAmount = self.lpSvc.GetLPBalanceForStorePurchase(self.corpID)
            self.corpLPsLabel.text = self._GetCorpLPsLabel(lpAmount)
        finally:
            self.HideLoad()

        exchangeRate = self.lpSvc.GetConcordLPExchangeRate(self.corpID)
        if self.lpSvc.IsUsingCharacterWallets(self.corpID) and exchangeRate is not None and exchangeRate > 0.0 and self.loyaltyPointsWalletSvc.GetCharacterConcordLPBalance() * exchangeRate > 1:
            self.EnableExchangeButton()
        else:
            self.DisableExchangeButton()
        self.RefreshOffers()

    def _OnClose(self, *etc):
        self.ReleaseOfferRefreshDespammer()

    def OpenConcordExchange(self):
        self.DisableExchangeButton(suppressHint=True)
        self.lpSvc.OpenConcordExchange(sm.GetService('station').stationItem.ownerID)

    def DisableExchangeButton(self, suppressHint = False):
        self.exchangeButton.Disable()
        self.exchangeButton.OnClick = None
        fromCorpName = cfg.eveowners.Get(appConst.ownerCONCORD).ownerName
        toCorpName = cfg.eveowners.Get(self.corpID).ownerName
        if suppressHint:
            self.exchangeButton.SetHint('')
        else:
            exchangeRate = self.lpSvc.GetConcordLPExchangeRate(self.corpID)
            if self.lpSvc.IsUsingCorpWallets(self.corpID):
                hint = localization.GetByLabel('UI/LPStore/CannotExchangeCorporationLP')
            elif exchangeRate is None or exchangeRate == 0.0:
                hint = self._GetExchangeRateHint(fromCorpName, toCorpName)
            elif fromCorpName == toCorpName:
                hint = localization.GetByLabel('UI/LPStore/ExchangeProhibited', fromCorpName=fromCorpName)
            else:
                hint = localization.GetByLabel('UI/LPStore/ExchangeUnavailable', fromCorpName=fromCorpName, toCorpName=toCorpName)
            self.exchangeButton.SetHint(hint)

    def EnableExchangeButton(self):
        self.exchangeButton.Enable()
        self.exchangeButton.OnClick = lambda *discard: self.OpenConcordExchange()
        fromCorpName = cfg.eveowners.Get(appConst.ownerCONCORD).ownerName
        toCorpName = cfg.eveowners.Get(self.corpID).ownerName
        exchangeRate = self.lpSvc.GetConcordLPExchangeRate(self.corpID)
        self.exchangeButton.SetHint(localization.GetByLabel('UI/LPStore/ConvertLPMsg', toCorpName=toCorpName, exchangeRate=exchangeRate, fromCorpName=fromCorpName))

    def _RefreshOffersInternal(self):
        self.ShowLoad()
        try:
            filters, textFilter = self.filters.GetCurrentFilters()
            scroll = self.scroll
            pos = scroll.GetScrollProportion()
            storeOffers = self._GetStoreOffers()
            offers = self._ProcessOffers(storeOffers, filters, textFilter)
            self.scroll.sr.fixedColumns = self._GetMinColumnWidths()
            scroll.LoadContent(headers=self._GetHeaders(), contentList=offers, customColumnWidths=True, noContentHint=localization.GetByLabel('UI/LPStore/NoMatchingOffers'), sortby=self._GetSortByLabel())
            columnWidthSettingsVersion = 1
            languageID = localization.util.GetLanguageID()
            settingsKey = 'columnWidthsReset_%s_%s' % (columnWidthSettingsVersion, languageID)
            if offers and not settings.user.ui.Get(settingsKey, False):
                scroll.ResetColumnWidths()
                settings.user.ui.Set(settingsKey, True)
            scroll.ScrollToProportion(pos)
        finally:
            self.HideLoad()

    def _GetStoreOffers(self):
        return sm.GetService('lpstore').GetOffers(self.corpID)

    def _ProcessOffers(self, storeOffers, filters, textFilter):
        offers = []
        currentIskBalance = self.lpSvc.GetISKBalanceForStorePurchase(self.corpID)
        currentLPBalance = self.lpSvc.GetLPBalanceForStorePurchase(self.corpID)
        currentAKBalance = self.lpSvc.GetMyAnalysisKredits()
        for offer in storeOffers:
            if not self.Check(offer, filters, textFilter):
                continue
            offer['sort_%s' % localization.GetByLabel('UI/LPStore/cost')] = (offer[LpRequirement.LP_REQUIREMENT_NAME], offer[ISKRequirement.ISK_REQUIREMENT_NAME])
            offer['sort_%s' % localization.GetByLabel('UI/LPStore/RequiredItems')] = len(offer['reqItems'])
            offer['iskBalance'] = currentIskBalance
            offer['lpBalance'] = currentLPBalance
            offer['akBalance'] = currentAKBalance
            offers.append(GetFromClass(LPOfferEntry2, offer))

        return offers

    def InitOfferRefreshDespammer(self):
        self.offerRefreshDespammerInitiated = True
        self.offerRefreshDespammer = Despammer(self._RefreshOffersInternal, delay=200)
        self._RefreshOffers = self.offerRefreshDespammer.Send

    def RefreshOffers(self):
        if hasattr(self, '_RefreshOffers'):
            self._RefreshOffers()

    def _GetHeaders(self):
        return LPOfferEntry2.Headers

    def _GetMinColumnWidths(self):
        return LPOfferEntry2.ColumnWidths

    def _HasStandingsRequirement(self):
        for offer in sm.GetService('lpstore').GetOffers(self.corpID):
            if offer.Get('requiredStandings', None):
                return True

        return False

    def ReleaseOfferRefreshDespammer(self):
        if hasattr(self, 'offerRefreshDespammer'):
            uthread.new(self.offerRefreshDespammer.Stop)
            del self.offerRefreshDespammer

    def OnLPStoreFilterChange(self):
        self.RefreshOffers()

    def OnLPStorePresetsChange(self):
        self.RefreshPresets()

    def OnLPStoreCurrentPresetChange(self):
        self.RefreshPresets()

    def OnSessionChanged(self, _is_remote, _session, change):
        if 'corprole' in change or 'corpAccountKey' in change:
            self.useCorpWalletsCb.display = self.lpSvc.CanCharacterUseCorpWallets(self.corpID)
            if not self.useCorpWalletsCb.display:
                self.useCorpWalletsCb.SetChecked(False, False)
            self.OnUseCorpWalletsCheckboxChange(self.useCorpWalletsCb)

    def RefreshPresets(self):
        self.ShowLoad()
        try:
            self.filters.RefreshPresets()
        finally:
            self.HideLoad()

    def Check(self, offer, filters, textFilter = ''):
        if textFilter and evetypes.GetName(offer.typeID).lower().find(textFilter) < 0:
            return False
        for name, val in filters.iteritems():
            if not getattr(self, 'Check_%s' % name)(offer, val):
                return False

        return True

    def CategoryFromType(self, typeID):
        return evetypes.GetCategoryID(typeID)

    def GroupFromType(self, typeID):
        return evetypes.GetGroupID(typeID)

    def Check_rewardCategory(self, offer, val):
        return self.CategoryFromType(offer.typeID) == val

    def Check_rewardGroup(self, offer, val):
        return self.GroupFromType(offer.typeID) == val

    def Check_rewardType(self, offer, val):
        return offer.typeID == val

    def Check_reqCategory(self, offer, val):
        for typeID, qty in offer.reqItems:
            if self.CategoryFromType(typeID) == val:
                return True

        return False

    def Check_reqGroup(self, offer, val):
        for typeID, qty in offer.reqItems:
            if self.GroupFromType(typeID) == val:
                return True

        return False

    def Check_reqType(self, offer, val):
        for typeID, qty in offer.reqItems:
            if typeID == val:
                return True

        return False

    def Check_reqIllegal(self, offer, _val):
        for typeID, qty in offer.reqItems:
            if self.factionID in typeHelpers.GetIllegality(typeID):
                return False

        return True

    def Check_reqNotInHangar(self, offer, _val):
        for typeID, qty in offer.reqItems:
            if not self.lpSvc.HaveItem(typeID, qty):
                return False

        return True

    def Check_minLP(self, offer, val):
        return offer.lpCost >= val

    def Check_maxLP(self, offer, val):
        return offer.lpCost <= val

    def Check_minISK(self, offer, val):
        return offer.iskCost >= val

    def Check_maxISK(self, offer, val):
        return offer.iskCost <= val

    def Check_minAnalysisKredits(self, offer, val):
        analysisKreditsCost = getattr(offer, 'akCost', None)
        if analysisKreditsCost:
            return analysisKreditsCost >= val
        return False

    def Check_maxAnalysisKredits(self, offer, val):
        analysisKreditsCost = getattr(offer, 'akCost', None)
        if analysisKreditsCost:
            return analysisKreditsCost <= val
        return True

    def Check_dynamicMaxLP(self, offer, _val):
        return self.Check_maxLP(offer, self.lpSvc.GetLPBalanceForStorePurchase(self.corpID))

    def Check_dynamicMaxISK(self, offer, _val):
        return self.Check_maxISK(offer, self.lpSvc.GetISKBalanceForStorePurchase(self.corpID))

    def Check_dynamicMaxAnalysisKredits(self, offer, _val):
        return self.Check_maxAnalysisKredits(offer, self.lpSvc.GetMyAnalysisKredits())

    def Check_dynamicStandings(self, offer, _val):
        return self.lpSvc.IsStandingsFulfilled(offer)

    def _GetCorpLPsLabel(self, lpAmount):
        return localization.GetByLabel('UI/LPStore/CurrentLPs', lpAmount=lpAmount)

    def _GetSortByLabel(self):
        return localization.GetByLabel('UI/LPStore/LPCost')

    def _GetExchangeRateHint(self, fromCorpName, toCorpName):
        return localization.GetByLabel('UI/LPStore/ExchangeRateNotDefined', fromCorpName=fromCorpName, toCorpName=toCorpName)

    def _on_corp_lp_purchases_killswitch_changed(self, _value):
        self.useCorpWalletsCb.display = self.lpSvc.CanCharacterUseCorpWallets(self.corpID)
        self.useCorpWalletsCb.SetChecked(False, report=False)
        self.lpSvc.ResetWalletsSourceChoices()

    def OnAccountChange_Local(self, accountKey, ownerID, balance):
        if balance is None:
            return
        if accountKey not in ('cash', 'cash2', 'cash3', 'cash4', 'cash5', 'cash6', 'cash7'):
            return
        if ownerID == session.charid:
            self._on_char_account_change()
        elif ownerID == session.corpid:
            self._on_corp_account_change()

    def _on_char_account_change(self):
        self.RefreshOffers()

    def _on_corp_account_change(self):
        self.RefreshOffers()
