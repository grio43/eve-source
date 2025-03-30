#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\subtitles\fsdeditor\custom.py
import evetypes
from nodegraph.subtitles.fsdeditor.entity_names import get_space_object_highlight_name
from platformtools.compatibility.exposure.fsdeditor import fsdutil
from fsdeditor.utils.characters import get_character_name
from fsdeditor.utils.characters import get_faction_name
from fsdeditor.utils.corporations import get_npc_corporation_name
from nodegraph.common.const import *
from nodegraph.subtitles.common.entity_names import format_distance
from nodegraph.subtitles.common.entity_names import get_item_name
from nodegraph.subtitles import register_subtitle_function
from eve.common.script.sys.idCheckers import IsFaction
from eve.common.script.sys.idCheckers import IsNPCCharacter
from eve.common.script.sys.idCheckers import IsNPCCorporation

def get_camera_look_at_object_subtitle(distance = None, **kwargs):
    if distance:
        return 'Distance: {}'.format(format_distance(distance))
    return 'Distance: Object Radius'


def get_validate_in_range_subtitle(distance = None, **kwargs):
    return '{}'.format(format_distance(distance))


def _get_owner_name(owner_id):
    if IsFaction(owner_id):
        return get_faction_name(owner_id)
    if IsNPCCorporation(owner_id):
        return get_npc_corporation_name(owner_id)
    if IsNPCCharacter(owner_id):
        return get_character_name(owner_id)


def get_validate_item_parameters_subtitle(**kwargs):
    return get_item_name(**kwargs)


def get_validate_slim_item_parameters_subtitle(**kwargs):
    if not kwargs:
        return ''
    if 'owner_id' in kwargs:
        owner_name = _get_owner_name(kwargs['owner_id'])
        if owner_name:
            return owner_name
        else:
            return u'Owner: {}'.format(kwargs['owner_id'])
    if 'dungeon_object_id' in kwargs:
        return u'Dungeon object: {}'.format(kwargs['dungeon_object_id'])
    return get_validate_item_parameters_subtitle(**kwargs)


def get_validate_navigation_condition_subtitle(minimum_distance = None, **kwargs):
    subtitle = get_validate_slim_item_parameters_subtitle(**kwargs)
    if minimum_distance:
        return u'{} - {}'.format(format_distance(minimum_distance), subtitle)
    return subtitle


def get_getter_find_closest_object_subtitle(distance = 0, **kwargs):
    name = get_item_name(**kwargs)
    if name:
        return u'{} - {}'.format(format_distance(distance), name)
    else:
        return ''


def get_sub_graph_node_subtitle(node_graph_id = None):
    node_graph = fsdutil.data('nodegraphs/nodegraphsdata/{}.staticdata', node_graph_id)
    if node_graph:
        return node_graph[node_graph_id].name


def get_highlight_space_object_subtitle(highlight_id = None, object_id = None, entity_group_id = None, item_id = None, type_id = None, group_id = None, **kwargs):
    attributes_dict = {'object_id': object_id,
     'entity_group_id': entity_group_id,
     'item_id': item_id,
     'type_id': evetypes.GetName(type_id) if type_id else None,
     'group_id': evetypes.GetGroupNameByGroup(group_id) if group_id else None}
    attributes_string = ', '.join([ '{name}: {value}'.format(name=attribute_name, value=attribute_value) for attribute_name, attribute_value in attributes_dict.items() if attribute_value is not None ])
    if highlight_id:
        highlight_name = get_space_object_highlight_name(highlight_id)
        if attributes_string:
            return '{highlight_name} ({attributes})'.format(highlight_name=highlight_name, attributes=attributes_string)
        return highlight_name
    return attributes_string


def get_orbit_target_subtitle(distance = None, **kwargs):
    if distance:
        return 'Distance: {}'.format(format_distance(distance))
    return 'Distance: player settings'


def register_subtitle_functions():
    register_subtitle_function(ACTION_NODE, atom_ids=[CAMERA_LOOK_AT_OBJECT_ATOM, CAMERA_LOOK_AT_SELF_ATOM], func=get_camera_look_at_object_subtitle)
    register_subtitle_function(ACTION_NODE, atom_ids={HIGHLIGHT_SPACE_OBJECT_ATOM, CLEAR_SPACE_OBJECT_HIGHLIGHT_ATOM}, func=get_highlight_space_object_subtitle)
    register_subtitle_function(ACTION_NODE, atom_ids={ORBIT_TARGET_ATOM}, func=get_orbit_target_subtitle)
    register_subtitle_function(CONDITION_NODE, atom_ids=[IN_RANGE_ATOM], func=get_validate_in_range_subtitle)
    register_subtitle_function(CONDITION_NODE, atom_ids=[SLIM_ITEM_PARAMETERS_ATOM, TARGET_LOCKED_ATOM, SPACE_OBJECT_SELECTED_ATOM], func=get_validate_slim_item_parameters_subtitle)
    register_subtitle_function(CONDITION_NODE, atom_ids=[APPROACHING_ATOM, MOVING_TOWARDS_ATOM, ORBITING_ATOM], func=get_validate_navigation_condition_subtitle)
    register_subtitle_function(CONDITION_NODE, atom_ids=[IN_SHIP_ATOM, JUMPING_ATOM, WARPING_ATOM], func=get_validate_item_parameters_subtitle)
    register_subtitle_function(GETTER_NODE, atom_ids=[FIND_CLOSEST_OBJECT_ATOM], func=get_getter_find_closest_object_subtitle)
    register_subtitle_function(SUB_GRAPH_NODE, func=get_sub_graph_node_subtitle)
