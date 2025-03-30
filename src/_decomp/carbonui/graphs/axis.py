#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\axis.py
import math
import blue
import localization
from carbon.common.script.util.commonutils import StripTags
from signals import Signal
AXIS_TIGHT = 0
AXIS_FROM_ZERO = 1
AXIS_CUSTOM = 2
AXIS_FILTERED = 3

class AxisOrientation(object):
    HORIZONTAL = 0
    VERTICAL = 1


class InteractionLimit(object):
    NONE = 0
    DATA_RANGE = 1
    DATA_AND_VIEWPORT_RANGE = 2


def GetStrippedLabel(path, **kwargs):
    label = localization.GetByLabel(path, **kwargs)
    if isinstance(label, basestring):
        label = StripTags(label, stripOnly=['localized'])
    return label


def GetRangeFromSequences(*sequences):
    minv = None
    maxv = None
    for sequence in sequences:
        if sequence:
            v = min(sequence)
            if minv is None:
                minv = v
            else:
                minv = min(minv, v)
            v = max(sequence)
            if maxv is None:
                maxv = v
            else:
                maxv = max(maxv, v)

    return (minv, maxv)


def FixupRange(dataRange):
    dataRange = (float(dataRange[0]), float(dataRange[1]))
    if dataRange[0] > dataRange[1]:
        dataRange = (dataRange[1], dataRange[0])
    if dataRange[0] == dataRange[1]:
        dataRange = (dataRange[0], dataRange[0] + 0.1)
    return dataRange


