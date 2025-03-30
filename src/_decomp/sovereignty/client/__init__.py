#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\client\__init__.py
from caching import Memoize

@Memoize
def get_sov_region_ids():
    from eve.common.script.sys.idCheckers import IsKnownSpaceSystem
    region_ids = set()
    faction_service = sm.GetService('faction')
    for system_id, system in cfg.mapSystemCache.iteritems():
        if IsKnownSpaceSystem(system_id) and faction_service.GetFactionOfSolarSystem(system_id) is None:
            region_ids.add(system.regionID)

    return frozenset(region_ids)


@Memoize
def get_sov_system_ids():
    from eve.common.script.sys.idCheckers import IsKnownSpaceSystem
    faction_service = sm.GetService('faction')
    return frozenset([ system_id for system_id, system in cfg.mapSystemCache.iteritems() if IsKnownSpaceSystem(system_id) and faction_service.GetFactionOfSolarSystem(system_id) is None ])
