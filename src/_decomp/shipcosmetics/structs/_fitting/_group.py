#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\structs\_fitting\_group.py
__all__ = ['ShipCosmeticFittingGroup']
from shipcosmetics.structs import AbstractShipCosmeticModule

class ShipCosmeticFittingGroup(object):
    __slots__ = ('group_index', '_slots_by_index')

    def __init__(self, group_index, slots_by_index = None):
        self.group_index = group_index
        self._slots_by_index = slots_by_index or {}

    def get_ship_cosmetic_module(self, slot_index):
        return self._slots_by_index.get(slot_index, None)

    def get_enabled_slots(self):
        return (slot for slot in self._slots_by_index.itervalues() if slot)

    def is_empty(self):
        if not self._slots_by_index:
            return True
        for slot in self._slots_by_index.itervalues():
            if slot:
                return False

        return True

    def __nonzero__(self):
        return not self.is_empty()

    def set_slot(self, slot_index, ship_cosmetic_module):
        existing = self.get_ship_cosmetic_module(slot_index)
        self._slots_by_index[slot_index] = ship_cosmetic_module
        return existing
