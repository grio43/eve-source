#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphs\exoplanetstutorialgraph.py
from projectdiscovery.client.projects.exoplanets.graphs.exoplanetsgraph import ExoPlanetsGraph
from projectdiscovery.client.projects.exoplanets.graphs.tutorialgraph import TutorialGraph
from carbonui.uicore import uicore
import carbonui.graphs.axis as axis

class ExoPlanetsTutorialGraph(ExoPlanetsGraph):
    __notifyevents__ = ExoPlanetsGraph.__notifyevents__ + ['OnDisplayTutorialGraph', 'OnRemoveTutorialGraphs', 'OnTutorialReset']

    def ApplyAttributes(self, attributes):
        self._are_tutorial_graph_hidden = False
        self._tutorial_graphs = []
        self._tutorial_marker_cache = []
        self._tutorial_category_axes = []
        self._was_zoom_animation_running = False
        self._is_right_click_disabled = False
        self._is_left_click_disabled = False
        self._is_no_mouse_up = False
        self._is_mouse_down = False
        self._task_number = 0
        super(ExoPlanetsTutorialGraph, self).ApplyAttributes(attributes)

    def OnDataLoaded(self, data):
        super(ExoPlanetsTutorialGraph, self).OnDataLoaded(data)
        if self._task_number == 0:
            min_time, max_time = data[0][0], data[-1][0]
            self.zoom(0.75 * min_time + 0.25 * max_time, 0.25 * min_time + 0.75 * max_time)
        self._task_number += 1

    def OnTutorialReset(self):
        self._task_number = 0

    def clean_container(self):
        self._tutorial_marker_cache = []
        self._destruct_tutorial_graphs()
        super(ExoPlanetsTutorialGraph, self).clean_container()

    def _on_animation(self):
        super(ExoPlanetsTutorialGraph, self)._on_animation()
        if not self._is_zoom_animation:
            self._hide_tutorial_graphs()
        else:
            self._was_zoom_animation_running = True

    def set_current_task(self, task_index):
        self._task_number = task_index

    def _on_animation_stopped(self):
        super(ExoPlanetsTutorialGraph, self)._on_animation_stopped()
        if not self.is_animation_running() and not self._was_zoom_animation_running:
            self._show_tutorial_graphs()
        else:
            self._was_zoom_animation_running = False

    def display_tutorial_graph(self, transit_selection):
        self._tutorial_marker_cache.append(transit_selection)
        category_axis = self._time_axis_type([0], dataRange=(self._time_axis.get_min_value(), self._time_axis.get_max_value()), margins=(0.01, 0.01))
        category_axis.set_zoom(*self._time_axis.get_visible_range())
        self._category_axes.append(category_axis)
        self._graph_area.AddAxis(orientation=axis.AxisOrientation.HORIZONTAL, axis=category_axis)
        graph = TutorialGraph(name='TutorialGraph', parent=self._graph_area, categoryAxis=category_axis, valueAxis=self._flux_axis, transitSelection=transit_selection, opacity=0 if self._are_tutorial_graph_hidden else 1)
        self._graphs.append(graph)
        self._tutorial_graphs.append(graph)
        self._tutorial_category_axes.append(category_axis)

    def display_transit_markers(self, transit_selections, *args, **kwargs):
        super(ExoPlanetsTutorialGraph, self).display_transit_markers(transit_selections, *args, **kwargs)
        for graph in self._tutorial_graphs:
            graph.set_transit_selection_filter(transit_selections)

    def _hide_tutorial_graphs(self):
        self._destruct_tutorial_graphs()

    def _show_tutorial_graphs(self):
        cache = self._tutorial_marker_cache
        self._tutorial_marker_cache = []
        for marker in cache:
            self.display_tutorial_graph(marker)

    def zoom(self, *args, **kwargs):
        super(ExoPlanetsTutorialGraph, self).zoom(*args, **kwargs)
        if self.is_zoom():
            sm.ScatterEvent('OnProjectDiscoveryZoom', self._control_axis.get_visible_range())

    def OnMouseMove(self, *args):
        if self._is_mouse_down:
            sm.ScatterEvent('OnProjectDiscoveryMouseDrag')
        super(ExoPlanetsTutorialGraph, self).OnMouseMove(*args)

    def OnDisplayTutorialGraph(self, transit_marker, hide_graphs = False):
        self._are_tutorial_graph_hidden = hide_graphs
        self.display_tutorial_graph(transit_marker)

    def OnRemoveTutorialGraphs(self):
        self._tutorial_marker_cache = []
        self._destruct_tutorial_graphs()

    def _destruct_tutorial_graphs(self):
        for graph, axis in zip(self._tutorial_graphs, self._tutorial_category_axes):
            graph.Close()
            self._graphs.remove(graph)
            self._category_axes.remove(axis)

        self._tutorial_category_axes = []
        self._tutorial_graphs = []

    def disable_right_click(self, is_disabled = True):
        self._is_right_click_disabled = is_disabled

    def disable_left_click(self, is_disabled = True):
        self._is_left_click_disabled = is_disabled

    def OnMouseDown(self, *args):
        self._is_mouse_down = True
        if uicore.uilib.rightbtn and self._is_right_click_disabled:
            self._is_no_mouse_up = True
            return
        if uicore.uilib.leftbtn and self._is_left_click_disabled:
            self._is_no_mouse_up = True
            return
        super(ExoPlanetsTutorialGraph, self).OnMouseDown(*args)

    def OnMouseUp(self, *args):
        self._is_mouse_down = False
        if self._is_no_mouse_up:
            self._is_no_mouse_up = False
            return
        super(ExoPlanetsTutorialGraph, self).OnMouseUp(*args)

    def OnMouseWheel(self, amount, *args):
        sm.ScatterEvent('OnProjectDiscoveryScroll', amount)
        super(ExoPlanetsTutorialGraph, self).OnMouseWheel(amount)

    @property
    def graph_area(self):
        return self._graph_area
