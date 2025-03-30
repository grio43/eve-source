#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\drawingpolygon\polygon.py
from drawingpolygon.components.fill import PolygonFill
from drawingpolygon.components.perimeter import PolygonPerimeter, PolygonSegment
from drawingpolygon.components.vertex import PolygonVertex
import drawingpolygon.cursors as cursors
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.primitives.container import Container
from gametime import GetTimeDiffInMs, GetWallclockTime
from signals.signal import Signal
import trinity
DRAG_UPDATE_TIMER_MSEC = 50
IS_RIGHT_CLICK_DELETE_ENABLED = False
VERTEX_CLOSED_TEXTURE_PATH = 'res:/UI/Texture/classes/DrawingTool/vertex.png'
VERTEX_OPEN_TEXTURE_PATH = 'res:/UI/Texture/classes/DrawingTool/vertex_open_ended.png'
VERTEX_DRAGGING_TEXTURE_PATH = 'res:/UI/Texture/classes/DrawingTool/vertex_moving.png'

def read(attributes, name, default):
    value = attributes.get(name, default)
    if value is not None:
        return value
    return default


class Polygon(Container):
    default_state = uiconst.UI_PICKCHILDREN
    default_align = uiconst.TOALL
    default_idx = 0
    default_max_vertices = 10
    default_perimeter_width = 2
    default_perimeter_width_factor = 2
    default_show_vertices = True
    default_show_fill = True
    default_fill_bg_color_selected = (0.0, 0.0, 0.0, 0.6)
    default_fill_bg_color_hovered = (0.0, 0.0, 0.0, 0.6)
    default_fill_bg_color_deselected = (0.0, 0.0, 0.0, 0.0)
    default_fill_color_selected = (0.2, 1.0, 1.0, 0.7)
    default_fill_color_hovered = (0.2, 1.0, 1.0, 0.4)
    default_fill_color_deselected = (0.0, 0.0, 0.0, 0.0)
    default_perimeter_color = (0.2, 1.0, 1.0, 1.0)
    default_perimeter_color_outer = (0.0, 0.0, 0.0, 1.0)
    FILL_COLOR_SELECTED_INVALID = (0.97, 0.09, 0.13, 0.7)
    FILL_COLOR_HOVERED_INVALID = (0.97, 0.09, 0.13, 0.5)
    FILL_COLOR_DESELECTED_INVALID = (0.0, 0.0, 0.0, 0.0)
    PERIMETER_COLOR_INVALID = (0.97, 0.09, 0.13, 1.0)
    NO_COLOR = (0.0, 0.0, 0.0, 0.0)

    def ApplyAttributes(self, attributes):
        self.drawing_area = attributes.get('area')
        self.max_vertices = read(attributes, 'max_vertices', self.default_max_vertices)
        self.perimeter_width = read(attributes, 'perimeter_width', self.default_perimeter_width)
        self.perimeter_width_factor = read(attributes, 'perimeter_width_factor', self.default_perimeter_width_factor)
        self.show_vertices = read(attributes, 'show_vertices', self.default_show_vertices)
        self.show_fill = read(attributes, 'show_fill', self.default_show_fill)
        self.fill_bg_color_selected = read(attributes, 'fill_bg_color_selected', self.default_fill_bg_color_selected)
        self.fill_bg_color_hovered = read(attributes, 'fill_bg_color_hovered', self.default_fill_bg_color_hovered)
        self.fill_bg_color_deselected = read(attributes, 'fill_bg_color_deselected', self.default_fill_bg_color_deselected)
        self.fill_color_selected = read(attributes, 'fill_color_selected', self.default_fill_color_selected)
        self.fill_color_hovered = read(attributes, 'fill_color_hovered', self.default_fill_color_hovered)
        self.fill_color_deselected = read(attributes, 'fill_color_deselected', self.default_fill_color_deselected)
        self.perimeter_color = read(attributes, 'perimeter_color', self.default_perimeter_color)
        self.perimeter_color_outer = read(attributes, 'perimeter_color_outer', self.default_perimeter_color_outer)
        self.set_order(order=attributes.get('order'))
        self.vertices = []
        self.active_vertex = None
        self.is_complete = False
        self.is_selected = True
        self.is_valid = True
        self.is_moving = False
        self.is_vertex_moving = False
        self.is_hovered = False
        self.time_of_start = GetWallclockTime()
        self.time_of_last_edit = GetWallclockTime()
        self.vertex_drag_updates_thread = None
        self.drag_updates_thread = None
        self.drag_mouse_position = None
        self.original_vertex_mouse_position = None
        self.wip_segment = None
        self.on_edit_started = Signal(signalName='on_edit_started')
        self.on_deleted = Signal(signalName='on_deleted')
        self.on_completed = Signal(signalName='on_completed')
        self.on_wip_segment_added = Signal(signalName='on_wip_segment_added')
        self.on_wip_segment_removed = Signal(signalName='on_wip_segment_removed')
        super(Polygon, self).ApplyAttributes(attributes)
        self._draw_fill()
        self._draw_perimeter()

    def Close(self):
        self._set_active_vertex(None)
        self._remove_x_button()
        self.on_deleted(self.order)
        super(Polygon, self).Close()

    def get_data(self):
        return {'vertices': [ self.drawing_area.transform_coordinates_to_proportions(vertex.x, vertex.y) for vertex in self.vertices ]}

    def _get_top_right(self):
        x = max([ vertex.x for vertex in self.vertices ])
        y = min([ vertex.y for vertex in self.vertices ])
        return (x, y)

    def _get_right(self):
        x, y = (0, 0)
        for vertex in self.vertices:
            if vertex.x > x:
                x = vertex.x
                y = vertex.y

        return (x, y)

    def get_time_spent(self):
        return max(0, GetTimeDiffInMs(self.time_of_start, self.time_of_last_edit))

    def scale(self, x_scale, y_scale):
        self.Hide()
        self._remove_x_button()
        for vertex in self.vertices:
            vertex.update_position(vertex.x * x_scale, vertex.y * y_scale)

        self._redraw_polygon()
        self._add_x_button()
        self.Show()

    def set_order(self, order):
        self.order = order
        self.name = 'Polygon%d' % order

    def set_arrangement_order(self, idx):
        self.SetOrder(idx)

    def set_cursor(self, cursor):
        self.fill.set_cursor(cursor)
        self.perimeter.set_cursor(cursor)

    def reset_cursor(self):
        self.fill.reset_cursor()
        self.perimeter.reset_cursor()

    def set_perimeter_color(self, perimeter_color):
        self.perimeter_color = perimeter_color
        self.perimeter_inner.Flush()
        self.perimeter_inner.SetRGBA(*perimeter_color)
        for vertex in self.vertices:
            self.perimeter_inner.add_vertex(vertex.x, vertex.y)

        if self.is_complete:
            self.perimeter_inner.isLoop = True

    def select(self):
        self.is_selected = True
        self._redraw_polygon()
        if self.is_complete:
            self.set_cursor(cursors.CURSOR_SELECTOR_TARGET)
        self._add_x_button()

    def deselect(self):
        self.is_selected = False
        self._remove_x_button()
        self._redraw_polygon()
        self.reset_cursor()

    def on_hover(self):
        self.is_hovered = True
        self._redraw_polygon()

    def on_dehover(self):
        self.is_hovered = False
        self._redraw_polygon()

    def enable(self):
        for vertex in self.vertices:
            vertex.Enable()

        self.perimeter.Enable()
        self.fill.Enable()

    def disable(self):
        for vertex in self.vertices:
            vertex.Disable()

        self.perimeter.Disable()
        self.fill.Disable()

    def update_validation(self, is_valid):
        if self.is_valid == is_valid:
            return
        self.is_valid = is_valid or not self.is_complete
        self._redraw_polygon()

    def add_point(self, x, y):
        if self.is_complete:
            return
        self._add_segment(x, y)
        self._add_vertex(x, y)
        if self.max_vertices and len(self.vertices) >= self.max_vertices:
            self.autocomplete_polygon()

    def remove_point(self, index):
        self._remove_segment(index)
        self._remove_vertex(index)

    def get_point_amount(self):
        return len(self.vertices)

    def _draw_perimeter(self):
        self.perimeter = PolygonPerimeter(name='Perimeter', parent=self, polygon=self, color=self.perimeter_color_outer, lineWidth=self.perimeter_width * self.perimeter_width_factor)
        self.perimeter.on_left_clicked.connect(self.on_left_clicked)
        if IS_RIGHT_CLICK_DELETE_ENABLED:
            self.perimeter.on_right_clicked.connect(self.on_right_clicked)
        self.perimeter.on_drag_started.connect(self.on_drag_started)
        self.perimeter.on_drag_ended.connect(self.on_drag_ended)
        self.perimeter.on_hover_started.connect(self.on_hover)
        self.perimeter.on_hover_ended.connect(self.on_dehover)
        self.perimeter_inner = PolygonPerimeter(name='PerimeterInner', parent=self, polygon=self, color=self._get_perimeter_color(), lineWidth=self.perimeter_width, state=uiconst.UI_DISABLED)

    def _draw_fill(self):
        fill_color = self._get_fill_color()
        fill_bg_color = self._get_fill_bg_color()
        self.fill_bg = PolygonFill(name='FillBg', parent=self, polygon=self, color=fill_bg_color, state=uiconst.UI_DISABLED)
        self.fill = PolygonFill(name='Fill', parent=self, polygon=self, color=fill_color, blendMode=trinity.TR2_SBM_ADD)
        self.fill.on_left_clicked.connect(self.on_left_clicked)
        if IS_RIGHT_CLICK_DELETE_ENABLED:
            self.fill.on_right_clicked.connect(self.on_right_clicked)
        self.fill.on_drag_started.connect(self.on_drag_started)
        self.fill.on_drag_ended.connect(self.on_drag_ended)
        self.fill.on_hover_started.connect(self.on_hover)
        self.fill.on_hover_ended.connect(self.on_dehover)

    def _get_invalid_fill_color(self):
        if self.is_selected:
            return self.FILL_COLOR_SELECTED_INVALID
        if self.is_hovered:
            return self.FILL_COLOR_HOVERED_INVALID
        return self.FILL_COLOR_DESELECTED_INVALID

    def _get_fill_bg_color(self):
        if not self.show_fill or not self.is_valid:
            return self.NO_COLOR
        if self.is_selected:
            return self.fill_bg_color_selected
        if self.is_hovered:
            return self.fill_bg_color_hovered
        return self.fill_bg_color_deselected

    def _get_fill_color(self):
        if not self.show_fill:
            return self.NO_COLOR
        if not self.is_valid:
            return self._get_invalid_fill_color()
        if self.is_selected:
            return self.fill_color_selected
        if self.is_hovered:
            return self.fill_color_hovered
        return self.fill_color_deselected

    def _get_perimeter_color(self):
        if self.is_valid:
            return self.perimeter_color
        else:
            return self.PERIMETER_COLOR_INVALID

    def _redraw_polygon(self):
        self.perimeter.Flush()
        self.fill.Flush()
        self.fill_bg.Flush()
        self.perimeter_inner.Flush()
        fill_color = self._get_fill_color()
        self.fill.SetRGBA(*fill_color)
        fill_bg_color = self._get_fill_bg_color()
        self.fill_bg.SetRGBA(*fill_bg_color)
        perimeter_color = self._get_perimeter_color()
        self.perimeter_inner.SetRGBA(*perimeter_color)
        for vertex in self.vertices:
            self._add_segment(vertex.x, vertex.y)

        if self.is_complete:
            self._complete_polygon()
        elif self.vertices:
            self._set_active_vertex(self.vertices[-1])

    def _redraw_vertices(self):
        if not self.vertices:
            return
        if self.is_complete:
            for vertex in self.vertices:
                vertex.set_base_texture(VERTEX_CLOSED_TEXTURE_PATH)

        else:
            for vertex in self.vertices[:-1]:
                vertex.set_base_texture(VERTEX_CLOSED_TEXTURE_PATH)

            last_vertex = self.vertices[-1]
            last_vertex.set_base_texture(VERTEX_OPEN_TEXTURE_PATH)

    def _add_vertex(self, x, y):
        vertex_order = len(self.vertices)
        vertex = PolygonVertex(name='Vertex%d' % vertex_order, parent=self, get_mouse_position=self.drawing_area.get_mouse_position, polygon=self, order=vertex_order, x=x, y=y, texturePath=VERTEX_OPEN_TEXTURE_PATH, draggingTexturePath=VERTEX_DRAGGING_TEXTURE_PATH, opacity=1.0 if self.show_vertices else 0.0)
        vertex.on_left_clicked.connect(self.on_vertex_left_clicked)
        if IS_RIGHT_CLICK_DELETE_ENABLED:
            vertex.on_right_clicked.connect(self.on_vertex_right_clicked)
        vertex.on_drag_started.connect(self.on_vertex_drag_started)
        vertex.on_drag_ended.connect(self.on_vertex_drag_ended)
        self.vertices.append(vertex)
        self._set_active_vertex(vertex)
        self._redraw_vertices()

    def _remove_vertex(self, index):
        vertex_to_remove = self.vertices[index]
        was_active_vertex = self.active_vertex == vertex_to_remove
        vertex_to_remove.Close()
        del self.vertices[index]
        for order, vertex in enumerate(self.vertices):
            vertex.order = order

        if was_active_vertex:
            if len(self.vertices):
                self._set_active_vertex(self.vertices[-1])
            else:
                self._set_active_vertex(None)
        self._redraw_vertices()

    def _add_segment(self, x, y):
        self.perimeter.add_vertex(x, y)
        self.fill.add_vertex(x, y)
        self.fill_bg.add_vertex(x, y)
        self.perimeter_inner.add_vertex(x, y)

    def _remove_segment(self, index):
        self.perimeter.remove_vertex(index)
        self.fill.remove_vertex(index)
        self.fill_bg.remove_vertex(index)
        self.perimeter_inner.remove_vertex(index)

    def autocomplete_polygon(self):
        self._complete_polygon()
        self._set_active_vertex(None)
        self._remove_wip_segment()
        self.on_completed(self)

    def _complete_polygon(self):
        for vertex in self.vertices:
            vertex.set_base_cursor(cursors.CURSOR_RESIZER_COLLAPSED)
            vertex.set_dragging_cursor(cursors.CURSOR_RESIZER_EXPANDED)
            vertex.reset_cursor()

        self._redraw_vertices()
        self.perimeter.isLoop = True
        self.perimeter_inner.isLoop = True
        self.fill.complete()
        self.fill_bg.complete()
        self.is_complete = True

    def _set_active_vertex(self, vertex):
        if self.active_vertex == vertex:
            return
        self.active_vertex = vertex
        self._remove_wip_segment()
        if self.active_vertex:
            self._add_wip_segment()

    def _move(self, start_x, start_y, end_x, end_y):
        x_diff = end_x - start_x
        y_diff = end_y - start_y
        for vertex in self.vertices:
            vertex.update_position(x=vertex.x + x_diff, y=vertex.y + y_diff)

        self._redraw_polygon()

    def _delete(self):
        self._start_edit()
        self.Close()

    def _start_edit(self):
        self.on_edit_started(self)
        self._update_last_edit_time()

    def _update_last_edit_time(self):
        self.time_of_last_edit = GetWallclockTime()

    def on_left_clicked(self, *args):
        self._start_edit()

    def on_right_clicked(self, *args):
        self._delete()

    def on_drag_started(self, *args):
        self._start_edit()
        self._remove_wip_segment()
        self._start_drag_updates()

    def on_drag_ended(self, *args):
        self._end_drag_updates()
        self._add_wip_segment()

    def on_vertex_left_clicked(self, vertex):
        self._start_edit()
        if len(self.vertices) > 2 and vertex.order == 0:
            self.autocomplete_polygon()

    def on_vertex_right_clicked(self, vertex):
        self._start_edit()
        is_polygon_delete = len(self.vertices) <= 1
        self.remove_point(vertex.order)
        if is_polygon_delete:
            self.Close()

    def on_vertex_drag_started(self, vertex):
        self._start_edit()
        self._remove_wip_segment()
        self._start_vertex_drag_updates(vertex)

    def on_vertex_drag_ended(self, *args):
        self._end_vertex_drag_updates()
        self._add_wip_segment()

    def _start_drag_updates(self):
        self._end_drag_updates()
        self.is_moving = True
        self.drag_mouse_position = self.drawing_area.get_mouse_position()
        self.drag_updates_thread = AutoTimer(DRAG_UPDATE_TIMER_MSEC, self._update_while_dragging)
        self._remove_x_button()

    def _end_drag_updates(self):
        if self.drag_updates_thread:
            self.drag_updates_thread.KillTimer()
        self.is_moving = False
        self.drag_mouse_position = None
        self.drag_updates_thread = None
        self._update_last_edit_time()
        self._add_x_button()

    def _update_drag_mouse_position(self):
        start_x, start_y = self.drag_mouse_position
        end_x, end_y = self.drawing_area.get_mouse_position()
        x_diff = end_x - start_x
        y_diff = end_y - start_y
        for vertex in self.vertices:
            vertex_end_x = vertex.x + x_diff
            vertex_end_y = vertex.y + y_diff
            if not self.drawing_area.is_position_in_area(vertex_end_x, vertex_end_y):
                return False

        self.drag_mouse_position = (end_x, end_y)
        return True

    def _update_while_dragging(self):
        start_x, start_y = self.drag_mouse_position
        if not self._update_drag_mouse_position():
            return
        end_x, end_y = self.drag_mouse_position
        self._move(start_x, start_y, end_x, end_y)

    def _start_vertex_drag_updates(self, vertex):
        self._end_vertex_drag_updates()
        self.is_vertex_moving = True
        self.original_vertex_mouse_position = self.drawing_area.get_mouse_position()
        self.vertex_drag_updates_thread = AutoTimer(DRAG_UPDATE_TIMER_MSEC, self._update_vertex_while_dragging, vertex)
        self._remove_x_button()

    def _end_vertex_drag_updates(self):
        if self.vertex_drag_updates_thread:
            self.vertex_drag_updates_thread.KillTimer()
        self.is_vertex_moving = False
        self.original_vertex_mouse_position = None
        self.vertex_drag_updates_thread = None
        self._update_last_edit_time()
        self._add_x_button()

    def _update_vertex_while_dragging(self, vertex):
        x, y = self.drawing_area.get_mouse_position()
        vertex.update_position(x, y)
        should_abort_move = self.drawing_area.is_there_another_vertex_in_range(self, vertex)
        if should_abort_move:
            x, y = self.original_vertex_mouse_position
            vertex.update_position(x, y)
        self.perimeter.update_vertex(vertex.order, x, y)
        self.fill.update_vertex(vertex.order, x, y)
        self.fill_bg.update_vertex(vertex.order, x, y)
        self.perimeter_inner.update_vertex(vertex.order, x, y)
        if should_abort_move:
            self._end_vertex_drag_updates()

    def move_cursor(self):
        self._update_wip_segment()

    def _update_wip_segment(self):
        if self.wip_segment:
            x, y = self.drawing_area.get_mouse_position()
            self.wip_segment.update_vertex(1, x, y)

    def _add_wip_segment(self):
        if self.is_complete:
            return
        self._remove_wip_segment()
        self.wip_segment = PolygonSegment(name='wip_segment', parent=self.drawing_area, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, color=self.perimeter_color, lineWidth=self.perimeter_width)
        self.wip_segment.on_removed.connect(self.on_wip_segment_removed)
        self.on_wip_segment_added()
        last_vertex = self.vertices[-1]
        self.wip_segment.add_vertex(last_vertex.x, last_vertex.y)
        x, y = self.drawing_area.get_mouse_position()
        self.wip_segment.add_vertex(x, y)

    def _remove_wip_segment(self):
        if self.wip_segment:
            self.wip_segment.Close()
            self.wip_segment = None

    def _add_x_button(self):
        if not self.drawing_area.IsClickable() or not self.is_selected or not self.is_complete or self.is_moving or self.is_vertex_moving:
            return
        x, y = self._get_top_right()
        self.drawing_area.add_x_button(self._delete, x, y)

    def _remove_x_button(self):
        self.drawing_area.remove_x_button()
