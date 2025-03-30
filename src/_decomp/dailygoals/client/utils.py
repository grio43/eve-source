#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dailygoals\client\utils.py
import uuid
import logging
from dailygoals.client.const import RewardType
from eveProto.monolith_converters.units import get_single_value_from_split_precision_message
from goals.common.goalConst import CAREER_PATH_IDS, ContributionMethodTypes, ON_BEHALF_OF_CORP, ON_BEHALF_OF_SELF
from inventorycommon.const import typeskillpoints10000, typeskillpoints25000, typeskillpoints50000, typeskillpoints75000, typeskillpoints100000, typeskillpoints150000, typeskillpoints250000, typeskillpoints500000, typeskillpoints750000
logger = logging.getLogger('dailygoals')

def format_goal_from_payload(goal_id, goal_attributes, goal_progress, earnings, paid_completion = False):
    try:
        contribution_method_id, contribution_fields = _format_contribution_config(goal_attributes.contribution_configuration)
    except Exception as e:
        logger.exception(e)
        return None

    formatted_goal = {'goal_id': goal_id,
     'category': goal_attributes.category,
     'career_id': CAREER_PATH_IDS[goal_attributes.career],
     'assigner_id': goal_attributes.assigner.sequential,
     'contribution_method_id': contribution_method_id,
     'contribution_fields': contribution_fields,
     'name_id': goal_attributes.name_message.sequential,
     'desc_id': goal_attributes.description_message.sequential,
     'help_text_id': goal_attributes.help_text_message.sequential,
     'target': goal_attributes.target,
     'active_after': goal_attributes.active_after.ToDatetime(),
     'active_until': goal_attributes.active_until.ToDatetime(),
     'progress': goal_progress,
     'rewards': [],
     'has_earnings': bool(earnings),
     'omega_restricted_earnings': earnings[0].omega_required if earnings else goal_attributes.omega,
     'is_omega': goal_attributes.omega,
     'paid_completion': paid_completion}
    for payment in goal_attributes.payment:
        reward_info = get_reward_info_from_unit(payment.unit)
        if not reward_info:
            continue
        reward_info['asset_id'] = uuid.UUID(bytes=payment.asset.uuid)
        formatted_goal['rewards'].append(reward_info)

    return formatted_goal


def get_reward_info_from_unit(unit):
    reward_info = {}
    if unit.HasField('isk'):
        reward_info['reward_type'] = RewardType.ISK
        reward_info['amount'] = get_single_value_from_split_precision_message(unit.isk.amount)
    elif unit.HasField('lp'):
        reward_info['reward_type'] = RewardType.LOYALTY_POINTS
        reward_info['amount'] = unit.lp.amount.amount
    elif unit.HasField('sp'):
        reward_info['reward_type'] = RewardType.SKILL_POINTS
        reward_info['amount'] = unit.sp.amount
    elif unit.HasField('plex'):
        reward_info['reward_type'] = RewardType.PLEX
        reward_info['amount'] = unit.plex.amount.total_in_cents / 100
    elif unit.HasField('item'):
        reward_info['reward_type'] = RewardType.ITEM
        reward_info['amount'] = unit.item.amount
        reward_info['item_type_id'] = unit.item.type.sequential
    return reward_info


