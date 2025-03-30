#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihighlighting\const.py


class SpaceObjectType(object):
    OBJECT_ID = 1
    TYPE_ID = 2
    GROUP_ID = 3
    ENTITY_GROUP_ID = 4
    ITEM_ID = 5
    NEXT_ITEM_IN_ROUTE = 6


class SpaceObjectString(object):
    OBJECT_ID_STRING = 'objectID'
    TYPE_ID_STRING = 'typeID'
    GROUP_ID_STRING = 'groupID'
    ENTITY_GROUP_ID_STRING = 'entityGroupID'
    NEXT_ITEM_IN_ROUTE = 'nextItemInRoute'


SPACE_OBJECT_STRING_TO_TYPE = {SpaceObjectString.OBJECT_ID_STRING: SpaceObjectType.OBJECT_ID,
 SpaceObjectString.TYPE_ID_STRING: SpaceObjectType.TYPE_ID,
 SpaceObjectString.GROUP_ID_STRING: SpaceObjectType.GROUP_ID,
 SpaceObjectString.ENTITY_GROUP_ID_STRING: SpaceObjectType.ENTITY_GROUP_ID,
 SpaceObjectString.NEXT_ITEM_IN_ROUTE: SpaceObjectType.NEXT_ITEM_IN_ROUTE}
DEFAULT_AUDIO_ON = True
DEFAULT_AUDIO_OFF = False

class UiHighlightDirections(object):
    LEFT = 1
    UP = 2
    RIGHT = 3
    DOWN = 4


class UiHighlightDirectionStrings(object):
    LEFT = 'left'
    UP = 'up'
    RIGHT = 'right'
    DOWN = 'down'


DIRECTION_STRING_TO_ID = {UiHighlightDirectionStrings.LEFT: UiHighlightDirections.LEFT,
 UiHighlightDirectionStrings.UP: UiHighlightDirections.UP,
 UiHighlightDirectionStrings.RIGHT: UiHighlightDirections.RIGHT,
 UiHighlightDirectionStrings.DOWN: UiHighlightDirections.DOWN}
