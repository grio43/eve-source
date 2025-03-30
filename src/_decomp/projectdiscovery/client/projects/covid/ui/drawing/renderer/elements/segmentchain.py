#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\renderer\elements\segmentchain.py
from carbonui import const
from carbonui.primitives import container
from carbonui.primitives import vectorlinetrace
from . import segment, colors
from . import vertex
import logging
log = logging.getLogger('projectdiscovery.covid.renderer.segmentchain')

class SegmentChain(container.Container):
    default_name = 'segment_chain'
    default_state = const.UI_DISABLED
    default_idx = 0
    default_align = const.BOTTOMLEFT
    default_width = 10
    default_height = 10
    default_segment_style = segment.SEGMENT_STYLE_DEFAULT

    def __init__(self, points = None, segment_style = None, **attributes):
        self.segment_style = segment_style or SegmentChain.default_segment_style
        self.outer = None
        self.inner = None
        self._points = points or []
        self.vertex_list = []
        super(SegmentChain, self).__init__(segment_style=self.segment_style, **attributes)

    def ApplyAttributes(self, attributes):
        super(SegmentChain, self).ApplyAttributes(attributes)
        self.outer = vectorlinetrace.VectorLineTrace(parent=self, name='segment_chain_outer', lineWidth=segment.SEGMENT_WIDTH, cornerType=vectorlinetrace.CORNERTYPE_NONE, align=const.BOTTOMLEFT)
        self.inner = vectorlinetrace.VectorLineTrace(parent=self, name='segment_chain_inner', lineWidth=segment.SEGMENT_WIDTH_INNER, cornerType=vectorlinetrace.CORNERTYPE_NONE, align=const.BOTTOMLEFT, idx=0)
        self.redraw()

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, new_point_list):
        self._points = new_point_list
        self.redraw()

    def add_point(self, new_point):
        self._points.append(new_point)
        self.redraw()

    def pop_point(self):
        p = self._points.pop(-1)
        self.redraw()
        return p

    def clear(self):
        self._points = []
        self.redraw()

    def redraw(self):
        self.redraw_outer()
        self.redraw_inner()
        self.redraw_vertices()

    def redraw_vertices(self):
        while self.vertex_list:
            v = self.vertex_list.pop()
            v.Close()

        self.vertex_list = []
        first = True
        for p in self.points:
            self.vertex_list.append(vertex.Vertex(parent=self, vertex_style=vertex.VERTEX_STYLE_OPEN if first else vertex.VERTEX_STYLE_DEFAULT, left=p[0], top=p[1]))
            first = False

    def redraw_outer(self):
        self.outer.Flush()
        color = colors.BLACK.as_tuple
        for px, py in self._points:
            self.outer.AddPoint((px, -py), color)

    def redraw_inner(self):
        self.inner.Flush()
        color = colors.PDC19_RED.as_tuple if self.segment_style == segment.SEGMENT_STYLE_INVALID else colors.PDC19_BLUE.as_tuple
        for px, py in self._points:
            self.inner.AddPoint((px, -py), color)

    def update_style(self, new_style):
        if self.segment_style != new_style:
            self.segment_style = new_style
            self.redraw_inner()

    def set_style_default(self):
        self.update_style(segment.SEGMENT_STYLE_DEFAULT)

    def set_style_invalid(self):
        self.update_style(segment.SEGMENT_STYLE_INVALID)
