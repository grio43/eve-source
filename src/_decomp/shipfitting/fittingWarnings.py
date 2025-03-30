#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipfitting\fittingWarnings.py
from collections import defaultdict
from caching import Memoize
from carbon.common.lib.const import FLOAT_TOLERANCE
import evetypes
import dogma.data as dogma_data
from dogma.effects.modifiers import LocationRequiredSkillModifier
from eve.common.script.sys.idCheckers import IsStructure, IsShip
from inventorycommon.const import groupInterdictionNullifier, groupFreighter, groupPropulsionModule
from inventorycommon.util import IsModularShip, IsSubsystemFlagVisible
import shipfitting.fittingWarningConst as fittingWarningConst
from shipfitting.fittingWarningsCharges import FindModulesMissingCharges
from shipfitting.fittingWarningsStackingPenalty import FindModulesWithStackingPenalty
from dogma import const as dogmaConst
MASS_SPEEDBOOST_MAX_RATIO = 2.0
NON_PROP_MOD_GROUPS = [groupFreighter]

@Memoize
def _GetShieldTypesList():
    return evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_FITTING_WARNINGS_SHIELD)


@Memoize
def _GetArmorTypesList():
    return evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_FITTING_WARNINGS_ARMOR)


@Memoize
def _GetHullTypesList():
    return evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_FITTING_WARNINGS_HULL)


@Memoize
def _GetBuffingTypesList():
    return evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_FITTING_WARNINGS_BUFFING)


def GetPolarizedWeapons(dogmaStaticMgr, fittedModules):
    polarized = []
    for typeID, flagID, qty in fittedModules:
        if dogmaStaticMgr.TypeHasEffect(typeID, const.effectResistanceKillerHullAll) or dogmaStaticMgr.TypeHasEffect(typeID, const.effectResistanceKillerShieldArmorAll):
            polarized.append((typeID, flagID))

    return polarized


def GetModulesByTankGroup(fittedModules):
    armorModules = []
    shieldModules = []
    hullModules = []
    for typeID, flagID, qty in fittedModules:
        typeIDFlagIDTuple = (typeID, flagID)
        if typeID in _GetArmorTypesList():
            armorModules.append(typeIDFlagIDTuple)
        elif typeID in _GetShieldTypesList():
            shieldModules.append(typeIDFlagIDTuple)
        elif typeID in _GetHullTypesList():
            hullModules.append(typeIDFlagIDTuple)

    return (shieldModules, armorModules, hullModules)


def IsTankedForShieldAndArmor(fittedModules):
    shieldModules, armorModules, hullModules = GetModulesByTankGroup(fittedModules)
    if hullModules:
        return False
    if shieldModules and armorModules:
        return True
    return False


def GetNumTankedLayers(fittedModules):
    shieldModules, armorModules, hullModules = GetModulesByTankGroup(fittedModules)
    return bool(armorModules) + bool(shieldModules) + bool(hullModules)


def IsMultiTanking(fittedModules):
    return GetNumTankedLayers(fittedModules) > 1


def GetProblematicShipAndTankingCombo(shipTypeID, fittedModules):
    infoBubbleElementsForShip = cfg.infoBubbleTypeElements.get(shipTypeID, {})
    return GetProblematicCombo(fittedModules, infoBubbleElementsForShip)


def GetProblematicCombo(fittedModules, infoBubbleElementsForShip):
    problematicCombos = {}
    typeElementValues = set((y for x, y in infoBubbleElementsForShip.iteritems()))
    if fittingWarningConst.INFO_BUBBLE_SHIELD_OR_ARMOR in typeElementValues:
        return problematicCombos
    shieldModules, armorModules, hullModules = GetModulesByTankGroup(fittedModules)
    isShieldShip = fittingWarningConst.INFO_BUBBLE_SHIELD in typeElementValues
    isArmorShip = fittingWarningConst.INFO_BUBBLE_ARMOR in typeElementValues
    numTankingTypes = isShieldShip + isArmorShip
    if numTankingTypes == 1:
        if isShieldShip and armorModules:
            problematicCombos[fittingWarningConst.WARNING_ARMOR_TANKED_SHIELD_SHIP] = armorModules
        elif isArmorShip and shieldModules:
            problematicCombos[fittingWarningConst.WARNING_SHIELD_TANKED_ARMOR_SHIP] = shieldModules
    return problematicCombos


