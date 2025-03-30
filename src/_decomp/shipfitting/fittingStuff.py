#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipfitting\fittingStuff.py
import dogma.const as dogmaConst
import dogma.data as dogma_data
from eve.common.lib import appConst
import evetypes
from eveexceptions import UserError
from inventorycommon.util import IsShipFittingFlag, IsSubsystemFlag, IsSubsystemFlagVisible, IsShipFittable
from inventorycommon import const as invConst
import shipfitting.errorConst as errorConst
from utillib import KeyVal

def GetHardwareLayoutForShip(moduleTypeID, shipTypeID, dogmaStaticMgr, currentModuleList):
    typeID = moduleTypeID
    groupID = evetypes.GetGroupID(moduleTypeID)
    hardwareAttribs = {}
    typeEffects = dogmaStaticMgr.TypeGetEffects(typeID)
    GTA = dogmaStaticMgr.GetTypeAttribute2
    isTurret = isLauncher = False
    if const.effectHiPower in typeEffects:
        hardwareAttribs[const.attributeHiSlots] = int(GTA(shipTypeID, const.attributeHiSlots))
        if const.effectTurretFitted in typeEffects:
            hardwareAttribs[const.attributeTurretSlotsLeft] = int(GTA(shipTypeID, const.attributeTurretSlotsLeft))
            isTurret = True
        elif const.effectLauncherFitted in typeEffects:
            hardwareAttribs[const.attributeLauncherSlotsLeft] = int(GTA(shipTypeID, const.attributeLauncherSlotsLeft))
            isLauncher = True
    elif const.effectMedPower in typeEffects:
        hardwareAttribs[const.attributeMedSlots] = int(GTA(shipTypeID, const.attributeMedSlots))
    elif const.effectLoPower in typeEffects:
        hardwareAttribs[const.attributeLowSlots] = int(GTA(shipTypeID, const.attributeLowSlots))
    elif const.effectRigSlot in typeEffects:
        hardwareAttribs[const.attributeRigSlots] = int(GTA(shipTypeID, const.attributeRigSlots))
    elif const.effectSubSystem in typeEffects:
        hardwareAttribs[const.attributeMaxSubSystems] = int(GTA(shipTypeID, const.attributeMaxSubSystems))
    elif const.effectServiceSlot in typeEffects:
        hardwareAttribs[const.attributeServiceSlots] = int(GTA(shipTypeID, const.attributeServiceSlots))
    turretsFitted = 0
    launchersFitted = 0
    rigsFitted = 0
    calibration = 0
    shipHardwareModifierAttribs = dogmaStaticMgr.GetShipHardwareModifierAttribs()
    modulesByGroup = 0
    modulesByType = 0
    for item in currentModuleList:
        if not IsShipFittingFlag(item.flagID):
            continue
        if item.groupID == groupID:
            modulesByGroup += 1
        if item.typeID == typeID:
            modulesByType += 1
        if const.flagHiSlot0 <= item.flagID <= const.flagHiSlot7:
            if isTurret:
                if dogmaStaticMgr.TypeHasEffect(item.typeID, const.effectTurretFitted):
                    turretsFitted += 1
            elif isLauncher:
                if dogmaStaticMgr.TypeHasEffect(item.typeID, const.effectLauncherFitted):
                    launchersFitted += 1
        elif const.flagRigSlot0 <= item.flagID <= const.flagRigSlot7:
            rigsFitted += 1
            calibration += GTA(item.typeID, const.attributeUpgradeCost)
        elif IsSubsystemFlag(item.flagID):
            for attributeID, modifyingAttributeID in shipHardwareModifierAttribs:
                if attributeID not in hardwareAttribs:
                    continue
                hardwareAttribs[attributeID] += GTA(item.typeID, modifyingAttributeID)

    return (hardwareAttribs,
     turretsFitted,
     launchersFitted,
     rigsFitted,
     calibration,
     modulesByGroup,
     modulesByType)


def IsModuleTooBigForShip(moduleTypeID, shipTypeID, isCapitalShip = None, isStructure = None):
    if isCapitalShip is None:
        isCapitalShip = evetypes.GetGroupID(shipTypeID) in cfg.GetShipGroupByClassType()[appConst.GROUP_CAPITALSHIPS]
    if isStructure is None:
        isStructure = evetypes.GetCategoryID(shipTypeID) == invConst.categoryStructure
    if not isCapitalShip and not isStructure:
        itemVolume = evetypes.GetVolume(moduleTypeID)
        if itemVolume > invConst.maxNonCapitalModuleSize:
            return True
    return False


