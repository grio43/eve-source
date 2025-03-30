#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\factional_warfare_enlistment\provider.py
from eve.common.lib import appConst
from metadata.common.content_tags import ContentTags
from jobboard.client.job_provider import JobProvider
from jobboard.client.provider_type import ProviderType
from .job import FactionalWarfareEnlistmentJob
from jobboard.client import job_board_signals

class FactionalWarfareEnlistmentProvider(JobProvider):
    PROVIDER_ID = ProviderType.FACTIONAL_WARFARE_ENLISTMENT
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_factional_warfare, ContentTags.feature_pirate_insurgencies]
    JOB_CLASS = FactionalWarfareEnlistmentJob
    __notifyevents__ = ['OnEnlistmentStateUpdated_Local']

    def OnEnlistmentStateUpdated_Local(self, *args, **kwargs):
        tracked_jobs = self.get_tracked_jobs()
        for job in tracked_jobs:
            if job.is_completed:
                job_board_signals.on_job_completed(job)
            self.remove_tracked_job(job)

        job_board_signals.on_job_provider_state_changed(self)

    def _get_all_content(self):
        return [appConst.factionCaldariState,
         appConst.factionGallenteFederation,
         appConst.factionMinmatarRepublic,
         appConst.factionAmarrEmpire,
         appConst.factionAngelCartel,
         appConst.factionGuristasPirates]

    def _get_instance_id(self, faction_id):
        return faction_id

    def _construct_job(self, job_id, faction_id):
        return self.JOB_CLASS(job_id, self, faction_id)

    def toggle_tracked_job_by_player(self, job):
        tracked_job_ids = self.get_tracked_job_ids()
        if tracked_job_ids and job.job_id not in tracked_job_ids:
            for tracked_job_id in tracked_job_ids.keys():
                tracked_job = self.get_job(tracked_job_id)
                if tracked_job:
                    super(FactionalWarfareEnlistmentProvider, self).toggle_tracked_job_by_player(tracked_job)

        super(FactionalWarfareEnlistmentProvider, self).toggle_tracked_job_by_player(job)
