#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\lowhighvaluegraph.py
import trinity
from carbonui.primitives.vectorlinetrace import VectorLineTrace
import carbonui.const as uiconst
from carbonui.graphs.axis import AxisOrientation
from carbonui.graphs import animations
from carbonui.uicore import uicore

class LowHighValueGraph(VectorLineTrace):
    default_name = 'LowHighValueGraph'
    default_align = uiconst.TOPLEFT
    default_cornerType = 0
    default_spriteEffect = trinity.TR2_SFX_FILL
    default_lineWidth = 1.0
    default_lineColor = (1.0, 1.0, 1.0, 0.2)

    def ApplyAttributes(self, attributes):
        VectorLineTrace.ApplyAttributes(self, attributes)
        self._categoryAxis = attributes['categoryAxis']
        self._valueAxis = attributes['valueAxis']
        self._orientation = attributes.get('orientation', AxisOrientation.VERTICAL)
        self._categoryAxis.onChange.connect(self._AxisChanged)
        self._valueAxis.onChange.connect(self._AxisChanged)
        self._lineColor = attributes.get('lineColor', self.default_lineColor)
        self._values = attributes['values']
        self._vertices = None
        self._locked = False
        self._dirty = False
        self._animation = None
        self._Build()

    def GetLegendItem(self):
        line = VectorLineTrace(size=(10, 10), align=uiconst.TOLEFT, spriteEffect=trinity.TR2_SFX_FILL, lineWidth=3)
        line.AddPoints(((5, 0), (5, 10)), self._lineColor)
        return line

    def Animate(self, animationType, animationDynamics, duration):
        self.CancelAnimation()
        if animationType == animations.AnimationType.FADE:
            if animationDynamics == animations.AnimationDynamics.SIMULTANEOUS:
                uicore.animations.MorphScalar(self, 'opacity', startVal=0.0, endVal=1.0, duration=duration)
            else:
                raise ValueError('unsupported animation type')
        elif animationType == animations.AnimationType.GROW:
            self._animation = animations.CreateVertexAnimation(self, self._categoryAxis, self._valueAxis, self._orientation, animationDynamics, duration, 4)
        else:
            raise ValueError('unsupported animation type')

    def CancelAnimation(self, applyLastFrame = True):
        self.StopAnimations()
        self.opacity = 1.0
        if self._animation:
            self._animation.Cancel(applyLastFrame)
            self._animation = None

    def Close(self):
        self.CancelAnimation(False)
        super(LowHighValueGraph, self).Close()
        self._categoryAxis.onChange.disconnect(self._AxisChanged)
        self._valueAxis.onChange.disconnect(self._AxisChanged)

    def _Build(self):
        positions, colors = self._GetVertexPositions()
        self.AppendVertices(positions, self._GetTransform(), colors)

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

    def _GetVertexPositions(self):
        if self._vertices:
            return self._vertices
        positions = []
        if self._orientation == AxisOrientation.VERTICAL:
            for x, value in zip(xrange(len(self._categoryAxis.GetDataPoints())), self._values):
                positions.append((x, value[1]))
                positions.append((x, value[1]))
                positions.append((x, value[0]))
                positions.append((x, value[0]))

        else:
            for x, value in zip(xrange(len(self._categoryAxis.GetDataPoints())), self._values):
                positions.append((value[1], x))
                positions.append((value[1], x))
                positions.append((value[0], x))
                positions.append((value[0], x))

        colors = []
        color = self._lineColor
        clearColor = color[0:3] + (0,)
        for i in xrange(len(self._categoryAxis.GetDataPoints())):
            colors.append(clearColor)
            colors.append(color)
            colors.append(color)
            colors.append(clearColor)

        self._vertices = (positions, colors)
        return (positions, colors)

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
        positions, _ = self._GetVertexPositions()
        self.renderObject.SetVertices(positions, self._GetTransform())

    def CancelAnimations(self):
        self.StopAnimations()
        self.opacity = 1.0
