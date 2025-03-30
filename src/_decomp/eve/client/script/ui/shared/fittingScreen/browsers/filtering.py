#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\browsers\filtering.py
import evetypes
from eve.client.script.ui.shared.fittingScreen.settingUtil import HardwareFiltersSettingObject, FILTER_TYPE_DEFAULT
from inventorycommon.util import IsModularShip
from utillib import KeyVal
import telemetry
import blue

def GetFilters(isSimulated, hwFilterObject):
    slotFilterInfo = KeyVal(showHiSlots=hwFilterObject.GetHwHiSlotSetting(), showMedSlots=hwFilterObject.GetHwMedSlotSetting(), showLoSlots=hwFilterObject.GetHwLoSlotsSetting(), showRigSlots=hwFilterObject.GetHwRigSlotsSetting(), showSubSystemSlots=hwFilterObject.GetHwRigSlotsSetting(), showDrones=hwFilterObject.GetHwDronesSetting())
    filterMode_resourcesOnOutput = hwFilterObject.GetFilterModeForResource()
    resourceFilterActive = hwFilterObject.GetHwResourcesSetting() and isSimulated
    totalResourceFilterActive = resourceFilterActive and filterMode_resourcesOnOutput
    leftResourceFilterActive = resourceFilterActive and not filterMode_resourcesOnOutput
    filters = KeyVal(filterString=hwFilterObject.GetTextFilter(), filterByShipCanUse=hwFilterObject.GetHwShipCanUseSetting(), filterOnCpu=totalResourceFilterActive, filterOnCpuLeft=leftResourceFilterActive, filterOnPowergrid=totalResourceFilterActive, filterOnPowergridLeft=leftResourceFilterActive, filterOnCalibration=totalResourceFilterActive, filterOnCalibrationLeft=leftResourceFilterActive, filterOnSkills=hwFilterObject.GetHwSkillsSetting(), slotFilterInfo=slotFilterInfo)
    return filters


def GetCpuAndPowerLeft(dogmaLocation):
    cpuOutput = GetCpuOutputOfCurrentShip(dogmaLocation)
    cpuUsed = dogmaLocation.GetAttributeValue(dogmaLocation.GetCurrentShipID(), const.attributeCpuLoad)
    cpuLeft = cpuOutput - cpuUsed
    powerOutput = GetPowerOutputOfCurrentShip(dogmaLocation)
    powerUsed = dogmaLocation.GetAttributeValue(dogmaLocation.GetCurrentShipID(), const.attributePowerLoad)
    powerLeft = powerOutput - powerUsed
    calibrationOutput = GetCalibrationOfCurrentShip(dogmaLocation)
    calibrationUsed = dogmaLocation.GetAttributeValue(dogmaLocation.GetCurrentShipID(), const.attributeUpgradeLoad)
    calibrationLeft = calibrationOutput - calibrationUsed
    return (cpuLeft, powerLeft, calibrationLeft)


def GetCpuOutputOfCurrentShip(dogmaLocation):
    return dogmaLocation.GetAttributeValue(dogmaLocation.GetCurrentShipID(), const.attributeCpuOutput)


def GetPowerOutputOfCurrentShip(dogmaLocation):
    return dogmaLocation.GetAttributeValue(dogmaLocation.GetCurrentShipID(), const.attributePowerOutput)


def GetCalibrationOfCurrentShip(dogmaLocation):
    return dogmaLocation.GetAttributeValue(dogmaLocation.GetCurrentShipID(), const.attributeUpgradeCapacity)


def GetResourceRigsFitted(dogmaLocation):
    rigList = []
    shipID = dogmaLocation.GetCurrentShipID()
    for flagID in const.rigSlotFlags:
        rigItemID = dogmaLocation.GetSlotOther(shipID, flagID)
        if not rigItemID:
            continue
        dogmaItem = dogmaLocation.SafeGetDogmaItem(rigItemID)
        if not dogmaItem:
            continue
        if evetypes.GetGroupID(dogmaItem.typeID) == const.groupRigCore:
            rigList.append(dogmaItem.typeID)

    rigList.sort()
    return tuple(rigList)


