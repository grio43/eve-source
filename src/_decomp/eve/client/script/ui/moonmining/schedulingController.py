#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\moonmining\schedulingController.py
import gametime
from carbon.common.lib.const import SEC, MIN, HOUR
from carbon.common.script.util.mathCommon import FloatCloseEnough
from eve.client.script.ui.moonmining import GetRangeTimeForSlider
from moonmining.const import MAXIMUM_EXTRACTION_DURATION, MINIMUM_EXTRACTION_DURATION
from signals import Signal
import mathext

class SchedulingController(object):

    def __init__(self, fuelExpiryTime):
        self.fuelExpiryTime = fuelExpiryTime
        self.startTime, maxValidTime = GetRangeTimeForSlider()
        self.maxValidTime = long(maxValidTime / HOUR) * HOUR
        self.currentTime = self.startTime
        self.validTimeRange = self.maxValidTime - self.startTime
        self.fullRange = MAXIMUM_EXTRACTION_DURATION * SEC
        self.maxValidPercentage = self.validTimeRange / float(self.fullRange)
        self.on_hours_changed = Signal(signalName='on_hours_changed')
        self.on_fuel_changed = Signal(signalName='on_fuel_changed')

    @property
    def minValidTime(self):
        now = gametime.GetWallclockTime()
        return now + MINIMUM_EXTRACTION_DURATION * SEC + 2 * MIN

    def GetSliderStartTime(self):
        return self.startTime

    def GetMinValidTime(self):
        return self.minValidTime

    def GetMaxValidTime(self):
        return self.maxValidTime

    def GetCurrentTime(self):
        return self.currentTime

    def SetTimestamp(self, timestamp, numParts = 1):
        self.SetCurrentTimestamp(timestamp, numParts=numParts)

    def GetCurrentTimeAsPercentage(self):
        return float(self.currentTime - self.startTime) / self.fullRange

    def SetTimestampFromPercentage(self, value):
        value = min(value, self.maxValidPercentage)
        newTimestamp = self._GetClampedTimestamp(value * self.fullRange + self.startTime)
        self.SetCurrentTimestamp(newTimestamp)

    def AddHour(self):
        self.AddNumHours(1)

    def SubtractHour(self):
        self.AddNumHours(-1)

    def AddNumHours(self, numHours, numParts = 1):
        self.SetCurrentTimestamp(self.GetCurrentTime() + numHours * HOUR, numParts=numParts)

    def SetCurrentTimestamp(self, timestamp, numParts = 1):
        timestamp = self._RoundTimestampToPartsOfHour(timestamp, numParts)
        timestamp = self._GetClampedTimestamp(timestamp)
        wasChange = self.currentTime != timestamp
        self.currentTime = long(self._GetClampedTimestamp(timestamp))
        self.on_hours_changed(wasChange)

    def _GetClampedTimestamp(self, timestamp):
        return mathext.clamp(timestamp, self.minValidTime, self.maxValidTime)

    def GetMaxTime(self):
        return self.maxValidTime

    def _RoundTimestampToPartsOfHour(self, timestamp, numParts):
        partOfHour = float(timestamp) % HOUR / HOUR
        if FloatCloseEnough(partOfHour, 1.0):
            numHours = 0
        else:
            numHours = self._RoundToParts(partOfHour, numParts)
        newTimestamp = long(timestamp / HOUR) * HOUR + numHours * HOUR
        return newTimestamp

    def _RoundToParts(self, hourValue, numParts):
        return round(hourValue * numParts) / float(numParts)

    def SetFuelExpiryTime(self, timestamp):
        self.fuelExpiryTime = timestamp
        self.on_fuel_changed()

    def GetFuelExpiryTime(self):
        return self.fuelExpiryTime
