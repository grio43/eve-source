#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\utils\indexcast.py
__all__ = ['group_and_slot_index_to_backend', 'backend_to_group_and_slot_index']
_SHIFT_BITS = 6
_MASK = 63

def group_and_slot_index_to_backend(group_index, slot_index):
    if slot_index > _MASK:
        raise OverflowError('slot_index must be smaller then %s' % (_MASK + 1))
    return slot_index | group_index << _SHIFT_BITS


def backend_to_group_and_slot_index(backend_slot):
    return (backend_slot >> _SHIFT_BITS, backend_slot & _MASK)
