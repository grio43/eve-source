#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\gasTypesInDungeons\util.py
from evedungeons.client.gasTypesInDungeons.const import GAS_TYPES_BY_VALUE
from evetypes.utils import extract_lowest_type_id_for_group, sort_types_by_value

def get_consolidated_gas_types(type_ids):
    filtered_type_ids = extract_lowest_type_id_for_group(type_ids)
    return sort_types_by_value(filtered_type_ids, GAS_TYPES_BY_VALUE)
