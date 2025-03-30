#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\client\goals\goalsController.py
import logging
from collections import defaultdict
import corporation.client.goals.goalMessengerSignals as messenger_signals
import gametime
import threadutils
import uthread2
from assetholding.client import assetholdingSignals
from assetholding.client.assetholdingController import AssetHoldingController
from carbonui import uiconst
from carbonui.uicore import uicore
from corporation.client.goals import goalSignals
from corporation.client.goals.errors import AtGoalCapacity, BadRequestToReserveAsset, WalletAccessForbidden, InsufficientFunds, InvalidExpirationTime
from corporation.client.goals.featureFlag import are_corporation_goals_enabled
from corporation.client.goals.goal import CorporationGoal
from corporation.client.goals.goalMessenger import GoalMessenger
from corporation.client.goals.goalsSettings import qa_allow_short_corp_projects
from corporation.client.goals.goalsUtil import get_timespan_by_option
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.common.script.sys.idCheckers import IsNPCCorporation
from goals.common.goalConst import ContributionMethodTypes, GoalState
from localization import GetByLabel
logger = logging.getLogger('corporation_goals')

class CorpGoalsController(object):
    __notifyevents__ = ['OnCharacterSelected', 'OnSessionChanged']
    _instance = None

    def __init__(self):
        self._capacity = None
        self._messenger = None
        self._goals = {}
        self._fetching_data_for_goal_ids = set()
        self._active_goal_ids = set()
        self._is_active_dirty = True
        self._fetching_active = False
        self._unclaimed_goal_ids = set()
        self._is_unclaimed_dirty = True
        self._fetching_unclaimed = False
        self._has_tried_fetching_any_unclaimed_ids = False
        self._inactive_goal_ids = defaultdict(set)
        self._is_inactive_dirty = defaultdict(lambda : True)
        self._fetching_inactive = defaultdict(lambda : False)
        sm.RegisterNotify(self)
        self._connect_to_messenger_signals()
        AssetHoldingController.get_instance()

    def __del__(self):
        sm.UnregisterNotify(self)
        self._disconnect_from_messenger_signals()

    def _connect_to_messenger_signals(self):
        messenger_signals.on_goal_created_internal.connect(self._on_goal_created)
        messenger_signals.on_goal_deleted_internal.connect(self._on_goal_deleted)
        messenger_signals.on_goal_closed_internal.connect(self._on_goal_closed)
        messenger_signals.on_goal_completed_internal.connect(self._on_goal_completed)
        messenger_signals.on_goal_contribution_internal.connect(self._on_goal_contribution)
        messenger_signals.on_goal_progress_set_internal.connect(self._on_goal_progress_set)
        messenger_signals.on_goal_redeemed_internal.connect(self._on_goal_redeemed)
        messenger_signals.on_goal_name_changed_internal.connect(self._on_goal_name_changed)
        messenger_signals.on_goal_description_changed_internal.connect(self._on_goal_description_changed)
        messenger_signals.on_goal_expired_internal.connect(self._on_goal_expired)
        assetholdingSignals.on_entitlement_redeemed.connect(self._on_goal_redeemed)

    def _disconnect_from_messenger_signals(self):
        messenger_signals.on_goal_created_internal.disconnect(self._on_goal_created)
        messenger_signals.on_goal_deleted_internal.disconnect(self._on_goal_deleted)
        messenger_signals.on_goal_closed_internal.disconnect(self._on_goal_closed)
        messenger_signals.on_goal_completed_internal.disconnect(self._on_goal_completed)
        messenger_signals.on_goal_contribution_internal.disconnect(self._on_goal_contribution)
        messenger_signals.on_goal_progress_set_internal.disconnect(self._on_goal_progress_set)
        messenger_signals.on_goal_redeemed_internal.disconnect(self._on_goal_redeemed)
        messenger_signals.on_goal_name_changed_internal.disconnect(self._on_goal_name_changed)
        messenger_signals.on_goal_description_changed_internal.disconnect(self._on_goal_description_changed)
        messenger_signals.on_goal_expired_internal.disconnect(self._on_goal_expired)
        assetholdingSignals.on_entitlement_redeemed.disconnect(self._on_goal_redeemed)

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = CorpGoalsController()
        return cls._instance

    @property
    def messenger(self):
        if self._messenger is None:
            self._messenger = GoalMessenger.get_instance(sm.GetService('publicGatewaySvc'))
        return self._messenger

    def redeem_reward(self, goal_id):
        try:
            self.messenger.redeem_reward(goal_id)
        except Exception as e:
            logger.warning('Failed to redeem goal with id %s - %s', goal_id, str(e))
            goalSignals.on_goal_redeem_failed(goal_id)

    def get_active_goals(self, fetch_contribution = True, wait = True):
        self.fetch_active_goals(fetch_contribution=fetch_contribution)
        if wait:
            self.wait_for_active()
        return self.get_cached_active_goals()

    def get_cached_active_goals(self):
        return [ self._goals[goal_id] for goal_id in self._active_goal_ids if self._goals[goal_id].has_data() ]

    def fetch_active_goals(self, fetch_contribution = True):
        if not self._should_fetch_goals():
            return
        if self._fetching_active:
            return
        if self._is_active_dirty:
            self._fetching_active = True
            uthread2.start_tasklet(self._fetch_active_goal_ids)
        uthread2.start_tasklet(self._fetch_missing_active_goals_data, fetch_contribution)

    def wait_for_active(self):
        while self._fetching_active:
            uthread2.Yield()

    def get_unclaimed_goals(self, wait = True):
        self.fetch_unclaimed_goals()
        if wait:
            self.wait_for_unclaimed()
        return self.get_cached_unclaimed_goals()

    def get_cached_unclaimed_goals(self):
        return [ self._goals[goal_id] for goal_id in self._unclaimed_goal_ids if self._goals[goal_id].has_data() ]

    def fetch_unclaimed_goals(self):
        if not self._should_fetch_goals():
            return
        if self._fetching_unclaimed:
            return
        if self._is_unclaimed_dirty:
            self._fetching_unclaimed = True
            uthread2.start_tasklet(self._fetch_unclaimed_goal_ids)
        uthread2.start_tasklet(self._fetch_missing_unclaimed_goals_data)

    def wait_for_unclaimed(self):
        while self._fetching_unclaimed:
            uthread2.Yield()

    def get_inactive_goals(self, months_since = None, fetch_contribution = True, wait = True):
        self.fetch_inactive_goals(months_since, fetch_contribution)
        if wait:
            self.wait_for_inactive(months_since)
        return self.get_cached_inactive_goals(months_since)

    def get_cached_inactive_goals(self, months_since = None):
        return [ self._goals[goal_id] for goal_id in self._inactive_goal_ids[months_since] if self._goals[goal_id].has_data() ]

    def fetch_inactive_goals(self, months_since = None, fetch_contribution = True):
        if not self._should_fetch_goals():
            return
        if self._fetching_inactive[months_since]:
            return
        if self._is_inactive_dirty[months_since]:
            self._fetching_inactive[months_since] = True
            uthread2.start_tasklet(self._fetch_inactive_goal_ids, months_since)
        uthread2.start_tasklet(self._fetch_missing_inactive_goals_data, months_since, fetch_contribution)

    def wait_for_inactive(self, months_since = None):
        while self._fetching_inactive[months_since]:
            uthread2.Yield()

    def is_inactive_goal(self, goal_id, months_since = None):
        return goal_id in self._inactive_goal_ids[months_since] and self._goals[goal_id].has_data()

    def get_goal(self, goal_id):
        goal = self._goals.get(goal_id, None)
        if goal and goal.has_data():
            return goal
        if not self._should_fetch_goals():
            return
        if not goal:
            logger.info('Creating goal from get_goal %s', goal_id)
            goal = CorporationGoal(goal_id)
            self._goals[goal_id] = goal
        self._fetch_missing_goal_data(goal, wait_while_fetching=True)
        if not goal.has_data():
            return
        return goal

    def has_unclaimed_rewards(self):
        if not bool(self._unclaimed_goal_ids) and not self._has_tried_fetching_any_unclaimed_ids and self._is_unclaimed_dirty and not self._fetching_unclaimed and are_corporation_goals_enabled():
            self._has_tried_fetching_any_unclaimed_ids = True
            uthread2.start_tasklet(self._fetch_unclaimed_page, None)
        return bool(self._unclaimed_goal_ids)

    def _should_fetch_goals(self):
        return session.corpid and not IsNPCCorporation(session.corpid) and are_corporation_goals_enabled()

    def _fetch_active_goal_ids(self):
        self._fetching_active = True
        next_token = None
        has_exception = False
        while next_token != '':
            try:
                next_token = self._fetch_active_page(token=next_token)
            except Exception as e:
                logger.warning('Unable to fetch active goal ids with token %s - %s', next_token, str(e))
                has_exception = True
                break

        self._fetching_active = False
        self._is_active_dirty = has_exception

    def _fetch_active_page(self, token):
        if token is None:
            token = ''
        next_token, goal_ids = self.messenger.get_active_goal_ids(token=token)
        for goal_id in goal_ids:
            if goal_id not in self._goals:
                self._goals[goal_id] = CorporationGoal(goal_id)
            self._active_goal_ids.add(goal_id)

        return next_token

    def _fetch_missing_active_goals_data(self, fetch_contribution = True):
        self.wait_for_active()
        for goal_id in self._active_goal_ids:
            self._fetch_missing_goal_data(self._goals.get(goal_id, None), fetch_contribution)

    def _fetch_unclaimed_goal_ids(self):
        self._fetching_unclaimed = True
        next_token = None
        has_exception = False
        while next_token != '':
            try:
                next_token = self._fetch_unclaimed_page(token=next_token)
            except Exception as e:
                logger.warning('Unable to fetch unclaimed goal ids with token %s - %s', next_token, str(e))
                has_exception = True
                break

        self._fetching_unclaimed = False
        self._is_unclaimed_dirty = has_exception

    def _fetch_unclaimed_page(self, token):
        if token is None:
            token = ''
        next_token, goal_ids = self.messenger.get_unclaimed_goal_ids(token=token)
        self._has_tried_fetching_any_unclaimed_ids = True
        for goal_id in goal_ids:
            if goal_id not in self._goals:
                self._goals[goal_id] = CorporationGoal(goal_id)
            self._unclaimed_goal_ids.add(goal_id)

        if bool(goal_ids):
            goalSignals.on_unclaimed_goal_ids_changed()
        return next_token

    def _fetch_missing_unclaimed_goals_data(self):
        self.wait_for_unclaimed()
        for goal_id in self._unclaimed_goal_ids:
            self._fetch_missing_goal_data(self._goals.get(goal_id, None))

    def _fetch_inactive_goal_ids(self, months_since):
        self._fetching_inactive[months_since] = True
        next_token = None
        has_exception = False
        while next_token != '':
            try:
                next_token = self._fetch_inactive_page(months_since, token=next_token)
            except Exception as e:
                logger.warning('Unable to fetch inactive goal ids with token %s - %s', next_token, str(e))
                has_exception = True
                break

        self._fetching_inactive[months_since] = False
        self._is_inactive_dirty[months_since] = has_exception

    def _fetch_inactive_page(self, months_since, token):
        if token is None:
            token = ''
        start_time, duration = get_timespan_by_option(months_since)
        next_token, goal_ids = self.messenger.get_inactive_goal_ids(start_time, duration, token=token)
        for goal_id in goal_ids:
            if goal_id not in self._goals:
                self._goals[goal_id] = CorporationGoal(goal_id)
            self._inactive_goal_ids[months_since].add(goal_id)

        return next_token

    def _fetch_missing_inactive_goals_data(self, months_since, fetch_contribution = True):
        self.wait_for_inactive(months_since)
        for goal_id in self._inactive_goal_ids[months_since]:
            self._fetch_missing_goal_data(self._goals.get(goal_id, None), fetch_contribution)

    def _fetch_missing_goal_data(self, goal, fetch_contribution = True, wait_while_fetching = False):
        if not goal:
            return
        if goal.has_data() and (not fetch_contribution or goal.has_fetched_contribution()):
            return
        goal_id = goal.goal_id
        if goal_id not in self._fetching_data_for_goal_ids:
            self._fetching_data_for_goal_ids.add(goal_id)
            self.__fetch_missing_goal_data(goal, fetch_contribution)
        if wait_while_fetching:
            while goal_id in self._fetching_data_for_goal_ids:
                uthread2.Yield()

    @threadutils.threaded
    def __fetch_missing_goal_data(self, goal, fetch_contribution):
        goal_id = goal.get_id()
        updated = False
        if not goal.has_data():
            try:
                data = self.messenger.get_goal(goal_id)
            except Exception as e:
                logger.warning('Unable to fetch goal %s - %s', goal_id, str(e))
                data = None

            if data:
                goal.set_data(data)
                updated = True
            else:
                fetch_contribution = False
        if fetch_contribution and not goal.has_fetched_contribution():
            if goal.get_current_progress() == 0:
                summary = {'progress': 0,
                 'rewards_unclaimed': 0}
            else:
                try:
                    summary = self.messenger.get_my_contributor_summary(goal_id)
                except Exception as e:
                    logger.warning('Unable to fetch character contribution summary for goal %s - %s', goal_id, str(e))
                    summary = None

            if summary:
                goal.set_contribution(summary['progress'], summary['rewards_unclaimed'])
                if goal_id not in self._unclaimed_goal_ids and goal.has_unclaimed_reward():
                    self._unclaimed_goal_ids.add(goal_id)
                    goalSignals.on_unclaimed_goal_ids_changed()
                updated = True
        self._fetching_data_for_goal_ids.discard(goal_id)
        if updated:
            goalSignals.on_goal_data_fetched(goal)

    def _is_fetching_data_for_goal(self, goal):
        return goal.goal_id in self._fetching_data_for_goal_ids

    def _is_fetching_any_active_goal_data(self):
        return not self._active_goal_ids.isdisjoint(self._fetching_data_for_goal_ids)

    def _is_fetching_any_unclaimed_goal_data(self):
        return not self._unclaimed_goal_ids.isdisjoint(self._fetching_data_for_goal_ids)

    def _is_fetching_any_inactive_goal_data(self, months_since = None):
        return not self._inactive_goal_ids[months_since].isdisjoint(self._fetching_data_for_goal_ids)

    def flush_cache(self):
        self._capacity = None
        self._goals.clear()
        self._active_goal_ids.clear()
        self._is_active_dirty = True
        self._unclaimed_goal_ids.clear()
        self._is_unclaimed_dirty = True
        self._has_tried_fetching_any_unclaimed_ids = False
        self._inactive_goal_ids.clear()
        self._is_inactive_dirty.clear()
        goalSignals.on_cache_invalidated()
        logger.info('GoalsController::flush_cache')

    def get_all_goal_contributor_summaries(self, goal_id):
        goal = self._goals.get(goal_id, None)
        if not goal:
            return []
        cached = goal.all_contributor_summaries
        if cached is not None and gametime.GetSecondsSinceWallclockTime(goal.all_contributor_summaries_fetch_time) < 60:
            return cached
        goal.all_contributor_summaries_fetch_time = gametime.GetWallclockTime()
        result = []
        next_token = None
        has_exception = False
        while next_token != '':
            try:
                if next_token is None:
                    next_token = ''
                next_token, summaries = self.messenger.get_all_contributor_summaries_for_goal(goal_id=goal_id, token=next_token)
                result.extend(summaries)
            except Exception as e:
                logger.warning('Unable to fetch contributor summaries for goal %s with token %s - %s', goal_id, next_token, str(e))
                has_exception = True
                break

        if not has_exception:
            goal.all_contributor_summaries = result
        return result

    def _has_funds(self, amount):
        wallet = sm.GetService('wallet')
        wealth = wallet.GetCorpWealth(accountKey=session.corpAccountKey)
        return wealth >= amount

    def create_goal(self, name, description, desired_progress, method_type, contribution_fields = None, career_path = None, payment_per_contribution = None, end_time = None, participation_limit = None, coverage_limit = None, multiplier = None):
        if payment_per_contribution and not self._has_funds(payment_per_contribution * desired_progress):
            ShowQuickMessage(GetByLabel('UI/Corporations/Goals/InsufficientFunds'))
            raise InsufficientFunds('Funds in the selected wallet division do not suffice to create project')
        try:
            self.messenger.create_goal(name=name, description=description, desired_progress=desired_progress, method_id=method_type, contribution_fields=contribution_fields or {}, career_path=career_path, payment=payment_per_contribution, expiration=end_time, validate_end_date=not qa_allow_short_corp_projects.get(), participation_limit=participation_limit, coverage_limit=coverage_limit, multiplier=multiplier)
        except AtGoalCapacity:
            max_active = self.get_active_capacity()
            ShowQuickMessage(GetByLabel('UI/Corporations/Goals/AtGoalsCapacity', numMax=max_active))
            raise
        except BadRequestToReserveAsset:
            ShowQuickMessage(GetByLabel('UI/Corporations/Goals/InsufficientFunds'))
            raise
        except WalletAccessForbidden:
            ShowQuickMessage(GetByLabel('UI/Corporations/Wallet/WalletDivisionAccessDenied'))
            raise
        except InvalidExpirationTime:
            ShowQuickMessage(GetByLabel('UI/Corporations/Goals/InvalidDuration'))
            raise
        except Exception:
            ShowQuickMessage(GetByLabel('UI/Corporations/Goals/FailedToConnect'))
            self.flush_cache()
            raise

    def delete_goal(self, goal_id, show_prompt = True):
        try:
            if show_prompt and uicore.Message('DeleteCorpProject', buttons=uiconst.YESNO) != uiconst.ID_YES:
                return
            self.messenger.delete_goal(goal_id)
        except Exception:
            ShowQuickMessage(GetByLabel('UI/Corporations/Goals/FailedToConnect'))
            self.flush_cache()
            raise

    def complete_goal(self, goal_id):
        try:
            if uicore.Message('CompleteCorpProject', buttons=uiconst.YESNO) != uiconst.ID_YES:
                return
            goal = self.get_goal(goal_id)
            current_progress = goal.get_current_progress()
            desired_progress = goal.get_desired_progress()
            updated_progress = desired_progress
            self._set_goal_progress(goal_id, current_progress, updated_progress, desired_progress)
        except Exception:
            ShowQuickMessage(GetByLabel('UI/Corporations/Goals/FailedToConnect'))
            self.flush_cache()
            raise

    def close_goal(self, goal_id):
        try:
            if uicore.Message('CloseCorpProject', buttons=uiconst.YESNO) != uiconst.ID_YES:
                return
            self.messenger.close_goal(goal_id)
        except Exception:
            ShowQuickMessage(GetByLabel('UI/Corporations/Goals/FailedToConnect'))
            self.flush_cache()
            raise

    def set_current_progress(self, goal_id, updated_progress):
        goal = self._goals.get(goal_id, None)
        if not goal:
            return
        current_progress = goal.get_current_progress()
        desired_progress = goal.get_desired_progress()
        self._set_goal_progress(goal_id, current_progress, updated_progress, desired_progress)

    def get_items_pending_delivery(self, office_id):
        if not are_corporation_goals_enabled():
            return {}
        try:
            goals = self.get_active_goals(wait=False, fetch_contribution=False)
        except (NotImplementedError, RuntimeError):
            return {}

        quantity_by_type = defaultdict(int)
        for goal in goals:
            if goal.has_reached_participation_limit():
                continue
            contribution_method = goal.get_contribution_method()
            if contribution_method.method_id == ContributionMethodTypes.DELIVER_ITEM and contribution_method.office in (None, office_id):
                quantity_by_type[contribution_method.item_type] += goal.get_my_remaining_progress()

        return quantity_by_type

    def get_active_capacity(self):
        if self._capacity is None:
            try:
                self._capacity = self.messenger.get_capacity()
            except Exception:
                return 0

        return self._capacity

    def qa_delete_all_goals(self):
        for goal in self.get_cached_active_goals():
            if not goal.get_current_progress():
                self.delete_goal(goal.get_id(), show_prompt=False)

    def _set_goal_progress(self, goal_id, current_progress, updated_progress, desired_progress):
        updated_progress = min(updated_progress, desired_progress)
        try:
            self.messenger.set_manual_goal_progress(goal_id=goal_id, current_progress=current_progress, updated_progress=updated_progress)
        except Exception:
            ShowQuickMessage(GetByLabel('UI/Corporations/Goals/FailedToConnect'))
            self.flush_cache()
            raise

    def OnSessionChanged(self, _isRemote, _session, change):
        if 'corpid' in change:
            self.flush_cache()

    def OnCharacterSelected(self, *args, **kwargs):
        self.flush_cache()

    def _on_goal_created(self, goal_id, goal_data):
        goal = CorporationGoal(goal_id)
        goal.set_data(goal_data)
        self._goals[goal_id] = goal
        self._active_goal_ids.add(goal.goal_id)
        goalSignals.on_created(goal_id)

    def _on_goal_deleted(self, goal_id):
        goal = self._goals.pop(goal_id, None)
        self._active_goal_ids.discard(goal_id)
        for months_since in self._inactive_goal_ids:
            self._inactive_goal_ids[months_since].discard(goal_id)

        if goal:
            goalSignals.on_deleted(goal_id)

    def _on_goal_closed(self, goal_id):
        goal = self._goals.get(goal_id, None)
        self._active_goal_ids.discard(goal_id)
        self._inactive_goal_ids[None].add(goal_id)
        if goal:
            goal.close()
            goalSignals.on_closed(goal_id)
            goalSignals.on_state_changed(goal_id, state=GoalState.CLOSED)

    def _on_goal_completed(self, goal_id):
        goal = self._goals.get(goal_id, None)
        self._active_goal_ids.discard(goal_id)
        self._inactive_goal_ids[None].add(goal_id)
        if goal:
            desired_progress = goal.get_desired_progress()
            goal.set_current_progress(desired_progress)
            goal.complete()
            goalSignals.on_completed(goal_id)
            goalSignals.on_state_changed(goal_id, state=GoalState.COMPLETED)

    def _on_goal_expired(self, goal_id):
        goal = self._goals.get(goal_id, None)
        self._active_goal_ids.discard(goal_id)
        self._inactive_goal_ids[None].add(goal_id)
        if goal:
            goal.expire()
            goalSignals.on_expired(goal_id)
            goalSignals.on_state_changed(goal_id, state=GoalState.EXPIRED)

    def _on_goal_progress_set(self, goal_id, progress):
        logger.info('GoalsController::_on_goal_progress_set: goal_id=%s, progress=%s', goal_id, progress)
        goal = self._goals.get(goal_id, None)
        if not goal:
            logger.info('Goal not found, not setting progress: goal_id=%s, progress=%s', goal_id, progress)
            return
        goal.set_current_progress(progress)
        goalSignals.on_progress_changed(goal_id, progress, state_changed=False)

    def _on_goal_contribution(self, goal_id, progress_added, current_progress):
        goal = self._goals.get(goal_id, None)
        if not goal:
            return
        state_changed = goal.update_my_progress(progress_added)
        goal.set_current_progress(current_progress)
        if goal_id not in self._unclaimed_goal_ids and goal.has_unclaimed_reward():
            self._unclaimed_goal_ids.add(goal_id)
            goalSignals.on_unclaimed_goal_ids_changed()
        goalSignals.on_progress_changed(goal_id, current_progress, state_changed=state_changed)

    def _on_goal_redeemed(self, goal_id, quantity):
        goal = self._goals.get(goal_id, None)
        if goal:
            goal.update_redeemed_capacity(quantity)
            if not goal.has_unclaimed_reward() and goal_id in self._unclaimed_goal_ids:
                self._unclaimed_goal_ids.discard(goal_id)
                goalSignals.on_unclaimed_goal_ids_changed()

    def _on_goal_name_changed(self, goal_id, new_name):
        goal = self._goals.get(goal_id, None)
        if goal:
            goal.set_name(new_name)
            goalSignals.on_goal_name_changed(goal_id)

    def _on_goal_description_changed(self, goal_id, new_description):
        goal = self._goals.get(goal_id, None)
        if goal:
            goal.set_description(new_description)
            goalSignals.on_goal_description_changed(goal_id)


def __SakeReloadHook():
    try:
        CorpGoalsController.get_instance().flush_cache()
    except Exception:
        import log
        log.LogException()
