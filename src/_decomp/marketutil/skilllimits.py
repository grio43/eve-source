#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\marketutil\skilllimits.py
import inventorycommon.const as invconst
from itertoolsext import Bundle
from .const import rangeStation, rangeSolarSystem, rangeRegion, ACCOUNTING_SKILL_MODIFIER, BROKER_RELATIONS_SKILL_MODIFIER, PIRATE_ALIGNMENT_ZARZAKH_MODIFIER, SYSTEMS_WITH_FACTION_DISCOUNT
JUMPS_PER_SKILL_LEVEL = {0: rangeStation,
 1: rangeSolarSystem,
 2: 5,
 3: 10,
 4: 20,
 5: rangeRegion}

class SkillLimits(dict):

    def __init__(self, skillLevels, GetDynamicBaseTax, doSkillsApply):
        super(SkillLimits, self).__init__()
        self.GetDynamicBaseTax = GetDynamicBaseTax
        self.skillLevels = skillLevels
        self.doSkillsApply = doSkillsApply

    def GetBrokersFeeForLocation(self, locationID):
        baseTax = self.GetDynamicBaseTax(locationID)
        if baseTax is None:
            return
        transactionTax = baseTax / 100.0
        if self.doSkillsApply:
            transactionTax -= self.skillLevels.broker * BROKER_RELATIONS_SKILL_MODIFIER / 100
        return transactionTax

    def GetModificationFeeDiscount(self):
        return 0.5 + 0.06 * self.skillLevels.margin


def GetMarketSkills(skillLevelsDict):
    skillLevels = Bundle(retail=skillLevelsDict.get(invconst.typeRetail, 0), trade=skillLevelsDict.get(invconst.typeTrade, 0), wholeSale=skillLevelsDict.get(invconst.typeWholesale, 0), accounting=skillLevelsDict.get(invconst.typeAccounting, 0), broker=skillLevelsDict.get(invconst.typeBrokerRelations, 0), tycoon=skillLevelsDict.get(invconst.typeTycoon, 0), marketing=skillLevelsDict.get(invconst.typeMarketing, 0), procurement=skillLevelsDict.get(invconst.typeProcurement, 0), visibility=skillLevelsDict.get(invconst.typeVisibility, 0), daytrading=skillLevelsDict.get(invconst.typeDaytrading, 0), margin=skillLevelsDict.get(invconst.typeMarginTrading, 0))
    return skillLevels


def GetSkillLimits(GetMarketSkills_, GetDynamicBaseTax, doSkillsApply, taxRate, factionID, solarSystemID):
    typeIDs = [invconst.typeRetail,
     invconst.typeTrade,
     invconst.typeWholesale,
     invconst.typeAccounting,
     invconst.typeBrokerRelations,
     invconst.typeTycoon,
     invconst.typeMarketing,
     invconst.typeProcurement,
     invconst.typeVisibility,
     invconst.typeDaytrading,
     invconst.typeMarginTrading]
    skillLevels = GetMarketSkills_(typeIDs)
    limits = SkillLimits(skillLevels, GetDynamicBaseTax, doSkillsApply)
    maxOrderCount = 5 + skillLevels.trade * 4 + skillLevels.retail * 8 + skillLevels.wholeSale * 16 + skillLevels.tycoon * 32
    limits['cnt'] = maxOrderCount
    transactionTax = taxRate / 100.0
    transactionTax *= 1 - skillLevels.accounting * ACCOUNTING_SKILL_MODIFIER
    transactionTax *= 1 - GetLocationDiscount(factionID, solarSystemID)
    limits['acc'] = transactionTax
    limits['ask'] = JUMPS_PER_SKILL_LEVEL[skillLevels.marketing]
    limits['bid'] = JUMPS_PER_SKILL_LEVEL[skillLevels.procurement]
    limits['vis'] = JUMPS_PER_SKILL_LEVEL[skillLevels.visibility]
    limits['mod'] = JUMPS_PER_SKILL_LEVEL[skillLevels.daytrading]
    return limits


def GetLocationDiscount(factionID, solarSystemID):
    from eve.common.script.util.facwarCommon import IsPirateFWFaction
    modifier = 0.0
    if solarSystemID in SYSTEMS_WITH_FACTION_DISCOUNT:
        if IsPirateFWFaction(factionID):
            modifier = PIRATE_ALIGNMENT_ZARZAKH_MODIFIER
    return modifier
