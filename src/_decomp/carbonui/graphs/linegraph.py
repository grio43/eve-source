#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\linegraph.py
import carbonui.const as uiconst
import trinity
from carbonui.graphs import animations
from carbonui.graphs.axis import AxisOrientation
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorlinetrace import VectorLineTrace, CORNERTYPE_ROUND
from carbonui.uicore import uicore
LEGEND_SPRITE = 'res:/ui/texture/classes/graph/linelegend.png'

class LineGraph(VectorLineTrace):
    default_name = 'LineGraph'
    default_cornerType = CORNERTYPE_ROUND
    default_state = uiconst.UI_DISABLED
    default_lineWidth = 1.0
    default_spriteEffect = trinity.TR2_SFX_FILL_AA
    default_lineColor = (1.0, 1.0, 1.0, 1.0)

    def ApplyAttributes(self, attributes):
        VectorLineTrace.ApplyAttributes(self, attributes)
        self._categoryAxis = attributes['categoryAxis']
        self._valueAxis = attributes['valueAxis']
        self._orientation = attributes.get('orientation', AxisOrientation.VERTICAL)
        self._categoryAxis.onChange.connect(self._AxisChanged)
        self._valueAxis.onChange.connect(self._AxisChanged)
        self._values = attributes['values']
        self._dataPoints = attributes.get('dataPoints', None)
        self._vertices = None
        self._animation = None
        self._locked = False
        self._dirty = False
        self.lineColor = attributes.get('lineColor', self.default_lineColor)
        self._Build()

    def _Build(self):
        self.AppendVertices(self._GetVertexPositions(), self._GetTransform(), self.lineColor)

    def GetLegendItem(self):
        return Sprite(name='legendPoint', texturePath=LEGEND_SPRITE, color=self.lineColor, size=(16, 16), align=uiconst.TOLEFT)

    def Animate(self, animationType, animationDynamics, duration):
        self.CancelAnimation()
        self._animation = animations.CreateAnimation(self, self._categoryAxis, self._valueAxis, self._orientation, animationType, animationDynamics, duration, 1)

    def CancelAnimation(self, applyLastFrame = True):
        self.StopAnimations()
        self.opacity = 1.0
        if self._animation:
            self._animation.Cancel(applyLastFrame)
            self._animation = None

    def Close(self):
        self.CancelAnimation(False)
        super(LineGraph, self).Close()
        self._categoryAxis.onChange.disconnect(self._AxisChanged)
        self._valueAxis.onChange.disconnect(self._AxisChanged)

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

    def _GetTransform(self):
        dpiScaling = uicore.desktop.dpiScaling
        transform = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        if self._orientation == AxisOrientation.VERTICAL:
            transform = self._categoryAxis.UpdateToViewportTransform(transform, 0, dpiScaling)
            transform = self._valueAxis.UpdateToViewportTransform(transform, 1, dpiScaling)
        else:
            transform = self._categoryAxis.UpdateToViewportTransform(transform, 1, dpiScaling)
            transform = self._valueAxis.UpdateToViewportTransform(transform, 0, dpiScaling)
        return transform

    def _GetDataRange(self):
        if self._dataPoints is not None:
            return self._dataPoints
        return xrange(len(self._categoryAxis.GetDataPoints()))

    def _GetVertexPositions(self):
        if self._vertices:
            return self._vertices
        if self._orientation == AxisOrientation.VERTICAL:
            vertices = zip(self._GetDataRange(), self._values)
        else:
            vertices = zip(self._values, self._GetDataRange())
        self._vertices = vertices
        return vertices

    def SetValues(self, values):
        self._vertices = None
        self._values = values
