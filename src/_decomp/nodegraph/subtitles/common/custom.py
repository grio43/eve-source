#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\subtitles\common\custom.py
from nodegraph.common.const import *
from nodegraph.subtitles.common.entity_names import get_item_name
from nodegraph.subtitles import get_entity_name_getter
from nodegraph.subtitles import register_subtitle_function

def get_set_destination_subtitle(destination_id = None, clear_waypoints = None, **kwargs):
    location_name_getter = get_entity_name_getter('location')
    subtitle = location_name_getter(destination_id)
    if clear_waypoints:
        subtitle = '{} - Clear waypoints'.format(subtitle, clear_waypoints)
    return subtitle


def get_slash_command_subtitle(slash_command = '', wait_for_session = None, **kwargs):
    if wait_for_session:
        return '{} (Wait for session)'.format(slash_command)
    return slash_command


def get_set_checkpoint_subtitle(checkpoint_id = None, **kwargs):
    getter = get_entity_name_getter('checkpoint')
    checkpoint_name = getter(checkpoint_id)
    if checkpoint_name:
        return '{} ({})'.format(checkpoint_name, checkpoint_id)
    return checkpoint_id


def get_change_setting_subtitle(settings_section, settings_group, settings_id, settings_value):
    return '{}.{}.{}: {}'.format(settings_section, settings_group, settings_id, settings_value)


def get_in_station_subtitle(station_id = None, station_type_id = None):
    location_name_getter = get_entity_name_getter('location')
    type_name_getter = get_entity_name_getter('type')
    if station_id:
        return location_name_getter(station_id)
    if station_type_id:
        return type_name_getter(station_type_id)
    return ''


def get_validate_item_parameters_subtitle(**kwargs):
    return get_item_name(**kwargs)


def get_validate_ship_health_subtitle(health_type = None, percentage = None, attribute_value = None, operator = None, **kwargs):
    if percentage:
        return u'{} {} {}%'.format(health_type, operator, attribute_value, percentage)
    return u'{} {} {}'.format(health_type, operator, attribute_value)


def get_validate_client_settings_subtitle(settings_section = None, settings_group = None, settings_id = None, settings_value = None, **kwargs):
    return u'{}.{}.{}={}'.format(settings_section, settings_group, settings_id or 'MISSING', settings_value or 'MISSING')


def get_blackboard_event_node_subtitle(blackboard_key = None, keep_listening = None, validate_on_start = None, **kwargs):
    result = [blackboard_key or '']
    if keep_listening:
        result.append('KeepListening')
    if validate_on_start:
        result.append('ValidateOnStart')
    return ' - '.join(result)


def get_blackboard_validation_node_subtitle(blackboard_key = None, flipped = None, operator = None, blackboard_value = None, **kwargs):
    if blackboard_key:
        return u'{} {} {} {}'.format(blackboard_key, operator, blackboard_value, '(flipped)' if flipped else '')
    return ''


def get_blackboard_write_node_subtitle(blackboard_key = None, blackboard_value = None, input_key = None, **kwargs):
    if blackboard_value:
        return u'{}={}'.format(blackboard_key, blackboard_value)
    if input_key:
        return u'{}->{}'.format(input_key, blackboard_key)
    return blackboard_key


def get_blackboard_read_node_subtitle(blackboard_key = '', output_key = '', **kwargs):
    return u'{}->{}'.format(blackboard_key, output_key)


def get_event_node_subtitle(keep_listening = None, validate_on_start = None, **kwargs):
    result = []
    if keep_listening:
        result.append('KeepListening')
    if validate_on_start:
        result.append('ValidateOnStart')
    return ' - '.join(result)


def get_event_group_node_subtitle(require_all = None, keep_listening = None, **kwargs):
    result = []
    if keep_listening:
        result.append('KeepListening')
    if require_all:
        result.append('RequireAll')
    else:
        result.append('RequireAny')
    return ' - '.join(result)


