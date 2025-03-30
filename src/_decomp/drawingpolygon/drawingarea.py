#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\drawingpolygon\drawingarea.py
from drawingpolygon.cursors import CURSOR_SELECTOR_POSITION
from drawingpolygon.polygon import Polygon
from drawingpolygon.xbutton import XButton
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from signals import Signal
from uthread2 import StartTasklet

class DrawingArea(Container):
    default_max_polygons = 8

    def ApplyAttributes(self, attributes):
        super(DrawingArea, self).ApplyAttributes(attributes)
        self.max_polygons = attributes.get('max_polygons', self.default_max_polygons)
        self.buffer_size = attributes.get('buffer_size')
        self.on_polygon_added = Signal(signalName='on_polygon_added')
        self.on_polygon_deleted = Signal(signalName='on_polygon_deleted')
        self.on_polygons_changed = Signal(signalName='on_polygons_changed')
        self.on_wip_polygon_cleared = Signal(signalName='on_wip_polygon_cleared')
        self.on_polygon_started = Signal(signalName='on_polygon_started')
        self.on_polygon_selected = Signal(signalName='on_polygon_selected')
        self.on_polygon_deselected = Signal(signalName='on_polygon_deselected')
        self.on_point_added = Signal(signalName='on_point_added')
        self.buffer = Container(name='buffer_container', parent=self.parent, align=uiconst.CENTER, idx=0)
        self.content = DrawingContent(name='content_container', parent=self, align=uiconst.CENTER, state=uiconst.UI_NORMAL, drawing_area=self, buffer_area=self.buffer)
        self.x_button = None

    def SetSize(self, width, height):
        super(DrawingArea, self).SetSize(width, height)
        self.buffer.width = self.width + 2 * self.buffer_size
        self.buffer.height = self.height + 2 * self.buffer_size
        self.content.SetSize(width, height)

    def get_polygons(self):
        return [ polygon.get_data() for polygon in self.content.polygons ]

    def get_time_spent_per_polygon(self):
        return [ polygon.get_time_spent() for polygon in self.content.polygons ]

    def get_mouse_position(self):
        return self._constrain_to_area(uicore.uilib.x, uicore.uilib.y)

    def transform_coordinates_to_proportions(self, x, y):
        new_x, new_y = (0, 0)
        if self.width:
            new_x = float(x) / self.width
        if self.height:
            new_y = float(y) / self.height
        return [new_x, 1.0 - new_y]

    def transform_proportions_to_coordinates(self, x, y):
        return (x * self.width, y * self.height)

    def _constrain_to_area(self, x, y):
        min_x, min_y = (0, 0)
        max_x, max_y = self.width, self.height
        return (sorted([min_x, max_x, x - self.absoluteLeft])[1], sorted([min_y, max_y, y - self.absoluteTop])[1])

    def is_position_in_area(self, x, y):
        min_x, min_y = (0, 0)
        max_x, max_y = self.width, self.height
        return min_x <= x <= max_x and min_y <= y <= max_y

    def is_there_another_vertex_in_range(self, polygon, vertex):
        for other_vertex in polygon.vertices:
            if other_vertex.order != vertex.order:
                if vertex.is_within_range(other_vertex):
                    return True

        return False

    def add_x_button(self, button_function, x, y):
        self.remove_x_button()
        self.x_button = XButton(name='x_button', parent=self.buffer, align=uiconst.TOPLEFT, button_function=button_function)
        self.x_button.left = self.buffer_size + x + 5
        self.x_button.top = self.buffer_size + y - self.x_button.height - 5

    def remove_x_button(self):
        if self.x_button:
            self.x_button.Close()
            self.x_button = None

    def toggle_polygon_selection(self, index):
        self.content.toggle_polygon_selection(index)

    def inject_click(self, x, y):
        self.content.on_click(x, y)

    def change_perimeter_color(self, perimeter_color):
        self.content.change_perimeter_color(perimeter_color)

    def inject_polygon(self, vertices, send_to_back = None, show_vertices = None, show_fill = None, perimeter_width = None, perimeter_color = None, fill_color = None, fill_bg_color = None):
        self.content.inject_polygon(vertices, send_to_back, show_vertices, show_fill, perimeter_width, perimeter_color, fill_color, fill_bg_color)

    def Enable(self, *args):
        super(DrawingArea, self).Enable(*args)
        self.buffer.SetState(uiconst.UI_PICKCHILDREN)
        self.content.SetState(uiconst.UI_NORMAL)

    def Disable(self, *args):
        super(DrawingArea, self).Disable(*args)
        self.buffer.Disable(*args)
        self.content.Disable(*args)
        self.remove_x_button()

    def Close(self):
        self.buffer.Close()
        super(DrawingArea, self).Close()

    def on_number_of_polygons_changed(self, number_of_polygons):
        self.on_polygons_changed(number_of_polygons)


