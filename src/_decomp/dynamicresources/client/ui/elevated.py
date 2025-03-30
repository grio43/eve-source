#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ui\elevated.py
from __future__ import division
import math
import weakref
import eveui
import signals
import trinity
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore

class ElevatedControllerBase(object):

    def __init__(self):
        self.inertia = 2.0
        self.elevation_inertia_coefficient = 1.0
        self.focus_position = None
        self.focus_falloff = 100.0
        self.focus_elevation_multiplier = 5.0
        self._closed = False
        self.on_close = signals.Signal()
        self.on_update = signals.Signal()

    @property
    def closed(self):
        return self._closed

    def close(self):
        self._closed = True
        self.on_close()


class CurveSetBinding(object):

    def __init__(self, curve_set, obj):
        self._object_ref = weakref.ref(obj)
        self._curve_set_ref = weakref.ref(curve_set)
        curve_set.curves.append(obj)

    def __del__(self):
        obj = self._object_ref()
        curve_set = self._curve_set_ref()
        if obj is not None and curve_set is not None:
            curve_set.curves.fremove(obj)


class ElevatedController(ElevatedControllerBase):

    def __init__(self, transform):
        self._transform = transform
        super(ElevatedController, self).__init__()
        self.follow_mouse = False
        self._tracker = None
        self._tracker_binding = None
        self._init_tracker()

    @property
    def transform(self):
        return self._transform

    @transform.setter
    def transform(self, transform):
        self._transform = transform
        if self._tracker:
            self._tracker.trackTransform = self._transform

    @property
    def offset_target(self):
        if self.follow_mouse:
            return eveui.Mouse.position()
        else:
            l, t, w, h = uicore.layer.inflight.GetAbsolute()
            return (w / 2 - l, h / 2 - t)

    def _init_tracker(self):
        self._tracker = trinity.EveProjectBracket()
        self._tracker.parent = uicore.layer.inflight.GetRenderObject()
        self._tracker.trackTransform = self._transform

        def update_callback(tracker, object_ref = weakref.ref(self)):
            obj = object_ref()
            if obj is not None:
                obj._update()

        self._tracker.bracketUpdateCallback = update_callback
        self._tracker_binding = CurveSetBinding(uicore.uilib.bracketCurveSet, self._tracker)

    def _stop_tracker(self):
        self._tracker.bracketUpdateCallback = None
        self._tracker = None
        self._tracker_binding = None

    def close(self):
        if self._tracker is not None:
            self._stop_tracker()
        super(ElevatedController, self).close()

    def _update(self):
        bracket_x, bracket_y = self._tracker.projectedPosition
        bracket_x = eveui.reverse_scale_dpi(bracket_x)
        bracket_y = eveui.reverse_scale_dpi(bracket_y)
        self.on_update((bracket_x, bracket_y))


class ElevatedBase(Container):

    def __init__(self, controller, layer, anchor = (0.5, 0.5), elevation = 0.0, offset = (0, 0), parent = None, **kwargs):
        super(ElevatedBase, self).__init__(parent=layer, align=uiconst.TOPLEFT, **kwargs)
        self._controller = controller
        self._elevation = elevation
        self._anchor = anchor
        self._offset = offset
        self._parent = parent
        self._current_position = None
        self._controller.on_update.connect(self._on_update)
        self._controller.on_close.connect(self.Close)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, offset):
        self._offset = offset

    @property
    def controller(self):
        return self._controller

    def _on_update(self, position):
        old_x, old_y = position
        if self._current_position is not None:
            old_x, old_y = self._current_position
        x, y = position
        offset_x, offset_y = self._get_offset()
        x += offset_x
        y += offset_y
        inertia_multiplier = 1.0 + abs(self._elevation * self._controller.elevation_inertia_coefficient)
        divisor = 1.0 + self._controller.inertia * inertia_multiplier
        delta_x = (x - old_x) / divisor
        delta_y = (y - old_y) / divisor
        if abs(delta_x) <= 1.0:
            delta_x = 0.0
        if abs(delta_y) <= 1.0:
            delta_y = 0.0
        anchor_x, anchor_y = self._anchor
        width, height = self.GetCurrentAbsoluteSize()
        if width is None:
            width = 0
        if height is None:
            height = 0
        if self._elevation > 0:
            left = old_x - anchor_x * width + delta_x
            top = old_y - anchor_y * height + delta_y
        else:
            left = x + (x - old_x) - anchor_x * width - delta_x
            top = y + (y - old_y) - anchor_y * height - delta_y
        focus_position = self._controller.focus_position
        if focus_position is not None:
            focus_x = focus_position[0] - x
            focus_y = focus_position[1] - y
            focus_distance = math.sqrt(focus_x ** 2 + focus_y ** 2)
            if focus_distance < self._controller.focus_falloff:
                focus_distance *= self._controller.focus_falloff / focus_distance
            focus_x /= focus_distance
            focus_y /= focus_distance
            elevation_multiplier = self._elevation * self._controller.focus_elevation_multiplier
            left += focus_x * elevation_multiplier
            top += focus_y * elevation_multiplier
        self.left = left
        self.top = top
        self._current_position = (old_x + delta_x, old_y + delta_y)

    def _get_offset(self):
        if self._parent is not None:
            parent_offset_x, parent_offset_y = self._parent.offset
            return (self._offset[0] + parent_offset_x, self._offset[1] + parent_offset_y)
        else:
            return self._offset

    def Close(self):
        self._controller.on_update.disconnect(self._on_update)
        self._controller.on_close.disconnect(self.Close)
        super(ElevatedBase, self).Close()


class ElevatedContainer(ElevatedBase):
    default_name = 'ElevatedContainer'

    def __init__(self, controller, layer, anchor = (0.5, 0.5), elevation = 0.0, offset = (0, 0), parent = None, width = 0, height = 0):
        super(ElevatedContainer, self).__init__(controller=controller, layer=layer, anchor=anchor, elevation=elevation, width=width, height=height, offset=offset, parent=parent)


class ElevatedContainerAutoSize(ElevatedBase, ContainerAutoSize):
    default_name = 'ElevatedContainerAutoSize'

    def __init__(self, controller, layer, anchor = (0.5, 0.5), elevation = 0.0, offset = (0, 0), parent = None, width = 0, height = 0, align_mode = None):
        super(ElevatedContainerAutoSize, self).__init__(controller=controller, layer=layer, anchor=anchor, elevation=elevation, width=width, height=height, offset=offset, parent=parent, alignMode=align_mode)
