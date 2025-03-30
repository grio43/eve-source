#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\inventoryutil\client\inventory.py
import inventorycommon.const as inv_const
import eve.common.script.sys.eveCfg as eveCfg
from collections import defaultdict
from eve.common.script.sys.idCheckers import IsShip, IsShipType
from inventorycommon.util import IsModularShip
from dogma import data as dogma_data
import dogma.const as dogmaConst

def get_hangar_inventory():
    try:
        if session.stationid:
            return sm.GetService('invCache').GetInventory(inv_const.containerHangar)
        if session.structureid:
            return sm.GetService('invCache').GetInventoryFromId(session.structureid)
        return None
    except Exception:
        return None


def get_ship_inventory():
    if not eveCfg.InShip():
        return None
    try:
        return sm.GetService('invCache').GetInventoryFromId(session.shipid)
    except Exception:
        return None


def get_inventory_and_flags_for_hangar():
    inventory = get_hangar_inventory()
    ret = []
    if inventory:
        ret.append((inventory, [inv_const.flagHangar]))
    return ret


def get_inventory_and_flags_for_current_ship(use_only_cargo = False):
    inventory = get_ship_inventory()
    ret = []
    if inventory:
        flags = get_valid_ship_flags_for_current_ship(use_only_cargo)
        ret.append((inventory, flags))
    return ret


def get_inventory_and_flags_for_current_location():
    ret = []
    ret.extend(get_inventory_and_flags_for_hangar())
    ret.extend(get_inventory_and_flags_for_current_ship(use_only_cargo=True))
    return ret


def get_inventory_and_flags_for_other_ships_in_hangar():
    inventory = get_hangar_inventory()
    ret = []
    if inventory:
        ships = [ item.itemID for item in inventory.List(inv_const.flagHangar) if IsShip(item.categoryID) and item.itemID != session.shipid ]
        for ship_id in ships:
            inventory = sm.GetService('invCache').GetInventoryFromId(ship_id)
            type_id = inventory.typeID
            flags = get_valid_ship_flags(ship_id, type_id)
            ret.append((inventory, flags))

    return ret


def get_valid_ship_flags_for_current_ship(use_only_cargo = False):
    ship_id = session.shipid
    ship = sm.GetService('invCache').GetInventoryFromId(ship_id)
    type_id = ship.typeID
    return get_valid_ship_flags(ship_id, type_id, use_only_cargo)


def get_valid_ship_flags(ship_id, type_id, use_only_cargo = False):
    return sm.GetService('godma').GetFlagsWithValidCapacity(ship_id, type_id, use_only_cargo)


def get_fitting_flags_for_ship_type(type_id):
    if not IsShipType(type_id):
        return []
    if IsModularShip(type_id):
        return inv_const.shipFittingFlags
    result = []
    for attributeID, flags in ((dogmaConst.attributeHiSlots, inv_const.hiSlotFlags),
     (dogmaConst.attributeMedSlots, inv_const.medSlotFlags),
     (dogmaConst.attributeLowSlots, inv_const.loSlotFlags),
     (dogmaConst.attributeRigSlots, inv_const.rigSlotFlags)):
        slot_amount = int(dogma_data.get_type_attribute(type_id, attributeID, 0))
        if slot_amount:
            result.extend(flags[:slot_amount])

    return result


def is_item_in_inventory(inventories_and_flags, item_id):
    for inventory, flags in inventories_and_flags:
        for item in inventory.ListByFlags(flags):
            if item.itemID == item_id:
                return True

    return False


def is_item_in_current_ship(item_id):
    inventories_and_flags = get_inventory_and_flags_for_current_ship()
    return is_item_in_inventory(inventories_and_flags, item_id)


def is_item_in_station(item_id):
    inventories_and_flags = get_inventory_and_flags_for_hangar()
    return is_item_in_inventory(inventories_and_flags, item_id)


def _are_types_in_location(quantity_by_type_id, inventories_and_flags):
    _, is_there_enough = _get_type_quantities_in_location(quantity_by_type_id, inventories_and_flags)
    return is_there_enough


def _get_type_quantities_in_location(quantity_by_type_id, inventories_and_flags):
    quantities_found = defaultdict(int)
    is_there_enough = False
    inventories_and_flags.reverse()
    for inventory, flags in inventories_and_flags:
        quantities_found = defaultdict(int)
        for item in inventory.ListByFlags(flags):
            if item.typeID in quantity_by_type_id and item.stacksize > 0:
                quantities_found[item.typeID] += item.stacksize

        is_there_enough = True
        for type_id, quantity in quantity_by_type_id.items():
            quantity_found = quantities_found[type_id]
            if quantity_found < quantity:
                is_there_enough = False
                break

        if is_there_enough:
            return (quantities_found, is_there_enough)

    return (quantities_found, is_there_enough)


def are_types_in_current_location(quantity_by_type_id):
    inventories_and_flags = get_inventory_and_flags_for_current_location()
    return _are_types_in_location(quantity_by_type_id, inventories_and_flags)


def get_type_quantities_in_current_location(quantity_by_type_id):
    inventories_and_flags = get_inventory_and_flags_for_current_location()
    quantities_found, _ = _get_type_quantities_in_location(quantity_by_type_id, inventories_and_flags)
    return quantities_found
