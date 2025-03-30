#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\abyss\const.py
from caching.memoize import Memoize
ABYSS_REGIONS = [12000001,
 12000002,
 12000003,
 12000004,
 12000005]
DEV_NAMES = ['Andre',
 'Ben',
 'Bergthor',
 'Bergur',
 'Carl',
 'Chance',
 'Chris',
 'Euan',
 'Freyr',
 'Georg',
 'Hafsteinn',
 'Hinrik',
 'Hooper',
 'Huni',
 'Javier',
 'Jonathan',
 'Kasper',
 'Kristinn',
 'Mark',
 'Norbert',
 'Olafur',
 'Scott',
 'Sergey',
 'Skuli',
 'Steve',
 'Steven',
 'Svanhvit',
 'Tormod',
 'Willem']
MAX_PLAYERS = 3
CRUISER_SOLO_CONTENT = 1
FRIGATE_FLEET_CONTENT = 2
CRUISER_PVP_CONTENT = 3
TWO_PLAYER_DESTROYERS = 4

@Memoize
def get_all_abyss_system_ids():
    system_ids = []
    for region_id in ABYSS_REGIONS:
        region = cfg.mapRegionCache[region_id]
        for constellation_id in region.constellationIDs:
            constellation = cfg.mapConstellationCache[constellation_id]
            for solarsystem_id in constellation.solarSystemIDs:
                system_ids.append(solarsystem_id)

    return system_ids
