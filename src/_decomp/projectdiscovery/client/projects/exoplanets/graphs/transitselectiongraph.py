#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphs\transitselectiongraph.py
import trinity
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from carbonui.uianimations import animations
from carbonui.uicore import uicore

class TransitSelectionGraph(VectorLineTrace):
    __notifyevents__ = ['OnProjectDiscoveryMarkerDim']
    default_lineColor = (1.0, 1.0, 1.0, 1.0)
    default_spriteEffect = trinity.TR2_SFX_COPY
    default_lineWidth = 1
    default_texturePath = 'res:/UI/Texture/classes/Exoplanets/Marker/marker_5.png'
    default_textureWidth = 23

    def ApplyAttributes(self, attributes):
        VectorLineTrace.ApplyAttributes(self, attributes)
        self._category_axis = attributes['categoryAxis']
        self._value_axis = attributes['valueAxis']
        self.lineColor = attributes.get('lineColor', self.default_lineColor)
        self._transit_selection = attributes.get('transitSelection')
        self._vertices = None
        self._locked = False
        self._dirty = False
        self._is_destroyed = False
        self._category_axis.onChange.connect(self._axis_changed)
        self._value_axis.onChange.connect(self._axis_changed)
        if self._transit_selection:
            self._transit_selection.on_change.connect(self._update_axis)
        self.renderObject.AppendVertices(self._get_vertices(), self._get_transform(), self.lineColor)
        animations.BlinkIn(self)
        sm.RegisterNotify(self)

    def LockGraphUpdates(self):
        self._locked = True

    def UnlockGraphUpdates(self):
        if self._locked:
            self._locked = False
            if self._dirty:
                self._rescale()

    def _update_axis(self):
        self.LockGraphUpdates()
        self._category_axis.set_data_points(self._transit_selection.get_centers())

    def _axis_changed(self, _):
        if self._locked:
            self._dirty = True
        else:
            self._rescale()

    def _rescale(self):
        if not self.renderObject:
            return
        self._dirty = False
        vertices = self._get_vertices()
        diff = len(vertices) - len(self.renderObject.vertices)
        if diff == 0:
            self.renderObject.SetVertices(vertices, self._get_transform(), self.lineColor)
        else:
            self.Flush()
            self.renderObject.AppendVertices(vertices, self._get_transform(), self.lineColor)

    def _get_vertices(self):
        categories = self._category_axis.GetDataPoints()
        is_top = True
        minimum, maximum = self._get_vertical_minimum_maximum_values()
        vertices = []
        fix_length = self._get_texture_fix_length()
        prev_value = None
        for value in categories:
            y1 = maximum if is_top else minimum
            y2 = minimum if is_top else maximum
            if value == prev_value:
                return [(value, y1), (value, y2)]
            if fix_length and prev_value:
                vertices.append((value + fix_length, y1))
            vertices.append((value, y1))
            vertices.append((value, y2))
            is_top = not is_top
            prev_value = value

        return vertices

    def _get_texture_fix_length(self):
        categories_mapped = list(self._category_axis.MapDataPointsToViewport())
        categories = list(self._category_axis.GetDataPoints())
        if len(categories) < 2:
            return 0
        dpi_scaling = uicore.desktop.dpiScaling
        first, second = categories[0], categories[1]
        first_mapped, second_mapped = categories_mapped[0] * dpi_scaling, categories_mapped[1] * dpi_scaling
        pixel_length = second_mapped - first_mapped
        left_over = pixel_length % self.textureWidth
        error = self.textureWidth - left_over
        length = second - first
        ratio = length / pixel_length if pixel_length else 1
        return error * ratio / 2.0

    def _get_vertical_minimum_maximum_values(self):
        visible = self._value_axis.get_visible_range()
        added = visible[1] - visible[0]
        minimum = self._value_axis.get_min_value() - added
        maximum = self._value_axis.get_max_value() + added
        minimum_mapped, maximum_mapped = self._value_axis.MapSequenceToViewport([minimum, maximum])
        minimum_mapped *= uicore.dpiScaling
        maximum_mapped *= uicore.dpiScaling
        pixel_length = maximum_mapped - minimum_mapped
        left_over = pixel_length % self.textureWidth
        error = self.textureWidth - left_over
        length = maximum - minimum
        ratio = length / pixel_length if pixel_length else 1
        error_added = error * ratio / 2.0
        return (minimum - error_added, maximum + error_added)

    def _get_transform(self):
        dpi_scaling = uicore.desktop.dpiScaling
        transform = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        transform = self._category_axis.UpdateToViewportTransform(transform, 0, dpi_scaling)
        transform = self._value_axis.UpdateToViewportTransform(transform, 1, dpi_scaling)
        return transform

    def Close(self):
        self._is_destroyed = True
        self.StopAnimations()
        self._category_axis.onChange.disconnect(self._axis_changed)
        self._value_axis.onChange.disconnect(self._axis_changed)
        if self._transit_selection:
            self._transit_selection.on_change.disconnect(self._update_axis)
            self._transit_selection = None
        animations.BlinkOut(self, callback=super(TransitSelectionGraph, self).Close)

    def set_line_color(self, line_color):
        self.lineColor = line_color

    def get_transit_selection(self):
        return self._transit_selection

    @property
    def category_axis(self):
        return self._category_axis

    def OnProjectDiscoveryMarkerDim(self, excluded):
        if not self._is_destroyed:
            if self.get_transit_selection() not in excluded:
                animations.FadeTo(self, self.opacity, 0.4, duration=0.5)
            else:
                animations.FadeIn(self, duration=0.5)
