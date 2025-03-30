#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\provider.py
from dailygoals.client.goalsController import DailyGoalsController
from dailygoals.client.featureFlag import are_daily_goals_enabled
import signals
import threadutils
from metadata.common.content_tags import ContentTags
from gametime import GetWallclockTimeNow, MIN, HOUR
from localization.formatters import FormatTimeIntervalShortWritten
from localization import GetByLabel
from jobboard.client import job_board_signals
from jobboard.client.job_provider import JobProvider
from jobboard.client.provider_type import ProviderType
import dailygoals.client.goalSignals as dailyGoalSignals
from .job import DailyGoalJob

class DailyGoalsProvider(JobProvider):
    PROVIDER_ID = ProviderType.DAILY_GOALS
    PROVIDER_CONTENT_TAGS = [ContentTags.feature_daily_goals]
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self, *args, **kwargs):
        DailyGoalsController.get_instance()
        self._final_alpha_milestone_id = None
        self.on_reward_track_progressed = signals.Signal('on_reward_track_progressed')
        super(DailyGoalsProvider, self).__init__(*args, **kwargs)

    def OnSessionChanged(self, _isRemote, _session, change):
        if 'charid' in change:
            job_board_signals.on_job_provider_state_changed(self)

    @property
    def final_alpha_milestone_id(self):
        if self._final_alpha_milestone_id is None:
            alpha_milestones = self.get_alpha_milestones_of_the_month()
            if alpha_milestones:
                self._final_alpha_milestone_id = alpha_milestones[-1].job_id
            else:
                self._final_alpha_milestone_id = None
        return self._final_alpha_milestone_id

    def get_reward_track_progress(self):
        milestone = self.get_job(self.final_alpha_milestone_id)
        if milestone:
            return milestone.current_progress
        return 0

    def has_unclaimed_rewards(self):
        return DailyGoalsController.get_instance().has_unclaimed_rewards()

    def has_claimable_rewards(self):
        self.wait_for_provider(refresh_jobs=False)
        for job in self._jobs.values():
            if job.has_claimable_rewards:
                return True

        return False

    def get_job_from_goal_id(self, goal_id):
        return self.get_job(self.get_job_id(goal_id))

    def get_jobs_of_the_day(self):
        self.wait_for_provider(refresh_jobs=False)
        goal_ids = DailyGoalsController.get_instance().get_daily_goal_ids_of_the_day()
        return [ j for j in self._jobs.values() if j.goal_id in goal_ids ]

    def get_bonus_job_of_the_day(self):
        self.wait_for_provider(refresh_jobs=False)
        goal_id = DailyGoalsController.get_instance().get_daily_bonus_goal_id_of_the_day()
        if goal_id:
            job_id = self.get_job_id(goal_id)
            return self.get_job(job_id)

    def get_alpha_milestones_of_the_month(self):
        self.wait_for_provider(refresh_jobs=False)
        goal_ids = DailyGoalsController.get_instance().get_monthly_milestone_goal_ids()
        jobs = [ j for j in self._jobs.values() if j.goal_id in goal_ids and not j.is_omega_restricted ]
        jobs.sort(key=lambda job: job.desired_progress)
        return jobs

    def get_omega_milestones_of_the_month(self):
        self.wait_for_provider(refresh_jobs=False)
        goal_ids = DailyGoalsController.get_instance().get_monthly_milestone_goal_ids()
        jobs = [ j for j in self._jobs.values() if j.goal_id in goal_ids and j.is_omega_restricted ]
        jobs.sort(key=lambda job: job.desired_progress)
        return jobs

    def get_unclaimed_omega_restricted_jobs(self):
        self.wait_for_provider(refresh_jobs=False)
        return [ job for job in self._jobs.values() if job.has_unclaimed_omega_restricted_rewards ]

    def get_time_remaining_text(self, job):
        time_now = GetWallclockTimeNow()
        time_remaining = max(job.expiration_time - time_now, 0)
        if time_remaining >= 24 * HOUR:
            showTo = 'hour'
        elif time_remaining >= 5 * MIN:
            showTo = 'minute'
        else:
            showTo = 'second'
        if time_remaining <= 24 * HOUR:
            showFrom = 'hour'
        else:
            showFrom = 'day'
        formatted_time = FormatTimeIntervalShortWritten(time_remaining, showFrom=showFrom, showTo=showTo)
        if time_remaining <= 0:
            return GetByLabel('UI/Generic/Expired')
        else:
            return GetByLabel('UI/ExpertSystem/ExpiresIn', time=formatted_time)

    def _should_enable(self):
        return are_daily_goals_enabled()

    def _on_window_initializing(self):
        super(DailyGoalsProvider, self)._on_window_initializing()
        DailyGoalsController.get_instance().fetch_unclaimed_goals_data()

    def _get_instance_id(self, daily_goal):
        return daily_goal.get_id()

    def _get_all_content(self):
        return DailyGoalsController.get_instance().get_all_goals()

    def _construct_job(self, job_id, daily_goal):
        return DailyGoalJob(job_id, self, daily_goal)

    def _register_availability(self):
        dailyGoalSignals.on_availability_changed.connect(self._on_availability_changed)

    def _unregister_availability(self):
        dailyGoalSignals.on_availability_changed.disconnect(self._on_availability_changed)

    def _register_slots(self):
        super(DailyGoalsProvider, self)._register_slots()
        dailyGoalSignals.on_completed.connect(self._on_completed)
        dailyGoalSignals.on_progress_changed.connect(self._on_progress_changed)
        dailyGoalSignals.on_cache_invalidated.connect(self._on_cache_invalidated)
        dailyGoalSignals.on_goal_payment_redeemed.connect(self._on_goal_payment_redeemed)
        dailyGoalSignals.on_unclaimed_goals_fetched.connect(self._on_unclaimed_goals_fetched)
        dailyGoalSignals.on_goal_data_fetched.connect(self._on_goal_data_fetched)

    def _unregister_slots(self):
        super(DailyGoalsProvider, self)._unregister_slots()
        dailyGoalSignals.on_completed.disconnect(self._on_completed)
        dailyGoalSignals.on_progress_changed.disconnect(self._on_progress_changed)
        dailyGoalSignals.on_cache_invalidated.disconnect(self._on_cache_invalidated)
        dailyGoalSignals.on_goal_payment_redeemed.disconnect(self._on_goal_payment_redeemed)
        dailyGoalSignals.on_unclaimed_goals_fetched.disconnect(self._on_unclaimed_goals_fetched)
        dailyGoalSignals.on_goal_data_fetched.disconnect(self._on_goal_data_fetched)

    def _on_goal_data_fetched(self, goal):
        if self._fetching:
            return
        self._create_job(goal)

    @threadutils.threaded
    def _on_unclaimed_goals_fetched(self):
        self.wait_for_provider(refresh_jobs=False)
        self._invalidate_cache()

    def _on_cache_invalidated(self):
        self._final_alpha_milestone_id = None
        self._jobs.clear()
        self._invalidate_cache()

    def _on_availability_changed(self, _old_value, _new_value):
        self._update_provider_state(self._should_enable())

    def _on_completed(self, goal_id):
        job = self.get_job_from_goal_id(goal_id)
        if not job:
            return
        job.update()
        job_board_signals.on_job_state_changed(job)
        job_board_signals.on_job_completed(job)
        self.service.add_relevance_score(job.content_tag_ids)

    def _on_progress_changed(self, goal_id, current_progress, previous_progress):
        job = self.get_job_from_goal_id(goal_id)
        if not job:
            return
        job.update()
        if current_progress > 0 and previous_progress == 0:
            job_board_signals.on_job_state_changed(job)
        if job.job_id == self.final_alpha_milestone_id:
            self.on_reward_track_progressed()

    def _on_goal_payment_redeemed(self, goal_id):
        job = self.get_job_from_goal_id(goal_id)
        if not job:
            return
        job.update()
        self.remove_tracked_job(job)
