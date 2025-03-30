#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphs\exoplanetsbasegraph.py
from carbonui.primitives.container import Container
from projectdiscovery.client.projects.exoplanets.graphs.linepointgraph import ExoPlanetsLinePointGraph
from projectdiscovery.client.projects.exoplanets.graphs.transitselectiongraph import TransitSelectionGraph
from projectdiscovery.client.projects.exoplanets.graphtools.basetool import BaseTool
from carbonui.uicore import uicore
import projectdiscovery.client.projects.exoplanets.graphs.axis as exo_axis
import carbonui.graphs.axis as axis
import blue
import uthread
import carbonui.const as uiconst
import logging
log = logging.getLogger(__name__)

class ExoPlanetsGraphContainer(Container):
    __notifyevents__ = ['OnDataLoaded']
    default_is_magnifying_glass_on_ctrl = True
    default_is_magnifying_glass_y_zoom = True
    default_is_point_graph = True

    def ApplyAttributes(self, attributes):
        super(ExoPlanetsGraphContainer, self).ApplyAttributes(attributes)
        self._zoom_replicate_count = 0
        self._graph_data = attributes.get('data', [])
        self._graphs = []
        self._is_folding = False
        self._graph_container = None
        self._time_axis_type = None
        self._flux_axis_type = None
        self._flux_axis = None
        self._time_axis = None
        self._category_axes = []
        self._main_graph = None
        self._graph_area = None
        self._is_point_graph = attributes.get('isPointGraph', self.default_is_point_graph)
        self._marker_line_width = 0.5
        self._fold_center = None
        self._period_length = None
        self._prev_tool = None
        self._is_hovering = False
        self.tooltipPanelClassInfo = None
        self._transit_selection_graphs = []
        self._transit_selection_category_axes = []
        self._zoomed_range = None
        self._tool = None
        self._tooltip = None
        self._tooltip_area = None
        self.is_mouse_moved = False
        self.is_wheel_scrolled = False
        self._is_time_axis_dirty = False
        self.scroll_amount = 0
        self.set_tool(BaseTool(self))
        sm.RegisterNotify(self)
        if attributes.get('startUpdateLoop', True):
            uthread.new(self.graph_update)

    def Close(self):
        sm.UnregisterNotify(self)
        super(ExoPlanetsGraphContainer, self).Close()

    def OnDataLoaded(self, data):
        self.clean_container()
        self._is_folding = False
        self._tool.set_is_folded(False)
        self.set_data(data)

    def _setup_layout(self):
        pass

    def graph_update(self):
        while not self.destroyed:
            if self.is_mouse_moved:
                self.is_mouse_moved = False
                self.on_mouse_move()
            if self.is_wheel_scrolled:
                self.is_wheel_scrolled = False
                self.on_mouse_wheel(self.scroll_amount)
            blue.synchro.Yield()
            self.unlock_graph_updates()

    def set_tool(self, tool):
        if self._tooltip:
            self._tooltip.Close()
        if self._tool:
            self._tool.on_tool_unset()
        self._tool = tool
        self._tool.set_is_folded(self.is_folding())
        self._tool.set_graph(self)
        self._tooltip = tool.get_tool_tip_object()
        self._tooltip.SetParent(self._tooltip_area)
        self._tool.on_tool_set()
        if self._is_hovering:
            self.OnMouseEnter()

    def OnMouseMove(self, *args):
        self.is_mouse_moved = True

    def OnMouseWheel(self, amount, *args):
        self.is_wheel_scrolled = True
        self.scroll_amount = amount

    def OnMouseDown(self, button, *args):
        if button not in (uiconst.MOUSELEFT, uiconst.MOUSERIGHT):
            return
        time, flux = self._get_mouse_values()
        if time and flux:
            self._tool.on_mouse_down(time, flux)

    def OnMouseUp(self, button, *args):
        if button not in (uiconst.MOUSELEFT, uiconst.MOUSERIGHT):
            return
        time, flux = self._get_mouse_values()
        if time and flux:
            self._tool.on_mouse_up(time, flux)

    def OnMouseExit(self, *args):
        self._is_hovering = False
        time, flux = self._get_mouse_values()
        if time and flux:
            self._tool.on_mouse_exit(time, flux)

    def OnMouseEnter(self, *args):
        self._is_hovering = True
        time, flux = self._get_mouse_values()
        if time and flux:
            self._tool.on_mouse_enter(time, flux)

    def OnMouseHover(self, *args):
        time, flux = self._get_mouse_values()
        if time and flux:
            self._tool.on_mouse_hover(time, flux)

    def OnClick(self, *args):
        time, flux = self._get_mouse_values()
        if time and flux:
            self._tool.on_click(time, flux)

    def on_mouse_move(self):
        time, flux = self._get_mouse_values()
        if time and flux:
            self._tool.on_mouse_move(time, flux)
        else:
            self._tool.on_mouse_exit()

    def on_mouse_wheel(self, amount):
        self._tool.on_scroll(amount)

    def _get_mouse_values(self):
        if not self._graph_area or not self._time_axis or not self._flux_axis:
            return (None, None)
        mouse_x, mouse_y = uicore.uilib.x, uicore.uilib.y
        graph_left, graph_top = self._graph_area.GetAbsolutePosition()
        graph_x, graph_y = mouse_x - graph_left, mouse_y - graph_top
        time = self._time_axis.get_axis_value_from_graph_coordinate(graph_x)
        flux = self._flux_axis.get_axis_value_from_graph_coordinate(graph_y)
        return (time, flux)

    def get_graph_data(self):
        return self._graph_data

    def _create_graph_from_data(self, data):
        self._graph_area.AddAxis(orientation=axis.AxisOrientation.HORIZONTAL, axis=self._time_axis)
        point_color = (0.7, 1, 1, 0.3)
        line_color = (0.3215, 0.4235, 0.4352, 2.7)
        self._main_graph = ExoPlanetsLinePointGraph(parent=self._graph_area, categoryAxis=self._time_axis, valueAxis=self._flux_axis, values=self.get_flux_values(data), lineWidth=0.2, pointSize=2, lineColor=line_color, pointColor=point_color, pointGraphShowState=self._is_point_graph)
        self._graphs.append(self._main_graph)

    def get_range_of_flux(self):
        flux_values = self.get_flux_values(self._graph_data)
        return (min(flux_values), max(flux_values))

    def get_time_values(self, data):
        return [ point[0] for point in data ]

    def get_flux_values(self, data):
        return [ point[1] for point in data ]

    def lock_graph_updates(self):
        for graph in self._graphs:
            graph.LockGraphUpdates()

    def unlock_graph_updates(self):
        for graph in self._graphs:
            graph.UnlockGraphUpdates()

    def display_transit_markers(self, transit_selections):
        self._remove_transit_selections_not_in_list(transit_selections)
        self._create_markers_not_in_list(transit_selections)

    def _remove_transit_selections_not_in_list(self, transit_selections):
        removed = []
        for graph in self._transit_selection_graphs:
            if graph.get_transit_selection() not in transit_selections:
                removed.append(graph)
                graph.Close()

        for graph in removed:
            self._graphs.remove(graph)
            self._transit_selection_graphs.remove(graph)
            self._category_axes.remove(graph.category_axis)

    def _create_markers_not_in_list(self, transit_selections):
        current_markers = [ graph.get_transit_selection() for graph in self._transit_selection_graphs ]
        for marker in transit_selections:
            if marker not in current_markers:
                graph, selection_axis = self._create_transit_selection_graph_components(marker)
                self._graphs.append(graph)
                self._transit_selection_graphs.append(graph)
                self._category_axes.append(selection_axis)
                self._transit_selection_category_axes.append(selection_axis)
                self._graph_area.AddAxis(orientation=axis.AxisOrientation.HORIZONTAL, axis=selection_axis)

    def _create_transit_selection_graph_components(self, transit_selection):
        selection_axis = self._time_axis_type(transit_selection.get_centers(), dataRange=(self._time_axis.get_min_value(), self._time_axis.get_max_value()), margins=(0.01, 0.01))
        min_time_value, max_time_value = self.get_time_visible_range()
        selection_axis.set_zoom(min_time_value, max_time_value)
        graph = TransitSelectionGraph(name='TransitSelectionGraph', parent=self._graph_area, categoryAxis=selection_axis, valueAxis=self._flux_axis, lineColor=transit_selection.get_color(), texturePath=transit_selection.pattern_path, transitSelection=transit_selection, state=uiconst.UI_DISABLED, lineWidth=1.0 / uicore.dpiScaling)
        return (graph, selection_axis)

    def clean_container(self):
        self._category_axes = []
        self._graphs = []
        self._transit_selection_graphs = []
        self._transit_selection_category_axes = []
        if self._graph_container:
            self._graph_container.Close()

    def set_data(self, data, flux_axis = exo_axis.ExoPlanetsAutoTickAxis, time_axis = exo_axis.ExoPlanetsDayTimeAxis):
        self._zoomed_range = None
        self._graph_data = data
        self._flux_axis_type = flux_axis
        self._time_axis_type = time_axis
        self.clean_container()
        self._setup_layout()

    def update_data(self, data, new_zoomed_range = None, adjust_zoom = True):
        self.lock_graph_updates()
        self._graph_data = data
        flux_values = self.get_flux_values(data)
        time_values = self.get_time_values(data)
        min_flux, max_flux = min(flux_values), max(flux_values)
        if self._main_graph:
            self._main_graph.SetValues(flux_values)
            self._time_axis.set_data_points(time_values)
            self._flux_axis.set_data_range(min_flux, max_flux)
        if adjust_zoom:
            self._zoomed_range = None
            if new_zoomed_range:
                self.zoom(*new_zoomed_range)
            else:
                self.zoom(*self.get_time_visible_range())

    def _remove_all_transit_selection_graphs(self):
        for graph in self._transit_selection_graphs:
            self._graphs.remove(graph)
            graph.Close()

        for category_axis in self._transit_selection_category_axes:
            self._category_axes.remove(category_axis)

        self._transit_selection_category_axes = []
        self._transit_selection_graphs = []

    def zoom(self, min_time_value, max_time_value, min_flux = None, max_flux = None):
        if not (min_flux and max_flux) and (min_time_value, max_time_value) == self._zoomed_range:
            self._zoom_replicate_count += 1
            return
        self._zoom_replicate_count = 0
        self._zoomed_range = (min_time_value, max_time_value)
        for category_axis in self._category_axes:
            category_axis.set_zoom(min_time_value, max_time_value)

        if self.is_folding():
            min_flux = min_flux or self._flux_axis.get_min_value()
            max_flux = max_flux or self._flux_axis.get_max_value()
            padding = (self._flux_axis.get_max_value() - self._flux_axis.get_min_value()) / 10
            self._flux_axis.set_zoom(min_flux - padding, max_flux + padding)
        elif min_flux and max_flux:
            self._flux_axis.set_zoom(min_flux, max_flux)
        else:
            in_range = [ self._graph_data[i][1] for i in xrange(len(self._graph_data)) if min_time_value <= self._graph_data[i][0] <= max_time_value ]
            in_range = sorted(in_range)
            if len(in_range) > 1:
                padding = (in_range[-1] - in_range[0]) / 10
                min_value, max_value = in_range[0] - padding, in_range[-1] + padding
                self._flux_axis.set_zoom(min_value, max_value)

    def get_time_visible_range(self):
        return self._time_axis.get_visible_range()

    def get_flux_visible_range(self):
        return self._flux_axis.get_visible_range()

    def is_zoom(self):
        if self._time_axis:
            max_range = (self._time_axis.get_min_value(), self._time_axis.get_max_value())
            current_range = self.get_time_visible_range()
            return max_range != current_range

    def get_time_range(self):
        time_values = self.get_time_values(self._graph_data)
        return (min(time_values), max(time_values))

    def on_graph_movement(self):
        if self._main_graph and self._main_graph.is_point_graph_visible():
            self._main_graph.hide_point_graph()

    def on_graph_movement_stopped(self):
        if self._main_graph and not self._main_graph.is_point_graph_visible():
            self._main_graph.show_point_graph()

    def fold(self, center, period, *args, **kwargs):
        try:
            self.lock_graph_updates()
            if not self.is_folding():
                self._tool.set_is_folded(True)
            half_period = period / 2.0
            self._fold_center = center
            self._period_length = period
            self._is_folding = True
            for category_axis in self._category_axes:
                category_axis.fold(center, period)

            self.zoom(center - half_period, center + half_period)
        except IndexError:
            log.exception('fold index error')

    def is_folding(self):
        return self._is_folding

    def unfold(self, *args, **kwargs):
        self.lock_graph_updates()
        if self.is_folding():
            self._tool.set_is_folded(False)
        self._is_folding = False
        self._fold_center = None
        self._period_length = None
        for category_axis in self._category_axes:
            category_axis.unfold()

    def get_displayed_transit_markers(self):
        return [ graph.get_transit_selection() for graph in self._transit_selection_graphs ]

    def map_time_value_to_screen_value(self, value):
        if self._time_axis:
            return self._time_axis.MapToViewport(value)

    def map_flux_value_to_screen_value(self, value):
        if self._flux_axis:
            return self._flux_axis.MapToViewport(value)

    @property
    def folding_center(self):
        return self._fold_center

    @property
    def folding_period(self):
        return self._period_length
