#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipfitting\fittingWarningsCharges.py
from collections import defaultdict
import evetypes
from caching import Memoize
from eve.common.lib import appConst

@Memoize
def _GetModulesUsingOptionalCharges():
    return evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_FITTING_WARNINGS_USE_OPTIONAL_CHARGES)


@Memoize
def _GetModulesNeedingCharges():
    return evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_FITTING_WARNINGS_NEED_CHARGES)


TREAT_AS_FULL = {appConst.groupScanProbeLauncher: 8}

def FindModulesMissingCharges(dogmaStaticMgr, currentFit):
    chargesInFlags = defaultdict(list)
    for typeID, flagID, qty in currentFit:
        if evetypes.GetCategoryID(typeID) == appConst.categoryCharge:
            chargesInFlags[flagID].append((typeID, qty))

    chargesInHold = _GetAllChargesInHolds(chargesInFlags)
    allChargesLeftInHolds = chargesInHold.copy()
    fittedModulesNeedingCharges = [ (typeID, flagID) for typeID, flagID, _ in currentFit if typeID in _GetModulesNeedingCharges() ]
    fittedModulesThatHaveOptionalCharges = [ (typeID, flagID) for typeID, flagID, _ in currentFit if typeID in _GetModulesUsingOptionalCharges() ]
    modulesWithoutCharges = []
    partiallyFullModulesByChargeTypeID = defaultdict(list)
    for eachModuleTypeID, eachFlagID in fittedModulesNeedingCharges + fittedModulesThatHaveOptionalCharges:
        chargeInfo = chargesInFlags.get(eachFlagID)
        if chargeInfo:
            chargeTypeID, chargeQty = chargeInfo[0]
            launcherCapacity = dogmaStaticMgr.GetTypeAttribute(eachModuleTypeID, appConst.attributeCapacity)
            chargeVolume = dogmaStaticMgr.GetTypeAttribute(chargeTypeID, appConst.attributeVolume)
            qtyFull = int(launcherCapacity / chargeVolume)
            overridenFull = TREAT_AS_FULL.get(evetypes.GetGroupID(eachModuleTypeID))
            if overridenFull and overridenFull < qtyFull:
                qtyFull = overridenFull
            missingQty = qtyFull - chargeQty
            if missingQty > 1:
                partiallyFullModulesByChargeTypeID[chargeTypeID].append((eachModuleTypeID, eachFlagID, chargeQty))
        else:
            modulesWithoutCharges.append((eachModuleTypeID, eachFlagID))

    for eachChargeTypeID, moduleInfo in partiallyFullModulesByChargeTypeID.iteritems():
        for moduleTypeID, flagID, chargeQty in moduleInfo:
            modulesWithoutCharges.append((moduleTypeID, flagID))
            allChargesLeftInHolds[eachChargeTypeID] += chargeQty

    partiallyFullModulesByChargeTypeID.clear()
    modulesThatCannotBeFilled = FindModulesThatCannotBeFilled(dogmaStaticMgr, allChargesLeftInHolds, modulesWithoutCharges)
    modulesRequiringCharges = [ x for x in modulesThatCannotBeFilled if x in fittedModulesNeedingCharges ]
    modulesWithOptionalCharges = [ x for x in modulesThatCannotBeFilled if x in fittedModulesThatHaveOptionalCharges ]
    return (modulesRequiringCharges, modulesWithOptionalCharges)


def FindModulesThatCannotBeFilled(dogmaStaticMgr, allChargesLeftInHolds, modulesWithoutCharges):
    usedWithGroupings = GetGroupsDict(dogmaStaticMgr, allChargesLeftInHolds, modulesWithoutCharges)
    modulesThatCannotBeFilled = []
    for chargeAndCap, moduleList in usedWithGroupings.iteritems():
        chargeTypeIDs, moduleCapacity = chargeAndCap
        numModulesLeftToFill = len(moduleList)
        for chargeTypeID in chargeTypeIDs:
            chargeVolume = dogmaStaticMgr.GetTypeAttribute(chargeTypeID, appConst.attributeVolume)
            qtyForFull = int(moduleCapacity / chargeVolume)
            numChargesInHold = allChargesLeftInHolds.get(chargeTypeID, 0)
            numberOfRounds = int(numChargesInHold / qtyForFull)
            numModulesLeftToFill -= numberOfRounds
            if numModulesLeftToFill <= 0:
                break
        else:
            modulesThatCannotBeFilled += moduleList

    return modulesThatCannotBeFilled


def GetGroupsDict(dogmaStaticMgr, allChargesLeftInHolds, modulesWithoutCharges):
    infoSvc = sm.GetService('info')
    usedWithGroupings = defaultdict(list)
    allChargeTypesLeft = allChargesLeftInHolds.keys()
    for typeID, flagID in modulesWithoutCharges:
        chargeTypeIDs = _GetUsedWithTuple(infoSvc, typeID, allChargeTypesLeft)
        if chargeTypeIDs is None:
            continue
        capacity = dogmaStaticMgr.GetTypeAttribute(typeID, appConst.attributeCapacity)
        usedWithGroupings[chargeTypeIDs, capacity].append((typeID, flagID))

    return usedWithGroupings


def _GetAllChargesInHolds(chargesInFlags):
    allChargesInCargoOrAmmoHold = defaultdict(int)
    for flagID, chargeInfo in chargesInFlags.iteritems():
        if flagID in (appConst.flagCargo, appConst.flagSpecializedAmmoHold):
            for chargeTypeID, chargeQty in chargeInfo:
                allChargesInCargoOrAmmoHold[chargeTypeID] += chargeQty

    return allChargesInCargoOrAmmoHold


@Memoize
def _GetUsedWithTuple(infoSvc, eachModuleTypeID, allChargeTypesLeft):
    allChargeTypesLeft = allChargeTypesLeft or ()
    chargeTypeIDs = infoSvc.GetUsedWithTypeIDs(eachModuleTypeID)
    if chargeTypeIDs is None:
        return
    chargeTypeIDs = {x for x in chargeTypeIDs if x in allChargeTypesLeft}
    return tuple(sorted(chargeTypeIDs))
