#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\structures\fitting.py
from cosmetics.common.structures.const import StructurePaintSlot

class StructurePaintwork(object):

    def __init__(self):
        self._slots = {StructurePaintSlot.PRIMARY: None,
         StructurePaintSlot.SECONDARY: None,
         StructurePaintSlot.DETAILING: None}

    def clear(self):
        for slot_index in self._slots:
            self._slots[slot_index] = None

    def get_slot(self, slot_index):
        if slot_index not in self._slots:
            raise KeyError('slot %s not defined' % slot_index)
        return self._slots[slot_index]

    def get_slots(self):
        return self._slots

    def get_slot_values(self):
        return tuple(self._slots.values())

    def set_slot(self, slot_index, slot_value):
        if slot_index not in self._slots:
            raise KeyError('slot %s not defined' % slot_index)
        self._slots[slot_index] = slot_value

    def __eq__(self, other):
        return all([ other.get_slot(key) == val for key, val in self._slots.iteritems() ])
