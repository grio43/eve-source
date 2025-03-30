#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\careergoals\client\goal_data_grouping.py
from collections import defaultdict
import characterdata.careerpathconst as cpConst
from goal_definition import GoalDefinition

def create_career_path_goal_groups():
    goal_definitions_per_career = {}
    for cp in cpConst.career_paths:
        if cp != cpConst.career_path_none:
            goal_definitions_per_career[cp] = CareerPathGoalGroup()

    return goal_definitions_per_career


class CareerPathGoalGroup(object):

    def __init__(self):
        self._career_path_goal_definition = None
        self._goal_definitions_per_group = defaultdict(list)

    @property
    def career_path_goal_definition(self):
        return self._career_path_goal_definition

    @career_path_goal_definition.setter
    def career_path_goal_definition(self, value):
        self._career_path_goal_definition = value

    def add_goal_definition(self, goal_definition):
        self._goal_definitions_per_group[goal_definition.group_id].append(goal_definition)

    def get_goal_definition(self, goal_id, group_id = None):
        if group_id is None:
            if self._career_path_goal_definition.goal_id == goal_id:
                return self._career_path_goal_definition
        for _, goal_definitions in self._goal_definitions_per_group.iteritems():
            for goal_definition in goal_definitions:
                if goal_definition.goal_id == goal_id:
                    return goal_definition

    def get_goal_definitions_in_group(self, group_id):
        return self._goal_definitions_per_group.get(group_id, [])

    def get_all_career_goal_definitions(self):
        all_goal_definitions = []
        for _, goal_definitions in self._goal_definitions_per_group.iteritems():
            all_goal_definitions.extend(goal_definitions)

        return all_goal_definitions

    def sort_goal_definitions(self):
        sorted_dict = {}
        for activity_id, goal_definitions in self._goal_definitions_per_group.iteritems():
            sorted_dict[activity_id] = sorted(goal_definitions)

        self._goal_definitions_per_group = sorted_dict


class OverallGoalGroup(object):

    def __init__(self):
        self._goal_definitions = []

    @property
    def goal_definitions(self):
        return self._goal_definitions

    def get_goal_definition(self, goal_id):
        for goal_definition in self.goal_definitions:
            if goal_definition.goal_id == goal_id:
                return goal_definition

    def add_goal_definition(self, goal_definition):
        self._goal_definitions.append(goal_definition)
        self._sort()

    def get_max_target(self):
        if len(self._goal_definitions) > 0:
            return self._goal_definitions[-1].target_value
        return 0

    def _sort(self):
        if len(self._goal_definitions) > 0:
            self._goal_definitions = sorted(self._goal_definitions)
