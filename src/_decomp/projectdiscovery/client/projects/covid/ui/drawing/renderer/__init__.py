#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\renderer\__init__.py
import signals
from carbonui import uiconst
from projectdiscovery.client.projects.covid.ui.drawing.renderer import elements
AREA_SIZE = 512
RULER_WIDTH = 20
BOTTOM_LINE_WIDTH = 1
import logging
log = logging.getLogger('projectdiscovery.covid.renderer')

class DrawingRenderer(object):

    def __init__(self, controller, parent_container):
        self.controller = controller
        self.parent_container = parent_container
        self._last_polygon_frame = -1
        self._last_segment_frame = -1
        self._last_cursor_state_frame = -1
        self.bottom_line = elements.minor.BottomLine(parent=self.parent_container, align=uiconst.BOTTOMLEFT, width=AREA_SIZE + RULER_WIDTH * 2, height=BOTTOM_LINE_WIDTH)
        self.corner_sw = elements.minor.Corner(parent=self.parent_container, orientation=elements.minor.Corner.ORIENTATION_NE, align=uiconst.BOTTOMLEFT, width=RULER_WIDTH, height=RULER_WIDTH, top=BOTTOM_LINE_WIDTH)
        self.ruler_s = elements.ruler.Ruler(parent=self.parent_container, orientation=elements.ruler.ORIENTATION_UP, show_label=False, align=uiconst.BOTTOMLEFT, width=AREA_SIZE, height=AREA_SIZE, top=BOTTOM_LINE_WIDTH, left=RULER_WIDTH)
        middle_nudge = -(RULER_WIDTH + BOTTOM_LINE_WIDTH)
        self.ruler_w = elements.ruler.Ruler(parent=self.parent_container, orientation=elements.ruler.ORIENTATION_RIGHT, show_label=False, align=uiconst.BOTTOMLEFT, width=RULER_WIDTH, height=AREA_SIZE, top=-middle_nudge)
        self.drawing_area = self._get_drawing_area(middle_nudge)
        self.ruler_e = elements.ruler.Ruler(parent=self.parent_container, orientation=elements.ruler.ORIENTATION_LEFT, show_label=True, align=uiconst.BOTTOMLEFT, width=RULER_WIDTH, height=AREA_SIZE, top=-middle_nudge, left=AREA_SIZE + RULER_WIDTH)
        top_nudge = middle_nudge - AREA_SIZE
        self.ruler_n = elements.ruler.Ruler(parent=self.parent_container, orientation=elements.ruler.ORIENTATION_DOWN, show_label=True, align=uiconst.BOTTOMLEFT, width=AREA_SIZE, height=RULER_WIDTH, top=-top_nudge, left=RULER_WIDTH)
        self.corner_ne = elements.minor.Corner(parent=self.parent_container, orientation=elements.minor.Corner.ORIENTATION_SW, align=uiconst.BOTTOMLEFT, width=RULER_WIDTH, height=RULER_WIDTH, top=-top_nudge, left=AREA_SIZE + RULER_WIDTH)
        self.sample_image = None
        self.cursor = elements.cursor.SciFiCursorRadius(parent=self.drawing_area, idx=0)
        self.x_button = elements.xbutton.XButton(name='x_button', parent=self.drawing_area, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL, button_function=self._x_button_click_callback, mouse_enter_callback=self._x_button_mouse_enter_callback)
        self.x_button.Hide()
        self.polygons = {}
        self.segment_chain = elements.segmentchain.SegmentChain(parent=self.drawing_area)
        self.segment = elements.segment.Segment(parent=self.drawing_area, state=uiconst.UI_HIDDEN)
        self.second_segment = elements.segment.Segment(parent=self.drawing_area, state=uiconst.UI_HIDDEN)
        self.golden_polygons = []
        self.on_polygon_enter_signal = signals.Signal(signalName='on_polygon_enter_signal')
        self.on_vertex_enter_signal = signals.Signal(signalName='on_vertex_enter_signal')
        self.on_x_button_enter_signal = signals.Signal(signalName='on_x_button_enter_signal')
        self.on_drawing_area_enter_signal = signals.Signal(signalName='on_drawing_area_enter_signal')
        self.on_x_button_click_signal = signals.Signal(signalName='on_x_button_click_signal')

    def _get_drawing_area(self, middle_nudge):
        return elements.area.DrawingArea(parent=self.parent_container, mouse_enter_callback=self._drawing_area_enter_callback, align=uiconst.BOTTOMLEFT, width=AREA_SIZE, height=AREA_SIZE, top=-middle_nudge, left=RULER_WIDTH)

    def set_size(self, new_size):
        self.bottom_line.width = new_size + RULER_WIDTH * 2
        self.ruler_s.width = new_size
        self.ruler_s.ruler_length = new_size
        self.ruler_w.height = new_size
        self.ruler_w.ruler_length = new_size
        self.drawing_area.height = new_size
        self.drawing_area.width = new_size
        if self.drawing_area.background_sprite:
            self.drawing_area.background_sprite.height = new_size
            self.drawing_area.background_sprite.width = new_size
        self.ruler_e.height = new_size
        self.ruler_e.ruler_length = new_size
        self.ruler_e.left = new_size + RULER_WIDTH
        self.ruler_n.width = new_size
        self.ruler_n.ruler_length = new_size
        self.ruler_n.top = RULER_WIDTH + BOTTOM_LINE_WIDTH + new_size
        self.corner_ne.top = RULER_WIDTH + BOTTOM_LINE_WIDTH + new_size
        self.corner_ne.left = new_size + RULER_WIDTH

    @property
    def drawing_area_pos(self):
        if self.drawing_area:
            return self.drawing_area.GetAbsolutePosition()
        else:
            return (-1, -1)

    @property
    def drawing_area_size(self):
        return (self.drawing_area.width, self.drawing_area.height)

    def update_polygons(self):
        any_selected = False
        old_polys = set(self.polygons.keys())
        for p in self.controller.polygons.itervalues():
            if p.uuid in self.polygons:
                old_polys.remove(p.uuid)
                self._sync_polygons(p)
                any_selected |= p.is_selected
            else:
                self.polygons[p.uuid] = self._make_new_polygon(p)

        if not any_selected:
            self._hide_x_button()
        if old_polys:
            self._hide_x_button()
            for key in old_polys:
                self.polygons[key].Close()
                del self.polygons[key]

        self.segment_chain.SetParent(self.drawing_area, 0)
        self.segment.SetParent(self.drawing_area, 0)
        self.second_segment.SetParent(self.drawing_area, 0)
        self.cursor.SetParent(self.drawing_area, 0)

    def _sync_polygons(self, tracked_polygon):
        poly = self.polygons[tracked_polygon.uuid]
        if not poly:
            raise ValueError('polygon ui element not found :(')
        if tracked_polygon.is_moving:
            poly.state = uiconst.UI_DISABLED
            self._hide_x_button()
        elif tracked_polygon.is_adjusting:
            poly.set_adjust_mode()
            self._hide_x_button()
        else:
            poly._points = tracked_polygon.as_tuple_list
            poly.set_translation(0, 0)
            if poly.adjust_mode:
                poly.unset_adjust_mode()
            poly.state = uiconst.UI_PICKCHILDREN
            if tracked_polygon.is_selected:
                self._activate_x_button(poly, tracked_polygon)
        poly.update_style(self._get_polygon_style(tracked_polygon), force=True)

    def _hide_x_button(self):
        self.x_button.SetParent(self.drawing_area)
        self.x_button.Hide()

    def _activate_x_button(self, polygon, tracked_polygon):
        self.x_button.polygon_uuid = tracked_polygon.uuid
        self.x_button.SetParent(polygon, idx=0)
        self.x_button.Show()

    def _polygon_mouse_enter_callback(self, polygon_uuid, is_exit = False):
        self.on_polygon_enter_signal(polygon_uuid=polygon_uuid, is_exit=is_exit)

    def _vertex_mouse_enter_callback(self, polygon_uuid, vertex_index, is_exit = False):
        self.on_vertex_enter_signal(polygon_uuid=polygon_uuid, vertex_index=vertex_index, is_exit=is_exit)

    def _drawing_area_enter_callback(self, is_exit = False):
        self.on_drawing_area_enter_signal(is_exit=is_exit)

    def _x_button_mouse_enter_callback(self, polygon_uuid, is_exit = False):
        self.on_x_button_enter_signal(polygon_uuid=polygon_uuid, is_exit=is_exit)

    def _x_button_click_callback(self, polygon_uuid):
        self.on_x_button_click_signal(polygon_uuid=polygon_uuid)

    def _make_new_polygon(self, tracked_polygon):
        return elements.polygon.Polygon(polygon_uuid=tracked_polygon.uuid, mouse_enter_callback=self._polygon_mouse_enter_callback, vertex_enter_callback=self._vertex_mouse_enter_callback, parent=self.drawing_area, points=tracked_polygon.as_tuple_list, polygon_style=self._get_polygon_style(tracked_polygon))

    def _get_polygon_style(self, tracked_polygon):
        if tracked_polygon.is_invalid:
            if tracked_polygon.is_selected:
                return elements.polygon.POLYGON_STYLE_INVALID_ACTIVE
            else:
                return elements.polygon.POLYGON_STYLE_INVALID
        if tracked_polygon.is_moving:
            return elements.polygon.POLYGON_STYLE_MOVING
        if tracked_polygon.is_selected:
            return elements.polygon.POLYGON_STYLE_ACTIVE
        if tracked_polygon.is_targeted:
            return elements.polygon.POLYGON_STYLE_HOVER
        return elements.polygon.POLYGON_STYLE_DEFAULT

    def update_segment_chain(self):
        if self.controller.state == self.controller.STATES.DRAWING:
            self.segment_chain.points = self.controller.drawing.segment_chain.as_tuple_list
            self.segment_chain.Show()
        elif self.controller.state != self.controller.STATES.MOVING_VERTEX:
            self.segment_chain.Hide()

    def update_cursor_state(self):
        if self.controller.cursor.target == self.controller.cursor.TARGETS.OFF_CANVAS:
            self.ruler_n.Hide()
            self.ruler_s.Hide()
            self.ruler_e.Hide()
            self.ruler_w.Hide()
            self.cursor.Hide()
        else:
            self.ruler_n.Show()
            self.ruler_s.Show()
            self.ruler_e.Show()
            self.ruler_w.Show()
            self.cursor.Show()
        if self.controller.cursor.is_invalid:
            if self.controller.state == self.controller.STATES.DRAWING:
                self.segment.set_style_invalid()
            self.cursor.set_style_invalid()
        else:
            if self.controller.cursor.is_snapping:
                self.cursor.set_style_snapping()
            else:
                self.cursor.set_style_default()
            if self.controller.state == self.controller.STATES.DRAWING:
                self.segment.set_style_default()

    def update_feedback(self):
        log.warning('update_feedback')

    def update_cursor_segment(self):
        seg = self.controller.visual_cursor_segment
        if seg:
            self.segment.start = seg.start.as_tuple
            self.segment.end = seg.end.as_tuple
            self.segment.Show()
        elif self.controller.state != self.controller.STATES.MOVING_VERTEX:
            self.segment.Hide()

    def update_cursor_and_friends(self):
        if self.controller.cursor.target != self.controller.cursor.TARGETS.OFF_CANVAS:
            self.ruler_n.update(self.controller.cursor.pos.right)
            self.ruler_s.update(self.controller.cursor.pos.right)
            self.ruler_e.update(self.controller.cursor.pos.up)
            self.ruler_w.update(self.controller.cursor.pos.up)
            self.cursor.update(self.controller.cursor.visual_pos)

    def update_polygon_moving(self):
        if self.controller.mover.state == self.controller.mover.STATES.MOVING:
            mp = self.polygons[self.controller.mover.target_polygon.uuid]
            mp.set_translation(*self.controller.mover.translation.as_tuple)
            mp.update_style(self._get_polygon_style(self.controller.mover.target_polygon))
            self._hide_x_button()
        elif self.controller.mover.state == self.controller.mover.STATES.READY:
            self.update_polygons()

    def update_golden(self):
        if self.golden_polygons:
            for gp in self.golden_polygons:
                gp.Close()

        self.golden_polygons = []
        if self.controller.golden_solution.polygons:
            for poly in self.controller.golden_solution.polygons:
                self.golden_polygons.append(self._make_golden_polygon(poly))

    def _make_golden_polygon(self, polymodel):
        log.warning('_make_golden_polygon')
        return elements.polygon.Polygon(parent=self.drawing_area, points=polymodel.as_tuple_list, polygon_style=elements.polygon.POLYGON_STYLE_GOLD, idx=-1)

    def update_vertex_moving(self):
        log.warning('update_vertex_moving...')
        if self.controller.adjuster.state == self.controller.adjuster.STATES.MOVING:
            self.segment_chain.points = self.controller.adjuster.static_segment_chain.as_tuple_list
            self.segment.start = self.controller.adjuster.left_segment.start.as_tuple
            self.segment.end = self.controller.adjuster.left_segment.end.as_tuple
            self.second_segment.start = self.controller.adjuster.right_segment.start.as_tuple
            self.second_segment.end = self.controller.adjuster.right_segment.end.as_tuple
            self.segment.Show()
            self.second_segment.Show()
            self.segment_chain.Show()
            self._hide_x_button()
            if self.controller.adjuster.is_overlapping:
                self.segment.set_style_invalid()
                self.second_segment.set_style_invalid()
            else:
                self.segment.set_style_default()
                self.second_segment.set_style_default()
        elif self.controller.adjuster.state == self.controller.adjuster.STATES.READY:
            self.second_segment.Hide()
            if self.controller.state != self.controller.STATES.DRAWING:
                self.segment.Hide()
                self.segment_chain.Hide()
