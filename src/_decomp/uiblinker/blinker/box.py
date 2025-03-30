#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\blinker\box.py
import chroma
import eveui
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.transform import Transform
from uiblinker.blinker.base import Blinker
from uiblinker.blinker.util import get_element_bounding_box

class BoxBlinker(Blinker, Container):
    size_min = 24
    inner_padding = 4

    def __init__(self, parent = None, align = uiconst.TOPLEFT, left = 0, top = 0, width = 24, height = 24):
        self._inner = None
        self._outer = None
        self._outer_transform = None
        super(BoxBlinker, self).__init__(parent=parent, align=align, left=left, top=top, width=max(width, self.size_min), height=max(height, self.size_min))

    @staticmethod
    def create_for(element, parent):
        left, top, width, height = get_element_bounding_box(element)
        left, top, width, height = BoxBlinker._compute_blink_area(left, top, width, height)
        return BoxBlinker(parent=parent, left=left, top=top, width=width, height=height)

    def layout(self, parent):
        self._inner = Frame(parent=parent, align=uiconst.TOALL, frameConst=uiconst.FRAME_BORDER2_CORNER0, color=chroma.Color.from_hex('#58A7BF').rgb, opacity=0.0)
        self._outer_transform = Transform(parent=parent, align=uiconst.TOALL, padding=-4, scalingCenter=(0.5, 0.5))
        self._outer = Frame(parent=self._outer_transform, align=uiconst.TOALL, frameConst=uiconst.FRAME_BORDER2_CORNER0, color=chroma.Color.from_hex('#58A7BF').rgb, opacity=0.0)

    def update_blink_area(self, element):
        left, top, width, height = get_element_bounding_box(element)
        self.pos = self._compute_blink_area(left, top, width, height)

    def animate_blink_pulse(self):
        eveui.fade_in(self._outer, end_value=1.5, duration=1.2, time_offset=0.1, curve_type=eveui.CurveType.wave)
        end_scale_vertical = 1.0 + max(0.0, 5.0 / self.height)
        end_scale_horizontal = 1.0 + max(0.0, 5.0 / self.width)
        eveui.animate(self._outer_transform, 'scale', start_value=(1.0, 1.0), end_value=(end_scale_horizontal, end_scale_vertical), duration=1.2, time_offset=0.1)
        eveui.fade_in(self._inner, end_value=3.0, duration=0.5, sleep=True)
        eveui.fade(self._inner, end_value=0.25, duration=1.5, sleep=True)

    @classmethod
    def _compute_blink_area(cls, left, top, width, height):
        width += 2 * cls.inner_padding
        height += 2 * cls.inner_padding
        left -= cls.inner_padding
        top -= cls.inner_padding
        left += int(round(min(width - cls.size_min, 0) / 2.0))
        top += int(round(min(height - cls.size_min, 0) / 2.0))
        return (left,
         top,
         max(width, cls.size_min),
         max(height, cls.size_min))
