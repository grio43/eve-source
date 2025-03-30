#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\inventory.py
import logging
from inventorycommon import FakeItemNotHere
logger = logging.getLogger(__name__)

def get_inventory_item(task, item_id):
    try:
        return get_inventory2(task).GetItem(item_id)
    except (RuntimeError, FakeItemNotHere):
        return None


def get_inventory2(task):
    return task.context.ballpark.inventory2


def get_inventory_mgr(task):
    return task.context.ballpark.inventoryMgr


def get_type_id_by_item_id(task, item_id):
    item = get_inventory_item(task, item_id)
    if item:
        return item.typeID
    else:
        return None


def get_cargo_capacity(task, item_id):
    return get_cargo_inventory(item_id, task).GetCapacity()


def get_cargo_inventory(item_id, task):
    return get_inventory_mgr(task).GetInventoryFromIdEx(item_id, -1)


def is_my_cargo_full(task):
    cargo_capacity = get_cargo_capacity(task, task.context.myItemId)
    return cargo_capacity.used + 1e-07 >= cargo_capacity.capacity


def get_cargo_used_fraction(task, item_id):
    cargo_capacity = get_cargo_capacity(task, item_id)
    return cargo_capacity.used / cargo_capacity.capacity


def remove_all_items(task, item_id):
    inventory2 = get_inventory2(task)
    inventory_mgr = get_inventory_mgr(task)
    logger.debug('removing all items from item %s', item_id)
    for item in inventory2.SelectItems(item_id):
        inventory_mgr.DestroyItem(item.itemID)
        logger.debug('removing item %s', item)
