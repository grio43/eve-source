#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evetypes\utils.py
from collections import defaultdict
from evetypes import GetGroupID

def extract_lowest_type_id_for_group(type_ids):
    type_ids_by_group_id = defaultdict(list)
    for type_id in type_ids:
        type_ids_by_group_id[GetGroupID(type_id)].append(type_id)

    filtered_type_ids = [ min(type_ids) for type_ids in type_ids_by_group_id.values() ]
    return filtered_type_ids


def sort_types_by_value(type_ids, ordered_types_list):
    type_ids = sorted(type_ids, key=lambda type_id: _get_value_sort_key(type_id, ordered_types_list), reverse=True)
    return type_ids


def _get_value_sort_key(type_id, ordered_types_list):
    if type_id in ordered_types_list:
        return ordered_types_list.index(type_id)
    else:
        return 0
