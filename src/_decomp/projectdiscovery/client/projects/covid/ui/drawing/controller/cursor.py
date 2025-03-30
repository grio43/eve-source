#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\controller\cursor.py
from projectdiscovery.client.projects.covid.ui.drawing import models
from projectdiscovery.client.projects.covid.ui.drawing.controller.states import CursorState
from projectdiscovery.client.projects.covid.ui.drawing.controller.states import CursorTarget
from projectdiscovery.client.projects.covid.ui.drawing.controller.styles import CursorStyle
from projectdiscovery.client.projects.covid.ui.drawing.controller import configs
from projectdiscovery.client.projects.covid.ui.drawing.controller import update

class Cursor(object):
    STATES = CursorState
    STYLES = CursorStyle
    TARGETS = CursorTarget

    def __init__(self, pos = None, state = CursorState.READY, target = CursorTarget.UNKNOWN, is_invalid = None, is_snapping = None, vertices_left = None, polygons_left = None, target_polygon = None, target_vertex_idx = None, snap_pos = None):
        self._pos = models.Coord(0, 0)
        if pos:
            self.pos = pos
        self._state = state
        self._target = target
        self._is_invalid = is_invalid if is_invalid is not None else False
        self._is_snapping = is_snapping if is_snapping is not None else False
        self._vertices_left = vertices_left if vertices_left is not None else configs.MAX_VERTICES
        self._polygons_left = polygons_left if polygons_left is not None else configs.MAX_POLYGONS
        self.target_polygon = target_polygon
        self.target_vertex_idx = target_vertex_idx
        self.snap_pos = snap_pos
        self.updater = update.UpdateController()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        if new_state != self._state:
            self.updater.tick()
        self._state = new_state

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        if value != self._target:
            self.updater.tick()
        self._target = value

    @property
    def is_invalid(self):
        return self._is_invalid

    @is_invalid.setter
    def is_invalid(self, value):
        if value != self._is_invalid:
            self.updater.tick()
        self._is_invalid = value

    @property
    def is_snapping(self):
        return self._is_snapping

    @is_snapping.setter
    def is_snapping(self, value):
        if value != self._is_snapping:
            self.updater.tick()
        self._is_snapping = value

    @property
    def vertices_left(self):
        return self._vertices_left

    @vertices_left.setter
    def vertices_left(self, value):
        if value != self._vertices_left:
            self.updater.tick()
        self._vertices_left = value

    @property
    def polygons_left(self):
        return self._polygons_left

    @polygons_left.setter
    def polygons_left(self, value):
        if value != self._polygons_left:
            self.updater.tick()
        self._polygons_left = value

    @property
    def cursor_style(self):
        if self.state == CursorState.DISABLED or self.target == CursorTarget.OFF_CANVAS:
            return CursorStyle.DISABLED
        if self.state == CursorState.UNKNOWN or self.target == CursorTarget.UNKNOWN:
            return CursorStyle.UNKNOWN
        if self.state == CursorState.READY:
            if self.target == CursorTarget.CANVAS:
                if self.polygons_left <= 0:
                    return CursorStyle.DRAWING_OUT_OF_POLYGONS
                else:
                    return CursorStyle.DRAWING_READY
            else:
                if self.target == CursorTarget.POLYGON:
                    return CursorStyle.HOVER_POLYGON
                if self.target == CursorTarget.VERTEX:
                    return CursorStyle.HOVER_VERTEX
                if self.target == CursorTarget.X_BUTTON:
                    return CursorStyle.HOVER_X_BUTTON
        elif self.state == CursorState.DRAWING:
            if self.target == CursorTarget.CANVAS:
                if self.is_snapping:
                    return CursorStyle.DRAWING_SNAPPING
                elif self.vertices_left <= 0:
                    return CursorStyle.DRAWING_OUT_OF_VERTICES
                else:
                    return CursorStyle.DRAWING_READY
            else:
                if self.target == CursorTarget.POLYGON:
                    return CursorStyle.DRAWING_INVALID
                if self.target == CursorTarget.VERTEX:
                    return CursorStyle.DRAWING_INVALID
                if self.target == CursorTarget.X_BUTTON:
                    return CursorStyle.DRAWING_INVALID
        elif self.state == CursorState.MODIFYING:
            if self.target == CursorTarget.POLYGON:
                if self.is_invalid:
                    return CursorStyle.MOVING_POLYGON_INVALID
                else:
                    return CursorStyle.MOVING_POLYGON
            elif self.target == CursorTarget.VERTEX:
                if self.is_invalid:
                    return CursorStyle.MOVING_VERTEX_INVALID
                else:
                    return CursorStyle.MOVING_VERTEX
        return CursorStyle.UNKNOWN

    def __repr__(self):
        return '<Cursor @{l}{pos} :{s} #{sty} [p={p}, v={v}]{i}{sn}{vp}>'.format(pos=self.pos, s=self.state.name, l=self.target.name, i=' invalid' if self.is_invalid else '', sn=' snap@' if self.is_snapping else '', vp=self.visual_pos if self.is_snapping else '', sty=self.cursor_style.name, p=self.polygons_left, v=self.vertices_left)

    @property
    def visual_pos(self):
        if self.is_snapping:
            return self.snap_pos
        return self._pos

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        if isinstance(value, models.Coord):
            self._pos.x = value.x
            self._pos.y = value.y
        elif isinstance(value, (list, tuple)) and len(value) == 2:
            self._pos.x = value[0]
            self._pos.y = value[1]
        elif isinstance(value, dict) and 'x' in value and 'y' in value:
            self._pos.x = value['x']
            self._pos.y = value['y']
        else:
            ValueError('Cursor.pos value must be a Coord, 2-tuple/list or a dict with x and y but was: %r' % value)
