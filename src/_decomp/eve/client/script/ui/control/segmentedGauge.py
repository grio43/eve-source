#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\segmentedGauge.py
import math
import uthread2
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.util.color import Color
from eve.client.script.ui.control.gauge import Gauge

class SegmentedGauge(Container):
    default_gapWidth = 1
    default_nsegments = 2
    default_color = Color.BLUE
    default_height = 6
    default_state = uiconst.UI_NORMAL

    def __init__(self, nsegments = default_nsegments, gapWidth = default_gapWidth, color = default_color, **kwargs):
        super(SegmentedGauge, self).__init__(**kwargs)
        self.nsegments = nsegments
        self.gapWidth = gapWidth
        self.color = color
        self.leadSegment = 0
        self.segments = [ self.CreateSegment(i) for i in range(0, nsegments) ]

    def CreateSegment(self, segmentNumber):
        return Gauge(parent=self, name='gauge_segment_{}'.format(segmentNumber), align=uiconst.TOLEFT_NOPUSH, state=uiconst.UI_DISABLED, color=self.color)

    def _OnSizeChange_NoBlock(self, newWidth, newHeight):
        segmentWidth = math.floor((newWidth - self.nsegments * self.gapWidth) / self.nsegments)
        remainder = (newWidth - self.nsegments * self.gapWidth) % self.nsegments
        for i in range(self.nsegments):
            segment = self.segments[i]
            segment.width = segmentWidth
            segment.left = i * (self.gapWidth + segmentWidth) + min(i, remainder)

    def SetValue(self, value, animate = True, duration = 1.0):
        self.value = value
        if animate:
            uthread2.StartTasklet(self._SetValueAsync, value, animate=animate, duration=duration)
        else:
            self._SetValueAsync(value, animate=animate, duration=duration)

    def _SetValueAsync(self, value, animate = True, duration = 0.3):
        valueForLeadSegment, newLeadSegment = math.modf(value / (1.0 / self.nsegments))
        newLeadSegment = int(newLeadSegment)
        distance = newLeadSegment - self.leadSegment
        if distance:
            segmentDuration = duration / distance
        else:
            segmentDuration = duration
        for i in range(self.leadSegment, newLeadSegment):
            self.segments[i].SetValue(1, animate=animate, duration=segmentDuration)
            if animate:
                uthread2.sleep(max(0, segmentDuration - 0.3))

        self.segments[newLeadSegment].SetValue(valueForLeadSegment, animate=animate, duration=segmentDuration)
        self.leadSegment = newLeadSegment
