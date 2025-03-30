#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveformat\volume.py
import evetypes
import inventorycommon.util
from eveformat import localization

def volume(amount):
    return localization.get_by_label('UI/Inventory/ContainerCapacity', capacity=amount)


def volume_from_item(item, include_per_unit = False):
    item_volume = volume(inventorycommon.util.GetItemVolume(item))
    if include_per_unit and item.stacksize > 1:
        type_volume = volume(inventorycommon.util.GetTypeVolume(item.typeID, 1))
        return localization.get_by_label('UI/Inventory/ItemStackVolume', itemVolume=item_volume, typeVolume=type_volume)
    return item_volume


def volume_from_type(type_id):
    return volume(evetypes.GetVolume(type_id))
