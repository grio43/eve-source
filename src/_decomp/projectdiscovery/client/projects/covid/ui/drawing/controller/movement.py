#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\controller\movement.py
from projectdiscovery.client.projects.covid.ui.drawing.controller import states
from projectdiscovery.client.projects.covid.ui.drawing import models
from projectdiscovery.client.projects.covid.ui.drawing.controller import update
from projectdiscovery.client.projects.covid.ui.drawing.controller import configs
import logging
log = logging.getLogger('projectdiscovery.covid.controller.movement')

class MovementController(object):
    STATES = states.MovementState

    def __init__(self):
        self._state = states.MovementState.DISABLED
        self._starting_pos = models.Coord(0, 0)
        self._current_pos = models.Coord(0, 0)
        self._is_out_of_bounds = False
        self._is_overlapping = False
        self._target_polygon = None
        self.updater = update.UpdateController()

    def enable(self):
        if self.state == states.MovementState.DISABLED:
            self.state = states.MovementState.READY
            self._reset()

    def disable(self):
        self.state = states.MovementState.DISABLED
        self._reset()

    def _reset(self):
        self.is_out_of_bounds = False
        self.is_overlapping = False
        if self._target_polygon:
            self._target_polygon.is_moving = False
            self._target_polygon.is_invalid = False
        self._target_polygon = None
        self._starting_pos = models.Coord(0, 0)
        self._current_pos = models.Coord(0, 0)
        self.updater.tick()

    def begin_move(self, target_polygon, starting_pos):
        if self.state == states.MovementState.DISABLED:
            return
        if self.state == states.MovementState.READY:
            self.state = states.MovementState.STARTING
            self._target_polygon = target_polygon
            self._starting_pos = starting_pos.as_copy
            self.current_pos = starting_pos
            self.updater.tick()
        else:
            log.error('trying to start movement in unsupported state: %r', self.state)
            self.state = states.MovementState.READY
            self._reset()

    def set_current_pos(self, new_current_pos):
        if self.state == states.MovementState.STARTING:
            self.current_pos = new_current_pos
            if self._move_start_radius_reached():
                self.state = states.MovementState.MOVING
                self._target_polygon.is_moving = True
        if self.state == states.MovementState.MOVING:
            self.current_pos = new_current_pos

    def cancel(self):
        self.state = states.MovementState.READY
        self._reset()

    def execute_move(self):
        if self.state == states.MovementState.MOVING:
            if self._is_overlapping:
                raise ValueError('trying to execute move while overlapping')
            if self._is_out_of_bounds:
                raise ValueError('trying to execute move while out of bounds')
            if not self._target_polygon:
                raise ValueError('trying to execute move without a polygon')
            self._target_polygon.translate(self.translation)
            self.state = states.MovementState.READY
            self._reset()
        else:
            log.error('trying to execute move while not actually moving')

    def _move_start_radius_reached(self):
        return not self._starting_pos.is_within_dist(self._current_pos, configs.START_MOVE_RADIUS)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value != self._state:
            self.updater.tick()
        self._state = value

    @property
    def starting_pos(self):
        return self._starting_pos

    @starting_pos.setter
    def starting_pos(self, value):
        raise AttributeError('starting_pos is read-only')

    @property
    def current_pos(self):
        return self._current_pos

    @current_pos.setter
    def current_pos(self, value):
        old_val = self._current_pos.as_copy
        if isinstance(value, models.Coord):
            self._current_pos.x = value.x
            self._current_pos.y = value.y
        elif isinstance(value, (list, tuple)) and len(value) == 2:
            self._current_pos.x = value[0]
            self._current_pos.y = value[1]
        elif isinstance(value, dict) and 'x' in value and 'y' in value:
            self._current_pos.x = value['x']
            self._current_pos.y = value['y']
        else:
            ValueError('current_pos value must be a Coord, 2-tuple/list or a dict with x and y but was: %r' % value)
        if old_val != self._current_pos:
            self.updater.tick()

    @property
    def translation(self):
        return self._starting_pos.delta(self._current_pos)

    @property
    def is_out_of_bounds(self):
        return self._is_out_of_bounds

    @is_out_of_bounds.setter
    def is_out_of_bounds(self, value):
        if value != self._is_out_of_bounds:
            self.updater.tick()
            self._target_polygon.is_invalid = value
        self._is_out_of_bounds = value

    @property
    def is_overlapping(self):
        return self._is_overlapping

    @is_overlapping.setter
    def is_overlapping(self, value):
        if value != self._is_overlapping:
            self.updater.tick()
            self._target_polygon.is_invalid = value
        self._is_overlapping = value

    @property
    def translated_segments(self):
        if self._target_polygon:
            tr = self.translation
            seg_list = []
            for s in self._target_polygon.segments:
                start = s.start
                start += tr
                end = s.end
                end += tr
                seg_list.append(s)

            return seg_list

    @property
    def target_polygon(self):
        return self._target_polygon

    @target_polygon.setter
    def target_polygon(self, value):
        raise AttributeError('target_polygon is read only')

    def __repr__(self):
        pos = ''
        if self.state in (states.MovementState.STARTING, states.MovementState.MOVING):
            pos = '@{st!r}->{c!r}'.format(st=self._starting_pos.as_tuple, c=self._current_pos.as_tuple)
        return '<MovementController:{s}{pos}{t}{oob}{ov}>'.format(s=self.state.name, pos=pos, t='#%s' % self._target_polygon.uuid if self._target_polygon else '', oob=' oob' if self._is_out_of_bounds else '', ov=' overlap' if self._is_overlapping else '')
