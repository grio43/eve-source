#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\acp.py
from careergoals.client.career_goal_svc import get_career_goals_svc
from careergoals.client.signal import on_goal_progress_changed, on_goal_completed
from .base import Event

class AcpGoalCompleted(Event):
    atom_id = 607

    def _register(self):
        on_goal_completed.connect(self._on_goal_completed)

    def _unregister(self):
        on_goal_completed.disconnect(self._on_goal_completed)

    def _on_goal_completed(self, goal_id):
        self.invoke(goal_id=goal_id)


class TotalAcpPointsChanged(Event):
    atom_id = 608

    def _register(self):
        on_goal_progress_changed.connect(self._on_goal_progress_changed)

    def _unregister(self):
        on_goal_progress_changed.disconnect(self._on_goal_progress_changed)

    def _on_goal_progress_changed(self, goal_id):
        acp_goals_controller = get_career_goals_svc().get_goal_data_controller()
        if not acp_goals_controller.is_overall_goal(goal_id):
            return
        self.invoke()
