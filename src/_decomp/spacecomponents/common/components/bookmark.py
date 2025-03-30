#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\common\components\bookmark.py
from spacecomponents.common.components.component import Component
from spacecomponents.common.componentConst import BOOKMARK_CLASS
from spacecomponents.common.data import get_space_component_for_type

class Bookmark(Component):

    def IsBookmarkable(self):
        return self.attributes.isBookmarkable


def IsTypeBookmarkable(typeID):
    try:
        attributes = get_space_component_for_type(typeID, BOOKMARK_CLASS)
        return bool(attributes is None or getattr(attributes, 'isBookmarkable', True))
    except (KeyError, AttributeError):
        return True
