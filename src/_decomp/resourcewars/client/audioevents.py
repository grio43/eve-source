#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\resourcewars\client\audioevents.py
import evetypes
from inventorycommon.const import groupNpcIndustrialCommand, RESOURCE_WARS_ORE_TYPES

def is_hauler_type(typeID):
    return typeID is not None and evetypes.GetGroupID(typeID) == groupNpcIndustrialCommand


def is_rw_ore_item(item):
    return item is not None and item.typeID in RESOURCE_WARS_ORE_TYPES


def on_not_enough_cargo_space(invControllerTypeID, item):
    if is_hauler_type(invControllerTypeID) and is_rw_ore_item(item):
        sm.GetService('audio').SendUIEvent('voc_rw_aura_haulmaxcapacity_aura_play')