class BaseAxis(object):

    def __init__(self, dataRange, viewportRange = (0.0, 1.0), visibleRange = None, behavior = AXIS_TIGHT, margins = (0.0, 0.0), interactionLimit = InteractionLimit.DATA_AND_VIEWPORT_RANGE, labelFormat = str):
        self._dataRange = FixupRange(dataRange)
        self._viewportRange = viewportRange
        self._visibleRange = FixupRange(visibleRange or dataRange)
        self._margins = margins
        self._behavior = behavior
        self._interactionLimit = interactionLimit
        self._labelFormat = labelFormat
        self.onChange = Signal(signalName='onChange')
        self._UpdateVisibleRange()

    def MapToView(self, value):
        return (value - self._visibleRange[0]) / (self._visibleRange[1] - self._visibleRange[0])

    def MapFromView(self, value):
        return self._visibleRange[0] + value * (self._visibleRange[1] - self._visibleRange[0])

    def MapToViewport(self, value):
        v = self.MapToView(value)
        return self._viewportRange[0] * (1 - v) + self._viewportRange[1] * v

    def MapFromViewport(self, value):
        v = (value - self._viewportRange[0]) / (self._viewportRange[1] - self._viewportRange[0])
        return self.MapFromView(v)

    def MapSequenceToViewport(self, sequence):
        visible = (self._viewportRange[1] - self._viewportRange[0]) / (self._visibleRange[1] - self._visibleRange[0])
        offset = self._viewportRange[0] - self._visibleRange[0] * visible
        return (offset + value * visible for value in sequence)

    def UpdateToViewportTransform(self, transform, column, dpiScaling = 1):
        visible = (self._viewportRange[1] - self._viewportRange[0]) / (self._visibleRange[1] - self._visibleRange[0])
        offset = (self._viewportRange[0] - self._visibleRange[0] * visible) * dpiScaling
        scale = visible * dpiScaling
        if column == 0:
            row0 = list(transform[0])
            row0[0] = scale
            row2 = list(transform[2])
            row2[0] = offset
            return (tuple(row0), transform[1], tuple(row2))
        else:
            row1 = list(transform[1])
            row1[1] = scale
            row2 = list(transform[2])
            row2[1] = offset
            return (transform[0], tuple(row1), tuple(row2))

    def SetViewportRange(self, viewport):
        if self._viewportRange == viewport:
            return
        self._viewportRange = viewport
        self._OnChange()

    def GetViewportRange(self):
        return self._viewportRange

    def GetViewportSize(self):
        return self._viewportRange[1] - self._viewportRange[0]

    def SetDataRange(self, dataRange):
        self._dataRange = dataRange
        self._UpdateVisibleRange()
        self._OnChange()

    def ZoomOn(self, visibleRange):
        if visibleRange is None:
            self._UpdateVisibleRange()
            self._OnChange()
            return
        scope = self._dataRange[1] - self._dataRange[0]
        if self._behavior == AXIS_FROM_ZERO:
            self._visibleRange = (self._visibleRange[0], visibleRange[1] + scope * self._margins[1])
        elif self._behavior == AXIS_TIGHT:
            self._visibleRange = (visibleRange[0] - scope * self._margins[0], visibleRange[1] + scope * self._margins[1])
        else:
            self._visibleRange = visibleRange
        self._visibleRange = FixupRange(self._visibleRange)
        self._OnChange()

    def GetDataRange(self):
        return self._dataRange

    def GetVisibleRange(self):
        return self._visibleRange

    def SetVisibleRange(self, visibleRange):
        if self._visibleRange != visibleRange:
            self._visibleRange = visibleRange
            self._OnChange()

    def GetBehavior(self):
        return self._behavior

    def SetBehavior(self, behavior):
        if self._behavior == behavior:
            return
        self._behavior = behavior
        self._UpdateVisibleRange()
        self._OnChange()

    def _UpdateVisibleRange(self):
        scope = self._dataRange[1] - self._dataRange[0]
        if self._behavior == AXIS_FROM_ZERO:
            self._visibleRange = (min(self._dataRange[0], 0), self._dataRange[1] + scope * self._margins[1])
        elif self._behavior == AXIS_TIGHT:
            self._visibleRange = (self._dataRange[0] - scope * self._margins[0], self._dataRange[1] + scope * self._margins[1])
        self._visibleRange = FixupRange(self._visibleRange)

    def Zoom(self, amount, ratio = 0.5):
        self._behavior = AXIS_CUSTOM
        scope = self._visibleRange[1] - self._visibleRange[0]
        amount *= scope
        if not amount:
            return
        oldVisibleRange = self._visibleRange
        self._visibleRange = (self._visibleRange[0] + amount * ratio, self._visibleRange[1] - amount * (1.0 - ratio))
        dataRange = abs(self.MapToView(self._dataRange[0]) - self.MapToView(self._dataRange[1]))
        if dataRange > 200 and amount > 0 or dataRange < 0.01 and amount < 0:
            self._visibleRange = oldVisibleRange
            return
        if self._visibleRange[1] <= self._visibleRange[0] or math.isinf(self._visibleRange[0]) or math.isinf(self._visibleRange[1]):
            self._visibleRange = oldVisibleRange
            return
        if abs(self.MapToViewport(self._dataRange[0]) - self.MapToViewport(self._dataRange[1])) < 1:
            self._visibleRange = oldVisibleRange
            return
        self._OnChange()

    def Pan(self, amount):
        scope = self._visibleRange[1] - self._visibleRange[0]
        delta = amount * scope
        if not delta:
            return
        self._behavior = AXIS_CUSTOM
        if self._interactionLimit == InteractionLimit.DATA_AND_VIEWPORT_RANGE:
            if self._visibleRange[1] + delta < self._dataRange[0]:
                delta = self._dataRange[0] - self._visibleRange[1]
            if self._visibleRange[0] + delta > self._dataRange[1]:
                delta = self._dataRange[1] - self._visibleRange[0]
        elif self._interactionLimit == InteractionLimit.DATA_RANGE:
            if self._visibleRange[0] + delta < self._dataRange[0]:
                delta = self._dataRange[0] - self._visibleRange[0]
            if self._visibleRange[1] + delta > self._dataRange[1]:
                delta = self._dataRange[1] - self._visibleRange[1]
        self._visibleRange = (self._visibleRange[0] + delta, self._visibleRange[1] + delta)
        self._OnChange()

    def GetTicks(self):
        return ()

    def GetTickLabel(self, tickValue):
        return self._labelFormat(tickValue)

    def _OnChange(self):
        self.onChange(self)

    def GetRangeText(self, start, end):
        return str(end - start)


class CategoryAxis(BaseAxis):

    def __init__(self, dataPoints, *args, **kwargs):
        super(CategoryAxis, self).__init__((-0.5, len(dataPoints) - 0.5), *args, **kwargs)
        self._dataPoints = dataPoints

    def GetDataPoints(self):
        return self._dataPoints

    def SetDataPoints(self, dataPoints, updateRange = True):
        self._dataPoints = dataPoints
        if updateRange:
            dataRange = FixupRange((-0.5, len(dataPoints) - 0.5))
            self.SetDataRange(dataRange)

    def MapDataPointsToViewport(self):
        return self.MapSequenceToViewport(xrange(len(self._dataPoints)))

    def GetTicks(self):
        return range(len(self._dataPoints))

    def GetTickLabel(self, tickValue):
        return self._labelFormat(self._dataPoints[tickValue])

    def GetRangeText(self, start, end):
        return ''


