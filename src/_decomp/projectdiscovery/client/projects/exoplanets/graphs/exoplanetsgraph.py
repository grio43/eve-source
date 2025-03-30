#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphs\exoplanetsgraph.py
from carbonui.graphs.axis import AutoTicksAxis
from carbonui.graphs.graph import GraphArea
from carbonui.graphs.grid import Grid
from carbonui.graphs.minimap import MiniMap
from carbonui.graphs.pointgraph import PointGraph
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from evegraphics import settings as gfxsettings
from projectdiscovery.client.projects.exoplanets.graphs.consensusgraph import ConsensusGraph
from projectdiscovery.client.projects.exoplanets.graphs.exoplanetsminigraph import ExoPlanetsMiniGraph
from projectdiscovery.client.projects.exoplanets.graphs.exoplanetsbasegraph import ExoPlanetsGraphContainer
from carbonui.primitives.line import Line
from carbonui.uianimations import animations as uianimations
from itertools import izip
from projectdiscovery.client import const
from projectdiscovery.client.projects.exoplanets.exoplanetsutil import calibration, binning, result, zoom
from projectdiscovery.client.projects.exoplanets.graphs.resulticongraph import ResultIconGraph
from projectdiscovery.client.projects.exoplanets.graphtools.magnifyingglasstool import MagnifyingGlassTool, MagnifyingGlassScalingOrientation
from projectdiscovery.client.projects.exoplanets.transitinformationcontainer import TransitInformationContainer
import carbonui.const as uiconst
import carbonui.graphs.axis as axis
import carbonui.graphs.axislabels as axislabels
import animations
import trinity
import geo2
import blue
import math
import localization
FOLD_ANIMATION_MAX_TIME = 0.5

