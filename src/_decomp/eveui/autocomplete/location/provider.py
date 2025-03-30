#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\location\provider.py
import threadutils
import localization
from carbon.common.script.util.commonutils import StripTags
from eve.common.script.sys import idCheckers
from eveui.autocomplete.provider import NameCache, NameCacheProvider
from eveui.autocomplete.location.suggestion import LocationSuggestion

class RegionProvider(NameCacheProvider):

    def __init__(self, filter = None):
        super(RegionProvider, self).__init__(cache=RegionNameCache.instance(), suggestion_type=LocationSuggestion, filter=filter)


class RegionNameCache(NameCache):

    def prime(self):
        cache = {}
        for location_id in cfg.mapRegionCache:
            if idCheckers.IsKnownSpaceRegion(location_id):
                info = cfg.mapRegionCache.Get(location_id)
                name = localization.GetByMessageID(info.nameID, important=False)
                cache[location_id] = name
            threadutils.BeNice(5)

        return cache


class ConstellationProvider(NameCacheProvider):

    def __init__(self, filter = None):
        super(ConstellationProvider, self).__init__(cache=ConstellationNameCache.instance(), suggestion_type=LocationSuggestion, filter=filter)


class ConstellationNameCache(NameCache):

    def prime(self):
        cache = {}
        for location_id in cfg.mapConstellationCache:
            if idCheckers.IsKnownSpaceConstellation(location_id):
                info = cfg.mapConstellationCache.Get(location_id)
                name = localization.GetByMessageID(info.nameID, important=False)
                cache[location_id] = name
            threadutils.BeNice(5)

        return cache


class SolarSystemProvider(NameCacheProvider):

    def __init__(self, filter = None):
        super(SolarSystemProvider, self).__init__(cache=SolarSystemNameCache.instance(), suggestion_type=LocationSuggestion, filter=filter)


class SolarSystemNameCache(NameCache):

    def prime(self):
        cache = {}
        for location_id in cfg.mapSystemCache:
            if not (idCheckers.IsVoidSpaceSystem(location_id) or idCheckers.IsAbyssalSpaceSystem(location_id)):
                solar_system = cfg.mapSystemCache.Get(location_id)
                name = localization.GetByMessageID(solar_system.nameID, important=False)
                cache[location_id] = name
            threadutils.BeNice(5)

        return cache


class StationProvider(NameCacheProvider):

    def __init__(self, filter = None):
        super(StationProvider, self).__init__(cache=StationNameCache.instance(), suggestion_type=LocationSuggestion, filter=filter)


class StationNameCache(NameCache):

    def prime(self):
        cache = {}
        for station in cfg.stations:
            info = cfg.evelocations.Get(station.stationID)
            cache[station.stationID] = StripTags(info.locationName)
            threadutils.BeNice(5)

        return cache