@telemetry.ZONE_METHOD
def GetValidTypeIDs(typeList, searchFittingHelper, hwSettingObject = None):
    fittingSvc = sm.GetService('fittingSvc')
    isSimulated = fittingSvc.IsShipSimulated()
    hwFilterObject = hwSettingObject or HardwareFiltersSettingObject()
    isBrowser = hwFilterObject.GetFilterType() == FILTER_TYPE_DEFAULT
    filters = GetFilters(isSimulated, hwFilterObject=hwFilterObject)
    fittingHelper = searchFittingHelper
    dogmaLocation = fittingSvc.GetCurrentDogmaLocation()
    skillSvc = sm.GetService('skills')
    ship = dogmaLocation.GetShipItem()
    if not ship:
        return typeList
    shipID = ship.itemID
    shipTypeID = ship.typeID
    shipRigSize = fittingHelper.GetShipRigSize(shipTypeID)
    isCapitalShip = fittingHelper.IsCapitalSize(evetypes.GetGroupID(shipTypeID))
    isModularShip = IsModularShip(shipTypeID)
    if isModularShip:
        numTurretsFitted, numLaunchersFitted = fittingHelper.GetFittedLauncherAndTurrets(dogmaLocation, ship)
    else:
        numTurretsFitted = numLaunchersFitted = 0
    cpuLeft, powerLeft, calibrationLeft = GetCpuAndPowerLeft(dogmaLocation)
    cpuOutput = GetCpuOutputOfCurrentShip(dogmaLocation)
    powerOutput = GetPowerOutputOfCurrentShip(dogmaLocation)
    calibrationOutput = GetCalibrationOfCurrentShip(dogmaLocation)
    resourceRigsFitted = GetResourceRigsFitted(dogmaLocation)
    ghostFittingSvc = sm.GetService('ghostFittingSvc')
    ret = set()
    dogmaLocation.scatterAttributeChanges = False
    try:
        for typeID in typeList:
            blue.pyos.BeNice()
            if isBrowser:
                if fittingHelper.IsMutaplasmid(typeID):
                    continue
                if fittingHelper.IsDynamicType(typeID):
                    continue
            if filters.filterByShipCanUse:
                if not fittingHelper.CanFitModuleToShipTypeOrGroup(shipTypeID, dogmaLocation, typeID):
                    continue
                if fittingHelper.IsRigSizeRestricted(typeID, shipRigSize):
                    continue
                if fittingHelper.IsModuleTooBig(shipTypeID, typeID, isCapitalShip):
                    continue
                if fittingHelper.RestrictedByDroneOrFighter(shipTypeID, typeID, isModularShip):
                    continue
                if isModularShip:
                    if fittingHelper.GetNumSlotForModuleForModularShip(dogmaLocation, shipID, typeID, numTurretsFitted, numLaunchersFitted) == 0:
                        continue
                elif fittingHelper.GetNumSlotForModule(shipTypeID, typeID) == 0:
                    continue
            filterOutFromSlotType = DoSlotTypeFiltering(fittingHelper, typeID, filters.slotFilterInfo)
            if filterOutFromSlotType:
                continue
            if filters.filterOnCalibration:
                usedByType = fittingHelper.GetCalibrationForModuleType(typeID)
                if usedByType > calibrationOutput:
                    continue
            elif filters.filterOnCalibrationLeft:
                usedByType = fittingHelper.GetCalibrationForModuleType(typeID)
                if usedByType > calibrationLeft:
                    continue
            if filters.filterOnSkills:
                missingSkills = fittingHelper.GetMissingSkills(typeID, dogmaLocation, skillSvc)
                if missingSkills:
                    continue
            if filters.filterOnCpu:
                usedByType = fittingHelper.GetCPUForModuleType(ghostFittingSvc, shipID, typeID, shipTypeID, resourceRigsFitted)
                if usedByType > cpuOutput:
                    continue
            elif filters.filterOnCpuLeft:
                usedByType = fittingHelper.GetCPUForModuleType(ghostFittingSvc, shipID, typeID, shipTypeID, resourceRigsFitted)
                if usedByType > cpuLeft:
                    continue
            if filters.filterOnPowergrid:
                usedByType = fittingHelper.GetPowergridForModuleType(ghostFittingSvc, shipID, typeID, shipTypeID, resourceRigsFitted)
                if usedByType > powerOutput:
                    continue
            elif filters.filterOnPowergridLeft:
                usedByType = fittingHelper.GetPowergridForModuleType(ghostFittingSvc, shipID, typeID, shipTypeID, resourceRigsFitted)
                if usedByType > powerLeft:
                    continue
            if not filters.filterString or filters.filterString in fittingHelper.GetTypeName(typeID):
                ret.add(typeID)

    finally:
        dogmaLocation.scatterAttributeChanges = True

    return ret


def GetValidModuleTypeIDs(typeList, searchFittingHelper, hwSettingObject = None):
    validTypeIDs = set()
    for typeID in typeList:
        try:
            if searchFittingHelper.IsModule(typeID):
                validTypeIDs.add(typeID)
        except Exception:
            pass

    return GetValidTypeIDs(validTypeIDs, searchFittingHelper, hwSettingObject)


def DoSlotTypeFiltering(fittingHelper, moduleTypeID, filterInfo):
    if filterInfo.showHiSlots + filterInfo.showLoSlots + filterInfo.showMedSlots + filterInfo.showRigSlots + filterInfo.showDrones + filterInfo.showSubSystemSlots in (0,):
        return False
    toCheck = [(filterInfo.showHiSlots, fittingHelper.IsHislotModule),
     (filterInfo.showLoSlots, fittingHelper.IsLoSlot),
     (filterInfo.showMedSlots, fittingHelper.IsMedslotModule),
     (filterInfo.showRigSlots, fittingHelper.IsRigSlot),
     (filterInfo.showDrones, fittingHelper.IsDroneOrFighter),
     (filterInfo.showSubSystemSlots, fittingHelper.IsSubSystemSlot)]
    for doCheck, checkFunc in toCheck:
        if doCheck:
            isSlotType = checkFunc(moduleTypeID)
            if isSlotType:
                return False

    return True
