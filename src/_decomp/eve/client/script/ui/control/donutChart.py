#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\donutChart.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.donutSegment import DonutSegment
from signals import Signal

class SegmentData:

    def __init__(self, value, segmentID = None, hint = None):
        self.value = value
        self.ratio = 0.0
        self.segmentID = segmentID
        self.hint = hint


class DonutChart(Container):
    default_name = 'DonutChart'
    default_radius = 50
    default_startAngle = -math.pi / 2
    default_isClockwise = True
    default_lineWidth = 10.0
    default_gapSize = 0.005
    default_minSegmentSize = 0.02
    default_color = (0.5, 0.65, 0.7, 1.0)
    default_outputMode = uiconst.OUTPUT_COLOR

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.radius = attributes.get('radius', self.default_radius)
        self.startAngle = attributes.get('startAngle', self.default_startAngle)
        self.isClockwise = attributes.get('isClockwise', self.default_isClockwise)
        self.gapSize = attributes.get('gapSize', self.default_gapSize)
        self.minSegmentSize = attributes.get('minSegmentSize', self.default_minSegmentSize)
        self.color = attributes.get('color', self.default_color)
        self.lineWidth = attributes.get('lineWidth', self.default_lineWidth)
        self.outputMode = attributes.get('outputMode', self.default_outputMode)
        self.segmentDataByID = {}
        self.segmentsByID = []
        self.width = self.height = self.radius * 2
        self.on_segment_clicked = Signal(signalName='on_segment_clicked')
        self.on_segment_mouse_enter = Signal(signalName='on_segment_mouse_enter')
        self.on_segment_mouse_exit = Signal(signalName='on_segment_mouse_exit')

    def AddSegment(self, value, segmentID, hint = None):
        self.segmentDataByID[segmentID] = SegmentData(value, segmentID, hint)

    def Reset(self):
        self.segmentDataByID = {}
        self.segmentsByID = {}

    def SetValues(self, values, segmentIDs = None, animate = False, animDuration = 1.0):
        self.Construct(animate, animDuration)

    def Construct(self, animate = True, animDuration = 1.0):
        self.Flush()
        values = [ data.value for data in self.segmentDataByID.values() ]
        if not sum(values) >= 1:
            return
        self._UpdateSegmentRatios(values)
        self.segmentsByID = self.ConstructSegments()
        if animate:
            self.AnimEntry(animDuration)

    def AnimEntry(self, animDuration):
        segments = sorted(self.segmentsByID.values(), key=lambda x: x.angle, reverse=True)
        for i, segment in enumerate(segments):
            self._AnimEntrySegment(animDuration, segment, i)

    def ConstructSegments(self):
        angle = 0.0
        segments = {}
        for data in self.GetSegmentData():
            color = self.GetSegmentColor(data.segmentID, data.value)
            segment = DonutSegment(parent=self, segmentID=data.segmentID, radius=self.radius, startAngle=angle, isClockwise=self.isClockwise, angle=2 * math.pi * (data.ratio - self.gapSize), colorStart=color, colorEnd=color, lineWidth=self.lineWidth, hint=data.hint, outputMode=self.outputMode)
            segment.on_clicked.connect(self.on_segment_clicked)
            segment.on_mouse_enter.connect(self.on_segment_mouse_enter)
            segment.on_mouse_exit.connect(self.on_segment_mouse_exit)
            segments[data.segmentID] = segment
            angle += data.ratio * 2 * math.pi

        return segments

    def _AnimEntrySegment(self, duration, segment, i):
        timeOffset = i * 0.025
        animations.FadeTo(segment, 0.0, 1.0, duration=duration, timeOffset=timeOffset)
        if segment.angle < 0.1 * math.pi:
            self._AnimEntrySmallSegment(duration * 0.5, segment, timeOffset)
        else:
            animations.MorphScalar(segment, 'end', 0.0, 1.0, duration=duration, timeOffset=timeOffset)

    def _AnimEntrySmallSegment(self, duration, segment, timeOffset):
        timeOffset += 0.3 * (1.0 - segment.angle / (0.5 * math.pi))
        angle = segment.startAngle + segment.angle / 2.0
        r = 0.15 * segment.radius
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        animations.MorphScalar(segment, 'left', x, segment.left, duration=duration, timeOffset=timeOffset)
        animations.MorphScalar(segment, 'top', y, segment.top, duration=duration, timeOffset=timeOffset)

    def _UpdateSegmentRatios(self, values):
        sumTotal = float(sum([ data.value for data in self.segmentDataByID.values() ]))
        sumRatio = 0
        for data in self.segmentDataByID.values():
            data.ratio = max(data.value / sumTotal, self.minSegmentSize)
            sumRatio += data.ratio

        for data in self.segmentDataByID.values():
            data.ratio /= sumRatio

    def GetSegmentColor(self, segmentID, value):
        data = self.segmentDataByID[segmentID]
        x = 0.3 + 0.7 * data.ratio
        return Color(*self.color).SetBrightness(x).GetRGBA()

    def GetSegmentData(self):
        segmentData = self.segmentDataByID.values()
        return sorted(segmentData, key=lambda data: data.value)
