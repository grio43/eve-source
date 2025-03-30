#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphs\consensusgraph.py
from carbonui.primitives.polygon import Polygon
from carbonui.uicore import uicore
from carbonui.uianimations import animations as uianimations
import carbonui.const as uiconst
from carbonui.graphs.axis import AxisOrientation
from projectdiscovery.client.projects.exoplanets.graphs import animations
import geo2
import localization

class ConsensusGraph(Polygon):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(ConsensusGraph, self).ApplyAttributes(attributes)
        self._category_axis = attributes.get('categoryAxis')
        self._value_axis = attributes.get('valueAxis')
        self._values = attributes.get('values')
        self._positive_color = attributes.get('positiveColor', (0, 0.8, 0, 1))
        self._neutral_color = attributes.get('neutralColor', (1, 1, 0, 1))
        self._hover_color = attributes.get('hoverColor', (1, 1, 1, 1))
        self._on_click = attributes.get('onClick')
        self._transit_markings = self.get_markings_from_markers(attributes.get('transitMarkers', []))
        if callable(self._on_click):
            self.cursor = uiconst.UICURSOR_MAGNIFIER
        self._animation = None
        self._vertices = None
        self._locked = False
        self._dirty = False
        self._time_ranges = []
        self._hover_index = None
        self._prev_color = None
        self._tooltip_rectangle = None
        self._category_axis.onChange.connect(self._axis_changed)
        self._value_axis.onChange.connect(self._axis_changed)
        self._build()

    def Animate(self, animationType, animationDynamics, duration):
        self.CancelAnimation()
        self._animation = animations.CreateAnimation(self, self._category_axis, self._value_axis, AxisOrientation.VERTICAL, animationType, animationDynamics, duration, 2)

    def CancelAnimation(self, applyLastFrame = True):
        self.StopAnimations()
        self.opacity = 1.0
        if self._animation:
            self._animation.Cancel(applyLastFrame)
            self._animation = None

    def Close(self):
        self.CancelAnimation(False)
        super(ConsensusGraph, self).Close()
        self._category_axis.onChange.disconnect(self._axis_changed)
        self._value_axis.onChange.disconnect(self._axis_changed)

    def LockGraphUpdates(self):
        self._locked = True

    def UnlockGraphUpdates(self):
        if self._locked:
            self._locked = False
            if self._dirty:
                self._rescale()

    def _axis_changed(self, _):
        if self._locked:
            self._dirty = True
        else:
            self._rescale()

    def _build(self):
        dpi_scaling = uicore.desktop.dpiScaling
        axis_zero = self._value_axis.MapToViewport(0) * dpi_scaling
        positions = []
        colors = []
        triangles = []
        self._time_ranges = self._get_time_value_pairs(self._category_axis.get_actual_data_points())
        mapped_paired_values = self._get_time_value_pairs(list(self._category_axis.MapDataPointsToViewport()))
        for i, ((min_x, max_x), y, value) in enumerate(zip(mapped_paired_values, self._value_axis.MapSequenceToViewport(self._values), self._values)):
            min_x *= dpi_scaling
            max_x *= dpi_scaling
            y *= dpi_scaling
            positions.append((min_x, y))
            positions.append((max_x, y))
            positions.append((max_x, axis_zero))
            positions.append((min_x, axis_zero))
            alpha = 0.2 if i % 2 == 0 else 0.3
            if self._is_player_in_interval(self._time_ranges[i]):
                color = (0,
                 1,
                 1,
                 alpha)
            else:
                color = self._get_value_color(value, alpha)
            colors.append(color)
            colors.append(color)
            colors.append(color)
            colors.append(color)
            triangles.append((4 * i, 4 * i + 1, 4 * i + 2))
            triangles.append((4 * i + 2, 4 * i + 3, 4 * i))

        self.renderObject.AppendVertices(positions, None, colors)
        self.renderObject.AppendTriangles(triangles)
        self.width = max((x[0] for x in positions))
        self.height = max((x[1] for x in positions))

    def _rescale(self):
        if not self.renderObject:
            return
        dpi_scaling = uicore.desktop.dpiScaling
        axis_zero = self._value_axis.MapToViewport(0) * dpi_scaling
        positions = []
        mapped_paired_values = self._get_time_value_pairs(list(self._category_axis.MapDataPointsToViewport()))
        for i, ((min_x, max_x), y) in enumerate(zip(mapped_paired_values, self._value_axis.MapSequenceToViewport(self._values))):
            min_x *= dpi_scaling
            max_x *= dpi_scaling
            y *= dpi_scaling
            positions.append((min_x, y))
            positions.append((max_x, y))
            positions.append((max_x, axis_zero))
            positions.append((min_x, axis_zero))

        self._adjust_graph_fade()
        self.renderObject.SetVertices(positions)

    def _adjust_graph_fade(self):
        if self.is_zoomed_on_column():
            if self.state == uiconst.UI_NORMAL:
                self.state = uiconst.UI_DISABLED
                uianimations.FadeTo(self, 1, 0, duration=0.3)
        elif self.opacity != 1 and self.state == uiconst.UI_DISABLED:
            self.state = uiconst.UI_NORMAL
            uianimations.FadeTo(self, self.opacity, 1.0)

    def is_zoomed_on_column(self):
        current_range = self._category_axis.get_visible_range()
        current_range = (round(current_range[0], 4), round(current_range[1], 4))
        left_ranges = [ time_range for time_range in self._time_ranges if time_range[0] <= current_range[0] <= time_range[1] ]
        right_ranges = [ time_range for time_range in self._time_ranges if time_range[0] <= current_range[1] <= time_range[1] ]
        if left_ranges and right_ranges:
            return left_ranges == right_ranges
        return False

    def _get_time_value_pairs(self, time_values):
        paired = []
        for i in xrange(len(time_values)):
            if i % 2 != 0:
                continue
            paired.append((time_values[i], time_values[i + 1]))

        return paired

    def _get_value_color(self, value, color_alpha = 1.0):
        t = max(min(value, 1), 0)
        color = geo2.Lerp(self._neutral_color, self._positive_color, t)
        return (color[0],
         color[1],
         color[2],
         color_alpha)

    def OnMouseEnter(self, *args):
        self._on_column_change(self._get_hover_index())

    def OnMouseMove(self, *args):
        index = self._get_hover_index()
        if self._hover_index != index:
            self._on_column_change(index)

    def OnMouseExit(self, *args):
        self._remove_hover_color()

    def OnClick(self, *args):
        if callable(self._on_click) and self._hover_index is not None:
            time_range = self._time_ranges[self._hover_index]
            self._on_click(*time_range)

    def _get_hover_index(self):
        graph_coordinate = uicore.uilib.x - self.GetAbsoluteLeft()
        time_value = self._category_axis.MapFromViewport(graph_coordinate)
        time_value = self._category_axis.map_normalized_value_to_actual_value(time_value)
        for i, (min_time, max_time) in enumerate(self._time_ranges):
            if min_time <= time_value <= max_time:
                return i

    def _set_hover_color(self):
        if self._hover_index is None:
            return
        offset = self._hover_index * 4
        self._prev_color = self.renderObject.vertices[offset].color
        for each in range(4):
            self.renderObject.vertices[offset + each].color = self._hover_color

        self.renderObject.SetDirty()

    def _remove_hover_color(self):
        if self._hover_index is None:
            return
        offset = self._hover_index * 4
        for each in range(4):
            self.renderObject.vertices[offset + each].color = self._prev_color

        self.renderObject.SetDirty()

    def _on_column_change(self, new_index):
        self._remove_hover_color()
        self._hover_index = new_index
        self._set_hover_color()
        self._set_hint()

    def _set_hint(self):
        if self._hover_index:
            self.SetHint(None)
            normalized_percent = self._values[self._hover_index]
            percentage = round(normalized_percent * 100, 1)
            self.SetHint(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/ConsensusBarTooltip', playersmarkinghere=percentage))

    def GetTooltipPosition(self):
        dpiScaling = uicore.desktop.dpiScaling
        offset = self._hover_index * 4
        tl = self.renderObject.vertices[offset].position
        br = self.renderObject.vertices[offset + 2].position
        pos = self.GetAbsolutePosition()
        self._tooltip_rectangle = (tl[0] / dpiScaling + pos[0],
         tl[1] / dpiScaling + pos[1],
         br[0] / dpiScaling - tl[0] / dpiScaling,
         br[1] / dpiScaling - tl[1] / dpiScaling)
        return self._tooltip_rectangle

    def get_markings_from_markers(self, markers):
        return sum([ marker.get_centers() for marker in markers ], [])

    def _is_player_in_interval(self, interval):
        return any([ interval[0] <= marking <= interval[1] for marking in self._transit_markings ])
