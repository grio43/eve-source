#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\iceTypesInDungeon\util.py
from evedungeons.client.iceTypesInDungeon.const import ICE_TYPES_BY_VALUE
from evedungeons.client.iceTypesInDungeon.data import get_ice_types_in_dungeon
from evetypes.utils import extract_lowest_type_id_for_group, sort_types_by_value

def get_consolidated_ice_types(type_ids):
    filtered_type_ids = extract_lowest_type_id_for_group(type_ids)
    return sort_types_by_value(filtered_type_ids, ICE_TYPES_BY_VALUE)


def get_consolidated_ice_types_in_dungeon(dungeon_id):
    return get_consolidated_ice_types(get_ice_types_in_dungeon(dungeon_id))