def GetErrorInfoDoesModuleTypeIDFit(fittingDogmaLocation, moduleTypeID, flagID, originalItemID = None):
    shipID = fittingDogmaLocation.shipID
    shipItem = fittingDogmaLocation.dogmaItems[shipID]
    shipTypeID = shipItem.typeID
    moduleErrorInfo = GetModuleErrorInfo(fittingDogmaLocation, moduleTypeID, shipTypeID)
    if moduleErrorInfo is not None:
        return moduleErrorInfo
    try:
        CheckCanFitType(fittingDogmaLocation, moduleTypeID, shipID, originalItemID)
    except UserError as e:
        if e.msg == 'CantFitTooManyByGroup':
            return KeyVal(errorKey=errorConst.CANT_FIT_TOO_MANY_BY_GROUP, extraInfo=e.dict.get('noOfModules', None))
        if e.msg == 'CantFitTooManyByType':
            return KeyVal(errorKey=errorConst.CANT_FIT_TOO_MANY_BY_TYPE, extraInfo=e.dict.get('noOfModules', None))
        if e.msg == 'ModuleNotPowered':
            return KeyVal(errorKey=errorConst.MODULE_NOT_POWERED, extraInfo=None)

    dogmaStaticMgr = fittingDogmaLocation.dogmaStaticMgr
    currentModuleList = shipItem.GetFittedItems().values()
    return GetErrorInfoFromHardware(dogmaStaticMgr, shipTypeID, moduleTypeID, flagID, currentModuleList)


def GetErrorInfoDoesModuleTypeIDFitCurrentShip(dogmaLocation, moduleTypeID, flagID):
    shipID = session.shipid
    shipItem = dogmaLocation.dogmaItems[shipID]
    shipTypeID = shipItem.typeID
    moduleErrorInfo = GetModuleErrorInfo(dogmaLocation, moduleTypeID, shipTypeID)
    if moduleErrorInfo is not None:
        return moduleErrorInfo
    try:
        dogmaLocation.CheckCanFitByShipAndType(shipID, moduleTypeID)
    except UserError as e:
        if e.msg == 'CantFitTooManyByGroup':
            return KeyVal(errorKey=errorConst.CANT_FIT_TOO_MANY_BY_GROUP, extraInfo=e.dict.get('noOfModules', None))
        if e.msg == 'CantFitTooManyByType':
            return KeyVal(errorKey=errorConst.CANT_FIT_TOO_MANY_BY_TYPE, extraInfo=e.dict.get('noOfModules', None))

    dogmaStaticMgr = dogmaLocation.dogmaStaticMgr
    currentModuleList = shipItem.GetFittedItems().values()
    return GetErrorInfoFromHardware(dogmaStaticMgr, shipTypeID, moduleTypeID, flagID, currentModuleList)


def GetModuleErrorInfo(dogmaLocation, moduleTypeID, shipTypeID):
    if not IsShipFittable(evetypes.GetCategoryID(moduleTypeID)):
        return KeyVal(errorKey=errorConst.MODULE_NOT_APPROPRIATE_FOR_CATEGORY, extraInfo=None)
    if not IsCategoryOK_StructureVsShipRestrictions(shipTypeID, moduleTypeID):
        return KeyVal(errorKey=errorConst.MODULE_NOT_APPROPRIATE_FOR_CATEGORY, extraInfo=None)
    if not CanFitModuleToShipTypeOrGroup(dogmaLocation, moduleTypeID):
        return KeyVal(errorKey=errorConst.CANT_FIT_MODULE_TO_SHIP, extraInfo=None)
    if IsModuleTooBigForShip(moduleTypeID, shipTypeID):
        return KeyVal(errorKey=errorConst.MODULE_TOO_BIG, extraInfo=None)


def IsRigTooSmall(dogmaStaticMgr, shipTypeID, moduleTypeID):
    shipRigSize = dogmaStaticMgr.GetTypeAttribute2(shipTypeID, dogmaConst.attributeRigSize)
    if shipRigSize:
        notRightSize = IsRigSizeRestricted(dogmaStaticMgr, moduleTypeID, shipRigSize)
        if notRightSize:
            return True
    return False


