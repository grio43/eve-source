#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanEditor\dragIndicatorLine.py
from carbonui import uiconst
from carbonui.primitives.line import Line
from carbonui.util.color import Color

class DragIndicatorLine(Line):
    default_color = Color.GRAY7
    default_height = 2
    default_state = uiconst.UI_DISABLED
