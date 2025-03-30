#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\npcs\client\entitystandings.py
from eve.common.lib.appConst import factionUnknown
from eve.common.script.sys import idCheckers
from npcs.common.owner import get_npc_faction
STANDINGS_NEUTRAL = 0.0

def get_standing_between_npc_and_player(from_id, to_id):
    faction_id = get_npc_faction(from_id)
    if faction_id == factionUnknown:
        return 0.0
    return sm.GetService('standing').GetStandingWithSkillBonus(faction_id, to_id)


def is_npc_hostile(hostile_response_threshold):
    return hostile_response_threshold > STANDINGS_NEUTRAL


def is_npc_hostile_towards_player(entity_slim_item, to_id):
    standings = get_standing_between_npc_and_player(entity_slim_item.ownerID, to_id)
    return standings <= entity_slim_item.hostile_response_threshold


def is_hostile_npc_target(slim_item):
    if not slim_item or not idCheckers.IsNPC(slim_item.ownerID) or not is_npc_hostile(slim_item.hostile_response_threshold):
        return False
    return is_npc_hostile_towards_player(slim_item, session.charid)