class ExoPlanetsGraph(ExoPlanetsGraphContainer):
    __notifyevents__ = ExoPlanetsGraphContainer.__notifyevents__ + ['OnProjectDiscoveryResultBackButtonPressed']
    default_mini_map_color = (1.0,
     1.0,
     1.0,
     0.09)

    def ApplyAttributes(self, attributes):
        self._audio_service = sm.GetService('audio')
        self.setup_binning_fidelity()
        self._mini_graph = None
        self._mini_map = None
        self._mini_map_area = None
        self._loading_wheel = None
        self._is_time_axis_dirty = False
        self._is_mini_map_hidden = False
        self._desired_animation_zoom = None
        self._m_update_progression = 0
        self._is_zoom_animation = False
        self._is_update_animation = False
        self._is_calibration_animation = False
        self._is_fold_animation = False
        self._m_calibration_progression = 0
        self._calibration_marking_start_points = []
        self._calibration_marking_end_points = []
        self._calibration_marking_color = (1, 1, 1, 1)
        self._calibration_axis = None
        self._calibration_graph = None
        self._start_animation_data = []
        self._end_animation_data = []
        self._consensus_vertical_axis = None
        self._consensus_time_axis = None
        self._consensus_graph = None
        self._interval_mapping = {}
        self._is_result_shown = False
        self._correct_horizontal_axis = None
        self._missed_horizontal_axis = None
        self._incorrect_horizontal_axis = None
        self._correct_graph = None
        self._missed_graph = None
        self._incorrect_graph = None
        self._fold_result_state = None
        self._fold_result_points_indices = []
        self._correct_point_indices = []
        self._missed_point_indices = []
        self._incorrect_point_indices = []
        self._result_icon_graphs = []
        self._correct_intervals = []
        self._incorrect_intervals = []
        self._missed_intervals = []
        self._last_scroll_time = 0
        self._scroll_reset_time = 1
        self._is_scroll_reset = True
        super(ExoPlanetsGraph, self).ApplyAttributes(attributes)
        self.pickState = uiconst.TR2_SPS_ON
        self._setup_layout()

    def setup_binning_fidelity(self):
        shader_quality = gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY)
        self.animation_binning_fidelity = 15 if shader_quality == 1 else 1
        self.binning_fidelity = 1

    def graph_update(self):
        while not self.destroyed:
            current_time = trinity.device.animationTime
            if self.is_mouse_moved:
                self.is_mouse_moved = False
                self.on_mouse_move()
            if self.is_wheel_scrolled:
                self.is_wheel_scrolled = False
                self.on_mouse_wheel(self.scroll_amount)
            if self._is_time_axis_dirty:
                self.on_time_axis_changed()
            if not self._is_scroll_reset and current_time >= self._last_scroll_time + self._scroll_reset_time:
                self._is_scroll_reset = True
                if not self.is_animation_running():
                    self.on_graph_movement_stopped()
            blue.synchro.Yield()
            self.unlock_graph_updates()

    def disable_point_graph(self):
        if self._main_graph:
            self._main_graph.set_show_status_of_point_graph(False)

    def enable_point_graph(self):
        if self._main_graph:
            self._main_graph.set_show_status_of_point_graph(True)
            if not self.is_animation_running() and self._is_scroll_reset:
                self._main_graph.show_point_graph()

    def on_mouse_wheel(self, amount):
        if self.is_folding():
            self._scroll_fade()
        super(ExoPlanetsGraph, self).on_mouse_wheel(amount)

    def _scroll_fade(self, *args, **kwargs):
        self._is_scroll_reset = False
        self._last_scroll_time = trinity.device.animationTime
        self.on_graph_movement()

    def _setup_layout(self):
        self._graph_container = None
        if self._loading_wheel:
            self._loading_wheel.Close()
            self._loading_wheel = None
        if self._graph_data:
            self.SetState(uiconst.UI_NORMAL)
            self.setup_graph()
            sm.ScatterEvent('OnEnableDetrend')
        else:
            self.SetState(uiconst.UI_DISABLED)
            self._setup_waiting_screen()

    def setup_graph(self):
        self._audio_service.SendUIEvent(const.Sounds.MainImageLoadStop)
        self._graph_container = Container(name='graphContainer', parent=self, align=uiconst.TOALL)
        self._consensus_vertical_axis = AutoTicksAxis(dataRange=(0, 1.6), tickCount=10, tickFilter=consensus_tick_filter, labelFormat=consensus_label_format)
        self._flux_axis = self._flux_axis_type(self.get_range_of_flux(), tickCount=4, margins=(0.01, 0.01))
        self._time_axis = self._time_axis_type(self.get_time_values(self._graph_data), margins=(0.01, 0.01))
        self._category_axes.append(self._time_axis)
        Line(parent=self._graph_container, align=uiconst.TOBOTTOM, opacity=0.2)
        self._setup_mini_map_area()
        Line(parent=self._graph_container, align=uiconst.TOBOTTOM, opacity=0.2)
        self._time_labels = axislabels.AxisLabels(name='ExoPlanetsTimeLabels', parent=self._graph_container, align=uiconst.TOBOTTOM, height=30, axis=self._time_axis, orientation=axis.AxisOrientation.HORIZONTAL, minFactor=0, maxFactor=1, textAlignment=uiconst.CENTER)
        Line(parent=self._graph_container, align=uiconst.TOBOTTOM, opacity=0.05)
        self._tooltip_area = Container(name='TooltipArea', parent=self._graph_container, align=uiconst.TOALL)
        if self._tool:
            self.set_tool(self._tool)
        self._consensus_graph_area = GraphArea(name='ConsensusGraphArea', parent=self._graph_container, align=uiconst.TOALL, clipChildren=False, state=uiconst.UI_PICKCHILDREN, opacity=0)
        self._graph_area = GraphArea(name='GraphArea', parent=self._graph_container, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self._transit_info_container = TransitInformationContainer(name='TransitInfoContainer', parent=self._graph_area, align=uiconst.CENTERRIGHT, height=60, width=500, top=30, padRight=10, buttonFunc=None)
        self._flux_labels = axislabels.AxisLabels(name='ExoPlanetsFluxLabels', parent=self._graph_area, align=uiconst.TOLEFT_NOPUSH, width=100, axis=self._flux_axis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1, maxFactor=0, textAlignment=uiconst.CENTERLEFT)
        self._consensus_labels = axislabels.AxisLabels(name='ConsensusLabels', parent=self._consensus_graph_area, align=uiconst.TORIGHT_NOPUSH, width=100, axis=self._consensus_vertical_axis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1, maxFactor=0, textAlignment=uiconst.CENTERRIGHT)
        self.set_fux_display_state(FluxDisplayState.RELATIVE)
        self._graph_area.AddAxis(orientation=axis.AxisOrientation.VERTICAL, axis=self._flux_axis, minFactor=1.0, maxFactor=0.0)
        self._graph_area.AddAxis(orientation=axis.AxisOrientation.HORIZONTAL, axis=self._time_axis)
        self._create_graph_from_data(self._graph_data)
        self.horizontalLines = Grid(parent=self._graph_area, axis=self._flux_axis, orientation=axis.AxisOrientation.VERTICAL, color=(1, 1, 1, 0.05), minFactor=1.0, maxFactor=0.0)
        self._consensus_lines = Grid(parent=self._consensus_graph_area, axis=self._consensus_vertical_axis, orientation=axis.AxisOrientation.VERTICAL, color=(1, 1, 1, 0.05), minFactor=1.0, maxFactor=0.0)

    def _setup_waiting_screen(self):
        self._audio_service.SendUIEvent(const.Sounds.MainImageLoadPlay)
        self._loading_wheel = LoadingWheel(name='LoadingWheel', parent=self, align=uiconst.CENTER)

    def _setup_mini_map_area(self):
        self._mini_map_area = Container(name='MiniMapArea', parent=self._graph_container, align=uiconst.TOBOTTOM, height=80)
        self._mini_map_area.pickState = uiconst.TR2_SPS_ON
        self._setup_zoom_mini_map()

    def _setup_zoom_mini_map(self):
        self._control_axis = self._time_axis_type(self.get_time_values(self._graph_data)[:1], dataRange=(self._time_axis.get_min_value(), self._time_axis.get_max_value()))
        self._category_axes.append(self._control_axis)
        self._control_axis.onChange.connect(self._set_time_axis_dirty)
        self._mini_map = MiniMap(name='MiniMap', parent=self._mini_map_area, align=uiconst.TOALL, controlAxis=self._control_axis, state=uiconst.UI_PICKCHILDREN)
        self._mini_map.slider.name = 'ExoPlanetsZoomSlider'
        self._mini_map.slider.beforeAxisUpdate.connect(self.lock_graph_updates)
        self._mini_map.slider.onSliderStart.connect(self.on_graph_movement)
        self._mini_map.slider.onSliderReleased.connect(self.on_graph_movement_stopped)
        self._mini_map.slider.onSliderWheel.connect(self._scroll_fade)
        self._mini_map.slider.pickState = uiconst.TR2_SPS_ON
        self._mini_graph = ExoPlanetsMiniGraph(name='MiniGraph', parent=self._mini_map_area, align=uiconst.TOALL, opacity=1, state=uiconst.UI_NORMAL)
        self._mini_graph.set_data(self._graph_data)
        self._mini_graph.set_tool(MagnifyingGlassTool(scaling_orientation=MagnifyingGlassScalingOrientation.HORIZONTAL, adjust_flux_zoom=False, on_click=lambda t1, t2, f1, f2: (self.zoom(t1, t2) if not self.is_folding() else None)))
        self.zoom(*self._control_axis.get_visible_range())

    def Close(self):
        if self._mini_map:
            self._control_axis.onChange.disconnect(self._set_time_axis_dirty)
            self._mini_map.slider.beforeAxisUpdate.disconnect(self.lock_graph_updates)
            self._mini_map.slider.onSliderStart.disconnect(self.on_graph_movement)
            self._mini_map.slider.onSliderReleased.disconnect(self.on_graph_movement_stopped)
            self._mini_map.slider.onSliderWheel.disconnect(self._scroll_fade)
        super(ExoPlanetsGraph, self).Close()

    def setup_result_graph(self, correct_intervals, missed_intervals, incorrect_intervals, interval_mapping):
        self._interval_mapping = interval_mapping
        self._correct_intervals = correct_intervals
        self._missed_intervals = missed_intervals
        self._incorrect_intervals = incorrect_intervals
        self._correct_point_indices, self._missed_point_indices, self._incorrect_point_indices = result.categorize_point_indices_to_result(self._graph_data, correct_intervals, missed_intervals, incorrect_intervals)
        self._show_result_graph()
        self._show_result_icon_graphs(correct_intervals, missed_intervals, incorrect_intervals)

    def _show_result_graph(self):
        self.clear_result_graph()
        if self.is_folding():
            points = [ self._graph_data[i] for i in self._fold_result_points_indices ]
            color = const.Colors.GREEN if self._fold_result_state == result.ResultStates.CORRECT else const.Colors.YELLOW
            self._correct_horizontal_axis, self._correct_graph = self._create_result_graph_components(points, color, points_size=3)
            uianimations.BlinkIn(self._correct_graph)
            return
        correct_points = [ self._graph_data[i] for i in self._correct_point_indices ]
        missed_points = [ self._graph_data[i] for i in self._missed_point_indices ]
        incorrect_points = [ self._graph_data[i] for i in self._incorrect_point_indices ]
        self._correct_horizontal_axis, self._correct_graph = self._create_result_graph_components(correct_points, const.Colors.GREEN)
        self._missed_horizontal_axis, self._missed_graph = self._create_result_graph_components(missed_points, const.Colors.YELLOW)
        self._incorrect_horizontal_axis, self._incorrect_graph = self._create_result_graph_components(incorrect_points, const.Colors.RED)
        self._is_result_shown = True
        uianimations.BlinkIn(self._correct_graph)
        uianimations.BlinkIn(self._missed_graph)
        uianimations.BlinkIn(self._incorrect_graph)

    def clear_result_graph(self):
        if self._correct_graph:
            self._correct_graph.Close()
        if self._missed_graph:
            self._missed_graph.Close()
        if self._incorrect_graph:
            self._incorrect_graph.Close()
        self._correct_horizontal_axis = None
        self._missed_horizontal_axis = None
        self._incorrect_horizontal_axis = None
        self._correct_graph = None
        self._missed_graph = None
        self._incorrect_graph = None

    def _create_result_graph_components(self, points, color, points_size = 4):
        time_values = self.get_time_values(points)
        flux_values = self.get_flux_values(points)
        category_axis = self._time_axis_type(time_values, dataRange=(self._time_axis.get_min_value(), self._time_axis.get_max_value()))
        category_axis.set_zoom(*self._control_axis.get_visible_range())
        if self.is_folding():
            category_axis.fold(self._fold_center, self._period_length)
        self._category_axes.append(category_axis)
        self._graph_area.AddAxis(orientation=axis.AxisOrientation.HORIZONTAL, axis=category_axis)
        graph = PointGraph(name='ResultGraph', parent=self._graph_area, categoryAxis=category_axis, valueAxis=self._flux_axis, values=flux_values, pointColor=color, pointSize=points_size, state=uiconst.UI_DISABLED, idx=0)
        return (category_axis, graph)

    def _show_result_icon_graphs(self, correct_intervals, missed_intervals, incorrect_intervals):
        axis1, graph1 = self._create_result_icon_graph_components(correct_intervals, 'res:/UI/Texture/classes/ProjectDiscovery/result_success.png', const.Colors.GREEN, localization.GetByLabel('UI/ProjectDiscovery/exoplanets/CorrectClickForInfo'))
        axis2, graph2 = self._create_result_icon_graph_components(missed_intervals, 'res:/UI/Texture/classes/ProjectDiscovery/result_missed.png', const.Colors.YELLOW, localization.GetByLabel('UI/ProjectDiscovery/exoplanets/MissedClickForInfo'))
        axis3, graph3 = self._create_result_icon_graph_components(incorrect_intervals, 'res:/UI/Texture/classes/ProjectDiscovery/result_fail.png', const.Colors.RED, localization.GetByLabel('UI/ProjectDiscovery/exoplanets/IncorrectClickForInfo'))
        self._result_icon_graphs = [graph1, graph2, graph3]

    def _get_intervals_centers(self, intervals):
        return [ interval[0] * 0.5 + interval[1] * 0.5 for interval in intervals ]

    def _create_result_icon_graph_components(self, intervals, icon_path, color, tooltip):
        interval_centers = self._get_intervals_centers(intervals)
        category_axis = self._time_axis_type(interval_centers, dataRange=(self._time_axis.get_min_value(), self._time_axis.get_max_value()))
        self._category_axes.append(category_axis)
        self._graph_area.AddAxis(orientation=axis.AxisOrientation.HORIZONTAL, axis=category_axis)
        graph = ResultIconGraph(name='ResultIconGraph', parent=self._graph_area, categoryAxis=category_axis, color=color, iconPath=icon_path, tooltipMessage=tooltip, transitIntervals=intervals, onClick=self._on_result_click, intervalMapping=self._interval_mapping)
        return (category_axis, graph)

    def _hide_icon_graphs(self, is_hidden = True):
        for graph in self._result_icon_graphs:
            graph.state = uiconst.UI_DISABLED if is_hidden else uiconst.UI_PICKCHILDREN
            animation = uianimations.BlinkOut if is_hidden else uianimations.BlinkIn
            animation(graph)

    def _on_result_click(self, minimum, maximum):
        self._hide_icon_graphs()

        def calibrate_in():
            self.clear_result_graph()
            self.calibrate_to_folded_mode(marker.get_center(), marker.get_period_length(), callback=lambda : self._show_result_graph() or sm.ScatterEvent('OnEnableDetrend') or sm.ScatterEvent('OnShowProjectDiscoveryResultBackButton'))

        self.hide_mini_map_zoom(True, duration=0.5)
        if (minimum, maximum) in self._interval_mapping:
            marker = self._interval_mapping[minimum, maximum]
            self._fold_result_points_indices, self._fold_result_state = result.get_intervals_points_indices_of_same_state(self._correct_intervals, self._missed_intervals, self._incorrect_intervals, (minimum, maximum), self._interval_mapping, self._graph_data)
            sm.ScatterEvent('OnDisplayTransitInformation', marker, state=self._fold_result_state)
            if len(marker.get_centers()) > 1:
                sm.ScatterEvent('OnDisableDetrend')
                self.reset_zoom(callback=calibrate_in)
                return
        else:
            sm.ScatterEvent('OnDisplayTransitInformation', None, epoch=round(0.5 * minimum + 0.5 * maximum - self._graph_data[0][0], 3))
        sm.ScatterEvent('OnShowProjectDiscoveryResultBackButton')
        self.zoom_animated(minimum - (maximum - minimum) * 2, maximum + (maximum - minimum) * 2, max_duration=0.5)

    def OnProjectDiscoveryResultBackButtonPressed(self, *args, **kwargs):
        self._hide_icon_graphs(False)
        if self.is_folding():
            self.calibrate_to_unfolded_mode(callback=lambda : self.show_mini_map_zoom(True, 0.5) or sm.ScatterEvent('OnDisplayTransitMarkers'))
        else:
            self.reset_zoom()
            self.show_mini_map_zoom(True, 0.5)
        sm.ScatterEvent('OnHideTransitInformation')

    def setup_consensus_graph(self, consensus_data, transit_markers):
        if not consensus_data:
            return
        time_values = []
        for min_time, max_time, value in consensus_data:
            time_values.append(min_time)
            time_values.append(max_time)

        uianimations.BlinkOut(self.horizontalLines, startVal=0.05, endVal=0.0)
        uianimations.BlinkIn(self._consensus_graph_area)
        self._consensus_time_axis = self._time_axis_type(time_values)
        self._consensus_graph_area.AddAxis(orientation=axis.AxisOrientation.VERTICAL, axis=self._consensus_vertical_axis, minFactor=1.0, maxFactor=0.0)
        self._consensus_graph_area.AddAxis(orientation=axis.AxisOrientation.HORIZONTAL, axis=self._consensus_time_axis)
        self._category_axes.append(self._consensus_time_axis)
        self._consensus_graph = ConsensusGraph(name='ConsensusGraph', parent=self._consensus_graph_area, categoryAxis=self._consensus_time_axis, valueAxis=self._consensus_vertical_axis, values=[ point[2] for point in consensus_data ], transitMarkers=transit_markers, onClick=lambda minimum, maximum: self.zoom_animated(minimum - (maximum - minimum) * 2, maximum + (maximum - minimum) * 2, max_duration=0.5))
        self._consensus_graph_area.opacity = 0
        uianimations.FadeIn(self._consensus_graph_area)
        self._consensus_graph.Animate(animations.AnimationType.GROW, animations.AnimationDynamics.RANDOM, 1.0)
        uianimations.FadeTo(self._graph_area, startVal=self._graph_area.opacity, endVal=0.5)

    def get_time_visible_range(self):
        return self._control_axis.get_visible_range()

    def reset_zoom(self, callback = None):
        if not self.is_zoom():
            invoke_callback(callback)
        else:
            self.zoom_animated(self._time_axis.get_min_value(), self._time_axis.get_max_value(), callback=callback)

    def zoom_animated(self, minimum_time, maximum_time, max_duration = 1.0, callback = None):
        minimum_time = min(max(minimum_time, self._graph_data[0][0]), self._graph_data[-1][0])
        maximum_time = min(max(maximum_time, self._graph_data[0][0]), self._graph_data[-1][0])
        start_zoom = self.get_time_visible_range()
        end_zoom = (minimum_time, maximum_time)
        if start_zoom == end_zoom:
            invoke_callback(callback)
            return
        self._desired_animation_zoom = (minimum_time, maximum_time)
        self._zoom_animation_callback = callback
        duration = zoom.get_zoom_animation_duration(start_zoom, end_zoom, max_duration=max_duration)
        self._is_zoom_animation = True
        self.state = uiconst.UI_DISABLED
        self._on_animation()
        uianimations.MorphVector2(self, '_zoom', self._zoom, end_zoom, duration, callback=self._after_zoom_animation)

    def _after_zoom_animation(self):
        self._is_zoom_animation = False
        min_time, max_time = self._desired_animation_zoom[0], self._desired_animation_zoom[1]
        self._desired_animation_zoom = None
        self.zoom(min_time, max_time)
        self.state = uiconst.UI_NORMAL
        self._on_animation_stopped()
        invoke_callback(self._zoom_animation_callback)
        self._zoom_animation_callback = None

    def _point_graph_toggle(self, *args):
        if self._main_graph:
            self._is_point_graph = not self._main_graph.get_show_status_of_point_graph()
            self._main_graph.set_show_status_of_point_graph(self._is_point_graph)
            self._main_graph.hide_point_graph() if not self._is_point_graph else self._main_graph.show_point_graph()

    def update_data(self, data, new_zoomed_range = None, adjust_zoom = True):
        super(ExoPlanetsGraph, self).update_data(data, new_zoomed_range, adjust_zoom)
        if not self._is_mini_map_hidden and not self.is_animation_running():
            self._mini_graph.update_data(data)

    def update_animated(self, data, callback = None):

        def update_callback():
            self._is_update_animation = False
            self.update_data(self._original_data)
            self._on_animation_stopped()
            invoke_callback(callback)

        self.lock_graph_updates()
        self._is_update_animation = True
        self._on_animation()
        self._original_data = data
        self._start_animation_data = binning.bin(self.get_graph_data(), self.animation_binning_fidelity)
        self._end_animation_data = binning.bin(data, self.animation_binning_fidelity)
        uianimations.MorphScalar(self, '_update_progression', 0, 1, 0.5, callback=update_callback)

    def clean_container(self):
        if self._tool:
            self._tooltip.SetParent(None)
        super(ExoPlanetsGraph, self).clean_container()
        self._consensus_graph = None
        self._consensus_graph_area = None
        self._consensus_time_axis = None
        self._consensus_vertical_axis = None
        self._is_result_shown = False
        self.clear_result_graph()

    def _set_time_axis_dirty(self, *args):
        self._is_time_axis_dirty = True

    def on_time_axis_changed(self, *args):
        self.lock_graph_updates()
        min_value, max_value = self.get_time_visible_range()
        self.zoom(min_value, max_value)
        self._is_time_axis_dirty = False

    def hide_mini_map_zoom(self, is_animate = False, duration = 1.0, callback = None):

        def animation_callback():
            self._mini_map.state = uiconst.UI_HIDDEN
            invoke_callback(callback)

        if is_animate:
            uianimations.FadeOut(self._mini_map, duration=duration, callback=animation_callback)
        else:
            animation_callback()

    def show_mini_map_zoom(self, is_animate = False, duration = 1.0, callback = None):

        def animation_callback():
            invoke_callback(callback)

        self._mini_map.SetState(uiconst.UI_NORMAL)
        self._mini_map.pickState = uiconst.TR2_SPS_CHILDREN
        if is_animate:
            uianimations.FadeIn(self._mini_map, duration=duration, callback=animation_callback)
        else:
            animation_callback()

    def fold_animated(self, center, period):

        def animation_callback():
            self._is_fold_animation = False
            self.state = uiconst.UI_NORMAL
            self.fold(center, period)
            self._on_animation_stopped()

        if self._is_folding:
            animated_center = self._reverse_engineer_center_fix(center, period)
        else:
            time_values = [ time for time, flux in self._graph_data ]
            min_time, max_time = time_values[0], time_values[-1]
            self._period_length = max_time - min_time
            self._fold_center = min_time + self._period_length / 2.0
            animated_center = self._fold_center
        if (self._fold_center, self._period_length) == (center, period):
            return
        self._is_fold_animation = True
        self._on_animation()
        self.state = uiconst.UI_DISABLED
        duration = self.get_fold_animation_time(animated_center)
        uianimations.MorphVector2(self, '_fold_variables', (self._fold_center, self._period_length), (animated_center, period), duration, callback=animation_callback)

    def get_fold_animation_time(self, fold_center):
        max_length = (self._time_axis.get_max_value() - self._time_axis.get_min_value()) / 2.0
        diff_center = math.fabs(fold_center - self._fold_center)
        return diff_center / max_length * FOLD_ANIMATION_MAX_TIME

    def calibrate_to_folded_mode(self, calibration_center, calibration_period, transit_selection = None, duration = 1.0, callback = None):

        def animation_callback():
            self._on_calibration_animation_ended(True, transit_selection, calibration_center, calibration_period, callback)

        if self.is_folding():
            invoke_callback(callback)
            return
        self._remove_transit_selections_not_in_list([transit_selection])
        if transit_selection and transit_selection.get_period_length():
            self._calibration_axis = self._transit_selection_graphs[0].category_axis
            self._calibration_marking_start_points = transit_selection.get_centers()
            self._calibration_marking_end_points = calibration.get_end_time_values(start_time_values=self._calibration_marking_start_points, center=calibration_center, period=calibration_period, min_time=min(self.get_time_values(self._graph_data)), max_time=max(self.get_time_values(self._graph_data)))
        self.state = uiconst.UI_DISABLED
        self._is_calibration_animation = True
        self._on_animation()
        self._original_data = self.get_graph_data()
        self._start_animation_data = binning.bin(self.get_graph_data(), self.animation_binning_fidelity)
        self._end_animation_data = calibration.get_end_data(self._start_animation_data, calibration_center, calibration_period)
        uianimations.MorphScalar(self, '_calibration_progression', 0, 1, duration=duration, callback=animation_callback)

    def calibrate_to_unfolded_mode(self, transit_selection = None, duration = 1.0, callback = None):

        def animation_callback():
            self._on_calibration_animation_ended(False, transit_selection, callback=callback)

        if not self.is_folding():
            invoke_callback(callback)
            return
        self.state = uiconst.UI_DISABLED
        self._is_calibration_animation = True
        self._on_animation()
        self._original_data = self.get_graph_data()
        self._end_animation_data = binning.bin(self.get_graph_data(), self.animation_binning_fidelity)
        self._start_animation_data = calibration.get_end_data(self._end_animation_data, self._fold_center, self._period_length)
        self._remove_transit_selections_not_in_list([transit_selection])
        if transit_selection and transit_selection.get_period_length():
            self._calibration_axis = self._transit_selection_graphs[0].category_axis
            self._calibration_marking_end_points = transit_selection.get_centers()
            self._calibration_marking_start_points = calibration.get_end_time_values(start_time_values=self._calibration_marking_end_points, center=transit_selection.get_center(), period=transit_selection.get_period_length(), min_time=min(self.get_time_values(self._graph_data)), max_time=max(self.get_time_values(self._graph_data)))
        self.unfold()
        self.update_data(self._start_animation_data)
        uianimations.MorphScalar(self, '_calibration_progression', 0, 1, duration=duration, callback=animation_callback)

    def _on_calibration_animation_ended(self, is_folding, transit_selection, center = None, period = None, callback = None):
        if transit_selection:
            points = self._calibration_marking_start_points if is_folding else self._calibration_marking_end_points
            self._calibration_axis.set_data_points(points)
            self._calibration_axis = None
            self._calibration_marking_start_points = []
            self._calibration_marking_end_points = []
        self._is_calibration_animation = False
        self.update_data(self._original_data)
        if is_folding:
            self.fold(center, period)
        self.state = uiconst.UI_NORMAL
        self._on_animation_stopped()
        invoke_callback(callback)

    def _on_animation(self):
        self._hide_graph_labels()
        self.on_graph_movement()
        if self._is_result_shown:
            self.clear_result_graph()

    def _on_animation_stopped(self):
        if not self.is_animation_running():
            self._show_graph_labels()
            self.on_graph_movement_stopped()
            if self._is_result_shown:
                self._show_result_graph()

    def _hide_graph_labels(self):
        uianimations.FadeOut(self._flux_labels, duration=0.1)
        uianimations.FadeOut(self._time_labels, duration=0.1)

    def _show_graph_labels(self):
        uianimations.FadeIn(self._flux_labels, duration=0.1)
        uianimations.FadeIn(self._time_labels, duration=0.1)

    def _reverse_engineer_center_fix(self, next_center, period_length):
        min_visible, max_visible = self._time_axis.get_visible_range()
        time_values = self.get_time_values(self._graph_data)
        min_time, max_time = min(time_values), max(time_values)
        if next_center < min_visible:
            while next_center < max_time:
                next_center += period_length

        elif next_center > max_visible:
            while next_center > min_time:
                next_center -= period_length

        return next_center

    def set_fux_display_state(self, state):
        self._flux_labels.Clear()
        if self._flux_axis:
            if state == FluxDisplayState.RELATIVE:
                flux_values = self.get_flux_values(self._graph_data)
                self._flux_axis.set_relative_flux_active(flux_values)
            else:
                self._flux_axis.set_actual_flux_active()

    def display_transit_markers(self, transit_selections, mini_map_transit_markers = None):
        super(ExoPlanetsGraph, self).display_transit_markers(transit_selections)
        if not mini_map_transit_markers:
            mini_map_transit_markers = []
        if self._mini_graph:
            self._mini_graph.display_transit_markers(mini_map_transit_markers)

    def is_animation_running(self):
        is_other_animation_running = self._is_calibration_animation or self._is_fold_animation or self._is_update_animation or self._is_zoom_animation
        return is_other_animation_running

    def unlock_graph_updates(self):
        super(ExoPlanetsGraph, self).unlock_graph_updates()
        if self._mini_graph:
            self._mini_graph.unlock_graph_updates()

    def zoom(self, *args, **kwargs):
        if self._desired_animation_zoom and self._zoom_replicate_count > 5:
            self.StopAnimations()
            invoke_callback(self._after_zoom_animation)
            return
        super(ExoPlanetsGraph, self).zoom(*args, **kwargs)

    @property
    def _calibration_progression(self):
        return self._m_calibration_progression

    @_calibration_progression.setter
    def _calibration_progression(self, value):
        self.lock_graph_updates()
        self._m_calibration_progression = value
        data = linearly_interpolate_data(self._start_animation_data, self._end_animation_data, value)
        self.update_data(data)
        if self._calibration_marking_start_points:
            marking = [ (1 - value) * start_time + value * end_time for start_time, end_time in izip(self._calibration_marking_start_points, self._calibration_marking_end_points) ]
            self._calibration_axis.set_data_points(marking)

    @property
    def _zoom(self):
        return self._zoomed_range

    @_zoom.setter
    def _zoom(self, zoom_range):
        self.zoom(*zoom_range)

    @property
    def _fold_variables(self):
        return (self._fold_center, self._period_length)

    @_fold_variables.setter
    def _fold_variables(self, _center_and_period):
        self.fold(*_center_and_period)

    @property
    def _update_progression(self):
        return self._m_update_progression

    @_update_progression.setter
    def _update_progression(self, t):
        self._m_update_progression = t
        data = linearly_interpolate_data(self._start_animation_data, self._end_animation_data, t)
        self.update_data(data)


class FluxDisplayState(object):
    RELATIVE = 0
    ACTUAL = 1


def invoke_callback(callback, *args, **kwargs):
    if callable(callback):
        callback(*args, **kwargs)


def linearly_interpolate_data(start_data, end_data, t):
    return [ geo2.Lerp(start, end, t) for start, end in izip(start_data, end_data) ]


def consensus_tick_filter(tick):
    return tick <= 1.0


def consensus_label_format(tick):
    return '%s%%' % int(tick * 100)