def FindModulesNotProvidingBonus(fittedModules, dronesAndFighters, mutaplasmidItemIDsByTypeID):
    missingSomethingToBonus = []
    allFittedGroups = {evetypes.GetGroupID(x) for x, _, _ in fittedModules}
    allFittedGroups.update({evetypes.GetGroupID(x) for x in dronesAndFighters})
    typeIDsToInvestigateFurther = set()
    for typeID, flagID, qty in fittedModules:
        groupID = evetypes.GetGroupID(typeID)
        affectedGroups = fittingWarningConst.GROUPS_AFFECTING_MODULE_GROUPS.get(groupID, None)
        if affectedGroups:
            if allFittedGroups.isdisjoint(affectedGroups):
                missingSomethingToBonus.append((typeID, flagID))
        else:
            if typeID not in _GetBuffingTypesList():
                continue
            typeIDsToInvestigateFurther.add(typeID)

    fittedTypeIDs = {typeID for typeID, flagID, qty in fittedModules}
    typesNotProvidingBonus = FindModulesNotProvidingBonusBasedOnSkillModifier(fittedTypeIDs, typeIDsToInvestigateFurther, mutaplasmidItemIDsByTypeID)
    for typeID, flagID, qty in fittedModules:
        if typeID in typesNotProvidingBonus:
            missingSomethingToBonus.append((typeID, flagID))

    return missingSomethingToBonus


def _GetSkillsAnModifiedAttributesForSkillModifier(buffingTypeID):
    effectsForType = dogma_data.get_type_effects(buffingTypeID)
    allSkillsAndAttributePairs = []
    for eachEffect in effectsForType:
        effectID = eachEffect.effectID
        skillsAndAttributePairs = _GetSkillsAndModifiedAttributesForEffect(effectID)
        allSkillsAndAttributePairs += skillsAndAttributePairs

    return allSkillsAndAttributePairs


def _GetSkillsAndModifiedAttributesForEffect(effectID):
    ec = sm.GetService('clientEffectCompiler')
    skillsAndAttributePairs = []
    try:
        expressions = ec.effects[effectID].effects
    except (KeyError, AttributeError) as e:
        return skillsAndAttributePairs

    for eachExpression in expressions:
        if isinstance(eachExpression, LocationRequiredSkillModifier) and eachExpression.IsShipModifier():
            skillTypeID = eachExpression.skillTypeID
            modifiedAttribute = eachExpression.modifiedAttributeID
            skillsAndAttributePairs += [(skillTypeID, modifiedAttribute)]

    return skillsAndAttributePairs


