#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphtools\magnifyingglasstool.py
from carbonui.graphs import axis
from carbonui.graphs.graph import GraphArea
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from eve.client.script.ui.control.themeColored import FrameThemeColored
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from projectdiscovery.client.projects.exoplanets.graphs.exoplanetsbasegraph import ExoPlanetsGraphContainer
from projectdiscovery.client.projects.exoplanets.graphtools.basetool import BaseTool
from carbonui.uicore import uicore
from eve.client.script.ui.control import tooltips
import carbonui.const as uiconst
import localization

def get_constraint_range(mouse_value, visible_range, ratio):
    zoom_width = (visible_range[1] - visible_range[0]) * ratio
    half_zoom_width = zoom_width * 0.5
    minimum, maximum = mouse_value - half_zoom_width, mouse_value + half_zoom_width
    if minimum < visible_range[0]:
        return (visible_range[0], visible_range[0] + zoom_width)
    if maximum > visible_range[1]:
        return (visible_range[1] - zoom_width, visible_range[1])
    return (minimum, maximum)


class MagnifyingGlassScalingOrientation(object):
    HORIZONTAL = 0
    VERTICAL = 1


class MagnifyingGlassPosition(object):
    ABOVE = 0
    BELOW = 1


class MagnifyingGlassTool(BaseTool):

    def __init__(self, min_flux_ratio = 0.2, min_time_ratio = 0.03, max_time_ratio = 0.25, time_ratio = 0.1, position = MagnifyingGlassPosition.ABOVE, scaling_orientation = MagnifyingGlassScalingOrientation.VERTICAL, adjust_flux_zoom = True, on_click = None, *args, **kwargs):
        self._tooltip = None
        self._max_time_ratio = max_time_ratio
        self._min_time_ratio = min_time_ratio
        self._max_flux_ratio = 1.0
        self._min_flux_ratio = min_flux_ratio
        self._flux_ratio = 0.5 if scaling_orientation == MagnifyingGlassScalingOrientation.VERTICAL else self._max_flux_ratio
        self._time_ratio = time_ratio
        self._x, self._y = (0, 0)
        self._position = position
        self._scaling_orientation = scaling_orientation
        self._adjust_flux_zoom = adjust_flux_zoom
        self._on_click = on_click
        self._is_hovering_over_graph = False
        super(MagnifyingGlassTool, self).__init__(*args, **kwargs)

    def get_tool_tip_object(self):
        self._tooltip = MagnifyingGlassTooltip(name='MagnifyingGlassToolTip', graph=self._graph)
        return self._tooltip

    def on_click(self, horizontal_mouse_value, vertical_mouse_value):
        if callable(self._on_click):
            min_time, max_time = self._get_time_range(horizontal_mouse_value)
            min_flux, max_flux = self._get_flux_range(vertical_mouse_value)
            self._on_click(min_time, max_time, min_flux, max_flux)

    def on_mouse_enter(self, horizontal_mouse_value, vertical_mouse_value):
        self._is_hovering_over_graph = True
        self._set_tool_cursor()
        self._x, self._y = horizontal_mouse_value, vertical_mouse_value
        self._show_and_update_tooltip(horizontal_mouse_value, vertical_mouse_value)

    def on_mouse_move(self, horizontal_mouse_value, vertical_mouse_value):
        self._x, self._y = horizontal_mouse_value, vertical_mouse_value
        self._show_and_update_tooltip(horizontal_mouse_value, vertical_mouse_value)

    def on_mouse_hover(self, horizontal_mouse_value, vertical_mouse_value):
        left, top, width, height = self._get_zoom_screen_position(horizontal_mouse_value, vertical_mouse_value)
        self._tooltip.update_tooltip_position(left, top, self._position)

    def on_mouse_exit(self, horizontal_mouse_value, vertical_mouse_value):
        self._is_hovering_over_graph = False
        self._tooltip.hide()
        self._remove_tool_cursor()

    def on_scroll(self, scroll_amount):
        amount = 0.03 if scroll_amount >= 0 else -0.03
        if self._scaling_orientation == MagnifyingGlassScalingOrientation.VERTICAL:
            self._flux_ratio = max(min(self._max_flux_ratio, self._flux_ratio + amount), self._min_flux_ratio)
        else:
            self._time_ratio = max(min(self._max_time_ratio, self._time_ratio + amount), self._min_time_ratio)
        self._show_and_update_tooltip(self._x, self._y)

    def _get_zoom_screen_width(self):
        if self._tooltip:
            return self._graph.map_time_value_to_screen_value(self._graph.get_time_visible_range()[1]) * self._time_ratio

    def _get_zoom_screen_height(self):
        if self._tooltip:
            return self._graph.map_flux_value_to_screen_value(self._graph.get_flux_visible_range()[0]) * self._flux_ratio

    def _get_zoom_screen_position(self, horizontal_mouse_value, vertical_mouse_value):
        time_zoom_range = self._get_time_range(horizontal_mouse_value)
        flux_zoom_range = self._get_flux_range(vertical_mouse_value)
        width = self._get_zoom_screen_width()
        height = self._get_zoom_screen_height()
        left = self._graph.map_time_value_to_screen_value(time_zoom_range[0])
        top = self._graph.map_flux_value_to_screen_value(flux_zoom_range[1])
        return (left,
         top,
         width,
         height)

    def _show_and_update_tooltip(self, horizontal_mouse_value, vertical_mouse_value):
        left, top, width, height = self._get_zoom_screen_position(horizontal_mouse_value, vertical_mouse_value)
        min_time, max_time = self._get_time_range(horizontal_mouse_value)
        min_flux, max_flux = self._get_flux_range(vertical_mouse_value) if self._adjust_flux_zoom else (None, None)
        self._tooltip.show()
        self._tooltip.update_zoom_container_width(width)
        self._tooltip.update_zoom_container_height(height)
        self._tooltip.update_tooltip_position(left, top, self._position)
        self._tooltip.zoom(min_time, max_time, min_flux, max_flux)

    def on_tool_set(self):
        if self._is_hovering_over_graph:
            self._set_tool_cursor()

    def on_tool_unset(self):
        self._is_hovering_over_graph = False
        self._remove_tool_cursor()
        self._graph.tooltipPanelClassInfo = None

    def _remove_tool_cursor(self):
        uicore.uilib.SetCursor(uiconst.UICURSOR_DEFAULT)

    def _set_tool_cursor(self):
        uicore.uilib.SetCursor(uiconst.UICURSOR_MAGNIFIER)

    def _get_time_range(self, horizontal_mouse_value):
        return get_constraint_range(horizontal_mouse_value, self._graph.get_time_visible_range(), self._time_ratio)

    def _get_flux_range(self, vertical_mouse_value):
        return get_constraint_range(vertical_mouse_value, self._graph.get_flux_visible_range(), self._flux_ratio)


