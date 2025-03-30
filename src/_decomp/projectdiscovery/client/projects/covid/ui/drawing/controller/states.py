#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\controller\states.py
import enum

class DrawingState(enum.IntEnum):
    UNKNOWN = 0
    DISABLED = 1
    READY = 2
    DRAWING = 3
    MOVING_VERTEX = 4
    MOVING_POLYGON = 5


class CursorState(enum.IntEnum):
    UNKNOWN = 0
    DISABLED = 1
    READY = 2
    DRAWING = 3
    MODIFYING = 4


class CursorTarget(enum.IntEnum):
    UNKNOWN = 0
    CANVAS = 1
    POLYGON = 2
    VERTEX = 3
    X_BUTTON = 4
    OFF_CANVAS = 5


class NewDrawingState(enum.IntEnum):
    UNKNOWN = 0
    DISABLED = 1
    READY = 2
    DRAWING = 3


class MovementState(enum.IntEnum):
    UNKNOWN = 0
    DISABLED = 1
    READY = 2
    STARTING = 3
    MOVING = 4


class AdjustmentState(enum.IntEnum):
    UNKNOWN = 0
    DISABLED = 1
    READY = 2
    MOVING = 3
