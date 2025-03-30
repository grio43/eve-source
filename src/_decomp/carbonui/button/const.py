#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\button\const.py
import enum
HEIGHT_NORMAL = 32
HEIGHT_COMPACT = 24
HEIGHT_EXPANDED = 40

class InteractionState(enum.Enum):
    hovered = 1
    pressed = 2
    disabled = 3
    focused = 4
    selected = 5


class ButtonStyle(enum.Enum):
    NORMAL = 1
    WARNING = 2
    DANGER = 3
    MONETIZATION = 4
    SUCCESS = 5


class ButtonVariant(enum.Enum):
    NORMAL = 1
    PRIMARY = 2
    GHOST = 3


class ButtonFrameType(enum.Enum):
    RECTANGLE = 1
    CUT_BOTTOM_RIGHT = 2
    CUT_BOTTOM_LEFT = 3
    CUT_BOTTOM_LEFT_RIGHT = 4