def FindModulesNotProvidingBonusBasedOnSkillModifier(fittedTypeIDs, typeIDsToInvestigateFurther, mutaplasmidItemIDsByTypeID):
    attributesOfInterest = set()
    skillsOfInterest = set()
    skillsAndAttributesNeededByTypeID = {}
    for eachPotentialBuffTypeID in typeIDsToInvestigateFurther:
        allSkillsAndAttributePairs = _GetSkillsAnModifiedAttributesForSkillModifier(eachPotentialBuffTypeID)
        if allSkillsAndAttributePairs:
            skillsOfInterest.update([ x[0] for x in allSkillsAndAttributePairs ])
            attributesOfInterest.update([ x[1] for x in allSkillsAndAttributePairs ])
            skillsAndAttributesNeededByTypeID[eachPotentialBuffTypeID] = allSkillsAndAttributePairs

    typeIDsBySkill = GetTypeIDsBySkill(fittedTypeIDs, skillsOfInterest)
    typeIDsByAttributeID = GetTypeIDsByAttributeIDs(fittedTypeIDs, attributesOfInterest, mutaplasmidItemIDsByTypeID)
    modulesThatAreProvidingBonus = set()
    for buffingTypeID, xSkillsAndAttributes in skillsAndAttributesNeededByTypeID.iteritems():
        for xSkillTypeID, xModifiedAttribute in xSkillsAndAttributes:
            typesWithSkill = typeIDsBySkill.get(xSkillTypeID, set())
            typesWithAttribute = typeIDsByAttributeID.get(xModifiedAttribute, set())
            typesWithBoth = typesWithSkill.intersection(typesWithAttribute)
            if typesWithBoth:
                modulesThatAreProvidingBonus.add(buffingTypeID)
                break

    infoSvc = sm.GetService('info')
    for buffingTypeID, xSkillsAndAttributes in skillsAndAttributesNeededByTypeID.iteritems():
        buffingTypeIDWasAdded = False
        if buffingTypeID in modulesThatAreProvidingBonus:
            continue
        for eachFittedTypeID in fittedTypeIDs:
            isLauncher = HasEffect(eachFittedTypeID, const.effectLauncherFitted)
            if not isLauncher:
                continue
            chargeTypeIDs = infoSvc.GetUsedWithTypeIDs(eachFittedTypeID)
            if not chargeTypeIDs:
                continue
            chargesBySkill = GetTypeIDsBySkill(chargeTypeIDs, skillsOfInterest)
            chargesByAttributeID = GetTypeIDsByAttributeIDs(chargeTypeIDs, attributesOfInterest, mutaplasmidItemIDsByTypeID)
            for xSkillTypeID, xModifiedAttribute in xSkillsAndAttributes:
                chargesWithSkill = chargesBySkill.get(xSkillTypeID, set())
                chargesWithAttribute = chargesByAttributeID.get(xModifiedAttribute, set())
                chargesWithBoth = chargesWithSkill.intersection(chargesWithAttribute)
                if chargesWithBoth:
                    modulesThatAreProvidingBonus.add(buffingTypeID)
                    buffingTypeIDWasAdded = True
                    break

            if buffingTypeIDWasAdded:
                break

    modulesTypesNotProvidingBonus = set(skillsAndAttributesNeededByTypeID.keys()) - modulesThatAreProvidingBonus
    return modulesTypesNotProvidingBonus


def GetTypeIDsBySkill(fittedTypeIDs, skillsOfInterest):
    allAllTypeIDsBySkillType = defaultdict(set)
    for eachFittedTypeID in fittedTypeIDs:
        skillReq = _GetSkillReqTypeIDs(eachFittedTypeID)
        for eachSkillTypeID in skillReq:
            if eachSkillTypeID in skillsOfInterest:
                allAllTypeIDsBySkillType[eachSkillTypeID].add(eachFittedTypeID)

    return allAllTypeIDsBySkillType


def GetTypeIDsByAttributeIDs(fittedTypeIDs, attributesOfInterest, mutaplasmidItemIDsByTypeID):
    allAllTypeIDsByAttributeID = defaultdict(set)
    for eachFittedTypeID in fittedTypeIDs:
        typeAttributeIDs = set(dogma_data.get_type_attributes_by_id(eachFittedTypeID))
        mutaplasmidAttributeIDs = GetMutaplasmidAttributeIDs(mutaplasmidItemIDsByTypeID.get(eachFittedTypeID, []))
        typeAttributeIDs.update(mutaplasmidAttributeIDs)
        for eachAttributeID in typeAttributeIDs:
            if eachAttributeID in attributesOfInterest:
                allAllTypeIDsByAttributeID[eachAttributeID].add(eachFittedTypeID)

    return allAllTypeIDsByAttributeID


def GetMutaplasmidAttributeIDs(itemIDs):
    attributeIDs = set()
    if not itemIDs:
        return attributeIDs
    dynamicItemSvc = sm.GetService('dynamicItemSvc')
    for eachItemID in itemIDs:
        try:
            attributeDictForItem = dynamicItemSvc.GetDynamicItemAttributes(eachItemID)
        except StandardError:
            continue

        attributeIDs.update(attributeDictForItem)

    return attributeIDs


