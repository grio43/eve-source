#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\provider.py
from eve.common.script.sys.idCheckers import IsSolarSystem
from metadata.common.content_tags import ContentTags
import threadutils
import gametime
from jobboard.client import job_board_signals
from jobboard.client.feature_flag import are_dungeons_in_job_board_available
from jobboard.client.features.dungeons.job import DungeonJob
from jobboard.client.job_provider import JobProvider
from jobboard.client.util import get_instance_id_from_job_id

class BaseDungeonsProvider(JobProvider):
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_dungeons]
    JOB_CLASS = DungeonJob
    __notifyevents__ = ['OnDungeonEntered', 'OnDungeonExited', 'OnDungeonCompleted']

    def __init__(self, *args, **kwargs):
        self._force_tracked = None
        super(BaseDungeonsProvider, self).__init__(*args, **kwargs)

    def _refresh_on_init(self):
        refreshed = super(BaseDungeonsProvider, self)._refresh_on_init()
        if refreshed:
            current_dungeon = sm.GetService('dungeonTracking').current_dungeon
            if current_dungeon:
                self.OnDungeonEntered(current_dungeon.dungeon_id, current_dungeon.instance_id)
        return refreshed

    def _should_refresh_on_init(self):
        result = super(BaseDungeonsProvider, self)._should_refresh_on_init()
        if result:
            return True
        current_dungeon = sm.GetService('dungeonTracking').current_dungeon
        if current_dungeon and self._is_site_relevant(current_dungeon.archetype_id, current_dungeon.entry_type_id):
            return True
        return False

    def _is_site_relevant(self, archetype_id, entry_type_id):
        return False

    def _register_availability(self):
        job_board_signals.on_dungeons_feature_availability_changed.connect(self._on_availability_changed)

    def _unregister_availability(self):
        job_board_signals.on_dungeons_feature_availability_changed.disconnect(self._on_availability_changed)

    def _should_enable(self):
        return are_dungeons_in_job_board_available()

    def _on_availability_changed(self, _old_value, _new_value):
        self._update_provider_state(self._should_enable())

    def OnDungeonCompleted(self, dungeon_id):
        current_dungeon = sm.GetService('dungeonTracking').current_dungeon
        if not current_dungeon:
            return
        job_id = self.get_job_id(current_dungeon.instance_id)
        job = self._jobs.get(job_id, None)
        if job and not job.is_completed:
            job.is_completed = True

    @threadutils.threaded
    def OnDungeonEntered(self, _dungeon_id, instance_id):
        current_dungeon = sm.GetService('dungeonTracking').current_dungeon
        if not current_dungeon or not self._is_site_relevant(current_dungeon.archetype_id, current_dungeon.entry_type_id):
            return
        job_id = self.get_job_id(instance_id)
        job = self.try_fetch_job(job_id)
        if not job:
            return
        job.update()
        job_board_signals.on_job_state_changed(job)
        if job.active_dungeon_objective_chain:
            if not job.is_tracked:
                self._force_tracked = True
            self.add_tracked_job(job, set_expanded=True)

    def OnDungeonExited(self, _dungeon_id, instance_id):
        job_id = self.get_job_id(instance_id)
        job = self._jobs.get(job_id, None)
        if not job:
            return
        if instance_id is None:
            self._remove_job(job_id)
        else:
            if self._force_tracked or job.is_completed:
                self.remove_tracked_job(job)
            job.update()
            job_board_signals.on_job_state_changed(job)
        self._force_tracked = None

    def _get_instance_id(self, dungeon):
        return dungeon['instance_id']

    def _get_all_content(self):
        return []

    def _construct_job(self, job_id, dungeon):
        return self.JOB_CLASS(job_id, self, dungeon)