def GetErrorInfoFromHardware(dogmaStaticMgr, shipTypeID, moduleTypeID, flagID, currentModuleList):
    hardwareLayout, turretsFitted, launchersFitted, rigsFitted, totalCalibration, modulesByGroup, modulesByType = GetHardwareLayoutForShip(moduleTypeID, shipTypeID, dogmaStaticMgr, currentModuleList)
    if dogmaStaticMgr.TypeHasEffect(moduleTypeID, dogmaConst.effectLauncherFitted):
        balance = hardwareLayout[dogmaConst.attributeLauncherSlotsLeft] - launchersFitted
        if balance < 1:
            return KeyVal(errorKey=errorConst.NOT_ENOUGH_LAUNCHER_SLOTS, extraInfo=None)
    if dogmaStaticMgr.TypeHasEffect(moduleTypeID, dogmaConst.effectTurretFitted):
        balance = hardwareLayout[dogmaConst.attributeTurretSlotsLeft] - turretsFitted
        if balance < 1:
            return KeyVal(errorKey=errorConst.NOT_ENOUGH_TURRET_SLOTS, extraInfo=None)
    if dogmaStaticMgr.TypeHasEffect(moduleTypeID, dogmaConst.effectRigSlot):
        balance = hardwareLayout[dogmaConst.attributeRigSlots] - rigsFitted
        if balance < 1:
            return KeyVal(errorKey=errorConst.NOT_ENOUGH_RIG_SLOTS, extraInfo=None)
        if IsRigTooSmall(dogmaStaticMgr, shipTypeID, moduleTypeID):
            return KeyVal(errorKey=errorConst.RIG_WRONG_SIZE, extraInfo=None)
    try:
        firstSlot, firstNonSlot = GetValidSlotsForType(dogmaStaticMgr, hardwareLayout, moduleTypeID)
        if flagID < firstSlot or flagID >= firstNonSlot:
            return KeyVal(errorKey=errorConst.SLOT_NOT_PRESENT, extraInfo=None)
    except UserError as e:
        if e.msg == 'ModuleNotPowered':
            return KeyVal(errorKey=errorConst.MODULE_NOT_POWERED, extraInfo=None)


def IsFittable(effectID):
    isFittable = effectID in (const.effectHiPower,
     const.effectMedPower,
     const.effectLoPower,
     const.effectSubSystem,
     const.effectRigSlot,
     const.effectServiceSlot)
    return isFittable


def IsRightSlotForType(dogmaStaticMgr, typeID, flagID):
    flagsForType = GetSlotListForTypeID(dogmaStaticMgr, typeID)
    return flagID in flagsForType


def GetSlotTypeForType(typeID):
    for effect in dogma_data.get_type_effects(typeID):
        if IsFittable(effect.effectID):
            return effect.effectID


POWER_TO_FLAG_DICT = {dogmaConst.effectHiPower: invConst.hiSlotFlags,
 dogmaConst.effectMedPower: invConst.medSlotFlags,
 dogmaConst.effectLoPower: invConst.loSlotFlags,
 dogmaConst.effectRigSlot: invConst.rigSlotFlags,
 dogmaConst.effectSubSystem: invConst.subsystemSlotFlags,
 dogmaConst.effectServiceSlot: invConst.serviceSlotFlags}

def GetSlotListForTypeID(dogmaStaticMgr, typeID):
    slotType = GetSlotTypeForType(typeID)
    slotList = POWER_TO_FLAG_DICT.get(slotType, [])
    if slotType == const.effectSubSystem:
        slotList = [int(dogmaStaticMgr.GetTypeAttribute2(typeID, const.attributeSubSystemSlot))]
    return slotList


def GetValidSlotsForType(dogmaIM, hardwareLayout, typeID):
    eff = dogmaIM.TypeGetEffects(typeID)
    if dogmaConst.effectLoPower in eff:
        slotsAllowed = hardwareLayout[dogmaConst.attributeLowSlots]
        firstSlot, firstNonSlot = invConst.flagLoSlot0, min(invConst.flagLoSlot0 + slotsAllowed, invConst.flagLoSlot7 + 1)
    elif dogmaConst.effectHiPower in eff:
        slotsAllowed = hardwareLayout[dogmaConst.attributeHiSlots]
        firstSlot, firstNonSlot = invConst.flagHiSlot0, min(invConst.flagHiSlot0 + slotsAllowed, invConst.flagHiSlot7 + 1)
    elif dogmaConst.effectMedPower in eff:
        slotsAllowed = hardwareLayout[dogmaConst.attributeMedSlots]
        firstSlot, firstNonSlot = invConst.flagMedSlot0, min(invConst.flagMedSlot0 + slotsAllowed, invConst.flagMedSlot7 + 1)
    elif dogmaConst.effectRigSlot in eff:
        slotsAllowed = hardwareLayout[dogmaConst.attributeRigSlots]
        firstSlot, firstNonSlot = invConst.flagRigSlot0, min(invConst.flagRigSlot0 + slotsAllowed, invConst.flagRigSlot7 + 1)
    elif dogmaConst.effectSubSystem in eff:
        slotsAllowed = hardwareLayout[dogmaConst.attributeMaxSubSystems]
        desiredFlag = int(dogmaIM.GetTypeAttribute2(typeID, dogmaConst.attributeSubSystemSlot))
        if not IsSubsystemFlagVisible(desiredFlag):
            firstSlot = invConst.flagSubSystemSlot0 + invConst.numVisibleSubsystems
            firstNonSlot = min(invConst.flagSubSystemSlot0 + slotsAllowed, invConst.flagSubSystemSlot7 + 1)
            if firstNonSlot < firstSlot:
                raise UserError('NoSuitableSlotsForThisSubSystem', {'subSystemName': (const.UE_TYPEID, typeID)})
        else:
            firstSlot, firstNonSlot = desiredFlag, desiredFlag + 1
    elif dogmaConst.effectServiceSlot in eff:
        slotsAllowed = hardwareLayout[dogmaConst.attributeServiceSlots]
        firstSlot, firstNonSlot = invConst.flagServiceSlot0, min(invConst.flagServiceSlot0 + slotsAllowed, invConst.flagServiceSlot7 + 1)
    else:
        slotsAllowed = 0
    if slotsAllowed <= 0:
        raise UserError('ModuleNotPowered', {'type': typeID})
    return (int(firstSlot), int(firstNonSlot))


