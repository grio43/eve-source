#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\datepicker.py
import datetime
import time
import blue
import calendar
import datetimeutils
import gametime
import localization
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from dateutil import relativedelta
from eve.common.lib import appConst as const
from localization.formatters import FormatTimeIntervalShortWritten

class DatePicker(Container):
    __guid__ = 'xtriui.DatePicker'
    __nonpersistvars__ = []
    months = [localization.GetByLabel('UI/Common/Months/January'),
     localization.GetByLabel('UI/Common/Months/February'),
     localization.GetByLabel('UI/Common/Months/March'),
     localization.GetByLabel('UI/Common/Months/April'),
     localization.GetByLabel('UI/Common/Months/May'),
     localization.GetByLabel('UI/Common/Months/June'),
     localization.GetByLabel('UI/Common/Months/July'),
     localization.GetByLabel('UI/Common/Months/August'),
     localization.GetByLabel('UI/Common/Months/September'),
     localization.GetByLabel('UI/Common/Months/October'),
     localization.GetByLabel('UI/Common/Months/November'),
     localization.GetByLabel('UI/Common/Months/December')]

    def Startup(self, now = None, withTime = False, timeparts = 4, startYear = None, yearRange = None, set_value = None):
        self.timeparts = timeparts
        if now is None:
            now = time.gmtime()
        if startYear is None:
            startYear = const.calendarStartYear
        year = max(startYear, now[0])
        month = now[1]
        day = now[2]
        left = 0
        if yearRange is None:
            yRange = year - startYear + 1
        else:
            yRange = yearRange
        self.yearBase = year
        yearops = [ (localization.formatters.FormatNumeric(startYear + i, decimalPlaces=0), startYear + i) for i in xrange(yRange) ]
        self.ycombo = Combo(parent=self, label=localization.GetByLabel('UI/Common/DateWords/Year'), options=yearops, name='year', select=set_value[0] if set_value else year, callback=self.OnComboChange, pos=(left,
         0,
         0,
         0), align=uiconst.TOPLEFT, adjustWidth=True)
        left += self.ycombo.width + 4
        self.monthBase = month
        monthops = [ (self.months[i], i + 1) for i in xrange(12) ]
        self.mcombo = Combo(parent=self, label=localization.GetByLabel('UI/Common/DateWords/Month'), options=monthops, name='month', select=set_value[1] if set_value else month, callback=self.OnComboChange, pos=(left,
         0,
         0,
         0), align=uiconst.TOPLEFT, adjustWidth=True)
        left += self.mcombo.width + 4
        self.dayBase = day
        firstday, numdays = calendar.monthrange(year, month)
        dayops = [ (localization.formatters.FormatNumeric(i + 1, decimalPlaces=0), i + 1) for i in xrange(numdays) ]
        self.dcombo = Combo(parent=self, label=localization.GetByLabel('UI/Common/DateWords/Day'), options=dayops, name='day', select=set_value[2] if set_value else day, callback=self.OnComboChange, pos=(left,
         0,
         0,
         0), align=uiconst.TOPLEFT, adjustWidth=True)
        self.width = self.dcombo.left + self.dcombo.width
        self.height = self.ycombo.height
        if withTime:
            if set_value:
                index = self._GetTimeIndexFromHourAndMin(set_value[3], set_value[4])
            else:
                index = self.GetTimeIndex(now)
            hourops = self.GetTimeOptions()
            self.hourBase = now[3]
            self.minuteBase = now[4]
            left += self.dcombo.width + 4
            self.hcombo = Combo(parent=self, label=localization.GetByLabel('UI/Common/DateWords/Time'), options=hourops, name='time', select=index, callback=self.OnComboChange, pos=(left,
             0,
             0,
             0), align=uiconst.TOPLEFT, adjustWidth=True)
            self.width = self.hcombo.left + self.hcombo.width
            self.height = self.hcombo.height

    def OnComboChange(self, combo, header, value, *args):
        self.CheckDays()
        if hasattr(self, 'OnDateChange'):
            self.OnDateChange()

    def _ResetCombosToDefault(self):
        currentSelection = self.mcombo.selectedValue
        self.mcombo.LoadOptions([ (self.months[i], i + 1) for i in xrange(12) ])
        self.mcombo.SelectItemByValue(currentSelection)
        currentSelection = self.dcombo.selectedValue
        firstday, numdays = calendar.monthrange(self.ycombo.GetValue(), self.mcombo.GetValue())
        self.dcombo.LoadOptions([ (localization.formatters.FormatNumeric(i + 1, decimalPlaces=0), i + 1) for i in xrange(numdays) ])
        self.dcombo.SelectItemByValue(currentSelection)
        currentValue = self.GetValueAsDateTime()
        currentIndex = self._GetTimeIndexFromHourAndMin(currentValue.hour, currentValue.minute - 1)
        hourops = self.GetTimeOptions()
        self.hcombo.LoadOptions(hourops)
        self.hcombo.SelectItemByValue(currentIndex)

    def CheckDays(self):
        sely = self.ycombo.GetValue()
        selm = self.mcombo.GetValue()
        seld = self.dcombo.GetValue()
        firstday, numdays = calendar.monthrange(sely, selm)
        dayops = [ (str(i + 1), i + 1) for i in xrange(numdays) ]
        self.dcombo.LoadOptions(dayops, min(seld, numdays))

    def SetValueFromNow(self, seconds = 0, minutes = 0, hours = 0, days = 0, weeks = 0, months = 0, years = 0):
        now = datetime.datetime.utcnow()
        time_to_advance = relativedelta.relativedelta(seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks, months=months, years=years)
        target_time = now + time_to_advance
        target_time_tuple = target_time.timetuple()
        year = target_time_tuple.tm_year
        month = target_time_tuple.tm_mon
        day = target_time_tuple.tm_mday
        hour = target_time_tuple.tm_hour
        minute = target_time_tuple.tm_min
        self._ResetCombosToDefault()
        self.ycombo.SetValue(year)
        self.mcombo.SetValue(month)
        self.dcombo.SetValue(day)
        if getattr(self, 'hcombo', None) is not None:
            index = self._GetTimeIndexFromHourAndMin(hour, minute)
            self.hcombo.SetValue(index)

    def SetValue(self, gametime):
        time_datetime = datetimeutils.filetime_to_datetime(gametime)
        time_tuple = time_datetime.timetuple()
        year = time_tuple.tm_year
        month = time_tuple.tm_mon
        day = time_tuple.tm_mday
        hour = time_tuple.tm_hour
        minute = time_tuple.tm_min
        self.ycombo.SetValue(year)
        self.mcombo.SetValue(month)
        self.dcombo.SetValue(day)
        if getattr(self, 'hcombo', None) is not None:
            index = self._GetTimeIndexFromHourAndMin(hour, minute)
            self.hcombo.SetValue(index)
        self.OnComboChange(None, None, None, None)

    def GetValue(self):
        y = self.ycombo.GetValue()
        m = self.mcombo.GetValue()
        d = self.dcombo.GetValue()
        h = 0
        min = 0
        if getattr(self, 'hcombo', None) is not None:
            time = self.hcombo.GetValue()
            h = time / self.timeparts
            interval = 60 / self.timeparts
            min = time % self.timeparts * interval
        return blue.os.GetTimeFromParts(y, m, d, h, min, 0, 0)

    def GetValueAsDateTime(self):
        return datetimeutils.filetime_to_datetime(self.GetValue())

    def GetDurationFromNow(self):
        return relativedelta.relativedelta(self.GetValueAsDateTime(), datetime.datetime.utcnow())

    def HasDatePassed(self):
        wallclock_now = gametime.GetWallclockTimeNow()
        wallclock_destination = self.GetValue()
        if wallclock_destination - wallclock_now < 0:
            return True

    def GetDurationFromNowString(self, show_from = 'year', show_to = 'minute'):
        wallclock_now = gametime.GetWallclockTimeNow()
        wallclock_destination = self.GetValue()
        if wallclock_destination - wallclock_now < 0:
            return None
        return FormatTimeIntervalShortWritten(wallclock_destination - wallclock_now, showFrom=show_from, showTo=show_to)

    def GetTimeOptions(self, *args):
        hours = []
        counter = 0
        for h in xrange(0, 24):
            interval = 60 / self.timeparts
            for m in xrange(0, self.timeparts):
                min = m * interval
                timeStr = '%.2d:%.2d' % (h, min)
                hours.append((timeStr, counter))
                counter += 1

        return hours

    def GetTimeIndex(self, now, *args):
        if len(now) > 3:
            hour = now[3]
        else:
            hour = 12
        if len(now) > 4:
            min = now[4]
        else:
            min = 0
        return self._GetTimeIndexFromHourAndMin(hour, min)

    def _GetTimeIndexFromHourAndMin(self, hour, min):
        interval = 60 / self.timeparts
        index = hour * self.timeparts + min / interval
        if min % interval * 2 > interval:
            index += 1
        return index
