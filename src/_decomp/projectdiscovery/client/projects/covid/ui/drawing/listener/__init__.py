#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\listener\__init__.py
import mathext
from carbonui.uicore import uicore
from carbonui import uiconst
import logging
log = logging.getLogger('projectdiscovery.covid.listener')

class DrawingEventListener(object):
    _DEBUG_MARKER = 65

    def __init__(self, controller, renderer, passive = False):
        self.controller = controller
        self.renderer = renderer
        self._mouse_move_cookie = None
        self._mouse_down_cookie = None
        self._mouse_up_cookie = None
        self._key_up_cookie = None
        if not passive:
            self.register_event_handlers()

    def register_event_handlers(self):
        if self._mouse_move_cookie is None:
            self._mouse_move_cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.on_mouse_move)
        if self._mouse_down_cookie is None:
            self._mouse_down_cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.on_mouse_down)
        if self._mouse_up_cookie is None:
            self._mouse_up_cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.on_mouse_up)
        if self._key_up_cookie is None:
            self._key_up_cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.on_key_up)
        self.controller.cursor.updater.register_update_callback(self.renderer.update_cursor_state)
        self.controller.feedback.updater.register_update_callback(self.renderer.update_feedback)
        self.controller.updater_segment_chain.register_update_callback(self.renderer.update_segment_chain)
        self.controller.updater_cursor_segment.register_update_callback(self.renderer.update_cursor_segment)
        self.controller.updater_polygons.register_update_callback(self.renderer.update_polygons)
        self.controller.mover.updater.register_update_callback(self.renderer.update_polygon_moving)
        self.controller.adjuster.updater.register_update_callback(self.renderer.update_vertex_moving)
        self.controller.golden_solution.updater.register_update_callback(self.renderer.update_golden)

    def unregister_event_handlers(self):
        if self._mouse_move_cookie:
            uicore.event.UnregisterForTriuiEvents(self._mouse_move_cookie)
            self._mouse_move_cookie = None
        if self._mouse_down_cookie:
            uicore.event.UnregisterForTriuiEvents(self._mouse_down_cookie)
            self._mouse_down_cookie = None
        if self._mouse_up_cookie:
            uicore.event.UnregisterForTriuiEvents(self._mouse_up_cookie)
            self._mouse_up_cookie = None
        if self._key_up_cookie:
            uicore.event.UnregisterForTriuiEvents(self._key_up_cookie)
            self._key_up_cookie = None
        self.controller.cursor.updater.clear()
        self.controller.feedback.updater.clear()
        self.controller.updater_segment_chain.clear()
        self.controller.updater_cursor_segment.clear()
        self.controller.updater_polygons.clear()
        self.controller.mover.updater.clear()
        self.controller.adjuster.updater.clear()
        self.controller.golden_solution.updater.clear()

    def on_mouse_down(self, element, event_id, params):
        log.debug('on_mouse_down...%r', params)
        btn = params[0]
        if btn == uiconst.MOUSELEFT:
            self.controller.action_begin()
        return True

    def on_mouse_up(self, element, event_id, params):
        log.debug('on_mouse_up...%r', params)
        btn = params[0]
        if btn == uiconst.MOUSELEFT:
            self.controller.action_execute()
        elif btn in (uiconst.MOUSERIGHT, uiconst.MOUSEXBUTTON1):
            self.controller.action_back()
        return True

    def on_mouse_move(self, element, event_id, params):
        self.controller.set_cursor_pos(self._mouse_to_cursor_coords())
        self.renderer.update_cursor_and_friends()
        return True

    def on_key_up(self, element, event_id, params):
        key = params[0]
        if key == uiconst.VK_BACK:
            self.controller.action_back()
        elif key == uiconst.VK_DELETE:
            self.controller.action_delete()
        elif key == uiconst.VK_ESCAPE:
            self.controller.action_cancel()
        elif key == uiconst.VK_D:
            self.controller.logdump_states()
        elif key == uiconst.VK_M:
            c = chr(DrawingEventListener._DEBUG_MARKER)
            log.warning('=====[ LOGMARK: %s ]=====' % (c * 40))
            DrawingEventListener._DEBUG_MARKER += 1
        return True

    def _mouse_to_cursor_coords(self):
        dapos_x, dapos_y = self.renderer.drawing_area_pos
        dasize_x, dasize_y = self.renderer.drawing_area_size
        if dapos_x <= uicore.uilib.x <= dapos_x + dasize_x and dapos_y <= uicore.uilib.y <= dapos_y + dasize_y:
            if self.controller.cursor.target == self.controller.cursor.TARGETS.OFF_CANVAS:
                self.controller.set_cursor_target()
        elif self.controller.cursor.target != self.controller.cursor.TARGETS.OFF_CANVAS:
            self.controller.set_cursor_off_canvas()
        return (mathext.clamp(uicore.uilib.x - dapos_x - 1, 0, dasize_x - 1), dasize_y - mathext.clamp(uicore.uilib.y - dapos_y, 1, dasize_y))

    def on_polygon_mouse_enter(self, polygon_uuid, is_exit = False):
        log.debug('on_polygon_mouse_enter(polygon_uuid=%r, is_exit=%r)', polygon_uuid, is_exit)
        if is_exit:
            self.controller.set_cursor_target()
        else:
            self.controller.set_cursor_target(polygon_uuid)
        log.debug('on_polygon_mouse_enter=>%r', self.controller.cursor)

    def on_vertex_mouse_enter(self, polygon_uuid, vertex_index, is_exit = False):
        log.debug('on_vertex_mouse_enter(polygon_uuid=%r, vertex_index=%r, is_exit=%r)', polygon_uuid, vertex_index, is_exit)
        if is_exit:
            self.controller.set_cursor_target()
        else:
            self.controller.set_cursor_target(polygon_uuid, vertex_index)
        log.debug('on_vertex_mouse_enter=>%r', self.controller.cursor)

    def on_drawing_area_mouse_enter(self, is_exit = False):
        log.debug('on_drawing_area_mouse_enter(is_exit=%r)', is_exit)

    def on_x_button_mouse_enter(self, polygon_uuid, is_exit = False):
        log.debug('on_x_button_mouse_enter(polygon_uuid=%r, is_exit=%r)', polygon_uuid, is_exit)
        if is_exit:
            self.controller.set_cursor_target()
        else:
            self.controller.set_cursor_target(polygon_uuid, x_button=True)
        log.debug('on_x_button_mouse_enter=>%r', self.controller.cursor)

    def on_x_button_click(self, polygon_uuid):
        log.debug('on_x_button_click=>%r', polygon_uuid)
        self.controller.set_cursor_target(polygon_uuid)
        self.controller.action_delete()
