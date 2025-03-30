#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\linemarkers.py
from carbon.common.script.util.format import FmtAmt
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveLabelVertical import VerticalLabel
from math import pi
LINE_WIDTH = 8
LINE_HEIGHT = 1
LINE_LEFT = 15
LINE_COLOR = (0.96, 0.96, 0.96, 1.0)
VALUE_FONTSIZE = 10
VALUE_WIDTH = 28
VALUE_LEFT = 18
VALUE_COLOR = (0.96, 0.96, 0.96, 1.0)
MARKER_WIDTH = LINE_LEFT + LINE_WIDTH + VALUE_LEFT + VALUE_WIDTH
MARKER_HEIGHT = 15
CORNER_WIDTH = 8
CORNER_HEIGHT = 8
CORNER_TEXTURE_PATH = 'res:/UI/Texture/classes/ProjectDiscovery/covid/corner_decoration.png'
CLUSTERS_MARKED_FONTSIZE = 10
CLUSTERS_MARKED_COLOR = (0.96, 0.96, 0.96, 1.0)

class LineMarker(Container):
    default_state = uiconst.UI_HIDDEN
    default_shouldShowValue = False
    default_isHorizontal = True
    default_isInverted = False

    def ApplyAttributes(self, attributes):
        super(LineMarker, self).ApplyAttributes(attributes)
        self.should_show_value = attributes.get('shouldShowValue', self.default_shouldShowValue)
        self.is_horizontal = attributes.get('isHorizontal', self.default_isHorizontal)
        self.is_inverted = attributes.get('isInverted', self.default_isInverted)
        if self.is_horizontal:
            self.width, self.height = MARKER_WIDTH, MARKER_HEIGHT
        else:
            self.width, self.height = MARKER_HEIGHT, MARKER_WIDTH
        self.setup_layout()

    def setup_layout(self):
        self._add_line()
        self._add_value()

    def _add_line(self):
        if self.is_horizontal:
            width, height = LINE_WIDTH, LINE_HEIGHT
            left, top = LINE_LEFT, 0
            align = uiconst.CENTERRIGHT if self.is_inverted else uiconst.CENTERLEFT
        else:
            width, height = LINE_HEIGHT, LINE_WIDTH
            left, top = 0, LINE_LEFT
            align = uiconst.CENTERBOTTOM if self.is_inverted else uiconst.CENTERTOP
        self.line = Line(name='line', parent=self, align=align, width=width, height=height, left=left, top=top, color=LINE_COLOR)

    def _add_value(self):
        if self.should_show_value:
            if self.is_horizontal:
                label_class = Label
                rotation = 0.0
                left, top = self.line.left + self.line.width + VALUE_LEFT, 0
                align = uiconst.CENTERRIGHT if self.is_inverted else uiconst.CENTERLEFT
            else:
                left, top = -MARKER_HEIGHT / 2, self.line.top + self.line.height + VALUE_LEFT
                if not self.is_inverted:
                    top = top + VALUE_WIDTH
                align = uiconst.CENTERBOTTOM if self.is_inverted else uiconst.CENTERTOP
                label_class = VerticalLabel
                rotation = pi / 2
            self.value = label_class(name='value', parent=self, align=align, fontsize=VALUE_FONTSIZE, left=left, top=top, color=VALUE_COLOR, labelClass=Label, rotation=rotation)
        else:
            self.value = None

    def set_x(self, x):
        self.left = x - MARKER_HEIGHT / 2

    def set_y(self, y):
        self.top = y - MARKER_HEIGHT / 2

    def update_value(self, value):
        if self.value:
            self.value.SetText(FmtAmt(value, showFraction=2))


class LineMarkersDecoration(Container):

    def ApplyAttributes(self, attributes):
        super(LineMarkersDecoration, self).ApplyAttributes(attributes)
        self.is_enabled = True
        self.mouse_move_cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.on_general_move)
        self._add_markers()

    def _add_markers(self):
        top_marker = LineMarker(name='top_marker', parent=self, align=uiconst.TOPLEFT, left=-MARKER_HEIGHT / 2, shouldShowValue=True, isHorizontal=False)
        bottom_marker = LineMarker(name='bottom_marker', parent=self, align=uiconst.BOTTOMLEFT, left=-MARKER_HEIGHT / 2, isHorizontal=False, isInverted=True)
        self.x_markers = [top_marker, bottom_marker]
        left_marker = LineMarker(name='left_marker', parent=self, align=uiconst.TOPLEFT, top=-MARKER_HEIGHT / 2)
        right_marker = LineMarker(name='right_marker', parent=self, align=uiconst.TOPRIGHT, top=-MARKER_HEIGHT / 2, shouldShowValue=True, isInverted=True)
        self.y_markers = [left_marker, right_marker]

    def Close(self):
        uicore.event.UnregisterForTriuiEvents(self.mouse_move_cookie)
        super(LineMarkersDecoration, self).Close()

    def Enable(self, *args):
        self.is_enabled = True
        super(LineMarkersDecoration, self).SetState(uiconst.UI_PICKCHILDREN)
        self.mouse_move_cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.on_general_move)

    def Disable(self, *args):
        self.is_enabled = False
        super(LineMarkersDecoration, self).Disable(*args)
        uicore.event.UnregisterForTriuiEvents(self.mouse_move_cookie)

    def update_marker_positions(self, x, y):
        for marker in self.x_markers:
            marker.set_x(x)
            marker.update_value(float(x) / self.width * 100)

        for marker in self.y_markers:
            marker.set_y(y)
            marker.update_value(float(y) / self.height * 100)

    def show_markers(self):
        for marker in self.x_markers + self.y_markers:
            marker.SetState(uiconst.UI_DISABLED)

    def hide_markers(self):
        for marker in self.x_markers + self.y_markers:
            marker.Hide()

    def is_position_in_area(self, x, y):
        return 0 <= x <= self.width and 0 <= y <= self.height

    def on_general_move(self, *args):
        if self.is_enabled and self.width > 0 and self.height > 0:
            x = uicore.uilib.x - self.absoluteLeft
            y = uicore.uilib.y - self.absoluteTop
            if self.is_position_in_area(x, y):
                self.update_marker_positions(x, y)
                self.show_markers()
                return True
        self.hide_markers()
        return True
