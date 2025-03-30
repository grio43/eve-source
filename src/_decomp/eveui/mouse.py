#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\mouse.py
import collections
import enum
import carbonui.uiconst
import carbonui.uicore
Position = collections.namedtuple('Position', ('x', 'y'))

class Mouse(int, enum.Enum):

    @staticmethod
    def position():
        return Position(carbonui.uicore.uicore.uilib.x, carbonui.uicore.uicore.uilib.y)

    @staticmethod
    def set_cursor(self, cursor):
        carbonui.uicore.uicore.uilib.SetCursor(cursor)

    @property
    def is_down(self):
        return carbonui.uicore.uicore.uilib.GetMouseButtonState(self.value)

    left = carbonui.uiconst.MOUSELEFT
    right = carbonui.uiconst.MOUSERIGHT
    middle = carbonui.uiconst.MOUSEMIDDLE
    back = carbonui.uiconst.MOUSEXBUTTON1
    forward = carbonui.uiconst.MOUSEXBUTTON2


class MouseCursor(str, enum.Enum):
    default = carbonui.uiconst.UICURSOR_DEFAULT
    select = carbonui.uiconst.UICURSOR_SELECT
    draggable = carbonui.uiconst.UICURSOR_DRAGGABLE
    ibeam = carbonui.uiconst.UICURSOR_IBEAM
    divider_adjust = carbonui.uiconst.UICURSOR_DIVIDERADJUST
    none = carbonui.uiconst.UICURSOR_NONE
    vertical_resize = carbonui.uiconst.UICORSOR_VERTICAL_RESIZE
    has_menu = carbonui.uiconst.UICURSOR_HASMENU
    top_right_bottom_left_drag = carbonui.uiconst.UICURSOR_TOP_RIGHT_BOTTOM_LEFT_DRAG
    top_left_bottom_right_drag = carbonui.uiconst.UICURSOR_TOP_LEFT_BOTTOM_RIGHT_DRAG
    left_right_drag = carbonui.uiconst.UICURSOR_LEFT_RIGHT_DRAG
    top_bottom_drag = carbonui.uiconst.UICURSOR_TOP_BOTTOM_DRAG
    horizontal_resize = carbonui.uiconst.UICORSOR_HORIZONTAL_RESIZE
    finger = carbonui.uiconst.UICORSOR_FINGER
    pointer_menu = carbonui.uiconst.UICURSOR_POINTER_MENU
    magnifier = carbonui.uiconst.UICURSOR_MAGNIFIER
    cc_up_down = carbonui.uiconst.UICURSOR_CCUPDOWN
    cc_left_right = carbonui.uiconst.UICURSOR_CCLEFTRIGHT
    cc_all_directions = carbonui.uiconst.UICURSOR_CCALLDIRECTIONS
    cc_selection = carbonui.uiconst.UICURSOR_CCSELECTION
    cc_head_tilt = carbonui.uiconst.UICURSOR_CCHEADTILT
    cc_shoulder_twist = carbonui.uiconst.UICURSOR_CCSHOULDERTWIST
    cc_head_all = carbonui.uiconst.UICURSOR_CCHEADALL