def CanFitModuleToShipTypeOrGroup(dogmaLocation, typeID):
    shipItem = dogmaLocation.dogmaItems[dogmaLocation.GetCurrentShipID()]
    return GetCanFitModuleTypeToShipType(dogmaLocation, shipItem.typeID, typeID)


def GetCanFitModuleTypeToShipType(dogmaLocation, shipTypeID, moduleTypeID):
    groupID = evetypes.GetGroupID(shipTypeID)
    return dogmaLocation.dogmaStaticMgr.CanFitModuleToShipTypeOrGroup(moduleTypeID, shipTypeID, groupID)


def IsRigSizeRestricted(dogmaStaticMgr, moduleTypeID, shipRigSize):
    if not dogmaStaticMgr.TypeHasEffect(moduleTypeID, dogmaConst.effectRigSlot):
        return False
    rigSize = dogmaStaticMgr.GetTypeAttribute2(moduleTypeID, dogmaConst.attributeRigSize)
    if shipRigSize != rigSize:
        return True
    return False


def IsCategoryOK_StructureVsShipRestrictions(shipTypeID, moduleTypeID):
    moduleCategoryID = evetypes.GetCategoryID(moduleTypeID)
    if evetypes.GetCategoryID(shipTypeID) == invConst.categoryStructure:
        return moduleCategoryID in (invConst.categoryStructureModule, invConst.categoryFighter)
    else:
        return moduleCategoryID != invConst.categoryStructureModule


def IsRigSlot(flagID):
    return flagID in invConst.rigSlotFlags


def CheckCanFitType(fittingDogmaLocation, typeID, locationID, originalItemID):
    maxGroupFitted = fittingDogmaLocation.GetAttributesForRealItemID(originalItemID, typeID).get(const.attributeMaxGroupFitted)
    if maxGroupFitted:
        groupID = evetypes.GetGroupID(typeID)
        modulesByGroup = fittingDogmaLocation.GetModuleListByShipGroup(locationID, groupID)
        if len(modulesByGroup) >= maxGroupFitted:
            shipItem = fittingDogmaLocation.dogmaItems[locationID]
            raise UserError('CantFitTooManyByGroup', {'ship': shipItem.typeID,
             'module': typeID,
             'groupName': evetypes.GetGroupName(typeID),
             'noOfModules': int(maxGroupFitted),
             'noOfModulesFitted': len(modulesByGroup)})
    maxTypeFitted = fittingDogmaLocation.GetAttributesForRealItemID(originalItemID, typeID).get(const.attributeMaxGroupFitted)
    if maxTypeFitted:
        modulesByType = fittingDogmaLocation.GetModuleListByShipType(locationID, typeID)
        if len(modulesByType) >= maxTypeFitted:
            shipItem = fittingDogmaLocation.dogmaItems[locationID]
            raise UserError('CantFitTooManyByType', {'ship': shipItem.typeID,
             'module': typeID,
             'noOfModules': int(maxTypeFitted),
             'noOfModulesFitted': len(modulesByType)})


def IsThereRigMismatch(currentlyFittedRigsByFlagID, rigsInFitByFlagIDs):
    otherRigsAlreadyInSlot = [ xFlag for xFlag, xTypeID in rigsInFitByFlagIDs.iteritems() if xFlag in currentlyFittedRigsByFlagID and currentlyFittedRigsByFlagID[xFlag] != xTypeID ]
    currentRigsNotInFits = [ xFlag for xFlag, xTypeID in currentlyFittedRigsByFlagID.iteritems() if xFlag not in rigsInFitByFlagIDs ]
    rigMismatch = bool(otherRigsAlreadyInSlot or currentRigsNotInFits)
    return rigMismatch
