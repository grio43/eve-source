#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphs\linepointgraph.py
from carbonui.graphs.pointgraph import PointGraph
from carbonui.uianimations import animations as uianimations
from projectdiscovery.client.projects.exoplanets.graphs.linegraph import ExoPlanetsLineGraph
from carbonui.graphs import animations
import carbonui.const as uiconst

class ExoPlanetsLinePointGraph(object):
    default_color = (1, 1, 1, 0.2)

    def __init__(self, pointColor = default_color, lineColor = default_color, values = None, parent = None, categoryAxis = None, valueAxis = None, lineWidth = 0.5, pointSize = 4, pointGraphShowState = True, fade = True, state = uiconst.UI_DISABLED):
        self._point_color = pointColor
        self._line_color = lineColor
        self._values = values
        self._parent = parent
        self._category_axis = categoryAxis
        self._value_axis = valueAxis
        self._line_width = lineWidth
        self._point_size = pointSize
        self._line_graph = None
        self._point_graph = None
        self._is_point_graph = pointGraphShowState
        self._is_fade = fade
        self._state = state
        self.show_line_graph()
        self.show_point_graph()

    def show_point_graph(self):
        if not self._point_graph and self._is_point_graph:
            self._point_graph = PointGraph(parent=self._parent, categoryAxis=self._category_axis, valueAxis=self._value_axis, values=self._values, pointSize=self._point_size, pointColor=self._point_color, state=self._state)
            if self._is_fade:
                uianimations.FadeTo(self._point_graph, 0, 1)

    def show_line_graph(self):
        if not self._line_graph:
            self._line_graph = ExoPlanetsLineGraph(parent=self._parent, categoryAxis=self._category_axis, valueAxis=self._value_axis, values=self._values, lineWidth=self._line_width, lineColor=self._line_color, state=self._state)
            if self._is_fade:
                uianimations.FadeTo(self._line_graph, 0, 1)

    def hide_point_graph(self):
        if self._point_graph:
            self._point_graph.Close()
            self._point_graph = None

    def LockGraphUpdates(self):
        if self._line_graph:
            self._line_graph.LockGraphUpdates()
        if self._point_graph:
            self._point_graph.LockGraphUpdates()

    def UnlockGraphUpdates(self):
        if self._line_graph:
            self._line_graph.UnlockGraphUpdates()
        if self._point_graph:
            self._point_graph.UnlockGraphUpdates()

    def set_show_status_of_point_graph(self, status):
        self._is_point_graph = status
        if not status:
            self.hide_point_graph()

    def get_show_status_of_point_graph(self):
        return self._is_point_graph

    def SetValues(self, values):
        self._values = values
        if self._line_graph:
            self._line_graph.SetValues(values)
        if self._point_graph:
            self._point_graph.SetValues(values)

    def Animate(self, animationType, animationDynamics, duration):
        if self._line_graph:
            self._line_graph.Animate(animationType, animationDynamics, duration)
        if self._point_graph:
            self._point_graph.Animate(animationType, animationDynamics, duration)

    def is_point_graph_visible(self):
        if self._point_graph:
            return True
        return False
