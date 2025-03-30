#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\structs\_fitting\_fitting.py
__all__ = ['ShipCosmeticFitting']
from shipcosmetics.structs._fitting._group import ShipCosmeticFittingGroup

class ShipCosmeticFitting(object):
    __slots__ = ('_groups_by_index', 'ship_item_id', 'character_id')

    def __init__(self, ship_item_id, character_id, groups_by_index = None):
        self.ship_item_id = ship_item_id
        self.character_id = character_id
        self._groups_by_index = groups_by_index or {}

    def get_ship_cosmetic_fitting_group(self, group_index):
        return self._groups_by_index.get(group_index, None)

    def get_ship_cosmetic_fitting_types(self):
        cosmetic_types = []
        for group in self._groups_by_index.itervalues():
            for slot in group.get_enabled_slots():
                cosmetic_types.append(slot.getCosmeticType())

        return cosmetic_types

    def set_slot(self, group_index, slot_index, ship_cosmetic_module):
        group = self.get_ship_cosmetic_fitting_group(group_index)
        if not group:
            group = ShipCosmeticFittingGroup(group_index)
        existing = group.set_slot(slot_index, ship_cosmetic_module)
        self._groups_by_index[group_index] = group
        return existing

    def get_by_indices(self, group_index, slot_index):
        group = self.get_ship_cosmetic_fitting_group(group_index)
        if group:
            return group.get_ship_cosmetic_module(slot_index)

    def is_empty(self):
        if not self._groups_by_index:
            return True
        for group in self._groups_by_index.itervalues():
            if not group.is_empty():
                return False

        return True

    def __nonzero__(self):
        return not self.is_empty()
