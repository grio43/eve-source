#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\client\goals\goal.py
import gametime
from carbon.common.script.util.format import DateToBlue
import eveformat
from goals.client.contributionMethods import get_contribution_method
from goals.common import goalConst
from goals.common.goalConst import GoalState, ContributionMethodTypes
from corporation.client.goals.goalsUtil import CanAuthorGoals
from jobboard.client.util import get_closest_solarsystem_in_locations_from
from localization.formatters import FormatNumeric
from logging import getLogger
from .goalDragData import GoalDragData
from .goalReward import CorpGoalReward
from .goalSignals import on_goal_reward_earned, on_goal_reward_redeemed, on_closest_solar_system_changed
logger = getLogger('corporation_goals')

class CorporationGoal(object):
    __notifyevents__ = ['OnAutopilotUpdated', 'OnSessionChanged']

    def __init__(self, goal_id):
        self.goal_id = goal_id
        self.created = None
        self.name = None
        self.description = None
        self.desired_progress = None
        self.current_progress = None
        self.state = GoalState.UNSPECIFIED
        self.creator = None
        self._assigner_type = None
        self._assigner_id = None
        self._assignee_type = None
        self._assignee_id = None
        self.contribution_method = None
        self._career_path = None
        self._my_progress = 0
        self._finish_time = None
        self._due_time = None
        self._ui_annotations = None
        self._reward = None
        self.all_contributor_summaries = None
        self.all_contributor_summaries_fetch_time = None
        self._has_set_data = False
        self._has_fetched_contribution = False
        self._participation_limit = None
        self._multiplier = None
        self._coverage_limit = None
        self._closest_solar_system_id = None
        sm.RegisterNotify(self)

    def __del__(self):
        sm.UnregisterNotify(self)

    def OnAutopilotUpdated(self, *args, **kwargs):
        if self._closest_solar_system_id:
            self._update_closest_location()

    def OnSessionChanged(self, is_remote, session, change):
        if not self._closest_solar_system_id:
            return
        if 'locationid' in change:
            self._update_closest_location()

    def set_data(self, data):
        self.goal_id = data.get('goal_id', None)
        self.created = data.get('created', None)
        self.name = data.get('name', None)
        self.description = data.get('description', None)
        self.desired_progress = data.get('desired_progress', 0)
        self.current_progress = data.get('current_progress', 0)
        self.state = data.get('state', GoalState.ACTIVE)
        self.creator = data.get('creator', None)
        self._assigner_type = data.get('assigner_organization_type', None)
        self._assigner_id = data.get('assigner_organization_id', None)
        self._assignee_type = data.get('assignee_organization_type', None)
        self._assignee_id = data.get('assignee_organization_id', None)
        self.contribution_method = get_contribution_method(data.get('method_id', None), data.get('contribution_fields', None))
        self._career_path = data.get('career_path', None)
        self._finish_time = data.get('finish_time', None)
        self._due_time = data.get('due_time', None)
        self._ui_annotations = data.get('ui_annotations', {})
        self._participation_limit = data.get('participation_limit', None)
        self._coverage_limit = data.get('coverage_limit', None)
        self._multiplier = data.get('multiplier', None)
        reward_info = data.get('reward', None)
        if reward_info:
            self._reward = CorpGoalReward(asset_id=reward_info['asset_id'], amount_per_unit=reward_info['amount_per_unit'])
        else:
            self._reward = None
        self._has_set_data = True

    @property
    def expiration_time(self):
        return DateToBlue(self.get_due_datetime())

    def set_contribution(self, progress, rewards_unclaimed):
        self._my_progress = progress
        if self._reward:
            self._reward.earned_capacity = progress
            self._reward.unclaimed_capacity = rewards_unclaimed
        self._has_fetched_contribution = True

    def has_fetched_contribution(self):
        return self._has_fetched_contribution

    def has_data(self):
        return self._has_set_data

    def get_id(self):
        return self.goal_id

    def get_creation_datetime(self):
        return self.created

    def get_completed_datetime(self):
        if self._finish_time:
            return self._finish_time

    def get_due_datetime(self):
        if self._due_time:
            return self._due_time

    def get_cloned_project_duration(self):
        if not self._due_time:
            return None
        duration = self.get_due_datetime() - self.get_creation_datetime()
        return duration

    def get_end_time(self):
        if self._due_time:
            return self.expiration_time
        if self._finish_time:
            return DateToBlue(self.get_completed_datetime())

    def get_participation_limit(self):
        return self._participation_limit

    def get_multiplier(self):
        return self._multiplier

    def get_multiplier_percentage(self):
        if self._multiplier:
            return eveformat.number(self._multiplier * 100, 0)

    def get_coverage_limit(self):
        return self._coverage_limit

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name

    def get_description(self):
        return self.description

    def set_description(self, new_description):
        self.description = new_description

    def get_desired_progress(self):
        return self.desired_progress

    def get_desired_progress_with_unit(self):
        return self._get_value_with_unit(self.desired_progress)

    def _get_value_with_unit(self, progress):
        return u'{} {}'.format(FormatNumeric(progress, useGrouping=True), self.get_unit()).strip()

    def get_current_progress(self):
        return self.current_progress

    def get_current_progress_with_unit(self):
        return self._get_value_with_unit(self.current_progress)

    def update_my_progress(self, added_progress):
        state_changed = False
        if self._my_progress == 0 and added_progress > 0:
            state_changed = True
        self._my_progress += added_progress
        if self._reward:
            had_unclaimed = self.has_unclaimed_reward()
            self._reward.earned_capacity = self._my_progress
            self._reward.unclaimed_capacity += added_progress
            on_goal_reward_earned(self.goal_id)
            if not state_changed:
                state_changed = had_unclaimed != self.has_unclaimed_reward()
        return state_changed

    def get_my_progress(self):
        return self._my_progress

    def has_personal_progress(self):
        if self.contribution_method.method_id == ContributionMethodTypes.MANUAL:
            return CanAuthorGoals()
        return True

    def get_remaining_progress(self):
        return max(0, self.get_desired_progress() - self.get_current_progress())

    def get_my_remaining_progress(self):
        if self.get_participation_limit():
            return min(self.get_remaining_progress(), max(0, self.get_participation_limit() - self.get_my_progress()))
        return self.get_remaining_progress()

    def get_my_total_progress(self):
        if self.get_participation_limit():
            return self.get_participation_limit()
        return self.get_desired_progress()

    def get_contribution_method(self):
        return self.contribution_method

    def set_current_progress(self, progress):
        if self.current_progress is not None and self.current_progress > progress:
            return
        self.current_progress = progress
        logger.info('Goal::set_current_progress: goal_id=%s, progress=%s', self.goal_id, progress)

    def get_progress_ratio(self):
        return float(self.get_current_progress()) / self.get_desired_progress()

    def get_my_progress_ratio(self):
        if self.get_participation_limit():
            return float(self.get_my_progress()) / self.get_participation_limit()
        return float(self.get_my_progress()) / self.get_desired_progress()

    def get_state(self):
        return self.state

    def get_state_label(self):
        return goalConst.state_labels[self.state]

    def get_ui_annotation(self, key):
        return self._ui_annotations.get(key, None)

    def complete(self):
        self.state = GoalState.COMPLETED
        self._finish_time = gametime.now()

    def close(self):
        self.state = GoalState.CLOSED
        self._finish_time = gametime.now()

    def expire(self):
        self.state = GoalState.EXPIRED
        self._finish_time = gametime.now()

    def is_active(self):
        return self.state == GoalState.ACTIVE

    def is_completed(self):
        return self.state == GoalState.COMPLETED

    def is_closed(self):
        return self.state == GoalState.CLOSED

    def is_expired(self):
        return self.state == GoalState.EXPIRED

    def get_assigner_organization(self):
        return (self._assigner_type, self._assigner_id)

    def get_assignee_organization(self):
        return (self._assignee_type, self._assignee_id)

    def get_creator(self):
        return self.creator

    def get_creator_name(self):
        return cfg.eveowners.Get(self.creator).ownerName

    def get_closest_solar_system_id(self):
        if self._closest_solar_system_id is None:
            self._update_closest_location()
        return self._closest_solar_system_id

    def get_location_ids(self):
        location_ids = self.contribution_method.solar_system
        if not location_ids:
            return []
        if not isinstance(location_ids, list):
            return [location_ids]
        return location_ids

    def get_location_id(self):
        location = self.contribution_method.location
        if location is None or isinstance(location, list):
            return
        return location

    def get_unit(self):
        return self.contribution_method.unit or ''

    def is_manual(self):
        return self.contribution_method.method_id == ContributionMethodTypes.MANUAL

    def is_ship_insurance(self):
        return self.contribution_method.method_id == ContributionMethodTypes.SHIP_INSURANCE

    @property
    def career_path(self):
        return self._career_path

    def get_drag_data(self):
        return [GoalDragData(self)]

    def has_rewards(self):
        if not self._reward:
            return False
        return bool(self._reward.amount_per_unit)

    def has_reached_participation_limit(self):
        if self._participation_limit is None:
            return False
        return self.get_participation_limit() <= self.get_my_progress()

    def get_total_isk(self):
        if not self._reward:
            return 0
        return self._reward.amount_per_unit * self.get_desired_progress()

    def get_total_remaining_isk(self):
        if not self._reward:
            return 0
        return self._reward.amount_per_unit * self.get_remaining_progress()

    def get_my_remaining_isk(self):
        if not self._reward:
            return 0
        if self.get_participation_limit():
            return self._reward.amount_per_unit * self.get_my_remaining_progress()
        return self.get_total_remaining_isk()

    def get_isk_per_contribution(self):
        if not self._reward:
            return 0
        return self._reward.amount_per_unit

    def get_earned_amount(self):
        if not self._reward:
            return 0
        return self._reward.earned_amount

    def get_claimed_amount(self):
        if not self._reward:
            return 0
        return self._reward.redeemed_amount

    def get_unclaimed_amount(self):
        if not self._reward:
            return 0
        return self._reward.claimable_amount

    def has_unclaimed_reward(self):
        return bool(self._reward and self._reward.unclaimed_capacity)

    def get_claimable_reward(self):
        if not self.has_unclaimed_reward():
            return None
        return self._reward

    def update_redeemed_capacity(self, capacity):
        if self._reward:
            had_unclaimed = self.has_unclaimed_reward()
            self._reward.unclaimed_capacity = max(0, self._reward.unclaimed_capacity - capacity)
            on_goal_reward_redeemed(self.goal_id, state_changed=had_unclaimed != self.has_unclaimed_reward())

    def _update_closest_location(self):
        solar_system = self.contribution_method.solar_system
        if solar_system is not None and isinstance(solar_system, list):
            closest_solar_system_id = get_closest_solarsystem_in_locations_from(session.solarsystemid2, set(solar_system), sm.GetService('map'), sm.GetService('clientPathfinderService'))[0]
        else:
            closest_solar_system_id = solar_system
        if self._closest_solar_system_id != closest_solar_system_id:
            self._closest_solar_system_id = closest_solar_system_id
            on_closest_solar_system_changed(self.goal_id, self._closest_solar_system_id)