class CannotAddMorePolygons(Exception):
    pass


class DrawingContent(Container):
    MINIMUM_POINTS = 3

    def ApplyAttributes(self, attributes):
        super(DrawingContent, self).ApplyAttributes(attributes)
        self.drawing_area = attributes.get('drawing_area')
        self.buffer_area = attributes.get('buffer_area')
        self.on_number_of_polygons_changed = Signal(signalName='on_number_of_polygons_changed')
        self.on_number_of_polygons_changed.connect(self.drawing_area.on_number_of_polygons_changed)
        self.on_polygon_added = Signal(signalName='on_polygon_added')
        self.on_polygon_added.connect(self.drawing_area.on_polygon_added)
        self.on_polygon_deleted = Signal(signalName='on_polygon_deleted')
        self.on_polygon_deleted.connect(self.drawing_area.on_polygon_deleted)
        self.on_wip_polygon_cleared = Signal(signalName='on_wip_polygon_cleared')
        self.on_wip_polygon_cleared.connect(self.drawing_area.on_wip_polygon_cleared)
        self.on_polygon_started = Signal(signalName='on_polygon_started')
        self.on_polygon_started.connect(self.drawing_area.on_polygon_started)
        self.on_polygon_selected = Signal(signalName='on_polygon_selected')
        self.on_polygon_selected.connect(self.drawing_area.on_polygon_selected)
        self.on_polygon_deselected = Signal(signalName='on_polygon_deselected')
        self.on_polygon_deselected.connect(self.drawing_area.on_polygon_deselected)
        self.on_point_added = Signal(signalName='on_point_added')
        self.on_point_added.connect(self.drawing_area.on_point_added)
        self.cursor = CURSOR_SELECTOR_POSITION
        self.polygons = []
        self.active_polygon = None
        self.selected_polygon = None
        self._selection_update_thread = None
        self._on_internal_click_thread = None
        self._on_external_click_thread = None
        self.mouse_up_cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.on_general_click)
        self.mouse_move_cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.on_general_move)
        self.esc_cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.on_general_key_up)

    def Close(self):
        self._release_control()
        uicore.event.UnregisterForTriuiEvents(self.mouse_up_cookie)
        uicore.event.UnregisterForTriuiEvents(self.mouse_move_cookie)
        uicore.event.UnregisterForTriuiEvents(self.esc_cookie)
        super(DrawingContent, self).Close()

    def Disable(self, *args):
        super(DrawingContent, self).Disable(*args)
        self.clear()
        self.select_all_polygons()

    def SetSize(self, width, height):
        previous_width, previous_height = self.width, self.height
        super(DrawingContent, self).SetSize(width, height)
        if previous_width < 1 or previous_height < 1:
            return
        x_scale = float(self.width) / previous_width
        y_scale = float(self.height) / previous_height
        for polygon in self.polygons:
            polygon.scale(x_scale, y_scale)

        self.clear()

    def clear(self):
        self._clear_selection()
        self._clear_wip_polygon()
        self._set_active_polygon(None)

    def _add_new_polygon(self):
        if self.drawing_area.max_polygons and len(self.polygons) >= self.drawing_area.max_polygons:
            raise CannotAddMorePolygons()
        new_polygon = self._add_polygon()
        self._set_active_polygon(new_polygon)
        self.on_polygon_started()

    def change_perimeter_color(self, perimeter_color):
        for polygon in self.polygons:
            polygon.set_perimeter_color(perimeter_color)

    def inject_polygon(self, points, send_to_back = None, show_vertices = None, show_fill = None, perimeter_width = None, perimeter_color = None, fill_color = None, fill_bg_color = None):
        polygon = self._add_polygon(show_vertices, show_fill, perimeter_width, perimeter_color, fill_color, fill_bg_color)
        for x_proportion, y_proportion in points:
            x, y = self.drawing_area.transform_proportions_to_coordinates(x_proportion, y_proportion)
            polygon.add_point(x, y)

        polygon.autocomplete_polygon()
        if send_to_back:
            polygon.set_arrangement_order(-1)

    def select_all_polygons(self):
        for polygon in self.polygons:
            polygon.select()

    def invalidate_polygons(self, invalid_polygons):
        for polygon in self.polygons:
            is_valid = polygon.order not in invalid_polygons
            polygon.update_validation(is_valid)

    def _add_polygon(self, show_vertices = None, show_fill = None, perimeter_width = None, perimeter_color = None, fill_color = None, fill_bg_color = None):
        new_polygon = Polygon(parent=self, area=self.drawing_area, order=len(self.polygons), show_vertices=show_vertices, show_fill=show_fill, perimeter_width=perimeter_width, perimeter_color=perimeter_color, fill_color_selected=fill_color, fill_bg_color_selected=fill_bg_color)
        new_polygon.on_edit_started.connect(self._on_polygon_edit_started)
        new_polygon.on_deleted.connect(self._on_polygon_deleted)
        new_polygon.on_completed.connect(self._on_polygon_completed)
        new_polygon.on_wip_segment_added.connect(self._take_control)
        new_polygon.on_wip_segment_removed.connect(self._release_control)
        self.polygons.append(new_polygon)
        return new_polygon

    def _set_active_polygon(self, polygon):
        self.active_polygon = polygon
        if self.active_polygon and not self.active_polygon.is_complete:
            for polygon in self.polygons:
                if polygon == self.active_polygon:
                    polygon.enable()
                else:
                    polygon.disable()

        else:
            for polygon in self.polygons:
                polygon.enable()

    def _on_polygon_edit_started(self, polygon):
        if self._selection_update_thread:
            self._selection_update_thread.kill()
        self._selection_update_thread = StartTasklet(self._update_polygon_selection, polygon)

    def _on_polygon_completed(self, polygon):
        if self._selection_update_thread:
            self._selection_update_thread.kill()
        if self.active_polygon:
            self._deselect_polygon(self.active_polygon)
        self._set_active_polygon(None)
        self.on_polygon_added(polygon.order)
        self.on_number_of_polygons_changed(len(self.polygons))

    def _on_polygon_deleted(self, index):
        if index >= len(self.polygons):
            return
        polygon_to_delete = self.polygons[index]
        is_complete = polygon_to_delete.is_complete
        if self.active_polygon == polygon_to_delete:
            self._set_active_polygon(None)
        if self.selected_polygon == polygon_to_delete:
            self.selected_polygon = None
        del self.polygons[index]
        for order, polygon in enumerate(self.polygons):
            polygon.set_order(order)

        self._update_polygon_arrangement()
        self.on_number_of_polygons_changed(len(self.polygons))
        self.on_polygon_deleted(index, is_complete)

    def toggle_polygon_selection(self, index):
        if index >= len(self.polygons):
            return
        polygon = self.polygons[index]
        if self.selected_polygon == polygon:
            self._deselect_polygon(polygon)
            if self.active_polygon == polygon:
                self._set_active_polygon(None)
        else:
            self._clear_selection()
            self._select_polygon(polygon)
            self._set_active_polygon(polygon)

    def _select_polygon(self, polygon):
        polygon.select()
        self.selected_polygon = polygon
        self._update_polygon_arrangement()
        self.on_polygon_selected(polygon.order)

    def _deselect_polygon(self, polygon):
        polygon.deselect()
        self.selected_polygon = None
        self._update_polygon_arrangement()
        self.on_polygon_deselected(polygon.order)

    def _clear_selection(self):
        if self.selected_polygon:
            self._deselect_polygon(self.selected_polygon)

    def _update_polygon_arrangement(self):
        for polygon in reversed(self.polygons):
            if polygon == self.selected_polygon:
                polygon.set_arrangement_order(0)
            else:
                polygon.set_arrangement_order(-1)

    def _update_polygon_selection(self, polygon):
        try:
            if self.active_polygon == polygon:
                return
            if self.active_polygon and not self.active_polygon.destroyed:
                if not self.active_polygon.is_complete:
                    return
                self._deselect_polygon(self.active_polygon)
                self._set_active_polygon(None)
            if not polygon.destroyed:
                self._set_active_polygon(polygon)
                self._select_polygon(self.active_polygon)
        finally:
            self._selection_update_thread = None

    def _clear_wip_polygon(self):
        if self.active_polygon and not self.active_polygon.is_complete:
            self.active_polygon.Close()
            self._set_active_polygon(None)
            self.on_wip_polygon_cleared()

    def _take_control(self):
        uicore.registry.RequestControl(self)

    def _release_control(self):
        uicore.registry.ReleaseControl(self)

    def OnClick(self, *args):
        x, y = self.drawing_area.get_mouse_position()
        self.on_click(x, y)

    def on_click(self, x, y):
        if self._on_internal_click_thread:
            self._on_internal_click_thread.kill()
        self._on_internal_click_thread = StartTasklet(self._process_internal_left_click, x, y)

    def _is_left_click(self, vkey):
        if vkey == uiconst.MOUSELEFT:
            return True
        return False

    def on_general_click(self, obj, eventID, (vkey, flag)):
        x, y = uicore.uilib.x - self.absoluteLeft, uicore.uilib.y - self.absoluteTop
        is_left_click = self._is_left_click(vkey)
        if self.drawing_area.is_position_in_area(x, y):
            if is_left_click:
                return True
            self.on_internal_right_click()
        elif is_left_click:
            self.on_external_left_click()
        return True

    def on_internal_right_click(self):
        if self._on_internal_click_thread:
            self._on_internal_click_thread.kill()
        self._on_internal_click_thread = StartTasklet(self._process_internal_right_click)

    def on_external_left_click(self):
        if self._on_external_click_thread:
            self._on_external_click_thread.kill()
        self._on_external_click_thread = StartTasklet(self._process_external_left_click)

    def _process_internal_left_click(self, x, y):
        try:
            if self.active_polygon:
                if self.active_polygon.is_complete:
                    self._deselect_polygon(self.active_polygon)
                    self._add_new_polygon()
            else:
                self._add_new_polygon()
            if self.active_polygon and not self.active_polygon.is_complete:
                self.active_polygon.add_point(x, y)
                self.on_point_added()
        except CannotAddMorePolygons:
            return
        finally:
            self._on_internal_click_thread = None

    def _process_internal_right_click(self):
        try:
            self._clear_wip_polygon()
        finally:
            self._on_general_click_thread = None

    def _process_external_left_click(self):
        try:
            if self.active_polygon:
                if self.active_polygon.get_point_amount() >= self.MINIMUM_POINTS:
                    self.active_polygon.autocomplete_polygon()
                else:
                    self._clear_wip_polygon()
        finally:
            self._on_general_click_thread = None

    def on_general_move(self, *args):
        x, y = uicore.uilib.x - self.absoluteLeft, uicore.uilib.y - self.absoluteTop
        if not self.drawing_area.is_position_in_area(x, y):
            return True
        if self.active_polygon:
            self.active_polygon.move_cursor()
        return True

    def on_general_key_up(self, _window, _event_id, key_data, *args):
        key, _ = key_data
        if key == uiconst.VK_ESCAPE:
            self._clear_wip_polygon()
        return True
