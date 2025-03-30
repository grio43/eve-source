#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\panel.py
import abc
import datetime
import eveui
import gametime
import signals
import threadutils
from carbonui import uiconst
from carbonui.uicore import uicore
from eveui import Rect
from dynamicresources.client.ess.bracket.tracker import TransformTracker

class BracketPanel(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, transform, layer, camera = None, clipping_dead_zone = 0, collapse_at_camera_distance = None, name = None, on_focus = None, collapsed = False):
        self._transform = transform
        self._layer = layer
        self._camera = camera
        self._clipping_dead_zone = clipping_dead_zone
        self._collapse_at_camera_distance = collapse_at_camera_distance
        self._is_forced_expanded = False
        self._is_collapsed = collapsed
        self.is_locked = False
        self._is_closed = False
        self._focused = False
        self._tracker = TransformTracker(name=name, parent=layer, transform=transform, curve_set=uicore.uilib.bracketCurveSet, tracker_parent=uicore.layer.inflight)
        self._state_requests = {}
        self._next_state_request_token_id = 1
        self.on_focus = signals.Signal()
        if on_focus:
            self.on_focus.connect(on_focus)
        self._clipped_state_token = None
        self._zoom_state_token = None
        self._interaction_state_token = None
        self._focus_state_token = None
        self._was_clipped = None
        self._start_frame_update_loop()

    @property
    def is_closed(self):
        return self._is_closed

    @property
    def tracker(self):
        return self._tracker

    @property
    def transform(self):
        return self._transform

    @property
    def layer(self):
        return self._layer

    @property
    def clipping_bounds(self):
        return get_absolute_bounds(self._layer)

    @property
    def is_collapsed(self):
        return self._is_collapsed

    @property
    def is_expanded(self):
        return not self._is_collapsed

    @property
    def can_expand(self):
        return self._is_collapsed and self._focus_state_token is None and not self._was_clipped

    @property
    def focused(self):
        return self._focused

    @focused.setter
    def focused(self, focused):
        if focused != self._focused:
            self._focused = focused
            self.on_focus(focused)

    def close(self):
        self._tracker.close()
        self._is_closed = True

    def focus(self):
        self.focused = True

    def unfocus(self):
        self.focused = False

    @threadutils.threaded
    def _start_frame_update_loop(self):
        collapse_at_cursor_distance = 150.0
        cursor_distance_grace_period = datetime.timedelta(seconds=1.0)
        cursor_last_within_distance_at = None
        while not self._is_closed:
            clipping_bounds = self.clipping_bounds
            content_bounds = self.content_bounds
            if self._is_forced_expanded:
                cursor_distance = content_bounds.distance_from_point(*eveui.Mouse.position())
                if cursor_distance < collapse_at_cursor_distance:
                    cursor_last_within_distance_at = gametime.now()
                else:
                    if cursor_last_within_distance_at is None:
                        cursor_last_within_distance_at = gametime.now()
                    dt = gametime.now() - cursor_last_within_distance_at
                    if dt >= cursor_distance_grace_period:
                        self._is_forced_expanded = False
            if not self._is_forced_expanded and self._interaction_state_token is not None:
                self._interaction_state_token.clear()
                self._interaction_state_token = None
            if self._was_clipped is not None:
                dead_zone_sign = 1 if self._was_clipped else -1
                dead_zone_delta = dead_zone_sign * (self._clipping_dead_zone / 2.0)
                content_bounds = content_bounds.inflate(dead_zone_delta)
            if content_bounds.is_empty:
                is_enveloped = clipping_bounds.contains(*content_bounds.center)
            else:
                is_enveloped = clipping_bounds.envelops(content_bounds)
            if is_enveloped and (self._was_clipped is None or self._was_clipped):
                self._was_clipped = False
                if self._clipped_state_token is not None:
                    self._clipped_state_token.clear()
                    self._clipped_state_token = None
            elif not is_enveloped and not self._was_clipped:
                self._was_clipped = True
                if self._clipped_state_token is None:
                    self._clipped_state_token = self.request_collapse(Priority.clipped)
            if self._collapse_at_camera_distance is not None and self._camera.is_valid:
                camera_distance = self._camera.distance_from_transform(self._transform)
                out_of_range = camera_distance > self._collapse_at_camera_distance
                if out_of_range and self._zoom_state_token is None:
                    self._zoom_state_token = self.request_collapse(Priority.zoomed_out)
                elif not out_of_range and self._zoom_state_token is not None:
                    self._zoom_state_token.clear()
                    self._zoom_state_token = None
            should_expand, should_lock = self._should_be_expanded()
            if self._is_collapsed and should_expand:
                self.expand()
                self.is_locked = False
                self._is_collapsed = False
            elif not self._is_collapsed and not should_expand:
                self.collapse(lock=should_lock)
                self.is_locked |= should_lock
                self._is_collapsed = True
            elif self._is_collapsed and not should_expand and not self.is_locked and should_lock:
                self.collapse(lock=should_lock)
                self._is_collapsed = True
                self.is_locked = True
            elif self._is_collapsed and not should_expand and self.is_locked and not should_lock:
                self.collapse(lock=should_lock)
                self._is_collapsed = True
                self.is_locked = False
            eveui.wait_for_next_frame()

    def request_collapse(self, priority = 0, lock = False):
        return self._allocate_state_request(priority, expand=False, lock=lock)

    def request_expand(self, priority = 0):
        return self._allocate_state_request(priority, expand=True)

    def _allocate_state_request(self, priority, expand, lock = False):
        token_id = self._next_state_request_token_id
        self._next_state_request_token_id += 1
        self._state_requests[token_id] = StateRequest(priority, expand, lock)
        return StateRequestToken(token_id, on_clear=self._clear_state_request)

    def _clear_state_request(self, token_id):
        try:
            del self._state_requests[token_id]
        except KeyError:
            pass

    def _should_be_expanded(self):
        if not self._state_requests:
            return (True, False)
        highest_priority = 0
        expand = False
        lock = False
        for request in self._state_requests.values():
            lock |= request.lock
            if request.priority > highest_priority:
                highest_priority = request.priority
                expand = request.expand
            elif request.priority == highest_priority:
                expand |= request.expand

        return (expand, lock)

    def force_expand(self):
        if not self._is_forced_expanded and self._is_collapsed:
            self._is_forced_expanded = True
            self._interaction_state_token = self.request_expand(Priority.player)
            uicore.uilib.RegisterForTriuiEvents([uiconst.UI_MOUSEDOWN], self._on_global_mouse_down)

    def force_collapse(self):
        if self._focus_state_token is None:
            self._focus_state_token = self.request_collapse(Priority.player)

    def clear_force_collapse(self):
        if self._focus_state_token is not None:
            self._focus_state_token.clear()
            self._focus_state_token = None

    def _on_global_mouse_down(self, target, *args, **kwargs):
        if target is None:
            return True
        if not self._is_forced_expanded:
            return False
        click_captured = self.content_bounds.contains(*eveui.Mouse.position())
        if self._is_forced_expanded and not click_captured:
            self._is_forced_expanded = False
            return False
        return True

    @abc.abstractproperty
    def content_bounds(self):
        pass

    @abc.abstractmethod
    def expand(self):
        pass

    @abc.abstractmethod
    def collapse(self, lock = False):
        pass


class Priority(object):
    control_point = 5
    player = 4
    no_content = 3
    zoomed_out = 2
    clipped = 1


class StateRequest(object):

    def __init__(self, priority, expand, lock):
        self.priority = priority
        self.expand = expand
        self.lock = lock

    @property
    def collapse(self):
        return not self.expand


class StateRequestToken(object):

    def __init__(self, token_id, on_clear):
        self._token_id = token_id
        self._cleared = False
        self.on_clear = signals.Signal()
        if on_clear:
            self.on_clear.connect(on_clear)

    def clear(self):
        if not self._cleared:
            self._cleared = True
            self.on_clear(self._token_id)

    def __del__(self):
        self.clear()


def get_absolute_bounds(ui_object, allow_alignment = False):
    if ui_object.destroyed:
        return Rect.zero()
    if allow_alignment:
        left, top, width, height = ui_object.GetAbsolute()
    else:
        left, top = ui_object.GetCurrentAbsolutePosition()
        width, height = ui_object.GetCurrentAbsoluteSize()
    return Rect(left, top, width, height)


from dynamicresources.client.ess.bracket.debug import __reload_update__
