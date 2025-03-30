#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\reference\element.py
import weakref
from uiblinker.reference import UiReference

class ElementReference(UiReference):

    def __init__(self, *elements):
        self._elements = weakref.WeakSet(elements)

    def resolve(self, root):
        return [ element for element in self._elements if not element.destroyed ]

    def __str__(self):
        return 'ElementReference({})'.format(', '.join((repr(element) for element in self._elements)))