def _format_contribution_config(config):
    if config.HasField('kill_npc'):
        methods = _construct_kill_npc_dict_from_proto(config.kill_npc.contribution_methods)
        return (ContributionMethodTypes.KILL_NPC, methods[0] if len(methods) > 0 else {})
    if config.HasField('damage_ship'):
        methods = _construct_damage_ship_dict_from_proto(config.damage_ship.contribution_methods)
        return (ContributionMethodTypes.DAMAGE_SHIP, methods[0] if len(methods) > 0 else {})
    if config.HasField('mine_ore'):
        methods = _construct_mine_ore_dict_from_proto(config.mine_ore.contribution_methods)
        return (ContributionMethodTypes.MINE_ORE, methods[0] if len(methods) > 0 else {})
    if config.HasField('fw_capture'):
        methods = _construct_capture_fw_complex_dict_from_proto(config.fw_capture.contribution_methods)
        return (ContributionMethodTypes.CAPTURE_FACWAR_COMPLEX, methods[0] if len(methods) > 0 else {})
    if config.HasField('fw_defend'):
        methods = _construct_defend_fw_complex_dict_from_proto(config.fw_defend.contribution_methods)
        return (ContributionMethodTypes.DEFEND_FACWAR_COMPLEX, methods[0] if len(methods) > 0 else {})
    if config.HasField('remote_shield_repair'):
        methods = _construct_remote_repair_dict_from_proto(config.remote_shield_repair.contribution_methods)
        return (ContributionMethodTypes.REMOTE_REPAIR_SHIELD, methods[0] if len(methods) > 0 else {})
    if config.HasField('remote_armor_repair'):
        methods = _construct_remote_repair_dict_from_proto(config.remote_armor_repair.contribution_methods)
        return (ContributionMethodTypes.REMOTE_REPAIR_ARMOR, methods[0] if len(methods) > 0 else {})
    if config.HasField('scan_signature'):
        methods = _construct_scan_signature_dict_from_proto(config.scan_signature.contribution_methods)
        return (ContributionMethodTypes.SCAN_SIGNATURE, methods[0] if len(methods) > 0 else {})
    if config.HasField('install_manufacturing_job'):
        methods = _construct_install_manufacturing_job_dict_from_proto(config.install_manufacturing_job.contribution_methods)
        return (ContributionMethodTypes.MANUFACTURE_ITEM, methods[0] if len(methods) > 0 else {})
    if config.HasField('complete_daily_goal'):
        methods = _construct_complete_goals_dict_from_proto(config.complete_daily_goal.contribution_methods)
        return (ContributionMethodTypes.COMPLETE_GOAL, methods[0] if len(methods) > 0 else {})
    if config.HasField('salvage_wreck'):
        methods = _construct_salvage_wreck_dict_from_proto(config.salvage_wreck.contribution_methods)
        return (ContributionMethodTypes.SALVAGE_WRECK, methods[0] if len(methods) > 0 else {})
    if config.HasField('earn_loyalty_points'):
        methods = _construct_earn_loyalty_points_dict_from_proto(config.earn_loyalty_points.contribution_methods)
        return (ContributionMethodTypes.EARN_LOYALTY_POINTS, methods[0] if len(methods) > 0 else {})
    if config.HasField('space_jump'):
        return (ContributionMethodTypes.SPACE_JUMP, {})


def _get_value_from_generic_matcher(matcher):
    if matcher.HasField('match_value'):
        return matcher.match_value.sequential
    else:
        return None


def _construct_kill_npc_dict_from_proto(data):
    result = []
    for method in data:
        result.append({'solar_system': _get_value_from_generic_matcher(method.solar_system)})

    return result


def _construct_damage_ship_dict_from_proto(data):
    result = []
    for method in data:
        result.append({'solar_system': _get_value_from_generic_matcher(method.solar_system),
         'ship': _get_value_from_generic_matcher(method.ship_type),
         'organization': _get_identity_from_matcher(method.identity)})

    return result


def _construct_mine_ore_dict_from_proto(data):
    result = []
    for method in data:
        result.append({'solar_system': _get_value_from_generic_matcher(method.solar_system),
         'ore': _get_ore_type_from_matcher(method.ore)})

    return result


def _construct_capture_fw_complex_dict_from_proto(data):
    result = []
    for method in data:
        result.append({'solar_system': _get_value_from_generic_matcher(method.solar_system),
         'faction': _get_value_from_generic_matcher(method.previous_owner),
         'complex_type': _get_value_from_generic_matcher(method.archetype)})

    return result


def _construct_defend_fw_complex_dict_from_proto(data):
    result = []
    for method in data:
        result.append({'solar_system': _get_value_from_generic_matcher(method.solar_system),
         'faction': _get_value_from_generic_matcher(method.owner),
         'complex_type': _get_value_from_generic_matcher(method.archetype)})

    return result


def _construct_remote_repair_dict_from_proto(data):
    result = []
    for method in data:
        result.append({'solar_system': _get_value_from_generic_matcher(method.solar_system),
         'ship': _get_value_from_generic_matcher(method.ship_type),
         'organization': _get_identity_from_matcher(method.identity)})

    return result


