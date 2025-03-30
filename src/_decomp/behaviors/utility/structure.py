#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\structure.py
from behaviors.utility.groups import get_my_entity_group_owner_id
from inventorycommon.const import categoryStructure
from npcs.npccorporations import get_corporation_faction_id
from structures import SETTING_HOUSING_CAN_DOCK

def get_structure_profiles():
    return sm.GetService('structureProfiles')


def can_dock_at_structure(task, structure_id):
    corporation_id = get_my_entity_group_owner_id(task)
    alliance_id = get_corporation_faction_id(corporation_id)
    structure_profiles = get_structure_profiles()
    value = structure_profiles.GetSettingValueForCharacter(corporation_id, structure_id, SETTING_HOUSING_CAN_DOCK, corporation_id, alliance_id, None)
    return value is not None


def is_structure(slim_item):
    return slim_item.categoryID == categoryStructure
