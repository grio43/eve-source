#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dailygoals\client\goalsController.py
import uthread2
import threadutils
import logging
from carbon.common.script.sys.serviceConst import ROLE_QA
from dailygoals.client.featureFlag import are_daily_goals_enabled
from dailygoals.client.goalMessenger import DailyGoalMessenger
from dailygoals.client.mockMessenger import MockDailyGoalMessenger
import dailygoals.client.goalMessengerSignals as messenger_signals
from dailygoals.client.const import DailyGoalCategory, BATCH_SIZE
import dailygoals.client.goalSignals as dailyGoalSignals
from dailygoals.client.goal import DailyGoal
from eve.common.script.util import notificationconst
from dailygoals.client.errors import GoalNotRedeemableToCurrentLocation, GoalMessengerError
from assetholding.client.assetholdingSignals import on_entitlement_redeemed
from assetholding.client.assetholdingController import AssetHoldingController
import dailygoals.client.qa_settings as daily_goals_qa_settings
logger = logging.getLogger('dailygoals')

class DailyGoalsController(object):
    __notifyevents__ = ['OnCharacterSelected']
    _instance = None

    def __init__(self):
        if daily_goals_qa_settings.daily_goals_use_mock.get():
            self._daily_goal_messenger = MockDailyGoalMessenger.get_instance(sm.GetService('publicGatewaySvc'))
        else:
            self._daily_goal_messenger = DailyGoalMessenger.get_instance(sm.GetService('publicGatewaySvc'))
        self._fetching_active = False
        self._active_goals = {}
        self._is_active_goals_dirty = True
        self._fetching_unclaimed = False
        self._unclaimed_goals = {}
        self._is_unclaimed_dirty = True
        self._unclaimed_goal_ids = set()
        self._has_tried_fetching_any_unclaimed_ids = False
        self._abort_fetching = False
        self._connect_to_messenger_signals()
        AssetHoldingController.get_instance()
        sm.RegisterNotify(self)

    def __del__(self):
        self._disconnect_from_messenger_signals()

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = DailyGoalsController()
        return cls._instance

    def _connect_to_messenger_signals(self):
        messenger_signals.on_current_goals_received_internal.connect(self._on_current_goals_received)
        messenger_signals.on_goal_completed_internal.connect(self._on_goal_completed)
        messenger_signals.on_goal_progressed_internal.connect(self._on_goal_progressed)
        messenger_signals.on_goal_redeemed_internal.connect(self._on_goal_redeemed)
        dailyGoalSignals.on_availability_changed.connect(self._on_availability_changed)
        on_entitlement_redeemed.connect(self._on_entitlement_redeemed)

    def _disconnect_from_messenger_signals(self):
        messenger_signals.on_current_goals_received_internal.disconnect(self._on_current_goals_received)
        messenger_signals.on_goal_completed_internal.disconnect(self._on_goal_completed)
        messenger_signals.on_goal_progressed_internal.disconnect(self._on_goal_progressed)
        messenger_signals.on_goal_redeemed_internal.disconnect(self._on_goal_redeemed)
        dailyGoalSignals.on_availability_changed.disconnect(self._on_availability_changed)
        on_entitlement_redeemed.disconnect(self._on_entitlement_redeemed)

    def flush_cache(self):
        if self._fetching_active or self._fetching_unclaimed:
            self._abort_fetching = True
        self._fetching_active = False
        self._active_goals = {}
        self._is_active_goals_dirty = True
        self._unclaimed_goals = {}
        self._is_unclaimed_dirty = True
        self._fetching_unclaimed = False
        self._unclaimed_goal_ids.clear()
        self._has_tried_fetching_any_unclaimed_ids = False
        dailyGoalSignals.on_cache_invalidated()

    def get_all_goals(self):
        all_goals = self._get_active_goals()
        if self._is_unclaimed_dirty:
            uthread2.start_tasklet(self._fetch_unclaimed_history_ids)
        all_goals.extend([ goal for goal in self._unclaimed_goals.values() if goal.has_data() ])
        return all_goals

    def get_daily_goal_ids_of_the_day(self):
        result = []
        for goal in self._active_goals.itervalues():
            if goal.get_category() == DailyGoalCategory.CATEGORY_DAILY:
                result.append(goal.get_id())

        return result

    def get_daily_bonus_goal_id_of_the_day(self):
        for goal in self._active_goals.itervalues():
            if goal.get_category() == DailyGoalCategory.CATEGORY_DAILY_BONUS:
                return goal.get_id()

    def get_monthly_milestone_goal_ids(self):
        result = []
        for goal in self._active_goals.itervalues():
            if goal.get_category() == DailyGoalCategory.CATEGORY_MONTHLY_BONUS:
                result.append(goal.get_id())

        return result

    def has_unclaimed_rewards(self):
        if not bool(self._unclaimed_goal_ids) and not self._has_tried_fetching_any_unclaimed_ids and self._is_unclaimed_dirty and not self._fetching_unclaimed and are_daily_goals_enabled():
            self._has_tried_fetching_any_unclaimed_ids = True
            uthread2.start_tasklet(self._fetch_unclaimed_page, None)
        return bool(self._unclaimed_goal_ids)

    def redeem_reward(self, goal_id, redeem_to_current_location = False):
        try:
            self._daily_goal_messenger.redeem_reward(goal_id, redeem_to_current_location)
        except GoalNotRedeemableToCurrentLocation:
            try:
                self._daily_goal_messenger.redeem_reward(goal_id, do_redeem_current_location=False)
            except Exception as e:
                logger.exception('Daily Goals: Unable to redeem on retry for goal %s' % goal_id)
                dailyGoalSignals.on_goal_payment_failed(goal_id)

        except Exception as e:
            logger.exception('Daily Goals: Failed to redeem goal with id %s' % goal_id)
            dailyGoalSignals.on_goal_payment_failed(goal_id)

    def pay_for_completion(self, goal_id):
        try:
            self._daily_goal_messenger.pay_for_completion(goal_id)
            self._get_goal(goal_id).set_paid_completion(True)
            dailyGoalSignals.on_pay_for_completion_successful(goal_id)
        except GoalMessengerError as gme:
            logger.exception('Daily Goals: Redeeming the goal returned status code %s' % gme.status_code)
            dailyGoalSignals.on_pay_for_completion_failed(goal_id, gme.status_code)
        except Exception as e:
            logger.exception('Daily Goals: Failed to redeem goal with id %s' % goal_id)
            dailyGoalSignals.on_pay_for_completion_failed(goal_id, None)

    def get_completion_convenience_counter(self):
        ret = 0
        for goal in self._get_active_goals():
            if goal.paid_completion():
                ret += 1

        return ret

    @threadutils.threaded
    def fetch_unclaimed_goals_data(self):
        if not are_daily_goals_enabled():
            return
        if self._is_unclaimed_dirty:
            self._fetch_unclaimed_history_ids()
        while self._fetching_unclaimed:
            uthread2.Yield()

        for goal in self._unclaimed_goals.values():
            self._fetch_missing_goal_data(goal)

    def _get_cached_goal(self, goal_id):
        if goal_id in self._active_goals:
            return self._active_goals[goal_id]
        if goal_id in self._unclaimed_goals:
            return self._unclaimed_goals[goal_id]

    def _get_goal(self, goal_id):
        goal = self._get_cached_goal(goal_id)
        if goal:
            return goal
        data = self._fetch_goal(goal_id)
        if not data:
            return None
        goal = DailyGoal(goal_id)
        goal.set_data(data)
        if goal.is_expired:
            self._unclaimed_goals[goal_id] = goal
        else:
            self._active_goals[goal_id] = goal
        return goal

    def _get_active_goals(self):
        self._fetch_active_goals()
        return self._active_goals.values()

    def _fetch_active_goals(self):
        if self._fetching_active or not self._is_active_goals_dirty or not are_daily_goals_enabled():
            return
        self._fetching_active = True
        try:
            data = self._daily_goal_messenger.get_current_goals()
        except Exception as e:
            self._fetching_active = False
            self._abort_fetching = False
            raise e

        for goal in data:
            goal_id = goal.get('goal_id', None)
            if goal and goal_id:
                daily_goal = DailyGoal(goal_id)
                daily_goal.set_data(goal)
                self._active_goals[goal_id] = daily_goal
                if goal_id in self._unclaimed_goals:
                    del self._unclaimed_goals[goal_id]
                dailyGoalSignals.on_goal_data_fetched(daily_goal)
                if goal_id not in self._unclaimed_goal_ids and daily_goal.has_unclaimed_rewards():
                    self._unclaimed_goal_ids.add(goal_id)
                    dailyGoalSignals.on_unclaimed_goal_ids_changed()

        self._fetching_active = False
        self._is_active_goals_dirty = False
        self._abort_fetching = False

    def _fetch_unclaimed_history_ids(self):
        if self._fetching_unclaimed or not self._is_unclaimed_dirty or not are_daily_goals_enabled():
            return
        self._fetching_unclaimed = True
        next_token = None
        has_exception = False
        while next_token != '':
            try:
                next_token = self._fetch_unclaimed_page(token=next_token)
            except Exception as e:
                logger.exception('Daily Goals: Unable to fetch goal ids with token %s, %s' % (next_token, str(e)))
                has_exception = True
                break

            if self._abort_fetching:
                break

        self._fetching_unclaimed = False
        self._is_unclaimed_dirty = has_exception
        self._abort_fetching = False
        dailyGoalSignals.on_unclaimed_goals_fetched()

    def _fetch_unclaimed_page(self, token):
        if token is None:
            token = ''
        self._has_tried_fetching_any_unclaimed_ids = True
        next_token, goal_ids = self._daily_goal_messenger.get_all_with_rewards_page(token=token, size=BATCH_SIZE)
        if self._abort_fetching:
            self._abort_fetching = False
            self._fetching_unclaimed = False
            return
        for goal_id in goal_ids:
            if goal_id in self._active_goals:
                continue
            if goal_id not in self._unclaimed_goals:
                self._unclaimed_goals[goal_id] = DailyGoal(goal_id)

        if bool(goal_ids):
            self._unclaimed_goal_ids.update(goal_ids)
            dailyGoalSignals.on_unclaimed_goal_ids_changed()
        return next_token

    @threadutils.threaded
    def _fetch_missing_goal_data(self, goal):
        if not goal or goal.fetching or goal.has_data():
            return
        goal.fetching = True
        data = self._fetch_goal(goal.get_id())
        goal.fetching = False
        if data is not None:
            goal.set_data(data)
            dailyGoalSignals.on_goal_data_fetched(goal)

    def _error_cleanup(self, log_text, exception):
        logger.exception('%s: %s' % log_text, str(exception))
        self._fetching_unclaimed = False
        self._abort_fetching = False

    def _fetch_goal(self, goal_id):
        try:
            goal_data = self._daily_goal_messenger.get_goal(goal_id)
        except Exception as e:
            logger.exception('Unable to fetch goal: %s' % str(e))
            return None

        return goal_data

    def _on_current_goals_received(self):
        self.flush_cache()

    @threadutils.threaded
    def _on_goal_completed(self, goal_id):
        goal = self._get_goal(goal_id)
        if not goal:
            return
        self._unclaimed_goal_ids.add(goal_id)
        desired_progress = goal.get_target_progress()
        goal.set_current_progress(desired_progress)
        dailyGoalSignals.on_completed(goal_id)
        if goal.get_category() != DailyGoalCategory.CATEGORY_MONTHLY_BONUS:
            self._dispatch_goal_completed_notification(goal_id, goal.get_name())
        elif not goal.is_last_milestone:
            self._dispatch_milestone_completed_notification()
        elif not sm.GetService('cloneGradeSvc').IsOmega():
            self._dispatch_track_completed_notification()

    def _on_goal_progressed(self, goal_id, progress):
        if goal_id not in self._active_goals:
            return
        previous_progress = self._active_goals[goal_id].get_current_progress()
        self._active_goals[goal_id].set_current_progress(progress)
        dailyGoalSignals.on_progress_changed(goal_id, progress, previous_progress)

    def _is_cached_active_or_unclaimed(self, goal_id):
        return goal_id in self._active_goals or goal_id in self._unclaimed_goals

    def _on_goal_redeemed(self, goal_id):
        if not self._is_cached_active_or_unclaimed(goal_id):
            return
        goal = self._get_goal(goal_id)
        if not goal:
            return
        goal.mark_as_redeemed()
        dailyGoalSignals.on_goal_payment_redeemed(goal_id)
        dailyGoalSignals.on_goal_payment_complete(goal_id)
        self._unclaimed_goal_ids.discard(goal_id)
        dailyGoalSignals.on_unclaimed_goal_ids_changed()

    def _on_entitlement_redeemed(self, goal_id, _):
        self._on_goal_redeemed(goal_id)

    def _on_availability_changed(self, _old_value, _new_value):
        self.flush_cache()

    def _dispatch_goal_completed_notification(self, goal_id, goal_name):
        sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeDailyGoalCompleted, data={'goalName': goal_name,
         'goalID': goal_id})

    def _dispatch_milestone_completed_notification(self):
        sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeDailyMilestoneCompleted, data={'isOmega': sm.GetService('cloneGradeSvc').IsOmega()})

    def _dispatch_track_completed_notification(self):
        sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeDailyRewardTrackCompleted, data={})

    def admin_set_progress(self, goal_id, progress_to_set):
        if session.role & ROLE_QA:
            goal = self._get_goal(goal_id)
            if goal:
                progress_to_add = progress_to_set - goal.get_current_progress()
                progress_to_add = max(0, progress_to_add)
                progress_to_add = min(progress_to_add, goal.get_target_progress() - goal.get_current_progress())
                if progress_to_add > 0:
                    self._daily_goal_messenger.set_goal_progress(goal_id, session.charid, progress_to_add)

    def OnCharacterSelected(self, *args, **kwargs):
        self.flush_cache()


def __SakeReloadHook():
    try:
        DailyGoalsController.get_instance().flush_cache()
    except Exception:
        import log
        log.LogException()
