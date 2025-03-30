#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\careergoals\client\career_goal_svc.py
import logging
import uuid
from careergoals.client.goal_data_controller import GoalDataController
from careergoals.client.messenger.event_messenger import PublicCareerGoalEventMessenger
from careergoals.client.messenger.notice_messenger import PublicCareerGoalNoticeMessenger
import careergoals.client.messenger.messenger_signal as messenger_signal
_instance = None

def get_career_goals_svc():
    global _instance
    if _instance is None:
        _instance = _CareerGoalsSvc()
    return _instance


logger = logging.getLogger(__name__)
FEATURE_FALLBACK = False

class _CareerGoalsSvc(object):
    __startupdependencies__ = ['publicGatewaySvc', 'machoNet']
    __notifyevents__ = ['OnSessionReset', 'OnSessionChanged']

    def __init__(self):
        self._public_gateway = sm.GetService('publicGatewaySvc')
        self._goal_data_controller = GoalDataController()
        self._event_messenger = PublicCareerGoalEventMessenger(self._public_gateway)
        self._notice_messenger = PublicCareerGoalNoticeMessenger(self._public_gateway)
        messenger_signal.on_goal_progressed.connect(self._on_progressed_notice)
        messenger_signal.on_goal_completed.connect(self._on_completed_notice)
        sm.RegisterNotify(self)

    def __del__(self):
        messenger_signal.on_goal_progressed.disconnect(self._on_progressed_notice)
        messenger_signal.on_goal_completed.disconnect(self._on_completed_notice)

    def get_goal_data_controller(self):
        return self._goal_data_controller

    def emit_goal_tracked(self, goal_id):
        self._event_messenger.goal_tracked(goal_id)

    def emit_career_selected(self, goal_id):
        self._event_messenger.career_selected(goal_id)

    def emit_group_selected(self, group_name, career_name):
        self._event_messenger.group_selected(group_name, career_name)

    def emit_goal_selected(self, goal_id):
        self._event_messenger.goal_selected(goal_id)

    def claim_reward(self, goal_id, reward_label):
        self._goal_data_controller.claim_reward(goal_id, reward_label)

    def _on_progressed_notice(self, goal_id, progress):
        self._goal_data_controller.update_local_goal_progress(goal_id, progress)

    def _on_completed_notice(self, goal_id):
        self._goal_data_controller.mark_local_goal_completed(goal_id)

    def OnSessionChanged(self, _isRemote, _sess, change):
        if 'charid' in change:
            self._goal_data_controller.clear_state_cache()
            self._goal_data_controller.clear_local_cache()

    def OnSessionReset(self):
        self._goal_data_controller.clear_state_cache()
        self._goal_data_controller.clear_local_cache()
