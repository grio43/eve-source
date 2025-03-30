#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\constants.py
import enum
import carbonui.uiconst

class Align(int, enum.Enum):
    absolute = carbonui.uiconst.ABSOLUTE
    bottom_left = carbonui.uiconst.BOTTOMLEFT
    bottom_right = carbonui.uiconst.BOTTOMRIGHT
    center = carbonui.uiconst.CENTER
    center_bottom = carbonui.uiconst.CENTERBOTTOM
    center_left = carbonui.uiconst.CENTERLEFT
    center_right = carbonui.uiconst.CENTERRIGHT
    center_top = carbonui.uiconst.CENTERTOP
    no_align = carbonui.uiconst.NOALIGN
    to_all = carbonui.uiconst.TOALL
    to_bottom = carbonui.uiconst.TOBOTTOM
    to_bottom_no_push = carbonui.uiconst.TOBOTTOM_NOPUSH
    to_bottom_prop = carbonui.uiconst.TOBOTTOM_PROP
    to_left = carbonui.uiconst.TOLEFT
    to_left_no_push = carbonui.uiconst.TOLEFT_NOPUSH
    to_left_prop = carbonui.uiconst.TOLEFT_PROP
    to_right = carbonui.uiconst.TORIGHT
    to_right_no_push = carbonui.uiconst.TORIGHT_NOPUSH
    to_right_prop = carbonui.uiconst.TORIGHT_PROP
    to_top = carbonui.uiconst.TOTOP
    to_top_no_push = carbonui.uiconst.TOTOP_NOPUSH
    to_top_prop = carbonui.uiconst.TOTOP_PROP
    top_left = carbonui.uiconst.TOPLEFT
    top_left_prop = carbonui.uiconst.TOPLEFT_PROP
    top_right = carbonui.uiconst.TOPRIGHT


class State(int, enum.Enum):
    disabled = carbonui.uiconst.UI_DISABLED
    hidden = carbonui.uiconst.UI_HIDDEN
    normal = carbonui.uiconst.UI_NORMAL
    pick_children = carbonui.uiconst.UI_PICKCHILDREN
