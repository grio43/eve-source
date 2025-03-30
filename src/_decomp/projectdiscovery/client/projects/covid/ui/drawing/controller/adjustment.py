#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\controller\adjustment.py
from projectdiscovery.client.projects.covid.ui.drawing.controller import states
from projectdiscovery.client.projects.covid.ui.drawing import models
from projectdiscovery.client.projects.covid.ui.drawing.controller import update
import logging
log = logging.getLogger('projectdiscovery.covid.controller.adjustment')

class AdjustmentController(object):
    STATES = states.AdjustmentState

    def __init__(self):
        self._state = states.AdjustmentState.DISABLED
        self._starting_pos = models.Coord(0, 0)
        self._current_pos = models.Coord(0, 0)
        self._is_overlapping = False
        self._target_polygon = None
        self._target_vertex_index = 0
        self._idx_up = 0
        self._idx_down = 0
        self._static_chain = None
        self._right = None
        self._right_of_right = None
        self._left = None
        self._left_of_left = None
        self.updater = update.UpdateController()

    def enable(self):
        if self.state == states.AdjustmentState.DISABLED:
            self.state = states.AdjustmentState.READY
            self._reset()

    def disable(self):
        self.state = states.AdjustmentState.DISABLED
        self._reset()

    def begin_move(self, target_polygon, target_vertex_index, starting_pos):
        if self.state == states.AdjustmentState.DISABLED:
            return
        if self.state == states.AdjustmentState.READY:
            self.state = states.AdjustmentState.MOVING
            self._target_polygon = target_polygon
            self._target_polygon.is_adjusting = True
            self._target_vertex_index = target_vertex_index
            self._idx_up = self._target_vertex_index + 1
            if self._idx_up >= len(self._target_polygon.verticies):
                self._idx_up = 0
            self._idx_down = self._target_vertex_index - 1
            if self._idx_down < 0:
                self._idx_down = len(self._target_polygon.verticies) - 1
            self._starting_pos = starting_pos.as_copy
            self.current_pos = starting_pos
            self.updater.tick()
            log.info('begin_move: %r', self)
        else:
            log.error('trying to start adjustment in unsupported state: %r', self.state)
            self.state = states.AdjustmentState.READY
            self._reset()

    def set_current_pos(self, new_current_pos):
        if self.state == states.AdjustmentState.MOVING:
            self.current_pos = new_current_pos

    def cancel(self):
        log.info('cancel: %r', self)
        self._reset()

    def execute_move(self):
        log.info('execute_move: %r', self)
        if self.state == states.AdjustmentState.MOVING:
            if self._is_overlapping:
                raise ValueError('trying to execute move while overlapping')
            if not self._target_polygon:
                raise ValueError('trying to execute move without a polygon')
            self._target_polygon.adjust(self._target_vertex_index, self._current_pos)
            self.state = states.MovementState.READY
            self._reset()
        else:
            log.error('trying to execute adjust while not actually moving')

    def _reset(self):
        self.is_overlapping = False
        if self._target_polygon:
            self._target_polygon.is_adjusting = False
            self._target_polygon.is_invalid = False
        self._target_polygon = None
        self._target_vertex_index = 0
        self._idx_up = 0
        self._idx_down = 0
        self._starting_pos = models.Coord(0, 0)
        self._current_pos = models.Coord(0, 0)
        self._static_chain = None
        self._right = None
        self._right_of_right = None
        self._left = None
        self._left_of_left = None
        self.updater.tick()

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
            self._left = None
            self._right = None
            self.updater.tick()

    @property
    def translation(self):
        return self._starting_pos.delta(self._current_pos)

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
    def target_polygon(self):
        return self._target_polygon

    @target_polygon.setter
    def target_polygon(self, value):
        raise AttributeError('target_polygon is read only')

    @property
    def target_vertex_index(self):
        return self._target_vertex_index

    @target_vertex_index.setter
    def target_vertex_index(self, value):
        raise AttributeError('target_vertex_index is read only')

    @property
    def adjusted_segment_chain(self):
        if self.state == states.AdjustmentState.MOVING:
            return models.SegmentChain([self._target_polygon.verticies[self._idx_down].as_copy, self._current_pos.as_copy, self._target_polygon.verticies[self._idx_up].as_copy])

    @property
    def static_segment_chain(self):
        if self.state == states.AdjustmentState.MOVING:
            if self._static_chain is None:
                left_buff = []
                right_buff = []
                current_buff = left_buff
                for i, v in enumerate(self._target_polygon.verticies):
                    if i > self._target_vertex_index:
                        right_buff.append(v.as_copy)
                    elif i < self._target_vertex_index:
                        left_buff.append(v.as_copy)

                self._static_chain = models.SegmentChain(right_buff + left_buff)
            return self._static_chain

    @property
    def left_segment(self):
        if self.state == states.AdjustmentState.MOVING:
            if self._left is None:
                self._left = models.Segment(self._target_polygon.verticies[self._idx_down].as_copy, self._current_pos.as_copy)
            return self._left

    @property
    def left_of_left_segment(self):
        if self.state == states.AdjustmentState.MOVING:
            if self._left_of_left is None:
                idx_downer = self._idx_down - 1
                if idx_downer < 0:
                    idx_downer = len(self._target_polygon.verticies) - 1
                self._left_of_left = models.Segment(self._target_polygon.verticies[idx_downer].as_copy, self._target_polygon.verticies[self._idx_down].as_copy)
            return self._left_of_left

    @property
    def right_segment(self):
        if self.state == states.AdjustmentState.MOVING:
            if self._right is None:
                self._right = models.Segment(self._current_pos.as_copy, self._target_polygon.verticies[self._idx_up].as_copy)
            return self._right

    @property
    def right_of_right_segment(self):
        if self.state == states.AdjustmentState.MOVING:
            if self._right_of_right is None:
                idx_upper = self._idx_up + 1
                if idx_upper >= len(self._target_polygon.verticies):
                    idx_upper = 0
                self._right_of_right = models.Segment(self._target_polygon.verticies[self._idx_up].as_copy, self._target_polygon.verticies[idx_upper].as_copy)
            return self._right_of_right

    def __repr__(self):
        pos = ''
        if self.state in (states.MovementState.STARTING, states.MovementState.MOVING):
            pos = '@{st!r}->{c!r}'.format(st=self._starting_pos.as_tuple, c=self._current_pos.as_tuple)
        return '<AdjustmentController:{s}{pos}{t}{ov}>'.format(s=self.state.name, pos=pos, t='#%s[%s]' % (self._target_polygon.uuid, self._target_vertex_index) if self._target_polygon else '', ov=' overlap' if self._is_overlapping else '')
