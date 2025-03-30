#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\areagraph.py
import math
import carbonui.const as uiconst
from carbonui.graphs import animations, axis
from carbonui.primitives.fill import Fill
from carbonui.primitives.polygon import Polygon
from carbonui.uicore import uicore

class AreaGraph(Polygon):
    default_name = 'AreaGraph'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_graphColor = (1, 1, 1, 0.2)
    default_hoverColor = (1, 1, 1, 1)

    def ApplyAttributes(self, attributes):
        Polygon.ApplyAttributes(self, attributes)
        self._categoryAxis = attributes['categoryAxis']
        self._valueAxis = attributes['valueAxis']
        self._orientation = attributes.get('orientation', axis.AxisOrientation.VERTICAL)
        self._categoryAxis.onChange.connect(self._AxisChanged)
        self._valueAxis.onChange.connect(self._AxisChanged)
        self._values = attributes['values']
        self._vertices = None
        self.graphColor = attributes.get('graphColor', self.default_graphColor)
        self.hoverColor = attributes.get('hoverColor', self.default_hoverColor)
        self._locked = False
        self._dirty = False
        self._originalColor = self.color
        self._animation = None
        self._Build()

    def GetLegendItem(self):
        return Fill(name='legendVolume', color=self.graphColor, align=uiconst.TOLEFT)

    def Animate(self, animationType, animationDynamics, duration):
        self.CancelAnimation()
        self._animation = animations.CreateAnimation(self, self._categoryAxis, self._valueAxis, self._orientation, animationType, animationDynamics, duration, 2)

    def CancelAnimation(self, applyLastFrame = True):
        self.StopAnimations()
        self.opacity = 1.0
        if self._animation:
            self._animation.Cancel(applyLastFrame)
            self._animation = None

    def Close(self):
        self.CancelAnimation(False)
        super(AreaGraph, self).Close()
        self._categoryAxis.onChange.disconnect(self._AxisChanged)
        self._valueAxis.onChange.disconnect(self._AxisChanged)

    def _Build(self):
        positions = self._GetVertexPositions()
        transform = self._GetTransform()
        color = self.graphColor
        self.AppendVertices(positions, transform, color)
        triangles = []
        for i in xrange(len(positions) / 2 - 1):
            i2 = i * 2
            triangles.append((i2 + 1, i2 + 3, i2 + 2))
            triangles.append((i2, i2 + 1, i2 + 2))

        self.renderObject.AppendTriangles(triangles)

    def _GetTransform(self):
        dpiScaling = uicore.desktop.dpiScaling
        transform = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        if self._orientation == axis.AxisOrientation.VERTICAL:
            transform = self._categoryAxis.UpdateToViewportTransform(transform, 0, dpiScaling)
            transform = self._valueAxis.UpdateToViewportTransform(transform, 1, dpiScaling)
        else:
            transform = self._categoryAxis.UpdateToViewportTransform(transform, 1, dpiScaling)
            transform = self._valueAxis.UpdateToViewportTransform(transform, 0, dpiScaling)
        return transform

    def _GetVertexPositions(self):
        if self._vertices:
            return self._vertices
        positions = []
        if self._orientation == axis.AxisOrientation.VERTICAL:
            for x, y in zip(xrange(len(self._categoryAxis.GetDataPoints())), self._values):
                positions.append((x, y))
                positions.append((x, 0))
                if x + 1 < len(self._values):
                    n = self._values[x + 1]
                    if n * y < 0:
                        z = float(abs(y)) / (abs(y) + abs(n))
                        positions.append((x + z, 0))
                        positions.append((x + z, 0))

        else:
            for x, y in zip(xrange(len(self._categoryAxis.GetDataPoints())), self._values):
                positions.append((y, x))
                positions.append((0, x))
                if x + 1 < len(self._values):
                    n = self._values[x + 1]
                    if n * y < 0:
                        z = float(abs(y)) / (abs(y) + abs(n))
                        positions.append((0, x + z))
                        positions.append((0, x + z))

        self._vertices = positions
        return positions

    def _AxisChanged(self, _):
        if self._locked:
            self._dirty = True
        else:
            self._Rescale()

    def LockGraphUpdates(self):
        self._locked = True

    def UnlockGraphUpdates(self):
        if self._locked:
            self._locked = False
            if self._dirty:
                self._Rescale()

    def _Rescale(self):
        self.CancelAnimation(False)
        self._dirty = False
        self.renderObject.SetVertices(self._GetVertexPositions(), self._GetTransform())

    def CancelAnimations(self):
        self.StopAnimations()
        self.opacity = 1.0

    def OnMouseEnter(self, *args):
        self._originalColor = self.color.GetRGBA()
        self.color = self.hoverColor

    def OnMouseExit(self, *args):
        self.color = self._originalColor
