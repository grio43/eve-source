#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\voidspace\common\__init__.py
from caching import Memoize
VOID_SPACE_REGIONS = [14000001,
 14000002,
 14000003,
 14000004,
 14000005]

@Memoize
def get_all_void_system_ids():
    system_ids = []
    for region_id in VOID_SPACE_REGIONS:
        region = cfg.mapRegionCache[region_id]
        for constellation_id in region.constellationIDs:
            constellation = cfg.mapConstellationCache[constellation_id]
            for solar_system_id in constellation.solarSystemIDs:
                system_ids.append(solar_system_id)

    return system_ids
