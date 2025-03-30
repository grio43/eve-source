#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\adapter.py
import signals
from carbonui.primitives import container
from projectdiscovery.client.projects.covid.ui.drawing import drawinggizmo
from projectdiscovery.client.projects.covid.ui.drawing import models
from projectdiscovery.client.projects.covid.ui.drawing import renderer
import logging
log = logging.getLogger('projectdiscovery.covid.adapter')

class DrawingToolAdapter(container.Container):

    def __init__(self, max_polygons, **kw):
        super(DrawingToolAdapter, self).__init__(**kw)
        self.is_enabled = True
        self.max_polygons = max_polygons
        self.gizmo = drawinggizmo.DrawingGizmo(parent_container=self)
        self.on_polygon_added = self.gizmo.controller.on_polygon_added
        self.on_polygon_deleted = self.gizmo.controller.on_polygon_deleted
        self.on_polygons_changed = self.gizmo.controller.on_polygons_changed
        self.on_wip_polygon_cleared = self.gizmo.controller.on_wip_polygon_cleared
        self.on_polygon_started = self.gizmo.controller.on_polygon_started
        self.on_polygon_selected = self.gizmo.controller.on_polygon_selected
        self.on_polygon_deselected = self.gizmo.controller.on_polygon_deselected
        self.on_point_added = self.gizmo.controller.on_point_added

    def ApplyAttributes(self, attributes):
        super(DrawingToolAdapter, self).ApplyAttributes(attributes)
        self.is_enabled = True

    def SetSize(self, width, height):
        log.warning('DrawingToolAdapter:SetSize(width=%r, height=%r)', width, height)
        super(DrawingToolAdapter, self).SetSize(width, height)
        self.gizmo.controller.resize(width - renderer.RULER_WIDTH * 2)
        self.gizmo.renderer.set_size(width - renderer.RULER_WIDTH * 2)

    def Enable(self, *args):
        log.warning('DrawingToolAdapter:Enable()')
        self.is_enabled = True
        self.gizmo.controller.enable()

    def Disable(self, *args):
        log.warning('DrawingToolAdapter:Disable(width=%r, height=%r)')
        self.is_enabled = False
        self.gizmo.controller.disable()

    def enable_markers(self):
        pass

    def disable_markers(self):
        pass

    def validate(self):
        if not self.gizmo.controller.has_minimum_required:
            return False
        return True

    def get_polygons(self):
        buf = []
        for uuid in self.gizmo.controller.polygon_order:
            buf.append({'vertices': [ self._scale_down(v) for v in self.gizmo.controller.polygons[uuid].verticies ]})

        return buf

    def _scale_down(self, coord):
        return [float(coord.right) / self.gizmo.controller.area_boundary.size.right, float(coord.up) / self.gizmo.controller.area_boundary.size.up]

    def get_time_spent_per_polygon(self):
        buf = []
        for uuid in self.gizmo.controller.polygon_order:
            buf.append(int(self.gizmo.controller.polygons[uuid].drawing_duration.total_seconds() * 1000))

        return buf

    def toggle_polygon_selection(self, index):
        uuid = self.gizmo.controller.polygon_order[index]
        if self.gizmo.controller.selected_polygon_uuid == uuid:
            self.gizmo.controller.clear_selection()
        else:
            self.gizmo.controller.select_polygon(uuid)

    def inject_click(self, x, y):
        log.warning('DrawingToolAdapter:inject_click(x=%r, y=%r)', x, y)
        self.gizmo.controller.enable()
        self.gizmo.controller.set_cursor_pos((int(x), int(self.gizmo.controller.area_boundary.size.y - y)))
        self.gizmo.controller.set_cursor_target()
        self.gizmo.controller.action_execute()
        self.gizmo.controller.disable()

    def inject_polygon(self, points, send_to_back = None, show_vertices = None, show_fill = None, perimeter_width = None, perimeter_color = None, fill_color = None):
        log.warning('DrawingToolAdapter:inject_polygon(points=%r)', points)
        self.gizmo.controller.golden_solution.add_polygon([ (v[0] * self.gizmo.controller.area_boundary.size.right, v[1] * self.gizmo.controller.area_boundary.size.up) for v in points ])
