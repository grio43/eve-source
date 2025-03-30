#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evePathfinder\eveMapWrapper.py
import pyEvePathfinder
import six
from evePathfinder.core import EvePathfinderCore
from threadutils import be_nice

class EveMapWrapper(object):

    def __init__(self):
        self._eve_map = pyEvePathfinder.EveMap()

    @property
    def map(self):
        return self._eve_map

    def add_regions(self, map_region_cache):
        for region_id, regionItem in six.iteritems(map_region_cache):
            self.add_region(region_id)
            for constellation_id in regionItem.constellationIDs:
                self.add_constellation(constellation_id, region_id)
                be_nice()

    def add_solar_systems(self, map_system_cache, get_security_level_func):
        for solar_system_id, system_info in six.iteritems(map_system_cache):
            security_level = get_security_level_func(solar_system_id)
            self.add_solar_system(solar_system_id, system_info.constellationID, security_level)
            be_nice()

    def add_jump_cache_jumps(self, jump_cache, ignored_stargate_ids = ()):
        for jump in jump_cache:
            if jump.stargateID not in ignored_stargate_ids:
                self.add_jump(jump.fromSystemID, jump.toSystemID)
                self.add_jump(jump.toSystemID, jump.fromSystemID)
            be_nice()

    def add_one_way_jumps(self, one_way_jump_tuples):
        for jump_tuple in one_way_jump_tuples:
            from_solar_system_id = jump_tuple[0]
            to_solar_system_id = jump_tuple[1]
            self.add_jump(from_solar_system_id, to_solar_system_id)
            be_nice()

    def add_region(self, region_id):
        self._eve_map.CreateRegion(region_id)

    def add_constellation(self, constellation_id, region_id):
        self._eve_map.CreateConstellation(constellation_id, region_id)

    def add_solar_system(self, solar_system_id, constellation_id, security_level):
        self._eve_map.CreateSolarSystem(solar_system_id, constellation_id, security_level)

    def add_jump(self, from_solar_system_id, to_solar_system_id):
        self._eve_map.AddJump(from_solar_system_id, to_solar_system_id, 0)

    def set_solar_system_security(self, solar_system_id, security_level):
        self._eve_map.SetSolarSystemSecurity(solar_system_id, security_level)

    def finalize(self):
        self._eve_map.Finalize()

    def create_core(self):
        return EvePathfinderCore(self._eve_map)
