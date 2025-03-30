#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\acp.py
import uuid
from careergoals.client.career_goal_svc import get_career_goals_svc
from .base import Condition

class AcpPoints(Condition):
    atom_id = 604

    def __init__(self, minimum_amount = None, **kwargs):
        super(AcpPoints, self).__init__(**kwargs)
        self.minimum_amount = self.get_atom_parameter_value('minimum_amount', minimum_amount)

    def validate(self, **kwargs):
        acp_goals_controller = get_career_goals_svc().get_goal_data_controller()
        acp_points = acp_goals_controller.get_overall_progress()
        return acp_points >= self.minimum_amount

    @classmethod
    def get_subtitle(cls, minimum_amount = None, **kwargs):
        return str(cls.get_atom_parameter_value('minimum_amount', minimum_amount))


class HasClaimableAcpReward(Condition):
    atom_id = 605

    def validate(self, **kwargs):
        acp_goals_controller = get_career_goals_svc().get_goal_data_controller()
        return bool(acp_goals_controller.get_claimable_rewards_count())


class HasCompletedAcpGoal(Condition):
    atom_id = 606

    def __init__(self, goal_id = None, **kwargs):
        super(HasCompletedAcpGoal, self).__init__(**kwargs)
        self.goal_id = goal_id

    def validate(self, **kwargs):
        if not self.goal_id:
            return False
        acp_goals_controller = get_career_goals_svc().get_goal_data_controller()
        goal_id = self.goal_id if isinstance(self.goal_id, uuid.UUID) else uuid.UUID(self.goal_id)
        goal = acp_goals_controller.get_goal(goal_id)
        if goal:
            return goal.is_completed()
        return False

    @classmethod
    def get_subtitle(cls, goal_id = None, **kwargs):
        return str(goal_id)
