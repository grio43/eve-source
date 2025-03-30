#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\loyaltyPointStore\paragonLpStorePanel.py
import evetypes
import copy
from carbonui.button.const import HEIGHT_NORMAL
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.cosmetics.structure.cosmeticLicenseErrorScreen import CosmeticLicenseErrorScreen
from eve.client.script.ui.station.loyaltyPointStore.lpOfferEntry import AllianceLogoLPOfferEntry, CorporationLogoLPOfferEntry, LPOfferEntry, on_cosmetic_license_purchase_failed
from eve.client.script.ui.station.loyaltyPointStore.lpOfferEntry2 import LPOfferEntry2
from eve.client.script.ui.station.loyaltyPointStore.paragonLpStoreFilters import ParagonLPStoreFilters
from eve.client.script.ui.station.loyaltyPointStore.paragonLpStoreConst import FILTER_ACQUIRED, FILTER_ALLIANCE_EMBLEMS, FILTER_ALL_FACTIONS, FILTER_ALL_HULLS, FILTER_CORP_EMBLEMS, FILTER_EMPIRE_FACTIONS, FILTER_FACTION, FILTER_HULL, FILTER_OTHER_FACTIONS
from eve.common.lib import appConst
from carbonui import uiconst
from inventorycommon.const import typeLoyaltyPointsHeraldry
from localization import GetByLabel
from eve.client.script.ui.control.infoNotice import InfoNotice
from eve.client.script.ui.station.loyaltyPointStore.lpStorePanel import LPStorePanel
from shipcosmetics.client.licensegateway.licenseSignals import on_enable_heraldry_purchase_flag_change
from shipcosmetics.common.const import CosmeticsType
_BUY_BUTTON_COLUMN_EMPTY_TITLE = ' '
_BUY_BUTTON_COLUMN_MIN_WIDTH = 220
REWARD_COLUMN_WIDTH_MIN = 568
COST_COLUMN_WIDTH_MIN = 105

