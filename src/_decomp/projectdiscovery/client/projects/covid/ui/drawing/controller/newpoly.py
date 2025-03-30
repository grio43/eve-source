#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\controller\newpoly.py
import datetime
from projectdiscovery.client.projects.covid.ui.drawing.controller import configs
from projectdiscovery.client.projects.covid.ui.drawing import models
from projectdiscovery.client.projects.covid.ui.drawing.controller.states import NewDrawingState
import logging
log = logging.getLogger('projectdiscovery.covid.controller.newdrawing')

class NewDrawingController(object):
    STATES = NewDrawingState

    def __init__(self):
        self._state = NewDrawingState.DISABLED
        self._segment_chain = models.SegmentChain()
        self._start_timestamp = datetime.datetime.utcnow()

    def enable(self):
        if self._state == NewDrawingState.DISABLED:
            self._state = NewDrawingState.READY

    def disable(self):
        self.reset()
        self._state = NewDrawingState.DISABLED

    def start_new(self, coord):
        if self._state == NewDrawingState.READY:
            self._segment_chain.add_vertex(coord.as_copy)
            self._state = NewDrawingState.DRAWING
        else:
            raise ValueError('state must be READY to start a new drawing: state=%r' % self._state.name)

    def add_vertex(self, coord):
        if self._state == NewDrawingState.DRAWING:
            if self.is_full:
                raise ValueError('maximum vertices reached')
            if coord not in self._segment_chain:
                self._segment_chain.add_vertex(coord.as_copy)
        else:
            raise ValueError('state must be DRAWING to add a new vertex: state=%r' % self._state.name)

    def undo(self):
        if self._state == NewDrawingState.DRAWING:
            if self.vertex_count == 1:
                self.reset()
            elif self.vertex_count > 1:
                self._segment_chain.verticies.pop(-1)

    def close(self):
        if self._state == NewDrawingState.DRAWING:
            if self.is_closable:
                res = models.TrackedPolygon(list_of_verticies=[ v.as_copy for v in self._segment_chain.verticies ], drawing_started_at=self._start_timestamp, drawing_duration=datetime.datetime.utcnow() - self._start_timestamp)
                self.reset()
                return res
            raise ValueError('minimum vertex count not reached: %s of %s' % (self.vertex_count, configs.MIN_VERTICES))
        else:
            raise ValueError('state must be DRAWING to close the chain: state=%r' % self._state.name)

    def reset(self):
        if self.segment_chain.verticies:
            self.segment_chain.verticies = []
        if self._state != NewDrawingState.DISABLED:
            self._state = NewDrawingState.READY

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        raise AttributeError('state should not be changed from the outside')

    @property
    def segment_chain(self):
        return self._segment_chain

    @segment_chain.setter
    def segment_chain(self, value):
        raise AttributeError('segment_chain should not be changed from the outside')

    @property
    def start_timestamp(self):
        return self._start_timestamp

    @start_timestamp.setter
    def start_timestamp(self, value):
        raise AttributeError('start_timestamp should not be changed from the outside')

    @property
    def vertices_left(self):
        return configs.MAX_VERTICES - self.vertex_count

    @property
    def is_closable(self):
        return self.vertex_count >= configs.MIN_VERTICES

    @property
    def is_full(self):
        return self.vertices_left <= 0

    @property
    def vertex_count(self):
        return len(self.segment_chain)

    @property
    def last_vertex(self):
        return self.segment_chain.last_vertex

    @property
    def first_vertex(self):
        return self.segment_chain.first_vertex

    def __repr__(self):
        return '<NewDrawingController:{s}{cl}{f} {ch}>'.format(s=self._state.name, ch=self.segment_chain, cl=' closable' if self.is_closable else '', f=' full' if self.is_full else '')