def _GetSkillReqTypeIDs(typeID):
    return sm.GetService('skills').GetRequiredSkillsRecursive(typeID).keys()


def IsOverOnCPU(fittingController):
    cpuLoadInfo = fittingController.GetCPULoad()
    cpuOutputInfo = fittingController.GetCPUOutput()
    cpuDiff = cpuOutputInfo.value - cpuLoadInfo.value
    return _IsOverloaded(cpuDiff)


def IsOverOnPowergrid(fittingController):
    powerLoadInfo = fittingController.GetPowerLoad()
    powerOutputInfo = fittingController.GetPowerOutput()
    powerDiff = powerOutputInfo.value - powerLoadInfo.value
    return _IsOverloaded(powerDiff)


def IsOverOnCalibration(fittingController):
    calibrationLoadInfo = fittingController.GetCalibrationLoad()
    calibrationOutputInfo = fittingController.GetCalibrationOutput()
    calibrationDiff = calibrationOutputInfo.value - calibrationLoadInfo.value
    return _IsOverloaded(calibrationDiff)


def IsCargoOverloaded(fittingController):
    shipID = fittingController.GetItemID()
    typeID = fittingController.GetTypeID()
    if IsStructure(evetypes.GetCategoryID(typeID)):
        return False
    shipCapacityInfo = fittingController.dogmaLocation.GetCapacity(shipID, None, const.flagCargo)
    total = shipCapacityInfo.capacity
    used = shipCapacityInfo.used
    diff = total - used
    return _IsOverloaded(diff)


def _IsOverloaded(value):
    if value > -FLOAT_TOLERANCE:
        return False
    return True


def GetMixedTurrets(highSlotModules):
    turretsByGroups = _GetTurretsByGroups(highSlotModules)
    isMixing = len(turretsByGroups) > 1
    if isMixing:
        return turretsByGroups
    return {}


def _GetTurretsByGroups(highSlotModules):
    turretsByGroupID = defaultdict(list)
    for eachTypeID, eachFlagID in highSlotModules:
        groupID = _GetGroupIdForTurret(eachTypeID)
        if groupID in fittingWarningConst.TURRET_GROUPS:
            turretsByGroupID[groupID].append((eachTypeID, eachFlagID))

    return turretsByGroupID


def _GetGroupIdForTurret(eachTypeID):
    hardCodedGroupID = fittingWarningConst.HARD_CODED_GROUPIDS.get(eachTypeID, None)
    groupID = hardCodedGroupID or evetypes.GetGroupID(eachTypeID)
    return groupID


def GetMixedLauncherGroups(dogmaStaticMgr, highSlotModules):
    launcherByGroups = _GetLaunchersByGroups(dogmaStaticMgr, highSlotModules)
    isMixing = len(launcherByGroups) > 1
    if isMixing:
        return launcherByGroups
    return {}


def _GetLaunchersByGroups(dogmaStaticMgr, highSlotModules):
    launchers = [ (typeID, flagID) for typeID, flagID in highSlotModules if dogmaStaticMgr.TypeHasEffect(typeID, const.effectLauncherFitted) ]
    launchersByGroup = defaultdict(list)
    for eachTypeID, eachFlagID in launchers:
        groupID = evetypes.GetGroupID(eachTypeID)
        launchersByGroup[groupID].append((eachTypeID, eachFlagID))

    return launchersByGroup


def GetMixedTurretSizes(highSlotModules, mutaplasmidItemIDsByTypeID):
    turretsBySize = _GetTurretsBySizes(highSlotModules, mutaplasmidItemIDsByTypeID)
    if len(turretsBySize) > 1:
        return turretsBySize
    return {}