def get_map_variable_node_subtitle(input_key = '', output_key = ''):
    return u'{}->{}'.format(input_key, output_key)


def get_node_graph_message_listener_node_subtitle(message_key = '', keep_listening = None):
    if keep_listening:
        return '{} - KeepListening'.format(message_key)
    return message_key


def get_repeat_node_subtitle(repeat_count = None, delay = None):
    return 'Repeat:{} - Delay:{} sec'.format('infinite' if repeat_count == 0 else repeat_count, delay)


def get_validation_group_node_subtitle(require_all = None, run_all = None):
    return 'Require {} {}'.format('ALL' if require_all else 'ANY', '- run all' if run_all else '')


def get_validate_has_agent_mission(agent_id = None, accepted = None, offered = None, **kwargs):
    result = []
    if accepted:
        result.append('Accepted')
    if offered:
        result.append('Offered')
    if agent_id:
        result.append('Agent:{}'.format(agent_id))
    return ' '.join(result)


def get_compare_values_node_subtitle(value_a = None, value_b = None, operator = None, flipped = None, **kwargs):
    if flipped:
        return u'{} {} {}'.format(value_b or '[value_b]', operator, value_a or '[value_a]')
    return u'{} {} {}'.format(value_a or '[value_a]', operator, value_b or '[value_b]')


def register_subtitle_functions():
    register_subtitle_function(BLACKBOARD_EVENT_NODE, func=get_blackboard_event_node_subtitle)
    register_subtitle_function(BLACKBOARD_VALIDATION_NODE, func=get_blackboard_validation_node_subtitle)
    register_subtitle_function(BLACKBOARD_WRITE_NODE, func=get_blackboard_write_node_subtitle)
    register_subtitle_function(BLACKBOARD_READ_NODE, func=get_blackboard_read_node_subtitle)
    register_subtitle_function(EVENT_NODE, func=get_event_node_subtitle)
    register_subtitle_function(EVENT_GROUP_NODE, func=get_event_group_node_subtitle)
    register_subtitle_function(MAP_VARIABLE_NODE, func=get_map_variable_node_subtitle)
    register_subtitle_function(NODE_GRAPH_MESSAGE_LISTENER_NODE, func=get_node_graph_message_listener_node_subtitle)
    register_subtitle_function(REPEAT_NODE, func=get_repeat_node_subtitle)
    register_subtitle_function(VALIDATION_GROUP_NODE, func=get_validation_group_node_subtitle)
    register_subtitle_function(ACTION_NODE, atom_ids={SET_DESTINATION_ATOM}, func=get_set_destination_subtitle)
    register_subtitle_function(ACTION_NODE, atom_ids={SLASH_COMMAND_ATOM}, func=get_slash_command_subtitle)
    register_subtitle_function(ACTION_NODE, atom_ids={SET_CHECKPOINT_ATOM}, func=get_set_checkpoint_subtitle)
    register_subtitle_function(ACTION_NODE, atom_ids={CHANGE_SETTING_ATOM}, func=get_change_setting_subtitle)
    register_subtitle_function(CONDITION_NODE, atom_ids={IN_STATION_ATOM}, func=get_in_station_subtitle)
    register_subtitle_function(CONDITION_NODE, atom_ids={ITEM_PARAMETERS_ATOM}, func=get_validate_item_parameters_subtitle)
    register_subtitle_function(CONDITION_NODE, atom_ids={SHIP_HEALTH_ATOM}, func=get_validate_ship_health_subtitle)
    register_subtitle_function(CONDITION_NODE, atom_ids={CLIENT_SETTINGS_ATOM}, func=get_validate_client_settings_subtitle)
    register_subtitle_function(CONDITION_NODE, atom_ids={HAS_AGENT_MISSION_ATOM}, func=get_validate_has_agent_mission)
    register_subtitle_function(CONDITION_NODE, atom_ids={COMPARE_VALUES_ATOM}, func=get_compare_values_node_subtitle)
