#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\inventory.py
from nodegraph.common.util import get_operator_function
from nodegraph.client.util import get_item_name
from nodegraph.client.getters.inventory import GetItemQuantity, GetItemQuantityInHangar, GetItemQuantityInShipCargo, GetItemQuantityInHangarIncludingShips
from .base import Condition

class ItemInInventory(Condition):
    atom_id = 20
    _getter_atom = GetItemQuantity

    def __init__(self, type_id = None, group_id = None, quantity = None, operator = None, location_id = None, stacked = None, **kwargs):
        super(ItemInInventory, self).__init__(**kwargs)
        self.type_id = type_id
        self.group_id = group_id
        self.quantity = self.get_atom_parameter_value('quantity', quantity)
        self.operator = self.get_atom_parameter_value('operator', operator)
        self.stacked = self.get_atom_parameter_value('stacked', stacked)
        self.location_id = location_id

    def _compare_quantity(self):
        result = self._getter_atom(type_id=self.type_id, group_id=self.group_id, location_id=self.location_id).get_values()
        quantity = result.get('quantity', 0)
        operator_func = get_operator_function(self.operator)
        return operator_func(quantity, self.quantity)

    def _compare_stacked(self):
        inventory_items_getter = self._getter_atom._inventory_items_getter
        result = inventory_items_getter(type_id=self.type_id, group_id=self.group_id, location_id=self.location_id).get_values()
        operator_func = get_operator_function(self.operator)
        if not result:
            return False
        for item in result.get('inventory_items') or []:
            if operator_func(item.stacksize, self.quantity):
                return True

        return False

    def validate(self, **kwargs):
        if self.stacked:
            return self._compare_stacked()
        else:
            return self._compare_quantity()

    @classmethod
    def get_subtitle(cls, quantity = None, operator = None, stacked = None, **kwargs):
        return u'{} {} {} - {}'.format('stacked' if cls.get_atom_parameter_value('stacked', stacked) else '', cls.get_atom_parameter_value('operator', operator), cls.get_atom_parameter_value('quantity', quantity), get_item_name(**kwargs))


class ItemInHangar(ItemInInventory):
    atom_id = 21
    _getter_atom = GetItemQuantityInHangar


class ItemInShipCargo(ItemInInventory):
    atom_id = 23
    _getter_atom = GetItemQuantityInShipCargo


class ItemInHangarIncludingShips(ItemInInventory):
    atom_id = 527
    _getter_atom = GetItemQuantityInHangarIncludingShips
