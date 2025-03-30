#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\loyaltyPointStore\lpStoreSvc.py
import copy
import blue
import evetypes
import localization
import log
import sys
import telemetry
import uthread
import launchdarkly
from appConst import corpHeraldry
from carbon.client.script.util.misc import TryDel
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from carbonui.util.bunch import Bunch
from caching.memoize import Memoize
from collections import defaultdict
from carbon.common.script.util.format import FmtAmt
from corporation.common import FLAG_CORP_LP_PURCHASES_KILLSWITCH, FLAG_CORP_LP_PURCHASES_KILLSWITCH_DEFAULT
from cosmetics.common import cosmeticsConst
from eve.client.script.ui.station.loyaltyPointStore.lpExchangeDialog import LPExhangeDialog
from eve.client.script.ui.station.loyaltyPointStore.lpStoreSignals import on_corp_lp_purchases_killswitch_changed
from eve.client.script.ui.station.loyaltyPointStore.lpStoreWindow import LPStoreWindow
from eve.client.script.ui.station.loyaltyPointStore.lpUtil import GetItemText
from eve.client.script.ui.station.loyaltyPointStore.paragonLpStoreConst import DEFAULT_PARAGON_FILTERS
from eve.client.script.ui.station.lpstoreRequirement import LpRequirement, ISKRequirement, AnalysisKreditsRequirement, EMRequirement
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from eve.common.script.util.facwarCommon import GetFwFactionIDForNpcCorp, IsPirateFWFaction
from loyaltypoints.lpUtil import get_hardcoded_lp_stations_for_corp
from npcs.npccorporations import get_corporation_exchange_rates
from resourcewars.common.const import FACTION_TO_RW_LP_CORP
from uthread2 import BufferedCall

