#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\storylines\client\objectives\loader.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import objectivesLoader
except ImportError:
    objectivesLoader = None

try:
    import goalsLoader
except ImportError:
    goalsLoader = None

class ObjectivesData(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/objectives.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/objectives.fsdbinary'
    __loader__ = objectivesLoader

    @classmethod
    def get_objective_by_id(cls, objective_id):
        return cls.GetData().get(objective_id, None)

    @classmethod
    def get_name(cls, objective_id):
        objective = cls.get_objective_by_id(objective_id)
        if objective:
            return objective.name
        return ''


class GoalsData(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/goals.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/goals.fsdbinary'
    __loader__ = goalsLoader

    @classmethod
    def get_goal_by_id(cls, goal_id):
        return cls.GetData().get(goal_id, None)

    @classmethod
    def get_name(cls, goal_id):
        goal = cls.get_goal_by_id(goal_id)
        if goal:
            return goal.name
        return ''
