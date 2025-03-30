#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\pointgraph.py
from itertools import izip
import trinity
from carbonui import uiconst
from carbonui.primitives.polygon import Polygon
from carbonui.primitives.sprite import Sprite
from carbonui.graphs import animations
from carbonui.graphs.axis import AxisOrientation
from carbonui.uicore import uicore
from carbonui.util import colorblind
from carbonui.util.color import Color

class PointGraph(Polygon):
    default_state = uiconst.UI_NORMAL
    default_pointSize = 7
    default_pointColor = (0.2, 0.54, 1.0, 1.0)
    default_texturePath = 'res:/UI/Texture/classes/graph/point.png'
    default_spriteEffect = trinity.TR2_SFX_COPY
    default_hoverColor = Color.GRAY8
    default_hideZero = False

    def ApplyAttributes(self, attributes):
        Polygon.ApplyAttributes(self, attributes)
        self.hideZero = attributes.get('hideZero', self.default_hideZero)
        self._categoryAxis = attributes['categoryAxis']
        self._valueAxis = attributes['valueAxis']
        self._orientation = attributes.get('orientation', AxisOrientation.VERTICAL)
        self._categoryAxis.onChange.connect(self._AxisChanged)
        self._valueAxis.onChange.connect(self._AxisChanged)
        self._values = attributes['values']
        self.pointColor = attributes.get('pointColor', (1, 1, 1, 1))
        self.hoverColor = attributes.get('hoverColor', self.default_hoverColor)
        self.pointSize = attributes.get('pointSize', self.default_pointSize)
        self.pointSizeMinMax = attributes.get('pointSizeMinMax', (self.pointSize, self.pointSize))
        self.color = (1, 1, 1, 1)
        self._locked = False
        self._dirty = False
        self._originalColor = self.color
        self._animation = None
        self._hoverIndex = None
        self._tooltipRect = None
        self._Build()

    def GetLegendItem(self):
        return Sprite(name='legendPoint', texturePath=self.texturePath, color=self.pointColor, size=(16, 16), align=uiconst.TOLEFT)

    @property
    def hint(self):
        if self._hoverIndex is None:
            return
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
        try:
            self.CancelAnimation(False)
            self._categoryAxis.onChange.disconnect(self._AxisChanged)
            self._valueAxis.onChange.disconnect(self._AxisChanged)
        finally:
            super(PointGraph, self).Close()

    def _Build(self):
        dpiScaling = uicore.desktop.dpiScaling
        pointSize2 = self._GetPointSize()
        positions = []
        if self._orientation == AxisOrientation.VERTICAL:
            for x, y, value in zip(self._categoryAxis.MapDataPointsToViewport(), self._valueAxis.MapSequenceToViewport(self._values), self._values):
                thisPointSize = self.GetPointSizeForValue(value, pointSize2)
                x *= dpiScaling
                y *= dpiScaling
                positions.append((x - thisPointSize, y - thisPointSize))
                positions.append((x + thisPointSize, y - thisPointSize))
                positions.append((x + thisPointSize, y + thisPointSize))
                positions.append((x - thisPointSize, y + thisPointSize))

        else:
            for y, x, value in zip(self._categoryAxis.MapDataPointsToViewport(), self._valueAxis.MapSequenceToViewport(self._values), self._values):
                thisPointSize = self.GetPointSizeForValue(value, pointSize2)
                x *= dpiScaling
                y *= dpiScaling
                positions.append((x - thisPointSize, y - thisPointSize))
                positions.append((x + thisPointSize, y - thisPointSize))
                positions.append((x + thisPointSize, y + thisPointSize))
                positions.append((x - thisPointSize, y + thisPointSize))

        texcoords = ((0, 0),
         (1, 0),
         (1, 1),
         (0, 1)) * len(self._values)
        triangles = []
        triangles.extend(((i, i + 1, i + 2) for i in xrange(0, len(self._values) * 4, 4)))
        triangles.extend(((i + 2, i + 3, i) for i in xrange(0, len(self._values) * 4, 4)))
        self.AppendVertices(positions, None, self.GetPointColors(), texcoords)
        self.renderObject.AppendTriangles(triangles)

    def GetPointColors(self):
        return self.pointColor

    def GetPointSizeForValue(self, value, defaultSize):
        if self.hideZero and value == 0:
            return 0
        return defaultSize

    def _Rescale(self):
        self.CancelAnimation()
        self._RemoveBarHighlight()
        dpiScaling = uicore.desktop.dpiScaling
        pointSize2 = self._GetPointSize()
        positions = []
        append = positions.append
        if self._orientation == AxisOrientation.VERTICAL:
            for x, y, value in izip(self._categoryAxis.MapDataPointsToViewport(), self._valueAxis.MapSequenceToViewport(self._values), self._values):
                thisPointSize = self.GetPointSizeForValue(value, pointSize2)
                x *= dpiScaling
                y *= dpiScaling
                xl = x - thisPointSize
                xr = x + thisPointSize
                yl = y - thisPointSize
                yr = y + thisPointSize
                append((xl, yl))
                append((xr, yl))
                append((xr, yr))
                append((xl, yr))

        else:
            for y, x, value in izip(self._categoryAxis.MapDataPointsToViewport(), self._valueAxis.MapSequenceToViewport(self._values), self._values):
                thisPointSize = self.GetPointSizeForValue(value, pointSize2)
                x *= dpiScaling
                y *= dpiScaling
                xl = x - thisPointSize
                xr = x + thisPointSize
                yl = y - thisPointSize
                yr = y + thisPointSize
                append((xl, yl))
                append((xr, yl))
                append((xr, yr))
                append((xl, yr))

        self.renderObject.SetVertices(positions)

    def _GetPointSize(self):
        barWidth = abs(self._categoryAxis.MapToViewport(0) - self._categoryAxis.MapToViewport(1))
        barWidth = min(max(barWidth, self.pointSizeMinMax[0]), self.pointSizeMinMax[1]) / 2.0
        return barWidth

    def _AxisChanged(self, _):
        if self._locked:
            self._dirty = True
        else:
            self._Rescale()

    def _RemoveBarHighlight(self):
        if self._hoverIndex is None:
            return
        self._SetBarColor(self._GetPointColor(self._hoverIndex), -float(self.pointSize) / 4)
        self._hoverIndex = None

    def _GetPointColor(self, index):
        return self.pointColor

    def _SetBarColor(self, color, sizeInc):
        color = colorblind.CheckReplaceColor(color)
        offset = self._hoverIndex * 4
        resize = ((-sizeInc, -sizeInc),
         (sizeInc, -sizeInc),
         (sizeInc, sizeInc),
         (-sizeInc, sizeInc))
        for each in xrange(4):
            v = self.renderObject.vertices[offset + each]
            v.position = (v.position[0] + resize[each][0], v.position[1] + resize[each][1])
            v.color = color

        self.renderObject.SetDirty()

    def OnMouseEnter(self, *args):
        indexOfPoint = self.GetIndexOfMousedOverPoint()
        self.HilitePoint(indexOfPoint)
        offset = indexOfPoint * 4
        topLeft = self.renderObject.vertices[offset].position
        bottomRight = self.renderObject.vertices[offset + 2].position
        graphAbsLeft, graphAbsTop = self.GetAbsolutePosition()
        dpiScaling = uicore.desktop.dpiScaling
        tooltipAreaLeft = topLeft[0] / dpiScaling + graphAbsLeft
        tooltipAreaTop = topLeft[1] / dpiScaling + graphAbsTop
        tooltipAreaWidth = bottomRight[0] / dpiScaling - topLeft[0] / dpiScaling
        tooltipAreaHeight = bottomRight[1] / dpiScaling - topLeft[1] / dpiScaling
        self._tooltipRect = (tooltipAreaLeft,
         tooltipAreaTop,
         tooltipAreaWidth,
         tooltipAreaHeight)

    def GetIndexOfMousedOverPoint(self):
        if self._orientation == AxisOrientation.VERTICAL:
            x = uicore.uilib.x - self.GetAbsoluteLeft()
        else:
            x = uicore.uilib.y - self.GetAbsoluteTop()
        x = self._categoryAxis.MapFromViewport(x)
        indexOfPoint = int(x)
        dpiScaling = uicore.desktop.dpiScaling
        graphAbsLeft, graphAbsTop = self.GetAbsolutePosition()
        startPoint = max(0, indexOfPoint - 5)
        for tryIndex in xrange(startPoint, startPoint + 10):
            offset = tryIndex * 4
            if len(self.renderObject.vertices) <= offset + 2:
                return indexOfPoint
            topLeft = self.renderObject.vertices[offset].position
            bottomRight = self.renderObject.vertices[offset + 2].position
            tooltipAreaLeft = topLeft[0] / dpiScaling + graphAbsLeft
            tooltipAreaTop = topLeft[1] / dpiScaling + graphAbsTop
            tooltipAreaRight = bottomRight[0] / dpiScaling + graphAbsLeft
            tooltipAreaBottom = bottomRight[1] / dpiScaling + graphAbsTop
            if tooltipAreaLeft <= uicore.uilib.x <= tooltipAreaRight and tooltipAreaTop <= uicore.uilib.y <= tooltipAreaBottom:
                return tryIndex

        return indexOfPoint

    def SetValues(self, values):
        self._values = values

    def HilitePoint(self, index):
        self._RemoveBarHighlight()
        self._hoverIndex = index
        if index is not None:
            self._SetBarColor(self.hoverColor, float(self.pointSize) / 4)

    def OnMouseExit(self, *args):
        self._RemoveBarHighlight()

    def LockGraphUpdates(self):
        self._locked = True

    def UnlockGraphUpdates(self):
        if self._locked:
            self._locked = False
            if self._dirty:
                self._Rescale()
