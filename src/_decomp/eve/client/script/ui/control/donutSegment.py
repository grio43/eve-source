#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\donutSegment.py
import math
import geo2
from carbonui import Color, uiconst
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from carbonui.uianimations import animations
from signals import Signal
MIN_NUM_POINTS = 24

class DonutSegment(VectorLineTrace):
    default_segmentID = None
    default_radius = 20
    default_angle = 2 * math.pi
    default_startAngle = -math.pi / 2
    default_isClockwise = True
    default_colorStart = (1.0, 1.0, 1.0, 1.0)
    default_colorEnd = (1.0, 1.0, 1.0, 1.0)
    default_outputMode = uiconst.OUTPUT_COLOR_AND_GLOW
    default_glowBrightness = 0.0

    def ApplyAttributes(self, attributes):
        VectorLineTrace.ApplyAttributes(self, attributes)
        self._radius = attributes.get('radius', self.default_radius)
        self.startAngle = attributes.get('startAngle', self.default_startAngle)
        self.angle = attributes.get('angle', self.default_angle)
        self.isClockwise = attributes.get('isClockwise', self.default_isClockwise)
        self._colorStart = Color.from_any(attributes.get('colorStart', self.default_colorStart))
        self._colorEnd = Color.from_any(attributes.get('colorEnd', self.default_colorEnd))
        self.segmentID = attributes.get('segmentID', None)
        value = attributes.value
        self.width = self.height = 2 * self._radius
        self.on_clicked = Signal(signalName='on_clicked')
        self.on_mouse_enter = Signal(signalName='on_mouse_enter')
        self.on_mouse_exit = Signal(signalName='on_mouse_exit')
        self._ReconstructControlPoints()
        if value is not None:
            self.SetValue(value)

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self.SetRadius(value)

    @property
    def colorStart(self):
        return self._colorStart

    @colorStart.setter
    def colorStart(self, color):
        self._colorStart = Color.from_any(color)
        self._ReconstructControlPoints()

    @property
    def colorEnd(self):
        return self._colorEnd

    @colorEnd.setter
    def colorEnd(self, color):
        self._colorEnd = Color.from_any(color)
        self._ReconstructControlPoints()

    def SetColor(self, start = None, end = None):
        if start is not None:
            self._colorStart = Color.from_any(start)
        if end is not None:
            self._colorEnd = Color.from_any(end)
        self._ReconstructControlPoints()

    def Refresh(self):
        self._ReconstructControlPoints()

    def _ReconstructControlPoints(self):
        self.Flush()
        numPoints = self._GetNumPoints()
        offset = min(0.01, self.angle / 4.0)
        rangeSize = self.angle - 2.0 * offset
        stepSize = rangeSize / float(numPoints)
        self._AddPoint(self.startAngle - offset, self.colorStart.rgba)
        for i in xrange(numPoints + 1):
            t = self.startAngle + offset + float(i) * stepSize
            color = geo2.Vec4Lerp(self.colorStart, self.colorEnd, i / float(numPoints))
            self._AddPoint(t, color)

        self._AddPoint(t + 2 * offset, self.colorEnd.rgba)

    def _GetNumPoints(self):
        numPoints = 0.2 * self._radius * self.angle
        numPoints = int(max(MIN_NUM_POINTS, numPoints))
        return numPoints

    def _AddPoint(self, t, color):
        point = self._GetLinePoint(t)
        self.AddPoint(point, color=color)

    def SetClockwise(self):
        self.isClockwise = True
        self._ReconstructControlPoints()

    def SetCounterClockwise(self):
        self.isClockwise = False
        self._ReconstructControlPoints()

    def _GetLinePoint(self, t):
        if not self.isClockwise:
            t = -t - math.pi
        w = self.lineWidth / 2.0
        r = self._radius - w
        xPoint = w + r * (1.0 + math.cos(t))
        yPoint = w + r * (1.0 + math.sin(t))
        return (xPoint, yPoint)

    @property
    def value(self):
        return self.GetValue()

    @value.setter
    def value(self, val):
        self.SetValue(val)

    def GetValue(self):
        return self.end - self.start

    def SetValue(self, value, duration = 0.0, sleep = False):
        if value == self.end:
            return
        if not duration:
            self.end = value
        else:
            animations.MorphScalar(self, 'end', self.end, value, duration=duration, sleep=sleep)

    def SetLineWidth(self, value):
        self.lineWidth = value
        self._ReconstructControlPoints()

    def OnClick(self, *args):
        self.on_clicked(self.segmentID)

    def OnMouseEnter(self, *args):
        self.on_mouse_enter(self.segmentID)
        animations.MorphScalar(self, 'glowBrightness', self.glowBrightness, 0.3, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        self.on_mouse_exit(self.segmentID)
        animations.MorphScalar(self, 'glowBrightness', self.glowBrightness, 0.0, duration=uiconst.TIME_EXIT)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if not self.hint:
            return None
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=self.hint)

    def GetTooltipPosition(self):
        xp, yp = self.GetAbsolutePosition()
        w, _ = self.GetAbsoluteSize()
        x, y = self.GetOuterCenterPoint()
        r = w / 2
        return (xp + r + x,
         yp + r + y,
         0,
         0)

    def GetOuterCenterPoint(self, radiusScale = 1.0):
        angle = self.GetCenterAngle()
        return self._GetPoint(angle, radiusScale)

    def GetPoint(self, value, radiusScale):
        angle = self.startAngle + value * self.angle
        return self._GetPoint(angle, radiusScale)

    def _GetPoint(self, angle, radiusScale):
        w, h = self.GetAbsoluteSize()
        r = radiusScale * w / 2
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        return (x, y)

    def GetOuterCenterPointAbsolute(self, radiusScale):
        x, y = self.GetOuterCenterPoint(radiusScale)
        l, t = self.GetAbsolutePosition()
        w, h = self.GetAbsoluteSize()
        x += l + w / 2.0
        y += t + h / 2.0
        return (x, y)

    def GetCenterAngle(self):
        startAngle = self.startAngle + self.angle * self.start
        angle = startAngle + self.angle / 2 * (self.end - self.start)
        return angle

    def GetTooltipPointer(self):
        angle = self.GetCenterAngle()
        if angle < math.pi / 4:
            return uiconst.POINT_LEFT_2
        elif angle < 3 * math.pi / 4:
            return uiconst.POINT_TOP_2
        elif angle < 5 * math.pi / 4:
            return uiconst.POINT_RIGHT_2
        elif angle < 7 * math.pi / 4:
            return uiconst.POINT_BOTTOM_2
        else:
            return uiconst.POINT_LEFT_2

    def SetRadius(self, radius):
        self._radius = radius
        self.width = self.height = 2 * radius
        self._ReconstructControlPoints()
        self.SetValue(self.end)