class AnomaliesProvider(BaseDungeonsProvider):
    DUNGEON_TRACKER_ID = None
    JUMPS_WHERE_DUNGEONS_ARE_ALWAYS_VISIBLE = 2
    JUMPS_WHERE_DUNGEONS_CAN_BE_VISIBLE = 5
    MAXIMUM_SOLAR_SYSTEMS_WHERE_DUNGEONS_CAN_BE_VISIBLE = 20
    INCLUDE_SYSTEMS_IN_ROUTE = True
    __notifyevents__ = BaseDungeonsProvider.__notifyevents__ + ['OnClientEvent_DestinationSet', 'OnAutopilotUpdated', 'OnDestinationCleared']

    def __init__(self, *args, **kwargs):
        self._tracker = sm.GetService('dungeonTracking').get_tracker(self.DUNGEON_TRACKER_ID)
        self._sites_by_system = {}
        super(AnomaliesProvider, self).__init__(*args, **kwargs)

    def _register_slots(self):
        super(AnomaliesProvider, self)._register_slots()
        self._tracker.on_sites_updated.connect(self._on_sites_updated)
        self._tracker.on_sites_invalidated.connect(self._on_sites_invalidated)

    def _unregister_slots(self):
        super(AnomaliesProvider, self)._unregister_slots()
        self._tracker.on_sites_updated.disconnect(self._on_sites_updated)
        self._tracker.on_sites_invalidated.disconnect(self._on_sites_invalidated)

    def try_fetch_job(self, job_id):
        job = super(AnomaliesProvider, self).try_fetch_job(job_id)
        if job:
            return job
        current_dungeon = sm.GetService('dungeonTracking').current_dungeon
        if current_dungeon and current_dungeon.objective_chain and self._is_site_relevant(current_dungeon.archetype_id, current_dungeon.entry_type_id):
            job = self._create_job(self._construct_dungeon_info(session.solarsystemid2, {'dungeonID': current_dungeon.dungeon_id,
             'instanceID': current_dungeon.instance_id}))
            return job

    def _is_site_relevant(self, archetype_id, entry_type_id):
        return self._tracker.is_site_relevant(archetype_id, entry_type_id)

    def _get_relevant_solar_systems(self):
        solar_systems_within_jump_range = self._get_solar_systems_within_jump_range()
        solar_systems_on_route = self._get_solar_systems_on_route()
        relevant_solar_systems = solar_systems_within_jump_range.union(solar_systems_on_route)
        relevant_solar_systems.add(session.solarsystemid2)
        if self.INCLUDE_SYSTEMS_IN_ROUTE:
            for job_id in self.get_tracked_job_ids():
                if job_id not in self._jobs:
                    continue
                relevant_solar_systems.add(self._jobs[job_id].solar_system_id)

        return relevant_solar_systems

    def _get_solar_systems_within_jump_range(self):
        relevant_solar_system_ids = set()
        current_solar_system_id = session.solarsystemid2
        pathfinder_service = sm.GetService('clientPathfinderService')
        systems_within_range = pathfinder_service.GetSystemsWithinAutopilotJumpRange(fromID=current_solar_system_id, jumpCountMin=0, jumpCountMax=self.JUMPS_WHERE_DUNGEONS_CAN_BE_VISIBLE + 1)
        for jumps, solar_system_ids in systems_within_range.iteritems():
            if jumps == 0:
                continue
            for solar_system_id in solar_system_ids:
                if solar_system_id in self._sites_by_system:
                    relevant_solar_system_ids.add(solar_system_id)

            if jumps >= self.JUMPS_WHERE_DUNGEONS_ARE_ALWAYS_VISIBLE and len(relevant_solar_system_ids) >= self.MAXIMUM_SOLAR_SYSTEMS_WHERE_DUNGEONS_CAN_BE_VISIBLE:
                break

        return relevant_solar_system_ids

    def _get_solar_systems_on_route(self):
        relevant_solar_system_ids = set()
        if not self.INCLUDE_SYSTEMS_IN_ROUTE:
            return relevant_solar_system_ids
        route = sm.GetService('starmap').GetAutopilotRoute() or []
        for location_id in route:
            if IsSolarSystem(location_id) and location_id in self._sites_by_system:
                relevant_solar_system_ids.add(location_id)

        return relevant_solar_system_ids

    def OnClientEvent_DestinationSet(self, destination_id):
        if self.INCLUDE_SYSTEMS_IN_ROUTE:
            self._invalidate_cache()

    def OnAutopilotUpdated(self):
        if self.INCLUDE_SYSTEMS_IN_ROUTE:
            self._invalidate_cache()

    def OnDestinationCleared(self):
        if self.INCLUDE_SYSTEMS_IN_ROUTE:
            self._invalidate_cache()

    def _on_sites_updated(self):
        self._invalidate_cache()

    def _on_sites_invalidated(self):
        self._invalidate_cache()

    def get_sites_by_system(self):
        return self._tracker.get_sites()

    def _get_all_content(self):
        result = []
        self._sites_by_system = dungeons_by_solar_system = self.get_sites_by_system()
        if not self._sites_by_system:
            return result
        tracked_instance_ids = set()
        if self.INCLUDE_SYSTEMS_IN_ROUTE:
            for job_id, track_time in self.get_tracked_job_ids().iteritems():
                if not track_time or gametime.GetDaysSinceWallclockTime(track_time) >= 1:
                    continue
                try:
                    tracked_instance_ids.add(int(get_instance_id_from_job_id(job_id)))
                except:
                    pass

        relevant_solar_system_ids = self._get_relevant_solar_systems()
        for solar_system_id in relevant_solar_system_ids:
            if solar_system_id not in dungeons_by_solar_system:
                continue
            dungeons_in_solar_system = dungeons_by_solar_system[solar_system_id]
            for dungeon in dungeons_in_solar_system:
                if dungeon is not None:
                    dungeon_info = self._construct_dungeon_info(solar_system_id, dungeon)
                    result.append(dungeon_info)
                    tracked_instance_ids.discard(dungeon_info['instance_id'])

        if tracked_instance_ids:
            for solar_system_id, dungeons in dungeons_by_solar_system.iteritems():
                if not tracked_instance_ids:
                    break
                for dungeon in dungeons:
                    if isinstance(dungeon, dict):
                        instance_id = dungeon.get('instanceID', dungeon.get('siteID'))
                    else:
                        instance_id = dungeon.instanceID
                    if instance_id not in tracked_instance_ids:
                        continue
                    dungeon_info = self._construct_dungeon_info(solar_system_id, dungeon)
                    result.append(dungeon_info)
                    tracked_instance_ids.discard(instance_id)
                    if not tracked_instance_ids:
                        break

        return result

    def _construct_dungeon_info(self, solar_system_id, dungeon_entry):
        result = {'solar_system_id': solar_system_id,
         'scan_result': None}
        if isinstance(dungeon_entry, dict):
            result['dungeon_id'] = dungeon_entry['dungeonID']
            result['instance_id'] = dungeon_entry.get('instanceID', dungeon_entry.get('siteID'))
        else:
            result['dungeon_id'] = dungeon_entry.dungeonID
            result['instance_id'] = dungeon_entry.instanceID
            if solar_system_id == session.solarsystemid2:
                scan_result = sm.GetService('sensorSuite').GetAnomaly(result['instance_id'])
                result['scan_result'] = scan_result
        return result