def _GetTurretsBySizes(highSlotModules, mutaplasmidItemIDsByTypeID):
    turrets = [ (typeID, flagID) for typeID, flagID in highSlotModules if evetypes.GetGroupID(typeID) in fittingWarningConst.TURRET_GROUPS ]
    turretsBySize = defaultdict(list)
    for typeID, flagID in turrets:
        sizeAttribute = dogma_data.get_type_attribute(typeID, const.attributeChargeSize)
        if sizeAttribute is None:
            for eachItemID in mutaplasmidItemIDsByTypeID.get(typeID, []):
                try:
                    sizeAttribute = sm.GetService('dynamicItemSvc').GetDynamicItemAttributes(eachItemID).get(const.attributeChargeSize, None)
                except StandardError:
                    continue

                if sizeAttribute:
                    break

        if sizeAttribute:
            turretsBySize[sizeAttribute] += [(typeID, flagID)]

    return turretsBySize


def FindMissingSubsystemFlags(shipTypeID, currentFit):
    if not IsModularShip(shipTypeID):
        return []
    missingFlags = []
    flagsWithSubsystems = {flagID for _, flagID, _ in currentFit if flagID in const.subsystemSlotFlags}
    for eachFlagID in const.subsystemSlotFlags:
        if eachFlagID not in flagsWithSubsystems:
            missingFlags.append(eachFlagID)

    return missingFlags


def FindModulesInNonExisitingSlots(fittingController, currentFit):
    modulesInNonExistingSlots = []
    shipID = fittingController.GetItemID()
    for typeID, flagID, _ in currentFit:
        if flagID not in const.fittingFlags:
            continue
        if IsSubsystemFlagVisible(flagID):
            if fittingController.HasStance() or not fittingController.HasSubsystems():
                modulesInNonExistingSlots.append((typeID, flagID))
        elif not fittingController.dogmaLocation.SlotExists(shipID, flagID):
            modulesInNonExistingSlots.append((typeID, flagID))

    return modulesInNonExistingSlots


def FindOfflineModules(fittingController):
    offlineModules = []
    inSimulation = sm.GetService('fittingSvc').IsShipSimulated()
    if inSimulation:
        return offlineModules
    dogmaLocation = fittingController.dogmaLocation
    shipItem = dogmaLocation.GetShipItem()
    if not shipItem:
        return offlineModules
    for moduleDogmaItem in shipItem.GetFittedItems().itervalues():
        if moduleDogmaItem.flagID in const.moduleSlotFlags and evetypes.GetCategoryID(moduleDogmaItem.typeID) in (const.categoryModule, const.categoryStructureModule):
            if not moduleDogmaItem.IsOnline():
                offlineModules.append((moduleDogmaItem.typeID, moduleDogmaItem.flagID))

    return offlineModules


def FindModulesWithMissingCharges(dogmaStaticMgr, fittingController):
    dogmaLocation = fittingController.dogmaLocation
    shipItem = dogmaLocation.GetShipItem()
    if not shipItem or not IsShip(shipItem.categoryID):
        return ([], [])
    currentFit = []
    for moduleDogmaItem in shipItem.GetFittedItems().itervalues():
        if moduleDogmaItem.flagID in const.moduleSlotFlags:
            if evetypes.GetCategoryID(moduleDogmaItem.typeID) == const.categoryCharge:
                qty = dogmaLocation.GetQuantity(moduleDogmaItem.itemID)
            else:
                qty = 1
            currentFit.append((moduleDogmaItem.typeID, moduleDogmaItem.flagID, qty))

    for flagID in [const.flagCargo, const.flagSpecializedAmmoHold]:
        itemsInHold = dogmaLocation.GetHoldItems(flagID)
        currentFit += [ (x.typeID, flagID, x.stacksize) for x in itemsInHold.itervalues() ]

    return FindModulesMissingCharges(dogmaStaticMgr, currentFit)


def FindUndersizedPropMod(dogmaStaticMgr, shipTypeID, fittedModules):
    if evetypes.GetGroupID(shipTypeID) in NON_PROP_MOD_GROUPS:
        return []
    undersized = []
    for typeID, flagID, qty in fittedModules:
        boosterFactor = dogmaStaticMgr.GetTypeAttribute(typeID, dogmaConst.attributeSpeedBoostFactor)
        if boosterFactor is None:
            continue
        mass = dogmaStaticMgr.GetTypeAttribute(shipTypeID, dogmaConst.attributeMass)
        ratio = mass / boosterFactor
        if ratio > MASS_SPEEDBOOST_MAX_RATIO:
            undersized.append((typeID, flagID))

    return undersized


