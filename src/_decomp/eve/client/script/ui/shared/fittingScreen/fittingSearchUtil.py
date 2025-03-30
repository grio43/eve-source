#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingSearchUtil.py
import itertools
from eve.client.script.ui.shared.fittingScreen.browsers.browserUtil import AUTO_FITTED_SERVICES_BY_STRUCTURE_TYPE
from eve.common.lib.appConst import GROUP_CAPITALSHIPS
import evetypes
from dynamicitemattributes import IsMutator
from shipfitting.fittingStuff import IsModuleTooBigForShip, GetSlotTypeForType, GetCanFitModuleTypeToShipType, IsRigSizeRestricted, IsCategoryOK_StructureVsShipRestrictions
MODULE_CATEGORIES = (const.marketCategoryShipEquipment,
 const.marketCategoryShipModifications,
 const.marketCategoryDrones,
 const.marketCategoryStructureEquipment,
 const.marketCategoryStructureModifications)
FAKE_FLAGID = -1
MAX_CPU_POWERGRID = 999999999999L

class SearchFittingHelper(object):
    __notifyevents__ = ['OnSkillsChanged']

    def __init__(self, cfg, *args):
        self.cfg = cfg
        self.dogmaStaticMgr = sm.GetService('clientDogmaIM').GetDogmaLocation().dogmaStaticMgr
        self.ResetAllVariables()
        sm.RegisterNotify(self)

    def ResetAllVariables(self):
        self.typeNames_lower = {}
        self.canFitModuleToShip = {}
        self.rigRestricted = {}
        self.tooBigModule = {}
        self.restrictedByDroneOrFighter = {}
        self.slotTypeByTypeID = {}
        self.shipRigSizeByTypeID = {}
        self.isCapitalShipByTypeID = {}
        self.marketCategoryByTypeID = {}
        self.numSlotsForModule = {}
        self.isHiSlot = {}
        self.isMedSlot = {}
        self.isLoSlot = {}
        self.isRigSlot = {}
        self.isSubSystemSlot = {}
        self.isServiceSlot = {}
        self.isDrone = {}
        self.isFighter = {}
        self.isDroneOrFighter = {}
        self.isDynamicType = {}
        self.missingSkills = {}
        self.cpuRequirementsByModuleTypeID = {}
        self.powergridRequirementsByModuleTypeID = {}
        self.calibrationRequirementByModuleTypeID = {}
        self.searchableTypeIDs = None
        self.searchableChargeTypeIDs = None
        self.isModule = {}
        self.isCharge = {}
        self.mutaplasmids = {}

    def GetTypeName(self, typeID):
        try:
            return self.typeNames_lower[typeID]
        except KeyError:
            t = evetypes.GetName(typeID)
            lower = t.lower()
            self.typeNames_lower[typeID] = lower
            return lower

    def ResetCpuAndPowergridDicts(self):
        self.cpuRequirementsByModuleTypeID = {}
        self.powergridRequirementsByModuleTypeID = {}

    def CanFitModuleToShipTypeOrGroup(self, shipTypeID, dogmaLocation, moduleTypeID):
        dictKey = (shipTypeID, moduleTypeID)
        try:
            return self.canFitModuleToShip[dictKey]
        except KeyError:
            canFit = GetCanFitModuleTypeToShipType(dogmaLocation, shipTypeID, moduleTypeID)
            if canFit:
                canFit = IsCategoryOK_StructureVsShipRestrictions(shipTypeID, moduleTypeID)
            self.canFitModuleToShip[dictKey] = canFit
            return canFit

    def IsMutaplasmid(self, typeID):
        try:
            return self.mutaplasmids[typeID]
        except KeyError:
            isMutaplasmid = IsMutator(typeID)
            self.mutaplasmids[typeID] = isMutaplasmid
            return isMutaplasmid

    def IsDynamicType(self, typeID):
        try:
            return self.isDynamicType[typeID]
        except KeyError:
            isDynamicType = evetypes.IsDynamicType(typeID)
            self.isDynamicType[typeID] = isDynamicType
            return isDynamicType

    def IsRigSizeRestricted(self, moduleTypeID, shipRigSize):
        dictKey = (moduleTypeID, shipRigSize)
        try:
            return self.rigRestricted[dictKey]
        except KeyError:
            isRestricted = IsRigSizeRestricted(self.dogmaStaticMgr, moduleTypeID, shipRigSize)
            self.rigRestricted[dictKey] = isRestricted
            return isRestricted

    def IsModuleTooBig(self, shipTypeID, moduleTypeID, isCapitalShip):
        dictKey = (shipTypeID, moduleTypeID)
        try:
            return self.tooBigModule[dictKey]
        except KeyError:
            tooBig = IsModuleTooBigForShip(moduleTypeID, shipTypeID, isCapitalShip)
            self.tooBigModule[dictKey] = tooBig
            return tooBig

    def RestrictedByDroneOrFighter(self, shipTypeID, typeID, isModularShip):
        dictKey = (shipTypeID, typeID)
        try:
            return self.restrictedByDroneOrFighter[dictKey]
        except KeyError:
            restricted = False
            if self.IsDroneOrFighter(typeID):
                isDrone = self.IsDrone(typeID)
                if isDrone:
                    droneBayCapacity = self.dogmaStaticMgr.GetTypeAttribute2(shipTypeID, const.attributeDroneCapacity)
                    if droneBayCapacity == 0 and not isModularShip:
                        restricted = True
                else:
                    fighterBayCapacity = self.dogmaStaticMgr.GetTypeAttribute2(shipTypeID, const.attributeFighterCapacity)
                    if fighterBayCapacity == 0:
                        restricted = True
                    elif not self._IsFighterAvailableForShipTypeID(shipTypeID, typeID):
                        restricted = True
            self.restrictedByDroneOrFighter[dictKey] = restricted
            return restricted

    def _IsFighterAvailableForShipTypeID(self, shipTypeID, fighterTypeID):
        fighterAttributes = [(const.attributeFighterSquadronIsHeavy, const.attributeFighterHeavySlots),
         (const.attributeFighterSquadronIsSupport, const.attributeFighterSupportSlots),
         (const.attributeFighterSquadronIsLight, const.attributeFighterLightSlots),
         (const.attributeFighterSquadronIsStandupHeavy, const.attributeFighterStandupHeavySlots),
         (const.attributeFighterSquadronIsStandupSupport, const.attributeFighterStandupSupportSlots),
         (const.attributeFighterSquadronIsStandupLight, const.attributeFighterStandupLightSlots)]
        for squadronAttributeID, slotAttributeID in fighterAttributes:
            if self.dogmaStaticMgr.GetTypeAttribute2(fighterTypeID, squadronAttributeID):
                if self.dogmaStaticMgr.GetTypeAttribute2(shipTypeID, slotAttributeID):
                    return True

        return False

    def GetNumSlotForModuleForModularShip(self, dogmaLocation, shipID, moduleTypeD, numTurretsFitted, numLaunchersFitted):
        attribute = self._GetAttributeForNumSlotsCheck(moduleTypeD)
        if attribute is None:
            return
        attrValue = dogmaLocation.GetAttributeValue(shipID, attribute)
        if attribute == const.attributeTurretSlotsLeft:
            return attrValue + numTurretsFitted
        if attribute == const.attributeLauncherSlotsLeft:
            return attrValue + numLaunchersFitted
        return attrValue

    def GetNumSlotForModule(self, shipTypeID, moduleTypeD):
        dictKey = (shipTypeID, moduleTypeD)
        try:
            return self.numSlotsForModule[dictKey]
        except KeyError:
            numSlots = self._GetNumForSlotModule(moduleTypeD, shipTypeID)
            self.numSlotsForModule[dictKey] = numSlots
            return numSlots

    def _GetNumForSlotModule(self, moduleTypeD, shipTypeID):
        attribute = self._GetAttributeForNumSlotsCheck(moduleTypeD)
        if attribute is None:
            return
        return self.dogmaStaticMgr.GetTypeAttribute(shipTypeID, attribute)

    def _GetAttributeForNumSlotsCheck(self, moduleTypeD):
        if self.IsHislotModule(moduleTypeD):
            typeEffects = self.dogmaStaticMgr.TypeGetEffects(moduleTypeD)
            if const.effectTurretFitted in typeEffects:
                attribute = const.attributeTurretSlotsLeft
            elif const.effectLauncherFitted in typeEffects:
                attribute = const.attributeLauncherSlotsLeft
            else:
                attribute = const.attributeHiSlots
        elif self.IsMedslotModule(moduleTypeD):
            attribute = const.attributeMedSlots
        elif self.IsLoSlot(moduleTypeD):
            attribute = const.attributeLowSlots
        elif self.IsRigSlot(moduleTypeD):
            attribute = const.attributeRigSlots
        elif self.IsServiceSlot(moduleTypeD):
            attribute = const.attributeServiceSlots
        else:
            return None
        return attribute

    def IsHislotModule(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectHiPower, self.isHiSlot)

    def IsMedslotModule(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectMedPower, self.isMedSlot)

    def IsLoSlot(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectLoPower, self.isLoSlot)

    def IsRigSlot(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectRigSlot, self.isRigSlot)

    def IsSubSystemSlot(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectSubSystem, self.isSubSystemSlot)

    def IsServiceSlot(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectServiceSlot, self.isServiceSlot)

    def IsDroneOrFighter(self, typeID):
        try:
            return self.isDroneOrFighter[typeID]
        except KeyError:
            isDroneOrFighter = self.IsDrone(typeID) or self.IsFighter(typeID)
            self.isDroneOrFighter[typeID] = isDroneOrFighter
            return isDroneOrFighter

    def IsDrone(self, typeID):
        try:
            return self.isDrone[typeID]
        except KeyError:
            categoryID = evetypes.GetCategoryID(typeID)
            isDrone = categoryID == const.categoryDrone
            self.isDrone[typeID] = isDrone
            return isDrone

    def IsFighter(self, typeID):
        try:
            return self.isFighter[typeID]
        except KeyError:
            categoryID = evetypes.GetCategoryID(typeID)
            isFighter = categoryID == const.categoryFighter
            self.isFighter[typeID] = isFighter
            return isFighter

    def IsModule(self, typeID):
        try:
            return self.isModule[typeID]
        except KeyError:
            isModule = evetypes.GetCategoryID(typeID) in (const.categoryModule, const.categoryStructureModule)
            self.isModule[typeID] = isModule
            return isModule

    def IsCharge(self, typeID):
        try:
            return self.isCharge[typeID]
        except KeyError:
            isCharge = evetypes.GetCategoryID(typeID) == const.categoryCharge
            self.isCharge[typeID] = isCharge
            return isCharge

    def IsSpecificSlotType(self, moduleTypeID, slotTypeWanted, cacheDict):
        try:
            return cacheDict[moduleTypeID]
        except KeyError:
            slotType = self.GetSlotTypeForModuleType(moduleTypeID)
            if slotType == slotTypeWanted:
                isRightType = True
            else:
                isRightType = False
            cacheDict[moduleTypeID] = isRightType
            return isRightType

    def GetSlotTypeForModuleType(self, moduleTypeID):
        try:
            return self.slotTypeByTypeID[moduleTypeID]
        except KeyError:
            slotType = GetSlotTypeForType(moduleTypeID)
            self.slotTypeByTypeID[moduleTypeID] = slotType
            return slotType

    def GetShipRigSize(self, shipTypeID):
        try:
            return self.shipRigSizeByTypeID[shipTypeID]
        except KeyError:
            rigSize = self.dogmaStaticMgr.GetTypeAttribute2(shipTypeID, const.attributeRigSize)
            self.shipRigSizeByTypeID[shipTypeID] = rigSize
            return rigSize

    def IsCapitalSize(self, groupID):
        try:
            return self.isCapitalShipByTypeID[groupID]
        except KeyError:
            isCapitalSize = groupID in self.cfg.GetShipGroupByClassType()[GROUP_CAPITALSHIPS]
            self.isCapitalShipByTypeID[groupID] = isCapitalSize
            return isCapitalSize

    def GetCalibrationForModuleType(self, moduleTypeID):
        try:
            return self.calibrationRequirementByModuleTypeID[moduleTypeID]
        except KeyError:
            calibrationValue = self.dogmaStaticMgr.GetTypeAttribute2(moduleTypeID, const.attributeUpgradeCost)
            self.calibrationRequirementByModuleTypeID[moduleTypeID] = calibrationValue
            return calibrationValue

    def GetCPUForModuleType(self, ghostFittingSvc, shipID, moduleTypeID, shipTypeID, resourceRigsFitted):
        dictKey = (shipTypeID, resourceRigsFitted, moduleTypeID)
        try:
            return self.cpuRequirementsByModuleTypeID[dictKey]
        except KeyError:
            cpuValue = self.dogmaStaticMgr.GetTypeAttribute2(moduleTypeID, const.attributeCpu)
            if cpuValue != 0:
                cpuValue, powerValue = self.GetCpuAndPower(ghostFittingSvc, shipID, moduleTypeID, dictKey)
            else:
                self.cpuRequirementsByModuleTypeID[dictKey] = cpuValue
            return cpuValue

    def GetPowergridForModuleType(self, ghostFittingSvc, shipID, moduleTypeID, shipTypeID, resourceRigsFitted):
        dictKey = (shipTypeID, resourceRigsFitted, moduleTypeID)
        try:
            return self.powergridRequirementsByModuleTypeID[dictKey]
        except KeyError:
            powerValue = self.dogmaStaticMgr.GetTypeAttribute2(moduleTypeID, const.attributePower)
            if powerValue != 0:
                cpuValue, powerValue = self.GetCpuAndPower(ghostFittingSvc, shipID, moduleTypeID, dictKey)
            else:
                self.powergridRequirementsByModuleTypeID[dictKey] = powerValue
            return powerValue

    def GetSearcableTypeIDs(self, marketGroups):
        if not self.searchableTypeIDs:
            myGroups = []
            for x in MODULE_CATEGORIES:
                myGroups += marketGroups[x]

            typeIDs = {i for i in itertools.chain.from_iterable([ x.types for x in myGroups ])}
            typeIDs.update(self._GetSpecialAssetModules(marketGroups))
            typeIDs.update(AUTO_FITTED_SERVICES_BY_STRUCTURE_TYPE.values())
            self.searchableTypeIDs = typeIDs
        return self.searchableTypeIDs

    def _GetSpecialAssetModules(self, marketGroups):
        myGroups = marketGroups[const.marketCategorySpecialEditionAssets]
        typeIDs = {i for i in itertools.chain.from_iterable([ x.types for x in myGroups ]) if self.IsModule(i)}
        return typeIDs

    def GetSearcableChargeTypeIDs(self, marketGroups):
        if not self.searchableChargeTypeIDs:
            myGroups = marketGroups[const.marketCategoryAmmunitionAndCharges]
            typeIDs = {i for i in itertools.chain.from_iterable([ x.types for x in myGroups ])}
            typeIDs.update(self._GetSpecialAssetCharges(marketGroups))
            self.searchableChargeTypeIDs = typeIDs
        return self.searchableChargeTypeIDs

    def _GetSpecialAssetCharges(self, marketGroups):
        myGroups = marketGroups[const.marketCategorySpecialEditionAssets]
        typeIDs = {i for i in itertools.chain.from_iterable([ x.types for x in myGroups ]) if self.IsCharge(i)}
        return typeIDs

    def GetMarketCategoryForType(self, typeID, allMarketGroups):
        try:
            return self.marketCategoryByTypeID[typeID]
        except KeyError:
            for mg in allMarketGroups:
                if typeID in mg.types:
                    topMarketCategory = mg
                    break
            else:
                topMarketCategory = None

            self.marketCategoryByTypeID[typeID] = topMarketCategory
            return topMarketCategory

    def GetCpuAndPower(self, ghostFittingSvc, shipID, moduleTypeID, dictKey):
        info = ghostFittingSvc.LoadFakeItem(shipID, moduleTypeID)
        if info is None:
            cpuValue = powerValue = MAX_CPU_POWERGRID
        else:
            cpuValue = info.cpuValue
            powerValue = info.powerValue
        self.cpuRequirementsByModuleTypeID[dictKey] = cpuValue
        self.powergridRequirementsByModuleTypeID[dictKey] = powerValue
        return (cpuValue, powerValue)

    def GetMissingSkills(self, typeID, dogmaLocation, skillSvc):
        try:
            return self.missingSkills[typeID]
        except KeyError:
            missingSkillsForType = dogmaLocation.GetMissingSkills(typeID, skillSvc)
            self.missingSkills[typeID] = missingSkillsForType
            return missingSkillsForType

    def OnSkillsChanged(self, skillInfos):
        toRemove = []
        for changedSkillTypeID, skillInfo in skillInfos.iteritems():
            newSkillLevel = skillInfo.effectiveSkillLevel
            for eachTypeID, missingSkillInfo in self.missingSkills.iteritems():
                missingLevel = missingSkillInfo.get(changedSkillTypeID, None)
                if missingLevel is not None and missingLevel <= newSkillLevel:
                    toRemove.append((eachTypeID, changedSkillTypeID))

        for typeID, skillTypeID in toRemove:
            self.missingSkills[typeID].pop(skillTypeID)

        if toRemove:
            sm.ScatterEvent('OnSkillFilteringUpdated')

    def BuildNameDict(self):
        marketGroups = sm.GetService('marketutils').GetMarketGroups()
        typeIDs = set(self.GetSearcableTypeIDs(marketGroups))
        typeIDs.update(self.GetSearcableChargeTypeIDs(marketGroups))
        for typeID in typeIDs:
            text = evetypes.GetName(typeID).lower()
            self.typeNames_lower[typeID] = text

    def GetFittedLauncherAndTurrets(self, dogmaLocation, shipItem):
        currentModuleList = shipItem.GetFittedItems().values()
        numTurrets = 0
        numLaunchers = 0
        for module in currentModuleList:
            if module.flagID not in const.hiSlotFlags:
                continue
            if dogmaLocation.dogmaStaticMgr.TypeHasEffect(module.typeID, const.effectTurretFitted):
                numTurrets += 1
            elif dogmaLocation.dogmaStaticMgr.TypeHasEffect(module.typeID, const.effectLauncherFitted):
                numLaunchers += 1

        return (numTurrets, numLaunchers)
