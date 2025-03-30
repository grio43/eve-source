#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphs\linegraph.py
from carbonui.graphs.axis import AxisOrientation
from carbonui.graphs.linegraph import LineGraph
import logging
logger = logging.getLogger(__name__)

class ExoPlanetsLineGraph(LineGraph):

    def ApplyAttributes(self, attributes):
        self._colors = []
        self._is_backwards = attributes.get('isBackwards', False)
        super(ExoPlanetsLineGraph, self).ApplyAttributes(attributes)
        self._categoryAxis = self._categoryAxis

    def _Build(self):
        vertices = self._get_vertex_positions()
        self._calculate_colors()
        self.renderObject.AppendVertices(vertices, self._GetTransform(), self._colors)

    def _Rescale(self):
        try:
            self.CancelAnimation(False)
            self._dirty = False
            vertices = self._get_vertex_positions()
            diff = len(vertices) - len(self.renderObject.vertices)
            if diff == 0:
                self.renderObject.SetVertices(self._vertices, self._GetTransform(), self._colors)
            else:
                self.Flush()
                self.renderObject.AppendVertices(self._vertices, self._GetTransform(), self._colors)
        except AttributeError:
            logger.warn('_Rescale attribute error', exc_info=1)

    def _get_vertex_positions(self):
        if self._orientation == AxisOrientation.VERTICAL:
            vertices = zip(self._categoryAxis.GetDataPoints(), self._values)
        else:
            vertices = zip(self._values, self._categoryAxis.GetDataPoints())
        self._vertices = vertices
        self._calculate_colors()
        return vertices

    def _calculate_colors(self):
        phase_indexes = self._categoryAxis.get_phase_division_indexes()
        self._colors = [ self.lineColor for vertex in self._vertices ]
        if not self._is_backwards:
            for index in phase_indexes:
                self._colors[index] = (0, 0, 0, 0)
                self._colors[index - 1] = (0, 0, 0, 0)
