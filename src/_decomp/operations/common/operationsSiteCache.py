#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\operationsSiteCache.py
from eve.common.lib.appConst import raceAmarr, raceMinmatar, raceGallente, raceCaldari
from operations.common.fsdloaders import OperationSitesLoader, OperationSchoolMapLoader

class OperationSite(object):

    def __init__(self, site):
        self.id = site.id
        self.developmentName = site.title
        self.title = site.name
        self.raceToDungeonMap = self.make_race_dungeon_dict(site.dungeonIDs)
        self.spawning = site.spawning
        self.shouldSpawn = site.shouldSpawn
        self.disableWarpToEntryPointRedirect = site.disableWarpToEntryPointRedirect

    def make_race_dungeon_dict(self, raceDungeonDict):
        raceIDDict = {raceAmarr: raceDungeonDict.amarr,
         raceCaldari: raceDungeonDict.caldari,
         raceGallente: raceDungeonDict.gallente,
         raceMinmatar: raceDungeonDict.minmatar}
        return raceIDDict


class OperationSiteCache(object):

    def __init__(self):
        self.operation_sites_data = None
        self.reload_fsd_data()

    def reload_fsd_data(self):
        self.operation_sites_data = self.load_operation_sites()

    def load_school_system_dictionary(self):
        schoolToStartingSystemDict = {}
        for connection in OperationSchoolMapLoader.GetConnections():
            schoolToStartingSystemDict[connection.schoolID] = connection.solarSystemID

        return schoolToStartingSystemDict

    def load_operation_sites(self):
        sitesByID = OperationSitesLoader.GetData()
        return dict(((siteId, OperationSite(site)) for siteId, site in sitesByID.iteritems()))

    def get_all_operation_sites(self):
        return self.operation_sites_data

    def get_solarsystem_id_from_school(self, schoolID):
        startInSystem = self.load_school_system_dictionary().get(schoolID, None)
        return startInSystem

    def get_site_by_id(self, siteID):
        return self.operation_sites_data[siteID]
