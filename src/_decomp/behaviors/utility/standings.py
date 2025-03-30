#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\standings.py
from behaviors.utility.blackboards import get_response_thresholds
from behaviors.utility.owner import get_owner_id
from npcs.common.standings import classify_standings
from npcs.server.standings import get_standings_from_npc_to_item

def get_standings_between(task, to_id):
    return get_standings_from_npc_to_item(_get_standing_manager(task), get_owner_id(task), to_id)


def classify_standings_between(task, to_id):
    standing_thresholds = get_response_thresholds(task)
    return classify_standings(standing_thresholds.hostile_response_threshold, standing_thresholds.friendly_response_threshold, get_standings_between(task, to_id))


def _get_standing_manager(task):
    return task.context.ballpark.broker.standingMgr


def is_hostile_towards(task, to_id):
    standing_thresholds = get_response_thresholds(task)
    standings = get_standings_between(task, to_id)
    return standings < standing_thresholds.hostile_response_threshold
