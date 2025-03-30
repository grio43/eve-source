#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\renderer\elements\polygon.py
from carbonui import const
from carbonui.primitives import polygon as carbon_polygon
from carbonui.primitives import base
from . import segmentchain
from . import colors
from . import segment
from . import vertex
import logging
log = logging.getLogger('projectdiscovery.covid.renderer.polygon')
POLYGON_STYLE_DEFAULT = 1
POLYGON_STYLE_HOVER = 2
POLYGON_STYLE_ACTIVE = 3
POLYGON_STYLE_INVALID = 4
POLYGON_STYLE_INVALID_ACTIVE = 5
POLYGON_STYLE_MOVING = 6
POLYGON_STYLE_GOLD = 7

class PolygonFiller(carbon_polygon.Polygon):
    default_state = const.UI_NORMAL

    def __init__(self, polygon_uuid = None, mouse_enter_callback = None, **attributes):
        self.polygon_uuid = polygon_uuid
        self.mouse_enter_callback = mouse_enter_callback
        super(PolygonFiller, self).__init__(**attributes)

    def OnMouseExit(self, *args):
        log.warning('%s:OnMouseExit:self=%r, args=%r', self.__class__.__name__, self, args)
        if self.mouse_enter_callback:
            self.mouse_enter_callback(polygon_uuid=self.polygon_uuid, is_exit=True)

    def OnMouseEnter(self, *args):
        log.warning('%s:OnMouseEnter:self=%r, args=%r', self.__class__.__name__, self, args)
        if self.mouse_enter_callback:
            self.mouse_enter_callback(polygon_uuid=self.polygon_uuid)


