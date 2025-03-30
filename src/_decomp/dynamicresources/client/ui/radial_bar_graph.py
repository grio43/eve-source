#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ui\radial_bar_graph.py
from __future__ import division
import math
import chroma
import eveui
import threadutils
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.polygon import Polygon

class RadialBarGraph(Container):

    def __init__(self, parent, align, data, radius = 120, inner_radius = 100, start_angle = 0.0, end_angle = 360.0, progress = 1.0, color = (1.0, 1.0, 1.0, 1.0), background_color = (1.0, 1.0, 1.0, 0.3), bar_gap_ratio = 2.5, value_radius_modifier = 1.0):
        self._data = data
        self._radius = eveui.scale_dpi(radius)
        self._inner_radius = eveui.scale_dpi(inner_radius)
        self._start_angle = start_angle
        self._end_angle = end_angle
        self._progress = progress
        self._color = chroma.Color.from_any(color).rgba
        self._background_color = chroma.Color.from_any(background_color).rgba
        self._bar_gap_ratio = bar_gap_ratio
        self._value_radius_modifier = value_radius_modifier
        super(RadialBarGraph, self).__init__(parent=parent, align=align, height=self._radius * 2, width=self._radius * 2)
        self._polygon = Polygon(parent=self, align=uiconst.CENTER)
        self._need_redraw = True
        self._start_frame_update_loop()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._need_redraw = True

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, radius):
        if self._inner_radius != radius:
            self._inner_radius = radius
            self._need_redraw = True

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, radius):
        if self.radius != radius:
            self._radius = radius
            self._need_redraw = True
            size = math.ceil(self._radius * 2.0)
            if size % 2 == 1:
                size += 1
            self.width = size
            self.height = size

    @property
    def start_angle(self):
        return self._start_angle

    @start_angle.setter
    def start_angle(self, angle):
        if self._start_angle != angle:
            self._start_angle = angle
            self._need_redraw = True

    @property
    def end_angle(self):
        return self._end_angle

    @end_angle.setter
    def end_angle(self, angle):
        if self._end_angle != angle:
            self._end_angle = angle
            self._need_redraw = True

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, progress):
        if self._progress != progress:
            old_progress = self._progress
            self._progress = progress
            bar_count = len(self._data)
            if int(bar_count * old_progress) != int(bar_count * self._progress):
                self._need_redraw = True

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        new_color = chroma.Color.from_any(color).rgba
        if new_color != self._color:
            self._color = new_color
            self._need_redraw = True

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        new_color = chroma.Color.from_any(color).rgba
        if new_color != self._background_color:
            self._background_color = new_color
            self._need_redraw = True

    @property
    def bar_gap_ratio(self):
        return self._bar_gap_ratio

    @bar_gap_ratio.setter
    def bar_gap_ratio(self, bar_gap_ratio):
        if self._bar_gap_ratio != bar_gap_ratio:
            self._bar_gap_ratio = bar_gap_ratio
            self._need_redraw = True

    @property
    def value_radius_modifier(self):
        return self._value_radius_modifier

    @value_radius_modifier.setter
    def value_radius_modifier(self, modifier):
        if self._value_radius_modifier != modifier:
            self._value_radius_modifier = modifier
            self._need_redraw = True

    def _draw(self):
        value_max = max(self.data)
        normalized_data = [ v / value_max for v in self.data ]
        bar_height_max = self._radius - self._inner_radius
        bar_count = len(normalized_data)
        bar_step_angle = abs(self._end_angle - self._start_angle) / bar_count
        gap_sweep = bar_step_angle / (self._bar_gap_ratio + 1.0)
        start_angle = self._start_angle - 90.0
        segment_count = max(1, 60 // len(normalized_data))
        color = self.color
        first_background_bar = round(self.progress * bar_count)
        all_vertices = []
        all_colors = []
        all_triangles = []
        for i, value in enumerate(normalized_data):
            if i == first_background_bar:
                color = self.background_color
            vertices, colors, triangles = _create_arc_polygon(inner_radius=self._inner_radius, outer_radius=self._radius - (1.0 - value) * self._value_radius_modifier * bar_height_max, segments=segment_count, color=color, start_angle=start_angle + bar_step_angle * i, end_angle=start_angle + bar_step_angle * (i + 1) - gap_sweep)
            vertex_offset = len(all_vertices)
            all_vertices.extend(vertices)
            all_colors.extend(colors)
            all_triangles.extend(((a + vertex_offset, b + vertex_offset, c + vertex_offset) for a, b, c in triangles))

        self._polygon.AppendVertices(positions=all_vertices, colors=all_colors, transform=None)
        self._polygon.SetTriangles(all_triangles)

    def _redraw(self):
        self._polygon.Flush()
        self._draw()

    @threadutils.threaded
    def _start_frame_update_loop(self):
        while not self.destroyed:
            if self._need_redraw:
                self._redraw()
                self._need_redraw = False
            eveui.wait_for_next_frame()


def _create_arc_polygon(inner_radius, outer_radius, start_angle, end_angle, color = (1.0, 1.0, 1.0, 1.0), segments = 10, feather = 1.0):
    vertices = []
    colors = []
    triangles = []
    total_sweep = abs(end_angle - start_angle)
    segment_sweep = total_sweep / segments
    for i in xrange(segments + 1):
        a = math.radians(start_angle + i * segment_sweep)
        x = math.cos(a)
        y = math.sin(a)
        vertices.append((x * inner_radius, y * inner_radius))
        vertices.append((x * outer_radius, y * outer_radius))
        colors.extend((color, color))

    for i in xrange(segments * 2):
        triangles.append((i, i + 1, i + 2))

    shift = len(vertices)
    fade_color = (color[0],
     color[1],
     color[2],
     0.0)
    inner_circumference = 2.0 * math.pi * inner_radius
    inner_px_per_deg = inner_circumference * (total_sweep / 360.0) / total_sweep
    inner_feather_angle = feather / inner_px_per_deg
    outer_circumference = 2.0 * math.pi * outer_radius
    outer_px_per_deg = outer_circumference * (total_sweep / 360.0) / total_sweep
    outer_feather_angle = feather / outer_px_per_deg
    radius_inner_feather = inner_radius - feather
    radius_outer_feather = outer_radius + feather
    for i in xrange(segments + 1):
        if i == 0:
            inner_angle = math.radians(start_angle - inner_feather_angle)
            outer_angle = math.radians(start_angle - outer_feather_angle)
        elif i == segments:
            inner_angle = math.radians(start_angle + i * segment_sweep + inner_feather_angle)
            outer_angle = math.radians(start_angle + i * segment_sweep + outer_feather_angle)
        else:
            inner_angle = outer_angle = math.radians(start_angle + i * segment_sweep)
        vertices.extend([(math.cos(inner_angle) * radius_inner_feather, math.sin(inner_angle) * radius_inner_feather), (math.cos(outer_angle) * radius_outer_feather, math.sin(outer_angle) * radius_outer_feather)])
        colors.extend((fade_color, fade_color))

    for i in xrange(segments * 2):
        triangles.append((i, shift + i, shift + i + 2))
        triangles.append((shift + i + 2, i + 2, i))

    vertex_count = len(vertices)
    triangles.append((0, 1, shift))
    triangles.append((shift, shift + 1, 1))
    triangles.append((shift - 2, shift - 1, vertex_count - 2))
    triangles.append((vertex_count - 2, vertex_count - 1, shift - 1))
    return (vertices, colors, triangles)
