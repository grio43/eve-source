#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\marketutil\brokerFee.py
import eve.common.lib.appConst as appConst
from eve.common.script.util import facwarCommon
from marketutil.const import MARKET_FACTION_STANDING_MULTIPLIER, MARKET_NPC_CORP_STANDING_MULTIPLIER
from utillib import KeyVal

class BrokerFeeProvider(object):

    def __init__(self, charWarfactionID, solarSystemID, factionToCharStanding, corpToCharStanding, sccSurchargeTax = 0.0):
        self.charWarfactionID = charWarfactionID
        self.solarSystemID = solarSystemID
        self.factionToCharStanding = factionToCharStanding
        self.corpToCharStanding = corpToCharStanding
        self.sccSurchargePercentage = sccSurchargeTax / 100.0

    def GetSccSurchargeInfo(self, oldAmount, newAmount, modificationFeeDiscount):
        if newAmount < 0.0:
            raise AttributeError('Amount must be positive')
        sccSurchargeFee = 0
        sccSurchargeModificationFee = 0
        if oldAmount is None:
            sccSurchargeFee = newAmount * self.sccSurchargePercentage
        else:
            sccSurchargeModificationFee = newAmount * self.sccSurchargePercentage * (1 - modificationFeeDiscount)
            if newAmount > oldAmount:
                sccSurchargeFee = (newAmount - oldAmount) * self.sccSurchargePercentage
        taxInfo = KeyVal()
        taxInfo.sccSurchargeAmt = sccSurchargeFee + sccSurchargeModificationFee
        taxInfo.rawSccSurchargePercentage = self.sccSurchargePercentage
        taxInfo.usingMinimumValue = False
        if self.sccSurchargePercentage:
            if taxInfo.sccSurchargeAmt <= appConst.mktMinimumSccSurcharge:
                taxInfo.sccSurchargeAmt = appConst.mktMinimumSccSurcharge
                taxInfo.usingMinimumValue = True
        return taxInfo

    def GetBrokerFeeInfo(self, oldAmount, newAmount, commissionPercentage, modificationFeeDiscount):
        if newAmount < 0.0:
            raise AttributeError('Amount must be positive')
        commissionPercentage = self.GetAdjustedCommissionPercentage(commissionPercentage)
        taxFee = 0
        modificationFee = 0
        if oldAmount is None:
            taxFee = newAmount * commissionPercentage
        else:
            modificationFee = newAmount * commissionPercentage * (1 - modificationFeeDiscount)
            if newAmount > oldAmount:
                taxFee = (newAmount - oldAmount) * commissionPercentage
        tax = KeyVal()
        tax.amt = taxFee + modificationFee
        tax.rawPercentage = commissionPercentage
        tax.usingMinimumValue = False
        if tax.amt <= appConst.mktMinimumFee:
            tax.amt = appConst.mktMinimumFee
            tax.usingMinimumValue = True
        return tax

    def GetAdjustedCommissionPercentage(self, commissionPercentage):
        commissionPercentage = facwarCommon.GetAdjustedFeePercentage(self.solarSystemID, self.charWarfactionID, commissionPercentage)
        commissionPercentage = self._GetStationOwnerAdjustedCommissionPercentage(commissionPercentage)
        return commissionPercentage

    def _GetStationOwnerAdjustedCommissionPercentage(self, commissionPercentage):
        commissionPercentage = commissionPercentage - self.factionToCharStanding * MARKET_FACTION_STANDING_MULTIPLIER - self.corpToCharStanding * MARKET_NPC_CORP_STANDING_MULTIPLIER
        return commissionPercentage
