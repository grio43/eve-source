#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\anomalyTracker.py
import gametime
from carbon.common.script.util.timerstuff import AutoTimer
from collections import defaultdict
from evedungeons.client.data import GetDungeon
from eve.common.lib.appConst import dunArchetypeOreAnomaly, dunArchetypeCombatSites, dunArchetypesFactionalWarfare, dunArchetypeHomefrontSites, dunArchetypeIceBelt, dunArchetypesInsurgencySites, dunArchetypeInvasionSites
from eve.common.script.sys.eveCfg import IsDocked
from eve.common.script.sys.idCheckers import IsTriglavianSystem
from inventorycommon.const import typeCosmicAnomaly
from logging import getLogger
import signals
import uthread2
logger = getLogger(__name__)
UNKNOWN_DUNGEON = None

class BaseCosmicAnomalyTracker(object):
    __notifyevents__ = ['OnSessionChanged']
    CLEAR_TIMER_MSEC = 600000
    ARCHETYPE_IDS = set()

    def __init__(self):
        self._sites = {}
        self._is_dirty = True
        self._fetch_time = 0
        self.on_sites_updated = signals.Signal('on_sites_updated')
        self.on_sites_invalidated = signals.Signal('on_sites_invalidated')
        self._are_local_sites_updated = False
        self.timer = None

    def initialize(self):
        sm.RegisterNotify(self)

    def get_sites(self):
        while self._fetch_time:
            uthread2.Yield()
            if gametime.GetSecondsSinceWallclockTime(self._fetch_time) >= 5:
                self._fetch_time = 0

        if self._is_dirty:
            self._is_dirty = False
            self._reset_timer()
            self._fetch_time = gametime.GetWallclockTime()
            try:
                logger.info('Fetching sites %s' % self.__class__.__name__)
                sites_from_server = self._fetch_sites_from_server()
            except:
                logger.exception('Failed to fetch sites %s' % self.__class__.__name__)
                sites_from_server = {}

            unpacked_sites = self._unpack(sites_from_server)
            current_solar_system_id = session.solarsystemid2
            if self._are_local_sites_updated:
                unpacked_sites[current_solar_system_id] = self._sites.get(current_solar_system_id, [])
            elif current_solar_system_id not in unpacked_sites:
                unpacked_sites[current_solar_system_id] = []
            self._sites = unpacked_sites
            if IsDocked():
                sm.GetService('sensorSuite').FullyUpdateSignalTrackerDebounced()
            self._fetch_time = 0
        return self._sites or {}

    def _reset_timer(self):
        if self.timer:
            self.timer.KillTimer()
            self.timer = None
        self.timer = AutoTimer(self.CLEAR_TIMER_MSEC, self._invalidate_cache)

    def _invalidate_cache(self):
        if self._is_dirty:
            return
        self._set_dirty()
        self.on_sites_invalidated()

    def OnSessionChanged(self, _is_remote, _session, change):
        if 'locationid' in change:
            self._are_local_sites_updated = False
            if IsDocked():
                self._invalidate_cache()
            else:
                self._set_dirty()

    def scan_results_updated(self, *args, **kwargs):
        changed = self._update_local_sites()
        if changed:
            self.on_sites_updated()

    def _set_dirty(self):
        self._is_dirty = True

    def _update_local_sites(self):
        sensorSuiteSvc = sm.GetService('sensorSuite')
        local_sites = sensorSuiteSvc.GetAnomalies()
        new_sites = [ site for site in local_sites if self._is_site_relevant_by_dungeon_id(site.dungeonID) ]
        if new_sites != self._sites.get(session.solarsystemid2, None):
            self._sites[session.solarsystemid2] = new_sites
            self._are_local_sites_updated = True
            return True
        else:
            return False

    def _unpack(self, instances):
        unpacked = defaultdict(list)
        for solar_system_id, dungeons in instances.iteritems():
            if isinstance(dungeons, int):
                unpacked[solar_system_id] = [UNKNOWN_DUNGEON] * dungeons
            else:
                unpacked[solar_system_id] = dungeons

        return unpacked

    def _get_cached_site(self, solar_system_id, instance_id):
        if solar_system_id in self._sites:
            for site in self._sites[solar_system_id]:
                if site is None:
                    continue
                if site.instanceID == instance_id:
                    return site

    def _is_site_cached(self, solar_system_id, instance_id):
        site = self._get_cached_site(solar_system_id, instance_id)
        return bool(site)

    def _fetch_sites_from_server(self):
        raise NotImplementedError('Must implement _fetch_sites_from_server in derived class')

    def _is_site_relevant_by_dungeon_id(self, dungeon_id):
        dungeon = GetDungeon(dungeon_id)
        if not dungeon:
            return False
        return self.is_site_relevant(dungeon.archetypeID, dungeon.entryTypeID)

    def is_site_relevant(self, archetype_id, entry_type_id):
        return entry_type_id == typeCosmicAnomaly and archetype_id in self.ARCHETYPE_IDS


