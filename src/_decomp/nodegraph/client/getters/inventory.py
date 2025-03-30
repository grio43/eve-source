#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\inventory.py
import sys
from collections import defaultdict
import logging
import evetypes
from nodegraph.common.util import get_object_predicate
from nodegraph.client.util import get_item_name
logger = logging.getLogger(__name__)
from inventoryutil.client.inventory import get_inventory_and_flags_for_current_ship, get_inventory_and_flags_for_hangar, get_inventory_and_flags_for_other_ships_in_hangar
import inventorycommon.const as inv_const
from .base import GetterAtom

class GetInventoryItem(GetterAtom):
    atom_id = 320

    def __init__(self, item_id = None, type_id = None, group_id = None, singleton_only = None):
        self.item_id = item_id
        self.type_id = type_id
        self.group_id = group_id
        self.singleton_only = self.get_atom_parameter_value('singleton_only', singleton_only)

    def _get_inventories_and_flags(self):
        result = get_inventory_and_flags_for_current_ship()
        result += get_inventory_and_flags_for_hangar()
        return result

    def get_values(self):
        if self.item_id:
            predicate = get_object_predicate('itemID', self.item_id)
        elif self.type_id:
            predicate = get_object_predicate('typeID', self.type_id)
        elif self.group_id:
            predicate = get_object_predicate('groupID', self.group_id)
        else:
            return None
        inventories_and_flags = self._get_inventories_and_flags()
        if not inventories_and_flags:
            return None
        for inventory, flags in inventories_and_flags:
            for item in inventory.ListByFlags(flags):
                if predicate(item):
                    if self.singleton_only and not item.singleton:
                        continue
                    return {'inventory_item': item,
                     'item_id': item.itemID,
                     'type_id': item.typeID,
                     'group_id': evetypes.GetGroupID(item.typeID),
                     'item_location_id': item.locationID}

    @classmethod
    def get_subtitle(cls, singleton_only = None, **kwargs):
        return u'{}{}'.format('singleton - ' if singleton_only else '', get_item_name(**kwargs))


class GetInventoryItems(GetterAtom):
    atom_id = 534

    def __init__(self, type_id = None, group_id = None, location_id = None):
        self.type_id = type_id
        self.group_id = group_id
        self.location_id = location_id

    def _get_inventories_and_flags(self):
        result = get_inventory_and_flags_for_current_ship()
        if not self.location_id or self.location_id == session.locationid:
            result += get_inventory_and_flags_for_hangar()
        return result

    def get_values(self):
        if self.type_id:
            predicate = get_object_predicate('typeID', self.type_id)
        elif self.group_id:
            predicate = get_object_predicate('groupID', self.group_id)
        else:
            return None
        inventories_and_flags = self._get_inventories_and_flags()
        if not inventories_and_flags:
            return None
        result = []
        for inventory, flags in inventories_and_flags:
            for item in inventory.ListByFlags(flags):
                if predicate(item):
                    result.append(item)

        return {'inventory_items': result}

    @classmethod
    def get_subtitle(cls, **kwargs):
        return get_item_name(**kwargs)


class GetInventoryItemsInHangar(GetInventoryItems):
    atom_id = 536

    def _get_inventories_and_flags(self):
        if self.location_id and self.location_id != session.locationid:
            return None
        return get_inventory_and_flags_for_hangar()


class GetInventoryItemsInShipCargo(GetInventoryItems):
    atom_id = 535

    def _get_inventories_and_flags(self):
        return get_inventory_and_flags_for_current_ship()


class GetInventoryItemsInHangarIncludingShips(GetInventoryItems):
    atom_id = None

    def _get_inventories_and_flags(self):
        if self.location_id and self.location_id != session.locationid:
            return None
        result = get_inventory_and_flags_for_hangar()
        result += get_inventory_and_flags_for_other_ships_in_hangar()
        return result


class GetInventoryContainer(GetterAtom):
    atom_id = 541

    def __init__(self, item_id = None):
        self.item_id = item_id

    def __get_container_dict(self):
        try:
            from eve.client.script.environment.invControllers import ShipCargo, StationItems
        except Exception as e:
            logger.exception('Unable to import, %s' % e)

        return {'ship': 'ShipCargo',
         'station_items': 'StationItems'}

    def get_values(self):
        if not self.item_id:
            return None
        from inventoryutil.client.inventory import is_item_in_current_ship, is_item_in_station
        container_dict = self.__get_container_dict()
        if is_item_in_current_ship(self.item_id):
            return {'name': container_dict['ship']}
        if session.stationid and is_item_in_station(self.item_id):
            return {'name': container_dict['station_items']}
        return {'name': None}

    @classmethod
    def get_subtitle(cls, **kwargs):
        return get_item_name(**kwargs)


class GetItemQuantity(GetterAtom):
    atom_id = 388
    _inventory_items_getter = GetInventoryItems

    def __init__(self, type_id = None, group_id = None, location_id = None):
        self.type_id = type_id
        self.group_id = group_id
        self.location_id = location_id

    def get_values(self):
        result = self._inventory_items_getter(type_id=self.type_id, group_id=self.group_id, location_id=self.location_id).get_values()
        if not result:
            return {'quantity': 0}
        quantity = 0
        for item in result.get('inventory_items', []):
            quantity += item.stacksize

        return {'quantity': quantity}

    @classmethod
    def get_subtitle(cls, **kwargs):
        return get_item_name(**kwargs)


class GetItemQuantityInHangar(GetItemQuantity):
    atom_id = 522
    _inventory_items_getter = GetInventoryItemsInHangar


class GetItemQuantityInShipCargo(GetItemQuantity):
    atom_id = 523
    _inventory_items_getter = GetInventoryItemsInShipCargo


class GetItemQuantityInHangarIncludingShips(GetItemQuantity):
    atom_id = 528
    _inventory_items_getter = GetInventoryItemsInHangarIncludingShips


class GetClosestAssetLocation(GetterAtom):
    atom_id = 579

    def __init__(self, type_id = None, group_id = None, singleton_only = None):
        self.type_id = type_id
        self.group_id = group_id
        self.singleton_only = self.get_atom_parameter_value('singleton_only', singleton_only)

    def get_values(self):
        if self.type_id:
            predicate = get_object_predicate('typeID', self.type_id)
        elif self.group_id:
            predicate = get_object_predicate('groupID', self.group_id)
        else:
            return
        all_items = sm.GetService('invCache').GetInventory(inv_const.containerGlobal).ListIncludingContainers()
        matching_items = defaultdict(list)
        for item in all_items:
            if predicate(item):
                if self.singleton_only and item.quantity > 0:
                    continue
                if item.locationID == session.locationid:
                    matching_items = {item.locationID: [item]}
                    break
                matching_items[item.locationID].append(item)

        if not matching_items:
            return
        get_jump_count = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent
        closest_location_id = None
        min_jumps = sys.maxint
        for location_id in matching_items.iterkeys():
            solar_system_id = cfg.evelocations.Get(location_id).solarSystemID
            jumps = get_jump_count(solar_system_id)
            if jumps < min_jumps:
                min_jumps = jumps
                closest_location_id = location_id

        if not closest_location_id:
            return
        item = matching_items[closest_location_id][0]
        return {'type_id': item.typeID,
         'group_id': evetypes.GetGroupID(item.typeID),
         'location_id': closest_location_id,
         'solar_system_id': cfg.evelocations.Get(closest_location_id).solarSystemID}

    @classmethod
    def get_subtitle(cls, singleton_only = None, **kwargs):
        return u'{}{}'.format('singleton - ' if singleton_only else '', get_item_name(**kwargs))
