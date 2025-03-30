#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\blinker\ring.py
from __future__ import division
import math
import chroma
import eveui
import mathext
import threadutils
import trinity
import uthread2
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.transform import Transform
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from uiblinker.blinker.base import Blinker
from uiblinker.blinker.util import get_element_bounding_box

class RingBlinker(Blinker, Container):
    size_min = 24

    def __init__(self, parent = None, align = uiconst.TOPLEFT, left = 0, top = 0, size = 24):
        self._size = max(size, self.size_min)
        self._main_cont = None
        self._inner_wrap = None
        self._inner = None
        self._outer_transform = None
        self._outer = None
        self._resizing = False
        self._start_pending = False
        super(RingBlinker, self).__init__(parent=parent, align=align, left=left, top=top, width=size, height=size)

    @staticmethod
    def create_for(element, parent):
        left, top, width, height = get_element_bounding_box(element)
        left, top, size = RingBlinker._compute_position_and_size(left, top, width, height)
        return RingBlinker(parent=parent, left=left, top=top, size=size)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        value = max(value, self.size_min)
        if self._size != value:
            self._size = value
            self.width = value
            self.height = value
            if not self._resizing:
                self._resizing = True
                self._update_size()

    def layout(self, parent):
        self._main_cont = Container(parent=parent, align=uiconst.TOALL)
        self._inner_wrap = Container(parent=self._main_cont, align=uiconst.TOALL, opacity=0.0)
        self._inner = Ring(parent=self._inner_wrap, align=uiconst.CENTER, line_width=2.0, radius=self._size / 2.0, color=chroma.Color.from_hex('#58A7BF').rgb)
        self._outer_transform = Transform(parent=self._main_cont, align=uiconst.CENTER)
        self._outer = Ring(parent=self._outer_transform, align=uiconst.CENTER, line_width=1.5, radius=self._size / 2.0 + 4, color=chroma.Color.from_hex('#58A7BF').rgb, opacity=0.0)

    def update_blink_area(self, element):
        left, top, width, height = get_element_bounding_box(element)
        left, top, size = self._compute_position_and_size(left, top, width, height)
        self.left = left
        self.top = top
        self.size = size

    def animate_blink_pulse(self):
        eveui.fade(self._outer, start_value=0.0, end_value=1.5, duration=1.2, time_offset=0.1, curve_type=eveui.CurveType.wave)
        end_scale = 1.0 + max(0.0, 6.0 / self.size)
        eveui.animate(self._outer_transform, 'scale', start_value=(1.0, 1.0), end_value=(end_scale, end_scale), duration=1.2, time_offset=0.1)
        eveui.fade_in(self._inner_wrap, duration=0.16666666666666666, curve_type=eveui.CurveType.linear)
        eveui.animate(self._inner, 'opacity_overshot', end_value=2.0, duration=0.3333333333333333, time_offset=0.16666666666666666, curve_type=eveui.CurveType.linear)
        uthread2.sleep(0.5)
        eveui.animate(self._inner, 'opacity_overshot', end_value=0.0, duration=0.75, curve_type=eveui.CurveType.linear)
        eveui.fade(self._inner_wrap, end_value=0.25, duration=0.75, time_offset=0.75, sleep=True)

    def start(self):
        if not self.blinking and self._resizing:
            self._start_pending = True
        else:
            self._start_pending = False
            super(RingBlinker, self).start()

    @staticmethod
    def _compute_position_and_size(left, top, width, height):
        size = max(width, height)
        left += int(round((width - size) / 2.0))
        top += int(round((height - size) / 2.0))
        return (left, top, size)

    @threadutils.threaded
    def _update_size(self):
        self.stop(wait=True)
        if self.destroyed:
            return
        self._inner.radius = self._size / 2.0
        self._outer.radius = self._size / 2.0 + 4
        self._resizing = False
        if self._start_pending:
            self.start()


class Ring(VectorLineTrace):

    def __init__(self, parent, align, line_width = 1.0, radius = 1.0, color = (1.0, 1.0, 1.0), opacity = 1.0, blend_mode = trinity.TR2_SBM_BLEND):
        self._radius = radius
        self._opacity_overshot = 0.0
        self._real_color = color
        self._real_line_width = line_width
        self._line_color = (1.0, 1.0, 1.0)
        super(Ring, self).__init__(parent=parent, align=align, state=uiconst.UI_DISABLED, lineWidth=eveui.scale_dpi(line_width), isLoop=True, color=color, opacity=opacity, blendMode=blend_mode)
        self._generate_points()

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if self._radius != value:
            self._radius = value
            self._regenerate()

    @property
    def opacity_overshot(self):
        return self._opacity_overshot

    @opacity_overshot.setter
    def opacity_overshot(self, value):
        self._opacity_overshot = value
        r, g, b = self._real_color
        self.color = (min(r + r * (1.0 + value), 1.0), min(g + g * (1.0 + value), 1.0), min(b + b * (1.0 + value), 1.0))

    def _regenerate(self):
        self.Flush()
        self._generate_points()

    def _generate_points(self):
        outer_radius = self._radius + self.lineWidth
        segment_arc_length = mathext.lerp(3.0, 10.0, mathext.clamp((outer_radius - 10) / 50, 0.0, 1.0))
        segment_sweep_angle = segment_arc_length / outer_radius
        segments = int(max(5.0, round(2 * math.pi / segment_sweep_angle)))
        radian_per_segment = math.pi * 2 / segments
        point_offset = self._radius + self.lineWidth / 2.0
        for i in range(segments):
            self.AddPoint(pos=(math.cos(radian_per_segment * i) * point_offset, math.sin(radian_per_segment * i) * point_offset), color=(1.0, 1.0, 1.0, 1.0))

    def UpdateUIScaling(self, value, oldValue):
        self.lineWidth = eveui.scale_dpi(self._real_line_width)
        self._regenerate()
