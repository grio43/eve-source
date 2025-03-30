#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\mercenary_tactical_operations\provider.py
import logging
import threadutils
import uthread2
from eve.common.script.util import notificationconst
from evedungeons.common.instance_identifier import DungeonInstanceIdentifier
from jobboard.client import job_board_signals
from jobboard.client.features.mercenary_tactical_operations.job import MTOJob
from jobboard.client.job_provider import JobProvider
from jobboard.client.provider_type import ProviderType
from metadata.common.content_tags import ContentTags
from sovereignty.mercenaryden.client.feature_flag import is_contraband_mlp_version_enabled
from sovereignty.mercenaryden.client.mercenary_den_signals import on_start_activity_failed_unknown, on_activity_started_notice, on_activity_removed_notice, on_activity_completed_notice, on_activity_expiry_changed_notice, on_activity_added_notice, on_activities_loaded
from sovereignty.mercenaryden.client.repository import get_mercenary_den_repository
logger = logging.getLogger('mercenary_den')
REFRESH_DELAY = 5

class MTOJobProvider(JobProvider):
    PROVIDER_ID = ProviderType.MERCENARY_TACTICAL_OPS
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_mercenary_tactical_ops]
    __notifyevents__ = ['OnSubscriptionChanged_Local',
     'OnSkillsChanged',
     'OnDungeonEntered',
     'OnDungeonExited']

    def __init__(self, *args, **kwargs):
        super(MTOJobProvider, self).__init__(*args, **kwargs)

    def _should_enable(self):
        logger.info('MTO Provider enabled: %s', is_contraband_mlp_version_enabled())
        return is_contraband_mlp_version_enabled()

    def _should_refresh_on_window_initializing(self):
        return not self.is_hidden

    def _get_all_content(self):
        repository = get_mercenary_den_repository()
        return repository.get_all_mercenary_den_activities_for_character()

    def _construct_job(self, job_id, mto):
        return MTOJob(job_id, self, mto)

    def _get_instance_id(self, mto):
        return mto.id

    def _register_slots(self):
        super(MTOJobProvider, self)._register_slots()
        on_activity_added_notice.connect(self._on_activity_added)
        on_activity_removed_notice.connect(self._on_activity_removed)
        on_activity_completed_notice.connect(self._on_activity_completed)
        on_activity_expiry_changed_notice.connect(self._on_activity_expiry_changed)
        on_activity_started_notice.connect(self._on_activity_started)
        on_start_activity_failed_unknown.connect(self._on_start_activity_failed_unknown)
        on_activities_loaded.connect(self._on_activities_loaded)

    def _unregister_slots(self):
        super(MTOJobProvider, self)._unregister_slots()
        on_activity_added_notice.disconnect(self._on_activity_added)
        on_activity_removed_notice.disconnect(self._on_activity_removed)
        on_activity_completed_notice.disconnect(self._on_activity_completed)
        on_activity_expiry_changed_notice.disconnect(self._on_activity_expiry_changed)
        on_activity_started_notice.disconnect(self._on_activity_started)
        on_start_activity_failed_unknown.disconnect(self._on_start_activity_failed_unknown)
        on_activities_loaded.disconnect(self._on_activities_loaded)

    def _on_activity_started(self, activity):
        logger.info('MTOProvider::_on_activity_started ID: %s', activity.id)
        job = self._get_job_by_activity_id(activity.id)
        if job:
            job.mark_started()
            return
        logger.error('MTOProvider::_on_activity_started - Did not find associated activity.')

    def _on_activity_removed(self, mercenary_den_id, activity_id):
        logger.info('MTOProvider::_on_activity_removed ID: %s', activity_id)
        job = self._get_job_by_activity_id(activity_id)
        if job and job.is_tracked:
            eve.Message('MercenaryDen_TrackedJobExpired')
        self._remove_job_by_activity_id(activity_id)

    def _on_activity_expiry_changed(self, previous_expiry_datetime, activity):
        logger.info('MTOProvider::_on_activity_expiry_changed ID: %s', activity.id)
        job = self._get_job_by_activity_id(activity.id)
        if job:
            job.update_expiry(activity.expiry)
            return
        logger.error('MTOProvider::_on_activity_expiry_changed - Did not find associated activity.')

    def _on_activity_added(self, solar_system_id, activity):
        logger.info('MTOProvider::_on_activity_added ID: %s', activity.id)
        job = self._create_job(activity)
        if job is None:
            return
        sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeMercDenNewMTO, data={'job_link': unicode(job.get_notification_link()),
         'solar_system_id': solar_system_id})

    def _on_activity_completed(self, completed_activity):
        logger.info('MTOProvider::_on_activity_completed ID: %s', completed_activity.activity_id)
        job = self._get_job_by_activity_id(completed_activity.activity_id)
        if job:
            job.mark_completed()
            job_board_signals.on_job_state_changed(job)
            job_board_signals.on_job_completed(job)
            uthread2.start_tasklet(self._refresh_jobs_after_delay)
            return
        logger.error('MTOProvider::_on_activity_completed - Did not find associated activity.')

    def _on_activities_loaded(self):
        logger.info('MTOProvider::_on_activities_loaded')
        uthread2.start_tasklet(self._refresh_jobs_after_delay)

    def _refresh_jobs_after_delay(self):
        uthread2.sleep(REFRESH_DELAY)
        self.refresh_jobs()

    def _on_start_activity_failed_unknown(self, activity_id):
        logger.info('MTOProvider::_on_start_activity_failed_unknown ID: %s', activity_id)
        self._remove_job_by_activity_id(activity_id)

    def _remove_job_by_activity_id(self, activity_id):
        job_id = self.get_job_id(activity_id)
        self._remove_job(job_id)
        self.refresh_jobs()

    def _get_job_by_activity_id(self, activity_id):
        job_id = self.get_job_id(activity_id)
        return self._jobs.get(job_id)

    def OnSubscriptionChanged_Local(self):
        job_board_signals.on_job_provider_state_changed(self)

    def OnSkillsChanged(self, skills):
        job_board_signals.on_job_provider_state_changed(self)

    @threadutils.threaded
    def OnDungeonEntered(self, _dungeon_id, instance_id):
        if not isinstance(instance_id, DungeonInstanceIdentifier):
            return
        if not instance_id.is_external_activity:
            return
        job_id = self.get_job_id(instance_id.external_activity_id)
        job = self.try_fetch_job(job_id)
        if not job:
            return
        job.update()
        job_board_signals.on_job_state_changed(job)
        if job.active_dungeon_objective_chain:
            self.add_tracked_job(job, set_expanded=True)

    def OnDungeonExited(self, _dungeon_id, instance_id):
        if not isinstance(instance_id, DungeonInstanceIdentifier):
            return
        if not instance_id.is_external_activity:
            return
        job_id = self.get_job_id(instance_id.external_activity_id)
        job = self._jobs.get(job_id, None)
        if not job:
            return
        job.update()
        job_board_signals.on_job_state_changed(job)