def FindInefficientPropMod(shipTypeID, fittedModules):
    if evetypes.GetGroupID(shipTypeID) not in NON_PROP_MOD_GROUPS:
        return []
    inefficientPropMod = []
    for typeID, flagID, qty in fittedModules:
        if evetypes.GetGroupID(typeID) == groupPropulsionModule:
            inefficientPropMod.append((typeID, flagID))

    return inefficientPropMod


def FindModsDisablingBubbleImmunity(shipTypID, fittingController, dogmaStaticMgr, fittedModules):
    dogmaLocation = fittingController.dogmaLocation
    fittedItems = dogmaLocation.GetFittedItemsToShip()
    if not fittedItems:
        return []
    disablingImmunity = []
    immunityModules = []
    for moduleDogmaItem in fittedItems.itervalues():
        if evetypes.GetGroupID(moduleDogmaItem.typeID) == groupInterdictionNullifier:
            immunityModules.append((moduleDogmaItem.typeID, moduleDogmaItem.flagID))
        bubbleModifier = dogmaStaticMgr.GetTypeAttribute(moduleDogmaItem.typeID, dogmaConst.attributeWarpBubbleImmuneModifier)
        if bubbleModifier is not None:
            disablingImmunity.append((moduleDogmaItem.typeID, moduleDogmaItem.flagID))

    warpBubbleImmunity = dogmaStaticMgr.GetTypeAttribute(shipTypID, dogmaConst.attributeWarpBubbleImmune)
    if warpBubbleImmunity and disablingImmunity:
        return disablingImmunity
    if immunityModules and disablingImmunity:
        return disablingImmunity + immunityModules
    return []


def GetColorForLevel(warningLevel):
    return fittingWarningConst.colorByWarningLevel.get(warningLevel, None)


def GetHeaderForLevel(warningLevel):
    return fittingWarningConst.headerByWarningLevel.get(warningLevel, '')


def GetIconPathForTurretGroup(groupID):
    return fittingWarningConst.iconPathsByTurretGroup.get(groupID, None)


def GetIconPathForSizes(sizeValue):
    return fittingWarningConst.iconPathForSizes.get(sizeValue, None)


def GetWarningLevelFromWarningID(warningID):
    warningLevel, _, _ = fittingWarningConst.warningsByWarningID.get(warningID, (None, None, None))
    return warningLevel


def GetCargoOverloadedWarningID():
    fittingController = sm.GetService('ghostFittingSvc').GetGhostFittingController()
    if not fittingController or not fittingController.CurrentShipIsLoaded():
        return
    isOverloaded = IsCargoOverloaded(fittingController)
    if isOverloaded:
        return fittingWarningConst.WARNING_OVERLOADED_CARGO


def GetShieldArmorDualTankingModules(fittedModules):
    shieldModules, armorModules, hullModules = GetModulesByTankGroup(fittedModules)
    if shieldModules and armorModules:
        return shieldModules + armorModules
    return []


def GetMultiTankingModules(fittedModules):
    shieldModules, armorModules, hullModules = GetModulesByTankGroup(fittedModules)
    if shieldModules and armorModules and hullModules:
        return shieldModules + armorModules + hullModules
    return []


