#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\reference\item.py
from uiblinker.reference import UiReference
from uiblinker.reference.util import iter_element_tree

class InventoryItemReference(UiReference):

    def __init__(self, type_id = None, item_id = None):
        self._type_id = type_id
        self._item_id = item_id

    def resolve(self, root):
        return [ element for element in iter_element_tree(root) if getattr(element, '__class__', object).__name__ == 'InvItem' and (self._type_id is None or getattr(element, 'typeID', None) == self._type_id) and (self._item_id is None or getattr(element, 'id', None) == self._item_id) ]

    def __str__(self):
        return 'InventoryItemReference(type_id={!r}, item_id={!r})'.format(self._type_id, self._item_id)
