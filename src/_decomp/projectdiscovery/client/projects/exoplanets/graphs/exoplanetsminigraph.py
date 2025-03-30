#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphs\exoplanetsminigraph.py
import carbonui.const as uiconst
import carbonui.graphs.axis as axis
from carbonui.graphs.graph import GraphArea
from carbonui.primitives.container import Container
from projectdiscovery.client.projects.exoplanets.graphs.exoplanetsbasegraph import ExoPlanetsGraphContainer

class ExoPlanetsMiniGraph(ExoPlanetsGraphContainer):
    __notifyevents__ = ExoPlanetsGraphContainer.__notifyevents__ + ['OnSolutionSubmit', 'OnContinueFromRewards']

    def ApplyAttributes(self, attributes):
        self._is_point_graph = True
        self._marker_line_width = 0.3
        super(ExoPlanetsMiniGraph, self).ApplyAttributes(attributes)
        self._setup_layout()

    def _setup_layout(self):
        if self._graph_data:
            self._setup_graph()

    def _setup_graph(self):
        self._graph_container = Container(name='graphContainer', parent=self, align=uiconst.TOALL)
        self._flux_axis = self._flux_axis_type(self.get_range_of_flux(), tickCount=4, margins=(0.01, 0.01))
        self._time_axis = self._time_axis_type(self.get_time_values(self._graph_data), margins=(0.01, 0.01))
        self._category_axes.append(self._time_axis)
        self._tooltip_area = Container(name='TooltipArea', parent=self._graph_container, align=uiconst.TOALL)
        self._result_graph_area = GraphArea(name='ResultGraphArea', parent=self._graph_container, align=uiconst.TOALL)
        self._result_graph_area.pickState = uiconst.TR2_SPS_OFF
        self._graph_area = GraphArea(name='graph', parent=self._graph_container, align=uiconst.TOALL)
        self._graph_area.pickState = uiconst.TR2_SPS_OFF
        self._graph_area.AddAxis(orientation=axis.AxisOrientation.VERTICAL, axis=self._flux_axis, minFactor=1.0, maxFactor=0.0)
        self._graph_area.AddAxis(orientation=axis.AxisOrientation.HORIZONTAL, axis=self._time_axis)
        self._create_graph_from_data(self._graph_data)
        time_values = self.get_time_values(self._graph_data)
        self.zoom(min(time_values), max(time_values))

    def OnSolutionSubmit(self, *args, **kwargs):
        self.SetState(uiconst.UI_DISABLED)

    def OnContinueFromRewards(self, *args, **kwargs):
        self.SetState(uiconst.UI_NORMAL)
