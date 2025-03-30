#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\subtitles\common\entity_names.py
import evetypes
from eve.common.lib import appConst
_ENTITY_NAME_GETTERS = {}

def register_entity_name_getter(entity, getter):
    _ENTITY_NAME_GETTERS[entity] = getter


def get_entity_name_getter(entity):
    return _ENTITY_NAME_GETTERS.get(entity)


def get_item_name(**kwargs):
    if not kwargs:
        return ''
    item_id = kwargs.get('item_id', None)
    if item_id:
        return str(item_id)
    type_id = kwargs.get('type_id', None)
    if type_id:
        type_name = evetypes.GetName(type_id)
        return '{} ({})'.format(type_name, type_id)
    group_id = kwargs.get('group_id', None)
    if group_id:
        group_name = evetypes.GetGroupNameByGroup(group_id)
        return '{} ({})'.format(group_name, group_id)
    category_id = kwargs.get('category_id', None)
    if category_id:
        category_name = evetypes.GetCategoryNameByCategory(category_id)
        return '{} ({})'.format(category_name, category_id)
    return ''


def format_distance(dist, maxdemicals = 2):
    if dist < 10000.0:
        if dist == 0 or dist >= 1.0:
            dist = int(round(dist))
        return '{} m'.format(dist)
    if dist < 10000000000.0:
        dist = long(round(dist / 1000.0))
        return '{} km'.format(dist)
    dist = round(dist / appConst.AU, maxdemicals)
    return '{} AU'.format(dist)


def register_entity_name_getters():
    register_entity_name_getter('type', evetypes.GetName)
    register_entity_name_getter('distance', format_distance)
    register_entity_name_getter('blackboard_key', lambda blackboard_key: blackboard_key)
    register_entity_name_getter('blackboard_value', lambda blackboard_value: blackboard_value)