def EvaluateFit(fittingController):
    fittingSvc = sm.GetService('fittingSvc')
    try:
        currentFittingInfo = fittingSvc.GetFittingDictForCurrentFittingWindowShip()
    except RuntimeError as e:
        fittingSvc.LogWarn('Error when getting current fit: ', e)
        return

    shipTypeID, currentFit, allItems = currentFittingInfo
    fittedModules = [ (typeID, flagID, qty) for typeID, flagID, qty in currentFit if flagID in const.moduleSlotFlags ]
    highSlotModules = [ (typeID, flagID) for typeID, flagID, qty in fittedModules if flagID in const.hiSlotFlags ]
    dronesAndFighters = {typeID for typeID, flagID, _ in currentFit if flagID in fittingWarningConst.DRONE_AND_FIGHTER_BAYS}
    dronesAndFighters.update(fittingSvc.GetFighterTypesInTubes())
    dogmaStaticMgr = sm.GetService('clientDogmaStaticSvc')
    problematicShipAndTankCombos = GetProblematicShipAndTankingCombo(shipTypeID, fittedModules)
    mutaplasmidItemIDsByTypeID = GetMutaplasmidItemsByTypeID(allItems)
    reqCharges, optionalCharges = FindModulesWithMissingCharges(dogmaStaticMgr, fittingController)
    stackingWarningMed, stackingWarningLow, stackingWarningTargetedLow = FindFittedModulesWithStackingPenalty(currentFit)
    results = {fittingWarningConst.WARNING_MISSING_SUBSYSTEMS: FindMissingSubsystemFlags(shipTypeID, currentFit),
     fittingWarningConst.WARNING_MODULES_IN_INVALID_FLAGS: FindModulesInNonExisitingSlots(fittingController, currentFit),
     fittingWarningConst.WARNING_OVER_POWERGRID: IsOverOnPowergrid(fittingController),
     fittingWarningConst.WARNING_OVER_CPU: IsOverOnCPU(fittingController),
     fittingWarningConst.WARNING_OVER_CALIBRATION: IsOverOnCalibration(fittingController),
     fittingWarningConst.WARNING_OVERLOADED_CARGO: GetCargoOverloadedWarningID(),
     fittingWarningConst.WARNING_DUAL_TANKED: GetShieldArmorDualTankingModules(fittedModules),
     fittingWarningConst.WARNING_ARMOR_TANKED_SHIELD_SHIP: problematicShipAndTankCombos.get(fittingWarningConst.WARNING_ARMOR_TANKED_SHIELD_SHIP, None),
     fittingWarningConst.WARNING_SHIELD_TANKED_ARMOR_SHIP: problematicShipAndTankCombos.get(fittingWarningConst.WARNING_SHIELD_TANKED_ARMOR_SHIP, None),
     fittingWarningConst.WARNING_NOT_PROVIDING_BONUS: FindModulesNotProvidingBonus(fittedModules, dronesAndFighters, mutaplasmidItemIDsByTypeID),
     fittingWarningConst.WARNING_MIXING_TURRET_GROUPS: GetMixedTurrets(highSlotModules),
     fittingWarningConst.WARNING_MIXING_LAUNCHER_GROUPS: GetMixedLauncherGroups(dogmaStaticMgr, highSlotModules),
     fittingWarningConst.WARNING_MIXING_TURRET_SIZES: GetMixedTurretSizes(highSlotModules, mutaplasmidItemIDsByTypeID),
     fittingWarningConst.WARNING_POLARIZED_WEAPONS: GetPolarizedWeapons(dogmaStaticMgr, fittedModules),
     fittingWarningConst.WARNING_OFFLINE_MODULES: FindOfflineModules(fittingController),
     fittingWarningConst.WARNING_MISSING_REQ_CHARGES: reqCharges,
     fittingWarningConst.WARNING_MISSING_OPTIONAL_CHARGES: optionalCharges,
     fittingWarningConst.WARNING_STACKING_PENALTY_MED: stackingWarningMed,
     fittingWarningConst.WARNING_STACKING_PENALTY_LOW: stackingWarningLow,
     fittingWarningConst.WARNING_STACKING_PENALTY_TARGETED_LOW: stackingWarningTargetedLow,
     fittingWarningConst.WARNING_UNDERSIZED_PROP_MOD: FindUndersizedPropMod(dogmaStaticMgr, shipTypeID, fittedModules),
     fittingWarningConst.WARNING_DISABLED_BUBBLE_IMMUNITY: FindModsDisablingBubbleImmunity(shipTypeID, fittingController, dogmaStaticMgr, fittedModules),
     fittingWarningConst.WARNING_INEFFICIENT_PROP_MOD: FindInefficientPropMod(shipTypeID, fittedModules)}
    return results