class AutoTicksAxis(BaseAxis):

    def __init__(self, dataRange, tickCount = 0, tickFilter = None, tickBase = 10, *args, **kwargs):
        super(AutoTicksAxis, self).__init__(dataRange, *args, **kwargs)
        self._tickCount = tickCount
        self._tickFilter = tickFilter
        self._ticks = []
        self._tickBase = tickBase
        self._UpdateTicks()

    def SetTickCount(self, tickCount):
        self._tickCount = tickCount
        self._OnChange()

    def GetTicks(self):
        return self._ticks

    def _UpdateTicks(self):
        if not self._tickCount:
            self._ticks = []
            return
        delta = (self._visibleRange[1] - self._visibleRange[0]) / self._tickCount
        delta = self._tickBase ** math.ceil(math.log(delta, self._tickBase))
        start = math.floor(self._visibleRange[0] / delta) * delta
        cnt = int((self._visibleRange[1] - self._visibleRange[0]) / delta)
        while cnt * 2 < self._tickCount:
            delta /= 2
            cnt = int((self._visibleRange[1] - self._visibleRange[0]) / delta)

        incr = 0
        result = []
        while start + incr <= self._visibleRange[1]:
            if not self._tickFilter or self._tickFilter(start + incr):
                if not result or result[-1] != start + incr:
                    result.append(start + incr)
            incr += delta

        self._ticks = result

    def _OnChange(self):
        self._UpdateTicks()
        super(AutoTicksAxis, self)._OnChange()


class AutoTicksCategoryAxis(CategoryAxis):

    def __init__(self, dataRange, tickCount = 0, tickFilter = None, tickBase = 10, *args, **kwargs):
        super(AutoTicksCategoryAxis, self).__init__(dataRange, *args, **kwargs)
        self._tickCount = tickCount
        self._tickFilter = tickFilter
        self._tickBase = tickBase
        self._ticks = []
        self._UpdateTicks()

    def SetTickCount(self, tickCount):
        self._tickCount = tickCount
        self._OnChange()

    def GetTicks(self):
        return self._ticks

    def _UpdateTicks(self):
        if not self._tickCount:
            self._ticks = []
            return
        delta = (self._visibleRange[1] - self._visibleRange[0]) / self._tickCount
        delta = self._tickBase ** math.ceil(math.log(delta, self._tickBase))
        a = math.floor(self._visibleRange[0] / delta) * delta
        cnt = int((self._visibleRange[1] - self._visibleRange[0]) / delta)
        while cnt * 2 < self._tickCount and delta > 1:
            delta /= 2
            cnt = int((self._visibleRange[1] - self._visibleRange[0]) / delta)

        result = []
        while a <= self._visibleRange[1]:
            if not self._tickFilter or self._tickFilter(a):
                result.append(int(a))
            a += delta

        self._ticks = result

    def _OnChange(self):
        self._UpdateTicks()
        super(AutoTicksCategoryAxis, self)._OnChange()


class MonthlyTimeAxis(CategoryAxis):

    def __init__(self, timestamps, *args, **kwargs):
        super(MonthlyTimeAxis, self).__init__(timestamps, *args, **kwargs)
        self._months = [GetStrippedLabel('/Carbon/UI/Common/Months/JanuaryShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/FebruaryShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/MarchShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/AprilShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/MayShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/JuneShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/JulyShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/AugustShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/SeptemberShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/OctoberShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/NovemberShort'),
         GetStrippedLabel('/Carbon/UI/Common/Months/DecemberShort')]

    def GetTicks(self):
        months = []
        for i, t in enumerate(self._dataPoints):
            if self._visibleRange[0] <= i <= self._visibleRange[1] and blue.os.GetTimeParts(t)[3] == 1:
                months.append(i)

        return months

    def GetTickLabel(self, tickValue):
        month = blue.os.GetTimeParts(self._dataPoints[tickValue])[1]
        return self._months[month - 1]

    def GetRangeText(self, start, end):
        return str(int(round(end - start)))
