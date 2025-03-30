#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\client\UI\operationDestinationController.py
from operations.common.const import SiteSpawningType
from operations.common import warpSites as warpSiteTools
from caching.memoize import Memoize

@Memoize
def GetSchoolID(charID):
    characterMgr = sm.RemoteSvc('charMgr')
    charinfo = characterMgr.GetPublicInfo(charID)
    schoolID = charinfo.schoolID
    return schoolID


@Memoize
def GetSiteSolarSystem(charID, siteID):
    spawnType = warpSiteTools.GetSiteSpawnType(siteID)
    if spawnType == SiteSpawningType.IN_SCHOOL_STARTING_SYSTEM:
        schoolID = GetSchoolID(charID)
        return warpSiteTools.GetSolarsystemIDFromSchool(schoolID)
    solarSystemID = sm.RemoteSvc('keeper').GetOperationSpawnpointSolarSystem(charID, siteID)
    return solarSystemID
