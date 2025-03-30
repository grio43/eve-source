#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\corporation_goals\provider.py
from corporation.client.goals import goalSignals
from corporation.client.goals.goalsController import CorpGoalsController
from corporation.client.goals.featureFlag import are_corporation_goals_enabled
from metadata.common.content_tags import ContentTags
from eve.common.script.sys.idCheckers import IsPlayerCorporation
import localization
import logging
import uuid
from jobboard.client import job_board_signals
from jobboard.client.features.corporation_goals.job import CorporationGoalJob
from jobboard.client.features.corporation_goals.corporation_goal_job_signals import on_corporation_goal_job_added, on_corporation_goal_job_deleted
from jobboard.client.job_provider import JobProvider
from jobboard.client.provider_type import ProviderType
from jobboard.client.util import get_instance_id_from_job_id
logger = logging.getLogger('corporation_goals')

class CorporationGoalsProvider(JobProvider):
    PROVIDER_ID = ProviderType.CORPORATION_GOALS
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_corporation_projects]
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self, *args, **kwargs):
        self._controller = CorpGoalsController.get_instance()
        super(CorporationGoalsProvider, self).__init__(*args, **kwargs)

    @property
    def feature_title(self):
        corporation_projects_title = localization.GetByLabel('UI/Opportunities/BrowseCorporationProjects')
        if session.corpid and IsPlayerCorporation(session.corpid):
            corp_info = cfg.eveowners.Get(session.corpid)
            if corp_info:
                corporation_projects_title = localization.GetByLabel('UI/Opportunities/BrowseCorporationProjectsWithName', corporation_name=corp_info.ownerName)
        return corporation_projects_title

    def _should_enable(self):
        return are_corporation_goals_enabled()

    def _should_refresh_on_window_initializing(self):
        return not self.is_hidden

    def _on_jobs_refreshed(self):
        pass

    def add_tracked_job(self, job, set_expanded = True):
        super(CorporationGoalsProvider, self).add_tracked_job(job, set_expanded)
        self._cleanup_tracked_jobs()

    def _get_instance_id(self, corporation_goal):
        return corporation_goal.goal_id

    def _get_all_content(self):
        self._controller.fetch_unclaimed_goals()
        result = self._controller.get_active_goals()
        result.extend(self._controller.get_cached_unclaimed_goals())
        return result

    def _construct_job(self, job_id, corporation_goal):
        return CorporationGoalJob(job_id, self, corporation_goal)

    def _register_availability(self):
        job_board_signals.on_goals_feature_availability_changed.connect(self._on_availability_changed)
        goalSignals.on_availability_changed.connect(self._on_availability_changed)

    def _unregister_availability(self):
        job_board_signals.on_goals_feature_availability_changed.disconnect(self._on_availability_changed)
        goalSignals.on_availability_changed.disconnect(self._on_availability_changed)

    def _register_slots(self):
        super(CorporationGoalsProvider, self)._register_slots()
        goalSignals.on_cache_invalidated.connect(self._on_corp_goals_cache_invalidated)
        goalSignals.on_goal_data_fetched.connect(self._on_goal_data_fetched)
        goalSignals.on_created.connect(self._on_created)
        goalSignals.on_deleted.connect(self._on_deleted)
        goalSignals.on_closed.connect(self._on_closed)
        goalSignals.on_completed.connect(self._on_completed)
        goalSignals.on_expired.connect(self._on_closed)
        goalSignals.on_progress_changed.connect(self._on_progress_changed)
        goalSignals.on_goal_name_changed.connect(self._on_goal_name_changed)
        goalSignals.on_goal_description_changed.connect(self._on_goal_description_changed)
        goalSignals.on_goal_reward_redeemed.connect(self._on_goal_reward_redeemed)
        goalSignals.on_closest_solar_system_changed.connect(self._on_closest_solar_system_changed)

    def _unregister_slots(self):
        super(CorporationGoalsProvider, self)._unregister_slots()
        goalSignals.on_cache_invalidated.disconnect(self._on_corp_goals_cache_invalidated)
        goalSignals.on_goal_data_fetched.disconnect(self._on_goal_data_fetched)
        goalSignals.on_created.disconnect(self._on_created)
        goalSignals.on_deleted.disconnect(self._on_deleted)
        goalSignals.on_closed.disconnect(self._on_closed)
        goalSignals.on_completed.disconnect(self._on_completed)
        goalSignals.on_expired.disconnect(self._on_closed)
        goalSignals.on_progress_changed.disconnect(self._on_progress_changed)
        goalSignals.on_goal_name_changed.disconnect(self._on_goal_name_changed)
        goalSignals.on_goal_description_changed.disconnect(self._on_goal_description_changed)
        goalSignals.on_goal_reward_redeemed.disconnect(self._on_goal_reward_redeemed)
        goalSignals.on_closest_solar_system_changed.disconnect(self._on_closest_solar_system_changed)

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' in change:
            job_board_signals.on_job_provider_state_changed(self)

    def _on_corp_goals_cache_invalidated(self):
        self._invalidate_cache()

    def _on_availability_changed(self, _old_value, _new_value):
        self._update_provider_state(self._should_enable())

    def _on_goal_data_fetched(self, goal):
        if goal.is_active() or goal.has_unclaimed_reward():
            self._create_job(goal)
            on_corporation_goal_job_added(goal.goal_id)

    def _on_created(self, goal_id):
        logger.info('CorporationGoalsProvider::_on_created goal ID: %s', goal_id)
        self._create_job(self._controller.get_goal(goal_id))
        on_corporation_goal_job_added(goal_id)

    def _on_deleted(self, goal_id):
        logger.info('CorporationGoalsProvider::_on_deleted goal ID: %s', goal_id)
        job_id = self.get_job_id(goal_id)
        self._remove_job(job_id)
        on_corporation_goal_job_deleted(goal_id)

    def _on_closed(self, goal_id):
        self._goal_updated(goal_id, state_changed=True)

    def _on_completed(self, goal_id):
        job = self._goal_updated(goal_id, state_changed=True)
        if job:
            job_board_signals.on_job_completed(job)
            if job.personal_progress:
                self.service.add_relevance_score(job.content_tag_ids)

    def _on_goal_name_changed(self, goal_id):
        self._goal_updated(goal_id)

    def _on_goal_description_changed(self, goal_id):
        self._goal_updated(goal_id)

    def _on_progress_changed(self, goal_id, current_progress, state_changed):
        logger.info('CorporationGoalsProvider::_on_progress_changed goal_id=%s, progress=%s, state_changed:%s', goal_id, current_progress, state_changed)
        self._goal_updated(goal_id, state_changed)

    def _on_goal_reward_redeemed(self, goal_id, state_changed):
        job = self._goal_updated(goal_id, state_changed)
        if state_changed and job:
            if not job.is_trackable and job.is_tracked:
                self.remove_tracked_job(job)

    def _on_closest_solar_system_changed(self, goal_id, closest_solar_system_id):
        self._goal_updated(goal_id)

    def _goal_updated(self, goal_id, state_changed = False):
        job = self._get_job_by_goal_id(goal_id)
        if job:
            job.update()
            if state_changed:
                job_board_signals.on_job_state_changed(job)
        return job

    def _get_job_by_goal_id(self, goal_id):
        job_id = self.get_job_id(goal_id)
        return self._jobs.get(job_id)

    def _get_goal_id_from_job_id(self, job_id):
        instance_id = get_instance_id_from_job_id(job_id)
        return uuid.UUID(instance_id)

    def try_fetch_job(self, job_id):
        job = super(CorporationGoalsProvider, self).try_fetch_job(job_id)
        if job:
            return job
        goal_id = self._get_goal_id_from_job_id(job_id)
        goal = self._controller.get_goal(goal_id)
        if goal:
            job = self._create_job(goal)
            if job:
                logger.info('CorporationGoalsProvider::try_fetch_job did not find a job with ID %s but retrieved it successfully from CorpGoals', job_id)
                return job
        logger.info('CorporationGoalsProvider::try_fetch_job failed to find a job with ID %s', job_id)
