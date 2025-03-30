#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderESS.py
import appConst
import telemetry
import blue
from gametime import GetWallclockTime, SEC
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters, agencySignals
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.essSystemContentPiece import ESSSystemContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider
RESERVE_BANK_UNLOCKED_KEY = 'vaultOpen'
MAIN_BANK_AMOUNT_KEY = 'mainValue'
RESERVE_BANK_AMOUNT_KEY = 'reserveValue'
ESS_BOUNTY_OUTPUT_KEY = 'currentOutput'
MIN_REFRESH_INTERVAL_SECONDS = 30

class ContentProviderESS(BaseContentProvider):
    contentType = agencyConst.CONTENTTYPE_ESS
    contentGroup = contentGroupConst.contentGroupESSSystems

    def __init__(self):
        super(ContentProviderESS, self).__init__()
        agencySignals.on_content_group_selected.connect(self.Refresh)
        self.lastRefresh = GetWallclockTime()

    def Refresh(self, contentID, *args, **kwargs):
        if contentID == contentGroupConst.contentGroupESSSystems:
            if (GetWallclockTime() - self.lastRefresh) / SEC > MIN_REFRESH_INTERVAL_SECONDS:
                self.lastRefresh = GetWallclockTime()
                self.InvalidateContentPieces()

    @telemetry.ZONE_METHOD
    def _ConstructContentPieces(self):
        essDataBySolarSystemID = self._GetSolarSystemsWithESS()
        essDataBySolarSystemID = {solarSystemID:essData for solarSystemID, essData in essDataBySolarSystemID.iteritems() if self.CheckSystemCriteria(solarSystemID, essData)}
        for solarSystemID, essData in essDataBySolarSystemID.iteritems():
            contentPiece = self.ConstructSystemContentPiece(solarSystemID=solarSystemID, bountiesOutput=essData[ESS_BOUNTY_OUTPUT_KEY], mainBankAmount=essData[MAIN_BANK_AMOUNT_KEY], reserveBankAmount=essData[RESERVE_BANK_AMOUNT_KEY], reserveBankUnlocked=essData[RESERVE_BANK_UNLOCKED_KEY])
            self.AppendContentPiece(contentPiece)
            blue.pyos.BeNice()
            if self.contentPieces and len(self.contentPieces) >= 32:
                break

    def _GetSolarSystemsWithESS(self):
        return sm.RemoteSvc('dynamicResourceCacheMgr').GetESSAgencyData()

    @telemetry.ZONE_METHOD
    def ConstructSystemContentPiece(self, solarSystemID, bountiesOutput, mainBankAmount, reserveBankAmount, reserveBankUnlocked):
        return ESSSystemContentPiece(solarSystemID=solarSystemID, typeID=appConst.typeSolarSystem, itemID=solarSystemID, bountiesOutput=bountiesOutput, mainBankAmount=mainBankAmount, reserveBankAmount=reserveBankAmount, reserveBankUnlocked=reserveBankUnlocked)

    @telemetry.ZONE_METHOD
    def CheckSystemCriteria(self, solarSystemID, essData):
        return self.CheckDistanceCriteria(solarSystemID) and self.CheckBountiesOutputCriteria(essData) and self.CheckMainBankAmountCriteria(essData) and self.CheckReserveBankUnlockedCriteria(essData) and self.CheckReserveBankAmountCriteria(essData)

    def CheckBountiesOutputCriteria(self, essData):
        if not self._IsBountiesOutputFilterActive():
            return True
        minBountiesOutput = self._GetFilterValue(agencyConst.FILTERTYPE_ESSMINBOUNTY)
        maxBountiesOutput = self._GetFilterValue(agencyConst.FILTERTYPE_ESSMAXBOUNTY)
        systemBountyOutput = essData[ESS_BOUNTY_OUTPUT_KEY] * 100.0
        return int(minBountiesOutput) <= systemBountyOutput <= int(maxBountiesOutput)

    def CheckMainBankAmountCriteria(self, essData):
        if not self._IsMainBankAmountFilterActive():
            return True
        minMainBankAmount = self._GetFilterValue(agencyConst.FILTERTYPE_ESSMINMAINBANKAMOUNT)
        actualBankAmount = essData[MAIN_BANK_AMOUNT_KEY]
        return actualBankAmount >= minMainBankAmount

    def CheckReserveBankUnlockedCriteria(self, essData):
        if not self._IsReserveBankUnlockedFilterActive():
            return True
        reserveBankUnlocked = essData[RESERVE_BANK_UNLOCKED_KEY]
        return reserveBankUnlocked

    def CheckReserveBankAmountCriteria(self, essData):
        if not self._IsReserveBankAmountFilterActive():
            return True
        minReserveBankAmount = self._GetFilterValue(agencyConst.FILTERTYPE_ESSMINRESERVEBANKAMOUNT)
        actualBankAmount = essData[RESERVE_BANK_AMOUNT_KEY]
        return actualBankAmount >= minReserveBankAmount

    def _IsMainBankAmountFilterActive(self):
        return self._GetFilterValue(agencyConst.FILTERTYPE_ESSMINMAINBANKAMOUNTFILTERENABLED)

    def _IsReserveBankAmountFilterActive(self):
        return self._GetFilterValue(agencyConst.FILTERTYPE_ESSMINRESERVEBANKAMOUNTFILTERENABLED)

    def _IsBountiesOutputFilterActive(self):
        return self._GetFilterValue(agencyConst.FILTERTYPE_ESSBOUNTYFILTERENABLED)

    def _IsReserveBankUnlockedFilterActive(self):
        return self._GetFilterValue(agencyConst.FILTERTYPE_ESSRESERVEBANKUNLOCKED)

    def _GetFilterValue(self, filterType):
        return agencyFilters.GetFilterValue(self.contentGroup, filterType)