class UnknownCosmicAnomalyTracker(BaseCosmicAnomalyTracker):

    def __init__(self):
        self._unknown_sites = {}
        self._is_unknown_dirty = True
        self._fetch_time_unknown = 0
        super(UnknownCosmicAnomalyTracker, self).__init__()

    def _set_dirty(self):
        super(UnknownCosmicAnomalyTracker, self)._set_dirty()
        self._is_unknown_dirty = True

    def get_unknown_sites(self):
        while self._fetch_time_unknown:
            uthread2.Yield()
            if gametime.GetSecondsSinceWallclockTime(self._fetch_time_unknown) >= 5:
                self._fetch_time_unknown = 0

        if self._is_unknown_dirty:
            self._is_unknown_dirty = False
            self._fetch_time_unknown = gametime.GetWallclockTime()
            try:
                logger.info('Fetching unknown sites %s' % self.__class__.__name__)
                sites_from_server = self._fetch_unknown_sites_from_server()
            except:
                logger.exception('Failed to fetch unknown sites %s' % self.__class__.__name__)
                sites_from_server = {}

            self._unknown_sites = self._unpack(sites_from_server)
            self._fetch_time_unknown = 0
        return self._unknown_sites or {}

    def _fetch_unknown_sites_from_server(self):
        raise NotImplementedError('Must implement _fetch_unknown_sites_from_server in derived class')


class CombatAnomalyTracker(UnknownCosmicAnomalyTracker):
    ARCHETYPE_IDS = (dunArchetypeCombatSites,)

    def _fetch_sites_from_server(self):
        return sm.RemoteSvc('dungeonInstanceCacheMgr').GetCombatAnomalyInstances()

    def _fetch_unknown_sites_from_server(self):
        return sm.RemoteSvc('dungeonInstanceCacheMgr').GetCombatAnomaliesCount()


class IceBeltTracker(UnknownCosmicAnomalyTracker):
    ARCHETYPE_IDS = (dunArchetypeIceBelt,)

    def _fetch_sites_from_server(self):
        return sm.RemoteSvc('dungeonInstanceCacheMgr').GetIceBeltInstances()

    def _fetch_unknown_sites_from_server(self):
        return sm.RemoteSvc('dungeonInstanceCacheMgr').GetIceBeltsCount()


class OreAnomalyTracker(UnknownCosmicAnomalyTracker):
    ARCHETYPE_IDS = (dunArchetypeOreAnomaly,)

    def _fetch_sites_from_server(self):
        return sm.RemoteSvc('dungeonInstanceCacheMgr').GetOreAnomalyInstances()

    def _fetch_unknown_sites_from_server(self):
        return sm.RemoteSvc('dungeonInstanceCacheMgr').GetOreAnomaliesCount()


class FactionalWarfareSiteTracker(BaseCosmicAnomalyTracker):
    ARCHETYPE_IDS = dunArchetypesFactionalWarfare

    def _unpack(self, instances):
        fac_war_svc = sm.GetService('facwar')
        unpacked = defaultdict(list)
        for solar_system_id, dungeons in instances.iteritems():
            occupier_id = fac_war_svc.GetSystemOccupier(solar_system_id)
            if occupier_id is None:
                continue
            unpacked[solar_system_id] = [ dungeon for dungeon in dungeons if dungeon.factionID == occupier_id ]

        return unpacked

    def _fetch_sites_from_server(self):
        return sm.RemoteSvc('dungeonInstanceCacheMgr').GetFactionWarfareInstances()


class HomefrontOperationTracker(BaseCosmicAnomalyTracker):
    ARCHETYPE_IDS = (dunArchetypeHomefrontSites,)

    def _unpack(self, instances):
        return defaultdict(list, instances)

    def _fetch_sites_from_server(self):
        return sm.RemoteSvc('dungeonInstanceCacheMgr').GetHomefrontSiteInstances()


class PirateInsurgencySiteTracker(BaseCosmicAnomalyTracker):
    ARCHETYPE_IDS = dunArchetypesInsurgencySites

    def _unpack(self, instances):
        return defaultdict(list, instances)

    def _fetch_sites_from_server(self):
        return sm.RemoteSvc('dungeonInstanceCacheMgr').GetPirateInsurgencyInstances()


class TriglavianSiteTracker(BaseCosmicAnomalyTracker):
    CLEAR_TIMER_MSEC = 300000
    ARCHETYPE_IDS = (dunArchetypeInvasionSites,)

    def _unpack(self, instances):
        return defaultdict(list, instances)

    def _fetch_sites_from_server(self):
        if not IsTriglavianSystem(session.solarsystemid2):
            return {}
        return sm.RemoteSvc('dungeonInstanceCacheMgr').GetTriglavianSiteInstances()
