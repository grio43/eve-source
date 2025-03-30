#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\warpSites.py
import operationsSiteCache
from operations.common.const import SiteSpawningType
_operationSites = None

def GetOperationSites():
    global _operationSites
    if _operationSites is None:
        _operationSites = operationsSiteCache.OperationSiteCache()
    return _operationSites


class AuthoringException(BaseException):
    pass


def GetDungeonIDForSite(siteID, raceID):
    operationSite = GetOperationSites().get_site_by_id(siteID)
    if operationSite.raceToDungeonMap:
        return operationSite.raceToDungeonMap[raceID]


def GetSiteByID(siteID):
    return GetOperationSites().get_site_by_id(siteID)


def GetSiteSpawnType(siteID):
    operationSite = GetOperationSites().get_site_by_id(siteID)
    return operationSite.spawning


def CanWarpToSite(siteID, schoolID, solarSystemID):
    site = GetOperationSites().get_site_by_id(siteID)
    if site.spawning == SiteSpawningType.IN_SCHOOL_STARTING_SYSTEM:
        return solarSystemID == GetSolarsystemIDFromSchool(schoolID)
    return True


def ShouldSiteSpawnImmediately(siteID):
    operationSite = GetOperationSites().get_site_by_id(siteID)
    return operationSite.shouldSpawn


def GetAllSiteIDs():
    return GetOperationSites().get_all_operation_sites().keys()


def GetSolarsystemIDFromSchool(schoolID):
    try:
        systemID = GetOperationSites().get_solarsystem_id_from_school(schoolID)
        return systemID
    except KeyError:
        raise AuthoringException('Solar system ID for school ID %d has not yet been authored', schoolID)
