#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\storylines\client\objectives\controller.py
from storylines.client.objectives.trackers.airnpetracker import AirNpeObjectiveTracker
TRACKERS = {'AirNpe': AirNpeObjectiveTracker()}
DEFAULT_TRACKER = TRACKERS['AirNpe']

def _get_tracker(tracker_id):
    return TRACKERS.get(tracker_id, DEFAULT_TRACKER)


def set_objective_in_tracker(tracker_id, goal_id, objective_id, completed, warp_action, objective_values):
    tracker = _get_tracker(tracker_id)
    tracker.set_objective(goal_id, objective_id, completed, warp_action, objective_values)


def clear_objectives_in_tracker(tracker_id):
    tracker = _get_tracker(tracker_id)
    tracker.set_objective(goal_id=None, objective_id=None)
