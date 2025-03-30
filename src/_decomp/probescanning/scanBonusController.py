#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\scanBonusController.py
import operator
import dogma.data as dogma_data
from dogma.items.moduleDogmaItem import ModuleDogmaItem
from dogma.items.shipDogmaItem import ShipDogmaItem
from logmodule import LogException
from probescanning.const import SCAN_STRENGTH_ATTRIBUTE_ID, SCAN_DEVIATION_ATTRIBUTE_ID, SCAN_DURATION_ATTRIBUTE_ID, SCAN_STRENGTH_BONUS_ATTRIBUTE_IDS, SCAN_DEVIATION_BONUS_ATTRIBUTE_IDS, SCAN_DURATION_ALTERNATE_ATTRIBUTE_IDS, SCANNING_IMPLANTS_TYPE_IDS, attributeImplantSetSister, SCANNING_SUBSYSTEM_TYPE_IDS, SCANNING_SKILLS_TYPE_IDS

class ScanBonusController:

    def __init__(self):
        self.skillSvc = sm.GetService('skills')
        self.scanSvc = sm.GetService('scanSvc')
        self.godma = sm.GetService('godma')
        self.dogmaLoc = sm.GetService('clientDogmaIM').GetDogmaLocation()
        self.fittedModules = None

    def GetAttribute(self, attributeID, categoryID = None, groupID = None):
        self.UpdateFittedItems()
        if not self.fittedModules:
            return None
        for itemID, item in self.fittedModules.iteritems():
            if item.categoryID == categoryID or item.groupID == groupID:
                if not self.TypeHasAttribute(item.typeID, attributeID):
                    continue
                return item.attributes[attributeID]

    def TypeHasAttribute(self, typeID, attributeID):
        for each in dogma_data.get_type_attributes(typeID):
            if each.attributeID == attributeID:
                return True

        return False

    def GetScanStrengthAttribute(self):
        return self.GetAttribute(SCAN_STRENGTH_ATTRIBUTE_ID, categoryID=const.categoryCharge)

    def GetScanDeviationAttribute(self):
        return self.GetAttribute(SCAN_DEVIATION_ATTRIBUTE_ID, categoryID=const.categoryCharge)

    def GetScanDurationAttribute(self):
        return self.GetAttribute(SCAN_DURATION_ATTRIBUTE_ID, groupID=const.groupScanProbeLauncher)

    def GetBaseScanStrength(self):
        return self.godma.GetTypeAttribute2(self.scanSvc.GetActiveProbeTypeID(), SCAN_STRENGTH_ATTRIBUTE_ID)

    def GetBaseScanDeviation(self):
        return self.godma.GetTypeAttribute2(self.scanSvc.GetActiveProbeTypeID(), SCAN_DEVIATION_ATTRIBUTE_ID)

    def GetBaseScanDuration(self):
        return self.godma.GetTypeAttribute2(self.scanSvc.GetProbeLauncher().typeID, SCAN_DURATION_ATTRIBUTE_ID)

    def GetTotalScanStrength(self):
        launchedProbesData = self.scanSvc.GetProbeData()
        if not launchedProbesData:
            strengthAttribute = self.GetScanStrengthAttribute()
            if not strengthAttribute:
                return 0
            return strengthAttribute.GetValue()
        typeID = launchedProbesData.iteritems().next()[1].typeID
        return self.godma.GetTypeAttribute2(typeID, SCAN_STRENGTH_ATTRIBUTE_ID) * self.ConvertToFraction(self.GetTotalScanStrengthBonus())

    def GetTotalScanDeviation(self):
        launchedProbesData = self.scanSvc.GetProbeData()
        if not launchedProbesData:
            deviationAttribute = self.GetScanDeviationAttribute()
            if not deviationAttribute:
                return 0
            return deviationAttribute.GetValue()
        typeID = launchedProbesData.iteritems().next()[1].typeID
        return self.godma.GetTypeAttribute2(typeID, SCAN_DEVIATION_ATTRIBUTE_ID) * abs(self.ConvertToFraction(self.GetTotalScanDeviationBonus()))

    def GetTotalScanDuration(self):
        durationAttribute = self.GetScanDurationAttribute()
        if durationAttribute is None:
            return 0
        return durationAttribute.GetValue()

    def GetTotalScanStrengthBonus(self):
        modulesFactor = self.ConvertToFraction(self.GetScanStrengthBonusFromModules())
        shipFactor = self.ConvertToFraction(self.GetScanStrengthBonusFromShip())
        implantFactor = self.ConvertToFraction(self.GetScanStrengthBonusFromImplants())
        skillsFactor = self.ConvertToFraction(self.GetScanStrengthBonusFromSkills())
        return self.ConvertToDecimal(modulesFactor * shipFactor * implantFactor * skillsFactor)

    def GetTotalScanDeviationBonus(self):
        modulesFactor = self.ConvertToFraction(self.GetScanDeviationBonusFromModules())
        shipFactor = self.ConvertToFraction(self.GetScanDeviationBonusFromShip())
        implantFactor = self.ConvertToFraction(self.GetScanDeviationBonusFromImplants())
        skillsFactor = self.ConvertToFraction(self.GetScanDeviationBonusFromSkills())
        return self.ConvertToDecimal(modulesFactor * shipFactor * implantFactor * skillsFactor)

    def GetTotalScanDurationBonus(self):
        modulesFactor = self.ConvertToFraction(self.GetScanDurationBonusFromModules())
        shipFactor = self.ConvertToFraction(self.GetScanDurationBonusFromShip())
        implantFactor = self.ConvertToFraction(self.GetScanDurationBonusFromImplants())
        skillsFactor = self.ConvertToFraction(self.GetScanDurationBonusFromSkills())
        return self.ConvertToDecimal(modulesFactor * shipFactor * implantFactor * skillsFactor)

    def GetBonusFromLaunchedProbes(self, bonusID, originID):
        launchedProbesData = self.scanSvc.GetProbeData()
        if not launchedProbesData:
            return 0
        val = launchedProbesData.iteritems().next()[1].scanBonuses[bonusID][originID]
        if val:
            return val
        return 0

    def GetBonusFromModulesToNurfedAttribute(self, attribute):
        if attribute is None:
            return 0
        factor = attribute.GetNurfedModsFactor()
        return self.ConvertToDecimal(factor)

    def GetBonusFromModulesToAttribute(self, attribute):
        if attribute is None:
            return 0
        totalBonus = 0
        for id, modifier in attribute.GetIncomingModifiers():
            if isinstance(modifier.item, ModuleDogmaItem):
                totalBonus += modifier.GetValue()

        return totalBonus

    def GetScanStrengthBonusFromModules(self):
        fittedProbeAttribute = self.GetScanStrengthAttribute()
        if not fittedProbeAttribute:
            return self.GetBonusFromLaunchedProbes('strength', 'modules')
        return self.GetBonusFromModulesToNurfedAttribute(self.GetScanStrengthAttribute())

    def GetScanDeviationBonusFromModules(self):
        fittedProbeAttribute = self.GetScanDeviationAttribute()
        if not fittedProbeAttribute:
            return self.GetBonusFromLaunchedProbes('deviation', 'modules')
        return self.GetBonusFromModulesToNurfedAttribute(fittedProbeAttribute)

    def GetScanDurationBonusFromModules(self):
        return self.GetBonusFromModulesToAttribute(self.GetScanDurationAttribute())

    def GetBonusFromSkillsByAttributes(self, attributeIDs):
        bonuses = []
        for skillID in SCANNING_SKILLS_TYPE_IDS:
            totalBonus = 0
            skillLevel = self.skillSvc.GetEffectiveLevel(skillID) or 0
            for bonusID in attributeIDs:
                percentagePerLevel = self.godma.GetTypeAttribute2(skillID, bonusID)
                if percentagePerLevel:
                    totalBonus += skillLevel * percentagePerLevel
                    bonuses.append(self.ConvertToFraction(totalBonus))

        if bonuses:
            return self.ConvertToDecimal(reduce(operator.mul, bonuses))
        else:
            return 0

    def GetScanStrengthBonusFromSkills(self):
        return self.GetBonusFromSkillsByAttributes(SCAN_STRENGTH_BONUS_ATTRIBUTE_IDS)

    def GetScanDeviationBonusFromSkills(self):
        return self.GetBonusFromSkillsByAttributes(SCAN_DEVIATION_BONUS_ATTRIBUTE_IDS)

    def GetScanDurationBonusFromSkills(self):
        return self.GetBonusFromSkillsByAttributes(SCAN_DURATION_ALTERNATE_ATTRIBUTE_IDS)

    def GetBonusFromImplantsByAttributes(self, attributeIDs):
        implants = self.skillSvc.GetImplants()
        bonuses = []
        setBonuses = []
        for id, implant in implants.iteritems():
            if implant.typeID in SCANNING_IMPLANTS_TYPE_IDS:
                for bonusID in attributeIDs:
                    percentageBonus = self.godma.GetTypeAttribute2(implant.typeID, bonusID)
                    if percentageBonus:
                        bonuses.append(self.ConvertToFraction(percentageBonus))

            setBonus = self.godma.GetTypeAttribute2(implant.typeID, attributeImplantSetSister)
            if setBonus:
                setBonuses.append(setBonus)

        if bonuses:
            totalBonus = self.ConvertToDecimal(reduce(operator.mul, bonuses))
            if len(setBonuses) > 1:
                totalSetBonus = reduce(operator.mul, setBonuses)
                totalBonus *= totalSetBonus
            return totalBonus
        else:
            return 0

    def GetScanStrengthBonusFromImplants(self):
        return self.GetBonusFromImplantsByAttributes(SCAN_STRENGTH_BONUS_ATTRIBUTE_IDS)

    def GetScanDeviationBonusFromImplants(self):
        return self.GetBonusFromImplantsByAttributes(SCAN_DEVIATION_BONUS_ATTRIBUTE_IDS)

    def GetScanDurationBonusFromImplants(self):
        return self.GetBonusFromImplantsByAttributes(SCAN_DURATION_ALTERNATE_ATTRIBUTE_IDS)

    def GetBonusFromShip(self, attribute):
        shipBonus = self._GetBonusFromShip(attribute) / 100.0
        subsystemBonus = self.GetBonusFromSubsystems(attribute)
        return ((1.0 + shipBonus) * (1.0 + subsystemBonus) - 1.0) * 100.0

    def _GetBonusFromShip(self, attribute):
        if attribute is None:
            return 0
        try:
            for modifier in attribute.GetIncomingModifiers():
                if isinstance(modifier[1].item, ShipDogmaItem):
                    val = modifier[1].GetValue() or 0
                    if val:
                        return val
                    return 0

        except AttributeError:
            LogException('Getting Scan Bonus From Ship Failed')

        return 0

    def GetBonusFromSubsystems(self, attribute):
        if attribute.attribID != SCAN_STRENGTH_ATTRIBUTE_ID:
            return 0.0
        bonus = 1.0
        for typeID, attributeID in SCANNING_SUBSYSTEM_TYPE_IDS.iteritems():
            for module in self.fittedModules.values():
                if module.typeID == typeID:
                    attrValue = module.attributes[attributeID].GetValue()
                    bonus *= 1.0 + attrValue / 100.0

        return bonus - 1.0

    def GetScanStrengthBonusFromShip(self):
        fittedProbeAttribute = self.GetScanStrengthAttribute()
        if not fittedProbeAttribute:
            return self.GetBonusFromLaunchedProbes('strength', 'ship')
        return self.GetBonusFromShip(fittedProbeAttribute)

    def GetScanDeviationBonusFromShip(self):
        fittedProbeAttribute = self.GetScanDeviationAttribute()
        if not fittedProbeAttribute:
            return self.GetBonusFromLaunchedProbes('deviation', 'ship')
        return self.GetBonusFromShip(fittedProbeAttribute)

    def GetScanDurationBonusFromShip(self):
        return self.GetBonusFromShip(self.GetScanDurationAttribute())

    def ConvertToDecimal(self, fraction):
        if not fraction:
            return 0
        return (fraction - 1) * 100

    def ConvertToFraction(self, decimal):
        if not decimal:
            return 1
        return decimal / 100 + 1

    def UpdateFittedItems(self):
        ship = self.dogmaLoc.SafeGetDogmaItem(session.shipid)
        if ship:
            self.fittedModules = ship.GetFittedItems()
