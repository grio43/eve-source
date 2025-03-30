#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\battlefield.py
from ballpark.fleets.fleet_types import SUPPORTED_FLEET_TYPES
from behaviors.utility.awareness import get_fleet_awareness
from behaviors.utility.entity_groups import get_entity_group_member_ids
from ccpProfile import TimedFunction
import logging
logger = logging.getLogger(__name__)

def get_npc_cost_by_group_id(task, entity_group_id, spawn_table_id):
    if not entity_group_id:
        return 0
    member_ids = get_entity_group_member_ids(task, entity_group_id)
    return task.context.entityLocation.GetNpcFleetReporter().get_fleet_cost_for_item_ids(spawn_table_id, member_ids)


def get_player_cost_for_item_ids(task, item_ids):
    return sum(task.context.entityLocation.GetPlayerFleetReporter().get_fleet_cost_by_item_ids(item_ids).values())


def get_player_fleet_reporter(task):
    return task.context.entityLocation.GetPlayerFleetReporter()


def get_npc_fleet_reporter(task):
    return task.context.entityLocation.GetNpcFleetReporter()


def generate_player_fleet_report(task, spawn_pool_id):
    try:
        return get_player_fleet_reporter(task).generate(spawn_pool_id)
    except:
        logger.exception('failed to generate a player fleet report')
        raise


def get_total_fleet_points(task, spawn_pool_id, spawn_table_id):
    try:
        awareness = get_fleet_awareness(task, spawn_pool_id)
        total_npc_fleet_cost = get_npc_fleet_reporter(task).get_total_fleet_points(awareness, spawn_table_id, spawn_pool_id)
        return total_npc_fleet_cost
    except:
        logger.exception('failed to get the total npc fleet points')
        raise


@TimedFunction('behaviors::utility::battlefield::get_match_result')
def get_match_result(task, spawn_table_id, fleet_type, player_report, spawn_point_multiplier, support_points, supported_fleet_points, entity_group_id_by_fleet_type):
    fleet_report = player_report.fleet_by_type[fleet_type]
    player_fleet_cost = fleet_report.fleet_cost
    if supported_fleet_points > 0 and fleet_type in SUPPORTED_FLEET_TYPES:
        support_fleet_contribution = int(player_fleet_cost / float(supported_fleet_points) * support_points)
    else:
        support_fleet_contribution = 0
    player_fleet_cost = int((fleet_report.fleet_cost + support_fleet_contribution) * spawn_point_multiplier)
    entity_group_id = entity_group_id_by_fleet_type.get(fleet_type)
    if not entity_group_id:
        npc_fleet_cost = 0
    else:
        npc_fleet_cost = get_npc_cost_by_group_id(task, entity_group_id, spawn_table_id)
    match_result = {'fleet_type': fleet_type,
     'player_fleet_points': player_fleet_cost,
     'npc_fleet_points': npc_fleet_cost,
     'item_ids': fleet_report.item_ids}
    return match_result
