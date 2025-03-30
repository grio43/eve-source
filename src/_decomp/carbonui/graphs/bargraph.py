#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\bargraph.py
from carbonui.primitives.fill import Fill
from carbonui.primitives.polygon import Polygon
import carbonui.const as uiconst
from carbonui.graphs import animations
from carbonui.graphs.axis import AxisOrientation
from carbonui.uicore import uicore
from carbonui.util import colorblind
from carbonui.util.color import Color

class DynamicHint(object):

    def __init__(self, callback):
        self._callback = callback

    def __getitem__(self, item):
        return self._callback(item)


class BarGraph(Polygon):
    default_name = 'BarGraph'
    default_state = uiconst.UI_NORMAL
    default_barSize = 7

    def ApplyAttributes(self, attributes):
        Polygon.ApplyAttributes(self, attributes)
        self._categoryAxis = attributes['categoryAxis']
        self._valueAxis = attributes['valueAxis']
        self._orientation = attributes.get('orientation', AxisOrientation.VERTICAL)
        self._categoryAxis.onChange.connect(self._AxisChanged)
        self._valueAxis.onChange.connect(self._AxisChanged)
        self._values = attributes['values']
        self._barColors = attributes.get('barColors', None)
        self._vertices = None
        self.barColor = self.GetRGBA()
        self.hoverColor = attributes.get('hoverColor', self.barColor)
        self.negativeColor = attributes.get('negativeColor', self.barColor)
        self.negativeHoverColor = attributes.get('negativeHoverColor', self.negativeColor)
        self.barSize = attributes.get('barSize', self.default_barSize)
        self.barSizeMinMax = attributes.get('barSizeMinMax', (self.barSize, self.barSize))
        self.color = (1, 1, 1, 1)
        self._locked = False
        self._dirty = False
        self._originalColor = self.color
        self._animation = None
        self._hoverIndex = None
        self._tooltipRect = None
        self._Build()

    def GetLegendItem(self):
        return Fill(name='legendVolume', color=self.barColor, align=uiconst.TOLEFT)

    @property
    def hint(self):
        h = getattr(self, '_hint', None)
        if not isinstance(h, basestring) and hasattr(h, '__getitem__'):
            return h[self._hoverIndex]
        return h

    @hint.setter
    def hint(self, value):
        Polygon.hint.fset(self, value)

    def GetTooltipPosition(self):
        return self._tooltipRect

    def Animate(self, animationType, animationDynamics, duration):
        self.CancelAnimation()
        self._animation = animations.CreateAnimation(self, self._categoryAxis, self._valueAxis, self._orientation, animationType, animationDynamics, duration, 4)

    def CancelAnimation(self, applyLastFrame = True):
        self.StopAnimations()
        self.opacity = 1.0
        if self._animation:
            self._animation.Cancel(applyLastFrame)
            self._animation = None

    def Close(self):
        self.CancelAnimation(False)
        super(BarGraph, self).Close()
        self._categoryAxis.onChange.disconnect(self._AxisChanged)
        self._valueAxis.onChange.disconnect(self._AxisChanged)

    def _Build(self):
        dpiScaling = uicore.desktop.dpiScaling
        barWidth = self._GetBarWidth()
        barWidth *= dpiScaling
        axisZero = self._valueAxis.MapToViewport(0) * dpiScaling
        positions = []
        colors = []
        triangles = []
        for i, (x, y, value) in enumerate(zip(self._categoryAxis.MapDataPointsToViewport(), self._valueAxis.MapSequenceToViewport(self._values), self._values)):
            x *= dpiScaling
            y *= dpiScaling
            color = self.GetBarColor(i, value)
            if self._orientation == AxisOrientation.VERTICAL:
                positions.append((x - barWidth, y))
                positions.append((x + barWidth, y))
                positions.append((x + barWidth, axisZero))
                positions.append((x - barWidth, axisZero))
            else:
                positions.append((y, x - barWidth))
                positions.append((y, x + barWidth))
                positions.append((axisZero, x + barWidth))
                positions.append((axisZero, x - barWidth))
            colors.append(color)
            colors.append(color)
            colors.append(color)
            colors.append(color)
            triangles.append((4 * i, 4 * i + 1, 4 * i + 2))
            triangles.append((4 * i + 2, 4 * i + 3, 4 * i))

        self.AppendVertices(positions, None, colors)
        self.renderObject.AppendTriangles(triangles)
        self.width = max((x[0] for x in positions))
        self.height = max((x[1] for x in positions))

    def _Rescale(self):
        dpiScaling = uicore.desktop.dpiScaling
        barWidth = self._GetBarWidth()
        barWidth *= dpiScaling
        axisZero = self._valueAxis.MapToViewport(0) * dpiScaling
        positions = []
        for i, (x, y) in enumerate(zip(self._categoryAxis.MapDataPointsToViewport(), self._valueAxis.MapSequenceToViewport(self._values))):
            x *= dpiScaling
            y *= dpiScaling
            if self._orientation == AxisOrientation.VERTICAL:
                positions.append((x - barWidth, y))
                positions.append((x + barWidth, y))
                positions.append((x + barWidth, axisZero))
                positions.append((x - barWidth, axisZero))
            else:
                positions.append((y, x - barWidth))
                positions.append((y, x + barWidth))
                positions.append((axisZero, x + barWidth))
                positions.append((axisZero, x - barWidth))

        self.renderObject.SetVertices(positions)

    def _GetBarWidth(self):
        barWidth = abs(self._categoryAxis.MapToViewport(0) - self._categoryAxis.MapToViewport(1)) - 1
        barWidth = min(max(barWidth, self.barSizeMinMax[0]), self.barSizeMinMax[1]) / 2.0
        return barWidth

    def _AxisChanged(self, _):
        if self._locked:
            self._dirty = True
        else:
            self._Rescale()

    def AddBarHighlight(self, barIndex):
        self._hoverIndex = barIndex
        color = self.GetBarHoverColor(barIndex, self._values[self._hoverIndex])
        self._SetBarColor(color)

    def _RemoveBarHighlight(self):
        if self._hoverIndex is None:
            return
        color = self.GetBarColor(self._hoverIndex, self._values[self._hoverIndex])
        self._SetBarColor(color)
        self._hoverIndex = None

    def _SetBarColor(self, color):
        color = colorblind.CheckReplaceColor(color)
        offset = self._hoverIndex * 4
        for each in range(4):
            self.renderObject.vertices[offset + each].color = color

        self.renderObject.SetDirty()

    def GetBarColor(self, barIdx, value):
        if self._barColors is None:
            if value < 0:
                return self.negativeColor
            return self.barColor
        return self._barColors[barIdx]

    def GetBarHoverColor(self, barIdx, value):
        if self._barColors is None:
            if value < 0:
                return self.negativeHoverColor
            return self.hoverColor
        else:
            barColor = self._barColors[barIdx]
            c = Color(*barColor)
            sat = c.GetSaturation()
            newSat = min(1.0, max(0.0, sat - 0.3))
            hoverColor = c.SetSaturation(newSat).GetRGBA()
            return hoverColor

    def OnMouseEnter(self, *args):
        index = self.FindMouseoverIndex()
        self._RemoveBarHighlight()
        self.AddBarHighlight(index)
        dpiScaling = uicore.desktop.dpiScaling
        offset = index * 4
        tl = self.renderObject.vertices[offset].position
        br = self.renderObject.vertices[offset + 2].position
        pos = self.GetAbsolutePosition()
        self._tooltipRect = (tl[0] / dpiScaling + pos[0],
         tl[1] / dpiScaling + pos[1],
         br[0] / dpiScaling - tl[0] / dpiScaling,
         br[1] / dpiScaling - tl[1] / dpiScaling)

    def FindMouseoverIndex(self):
        if self._orientation == AxisOrientation.VERTICAL:
            x = uicore.uilib.x - self.GetAbsoluteLeft()
        else:
            x = uicore.uilib.y - self.GetAbsoluteTop()
        x = self._categoryAxis.MapFromViewport(x)
        index = int(round(x))
        return index

    def OnMouseExit(self, *args):
        self._RemoveBarHighlight()

    def LockGraphUpdates(self):
        self._locked = True

    def UnlockGraphUpdates(self):
        if self._locked:
            self._locked = False
            if self._dirty:
                self._Rescale()
