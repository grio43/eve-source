#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\dogma\clientDogmaUtilFunc.py
from eve.common.script.sys.idCheckers import IsSolarSystem
NOT_SPECIFIED = -1

def WasLaunchingDroneOrFighter(item, change, currentSolarsystemID):
    wasLaunching = WasLaunchingDrone(item, change, currentSolarsystemID) or WasLaunchingFighter(item, change, currentSolarsystemID)
    return wasLaunching


def WasLaunchingDrone(item, change, currentSolarsystemID):
    categoryToCheck = const.categoryDrone
    flagsToCheck = (const.flagDroneBay,)
    return _DroneOrFighterWasLaunched(item, change, categoryToCheck, flagsToCheck, currentSolarsystemID)


def WasLaunchingFighter(item, change, currentSolarsystemID):
    categoryToCheck = const.categoryFighter
    flagsToCheck = const.fighterTubeFlags
    return _DroneOrFighterWasLaunched(item, change, categoryToCheck, flagsToCheck, currentSolarsystemID)


def _DroneOrFighterWasLaunched(item, change, categoryToCheck, flagsToCheck, currentSolarsystemID):
    if item.categoryID != categoryToCheck:
        return False
    if item.locationID != currentSolarsystemID:
        return False
    if not IsSolarSystem(item.locationID):
        return False
    if const.ixLocationID not in change or change[const.ixLocationID] != session.shipid:
        return False
    if const.ixFlag not in change or change[const.ixFlag] not in flagsToCheck:
        return False
    return True
