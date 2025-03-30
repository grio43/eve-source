#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\entitystandings.py
from behaviors.const.combat import FW_ATTACK_NOT_SAME_FACTION, FW_ATTACK_ALL_ENEMIES, FW_ATTACK_INSURGENCY_ENEMIES
from eve.client.script.parklife import states as state
from eve.common.script.util.facwarCommon import IsCombatEnemyFaction, IsInsurgencyEnemyFaction, IsPirateFWFaction, IsAntiPirateFaction, HasPirateVsAntiPirateRelationship
from npcs.client.entitystandings import get_standing_between_npc_and_player
from npcs.common.owner import get_npc_faction
from npcs.common.standings import STANDINGS_HOSTILE, STANDINGS_NEUTRAL, STANDINGS_FRIENDLY
from spacecomponents.common.helper import GetEntityStandingsAttributes
import logging
logger = logging.getLogger(__name__)
ICON_COLOR_GOOD = (0.0, 0.4, 1.0)
ICON_COLOR_NEUTRAL = (1.0, 1.0, 1.0)
ICON_COLOR_BAD = (1.0, 0.1, 0.1)
HINT_HOSTILE_NPC = 'Tooltips/Overview/HostileNPC'
HINT_NEUTRAL_NPC = 'Tooltips/Overview/NeutralNPC'
ICON_SORT_ORDER_HINT_BY_STANDINGS_CLASS = {STANDINGS_HOSTILE: (ICON_COLOR_BAD, 1, HINT_HOSTILE_NPC),
 STANDINGS_NEUTRAL: (ICON_COLOR_NEUTRAL, 3, HINT_NEUTRAL_NPC),
 STANDINGS_FRIENDLY: (ICON_COLOR_GOOD, 5, None)}

def get_icon_color_sort_value_and_hint_for_fw_attack_method(slim_item, warfaction_id, fw_attack_method):
    faction_id = get_npc_faction(slim_item.ownerID)
    standingClass = STANDINGS_NEUTRAL
    if fw_attack_method == FW_ATTACK_NOT_SAME_FACTION:
        if faction_id == warfaction_id:
            standingClass = STANDINGS_FRIENDLY
        else:
            standingClass = STANDINGS_HOSTILE
    elif fw_attack_method == FW_ATTACK_ALL_ENEMIES:
        if IsCombatEnemyFaction(faction_id, warfaction_id):
            standingClass = STANDINGS_HOSTILE
        elif HasPirateVsAntiPirateRelationship(warfaction_id, faction_id):
            standingClass = STANDINGS_HOSTILE
        else:
            standingClass = STANDINGS_FRIENDLY
    elif fw_attack_method == FW_ATTACK_INSURGENCY_ENEMIES:
        if IsInsurgencyEnemyFaction(faction_id, warfaction_id):
            standingClass = STANDINGS_HOSTILE
        elif HasPirateVsAntiPirateRelationship(warfaction_id, faction_id):
            standingClass = STANDINGS_HOSTILE
        else:
            standingClass = STANDINGS_FRIENDLY
    color, order, hint = ICON_SORT_ORDER_HINT_BY_STANDINGS_CLASS[standingClass]
    return (color, order, hint)


def get_icon_color_sort_value_and_hint_for_owner_standing(slim_item, to_id):
    standings = get_standing_between_npc_and_player(slim_item.ownerID, to_id)
    if not hasattr(slim_item, 'hostile_response_threshold'):
        logger.error('EntityStanding::entity=%s does not have response threshold set', slim_item.typeID)
        return ICON_SORT_ORDER_HINT_BY_STANDINGS_CLASS[STANDINGS_NEUTRAL]
    return _get_icon_color_and_hint_from_entity_standing_response(slim_item, standings)


def _get_icon_color_and_hint_from_entity_standing_response(slim_item, standings):
    hostile_response_threshold = slim_item.hostile_response_threshold
    friendly_response_threshold = slim_item.friendly_response_threshold
    if hostile_response_threshold is None:
        standing_threshold = GetEntityStandingsAttributes(slim_item.typeID)
        hostile_response_threshold = standing_threshold.hostileResponseThreshold
        friendly_response_threshold = standing_threshold.friendlyResponseThreshold
        logger.error('failed getting standing thresholds from slim_item, defaulting to hostile=%s and friendly=%s for type=%s', hostile_response_threshold, friendly_response_threshold, slim_item.typeID)
    if standings <= hostile_response_threshold:
        color, order, hint = ICON_SORT_ORDER_HINT_BY_STANDINGS_CLASS[STANDINGS_HOSTILE]
    elif standings >= friendly_response_threshold:
        color, order, hint = ICON_SORT_ORDER_HINT_BY_STANDINGS_CLASS[STANDINGS_FRIENDLY]
    else:
        color, order, hint = ICON_SORT_ORDER_HINT_BY_STANDINGS_CLASS[STANDINGS_NEUTRAL]
    if color != ICON_COLOR_BAD:
        attacking = sm.GetService('stateSvc').GetState(slim_item.itemID, state.threatAttackingMe)
        if attacking:
            color = ICON_COLOR_BAD
            order = 1
    return (color, order, hint)
