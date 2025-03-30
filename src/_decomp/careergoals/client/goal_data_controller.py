#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\careergoals\client\goal_data_controller.py
import uuid
from carbon.common.script.sys.serviceConst import ROLE_QA
from careergoals.client import signal, errors
from careergoals.client.const import RewardLabel
from careergoals.client.goal import Goal
from careergoals.client.goal_data_grouping import create_career_path_goal_groups, OverallGoalGroup
from careergoals.client.goal_definition import GoalDefinition
import characterdata.careerpathconst as cpConst
from careergoals.client.messenger.request_messenger import PublicCareerGoalRequestMessenger
from careergoals.client.reward_definition import LegacyRewards

class GoalDataController(object):

    def __init__(self):
        self._public_gateway = sm.GetService('publicGatewaySvc')
        self._request_messenger = PublicCareerGoalRequestMessenger(self._public_gateway)
        self._goal_definitions_per_career = None
        self._overall_goal_definitions = None
        self._goals = None
        self._local_claimed_rewards = {}
        self._local_completed_goals = []
        self._legacy_rewards = LegacyRewards()

    def are_goals_loaded(self):
        return self._are_definitions_loaded() and self._are_states_loaded()

    def prime_definitions_and_states(self):
        self._load_states()

    def claim_reward(self, goal_id, reward_label):
        if not self._public_gateway.is_available():
            return
        success = self._request_messenger.claim_reward_request(goal_id)
        self.mark_local_reward_label_claimed(goal_id, reward_label, success)

    def _load_definitions(self):
        if not self._are_definitions_loaded():
            if not self._legacy_rewards.has_rewards():
                self._legacy_rewards.get_rewards_from_server()
            goals = self._request_messenger.get_goals_and_progress_request()
            self._goal_definitions_per_career = create_career_path_goal_groups()
            self._overall_goal_definitions = OverallGoalGroup()
            for definition_data in goals:
                goal_definition = GoalDefinition(self._legacy_rewards, definition_data)
                if goal_definition.career == cpConst.career_path_none:
                    self._overall_goal_definitions.add_goal_definition(goal_definition)
                elif goal_definition.group_id:
                    self._goal_definitions_per_career[goal_definition.career].add_goal_definition(goal_definition)
                else:
                    self._goal_definitions_per_career[goal_definition.career].career_path_goal_definition = goal_definition

            for each in self._goal_definitions_per_career.itervalues():
                each.sort_goal_definitions()

            signal.on_definitions_loaded()

    def _are_definitions_loaded(self):
        return self._goal_definitions_per_career is not None and self._overall_goal_definitions is not None and self._legacy_rewards.has_rewards()

    def _get_goal_definition(self, goal_id, career_id = None, group_id = None):
        self._load_definitions()
        if career_id is None:
            goal_definition = self._overall_goal_definitions.get_goal_definition(goal_id)
            if goal_definition is not None:
                return goal_definition
            for _, goals_per_career in self._goal_definitions_per_career.iteritems():
                found_goal_definition = goals_per_career.get_goal_definition(goal_id)
                if found_goal_definition is not None:
                    return found_goal_definition

        else:
            if group_id is None:
                career_path_goal_definition = self._goal_definitions_per_career[career_id].career_path_goal_definition
                if career_path_goal_definition.goal_id == goal_id:
                    return career_path_goal_definition
            return self._goal_definitions_per_career[career_id].get_goal_definition(goal_id, group_id)

    def _load_states(self):
        self._load_definitions()
        if self._goals is None:
            self._goals = {}
            goals = self._request_messenger.get_goals_and_progress_request()
            for state_data in goals:
                goal_id = uuid.UUID(bytes=state_data.goal.uuid)
                goal_definition = self._get_goal_definition(goal_id, None, None)
                if not goal_definition:
                    raise errors.CareerGoalDefinitionNotFound
                claim_state_per_reward_label = {RewardLabel.ALPHA: state_data.attributes.claimed}
                self._goals[goal_id] = Goal(goal_definition, state_data.attributes.progress, state_data.attributes.completed, claim_state_per_reward_label)

            signal.on_states_loaded()

    def _are_states_loaded(self):
        return self._goals is not None

    def get_all_goals(self):
        self._load_states()
        return self._goals

    def get_goal(self, goal_id):
        self._load_states()
        return self._goals.get(goal_id, None)

    def get_career_path_total_progress(self, career_path_id):
        self._load_states()
        all_career_goal_definitions = self._goal_definitions_per_career[career_path_id].get_all_career_goal_definitions()
        total_progress = 0
        for goal_definition in all_career_goal_definitions:
            goal = self.get_goal(goal_definition.goal_id)
            if goal:
                total_progress += goal_definition.progress

        return total_progress

    def get_career_path_goal(self, career_path_id):
        self._load_states()
        return self._goals.get(self._goal_definitions_per_career[career_path_id].career_path_goal_definition.goal_id, None)

    def get_overall_goals(self):
        self._load_states()
        return [ self._goals.get(x.goal_id, None) for x in self._overall_goal_definitions.goal_definitions ]

    def get_goals_in_group(self, career_path_id, group_id):
        self._load_states()
        if career_path_id in self._goal_definitions_per_career:
            return [ self._goals.get(x.goal_id, None) for x in self._goal_definitions_per_career[career_path_id].get_goal_definitions_in_group(group_id) ]
        else:
            return []

    def is_career_path_goal(self, goal_id, career_path_id):
        self._load_definitions()
        if career_path_id is None:
            return any([ x == goal_id for x in [ y.career_path_goal_definition.goal_id for y in self._goal_definitions_per_career.values() ] ])
        elif career_path_id not in self._goal_definitions_per_career:
            return False
        else:
            return goal_id == self._goal_definitions_per_career[career_path_id].career_path_goal_definition.goal_id

    def is_overall_goal(self, goal_id):
        self._load_definitions()
        return any([ x.goal_id == goal_id for x in self._overall_goal_definitions.goal_definitions ])

    def get_overall_progress(self):
        self._load_states()
        if len(self.get_overall_goals()) > 0:
            return self.get_overall_goals()[-1].progress
        return 0

    def get_max_overall_target(self):
        self._load_definitions()
        return self._overall_goal_definitions.get_max_target()

    def are_all_overall_goals_completed(self):
        self._load_states()
        return all([ g.is_completed() for g in self.get_overall_goals() ])

    def is_activity_completed(self, career_path_id, group_id):
        self._load_states()
        goals = self.get_goals_in_group(career_path_id, group_id)
        return all([ g.is_completed() for g in goals ])

    def get_goals_with_claimable_rewards(self):
        self._load_states()
        return [ g for g in self.get_all_goals().itervalues() if g.has_unclaimed_rewards() ]

    def get_claimable_rewards_count(self):
        self._load_states()
        claimable_rewards_count = 0
        for goal in self.get_goals_with_claimable_rewards():
            claimable_rewards_count += len(goal.get_unclaimed_reward_labels())

        return claimable_rewards_count

    def get_local_claimed_rewards(self):
        return self._local_claimed_rewards

    def update_local_goal_progress(self, goal_id, progress):
        self._load_states()
        goal = self.get_goal(goal_id)
        if goal:
            goal.update_local_progress(progress)
            signal.on_goal_progress_changed(goal_id, progress)

    def mark_local_goal_completed(self, goal_id):
        self._load_states()
        goal = self.get_goal(goal_id)
        if goal:
            goal.mark_local_completed()
            self._local_completed_goals.append(goal_id)
            signal.on_goal_progress_changed(goal_id, goal.definition.target_value)
            signal.on_goal_completed(goal_id)

    def mark_local_reward_label_claimed(self, goal_id, reward_label, success):
        self._load_states()
        if not success:
            signal.on_reward_claimed_failed(goal_id, reward_label)
        else:
            if goal_id not in self._local_claimed_rewards:
                self._local_claimed_rewards[goal_id] = []
            self._local_claimed_rewards[goal_id].append(reward_label)
            goal = self.get_goal(goal_id)
            if goal:
                goal.mark_local_reward_label_claimed(reward_label)
                signal.on_reward_claimed(goal_id, reward_label)

    def get_local_completed_goals_per_career(self):
        self._load_states()
        result = {}
        for goal_id in self._local_completed_goals:
            goal = self.get_goal(goal_id)
            if goal.definition.career not in result:
                result[goal.definition.career] = []
            result[goal.definition.career].append(goal)

        return result

    def clear_state_cache(self):
        self._goals = None

    def clear_definitions_cache(self):
        self._goal_definitions_per_career = None
        self._overall_goal_definitions = None
        self._legacy_rewards = LegacyRewards()
        self.clear_state_cache()
        self.clear_local_cache()

    def clear_local_cache(self):
        self._local_claimed_rewards = {}
        self._local_completed_goals = []
        self.clear_local_completed_goals()

    def clear_local_completed_goals(self):
        self._local_completed_goals = []

    def admin_complete_goal(self, goal_id):
        if not session.role & ROLE_QA:
            return
        self._request_messenger.admin_complete_goal_request(goal_id)

    def admin_progress_goal(self, goal_id, progress):
        if not session.role & ROLE_QA:
            return
        self._request_messenger.admin_progress_goal_request(goal_id, progress)