def GetMutaplasmidItemsByTypeID(allItems):
    itemIDsByTypeID = defaultdict(list)
    for eachItem in allItems:
        if evetypes.IsDynamicType(eachItem.typeID):
            itemIDsByTypeID[eachItem.typeID].append(eachItem.itemID)

    return dict(itemIDsByTypeID)


def FilterResultsForWarningLevel(fitResults, warningLevels):
    newResults = {}
    for eachWarningID, eachValue in fitResults.iteritems():
        lvl = GetWarningLevelFromWarningID(eachWarningID)
        if lvl in warningLevels:
            newResults[eachWarningID] = eachValue

    return newResults


def GetActiveWarningsByLevel(fittingController):
    if not fittingController or not fittingController.CurrentShipIsLoaded():
        return {}
    fitResults = EvaluateFit(fittingController)
    if fitResults is None:
        return {}
    activeWarningsByLevel = GetActiveWarningsByLevelFromResults(fitResults)
    return activeWarningsByLevel


def GetActiveWarningsByLevelFromResults(fitResults):
    activeWarningsByLevel = defaultdict(int)
    for warningID, warningValue in fitResults.iteritems():
        if bool(warningValue):
            lvl = GetWarningLevelFromWarningID(warningID)
            activeWarningsByLevel[lvl] += 1

    return activeWarningsByLevel


def GetSlotsMissingSkills(missingSkillsForTypeID):
    dogmaLocation = sm.GetService('fittingSvc').GetCurrentDogmaLocation()
    allFittedItems = {}
    warningSlotDict = {}
    extraHolds = [const.flagCargo, const.flagDroneBay, const.flagFighterBay] + const.fighterTubeFlags
    for eachHoldFlagID in extraHolds:
        allFittedItems.update(dogmaLocation.GetHoldItems(eachHoldFlagID))

    allFittedItems.update(dogmaLocation.GetFittedItemsToShip())
    validFlags = const.moduleSlotFlags + extraHolds
    for eachItem in allFittedItems.itervalues():
        if eachItem.flagID not in validFlags:
            continue
        if eachItem.typeID in missingSkillsForTypeID:
            warningSlotDict[eachItem.flagID] = fittingWarningConst.WARNING_LEVEL_SKILL

    return warningSlotDict


def HasEffect(typeID, effectID):
    return sm.GetService('clientDogmaStaticSvc').TypeHasEffect(typeID, effectID)


def FindFittedModulesWithStackingPenalty(currentFit):
    fittedModules = [ (typeID, flagID) for typeID, flagID, _ in currentFit if flagID in const.fittingFlags ]
    nonStackableAttributes, nonStackableAttributesTargeted = FindModulesWithStackingPenalty(fittedModules)
    nonStackableMed, nonStackableLow = _GetStackingWarnings(nonStackableAttributes)
    nonStackableTargetedMed, nonStackableTargetedLow = _GetStackingWarnings(nonStackableAttributesTargeted)
    nonStackableTargetedLow.update(nonStackableTargetedMed)
    return (nonStackableMed, nonStackableLow, nonStackableTargetedLow)


def _GetStackingWarnings(nonStackableAttributes):
    medThreshold = 3
    lowThresHold = 2
    medWarning = {}
    lowWarning = {}
    for a, m in nonStackableAttributes.iteritems():
        modulesForAttribute = m
        skillTypeID = a[2]
        if skillTypeID:
            otherModules = nonStackableAttributes.get((a[0],
             a[1],
             None,
             a[3]), set())
            modulesForAttribute = modulesForAttribute.union(otherModules)
        numModules = len(modulesForAttribute)
        if numModules > medThreshold:
            medWarning[a] = modulesForAttribute
        elif numModules > lowThresHold:
            lowWarning[a] = modulesForAttribute

    return (medWarning, lowWarning)