def _construct_scan_signature_dict_from_proto(data):
    result = []
    for method in data:
        result.append({'solar_system': _get_value_from_generic_matcher(method.solar_system),
         'signature_type': _get_value_from_generic_matcher(method.signature_type)})

    return result


def _construct_install_manufacturing_job_dict_from_proto(data):
    result = []
    for method in data:
        result.append({'owner': _get_owner_type_from_matcher(method.job_owner_type),
         'facility_location': _get_job_location_from_matcher(method.job_location),
         'item_type': _get_item_type_from_matcher(method.item_type)})

    return result


def _construct_complete_goals_dict_from_proto(data):
    result = []
    for method in data:
        result.append({'daily_goal': _get_goal_id_from_matcher(method.daily_goal)})

    return result


def _construct_salvage_wreck_dict_from_proto(data):
    result = []
    for method in data:
        result.append({'solar_system': _get_value_from_generic_matcher(method.solar_system)})

    return result


def _construct_earn_loyalty_points_dict_from_proto(data):
    result = []
    for method in data:
        result.append({'corporation_id': _get_value_from_generic_matcher(method.corporation)})

    return result


def _get_identity_from_matcher(matcher):
    if matcher.HasField('match_character_value'):
        return matcher.match_character_value.sequential
    elif matcher.HasField('match_corporation_value'):
        return matcher.match_corporation_value.sequential
    elif matcher.HasField('match_alliance_value'):
        return matcher.match_alliance_value.sequential
    elif matcher.HasField('match_faction_value'):
        return matcher.match_faction_value.sequential
    else:
        return None


def _get_owner_type_from_matcher(matcher):
    if matcher.HasField('match_any_character'):
        return ON_BEHALF_OF_SELF
    elif matcher.HasField('match_any_corporation'):
        return ON_BEHALF_OF_CORP
    else:
        return None


def _get_job_location_from_matcher(matcher):
    if matcher.HasField('station'):
        return matcher.station.sequential
    elif matcher.HasField('structure'):
        return matcher.structure.sequential
    else:
        return None


def _get_item_type_from_matcher(matcher):
    if matcher.HasField('item_type'):
        return matcher.item_type.sequential
    else:
        return None


def _get_ore_type_from_matcher(matcher):
    if matcher.HasField('ore'):
        return matcher.ore.sequential
    else:
        return None


def _get_goal_id_from_matcher(matcher):
    if matcher.HasField('goal'):
        return uuid.UUID(bytes=matcher.goal.uuid)
    else:
        return None


def find_skill_icon_from_amount(amount):
    if amount <= 10000:
        return 'res:/UI/Texture/Icons/SkillPoints/10k.png'
    if amount <= 25000:
        return 'res:/UI/Texture/Icons/SkillPoints/25k.png'
    if amount <= 50000:
        return 'res:/UI/Texture/Icons/SkillPoints/50k.png'
    if amount <= 100000:
        return 'res:/UI/Texture/Icons/SkillPoints/100k.png'
    if amount <= 150000:
        return 'res:/UI/Texture/Icons/SkillPoints/150k.png'
    if amount <= 250000:
        return 'res:/UI/Texture/Icons/SkillPoints/250k.png'
    if amount <= 500000:
        return 'res:/UI/Texture/Icons/SkillPoints/500k.png'
    if amount <= 750000:
        return 'res:/UI/Texture/Icons/SkillPoints/750k.png'
    return 'res:/UI/Texture/Icons/SkillPoints/1m.png'


def find_type_id_from_amount(amount):
    if amount <= 10000:
        return typeskillpoints10000
    if amount <= 25000:
        return typeskillpoints25000
    if amount <= 50000:
        return typeskillpoints50000
    if amount <= 75000:
        return typeskillpoints75000
    if amount <= 100000:
        return typeskillpoints100000
    if amount <= 150000:
        return typeskillpoints150000
    if amount <= 250000:
        return typeskillpoints250000
    if amount <= 500000:
        return typeskillpoints500000
    return typeskillpoints750000
