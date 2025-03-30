#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\storylines\client\objectives\base\tracker.py
from storylines.client.objectives.base.goal import StorylineGoal
from storylines.client.objectives.base.objective import StorylineObjective
from storylines.client.objectives.loader import GoalsData, ObjectivesData
from typeutils.metas import Singleton

class ObjectiveTracker(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.current_goal = None
        self.current_objective = None
        self.goals = {}

    def _find_goal_by_id(self, goal_id):
        if goal_id in self.goals:
            return self.goals[goal_id]
        goal_data = GoalsData().get_goal_by_id(goal_id)
        goal = StorylineGoal(goal_id=goal_id, title=goal_data.title, title_icon=getattr(goal_data, 'icon', None))
        self.goals[goal_id] = goal
        return goal

    def _create_objective(self, objective_id, objective_values = None):
        objective_data = ObjectivesData().get_objective_by_id(objective_id)
        objective = StorylineObjective(objective_id=objective_id, title=objective_data.title, text=objective_data.text, title_icon=getattr(objective_data, 'titleIcon', None), icon=getattr(objective_data, 'icon', None), icon_type_id=getattr(objective_data, 'iconTypeID', None), dungeon_id=getattr(objective_data, 'dungeonID', None), objective_values=objective_values)
        return objective

    def get_goals(self):
        if self.current_goal:
            return [self.current_goal]
        return []

    def get_objectives(self):
        if self.current_objective:
            return [self.current_objective]
        return []

    def get_objective(self):
        return self.current_objective

    def set_objective(self, goal_id, objective_id, completed = False, warp_action = None, objective_values = None):
        if self.current_objective:
            if self.current_objective.objective_id == objective_id:
                return
            self.current_objective.Update(is_active=False)
        try:
            self.current_objective = self._create_objective(objective_id, objective_values)
            self.current_goal = self._find_goal_by_id(goal_id)
        except (AttributeError, KeyError):
            self.current_objective = None
            self.current_goal = None

        if self.current_goal and self.current_objective:
            self.current_goal.Update(objectives=self.get_objectives())
            self.current_objective.Update(is_active=not completed, warp_action=warp_action)
        self._notify_of_update()

    def skip_mission(self):
        pass

    def _notify_of_update(self):
        raise NotImplementedError('Must implement notify_of_update in derived class')
