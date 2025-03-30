#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\escalation_sites\provider.py
import uthread2
from eve.common.lib.appConst import dunArchetypeEscalatingPathDungeons
from metadata.common.content_tags import ContentTags
from jobboard.client import job_board_signals
from jobboard.client.features.dungeons.escalation_sites.job import EscalationSiteJob
from jobboard.client.features.dungeons.provider import BaseDungeonsProvider
from jobboard.client.feature_flag import are_escalation_sites_in_job_board_available
from jobboard.client.provider_type import ProviderType
REFRESH_BUFFER_MSEC = 3000

class EscalationSitesProvider(BaseDungeonsProvider):
    PROVIDER_ID = ProviderType.ESCALATION_SITES
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_escalation_dungeon] + BaseDungeonsProvider.PROVIDER_CONTENT_TAGS
    JOB_CLASS = EscalationSiteJob
    __notifyevents__ = BaseDungeonsProvider.__notifyevents__ + ['OnEscalatingPathMessage', 'OnEscalationsDataUpdated']

    def __init__(self, *args, **kwargs):
        self.instance_ids_to_update = set()
        super(EscalationSitesProvider, self).__init__(*args, **kwargs)

    def OnDungeonExited(self, _dungeon_id, instance_id):
        job_id = self.get_job_id(instance_id)
        job = self.get_job(job_id)
        if job:
            self.refresh_jobs()
        else:
            super(EscalationSitesProvider, self).OnDungeonExited(_dungeon_id, instance_id)

    def OnEscalatingPathMessage(self, instance_id):
        self.instance_ids_to_update.add(instance_id)
        self.refresh_jobs()

    def OnEscalationsDataUpdated(self):
        self.refresh_jobs()

    @uthread2.BufferedCall(delay=REFRESH_BUFFER_MSEC)
    def refresh_jobs(self):
        super(EscalationSitesProvider, self).refresh_jobs()

    def _on_jobs_refreshed(self):
        super(EscalationSitesProvider, self)._on_jobs_refreshed()
        for instance_id in self.instance_ids_to_update:
            job_id = self.get_job_id(instance_id)
            job = self.get_job(job_id)
            if not job:
                continue
            job_board_signals.on_job_state_changed(job)
            if job.is_trackable and not job.is_tracked:
                self.add_tracked_job(job, set_expanded=True)

        self.instance_ids_to_update.clear()

    def _remove_job(self, job_id):
        job = self.get_job(job_id)
        if job:
            current_dungeon = sm.GetService('dungeonTracking').current_dungeon
            if current_dungeon and job.instance_id == current_dungeon.instance_id:
                return
        super(EscalationSitesProvider, self)._remove_job(job_id)

    def _get_all_content(self):
        return [ self._construct_escalation_info(escalation) for escalation in sm.GetService('journal').GetEscalations() if escalation.destDungeon ]

    def _construct_escalation_info(self, escalation):
        return {'dungeon_id': escalation.dungeon.destDungeonID,
         'instance_id': escalation.dungeon.instanceID,
         'solar_system_id': escalation.dungeon.solarSystemID,
         'expiration_time': escalation.expiryTime,
         'transmission_description_id': escalation.journalEntryTemplateID}

    def _register_availability(self):
        super(EscalationSitesProvider, self)._register_availability()
        job_board_signals.on_escalation_sites_feature_availability_changed.connect(self._on_availability_changed)

    def _unregister_availability(self):
        super(EscalationSitesProvider, self)._unregister_availability()
        job_board_signals.on_escalation_sites_feature_availability_changed.disconnect(self._on_availability_changed)

    def _should_enable(self):
        return super(EscalationSitesProvider, self)._should_enable() and are_escalation_sites_in_job_board_available()

    def _is_site_relevant(self, archetype_id, entry_type_id):
        return self._is_archetype_relevant(archetype_id)

    def _is_archetype_relevant(self, archetype_id):
        return archetype_id == dunArchetypeEscalatingPathDungeons
