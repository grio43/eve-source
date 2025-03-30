#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\completion_convenience\button_blocker.py
from jobboard.client.features.daily_goals.completion_convenience import completion_convenience_signals as cc_signals
import dailygoals.client.goalSignals as dailyGoalSignals
_instance = None

def get_button_blocker():
    global _instance
    if not _instance:
        _instance = CompletionConvenienceButtonBlocker()
    return _instance


class CompletionConvenienceButtonBlocker(object):

    def __init__(self):
        self._current_goal_id = None
        dailyGoalSignals.on_pay_for_completion_successful.connect(self._on_successful)
        dailyGoalSignals.on_pay_for_completion_failed.connect(self._on_failed)

    def process_started(self, goal_id):
        self._current_goal_id = goal_id
        cc_signals.buttons_blocked(goal_id)

    @property
    def is_blocked(self):
        return self._current_goal_id is not None

    @property
    def current_goal_id(self):
        return self._current_goal_id

    def _on_successful(self, goal_id):
        self._current_goal_id = None
        cc_signals.buttons_unblocked(goal_id)

    def _on_failed(self, goal_id, status_code):
        self._current_goal_id = None
        cc_signals.buttons_unblocked(goal_id)