class Polygon(segmentchain.SegmentChain):
    default_name = 'polygon'
    default_height = 1
    default_width = 1
    default_polygon_style = POLYGON_STYLE_DEFAULT
    default_state = const.UI_PICKCHILDREN

    def __init__(self, polygon_uuid = None, mouse_enter_callback = None, vertex_enter_callback = None, points = None, polygon_style = None, **attributes):
        self.polygon_style = polygon_style or Polygon.default_polygon_style
        self.filler = None
        self._filler_color = colors.BLACK.opaque(0.1).as_tuple
        self._inner_boundry = (0, 0, 0, 0)
        self._outer_boundry = (0, 0, 0, 0)
        self._move_transation = (0, 0)
        self.polygon_uuid = polygon_uuid
        self.mouse_enter_callback = mouse_enter_callback
        self.vertex_enter_callback = vertex_enter_callback
        self.adjust_mode = False
        super(Polygon, self).__init__(points=points, polygon_style=self.polygon_style, **attributes)

    def _calc_boundary(self):
        tmp = [9999999,
         9999999,
         -9999999,
         -9999999]
        for px, py in self._points:
            tmp[0] = min(tmp[0], px)
            tmp[1] = min(tmp[1], py)
            tmp[2] = max(tmp[2], px)
            tmp[3] = max(tmp[3], py)

        self._inner_boundry = (tmp[0],
         tmp[1],
         tmp[2] - tmp[0],
         tmp[3] - tmp[1])
        self._outer_boundry = (self._inner_boundry[0] - vertex.VERTEX_SHIFT_SIZE,
         self._inner_boundry[1] - vertex.VERTEX_SHIFT_SIZE,
         self._inner_boundry[2] + vertex.VERTEX_SIZE,
         self._inner_boundry[3] + vertex.VERTEX_SIZE)

    def _constrain_to_boundary(self):
        self.left = self._outer_boundry[0]
        self.top = self._outer_boundry[1]
        self.width = self._outer_boundry[2]
        self.height = self._outer_boundry[3]

    def set_translation(self, x, y):
        self._move_transation = (x, y)
        self._apply_translation()

    def _apply_translation(self):
        self.left = self._outer_boundry[0] + self._move_transation[0]
        self.top = self._outer_boundry[1] + self._move_transation[1]

    def ApplyAttributes(self, attributes):
        super(Polygon, self).ApplyAttributes(attributes)
        self.filler = PolygonFiller(polygon_uuid=self.polygon_uuid, mouse_enter_callback=self.mouse_enter_callback, parent=self, name='polygon_filler', idx=-1, align=const.TOPLEFT)
        self.update_style(self.polygon_style, force=True)
        self.redraw_filler()

    def redraw(self):
        if not self.adjust_mode:
            self._calc_boundary()
            self._constrain_to_boundary()
            if self.filler:
                self.redraw_filler()
                super(Polygon, self).redraw()
            self._apply_translation()

    def redraw_filler(self):
        if not self.adjust_mode:
            self.filler.Flush()
            for px, py in self._points:
                self.filler.AddPoint(base.ScaleDpi(px - self.left), base.ScaleDpi(self.height - py + self.top), self._filler_color)

            self.filler.Triangulate()

    def redraw_vertices(self):
        if self.polygon_style != POLYGON_STYLE_GOLD:
            if not self.adjust_mode:
                while self.vertex_list:
                    v = self.vertex_list.pop()
                    v.Close()

                self.vertex_list = []
                for i, p in enumerate(self.points):
                    x, y = self._pixel_shift(p[0], p[1], False)
                    self.vertex_list.append(vertex.Vertex(polygon_uuid=self.polygon_uuid, vertex_index=i, mouse_enter_callback=self.vertex_enter_callback, parent=self, state=const.UI_NORMAL, vertex_style=vertex.VERTEX_STYLE_DEFAULT, left=x, top=y))

    def _pixel_shift(self, x, y, flip_y = True):
        if flip_y:
            return (x - self._inner_boundry[0] + vertex.VERTEX_SHIFT_SIZE, -(y - self._inner_boundry[1] + vertex.VERTEX_SHIFT_SIZE))
        return (x - self._inner_boundry[0] + vertex.VERTEX_SHIFT_SIZE, y - self._inner_boundry[1] + vertex.VERTEX_SHIFT_SIZE)

    def redraw_outer(self):
        if self.polygon_style != POLYGON_STYLE_GOLD:
            self.outer.Flush()
            color = colors.BLACK.as_tuple
            for px, py in self._points:
                self.outer.AddPoint(self._pixel_shift(px, py), color)

            self.outer.AddPoint(self._pixel_shift(self._points[0][0], self._points[0][1]), colors.BLACK.as_tuple)

    def redraw_inner(self):
        self.inner.Flush()
        if self.polygon_style == POLYGON_STYLE_GOLD:
            color = colors.PDC19_SOLUTION_LINES.as_tuple
        else:
            color = colors.PDC19_RED.as_tuple if self.segment_style == segment.SEGMENT_STYLE_INVALID else colors.PDC19_BLUE.as_tuple
        for px, py in self._points:
            self.inner.AddPoint(self._pixel_shift(px, py), color)

        self.inner.AddPoint(self._pixel_shift(self._points[0][0], self._points[0][1]), color)

    def update_style(self, new_style, force = False):
        if self.polygon_style != new_style or force:
            self.polygon_style = new_style
            if self.polygon_style == POLYGON_STYLE_INVALID_ACTIVE:
                self.segment_style = segment.SEGMENT_STYLE_INVALID
                self._filler_color = colors.PDC19_RED.opaque(0.4).as_tuple
            elif self.polygon_style == POLYGON_STYLE_INVALID:
                self.segment_style = segment.SEGMENT_STYLE_INVALID
                self._filler_color = colors.PDC19_RED.opaque(0.2).as_tuple
            elif self.polygon_style == POLYGON_STYLE_ACTIVE:
                self.segment_style = segment.SEGMENT_STYLE_DEFAULT
                self._filler_color = colors.PDC19_BLUE.opaque(0.4).as_tuple
            elif self.polygon_style == POLYGON_STYLE_HOVER:
                self.segment_style = segment.SEGMENT_STYLE_DEFAULT
                self._filler_color = colors.PDC19_BLUE.opaque(0.2).as_tuple
            elif self.polygon_style == POLYGON_STYLE_MOVING:
                self.segment_style = segment.SEGMENT_STYLE_DEFAULT
                self._filler_color = colors.PDC19_WHITE.opaque(0.1).as_tuple
            elif self.polygon_style == POLYGON_STYLE_GOLD:
                self.segment_style = segment.SEGMENT_STYLE_GOLD
                self._filler_color = colors.PDC19_SOLUTION_FILL.as_tuple
            else:
                self.segment_style = segment.SEGMENT_STYLE_DEFAULT
                self._filler_color = colors.BLACK.opaque(0.1).as_tuple
            self.redraw()

    def set_style_default(self):
        self.update_style(POLYGON_STYLE_DEFAULT)

    def set_style_hover(self):
        self.update_style(POLYGON_STYLE_HOVER)

    def set_style_active(self):
        self.update_style(POLYGON_STYLE_ACTIVE)

    def set_style_invalid(self):
        self.update_style(POLYGON_STYLE_INVALID)

    def set_style_invalid_active(self):
        self.update_style(POLYGON_STYLE_INVALID_ACTIVE)

    def set_adjust_mode(self):
        self.adjust_mode = True
        self.filler.Hide()
        self.inner.Hide()
        self.outer.Hide()
        self.width = self.parent.width
        self.height = self.parent.height
        self.top = 0
        self.left = 0
        while self.vertex_list:
            v = self.vertex_list.pop()
            v.Hide()

    def unset_adjust_mode(self):
        self.adjust_mode = False
        self.filler.Show()
        self.inner.Show()
        self.outer.Show()
        self.redraw()
