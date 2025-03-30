#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\world_events\provider.py
from taleclient.tale_service import on_active_tale_added, on_active_tale_updated, on_active_tale_removed
from metadata.common.content_tags import ContentTags
from jobboard.client.job_provider import JobProvider
from jobboard.client.provider_type import ProviderType
from .feature_page import WorldEventsFeaturePage
from .job import WorldEventJob

class WorldEventsProvider(JobProvider):
    PROVIDER_ID = ProviderType.WORLD_EVENTS
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_world_events]
    FEATURE_PAGE_CLASS = WorldEventsFeaturePage
    __notifyevents__ = ['OnSessionChanged']

    def OnSessionChanged(self, _is_remote, _session, change):
        if 'locationid' in change:
            self._invalidate_cache()

    def _should_refresh_on_window_initializing(self):
        return not self.is_hidden

    def _should_refresh_on_window_maximized(self):
        return not self.is_hidden

    def _get_instance_id(self, tale_info):
        return tale_info['taleID']

    def _get_all_content(self):
        service = sm.GetService('tale')
        active_tales = service.get_active_world_event_tales()
        active_tale_ids = [ tale.tale_id for tale in active_tales ]
        global_world_event_tales = service.get_global_world_event_tales()
        result = {}
        for tale_info in global_world_event_tales:
            tale_id = tale_info['taleID']
            if tale_info['managerSolarSystemID'] == session.solarsystemid2:
                if tale_id not in active_tale_ids:
                    continue
            result[tale_id] = tale_info

        for active_tale in active_tales:
            result[active_tale.tale_id] = _details_from_active_tale(active_tale)

        return result.values()

    def _construct_job(self, job_id, tale_info):
        return WorldEventJob(job_id, self, tale_info)

    def _register_slots(self):
        super(WorldEventsProvider, self)._register_slots()
        on_active_tale_added.connect(self._on_active_tale_added)
        on_active_tale_updated.connect(self._on_active_tale_updated)
        on_active_tale_removed.connect(self._on_active_tale_removed)

    def _unregister_slots(self):
        super(WorldEventsProvider, self)._unregister_slots()
        on_active_tale_added.disconnect(self._on_active_tale_added)
        on_active_tale_updated.disconnect(self._on_active_tale_updated)
        on_active_tale_removed.disconnect(self._on_active_tale_removed)

    def _on_active_tale_added(self, tale_id):
        self._update_active_tale_job(tale_id)

    def _on_active_tale_updated(self, tale_id):
        self._update_active_tale_job(tale_id)

    def _on_active_tale_removed(self, tale_id):
        job_id = self.get_job_id(tale_id)
        self._remove_job(job_id)

    def _update_active_tale_job(self, tale_id):
        active_tale = sm.GetService('tale').get_active_tale(tale_id)
        if not active_tale:
            return
        job_id = self.get_job_id(tale_id)
        job = self.get_job(job_id)
        details = _details_from_active_tale(active_tale)
        if job:
            job.update(details)
        else:
            self._create_job(details)


def _details_from_active_tale(active_tale):
    return {'taleID': active_tale.tale_id,
     'templateID': active_tale.template_id,
     'managerSolarSystemID': active_tale.manager_solar_system_id,
     'influence': active_tale.influence,
     'templateNameID': active_tale.title_id,
     'templateDescriptionID': active_tale.description_id,
     'endTime': active_tale.end_time,
     'aggressorFactionID': active_tale.aggressor_faction_id}
