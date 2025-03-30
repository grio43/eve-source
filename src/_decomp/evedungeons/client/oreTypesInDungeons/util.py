#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\oreTypesInDungeons\util.py
from evedungeons.client.oreTypesInDungeons.const import ORE_TYPES_BY_VALUE
from evedungeons.client.oreTypesInDungeons.data import get_ore_types_in_dungeon, get_asteroid_types_by_solar_system
from evetypes.utils import extract_lowest_type_id_for_group, sort_types_by_value

def get_consolidated_ore_types(type_ids):
    filtered_type_ids = extract_lowest_type_id_for_group(type_ids)
    return sort_types_by_value(filtered_type_ids, ORE_TYPES_BY_VALUE)


def get_consolidated_ore_types_in_dungeon(dungeon_id):
    return get_consolidated_ore_types(get_ore_types_in_dungeon(dungeon_id))


def get_consolidated_ore_types_in_system(solar_system_id):
    type_ids = get_asteroid_types_by_solar_system(solar_system_id)
    return get_consolidated_ore_types(type_ids)
