#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\subtitles\eveclient\custom.py
import evetypes
from nodegraph.client.util import get_item_name
from nodegraph.common.const import *
from nodegraph.common.nodedata import get_node_graph_data
from nodegraph.subtitles import register_subtitle_function
from carbon.common.script.util.format import FmtDist
from uihighlighting.fsdloaders import SpaceObjectHighlightsLoader

def get_camera_look_at_object_subtitle(distance = None, **kwargs):
    if distance:
        return 'Distance: {}'.format(FmtDist(distance))
    return 'Distance: Object Radius'


def get_validate_in_range_subtitle(distance = None, **kwargs):
    return '{}'.format(FmtDist(distance))


def get_validate_slim_item_parameters_subtitle(**kwargs):
    if not kwargs:
        return ''
    if 'owner_id' in kwargs:
        owner = cfg.eveowners.Get(kwargs['owner_id'])
        if owner:
            return owner.name
        else:
            return u'Owner: {}'.format(kwargs['owner_id'])
    if 'dungeon_object_id' in kwargs:
        return u'Dungeon object: {}'.format(kwargs['dungeon_object_id'])
    return get_item_name(**kwargs)


def get_getter_find_closest_object_subtitle(distance = 0, **kwargs):
    name = get_item_name(**kwargs)
    if name:
        return u'{} - {}'.format(FmtDist(distance), name)
    else:
        return ''


def get_navigation_condition_subtitle(**kwargs):
    subtitle = get_validate_slim_item_parameters_subtitle(**kwargs)
    minimum_distance = kwargs.get('minimum_distance')
    if minimum_distance:
        return u'{} - {}'.format(FmtDist(minimum_distance), subtitle)
    return subtitle


def get_sub_graph_node_subtitle(node_graph_id = None):
    node_graph = get_node_graph_data(node_graph_id)
    if node_graph:
        return node_graph.name
    return ''


def get_highlight_space_object_subtitle(highlight_id = None, object_id = None, entity_group_id = None, item_id = None, type_id = None, group_id = None, **kwargs):
    attributes_dict = {'object_id': object_id,
     'entity_group_id': entity_group_id,
     'item_id': item_id,
     'type_id': evetypes.GetName(type_id) if type_id else None,
     'group_id': evetypes.GetGroupNameByGroup(group_id) if group_id else None}
    attributes_string = ', '.join([ '{name}: {value}'.format(name=attribute_name, value=attribute_value) for attribute_name, attribute_value in attributes_dict.items() if attribute_value is not None ])
    if highlight_id:
        highlight = SpaceObjectHighlightsLoader.GetByID(highlight_id)
        highlight_name = None
        if highlight:
            highlight_name = highlight.name
        if attributes_string:
            return '{highlight_name} ({attributes})'.format(highlight_name=highlight_name, attributes=attributes_string)
        return highlight_name
    return attributes_string


def get_is_fitting_attribute_expanded_subtitle(menu_name):
    return u'{}'.format(menu_name)


def register_subtitle_functions():
    register_subtitle_function(ACTION_NODE, atom_ids=[CAMERA_LOOK_AT_OBJECT_ATOM, CAMERA_LOOK_AT_SELF_ATOM], func=get_camera_look_at_object_subtitle)
    register_subtitle_function(CONDITION_NODE, atom_ids=[IN_RANGE_ATOM], func=get_validate_in_range_subtitle)
    register_subtitle_function(CONDITION_NODE, atom_ids=[SLIM_ITEM_PARAMETERS_ATOM, TARGET_LOCKED_ATOM, SPACE_OBJECT_SELECTED_ATOM], func=get_validate_slim_item_parameters_subtitle)
    register_subtitle_function(CONDITION_NODE, atom_ids={IS_FITTING_ATTRIBUTE_EXPANDED_ATOM}, func=get_is_fitting_attribute_expanded_subtitle)
    register_subtitle_function(GETTER_NODE, atom_ids=[FIND_CLOSEST_OBJECT_ATOM], func=get_getter_find_closest_object_subtitle)
    register_subtitle_function(CONDITION_NODE, atom_ids=[APPROACHING_ATOM, MOVING_TOWARDS_ATOM, ORBITING_ATOM], func=get_navigation_condition_subtitle)
    register_subtitle_function(ACTION_NODE, atom_ids={HIGHLIGHT_SPACE_OBJECT_ATOM, CLEAR_SPACE_OBJECT_HIGHLIGHT_ATOM}, func=get_highlight_space_object_subtitle)
    register_subtitle_function(SUB_GRAPH_NODE, func=get_sub_graph_node_subtitle)