class LPStoreSvc(Service):
    __guid__ = 'svc.lpstore'
    __notifyevents__ = ['OnAccountChange',
     'ProcessSessionChange',
     'OnCharacterLPBalanceChange_Local',
     'OnCorporationLPBalanceChange_Local',
     'OnAnalysisKreditsChange',
     'OnItemChangeProcessed']
    __dependencies__ = ['settings',
     'clientPathfinderService',
     'loyaltyPointsWalletSvc',
     'wallet']
    settingsVersion = 4

    def Run(self, *etc):
        Service.Run(self, *etc)
        self.cache = Bunch()
        self._ClearCache()
        self.LpOfferRequirements = {}
        self.defaultPreset = localization.GetByLabel('UI/LPStore/PresetAll')
        self.currentParagonFilters = {}
        self.storesUsingCorpWalletMode = set()
        self._corp_spending_killswitch = FLAG_CORP_LP_PURCHASES_KILLSWITCH_DEFAULT
        ld_client = launchdarkly.get_client()
        ld_client.notify_flag(FLAG_CORP_LP_PURCHASES_KILLSWITCH, FLAG_CORP_LP_PURCHASES_KILLSWITCH_DEFAULT, self._on_corp_spending_killswitch_changed)

    @staticmethod
    def _GetRemoteLPService():
        return sm.RemoteSvc('LPSvc')

    def _ClearCache(self):
        self.cache.clear()
        self.cache.offers = {}

    def GetCurrentFilters(self):
        return self.currentFilters.copy()

    def GetCurrentParagonFilters(self):
        return copy.deepcopy(self.currentParagonFilters)

    def GetCurrentPresetLabel(self):
        return self.currentPreset

    def IsRWCorp(self, corpID):
        return corpID in FACTION_TO_RW_LP_CORP.values()

    def OpenConcordExchange(self, corpID):
        exchangeRate = self.GetConcordLPExchangeRate(corpID)
        myConcordLP = self.loyaltyPointsWalletSvc.GetCharacterConcordLPBalance()
        corporationLPs = self.loyaltyPointsWalletSvc.GetCharacterWalletLPBalance(corpID)
        LPExhangeDialog.CloseIfOpen(windowID='LPExhangeDialog_%s' % corpID)
        LPExhangeDialog.Open(windowID='LPExhangeDialog_%s' % corpID, currentFromCorpLPs=myConcordLP, currentToCorpLPs=corporationLPs, exchangeRate=exchangeRate, toCorpID=corpID)

    def GetConcordLPExchangeRate(self, corpID):
        stationItem = sm.GetService('station').stationItem
        if not corpID and idCheckers.IsNPC(stationItem.ownerID):
            corpID = stationItem.ownerID
        return get_corporation_exchange_rates(appConst.ownerCONCORD, default={}).get(corpID)

    def GetOffers(self, corpID):
        if self.cache.offers.get(corpID, None) is None:
            self.cache.offers[corpID] = sm.RemoteSvc('LPStoreMgr').GetAvailableOffersFromCorp(corpID)
            self._RefreshOfferSortValues(corpID)
        return self.cache.offers[corpID]

    def ConvertConcordLP(self, corpID, amount):
        self._GetRemoteLPService().ExchangeConcordLP(corpID, amount)

    def GetCorpName(self, corpID):
        return cfg.eveowners.Get(corpID).name

    def AddFilters(self, newFilters):
        newFilters = dict(self.currentFilters, **newFilters)
        self.ChangeFilters(newFilters)

    def RemoveFilter(self, key):
        TryDel(self.currentFilters, key)
        self.ChangeFilters(self.currentFilters)

    def ChangeFilters(self, newFilters):
        self.currentFilters = newFilters
        self.currentPreset = localization.GetByLabel('UI/LPStore/PresetNone')
        self._PersistFilters()
        sm.ScatterEvent('OnLPStoreCurrentPresetChange')
        sm.ScatterEvent('OnLPStoreFilterChange')

    def ChangeParagonFilters(self, newFilters):
        self.currentParagonFilters = newFilters
        self._PersistParagonFilters()
        sm.ScatterEvent('OnLPStoreParagonFilterChange')

    def ChangeCurrentPreset(self, newPreset):
        self.currentPreset = newPreset
        self.currentFilters = self._GetPresetFilters(newPreset)
        self._PersistFilters()
        sm.ScatterEvent('OnLPStoreCurrentPresetChange')
        sm.ScatterEvent('OnLPStoreFilterChange')

    def GetPresets(self):
        ret = self._GetDefaultPresets() + self.userPresets
        if self.currentPreset == localization.GetByLabel('UI/LPStore/PresetNone'):
            ret.insert(0, Bunch(label=localization.GetByLabel('UI/LPStore/PresetNone'), filters=None, editable=False))
        return ret

    def AddPreset(self, name, filters):
        self.userPresets.append(Bunch(label=name, filters=filters, editable=True))
        self._PersistPresets()
        sm.ScatterEvent('OnLPStorePresetsChange')

    def OverwritePreset(self, label, filters):
        for i, p in enumerate(self.userPresets):
            if p.label == label:
                self.userPresets[i] = Bunch(label=label, filters=filters.copy(), editable=True)
                self.ChangeCurrentPreset(label)
                self._PersistPresets()
                return
        else:
            log.LogError('svc.lpstore.OverwritePreset: Preset not found.')

    def DeletePreset(self, label):
        if label == self.currentPreset:
            self.ChangeCurrentPreset(self.defaultPreset)
        for p in self.userPresets:
            if p.label == label:
                self.userPresets.remove(p)
                self._PersistPresets()
                sm.ScatterEvent('OnLPStorePresetsChange')
                return
        else:
            log.LogError('svc.lpstore.DeletePreset: Preset not found.')

    def _GetSetting(self, key, default):
        return settings.user.ui.Get('%s_%s' % (key, self.settingsVersion), default)

    def _SetSetting(self, key, value):
        return settings.user.ui.Set('%s_%s' % (key, self.settingsVersion), value)

    def _InitPresets(self):
        if hasattr(self, 'initedPresets'):
            return
        self.userPresets = [ Bunch(**d) for d in self._GetSetting('lpStoreFilterPresets', []) ]
        self.currentPreset = self._GetSetting('lpStoreCurrentPreset', self.defaultPreset)
        if self.currentPreset == localization.GetByLabel('UI/LPStore/PresetNone'):
            self.currentFilters = settings.user.ui.Get('lpStoreCurrentFilters', self._GetPresetFilters(self.defaultPreset))
        else:
            self.currentFilters = self._GetPresetFilters(self.currentPreset)
        self.currentParagonFilters = self._GetSetting('lpStoreCurrentParagonFilters', DEFAULT_PARAGON_FILTERS)
        self.initedPresets = True

    def _GetPresetFilters(self, label):
        if label == localization.GetByLabel('UI/LPStore/PresetNone'):
            return self.currentFilters
        for preset in self.GetPresets():
            if preset.label == label:
                return preset.filters

        return self._GetPresetFilters(self.defaultPreset)

    def _PersistPresets(self):
        self._SetSetting('lpStoreFilterPresets', [ {'label': preset.label,
         'filters': preset.filters,
         'editable': True} for preset in self.userPresets ])
        self.settings.SaveSettings()

    def _PersistFilters(self):
        self._SetSetting('lpStoreCurrentPreset', self.currentPreset)
        if self.currentPreset == localization.GetByLabel('UI/LPStore/PresetNone'):
            self._SetSetting('lpStoreCurrentFilters', self.currentFilters)
        self.settings.SaveSettings()

    def _PersistParagonFilters(self):
        self._SetSetting('lpStoreCurrentParagonFilters', self.currentParagonFilters)
        self.settings.SaveSettings()

    def _GetDefaultPresets(self):
        affordableFilters = {'reqNotInHangar': True,
         'dynamicMaxLP': True,
         'dynamicMaxISK': True,
         'dynamicMaxAnalysisKredits': True,
         'dynamicStandings': True}
        return [Bunch(label=localization.GetByLabel('UI/LPStore/PresetAffordable'), filters=affordableFilters, editable=False), Bunch(label=localization.GetByLabel('UI/LPStore/PresetAll'), filters={}, editable=False)]

    def _RefreshOfferSortValues(self, corpID):
        for offer in self.cache.offers[corpID]:
            self._SetOfferDataSortOrder(offer)

    def AcceptOffer(self, data, numberOfOffers = 1):
        if getattr(self, 'acceptingOffer', False):
            return uiconst.ID_NO
        try:
            self.acceptingOffer = True
            message, args = self._GetConfirmMessage(data, numberOfOffers)
            if eve.Message(message, args, uiconst.OKCANCEL, uiconst.ID_OK) != uiconst.ID_OK:
                return uiconst.OKCANCEL
            if self.IsUsingCharacterWallets(data.corpID):
                ret = sm.RemoteSvc('LPStoreMgr').TakeOfferForCharacter(data.corpID, data.offerID, numberOfOffers)
            elif self.IsUsingCorpWallets(data.corpID):
                ret = sm.RemoteSvc('LPStoreMgr').TakeOfferForCorporation(data.corpID, data.offerID, numberOfOffers)
            else:
                raise RuntimeError('Invalid LPStoreSvc walletMode {0}'.format(self.walletMode))
            if ret:
                eve.Message('LPStoreOfferAccepted', {'name': cfg.eveowners.Get(eve.session.charid).name})
            if self.cache.analysisKredits:
                del self.cache.analysisKredits
            if len(data.reqItems) > 0 and self.cache.hangarInv:
                del self.cache.hangarInv
            self.DirtyWindow()
        finally:
            self.acceptingOffer = False

        if ret:
            return uiconst.ID_YES
        return uiconst.ID_NO

    def _GetConfirmMessage(self, data, numberOfOffers):
        offer = GetItemText(data.typeID, data.qty, numberOfOffers).replace('<br>', ' ')
        if evetypes.GetGroupID(data.typeID) == appConst.groupShipCosmeticLicense:
            price = localization.GetByLabel('UI/LPStore/PriceInEMSimple', lpCost=FmtAmt(data.lpCost))
            return ('ConfirmAcceptEmblemLPOffer', {'offer': offer,
              'price': price})
        else:
            price = self._GetPrice(data, numberOfOffers)
            if self.IsUsingCharacterWallets(data.corpID):
                messageName = 'ConfirmAcceptLPOffer'
            elif self.IsUsingCorpWallets(data.corpID):
                messageName = 'ConfirmAcceptLPOfferUsingCorpWallet'
            else:
                raise RuntimeError('Invalid LPStoreSvc walletMode {0}'.format(self.walletMode))
            return (messageName, {'offer': offer,
              'price': price})

    def _GetPrice(self, data, numberOfOffers):
        price = ''
        for requirement in self.LpOfferRequirements[data.corpID]:
            requirementName = requirement.name
            if requirementName:
                cost = data.Get(requirementName, 0)
                if cost > 0:
                    totalCost = requirement.formatAmount(cost * numberOfOffers)
                    if requirement.priceLabelPath:
                        keywords = {requirementName: totalCost}
                        price += localization.GetByLabel(requirement.priceLabelPath, **keywords) + '<br>'
                    else:
                        price += localization.GetByLabel('UI/LPStore/OfferItems', itemText=totalCost) + '<br>'

        for item in data.reqItems:
            price += localization.GetByLabel('UI/LPStore/OfferItems', itemText=GetItemText(item[0], item[1], numberOfOffers)) + '<br>'

        return price

    def HaveItem(self, typeID, qty):
        return self.GetInvenoryItemQuantity(typeID) >= qty

    def GetInvenoryItemQuantity(self, typeID):
        if self.cache.hangarInv is None:
            hi = {}
            inv = sm.GetService('invCache').GetInventory(appConst.containerHangar).List(appConst.flagHangar)
            for item in inv:
                if not item.singleton:
                    hi[item.typeID] = max(hi.get(item.typeID, 0), item.stacksize)

            self.cache.hangarInv = hi
        return self.cache.hangarInv.get(typeID, 0)

    def GetISKBalanceForStorePurchase(self, storeCorpID):
        if self.IsUsingCharacterWallets(storeCorpID):
            return self.wallet.GetWealth()
        elif self.IsUsingCorpWallets(storeCorpID):
            return self._GetCorpWealth_Memozied(accountKey=session.corpAccountKey)
        else:
            return None

    @Memoize(1.0 / 60.0)
    def _GetCorpWealth_Memozied(self, accountKey):
        return self.wallet.GetCorpWealth(accountKey)

    def GetLPBalanceForStorePurchase(self, storeCorpID):
        if self.IsUsingCharacterWallets(storeCorpID):
            return self.loyaltyPointsWalletSvc.GetCharacterWalletLPBalance(storeCorpID)
        elif self.IsUsingCorpWallets(storeCorpID):
            return self.loyaltyPointsWalletSvc.GetCorporationWalletLPBalance(storeCorpID)
        else:
            return None

    def GetMyAnalysisKredits(self):
        if self.cache.analysisKredits is None:
            self.cache.analysisKredits = sm.RemoteSvc('ProjectDiscovery').get_player_analysis_kredits()
        return self.cache.analysisKredits

    def OpenLPStore(self, corpIDs):
        for corpID in corpIDs:
            self.GetOffers(corpID)

        self._InitPresets()
        self.cache.hangarInv = None
        wnd = LPStoreWindow.GetIfOpen()
        if wnd is None:
            wnd = LPStoreWindow(corpIDs=corpIDs)
        else:
            wnd.ToggleOpenClose()
        if wnd:
            wnd.RefreshIfNotAlready()
            wnd.RefreshOffers()
        return wnd

    def DirtyWindow(self):
        if not getattr(self, 'refreshpending', False):
            self.refreshpending = True
            uthread.pool('lpStore::ReportDirtyWindow', self.__DirtyWindow)

    def __DirtyWindow(self):
        try:
            blue.pyos.synchro.SleepWallclock(1000)
            for corpID in self.cache.offers.keys():
                self._RefreshOfferSortValues(corpID)

            w = self._GetWnd()
            if w is not None:
                w.Refresh()
        finally:
            self.refreshpending = False

    def _GetWnd(self):
        return LPStoreWindow.GetIfOpen()

    def OnAccountChange(self, accountKey, ownerID, _balance):
        if accountKey == 'cash' and ownerID == eve.session.charid:
            self.DirtyWindow()

    def ProcessSessionChange(self, _isremote, _session, change):
        if 'stationid' in change:
            self._ClearCache()
            w = self._GetWnd()
            if w:
                w.Close()
            self.ResetWalletsSourceChoices()
        if 'corprole' in change or 'corpAccountKey' in change:
            self.ResetWalletsSourceChoices()

    def OnCharacterLPBalanceChange_Local(self, issuerCorpID, lpBefore, lpAfter):
        if self.IsUsingCharacterWallets(issuerCorpID):
            self.DirtyWindow()

    def OnCorporationLPBalanceChange_Local(self, issuerCorpID):
        if self.IsUsingCorpWallets(issuerCorpID):
            self.DirtyWindow()

    def OnAnalysisKreditsChange(self):
        currentAnalysisKredits = self.cache.analysisKredits
        if self.cache.analysisKredits is not None:
            del self.cache.analysisKredits
        self.DirtyWindow()
        if session.stationid and currentAnalysisKredits == 0:
            sm.GetService('station').ReloadLobby()

    def OnItemChangeProcessed(self, item = None, change = None):
        self._on_item_change_processed_internal()

    @BufferedCall(200)
    def _on_item_change_processed_internal(self):
        if self.cache.hangarInv is not None:
            del self.cache.hangarInv
        self.DirtyWindow()

    def ResetWalletsSourceChoices(self):
        self.storesUsingCorpWalletMode.clear()
        self.DirtyWindow()

    def UseCharacterWallets(self, storeCorpID):
        self.storesUsingCorpWalletMode.discard(storeCorpID)
        self.DirtyWindow()

    def UseCorporationWallets(self, storeCorpID):
        self.storesUsingCorpWalletMode.add(storeCorpID)
        self.DirtyWindow()

    def IsUsingCharacterWallets(self, storeCorpID):
        return storeCorpID not in self.storesUsingCorpWalletMode

    def IsUsingCorpWallets(self, storeCorpID):
        return storeCorpID in self.storesUsingCorpWalletMode

    def CanCharacterUseCorpWallets(self, storeCorpID):
        if self._corp_spending_killswitch:
            return False
        if storeCorpID == corpHeraldry:
            return False
        return bool(session.corprole & appConst.corpRoleDirector)

    def _SetOfferDataSortOrder(self, data):
        offerData = [(localization.GetByLabel('UI/LPStore/Reward'), evetypes.GetName(data.typeID))]
        for requirement in self.GetRequirements(data.corpID):
            requirementName = requirement.name
            cost = data.Get(requirementName, 0)
            if requirement.costLabelPath:
                costLabel = localization.GetByLabel(requirement.costLabelPath)
                if not cost:
                    cost = 0
                offerData.append((costLabel, cost))

        requiredStandings = data.Get('requiredStandings', None)
        standingsValue = requiredStandings['value'] if requiredStandings else -11
        offerData.append((localization.GetByLabel('UI/LPStore/StandingsRequired'), standingsValue))
        for label, sortval in offerData:
            data.Set('sort_%s' % label, sortval)

    def GetRequirements(self, corpID):
        if corpID not in self.LpOfferRequirements:
            self._CreateRequirements(corpID)
        return self.LpOfferRequirements[corpID]

    def _CreateRequirements(self, corpID):
        if corpID == cosmeticsConst.LP_STORE_CORP:
            self.LpOfferRequirements[corpID] = [EMRequirement(checkAmountFunction=lambda : self.loyaltyPointsWalletSvc.GetCharacterEvermarkBalance())]
        else:
            self.LpOfferRequirements[corpID] = [LpRequirement(checkAmountFunction=lambda : self.GetLPBalanceForStorePurchase(corpID)), ISKRequirement(checkAmountFunction=lambda : self.GetISKBalanceForStorePurchase(corpID)), AnalysisKreditsRequirement(checkAmountFunction=self.GetMyAnalysisKredits)]

    def CanAcceptOffer(self, data):
        requiredItems = data.Get('reqItems', [])
        missingItems = [ 1 for typeID, qty in requiredItems if not self.HaveItem(typeID, qty) ]
        areCostRequirementsFulfilled = self.AreRequirementsFulfilled(data)
        return areCostRequirementsFulfilled and not missingItems and self.IsStandingsFulfilled(data)

    def AreRequirementsFulfilled(self, data):
        requirementList = self.LpOfferRequirements[data.corpID]
        for requirement in requirementList:
            if not self._IsRequirementFulfilled(data, requirement):
                return False

        return True

    def _IsRequirementFulfilled(self, data, requirement):
        requirementName = requirement.name
        if not requirementName:
            return True
        cost = data.Get(requirementName, 0)
        return requirement.checkAmount(cost)

    def IsStandingsFulfilled(self, data):
        requiredStandings = data.Get('requiredStandings', None)
        if not requiredStandings:
            return True
        currentStanding = sm.GetService('standing').GetStandingWithSkillBonus(requiredStandings['ownerID'], session.charid)
        return requiredStandings['value'] < currentStanding

    @telemetry.ZONE_FUNCTION
    def GetNearestDockableWithLPStoreForCorp(self, corpID):
        if sm.GetService('lpstore').IsRWCorp(corpID):
            rw_station_ids = sm.RemoteSvc('RWManager').get_closest_rw_stations(session.solarsystemid2)
            nearestRWStationID = rw_station_ids.get(corpID, None)
            return nearestRWStationID
        stationsOwnedByCorp = sm.RemoteSvc('stationSvc').GetStationsForOwner(corpID)
        stationsOwnedByCorpBySolarSystemID = defaultdict(list)
        for station in stationsOwnedByCorp:
            stationsOwnedByCorpBySolarSystemID[station.solarSystemID].append(station.stationID)

        hardcoded_stations = get_hardcoded_lp_stations_for_corp(corpID)
        for stationID in hardcoded_stations:
            stationsOwnedByCorpBySolarSystemID[cfg.evelocations.Get(stationID).solarSystemID].append(stationID)

        fwFactionID = GetFwFactionIDForNpcCorp(corpID)
        if IsPirateFWFaction(fwFactionID):
            structureID, solarSystemID = sm.GetService('insurgencyCampaignSvc').GetActiveFobStructureIdAndSystemIdForFaction(fwFactionID)
            if structureID and solarSystemID:
                stationsOwnedByCorpBySolarSystemID[solarSystemID].append(structureID)
        nearestDockableLocation = None
        jumpsToNearestStation = sys.maxint
        for solarSystemID, stationIDs in stationsOwnedByCorpBySolarSystemID.iteritems():
            for dockableLocationID in stationIDs:
                blue.pyos.BeNice()
                if session.stationid == dockableLocationID:
                    return dockableLocationID
                if session.structureid == dockableLocationID:
                    return dockableLocationID
                dist = self.clientPathfinderService.GetJumpCount(session.solarsystemid2, solarSystemID)
                if dist <= jumpsToNearestStation:
                    jumpsToNearestStation = dist
                    nearestDockableLocation = dockableLocationID

        return nearestDockableLocation

    def _on_corp_spending_killswitch_changed(self, ld_client, feature_key, fallback, _flagDeleted):
        current_value = self._corp_spending_killswitch
        self._corp_spending_killswitch = ld_client.get_bool_variation(feature_key=feature_key, fallback=fallback)
        if self._corp_spending_killswitch != current_value:
            on_corp_lp_purchases_killswitch_changed(self._corp_spending_killswitch)
