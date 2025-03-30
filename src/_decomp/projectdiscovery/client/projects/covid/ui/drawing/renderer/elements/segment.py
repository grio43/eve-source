#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\renderer\elements\segment.py
from carbonui import const
from carbonui.primitives import container
from carbonui.primitives import vectorline
from projectdiscovery.client.projects.covid.ui.drawing.renderer.elements import colors
import logging
log = logging.getLogger('projectdiscovery.covid.renderer.segment')
SEGMENT_WIDTH = 4
SEGMENT_WIDTH_INNER = 2
SEGMENT_STYLE_DEFAULT = 1
SEGMENT_STYLE_INVALID = 2
SEGMENT_STYLE_GOLD = 3

class Segment(container.Container):
    default_name = 'segment'
    default_state = const.UI_DISABLED
    default_idx = 0
    default_align = const.BOTTOMLEFT
    default_width = 10
    default_height = 10
    default_start = (0, 0)
    default_end = (100, 100)
    default_segment_style = SEGMENT_STYLE_DEFAULT

    def __init__(self, start = None, end = None, segment_style = None, **attributes):
        self.segment_style = segment_style or Segment.default_segment_style
        self._start = start or Segment.default_start
        self._end = end or Segment.default_end
        self.outer = None
        self.inner = None
        super(Segment, self).__init__(segment_style=self.segment_style, **attributes)

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, new_pos):
        self._start = new_pos
        self.outer.translationFrom = self.y_flipped_start
        self.inner.translationFrom = self.y_flipped_start

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, new_pos):
        self._end = new_pos
        self.outer.translationTo = self.y_flipped_end
        self.inner.translationTo = self.y_flipped_end

    @property
    def y_flipped_start(self):
        return (self._start[0], -self._start[1])

    @y_flipped_start.setter
    def y_flipped_start(self, new_flipped_pos):
        self.start = (new_flipped_pos[0], -new_flipped_pos[1])

    @property
    def y_flipped_end(self):
        return (self._end[0], -self._end[1])

    @y_flipped_end.setter
    def y_flipped_end(self, new_flipped_pos):
        self.end = (new_flipped_pos[0], -new_flipped_pos[1])

    def ApplyAttributes(self, attributes):
        super(Segment, self).ApplyAttributes(attributes)
        self.outer = vectorline.VectorLine(parent=self, name='segment_outer', colorFrom=colors.BLACK.as_tuple, colorTo=colors.BLACK.as_tuple, widthFrom=SEGMENT_WIDTH, widthTo=SEGMENT_WIDTH, align=const.BOTTOMLEFT, translationFrom=self.y_flipped_start, translationTo=self.y_flipped_end)
        self.inner = vectorline.VectorLine(parent=self, name='segment_inner', colorFrom=colors.PDC19_BLUE.as_tuple, colorTo=colors.PDC19_BLUE.as_tuple, widthFrom=SEGMENT_WIDTH_INNER, widthTo=SEGMENT_WIDTH_INNER, align=const.BOTTOMLEFT, idx=0, translationFrom=self.y_flipped_start, translationTo=self.y_flipped_end)
        self.update_style(self.segment_style)

    def update_style(self, new_style):
        if self.segment_style != new_style:
            self.segment_style = new_style
            if self.segment_style == SEGMENT_STYLE_INVALID:
                self.inner.colorFrom = colors.PDC19_RED.as_tuple
                self.inner.colorTo = colors.PDC19_RED.as_tuple
            else:
                self.inner.colorFrom = colors.PDC19_BLUE.as_tuple
                self.inner.colorTo = colors.PDC19_BLUE.as_tuple

    def set_style_default(self):
        self.update_style(SEGMENT_STYLE_DEFAULT)

    def set_style_invalid(self):
        self.update_style(SEGMENT_STYLE_INVALID)