class MagnifyingGlassTooltip(Container):

    def ApplyAttributes(self, attributes):
        super(MagnifyingGlassTooltip, self).ApplyAttributes(attributes)
        self._is_shown = False
        self._graph = attributes.get('graph')
        self._tooltip_move_position = None
        self._zoom = None
        self._setup_layout()

    def _setup_layout(self):
        self._zoom_container = Container(name='ZoomContainer', parent=self, align=uiconst.TOPLEFT, width=100, height=100, opacity=0)
        FrameThemeColored(bgParent=self._zoom_container, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self._construct_tooltip_wrapper()

    def _construct_tooltip_wrapper(self):
        if self._graph:
            self._graph.tooltipPanelClassInfo = MagnifierGlassTooltipWrapper(self._graph, self._get_zoom)

    def update_tooltip_position(self, left, top, position):
        self._zoom_container.left = left
        self._zoom_container.top = top
        if self._graph.tooltipPanelClassInfo and hasattr(self._graph.tooltipPanelClassInfo, 'tooltipPanel') and self._graph.tooltipPanelClassInfo.tooltipPanel:
            self._tooltip_move_position = self._get_tooltip_move_position(position)
            self._graph.tooltipPanelClassInfo.tooltipPanel.backgroundFrame.UpdatePointerPosition(self._get_pointer_direction(position))
            self._graph.tooltipPanelClassInfo.tooltipPanel.SetPosition(*self._tooltip_move_position)

    def _get_tooltip_move_position(self, position):
        left = self._zoom_container.GetAbsoluteLeft() - self._graph.tooltipPanelClassInfo.tooltipPanel.width / 2
        left += self._zoom_container.width / 2
        top = self._zoom_container.GetAbsoluteTop()
        top += self._zoom_container.height + 9 if position == MagnifyingGlassPosition.BELOW else -(self._graph.tooltipPanelClassInfo.tooltipPanel.height + 9)
        return (left, top)

    def _get_pointer_direction(self, position):
        if position == MagnifyingGlassPosition.BELOW:
            return uiconst.POINT_TOP_2
        return uiconst.POINT_BOTTOM_2

    def update_zoom_container_width(self, width):
        self._zoom_container.width = width

    def update_zoom_container_height(self, height):
        self._zoom_container.height = height

    def show(self):
        if not self._is_shown:
            self._is_shown = True
            animations.FadeIn(self._zoom_container, duration=0.25)

    def hide(self):
        if self._is_shown:
            self._is_shown = False
            animations.FadeOut(self._zoom_container, duration=0.25)

    def zoom(self, min_time, max_time, min_flux, max_flux):
        self._zoom = (min_time,
         max_time,
         min_flux,
         max_flux)
        if self._graph.tooltipPanelClassInfo:
            self._graph.tooltipPanelClassInfo.zoom(min_time, max_time, min_flux, max_flux)

    def _get_zoom(self):
        return self._zoom


class MagnifierGlassTooltipWrapper(TooltipBaseWrapper):

    def __init__(self, graph, get_zoom_func, *args, **kwargs):
        super(MagnifierGlassTooltipWrapper, self).__init__(*args, **kwargs)
        self._graph = graph
        self.tooltipPanel = None
        self._tooltip_graph = None
        self._get_zoom = get_zoom_func

    def CreateTooltip(self, parent, owner, idx):
        self._tooltip_graph = None
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_DISABLED)
        self.tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/MagnifyingGlass'), bold=True, cellPadding=(0, 5, 0, 5), wrapWidth=300)
        image_container = Container(width=300, height=300, align=uiconst.TOPLEFT, clipChildren=True)
        FrameThemeColored(bgParent=image_container, colorType=uiconst.COLORTYPE_UIHILIGHT)
        inner_image_container = Container(parent=image_container, width=298, height=298, align=uiconst.CENTER, clipChildren=True)
        graph = MagnifierGlassGraph(name='TooltipGraph', parent=inner_image_container, align=uiconst.TOALL, opacity=1, startUpdateLoop=False, state=uiconst.UI_DISABLED)
        graph.set_data(self._graph.get_graph_data())
        graph.display_transit_markers(self._graph.get_displayed_transit_markers())
        if self._graph.is_folding():
            graph.fold(self._graph.folding_center, self._graph.folding_period)
            graph.unlock_graph_updates()
        if self._get_zoom():
            graph.zoom(*self._get_zoom())
        self.tooltipPanel.AddCell(image_container, cellPadding=(0, 5, 0, 5))
        self._tooltip_graph = graph
        return self.tooltipPanel

    def zoom(self, min_time, max_time, min_flux, max_flux):
        if self._tooltip_graph:
            self._tooltip_graph.zoom(min_time, max_time, min_flux, max_flux)
            self._tooltip_graph.unlock_graph_updates()


class MagnifierGlassGraph(ExoPlanetsGraphContainer):
    default_is_point_graph = False

    def _setup_layout(self):
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