class ParagonLPStorePanel(LPStorePanel):
    __notifyevents__ = ['OnLPStoreParagonFilterChange']

    def ApplyAttributes(self, attributes):
        self.cosmeticsLicenseSvc = sm.GetService('cosmeticsLicenseSvc')
        self.fetchFreshCosmeticLicenses = True
        self._errorScreenPadding = attributes.errorScreenPadding
        super(ParagonLPStorePanel, self).ApplyAttributes(attributes)
        on_cosmetic_license_purchase_failed.connect(self._OnCosmeticLicensePurchaseFailed)
        on_enable_heraldry_purchase_flag_change.connect(self._OnHeraldryPurchaseFlagChanged)
        sm.RegisterNotify(self)

    def _OnClose(self, *args):
        on_cosmetic_license_purchase_failed.disconnect(self._OnCosmeticLicensePurchaseFailed)
        on_enable_heraldry_purchase_flag_change.disconnect(self._OnHeraldryPurchaseFlagChanged)
        super(ParagonLPStorePanel, self)._OnClose(*args)

    def ConstructTopParent(self):
        padding = (-self._errorScreenPadding[0],
         -self._errorScreenPadding[1],
         -self._errorScreenPadding[2],
         -self._errorScreenPadding[3])
        self.errorScreen = CosmeticLicenseErrorScreen(name='errorScreen', parent=self, align=uiconst.TOALL, padding=padding)
        self.errorScreen.CloseScreen(animate=False)
        super(ParagonLPStorePanel, self).ConstructTopParent()

    def ConstructInfoCont(self):
        super(ParagonLPStorePanel, self).ConstructInfoCont()
        InfoNotice(name='autoInjectInfo', parent=self.topParent, align=uiconst.TOTOP, labelText=GetByLabel('UI/ShipCosmetics/AutoInjectNotice'))
        if self.cosmeticsLicenseSvc.is_emblem_lp_cost_removed():
            InfoNotice(name='experimentInfo', parent=self.topParent, align=uiconst.TOTOP, labelText='LP Costs for all Emblems have been reduced to zero for the purpose of this mass test', padTop=6)

    def ConstructFilterCont(self):
        self.filters = ParagonLPStoreFilters(parent=self.topParent, name='filters', align=uiconst.TOTOP, height=HEIGHT_NORMAL, padding=(0, 32, 0, 16), filterEditClearedCallback=self.RefreshOffers, filterEditCallback=self.RefreshOffers, corpID=self.corpID)

    def RefreshPresets(self):
        pass

    def _GetStoreOffers(self):
        if self.cosmeticsLicenseSvc.are_heraldry_purchases_enabled():
            return sm.GetService('lpstore').GetOffers(self.corpID)
        else:
            return []

    def OnLPStoreParagonFilterChange(self):
        self.RefreshOffers()

    def _ProcessOffers(self, storeOffers, filters, textFilter):
        offers = []
        if self.cosmeticsLicenseSvc.are_heraldry_purchases_enabled():
            try:
                ownedLicenses = self.cosmeticsLicenseSvc.get_owned_ship_licenses(force_refresh=self.fetchFreshCosmeticLicenses)
                if self.fetchFreshCosmeticLicenses:
                    self.fetchFreshCosmeticLicenses = False
            except RuntimeError:
                ownedLicenses = []
                self.errorScreen.ShowScreen(GetByLabel('UI/LPStore/FetchLicensesFailedErrorMessage'), GetByLabel('UI/LPStore/FetchLicensesFailedErrorSubtext'), GetByLabel('UI/LPStore/FetchingFailedButton'), self._RetryFetchingCosmeticsLicenses)

        def IsLicenseOwned(license):
            for ownedLicense in ownedLicenses:
                if ownedLicense.fsdTypeID == license.fsdTypeID:
                    return True

            return False

        for offer in storeOffers:
            if evetypes.GetGroupID(offer.typeID) == appConst.groupShipCosmeticLicense:
                cosmeticLicense = self.cosmeticsLicenseSvc.get_by_ship_license_type_id(offer.typeID)
                offer['isOwned'] = IsLicenseOwned(cosmeticLicense)
                offer['shipTypeID'] = cosmeticLicense.shipTypeID
                offer['cosmeticType'] = cosmeticLicense.cosmeticType
                if self.cosmeticsLicenseSvc.is_emblem_lp_cost_removed():
                    offer = copy.deepcopy(offer)
                    offer.lpCost = 0
                sortID = 'sort_%s' % GetByLabel('UI/LPStore/EMCost')
                offer[sortID] = offer.lpCost
                if not self.Check(offer, filters, textFilter):
                    continue
                if cosmeticLicense.cosmeticType == CosmeticsType.ALLIANCE_LOGO:
                    offers.append(GetFromClass(AllianceLogoLPOfferEntry, offer))
                elif cosmeticLicense.cosmeticType == CosmeticsType.CORPORATION_LOGO:
                    offers.append(GetFromClass(CorporationLogoLPOfferEntry, offer))
            else:
                offers.append(GetFromClass(LPOfferEntry, offer))

        return offers

    def Check(self, offer, filters, textFilter = ''):
        if textFilter and evetypes.GetName(offer.typeID).lower().find(textFilter) < 0:
            return False
        if not hasattr(offer, 'shipTypeID') or not hasattr(offer, 'isOwned') or not hasattr(offer, 'cosmeticType'):
            return False
        includedCosmeticsTypes = []
        for f, value in filters.iteritems():
            if f == FILTER_FACTION and value != FILTER_ALL_FACTIONS:
                factionID = evetypes.GetFactionID(offer.shipTypeID)
                if value == FILTER_OTHER_FACTIONS:
                    if factionID in FILTER_EMPIRE_FACTIONS:
                        return False
                elif factionID is None or factionID != value:
                    return False
            groupID = evetypes.GetGroupID(offer.shipTypeID)
            if f == FILTER_HULL and value != FILTER_ALL_HULLS:
                if groupID != value:
                    return False
            if f == FILTER_CORP_EMBLEMS and value:
                includedCosmeticsTypes.append(CosmeticsType.CORPORATION_LOGO)
            if f == FILTER_ALLIANCE_EMBLEMS and value:
                includedCosmeticsTypes.append(CosmeticsType.ALLIANCE_LOGO)
            if f == FILTER_ACQUIRED and value:
                if offer.isOwned:
                    return False

        if offer.cosmeticType not in includedCosmeticsTypes:
            return False
        return True

    def _GetHeaders(self):
        headers = [GetByLabel('UI/LPStore/Reward')]
        requirements = self.lpSvc.GetRequirements(self.corpID)
        for requirementColumn in requirements:
            costLabelPath = requirementColumn.costLabelPath
            if costLabelPath:
                costLabel = GetByLabel(costLabelPath)
                headers.append(costLabel)

        if self.hasStandingsRequirement:
            headers.append(GetByLabel('UI/LPStore/StandingsRequired'))
        headers.append(_BUY_BUTTON_COLUMN_EMPTY_TITLE)
        return headers

    def _GetMinColumnWidths(self):
        minColumnWidths = {GetByLabel('UI/LPStore/Reward'): REWARD_COLUMN_WIDTH_MIN}
        requirements = self.lpSvc.GetRequirements(self.corpID)
        for requirementColumn in requirements:
            costLabelPath = requirementColumn.costLabelPath
            if costLabelPath:
                costLabel = GetByLabel(costLabelPath)
                minColumnWidths[costLabel] = COST_COLUMN_WIDTH_MIN

        if self.hasStandingsRequirement:
            minColumnWidths[GetByLabel('UI/LPStore/StandingsRequired')] = 86
        minColumnWidths[_BUY_BUTTON_COLUMN_EMPTY_TITLE] = _BUY_BUTTON_COLUMN_MIN_WIDTH
        return minColumnWidths

    def _RetryFetchingCosmeticsLicenses(self):
        self.errorScreen.CloseScreen(True)
        self.Refresh()

    def _OnHeraldryPurchaseFlagChanged(self, _flagValue):
        if self.offerRefreshDespammerInitiated:
            self.RefreshOffers()

    def _CloseErrorScreen(self):
        self.errorScreen.CloseScreen(True)

    def _OnCosmeticLicensePurchaseFailed(self):
        self.errorScreen.ShowScreen(GetByLabel('UI/LPStore/CosmeticLicensePurchaseFailedError'), GetByLabel('UI/LPStore/CosmeticLicensePurchaseFailedSubtext'), GetByLabel('UI/LPStore/CosmeticLicensePurchaseFailedButton'), self._CloseErrorScreen)

    def _GetCorpLPsLabel(self, lpAmount):
        return GetByLabel('UI/Common/TypeAmount', item=typeLoyaltyPointsHeraldry, amount=lpAmount)

    def _GetSortByLabel(self):
        return GetByLabel('UI/LPStore/EMCost')

    def _GetExchangeRateHint(self, fromCorpName, toCorpName):
        return GetByLabel('UI/LPStore/ExchangeRateNotDefinedEM', fromCorpName=fromCorpName, toCorpName=toCorpName)

    def _OnSizeChange_NoBlock(self, *args):
        super(ParagonLPStorePanel, self)._OnSizeChange_NoBlock(*args)
        if hasattr(self, 'errorScreen'):
            self.errorScreen.AdjustWidth(args[0])
