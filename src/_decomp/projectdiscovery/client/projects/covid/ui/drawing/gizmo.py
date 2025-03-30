#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\gizmo.py
from projectdiscovery.client.projects.covid.ui.drawing.controller import drawing
from projectdiscovery.client.projects.covid.ui.drawing import listener
from projectdiscovery.client.projects.covid.ui.drawing import renderer
from carbonui import const
from carbonui.primitives.container import Container
from projectdiscovery.client.projects.covid.ui.drawing.renderer.elements import colors
from signals import Signal
import logging
log = logging.getLogger('projectdiscovery.covid.gizmo')

class TestBox(Container):
    default_height = 600
    default_width = 700
    default_top = 70
    default_left = 140
    default_state = const.UI_PICKCHILDREN
    default_align = const.BOTTOMLEFT
    default_bgColor = colors.BLACK.opaque(0.6).as_tuple


class DrawingGizmo(Container):
    default_passive = False

    def ApplyAttributes(self, attributes):
        super(DrawingGizmo, self).ApplyAttributes(attributes)
        self.is_enabled = True
        passive = attributes.get('passive', self.default_passive)
        self.on_polygon_started = Signal(signalName='on_polygon_started')
        self.on_polygon_added = Signal(signalName='on_polygon_added')
        self.on_polygon_selected = Signal(signalName='on_polygon_selected')
        self.on_polygon_deselected = Signal(signalName='on_polygon_deselected')
        self.on_polygon_deleted = Signal(signalName='on_polygon_deleted')
        self.on_polygons_changed = Signal(signalName='on_polygons_changed')
        self.on_point_added = Signal(signalName='on_point_added')
        self.on_wip_polygon_cleared = Signal(signalName='on_wip_polygon_cleared')
        self.controller = drawing.DrawingController()
        self.renderer = renderer.DrawingRenderer(controller=self.controller, parent_container=self.parent)
        self.listener = listener.DrawingEventListener(controller=self.controller, renderer=self.renderer, passive=passive)
        self.renderer.on_polygon_enter_signal.connect(self.listener.on_polygon_mouse_enter)
        self.renderer.on_vertex_enter_signal.connect(self.listener.on_vertex_mouse_enter)
        self.renderer.on_drawing_area_enter_signal.connect(self.listener.on_drawing_area_mouse_enter)
        self.renderer.on_x_button_enter_signal.connect(self.listener.on_x_button_mouse_enter)
        self.renderer.on_x_button_click_signal.connect(self.listener.on_x_button_click)
        if not passive:
            self.controller.enable()

    def destroy(self):
        self.listener.unregister_event_handlers()

    def Enable(self, *args):
        self.is_enabled = True
        super(DrawingGizmo, self).Enable()

    def Disable(self, *args):
        self.is_enabled = False
        super(DrawingGizmo, self).Disable()

    def enable_markers(self):
        pass

    def disable_markers(self):
        pass

    def toggle_polygon_selection(self, index):
        pass

    def get_polygons(self):
        return []

    def get_time_spent_per_polygon(self):
        return []

    def inject_polygon(self, points, send_to_back = None, show_vertices = None, show_fill = None, perimeter_width = None, perimeter_color = None, fill_color = None):
        pass

    def inject_click(self, x, y):
        pass
