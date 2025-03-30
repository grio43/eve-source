#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\drawinggizmo.py
from projectdiscovery.client.projects.covid.ui.drawing.controller import drawing
from projectdiscovery.client.projects.covid.ui.drawing import listener
from projectdiscovery.client.projects.covid.ui.drawing import renderer
from carbonui import const
from carbonui.primitives import container
from projectdiscovery.client.projects.covid.ui.drawing.renderer.elements import colors
import logging
log = logging.getLogger('projectdiscovery.covid.gizmo')

class TestBox(container.Container):
    default_height = 600
    default_width = 700
    default_top = 70
    default_left = 140
    default_state = const.UI_PICKCHILDREN
    default_align = const.BOTTOMLEFT
    default_bgColor = colors.BLACK.opaque(0.6).as_tuple


class DrawingGizmo(object):

    def __init__(self, parent_container, passive = False):
        self.controller = drawing.DrawingController()
        self.renderer = renderer.DrawingRenderer(controller=self.controller, parent_container=parent_container)
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
