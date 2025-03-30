#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\eveCalendar.py
import calendar
import time
import blue
import eveLocalization
import eveicon
import uthread
import utillib
from bannedwords.client import bannedwords
from carbon.client.script.util.misc import GetAttrs
from carbon.common.script.util.format import FmtDate, GetTimeParts
from carbonui import TextColor, uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.util.various_unsorted import NiceFilter, SortListOfTuples
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from eve.client.script.ui.control.datepicker import DatePicker
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.user import SearchedUser
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.listgroup import ListGroup
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.control.themeColored import FrameThemeColored, FillThemeColored
import evetypes
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.neocom.ownerSearch import OwnerSearchWindow
from eve.client.script.ui.control import eveEditPlainText, eveIcon, eveLabel, eveScroll
from eve.client.script.ui.control.divider import Divider
import localization
from eve.client.script.ui.shared.userentry import User
from eve.common.lib import appConst
from eveexceptions import UserError
from globalConfig.getFunctions import IsContentComplianceControlSystemActive
from inventorycommon.util import IsNPC
from menu import MenuLabel
NUM_DAYROWS = 6
DAY_NAME_SHORT_TEXT = ['UI/Moonmining/MondayShort',
 'UI/Moonmining/TuesdayShort',
 'UI/Moonmining/WednesdayShort',
 'UI/Moonmining/ThursdayShort',
 'UI/Moonmining/FridayShort',
 'UI/Moonmining/SaturdayShort',
 'UI/Moonmining/SundayShort']
DAY_NAME_TEXT = ['/Carbon/UI/Common/Days/Monday',
 '/Carbon/UI/Common/Days/Tuesday',
 '/Carbon/UI/Common/Days/Wednesday',
 '/Carbon/UI/Common/Days/Thursday',
 '/Carbon/UI/Common/Days/Friday',
 '/Carbon/UI/Common/Days/Saturday',
 '/Carbon/UI/Common/Days/Sunday']

class CalendarWnd(Window):
    __guid__ = 'form.eveCalendarWnd'
    __notifyevents__ = []
    default_windowID = 'calendar'
    default_captionLabelPath = 'UI/Calendar/CalendarWindow/Caption'
    default_iconNum = 'res:/ui/Texture/WindowIcons/calendar.png'
    default_minSize = (580, 400)

    def ApplyAttributes(self, attributes):
        super(CalendarWnd, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        sm.GetService('neocom').BlinkOff('calendar')
        self.sr.leftSide = Container(name='leftSide', parent=self.sr.main, align=uiconst.TOLEFT, pos=(0, 0, 150, 0), padding=(6,
         const.defaultPadding,
         0,
         const.defaultPadding))
        self.sr.xDivider = Divider(name='xDivider', parent=self.sr.main, align=uiconst.TOLEFT, pos=(0,
         0,
         const.defaultPadding,
         0), state=uiconst.UI_NORMAL)
        self.sr.xDivider.Startup(self.sr.leftSide, 'width', 'x', 75, 200)
        self.sr.calendarForm = Calendar(pos=(0, 0, 0, 0), parent=self.sr.main, padding=(const.defaultPadding,
         1,
         2 * const.defaultPadding,
         const.defaultPadding))
        self.sr.leftSideTop = Container(name='leftSideTop', parent=self.sr.leftSide, align=uiconst.TOTOP, pos=(0, 0, 0, 40))
        self.sr.cbCont = ContainerAutoSize(name='cbCont', parent=self.sr.leftSide, align=uiconst.TOBOTTOM, pos=(0, 6, 0, 125), clipChildren=True)
        self.sr.leftSideBottom = Container(name='leftSideBottom', parent=self.sr.leftSide, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.sr.leftSideBottom.OnResize = self.OnResizeLeftSideBottom
        self.sr.updatedCont = Container(name='updatedCont', parent=self.sr.leftSideBottom, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 60))
        self.sr.yDivider = Divider(name='yDivider', parent=self.sr.leftSideBottom, align=uiconst.TOBOTTOM, pos=(0,
         0,
         0,
         const.defaultPadding), state=uiconst.UI_NORMAL)
        self.sr.yDivider.Startup(self.sr.updatedCont, 'height', 'y', 50, 205)
        self.sr.yDivider.OnSizeChanged = self.OnListsSizeChanged
        self.sr.todoCont = Container(name='todoCont', parent=self.sr.leftSideBottom, align=uiconst.TOALL, padTop=4)
        hdrText = localization.GetByLabel('UI/Calendar/CalendarWindow/UpcomingEvents')
        eveLabel.EveLabelMedium(text=hdrText, parent=self.sr.todoCont, align=uiconst.TOTOP, bold=True, height=18)
        self.sr.toDoForm = EventList(pos=(0, 0, 0, 0), parent=self.sr.todoCont, name='toDoForm', listentryClass=CalendarListEntry, getEventsFunc=sm.GetService('calendar').GetMyNextEvents, header=hdrText, listType='upcomingEvents')
        hdrText = localization.GetByLabel('UI/Calendar/CalendarWindow/LatestUpdates')
        eveLabel.EveLabelMedium(text=hdrText, parent=self.sr.updatedCont, align=uiconst.TOTOP, bold=True, height=18)
        self.sr.changesForm = UpdateEventsList(pos=(0, 0, 0, 0), parent=self.sr.updatedCont, name='changesForm', listentryClass=CalendarUpdatedEntry, getEventsFunc=sm.GetService('calendar').GetMyChangedEvents, header=hdrText, listType='latestUpdates')
        self.AddCheckBoxes()
        self.sr.cbCont.height = sum([ each.height for each in self.sr.cbCont.children ])
        Button(parent=self.sr.leftSideTop, label=localization.GetByLabel('UI/Calendar/CalendarWindow/NewEvent'), func=self.CreateNewEvent, pos=(0, 7, 0, 0), fixedheight=20)

    def AddCheckBoxes(self, *args):
        self.sr.cbCont.Flush()
        eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Calendar/CalendarWindow/Filters'), parent=self.sr.cbCont, align=uiconst.TOTOP, bold=True, height=18, padTop=3)
        checkboxInfo = [(localization.GetByLabel('UI/Calendar/CalendarWindow/GroupPersonal'), 'calendarTagCheked_%s' % appConst.calendarTagPersonal, True)]
        if session.corpid and not IsNPC(session.corpid):
            checkboxInfo.append((localization.GetByLabel('UI/Calendar/CalendarWindow/GroupCorp'), 'calendarTagCheked_%s' % appConst.calendarTagCorp, True))
        if session.allianceid:
            checkboxInfo.append((localization.GetByLabel('UI/Calendar/CalendarWindow/GroupAlliance'), 'calendarTagCheked_%s' % appConst.calendarTagAlliance, True))
        checkboxInfo.append((localization.GetByLabel('UI/Calendar/CalendarWindow/GroupCcp'), 'calendarTagCheked_%s' % appConst.calendarTagCCP, True))
        checkboxInfo.append((localization.GetByLabel('UI/Calendar/CalendarWindow/GroupAutomated'), 'calendarTagCheked_%s' % appConst.calendarTagAutomated, True))
        checkboxInfo.append((localization.GetByLabel('UI/Calendar/CalendarWindow/DeclinedEvents'), 'showDeclined', True))
        checkboxInfo.append((localization.GetByLabel('UI/Calendar/CalendarWindow/ShowTimestamp'), 'showTimestamp', True))
        self.sr.checkboxes = []
        for label, settingsKey, defaultValue in checkboxInfo:
            is_checked = 'calendar_%s' % settingsKey
            cb = Checkbox(text=label, parent=self.sr.cbCont, settingsKey=settingsKey, defaultValue=defaultValue, align=uiconst.TOTOP, padLeft=6, callback=self.DisplayCheckboxesChecked, checked=settings.user.ui.Get(is_checked, 1))
            self.sr.checkboxes.append(cb)

    def DisplayCheckboxesChecked(self, cb):
        config = 'calendar_%s' % cb.name
        settings.user.ui.Set(config, cb.checked)
        sm.ScatterEvent('OnCalendarFilterChange')

    def CreateNewEvent(self, *args):
        day = self.sr.calendarForm.selectedDay
        if day and not sm.GetService('calendar').IsInPast(day.year, day.month, day.monthday, allowToday=1):
            year = day.year
            month = day.month
            monthday = day.monthday
        else:
            eve.Message('CalendarCannotPlanThePast2')
            now = blue.os.GetWallclockTime()
            year, month, wd, monthday, hour, min, sec, ms = GetTimeParts(now)
        if not sm.GetService('calendar').IsInPast(year, month, monthday, allowToday=1):
            sm.GetService('calendar').OpenNewEventWnd(year, month, monthday)

    def OnListsSizeChanged(self, *args):
        h = self.sr.updatedCont.height
        l, t, w, absHeight = self.sr.leftSideBottom.GetAbsolute()
        if h > absHeight:
            h = absHeight
            ratio = float(h) / absHeight
            settings.user.ui.Set('calendar_listRatio', ratio)
            self._OnResize()
            return
        ratio = float(h) / absHeight
        settings.user.ui.Set('calendar_listRatio', ratio)

    def OnResizeLeftSideBottom(self, *args):
        if self and not self.destroyed and GetAttrs(self, 'sr', 'updatedCont'):
            l, t, w, absHeight = self.sr.leftSideBottom.GetAbsolute()
            scrollHeight = absHeight - 64
            ratio = settings.user.ui.Get('calendar_listRatio', 0.5)
            h = int(ratio * absHeight)
            if h > scrollHeight:
                h = scrollHeight
            self.sr.updatedCont.height = max(64, h)
            self.sr.yDivider.max = scrollHeight
        uthread.new(self.UpdateIndicators)

    def UpdateIndicators(self, *args):
        blue.pyos.synchro.Yield()
        self.sr.changesForm.UpdateMoreIndicators()
        self.sr.toDoForm.UpdateMoreIndicators()

    def _OnResize(self, *args):
        Window._OnResize(self)
        self.sr.calendarForm._OnResize()
        self.sr.changesForm.OnResize()
        self.sr.toDoForm.OnResize()

    def OnExpanded(self, *args):
        super(CalendarWnd, self).OnExpanded(*args)
        uthread.new(self.OnExpanded_thread)

    def OnExpanded_thread(self, *args):
        blue.pyos.synchro.SleepWallclock(50)
        if self and not self.destroyed:
            self.UpdateIndicators()


class Calendar(Container):
    __guid__ = 'form.eveCalendar'
    __notifyevents__ = ['OnReloadCalendar', 'OnReloadEvents', 'OnCalendarFilterChange']
    default_left = 0
    default_top = 0
    default_width = 256
    default_height = 256

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.GetService('calendar').GetEventResponses()
        self.monthInView = None
        self.allDayBoxes = []
        self.allDayBoxesByRows = {}
        self.allHeaderBoxes = []
        self.allDayRows = {}
        self.dayBoxesByDates = {}
        self.headerHeight = 24
        self.dayPadding = 1
        self.isTabStop = 1
        self.selectedDay = None
        self.disbleForward = False
        self.disbleBack = False
        self.Setup()
        self.InsertData()

    def Setup(self):
        sm.RegisterNotify(self)
        now = blue.os.GetWallclockTime()
        year, month, wd, day, hour, min, sec, ms = GetTimeParts(now)
        self.today = (year, month, day)
        self.calendar = calendar.Calendar()
        self.monthTextCont = Container(name='monthTextCont', parent=self, align=uiconst.TOTOP, pos=(0, 10, 0, 32))
        self.sr.gridCont = Container(name='gridCont', parent=self, align=uiconst.TOALL, pos=(0,
         0,
         0,
         const.defaultPadding))
        self.InsertBrowseControls()
        boxWidth = boxHeight = 30
        self.allHeaderBoxes = []
        self.allDayBoxes = []
        self.allDayBoxesByRows = {}
        row = Container(name='row', parent=self.sr.gridCont, align=uiconst.TOTOP, pos=(0,
         0,
         0,
         self.headerHeight))
        for j in xrange(0, const.calendarNumDaysInWeek):
            box = CalendarHeader(name='box', parent=row, align=uiconst.TOLEFT, pos=(0,
             0,
             boxWidth,
             0), padding=(self.dayPadding,
             self.dayPadding,
             self.dayPadding,
             self.dayPadding))
            self.allHeaderBoxes.append(box)
            setattr(self.sr, '%s_%s' % (0, j), box)

        row = None
        for i in xrange(1, NUM_DAYROWS + 1):
            row = Container(name='row', parent=self.sr.gridCont, align=uiconst.TOTOP, pos=(0,
             0,
             0,
             boxHeight))
            self.allDayRows[i] = row
            daysInRow = []
            box = None
            for j in xrange(0, const.calendarNumDaysInWeek):
                configname = '%s_%s' % (i, j)
                box = self.GetDay(row, boxWidth, configname)
                self.allDayBoxes.append(box)
                daysInRow.append(box)
                setattr(self.sr, configname, box)

            if box is not None:
                box.align = uiconst.TOALL
                box.width = 0
            self.allDayBoxesByRows[i] = daysInRow

        if row is not None:
            row.align = uiconst.TOALL
            row.height = 0
        self.SetSizes()
        self.sr.gridCont._OnSizeChange_NoBlock = self.OnGridContainerSize

    def InsertBrowseControls(self, *args):
        self.sr.backBtn = Button(name='BackBtn', align=uiconst.TOLEFT, parent=self.monthTextCont, texturePath=eveicon.navigate_back, iconSize=24, iconPadding=-4, func=self.OnBackBtn, hint=localization.GetByLabel('UI/Calendar/Hints/Previous'))
        self.sr.fwdBtn = Button(name='FwdBtn', parent=self.monthTextCont, align=uiconst.TOLEFT, padLeft=4, texturePath=eveicon.navigate_forward, iconSize=24, iconPadding=-4, func=self.OnFwdBtn, hint=localization.GetByLabel('UI/Calendar/Hints/Next'))
        self.sr.todayBtn = Button(parent=self.monthTextCont, label=localization.GetByLabel('UI/Calendar/CalendarWindow/Today'), func=self.GetToday, align=uiconst.TOPRIGHT, fixedheight=20)

    def ChangeBrowseDisplay(self, btn, disable = 0):
        if disable:
            btn.opacity = 0.3
            btn.state = uiconst.UI_DISABLED
        else:
            btn.opacity = 1.0
            btn.state = uiconst.UI_NORMAL

    def GetDay(self, parent, width, configname):
        box = CalendarDay(name='box', parent=parent, align=uiconst.TOLEFT, pos=(0,
         0,
         width,
         0), padding=(self.dayPadding,
         self.dayPadding,
         self.dayPadding,
         self.dayPadding), configname=configname)
        box.DoClickDay = self.DoClickDay
        box.DoDblClickDay = self.DoDblClickDay
        return box

    def GetDayNameText(self, dayNumber):
        dayName = localization.GetByLabel(DAY_NAME_SHORT_TEXT[dayNumber])
        return dayName

    def GetToday(self, *args):
        self.ResetBrowse()
        self.InsertData()

    def ResetBrowse(self, *args):
        self.disbleBack = False
        self.disbleForward = False
        self.ChangeBrowseDisplay(self.sr.backBtn, disable=self.disbleBack)
        self.ChangeBrowseDisplay(self.sr.fwdBtn, disable=self.disbleForward)

    def SetMonth(self, year, month, updateInView = 0, *args):
        if updateInView:
            self.yearMonthInView = (year, month)
        i = 1
        j = 0
        self.dayBoxesByDates = {}
        self.lastNextMonthDay = 0
        daysInMonth = self.calendar.monthdayscalendar(year, month)
        firstRow = daysInMonth[0]
        numEmptyDaysBefore = firstRow.count(0)
        emptyDaysBefore = []
        if emptyDaysBefore > 0:
            newYear, newMonth = sm.GetService('calendar').GetBrowsedMonth(-1, year, month)
            monthRange = calendar.monthrange(newYear, newMonth)
            emptyDaysBefore = [ d for d in xrange(monthRange[1], monthRange[1] - numEmptyDaysBefore, -1) ]
        for weekNumber, week in enumerate(daysInMonth):
            for monthday in week:
                notInMonth = 0
                if monthday == 0:
                    if weekNumber == 0:
                        monthday = emptyDaysBefore.pop(-1)
                        notInMonth = -1
                    else:
                        self.lastNextMonthDay += 1
                        monthday = self.lastNextMonthDay
                        notInMonth = 1
                self.ChangeDayBox(i, j, year, month, monthday, notInMonth)
                j += 1

            j = 0
            i += 1

        for i in xrange(i, NUM_DAYROWS + 1):
            for j in xrange(0, const.calendarNumDaysInWeek):
                self.lastNextMonthDay += 1
                monthday = self.lastNextMonthDay
                self.ChangeDayBox(i, j, year, month, monthday, notInMonth=1)

        self.SetMonthText(year, month)
        self.LoadEvents()

    def ChangeMonth(self, direction = 1, selectDay = 1, *args):
        year, month = self.yearMonthInView
        if direction == -1 and self.disbleBack or direction == 1 and self.disbleForward:
            return False
        year, month = sm.GetService('calendar').GetBrowsedMonth(direction, year, month)
        self.yearMonthInView = (year, month)
        self.SetMonth(year, month)
        now = blue.os.GetWallclockTime()
        rlYear, rlMonth, wd, day, hour, min, sec, ms = GetTimeParts(now)
        nowNumMonths = rlYear * 12 + rlMonth
        thenNumMonths = year * 12 + month
        difference = thenNumMonths - nowNumMonths
        self.disbleForward = 0
        self.disbleBack = 0
        if direction == 1 and difference >= const.calendarViewRangeInMonths:
            self.disbleForward = 1
        elif direction == -1 and -difference >= const.calendarViewRangeInMonths:
            self.disbleBack = 1
        self.ChangeBrowseDisplay(self.sr.backBtn, disable=self.disbleBack)
        self.ChangeBrowseDisplay(self.sr.fwdBtn, disable=self.disbleForward)
        self.selectedDay = self.CrawlForValidDay(self.selectedDay, direction, 'day')
        if selectDay:
            self.SelectDay()
        return True

    def SetCurrentRLMonth(self, selectToday = True, *args):
        now = blue.os.GetWallclockTime()
        year, month, wd, monthday, hour, min, sec, ms = GetTimeParts(now)
        self.yearMonthInView = (year, month)
        self.SetMonth(year, month)
        if selectToday:
            self.CrawlForAndSetMonthday(monthday)

    def ChangeDayBox(self, i, j, year, month, monthday = 0, notInMonth = 0):
        day = self.sr.get('%s_%s' % (i, j), None)
        if day:
            today = False
            if notInMonth == 0:
                self.dayBoxesByDates[monthday] = day
                if self.today == (year, month, monthday):
                    today = True
            day.SetDay(year, month, monthday=monthday, notInMonth=notInMonth, today=today)

    def SelectDay(self, *args):
        if self.selectedDay is None:
            self.selectedDay = self.sr.get('1_0', None)
        if self.selectedDay:
            for dayBox in self.allDayBoxes:
                if dayBox != self.selectedDay:
                    dayBox.SetSelectedFrameState(on=0)

            self.selectedDay.SetSelectedFrameState(on=1)

    def SelectNextDay(self, direction = 1, weekOrDay = 'day', *args):
        currentlySelected = self.selectedDay
        if currentlySelected is None:
            newSelected = self.sr.get('1_0', None)
        else:
            newSelected = self.FindAnotherDay(currentlySelected, direction, weekOrDay)
        if newSelected:
            if newSelected.disabled:
                wasChanged = self.ChangeMonth(direction, selectDay=0)
                if wasChanged == False:
                    return
                validDay = self.CrawlForValidDay(newSelected, direction, weekOrDay)
                newSelected = validDay
            self.selectedDay = newSelected
        self.SelectDay()

    def CrawlForValidDay(self, newSelected, direction, weekOrDay, *args):
        configname = newSelected.configname
        row, col = configname.split('_')
        if direction == -1:
            row = NUM_DAYROWS
        elif direction == 1:
            row = 1
        configname = '%s_%s' % (row, col)
        newSelected = self.sr.get(configname, None)
        while newSelected.disabled:
            newSelected = self.FindAnotherDay(newSelected, direction, weekOrDay)

        return newSelected

    def CrawlForMonthday(self, monthday, *args):
        for day in self.allDayBoxes:
            if day.monthday == monthday and not day.disabled:
                return day

    def CrawlForAndSetMonthday(self, monthday, *args):
        day = self.CrawlForMonthday(monthday)
        if day:
            self.selectedDay = day
            self.SelectDay()

    def OpenDay(self, *args):
        if self.selectedDay is not None:
            self.selectedDay.OnDblClickDay()

    def DoClickDay(self, day, *args):
        uthread.new(self.DoClickDay_thread, day)

    def DoClickDay_thread(self, day):
        if day.disabled:
            return
        self.selectedDay = day
        self.SelectDay()

    def DoDblClickDay(self, day, *args):
        if GetAttrs(day, 'disabled'):
            monthday = day.monthday
            self.ChangeMonth(day.disabled, selectDay=0)
            self.CrawlForAndSetMonthday(monthday)
        else:
            day.OpenSingleDayWnd()

    def FindAnotherDay(self, selectedDay, direction, weekOrDay = 'day'):
        newSelected = selectedDay
        index = self.allDayBoxes.index(selectedDay)
        if weekOrDay == 'day':
            if direction == -1:
                if index == 0:
                    newSelected = self.allDayBoxes[-1]
                else:
                    newSelected = self.allDayBoxes[index - 1]
            elif direction == 1:
                if len(self.allDayBoxes) > index + 1:
                    newSelected = self.allDayBoxes[index + 1]
                else:
                    newSelected = self.allDayBoxes[0]
        elif weekOrDay == 'week':
            configname = selectedDay.configname
            row, col = configname.split('_')
            row = int(row)
            col = int(col)
            if direction == -1:
                previousRow = row - 1
                newRow = self.allDayBoxesByRows.get(previousRow, None)
                if newRow is None:
                    newRow = self.allDayBoxesByRows.get(len(self.allDayBoxesByRows), None)
                    if newRow is None:
                        newRow = self.allDayBoxesByRows.get(1)
                newSelected = newRow[col]
            elif direction == 1:
                nextRow = row + 1
                newRow = self.allDayBoxesByRows.get(nextRow, None)
                if newRow is None:
                    newRow = self.allDayBoxesByRows.get(1)
                newSelected = newRow[col]
        return newSelected

    def AddMonthText(self, text = '', *args):
        if self.sr.Get('monthText', None) is None:
            self.sr.monthText = eveLabel.EveCaptionMedium(text=text, parent=self.monthTextCont, state=uiconst.UI_NORMAL, align=uiconst.CENTERTOP)
        return self.sr.monthText

    def SetMonthText(self, year, month, *args):
        self.AddMonthText()
        text = sm.GetService('calendar').GetMonthText(year, month)
        self.sr.monthText.text = text

    def SetHeader(self, *args):
        j = 0
        i = 0
        for j in xrange(0, const.calendarNumDaysInWeek):
            dayName = self.GetDayNameText(j)
            day = self.sr.get('%s_%s' % (i, j), None)
            if day:
                day.SetDayName(dayName)
            j += 1

    def SetSizes(self, size = None):
        if size is None:
            w, h = self.sr.gridCont.GetAbsoluteSize()
        else:
            w, h = size
        newBoxWidth = w / const.calendarNumDaysInWeek
        newBoxHeight = (h - self.headerHeight) / NUM_DAYROWS
        newBoxWidth -= 2 * self.dayPadding
        newBoxHeight -= 2 * self.dayPadding
        for box in self.allHeaderBoxes:
            box.width = newBoxWidth

        row = None
        for row in self.allDayRows.values():
            row.height = newBoxHeight

        if row is not None:
            row.height = 0
        counter = 0
        for box in self.allDayBoxes:
            counter += 1
            if counter >= const.calendarNumDaysInWeek:
                counter = 0
            else:
                box.width = newBoxWidth
            box.CheckEventsClipped()

        return (newBoxWidth, newBoxHeight)

    def InsertData(self, *args):
        self.SetCurrentRLMonth()
        self.SetHeader()

    def LoadEventsToADay(self, date, eventsThisDay):
        dayBox = self.dayBoxesByDates.get(date, None)
        if dayBox is None:
            return
        dayBox.LoadEvents(eventsThisDay)

    def LoadEvents(self, *args):
        yearInView, monthInView = self.yearMonthInView
        events = sm.GetService('calendar').GetEventsByMonthYear(monthInView, yearInView)
        showTag = sm.GetService('calendar').GetActiveTags()
        eventsByDates = {}
        for eventKV in events:
            if eventKV.isDeleted:
                continue
            year, month, wd, day, hour, minute, sec, ms = blue.os.GetTimeParts(eventKV.eventDateTime)
            ts = eventKV.eventDateTime - eveLocalization.GetTimeDelta() * const.SEC
            timeStr = localization.formatters.FormatDateTime(value=ts, dateFormat='none', timeFormat='short')
            eventKV.eventTimeStamp = timeStr
            if showTag is None or showTag & eventKV.flag != 0:
                eventsThisDay = eventsByDates.get(day, {})
                eventsThisDay[eventKV.eventID] = eventKV
                eventsByDates[day] = eventsThisDay

        for date, eventsThisDay in eventsByDates.iteritems():
            self.LoadEventsToADay(date, eventsThisDay)

    def OnKeyDown(self, vkey, flag, *args):
        if vkey == uiconst.VK_RIGHT:
            self.SelectNextDay(1)
        elif vkey == uiconst.VK_LEFT:
            self.SelectNextDay(-1)
        elif vkey == uiconst.VK_UP:
            self.SelectNextDay(-1, weekOrDay='week')
        elif vkey == uiconst.VK_DOWN:
            self.SelectNextDay(1, weekOrDay='week')
        elif vkey == uiconst.VK_RETURN:
            self.OpenDay()

    def OnSetFocus(self, *args):
        self.SelectDay()

    def OnBackBtn(self, *args):
        self.ChangeMonth(-1)

    def OnFwdBtn(self, *args):
        self.ChangeMonth()

    def OnCalendarFilterChange(self, *args):
        self.OnReloadCalendar()

    def OnGridContainerSize(self, displayWidth, displayHeight):
        self.SetSizes((displayWidth, displayHeight))

    def OnReloadCalendar(self, *args):
        year, month = self.yearMonthInView
        self.SetMonth(year, month)

    def OnReloadEvents(self, *args):
        self.LoadEvents()


class CalendarDay(Container):
    default_left = 0
    default_top = 0
    default_width = 256
    default_height = 256
    default_name = 'CalendarDay'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.year = None
        self.month = None
        self.monthday = 0
        self.events = {}
        self.eventHeight = 14
        self.disabled = 0
        self.configname = attributes.get('configname', None)
        self.Prepare_()

    def Prepare_(self, *args):
        self.sr.day = Container(name='dayNumberCont', parent=self, align=uiconst.TOALL, pos=(1, 1, 1, 1))
        self.sr.dayNumberCont = Container(name='dayNumberCont', parent=self.sr.day, align=uiconst.TOTOP, pos=(0, 0, 0, 12), state=uiconst.UI_NORMAL)
        self.sr.moreCont = Container(name='moreCont', parent=self.sr.day, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 10), state=uiconst.UI_HIDDEN, padding=(0, 0, 0, 0))
        self.AddMoreContFill()
        self.AddFill()
        self.AddFrame()
        self.sr.emptyDay = Container(name='emptyDay', parent=self.sr.day, align=uiconst.TOALL, pos=(0, 0, 0, 0), clipChildren=1)
        self.sr.emptyDay.state = uiconst.UI_NORMAL
        self.sr.dayNumberCont.OnDblClick = self.OnDblClickDay
        self.sr.dayNumberCont.OnMouseDown = self.OnMouseClickDay
        self.sr.dayNumberCont.GetMenu = self.GetMenu
        self.sr.emptyDay.OnDblClick = self.OnDblClickDay
        self.sr.emptyDay.OnMouseDown = self.OnMouseClickDay
        self.sr.emptyDay.GetMenu = self.GetMenu
        self.sr.fill.SetOrder(-1)
        self.sr.todayFill.SetOrder(-1)

    def AddMoreContFill(self, *args):
        icon = eveIcon.Icon(icon='ui_38_16_229', parent=self.sr.moreCont, pos=(0, -3, 16, 16), align=uiconst.CENTERTOP, idx=0, ignoreSize=True)
        icon.OnClick = self.OnMoreClick

    def AddFill(self, *args):
        self.sr.fill = FillThemeColored(parent=self, padding=1, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.5)

    def AddFrame(self, *args):
        self.sr.frame = FrameThemeColored(parent=self, name='frame', frameConst=uiconst.FRAME_BORDER1_CORNER0, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.1)
        self.sr.todayFill = Frame(parent=self, name='todayFill', frameConst=uiconst.FRAME_FILLED_CORNER0, padding=(1, 1, 1, 1), color=(0.5, 0.5, 0.5, 0.75))
        self.sr.selectedFrame = Frame(parent=self, name='frame', frameConst=uiconst.FRAME_BORDER1_CORNER0, color=(0.5, 0.5, 0.5, 0.1), padding=(1, 1, 1, 1), state=uiconst.UI_HIDDEN)

    def AddDayNumber(self, text = '', *args):
        if self.sr.Get('dayNumberText', None) is None:
            self.sr.dayNumberText = eveLabel.EveLabelMedium(text=text, parent=self.sr.dayNumberCont, state=uiconst.UI_DISABLED, left=1, align=uiconst.TOPRIGHT)
        return self.sr.dayNumberText

    def SetDayNumber(self, text = None, *args):
        self.AddDayNumber()
        if text is not None:
            text = localization.formatters.FormatNumeric(text, decimalPlaces=0)
            self.sr.dayNumberText.text = text

    def SetDayInfo(self, year, month, monthday = 0, *args):
        self.year = year
        self.month = month
        self.monthday = monthday

    def SetDay(self, year, month, monthday = 0, notInMonth = 0, today = False):
        self.SetDayNumber(text=monthday)
        self.ChangeDayVisibility(disabled=notInMonth)
        self.ClearDay()
        self.SetDayInfo(year, month, monthday=monthday)
        self.SetTodayMarker(today=today)

    def ChangeDayVisibility(self, disabled = 1, *args):
        self.disabled = disabled
        self.SetFillState(visible=not disabled)
        self.SetFrameState(visible=disabled)
        self.SetDayVisibility(visible=not disabled)

    def SetFrameState(self, visible = 1):
        self.sr.frame.SetAlpha([0.0, 0.4][bool(visible)])

    def SetFillState(self, visible = 1):
        self.sr.fill.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][bool(visible)]

    def SetDayVisibility(self, visible = 1):
        self.sr.day.opacity = [0.4, 1.0][bool(visible)]

    def SetTodayMarker(self, today = False, *args):
        self.sr.todayFill.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][today == True]

    def GetMenu(self, *args):
        return self.GetMenuFunction(*args)

    def GetMenuFunction(self, *args):
        m = []
        if self.disabled:
            return m
        if not sm.GetService('calendar').IsInPast(self.year, self.month, self.monthday, allowToday=1):
            m += [(MenuLabel('/Carbon/UI/Calendar/CreateNewEvent'), self.OpenNewEventWnd)]
        if not self.disabled:
            m += [(MenuLabel('/Carbon/UI/Calendar/ViewDay'), self.OpenSingleDayWnd)]
        return m

    def SetSelectedFrameState(self, on = 0):
        self.sr.selectedFrame.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][on]

    def OnMouseClickDay(self, *args):
        self.DoClickDay(self)

    def DoClickDay(self, object):
        self.SetSelectedFrameState(on=1)

    def OnDblClickDay(self, *args):
        self.DoDblClickDay(self)

    def DoDblClickDay(self, day, *args):
        self.OpenSingleDayWnd()

    def OpenNewEventWnd(self, *args):
        sm.GetService('calendar').OpenNewEventWnd(self.year, self.month, self.monthday)

    def OpenSingleDayWnd(self, *args):
        sm.GetService('calendar').OpenSingleDayWnd('day', self.year, self.month, self.monthday, self.events)

    def ClearDay(self, *args):
        self.events = {}
        self.CheckEventsClipped()
        self.sr.emptyDay.Flush()

    def LoadEvents(self, eventsThisDay, *args):
        self.sr.emptyDay.Flush()
        self.events = {}
        toSort = [ ((eventKV.eventTimeStamp, eventKV.eventTitle), eventKV) for eventKV in eventsThisDay.values() ]
        eventsKVs = SortListOfTuples(toSort)
        for eventInfo in eventsKVs:
            onDblClick = (self.OpenEvent, eventInfo)
            iconPath, response = sm.GetService('calendar').GetMyResponseIconFromID(eventInfo.eventID, long=1)
            if response == const.eventResponseDeleted or response == const.eventResponseDeclined and not settings.user.ui.Get('calendar_showDeclined', 1):
                continue
            tagIcon = self.GetTagIcon(eventInfo.flag)
            entry = CalendarEventEntry(name='calendarEventEntry', parent=self.sr.emptyDay, align=uiconst.TOTOP, pos=(0,
             0,
             0,
             self.eventHeight), padding=(1, 1, 1, 0), state=uiconst.UI_NORMAL, eventInfo=eventInfo, onDblClick=onDblClick, responseIconPath=iconPath, tagIcon=tagIcon, response=response)
            entry.MenuFunction = self.GetEventMenu
            self.events[eventInfo.eventID] = eventInfo

        self.CheckEventsClipped()

    def GetTagIcon(self, tag):
        tagIcon = sm.GetService('calendar').LoadTagIcon(tag)
        return tagIcon

    def GetEventMenu(self, entry, *args):
        eventInfo = entry.eventInfo
        m = sm.GetService('calendar').GetEventMenu(eventInfo, entry.response, getJumpOption=False)
        return m

    def OpenEvent(self, eventInfo, *args):
        sm.GetService('calendar').OpenEventWnd(eventInfo)

    def CheckEventsClipped(self, *args):
        numEvents = len(self.events)
        if numEvents < 1:
            self.sr.moreCont.state = uiconst.UI_HIDDEN
            return
        totalEntryHeight = numEvents * (self.eventHeight + 1)
        l, t, w, h = self.sr.emptyDay.GetAbsolute()
        moreHeight = 0
        if self.sr.moreCont.state != uiconst.UI_HIDDEN:
            moreHeight = self.sr.moreCont.height
        if totalEntryHeight > h + moreHeight:
            self.sr.moreCont.state = uiconst.UI_PICKCHILDREN
        else:
            self.sr.moreCont.state = uiconst.UI_HIDDEN

    def OnMoreClick(self, *args):
        sm.GetService('calendar').OpenSingleDayWnd('day', self.year, self.month, self.monthday, self.events)


class CalendarHeader(Container):
    default_left = 0
    default_top = 0
    default_width = 256
    default_height = 256
    default_name = 'CalendarHeader'
    default_charID = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.Prepare_()

    def Prepare_(self, *args):
        self.sr.dayNameCont = Container(name='dayNameCont', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.AddDayNameText()

    def AddDayNameText(self, text = '', *args):
        if self.sr.Get('dayNameText', None) is None:
            self.sr.dayNameText = EveLabelSmall(text=text, parent=self.sr.dayNameCont, state=uiconst.UI_NORMAL, align=uiconst.CENTERBOTTOM)
        return self.sr.dayNameText

    def SetDayName(self, text = None, *args):
        self.AddDayNameText()
        if text is not None:
            self.sr.dayNameText.text = text


class CalendarEventEntry(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.eventInfo = getattr(attributes, 'eventInfo', None)
        self.response = getattr(attributes, 'response', None)
        if self.eventInfo is not None:
            tagIcon = attributes.get('tagIcon', None)
            myResponse = attributes.get('response', None)
            time = self.eventInfo.eventTimeStamp
            title = self.eventInfo.eventTitle
            if settings.user.ui.Get('calendar_showTimestamp', 1):
                if getattr(self.eventInfo, 'importance', None) > 0:
                    text = localization.GetByLabel('/Carbon/UI/Calendar/EventTitleWithTimeImportant', timeStamp=time, eventTitle=title)
                else:
                    text = localization.GetByLabel('/Carbon/UI/Calendar/EventTitleWithTime', timeStamp=time, eventTitle=title)
            elif getattr(self.eventInfo, 'importance', None) > 0:
                text = localization.GetByLabel('/Carbon/UI/Calendar/EventTitleImportant', eventTitle=title)
            else:
                text = localization.GetByLabel('/Carbon/UI/Calendar/EventTitle', eventTitle=title)
            hint = sm.GetService('calendar').GetEventHint(self.eventInfo, myResponse)
            responseIconPath = attributes.get('responseIconPath', None)
        else:
            text = ''
            tagIcon = None
            responseIconPath = None
        onDblClick = getattr(attributes, 'onDblClick', None)
        if onDblClick is not None:
            self.OnDblClick = onDblClick
        self.Prepare_(text, tagIcon, responseIconPath, hint)

    def Prepare_(self, text = '', tagIcon = None, responseIconPath = None, hint = '', *args):
        self.clipChildren = 1
        self.AddLabel(text)
        self.height = 14
        self.AddIconCont(responsePath=responseIconPath, tagIcon=tagIcon)
        self.AddFill()
        self.hint = hint

    def AddLabel(self, text, *args):
        self.sr.label = eveLabel.EveLabelSmall(text=text, parent=self, left=14, top=0, state=uiconst.UI_DISABLED, color=None, align=uiconst.CENTERLEFT, maxLines=1)

    def AddFill(self, *args):
        self.sr.fill = Frame(parent=self, name='fill', frameConst=uiconst.FRAME_FILLED_SHADOW_CORNER0, color=(1.0, 1.0, 1.0, 0.05))
        self.sr.hilite = Frame(parent=self, name='hilite', frameConst=uiconst.FRAME_FILLED_SHADOW_CORNER0, pos=(1, 1, 0, 0), color=(1.0, 1.0, 1.0, 0.25), state=uiconst.UI_HIDDEN)

    def AddIconCont(self, responsePath = None, tagIcon = None, *args):
        self.sr.tagCont = Container(name='statusCont', parent=self, align=uiconst.TOPRIGHT, pos=(0, 2, 14, 14), state=uiconst.UI_DISABLED, idx=0)
        self.sr.tagCont.autoPos = uiconst.AUTOPOSYCENTER
        self.sr.responseCont = Container(name='responseCont', parent=self, align=uiconst.TOPLEFT, pos=(1, 0, 10, 14), state=uiconst.UI_DISABLED)
        if tagIcon is not None:
            self.SetTag(tagIcon)
        self.SetStatus(self.sr.responseCont, responsePath)

    def SetStatus(self, cont, iconPath = None):
        cont.Flush()
        if iconPath:
            Icon(icon=iconPath, parent=cont, align=uiconst.CENTER, pos=(0, 0, 16, 16))

    def SetTag(self, tagIcon):
        self.sr.tagCont.Flush()
        self.sr.tagCont.children.append(tagIcon)

    def GetMenu(self):
        return self.MenuFunction(self)

    def MenuFunction(self, entry, *args):
        return []

    def OnMouseEnter(self, *args):
        if GetAttrs(self, 'sr', 'hilite'):
            self.sr.hilite.state = uiconst.UI_DISABLED

    def OnMouseExit(self, *args):
        if GetAttrs(self, 'sr', 'hilite'):
            self.sr.hilite.state = uiconst.UI_HIDDEN


class CalendarNewEventWnd(Window):
    __guid__ = 'form.CalendarNewEventWnd'
    __notifyevents__ = ['OnRespondToEvent', 'OnRemoveCalendarEvent']
    default_iconNum = 'res:/ui/Texture/WindowIcons/calendar.png'
    default_minSize = (530, 370)
    default_height = 460

    def ApplyAttributes(self, attributes):
        super(CalendarNewEventWnd, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        year = attributes.year
        month = attributes.month
        monthday = attributes.monthday
        eventInfo = attributes.eventInfo
        edit = attributes.edit or False
        self.buttonGroup = None
        now = blue.os.GetWallclockTime()
        cyear, cmonth, cwd, cday, chour, cmin, csec, cms = GetTimeParts(now)
        if year is None or month is None:
            year = cyear
            month = cmonth
        if (year, month, monthday) == (cyear, cmonth, cday):
            year, month, monthday, hour = self.FindTimeToUse(year, month, monthday, chour)
        else:
            hour = 12
        self.year = year
        self.month = month
        self.monthday = monthday
        self.hour = hour
        self.min = 0
        self.configname = '%s_%s_%s' % (year, month, monthday)
        self.invitees = None
        self.oldInvitees = None
        self.inEditMode = False
        self.sr.infoCont = ContainerAutoSize(name='infoCont', parent=self.sr.main, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        self.sr.tabCont = Container(name='tabCont', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.sr.eventDescrCont = Container(name='invitedScroll', parent=self.sr.tabCont, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.sr.invitedCont = Container(name='invitedScroll', parent=self.sr.tabCont, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        subtabs = [[localization.GetByLabel('UI/Calendar/EventWindow/TabDescription'),
          self.sr.eventDescrCont,
          self,
          'descr']]
        flag = GetAttrs(eventInfo, 'flag')
        if flag is None or flag == const.calendarTagPersonal:
            subtabs.append([localization.GetByLabel('UI/Calendar/EventWindow/TabInvitations'),
             self.sr.invitedCont,
             self,
             'invitations'])
        elif flag in [const.calendarTagCorp, const.calendarTagAlliance] and session.corpid and session.corprole & const.corpRoleChatManager == const.corpRoleChatManager:
            subtabs.append([localization.GetByLabel('UI/Calendar/EventWindow/TabInvitations'),
             self.sr.invitedCont,
             self,
             'invitations'])
        self.sr.tabs = TabGroup(name='tabs', parent=self.sr.tabCont, idx=0, tabs=subtabs, groupID='calenderEvent_tabs', autoselecttab=0)
        self.sr.tabs.ShowPanelByName(localization.GetByLabel('UI/Calendar/EventWindow/TabDescription'))
        invTab = self.sr.tabs.sr.Get('%s_tab' % localization.GetByLabel('UI/Calendar/EventWindow/TabInvitations'), None)
        if invTab is not None:
            invTab.OnTabDropData = self.OnDropData
        if eventInfo is not None:
            eventDetails = sm.GetService('calendar').GetEventDetails(eventInfo.eventID, eventInfo.ownerID)
            self.eventID = eventInfo.eventID
            self.title = eventInfo.eventTitle
            self.descr = eventDetails.eventText
            self.creatorID = eventDetails.creatorID
            self.duration = eventInfo.eventDuration
            self.importance = eventInfo.importance
            self.eventTag = eventInfo.flag
            self.cbChecked = self.eventTag
            self.eventInfo = eventInfo
            self.year, self.month, cwd, self.monthdayday, self.hour, self.min, sec, ms = blue.os.GetTimeParts(eventInfo.eventDateTime)
            if edit:
                self.SetupCreateControls(new=not edit)
            else:
                self.SetupReadOnlyElements()
        else:
            self.eventID = None
            self.title = ''
            self.descr = ''
            self.creatorID = None
            self.duration = 0
            self.importance = 0
            self.eventTag = const.calendarTagPersonal
            self.cbChecked = const.calendarTagPersonal
            self.eventInfo = None
            self.SetupCreateControls()

    def Load(self, key, *args):
        if key == 'invitations':
            self.LoadInviteeTabScroll()

    def LoadInviteeTabScroll(self, *args):
        if getattr(self, 'eventID', None) is None:
            tag = self.cbChecked
        else:
            tag = self.eventTag
        if tag == const.calendarTagCCP:
            return
        if self.inEditMode:
            if tag in (const.calendarTagCorp, const.calendarTagAutomated):
                self.LoadCorpAllianceInScroll(session.corpid)
                return
            if tag == const.calendarTagAlliance:
                self.LoadCorpAllianceInScroll(session.allianceid)
                return
        self.LoadInviteeScroll()

    def SetupCreateControls(self, new = 1, *args):
        self.inEditMode = True
        left = 6
        top = 20
        thisDay = [self.year,
         self.month,
         self.monthday,
         self.hour,
         self.min]
        self.sr.infoCont.Flush()
        self.sr.infoCont.clipChildren = True
        if self.buttonGroup:
            self.buttonGroup.Close()
            self.buttonGroup = None
        btns = []
        if new:
            caption = localization.GetByLabel('UI/Calendar/EventWindow/CaptionNew')
            btns.append([localization.GetByLabel('UI/Calendar/EventWindow/Create'),
             self.CreateOrEditEvent,
             (1,),
             None])
        else:
            caption = localization.GetByLabel('UI/Calendar/EventWindow/CaptionEdit')
            btns.append([localization.GetByLabel('UI/Calendar/EventWindow/Save'),
             self.CreateOrEditEvent,
             (0,),
             None])
        btns.append([localization.GetByLabel('UI/Generic/Cancel'),
         self.CloseByUser,
         (),
         None])
        self.buttonGroup = ButtonGroup(btns=btns, parent=self.sr.main, idx=0)
        self.SetCaption(caption)
        label = eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Calendar/SingleDayWindow/Title'), parent=self.sr.infoCont, align=uiconst.TOTOP, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         0))
        self.sr.titleEdit = SingleLineEditText(name='titleEdit', parent=self.sr.infoCont, setvalue=self.title, maxLength=const.calendarMaxTitleSize, align=uiconst.TOTOP, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding))
        dateParent = Container(parent=self.sr.infoCont, align=uiconst.TOTOP, padding=(const.defaultPadding,
         label.textheight,
         const.defaultPadding,
         const.defaultPadding), height=100)
        now = blue.os.GetWallclockTime()
        cyear, cmonth, cwd, cday, chour, cmin, csec, cms = GetTimeParts(now)
        yearRange = const.calendarViewRangeInMonths / 12 + 1
        self.sr.fromDate = DatePicker(name='datepicker', parent=dateParent, align=uiconst.TOPLEFT, width=256, height=18, left=0, top=0)
        self.sr.fromDate.Startup(thisDay, True, 4, cyear, yearRange)
        durationOptions = [(localization.GetByLabel('UI/Calendar/EventWindow/DateNotSpecified'), None)]
        for i in xrange(1, 25):
            str = localization.GetByLabel('UI/Calendar/EventWindow/DateSpecified', hours=i)
            durationOptions += [(str, i * 60)]

        dLeft = self.sr.fromDate.left + self.sr.fromDate.width + 16
        self.sr.durationCombo = Combo(label=localization.GetByLabel('UI/Calendar/EventWindow/Duration'), parent=dateParent, options=durationOptions, name='duration', select=self.duration, left=dLeft, width=130, align=uiconst.TOPLEFT)
        dateParent.height = max(self.sr.fromDate.height, self.sr.durationCombo.height)
        self.sr.importantCB = Checkbox(text=localization.GetByLabel('UI/Calendar/EventWindow/Important'), parent=self.sr.infoCont, settingsKey='importantCB', checked=self.importance, align=uiconst.TOTOP, padLeft=const.defaultPadding)
        self.radioBtns = []
        if new:
            checkboxes = [(localization.GetByLabel('UI/Calendar/EventWindow/GroupPersonal'),
              'personal',
              const.calendarTagPersonal,
              const.calendarTagPersonal == self.eventTag)]
            if session.corpid and session.corprole & const.corpRoleChatManager == const.corpRoleChatManager:
                checkboxes.append((localization.GetByLabel('UI/Calendar/EventWindow/GroupCorporation'),
                 'corp',
                 const.calendarTagCorp,
                 const.calendarTagCorp == self.eventTag))
            if session.allianceid and session.corprole & const.corpRoleChatManager == const.corpRoleChatManager:
                checkboxes.append((localization.GetByLabel('UI/Calendar/EventWindow/GroupAlliance'),
                 'alliance',
                 const.calendarTagAlliance,
                 const.calendarTagAlliance == self.eventTag))
            for label, config, tag, checked in checkboxes:
                cb = RadioButton(text=label, parent=self.sr.infoCont, settingsKey=config, retval=tag, checked=checked, align=uiconst.TOTOP, groupname='eventTag', callback=self.TagCheckboxChecked, left=const.defaultPadding)
                self.radioBtns.append(cb)

        else:
            eventTypeH = localization.GetByLabel('UI/Calendar/EventWindow/EventType')
            eventType = sm.GetService('calendar').GetEventTypes().get(self.eventTag, '-')
            if eventType != '-':
                eventType = localization.GetByLabel(eventType)
            eveLabel.EveHeaderSmall(text=eventTypeH, parent=self.sr.infoCont, name='eventType', align=uiconst.TOTOP, padLeft=const.defaultPadding, state=uiconst.UI_NORMAL)
            eveLabel.EveLabelMedium(text=eventType, parent=self.sr.infoCont, align=uiconst.TOTOP, padLeft=const.defaultPadding, padBottom=const.defaultPadding, state=uiconst.UI_NORMAL)
        self.sr.infoCont.height = sum([ each.height + each.padTop + each.padBottom for each in self.sr.infoCont.children ])
        self.sr.eventDescrCont.Flush()
        readonly = IsContentComplianceControlSystemActive(sm.GetService('machoNet'))
        self.counter = None
        self.counter = EveLabelSmall(text='0/%s' % const.calendarMaxDescrSize, parent=self.sr.eventDescrCont, color=TextColor.SECONDARY, align=uiconst.BOTTOMRIGHT, state=uiconst.UI_NORMAL)
        self.sr.descrEdit = eveEditPlainText.EditPlainText(setvalue=self.descr, parent=self.sr.eventDescrCont, align=uiconst.TOALL, maxLength=const.calendarMaxDescrSize, showattributepanel=False, readonly=readonly, customCounter=self.counter)
        self.sr.invitedCont.Flush()
        self.sr.addIviteeeBtnCont = Container(name='btnCont', parent=self.sr.invitedCont, align=uiconst.TOTOP, pos=None, height=32, state=uiconst.UI_HIDDEN)
        Button(parent=self.sr.addIviteeeBtnCont, label=localization.GetByLabel('UI/Calendar/EventWindow/AddInvitee'), func=self.OpenAddInvteeWnd)
        if new or self.eventTag == const.calendarTagPersonal:
            self.sr.addIviteeeBtnCont.state = uiconst.UI_PICKCHILDREN
        self.AddQuickFilter(self.sr.addIviteeeBtnCont)
        self.sr.inviteScroll = eveScroll.Scroll(name='invitedScroll', parent=self.sr.invitedCont, padding=(0, 8, 0, 0))
        content = self.sr.inviteScroll.sr.content
        content.OnDropData = self.OnDropData
        if self.sr.tabs.GetSelectedArgs() == 'invitations':
            self.LoadInviteeTabScroll()

    def TagCheckboxChecked(self, radioButton, *args):
        tag = radioButton.GetReturnValue() or const.calendarTagPersonal
        self.cbChecked = tag
        if tag == const.calendarTagPersonal:
            self.sr.addIviteeeBtnCont.state = uiconst.UI_PICKCHILDREN
            self.LoadInviteeScroll()
        else:
            self.sr.addIviteeeBtnCont.state = uiconst.UI_HIDDEN
            if tag in (const.calendarTagCorp, const.calendarTagAutomated):
                self.LoadCorpAllianceInScroll(session.corpid)
            elif tag == const.calendarTagAlliance:
                self.LoadCorpAllianceInScroll(session.allianceid)

    def LoadCorpAllianceInScroll(self, entityID, *args):
        if entityID is None:
            return
        owner = cfg.eveowners.GetIfExists(entityID)
        if owner is None:
            return
        if evetypes.Exists(owner.typeID):
            scrolllist = [GetFromClass(User, {'charID': entityID})]
            self.sr.inviteScroll.Load(contentList=scrolllist, headers=[], noContentHint='')

    def AddSpacer(self, parent):
        spacer = Container(pos=(0, 0, 0, 4), align=uiconst.TOPLEFT)
        parent.AddCell(cellObject=spacer, colSpan=parent.columns)
        parent.FillRow()

    def SetupReadOnlyElements(self, *args):
        left = 8
        top = 6
        firstColumnItems = []
        secondColumnItems = []
        self.SetCaption(localization.GetByLabel('UI/Calendar/EventWindow/CaptionRead'))
        btns = []
        if not sm.GetService('calendar').IsInPastFromBlueTime(then=self.eventInfo.eventDateTime) and not self.eventInfo.isDeleted:
            if self.eventInfo.flag in [const.calendarTagCorp, const.calendarTagAlliance]:
                self.AddAcceptDeclineBtns(btns)
                if self.eventInfo.ownerID in [session.corpid, session.allianceid] and session.corprole & const.corpRoleChatManager == const.corpRoleChatManager:
                    self.InsertEditDeleteBtns(btns)
            elif self.eventInfo.flag == const.calendarTagPersonal:
                if self.eventInfo.ownerID != session.charid:
                    self.AddAcceptDeclineBtns(btns)
                else:
                    self.InsertEditDeleteBtns(btns)
        btns.append([localization.GetByLabel('UI/Generic/Close'),
         self.CloseByUser,
         (),
         None])
        if self.buttonGroup:
            self.buttonGroup.Close()
            self.buttonGroup = None
        self.buttonGroup = ButtonGroup(btns=btns, parent=self.sr.main, idx=0)
        infoCont = Container(name='infoCont', parent=self.sr.infoCont, align=uiconst.TOTOP)
        title = self.title
        if self.importance > 0:
            title = '<color=red>!</color>%s' % title
        caption = eveLabel.EveCaptionMedium(text=title, parent=infoCont, padding=(left,
         top,
         left,
         top), align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        top += caption.textheight
        self.infoContLayoutGrid = LayoutGrid(parent=infoCont, columns=2, top=top, left=6, cellSpacing=(20, 0))
        startH = localization.GetByLabel('UI/Calendar/EventWindow/StartTime')
        label = eveLabel.EveLabelSmallBold(text=startH, parent=self.infoContLayoutGrid, name='startTime', align=uiconst.TOPLEFT, idx=1, state=uiconst.UI_NORMAL)
        startTime = FmtDate(self.eventInfo.eventDateTime - eveLocalization.GetTimeDelta() * const.SEC, 'ls')
        dataLabel = eveLabel.EveLabelMedium(text=startTime, parent=self.infoContLayoutGrid, state=uiconst.UI_NORMAL)
        eventTypeH = localization.GetByLabel('UI/Calendar/EventWindow/EventType')
        label = eveLabel.EveLabelSmallBold(text=eventTypeH, parent=self.infoContLayoutGrid, name='eventType', align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        eventType = sm.GetService('calendar').GetEventTypes().get(self.eventTag, '-')
        if eventType != '-':
            eventType = localization.GetByLabel(eventType)
        dataLabel2 = eveLabel.EveLabelMedium(text=eventType, parent=self.infoContLayoutGrid, width=200, state=uiconst.UI_NORMAL)
        durationH = localization.GetByLabel('UI/Calendar/EventWindow/Duration')
        label = eveLabel.EveLabelSmallBold(text=durationH, parent=self.infoContLayoutGrid, name='duration', align=uiconst.TOPLEFT, idx=1, state=uiconst.UI_NORMAL)
        if self.eventInfo.eventDuration is None:
            durationLabel = localization.GetByLabel('UI/Calendar/EventWindow/DateNotSpecified')
        else:
            hours = self.eventInfo.eventDuration / 60
            durationLabel = localization.GetByLabel('UI/Calendar/EventWindow/DateSpecified', hours=hours)
        dataLabel = eveLabel.EveLabelMedium(text=durationLabel, parent=self.infoContLayoutGrid, state=uiconst.UI_NORMAL)
        creatorH = localization.GetByLabel('UI/Calendar/EventWindow/Creator')
        creatorInfo = cfg.eveowners.Get(self.creatorID)
        if self.eventTag == const.calendarTagCCP:
            creatorNameText = localization.GetByLabel('UI/Calendar/CalendarWindow/GroupCcp')
        elif self.creatorID == const.ownerSystem:
            creatorNameText = creatorInfo.name
        else:
            showInfoData = ('showinfo', creatorInfo.typeID, self.creatorID)
            creatorNameText = localization.GetByLabel('UI/Calendar/EventWindow/CreatorLink', charID=self.creatorID, showInfoData=showInfoData)
        label = eveLabel.EveLabelSmallBold(text=creatorH, parent=self.infoContLayoutGrid, name='eventType', align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        dataLabel2 = eveLabel.EveLabelMedium(text=creatorNameText, parent=self.infoContLayoutGrid, state=uiconst.UI_NORMAL)
        iconPath, myResponse = sm.GetService('calendar').GetMyResponseIconFromID(self.eventID, long=1, getDeleted=self.eventInfo.isDeleted)
        response = localization.GetByLabel(sm.GetService('calendar').GetResponseType().get(myResponse, 'UI/Generic/Unknown'))
        statusH = localization.GetByLabel('UI/Calendar/EventWindow/Status')
        label = eveLabel.EveLabelSmallBold(text=statusH, parent=self.infoContLayoutGrid, name='status', align=uiconst.TOPLEFT, idx=1, state=uiconst.UI_NORMAL)
        autosizeCont = ContainerAutoSize(name='autosizeCont', parent=self.infoContLayoutGrid, alignMode=uiconst.TOPLEFT)
        self.sr.reponseText = eveLabel.EveLabelMedium(text=response, parent=autosizeCont, state=uiconst.UI_NORMAL, left=20)
        if iconPath:
            eveIcon.Icon(icon=iconPath, parent=autosizeCont, align=uiconst.CENTERLEFT, pos=(0, 0, 16, 16))
        updateH = localization.GetByLabel('UI/Calendar/EventWindow/LastUpdated')
        label = eveLabel.EveLabelSmallBold(text=updateH, parent=self.infoContLayoutGrid, name='updated', align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        updateTime = FmtDate(self.eventInfo.dateModified, 'ls')
        dataLabel2 = eveLabel.EveLabelMedium(text=updateTime, parent=self.infoContLayoutGrid, width=200, state=uiconst.UI_NORMAL)
        self.infoContLayoutGrid.RefreshGridLayout()
        w, h = self.infoContLayoutGrid.GetSize()
        infoCont.height = h + self.infoContLayoutGrid.top + 2
        descr = self.descr
        self.sr.descrEdit = eveEditPlainText.EditPlainText(setvalue=descr, parent=self.sr.eventDescrCont, align=uiconst.TOALL, maxLength=1000, padding=const.defaultPadding, readonly=1)
        self.sr.invitedCont.Flush()
        self.sr.searchCont = Container(name='searchCont', parent=self.sr.invitedCont, align=uiconst.TOTOP, pos=(0, 0, 0, 26))
        self.AddQuickFilter(self.sr.searchCont)
        if self.eventTag in [const.calendarTagCCP, const.calendarTagAutomated]:
            self.sr.searchCont.state = uiconst.UI_HIDDEN
        elif self.eventTag in [const.calendarTagCorp, const.calendarTagAlliance] and session.corpid and not session.corprole & const.corpRoleChatManager == const.corpRoleChatManager:
            self.sr.searchCont.state = uiconst.UI_HIDDEN
        self.sr.inviteScroll = eveScroll.Scroll(name='invitedScroll', parent=self.sr.invitedCont, padding=const.defaultPadding)

    def InsertEditDeleteBtns(self, btns, top = 6, *args):
        editDeleteCont = ContainerAutoSize(name='editCont', parent=self.sr.infoCont, align=uiconst.TORIGHT)
        editBtn = Button(parent=editDeleteCont, label=localization.GetByLabel('UI/Calendar/EventWindow/Edit'), func=self.ChangeToEditMode, align=uiconst.TOTOP, padBottom=8)
        deleteBtn = Button(parent=editDeleteCont, label=localization.GetByLabel('UI/Calendar/EventWindow/Delete'), func=self.Delete, align=uiconst.TOTOP)
        editBtn.width = deleteBtn.width = max(editBtn.width, deleteBtn.width)
        editDeleteCont.width = 4 + editBtn.width

    def AddAcceptDeclineBtns(self, btns):
        iconPath, myResponse = sm.GetService('calendar').GetMyResponseIconFromID(self.eventID)
        if myResponse != const.eventResponseAccepted:
            btns.insert(0, [localization.GetByLabel('/Carbon/UI/Calendar/Accept'),
             self.RespondToEvent,
             (const.eventResponseAccepted,),
             None])
        if myResponse != const.eventResponseMaybe:
            btns.insert(1, [localization.GetByLabel('/Carbon/UI/Calendar/MaybeReply'),
             self.RespondToEvent,
             (const.eventResponseMaybe,),
             None])
        if myResponse != const.eventResponseDeclined:
            btns.insert(2, [localization.GetByLabel('/Carbon/UI/Calendar/Decline'),
             self.RespondToEvent,
             (const.eventResponseDeclined,),
             None])

    def AddQuickFilter(self, cont, *args):
        self.sr.searchBox = QuickFilterEdit(name='searchBox', parent=cont, setvalue='', maxLength=37, align=uiconst.TOPRIGHT, isCharacterField=True)
        self.sr.searchBox.ReloadFunction = self.LoadInviteeScroll

    def OpenAddInvteeWnd(self, *args):
        actionBtn = [(localization.GetByLabel('UI/Calendar/FindInviteesWindow/Add'), self.AddInviteeToEvent, 1)]
        caption = localization.GetByLabel('UI/Calendar/FindInviteesWindow/Caption')
        OwnerSearchWindow.CloseIfOpen(windowID='searchWindow_calendar')
        extraIconHintFlag = ['ui_73_16_13', localization.GetByLabel('UI/Calendar/Hints/CharacterAdded'), False]
        wnd = OwnerSearchWindow.Open(windowID='searchWindow_calendar', actionBtns=actionBtn, caption=caption, input='', getMyCorp=False, getMyLists=False, getMyAlliance=False, showContactList=True, extraIconHintFlag=extraIconHintFlag, configname=self.configname, ownerGroups=[const.groupCharacter])
        wnd.ExtraMenuFunction = self.InviteeMenuFunction
        wnd.IsAdded = self.CheckIfAdded

    def CheckIfAdded(self, contactID):
        if self.invitees is None:
            self.PopulateInviteeDicts(self.eventID)
        return contactID in self.invitees

    def AddInviteeToEvent(self, func, *args):
        if self.inEditMode is False:
            return
        if not self or self.destroyed:
            return
        sel = apply(func)
        selIDs = [ each.charID for each in sel ]
        self.AddInvitees(selIDs)

    def AddInvitees(self, charIDList):
        if self.inEditMode is False:
            return
        if self.invitees is None:
            self.PopulateInviteeDicts(self.eventID)
        for charID in charIDList:
            if charID == session.charid or charID is None:
                continue
            if len(self.invitees) >= const.calendarMaxInvitees:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Calendar/FindInviteesWindow/TooMany', max=const.calendarMaxInvitees)})
                break
            if charID not in self.invitees:
                self.invitees[charID] = const.eventResponseUndecided
                sm.ScatterEvent('OnSearcedUserAdded', charID, self.configname)

        self.LoadInviteeScroll()

    def LoadInviteeScroll(self, *args):
        filter = self.sr.searchBox.GetValue()
        if len(filter) >= 2:
            bannedwords.check_search_words_allowed(filter)
            return self.SearchInvitee()
        if self.invitees is None:
            self.PopulateInviteeDicts(self.eventID)
        responseDict = sm.GetService('calendar').GetResponsesToEventInStatusDict(self.eventID, self.invitees)
        scrolllist = []
        responseCategoryList = [const.eventResponseAccepted, const.eventResponseMaybe, const.eventResponseDeclined]
        if self.eventTag == const.calendarTagPersonal:
            responseCategoryList.insert(-1, const.eventResponseUndecided)
        for response in responseCategoryList:
            label = localization.GetByLabel(sm.GetService('calendar').GetResponseType().get(response, 'UI/Generic/Unknown'))
            scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetResponseSubContent,
             'label': label,
             'cleanLabel': label,
             'id': ('calendarInvitees', response),
             'state': 'locked',
             'BlockOpenWindow': 1,
             'showicon': sm.GetService('calendar').GetResponseIconNum(response),
             'showlen': 1,
             'groupName': 'labels',
             'groupItems': responseDict[response],
             'noItemText': localization.GetByLabel('UI/Calendar/EventWindow/NoCharacter'),
             'response': response,
             'DropData': self.DropUserOnGroup,
             'allowGuids': ['listentry.User', 'listentry.Sender', 'listentry.ChatUser']}))

        self.sr.inviteScroll.Load(contentList=scrolllist, headers=[], noContentHint='')

    def GetResponseSubContent(self, data, *args):
        response = data.response
        scrolllist = []
        if len(data.groupItems) > const.calendarMaxInviteeDisplayed:
            if response == const.eventResponseDeclined:
                label = localization.GetByLabel('UI/Calendar/EventWindow/TooManyDeclined', max=const.calendarMaxInviteeDisplayed)
            else:
                label = localization.GetByLabel('UI/Calendar/EventWindow/TooManyAccepted', max=const.calendarMaxInviteeDisplayed)
            return [GetFromClass(Generic, {'label': label,
              'sublevel': 1})]
        cfg.eveowners.Prime(data.groupItems)
        for charID in data.groupItems:
            if response == const.eventResponseUninvited:
                continue
            charinfo = cfg.eveowners.Get(charID)
            entry = GetFromClass(User, {'charID': charID,
             'MenuFunction': self.InviteeMenuFunction})
            scrolllist.append((charinfo.name.lower(), entry))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def InviteeMenuFunction(self, nodes, *args):
        m = []
        if self.inEditMode is False:
            return m
        if self.invitees is None:
            self.PopulateInviteeDicts(self.eventID)
        charIDs = [ node.charID for node in nodes if node.charID in self.invitees ]
        if session.charid in charIDs:
            charIDs.remove(session.charid)
        numCharIDs = len(charIDs)
        if numCharIDs > 0:
            label = localization.GetByLabel('UI/Calendar/EventWindow/RemoveInvitee', num=numCharIDs)
            m = [(label, self.RemoveInviteeFromScroll, (charIDs,))]
        return m

    def RemoveInviteeFromScroll(self, charIDs):
        if self.inEditMode is False:
            return
        if self.invitees is None:
            self.PopulateInviteeDicts(self.eventID)
        for charID in charIDs:
            self.invitees.pop(charID, None)

        sm.ScatterEvent('OnSearcedUserRemoved', charIDs, self.configname)
        self.LoadInviteeScroll()

    def ChangeToEditMode(self, *args):
        self.FlushAll()
        if self.invitees is None:
            self.PopulateInviteeDicts(self.eventID)
        self.oldInvitees = self.invitees.copy()
        self.SetupCreateControls(new=0)

    def FlushAll(self, *args):
        self.sr.infoCont.Flush()
        self.sr.eventDescrCont.Flush()
        self.sr.invitedCont.Flush()
        if self.buttonGroup:
            self.buttonGroup.Close()
            self.buttonGroup = None

    def FindTimeToUse(self, year, month, day, hour):
        firstDay, lastDay = calendar.monthrange(year, month)
        hour = hour + 1
        if hour > 23:
            hour = 0
            day = day + 1
        if day > lastDay:
            day = 1
            month += 1
        if month > const.calendarDecember:
            month = const.calendarJanuary
            year = year + 1
        return (year,
         month,
         day,
         hour)

    def CreateOrEditEvent(self, create = 1, *args):
        if getattr(self, 'editing', 0):
            return
        self.editing = 1
        try:
            eventTag = self.radioBtns[0].GetGroupValue() if self.radioBtns else 0
            if eventTag == 0:
                eventTag = self.eventTag
            descr = self.sr.descrEdit.GetValue()
            title = self.sr.titleEdit.GetValue()
            fromDate = self.sr.fromDate.GetValue()
            duration = self.sr.durationCombo.GetValue()
            important = self.sr.importantCB.checked
            cyear, cmonth, cwd, cday, chour, cmin, csec, cms = blue.os.GetTimeParts(fromDate + eveLocalization.GetTimeDelta() * const.SEC)
            if sm.GetService('calendar').IsInPast(cyear, cmonth, cday, chour, cmin):
                raise UserError('CalendarCannotPlanThePast')
            if create:
                if self.invitees is None:
                    self.PopulateInviteeDicts(self.eventID)
                newInviteeCharIDs = self.invitees.keys()
                sm.GetService('calendar').CreateNewEvent(fromDate, duration, title, descr, eventTag, important, invitees=newInviteeCharIDs)
            else:
                if self.invitees is None:
                    self.PopulateInviteeDicts(self.eventID)
                newInviteeCharIDs = [ charID for charID in self.invitees.keys() if charID not in self.oldInvitees.keys() ]
                removedInviteeCharIDs = [ charID for charID in self.oldInvitees.keys() if charID not in self.invitees.keys() ]
                wasEdited = sm.GetService('calendar').EditEvent(self.eventID, self.eventInfo.eventDateTime, fromDate, duration, title, descr, eventTag, important)
                if not wasEdited:
                    return
                if len(newInviteeCharIDs) + len(removedInviteeCharIDs) > 0:
                    sm.GetService('calendar').UpdateEventParticipants(self.eventID, newInviteeCharIDs, removedInviteeCharIDs)
        finally:
            self.editing = 0

        sm.ScatterEvent('OnReloadEvents')
        self.CloseByUser()

    def RespondToEvent(self, response, *args):
        sm.GetService('calendar').RespondToEvent(self.eventID, self.eventInfo, response)

    def Delete(self, *args):
        sm.GetService('calendar').DeleteEvent(self.eventID, self.eventInfo.ownerID)

    def Cancel(self, *args):
        self.CloseByUser()

    def OnDropData(self, dragObj, nodes, *args):
        toAdd = []
        for node in nodes:
            if node.__guid__ in ('listentry.User', 'listentry.Sender', 'listentry.ChatUser', 'listentry.SearchedUser') and node.IsCharacter and not IsNPC(node.itemID):
                toAdd.append(node.itemID)

        if len(toAdd) > 0:
            self.AddInvitees(toAdd)

    def DropUserOnGroup(self, groupID, nodes, *args):
        self.OnDropData(None, nodes)

    def _OnClose(self, *args):
        wnd = OwnerSearchWindow.GetIfOpen(windowID='searchWindow_calendar')
        if wnd and wnd.configname == self.configname:
            wnd.CloseByUser()

    def SearchInvitee(self, *args):
        if self.invitees is None:
            self.PopulateInviteeDicts(self.eventID)
        cfg.eveowners.Prime(self.invitees.keys())
        matched = NiceFilter(self.sr.searchBox.QuickFilter, [ cfg.eveowners.Get(charID) for charID in self.invitees.keys() ])
        extraIcons = {}
        for each in [const.eventResponseAccepted, const.eventResponseDeclined, const.eventResponseUndecided]:
            icon = sm.GetService('calendar').GetLongResponseIconPath(each)
            label = sm.GetService('calendar').GetResponseType().get(each, '')
            if label != '':
                label = localization.GetByLabel(label)
            extraIcons[each] = [icon, label, True]

        scrolllist = []
        for owner in matched:
            charID = owner.ownerID
            contact = utillib.KeyVal(contactID=charID)
            response = self.invitees.get(charID, None)
            if response is None:
                continue
            extraIconHintFlag = extraIcons.get(response, None)
            extraInfo = utillib.KeyVal(extraIconHintFlag=extraIconHintFlag, wndConfigname=self.configname)
            entryTuple = sm.GetService('addressbook').GetContactEntry(None, contact, extraInfo=extraInfo, listentryType=SearchedUser)
            scrolllist.append(entryTuple)

        scrolllist = SortListOfTuples(scrolllist)
        self.sr.inviteScroll.Load(contentList=scrolllist, headers=[], noContentHint=localization.GetByLabel('UI/Calendar/FindInviteesWindow/NothingFound'))

    def PopulateInviteeDicts(self, eventID):
        if eventID is None:
            self.invitees = {}
        else:
            ownerID = GetAttrs(self, 'eventInfo', 'ownerID')
            self.invitees = sm.GetService('calendar').GetResponsesToEvent(eventID, ownerID)
        self.oldInvitees = self.invitees.copy()

    def OnRespondToEvent(self, *args):
        self.CloseByUser()

    def OnRemoveCalendarEvent(self, eventID, eventDateTime, isDeleted):
        if self.eventID == eventID:
            self.CloseByUser()


class CalendarSingleDayWnd(Window):
    __guid__ = 'form.CalendarSingleDayWnd'
    __notifyevents__ = ['OnReloadCalendar', 'OnCalendarFilterChange']
    default_iconNum = 'res:/ui/Texture/WindowIcons/calendar.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        header = attributes.header
        year = attributes.year
        month = attributes.month
        monthday = attributes.monthday
        events = attributes.events
        wndType = attributes.wndType
        isADay = attributes.isADay or False
        self.date = (year, month, monthday)
        self.year = year
        self.month = month
        self.monthday = monthday
        self.wndType = wndType
        self.isADay = isADay
        sm.RegisterNotify(self)
        if isADay:
            dayDate = time.struct_time((year,
             month,
             monthday,
             0,
             0,
             0,
             0,
             1,
             0))
            caption = localization.formatters.FormatDateTime(value=dayDate, dateFormat='long', timeFormat='none')
        else:
            caption = header
        self.SetCaption(caption)
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=52, clipChildren=True)
        eveLabel.WndCaptionLabel(text=caption, parent=self.topParent)
        self.SetMinSize([315, 300])
        ButtonGroup(btns=[[localization.GetByLabel('UI/Generic/Close'),
          self.CloseByUser,
          (),
          None]], parent=self.sr.main, idx=0)
        self.sr.eventScroll = eveScroll.Scroll(name='eventScroll', parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.eventScroll.sr.id = 'calendar_singedaywnd'
        self.sr.eventScroll.sr.maxDefaultColumns = {localization.GetByLabel('UI/Generic/Unknown'): 150}
        self.LoadDaysEvents(events)

    def LoadDaysEvents(self, events, *args):
        self.events = events
        scrolllist = []
        includeUpdatedColumn = self.wndType == 'latestUpdates'
        for eventID, event in events.iteritems():
            iconPath, myResponse = sm.GetService('calendar').GetMyResponseIconFromID(eventID, long=1, getDeleted=event.isDeleted)
            if not settings.user.ui.Get('calendar_showDeclined', 1) and myResponse == const.eventResponseDeclined:
                continue
            if event.isDeleted and self.isADay:
                continue
            if self.isADay:
                timeStamp = getattr(event, 'eventTimeStamp', '')
            else:
                timeStamp = FmtDate(event.eventDateTime - eveLocalization.GetTimeDelta() * const.SEC, 'ss')
            label = '%s<t>%s' % (timeStamp, event.eventTitle)
            if includeUpdatedColumn:
                modified = FmtDate(event.dateModified, 'ss')
                label += '<t>%s' % modified
                sortBy = event.dateModified
            else:
                sortBy = event.eventDateTime
            data = utillib.KeyVal()
            data.label = label
            data.cleanLabel = label
            data.eventInfo = event
            data.eventID = event.eventID
            data.GetMenu = self.EventMenu
            data.iconPath = iconPath
            data.response = myResponse
            data.OnDblClick = self.DblClickEventEntry
            entry = GetFromClass(CalendarSingleDayEntry, {'label': label,
             'cleanLabel': label,
             'eventInfo': event,
             'eventID': event.eventID,
             'GetMenu': self.EventMenu,
             'iconPath': iconPath,
             'response': myResponse,
             'OnDblClick': self.DblClickEventEntry})
            scrolllist.append((sortBy, entry))

        scrolllist = SortListOfTuples(scrolllist, reverse=includeUpdatedColumn)
        headers = [localization.GetByLabel('UI/Calendar/SingleDayWindow/Time'), localization.GetByLabel('UI/Calendar/SingleDayWindow/Title')]
        if includeUpdatedColumn:
            headers.append(localization.GetByLabel('UI/Calendar/CalendarWindow/LatestUpdates'))
        self.sr.eventScroll.Load(contentList=scrolllist, headers=headers, noContentHint=localization.GetByLabel('UI/Calendar/SingleDayWindow/NoPlannedEvents'))

    def EventMenu(self, entry, *args):
        eventInfo = entry.sr.node.eventInfo
        m = sm.GetService('calendar').GetEventMenu(eventInfo, entry.sr.node.response)
        return m

    def DblClickEventEntry(self, entry, *args):
        eventInfo = entry.sr.node.eventInfo
        self.OpenEvent(eventInfo)

    def OpenEvent(self, eventInfo, *args):
        sm.GetService('calendar').OpenEventWnd(eventInfo)

    def OnReloadCalendar(self, *args):
        showTag = sm.GetService('calendar').GetActiveTags()
        if self.isADay:
            eventDict = {}
            events = sm.GetService('calendar').GetEventsByMonthYear(self.month, self.year)
            for eventKV in events:
                if not eventKV.isDeleted:
                    year, month, wd, day, hour, minute, sec, ms = blue.os.GetTimeParts(eventKV.eventDateTime)
                    if (year, month, day) == self.date and (showTag is None or showTag & eventKV.flag != 0):
                        eventDict[eventKV.eventID] = eventKV

            self.events = eventDict
            self.LoadDaysEvents(eventDict)
        elif self.wndType == 'upcomingEvents':
            events = sm.GetService('calendar').GetMyNextEvents()
            self.events = events
            self.LoadDaysEvents(events)
        elif self.wndType == 'latestUpdates':
            events = sm.GetService('calendar').GetMyChangedEvents()
            self.events = events
            self.LoadDaysEvents(events)

    def OnCalendarFilterChange(self, *args):
        self.OnReloadCalendar()


class CalendarSingleDayEntry(Generic):
    __guid__ = 'listentry.CalendarSingleDayEntry'

    def Startup(self, *args):
        self.sr.statusIconCont = Container(name='statusIconCont', parent=self, align=uiconst.TOPLEFT, pos=(0, 0, 16, 16))
        self.sr.flagIconCont = Container(name='statusIconCont', parent=self, align=uiconst.TOPRIGHT, pos=(0, 0, 14, 14))
        FrameThemeColored(parent=self.sr.flagIconCont)
        Generic.Startup(self, args)

    def Load(self, node):
        Generic.Load(self, node)
        self.sr.label.left = 16
        self.LoadStatusIcon(node)
        sm.GetService('calendar').LoadTagIconInContainer(node.eventInfo.flag, self.sr.flagIconCont)
        if node.eventInfo.importance > 0:
            self.UpdateLabel(node)
        node.Set('sort_%s' % localization.GetByLabel('UI/Calendar/SingleDayWindow/Time'), node.eventInfo.eventDateTime)
        self.hint = sm.GetService('calendar').GetEventHint(node.eventInfo, node.response)
        self.sr.label.Update()

    def LoadStatusIcon(self, data):
        self.sr.statusIconCont.Flush()
        icon = eveIcon.Icon(icon=data.iconPath, parent=self.sr.statusIconCont, align=uiconst.CENTERLEFT, pos=(0, 0, 16, 16))
        icon.hint = localization.GetByLabel(sm.GetService('calendar').GetResponseType().get(data.response, 'UI/Generic/Unknown'))

    def UpdateLabel(self, data):
        label = data.cleanLabel
        label = '<color=red>!</color> %s' % label
        self.sr.label.text = label
        self.sr.node.label = label
        self.sr.label.Update()


class EventList(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.maxEntries = 25
        self.events = {}
        self.listentryClass = attributes.get('listentryClass')
        self.getEventsFunc = attributes.get('getEventsFunc', sm.GetService('calendar').GetMyNextEvents)
        self.getEventsArgs = attributes.get('getEventsArgs', ())
        self.header = attributes.get('header', '')
        self.listType = attributes.get('listType', 'eventList')
        self.Setup()

    def Setup(self):
        sm.RegisterNotify(self)
        self.sr.moreCont = Container(name='moreCont', parent=self, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 10), state=uiconst.UI_NORMAL, padding=(0, 0, 0, 0))
        self.AddMoreContFill()
        self.SetupScroll()
        self.LoadNextEvents()

    def LoadNextEvents(self, *args):
        nextEvents = self.GetEvents()
        scrolllist = []
        self.events = {}
        for eventID, eventKV in nextEvents.iteritems():
            eventEntryTuple = self.GetEventEntryTuple(eventKV)
            if eventEntryTuple is None:
                continue
            self.events[eventID] = eventKV
            scrolllist.append(eventEntryTuple)

        scrolllist = SortListOfTuples(scrolllist, reverse=self.GetSortOrder())
        self.LoadScroll(scrolllist)
        self.OnResize()

    def SetupScroll(self, *args):
        self.sr.eventScroll = eveScroll.Scroll(name='eventScroll', parent=self)
        self.sr.eventScroll.scrollEnabled = 0
        self.sr.eventScroll.multiSelect = 0

    def GetEvents(self, *args):
        return apply(self.getEventsFunc, self.getEventsArgs)

    def GetEventEntryTuple(self, eventKV, *args):
        entry = self.GetEventEntry(eventKV)
        if entry is None:
            return
        return (eventKV.eventDateTime, entry)

    def GetSortOrder(self, *args):
        return 0

    def LoadScroll(self, scrolllist, *args):
        scrolllist = scrolllist[:self.maxEntries]
        self.sr.eventScroll.Load(contentList=scrolllist, headers=[], noContentHint='')

    def AddMoreContFill(self, *args):
        self.sr.backgroundFrame = PanelUnderlay(parent=self.sr.moreCont, padding=(-1, -1, -1, -1))
        icon = eveIcon.Icon(icon='ui_38_16_229', parent=self.sr.moreCont, pos=(0, -3, 16, 16), align=uiconst.CENTERTOP, idx=0, ignoreSize=True)
        icon.OnClick = self.OnMoreClick

    def GetEventEntry(self, eventInfo, *args):
        showTag = sm.GetService('calendar').GetActiveTags()
        if showTag is not None and showTag & eventInfo.flag == 0:
            return
        icon, myResponse = sm.GetService('calendar').GetMyResponseIconFromID(eventInfo.eventID, long=0, getDeleted=eventInfo.isDeleted)
        hint = localization.GetByLabel(sm.GetService('calendar').GetResponseType().get(myResponse, 'UI/Generic/Unknown'))
        return GetFromClass(self.listentryClass, {'label': eventInfo.eventTitle,
         'eventInfo': eventInfo,
         'icon': icon,
         'hint': hint,
         'response': myResponse})

    def OnResize(self, *args):
        uthread.new(self.UpdateMoreIndicators)

    def UpdateMoreIndicators(self, *args):
        if self.sr.eventScroll.scrollingRange >= self.sr.moreCont.height:
            self.sr.moreCont.state = uiconst.UI_PICKCHILDREN
        else:
            self.sr.moreCont.state = uiconst.UI_HIDDEN

    def OnReloadToDo(self, *args):
        self.LoadNextEvents()

    def OnCalendarFilterChange(self, *args):
        self.OnReloadToDo()

    def OnMoreClick(self, *args):
        sm.GetService('calendar').OpenSingleDayWnd(self.header, '', '', '', self.events, isADay=0, wndType=self.listType)


class UpdateEventsList(EventList):

    def GetEventEntryTuple(self, eventKV, *args):
        entry = self.GetEventEntry(eventKV)
        if entry is None:
            return
        return (eventKV.dateModified, entry)

    def GetSortOrder(self, *args):
        return 1


class CalendarListEntry(Generic):
    __guid__ = 'listentry.CalendarListEntry'
    __notifyevents__ = []
    TEXTMARGIN = 2

    def Startup(self, *args):
        self.sr.statusIconCont = Container(name='statusIconCont', parent=self, align=uiconst.TOPLEFT, pos=(0, 0, 16, 16))
        self.sr.tagIconCont = Container(name='statusIconCont', parent=self, align=uiconst.TOPRIGHT, pos=(0, 0, 16, 16))
        Frame(parent=self.sr.statusIconCont, color=(1.0, 1.0, 1.0, 0.5))
        Generic.Startup(self, args)
        self.sr.label.align = uiconst.TOPLEFT
        self.sr.label.top = self.TEXTMARGIN
        self.sr.timeLabel = eveLabel.EveLabelMedium(text='', parent=self, left=20, top=14, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, maxLines=1, color=(0.7, 0.7, 0.7, 0.75))
        self.sr.fill = Frame(parent=self, name='fill', frameConst=uiconst.FRAME_FILLED_SHADOW_CORNER0, color=(1.0, 1.0, 1.0, 0.05))
        sm.RegisterNotify(self)

    def Load(self, node):
        Generic.Load(self, node)
        self.sr.label.left = 20
        eventInfo = node.eventInfo
        hint = self.GetEventHint(eventInfo, node.response)
        self.hint = hint
        if eventInfo.importance > 0:
            label = self.sr.node.label
            newLabel = '<color=red>!</color> %s' % label
            self.sr.label.text = newLabel
        self.SetTime(eventInfo.eventDateTime - eveLocalization.GetTimeDelta() * const.SEC)
        self.sr.timeLabel.top = self.sr.label.top + self.sr.label.height
        self.LoadStatusIcon()
        sm.GetService('calendar').LoadTagIconInContainer(eventInfo.flag, self.sr.tagIconCont)
        self.sr.label.Update()

    def GetMenu(self, *args):
        eventInfo = self.sr.node.eventInfo
        m = sm.GetService('calendar').GetEventMenu(eventInfo, self.sr.node.response)
        return m

    def GetEventHint(self, eventInfo, myResponse, *args):
        hint = sm.GetService('calendar').GetEventHint(eventInfo, myResponse)
        return hint

    def _OnClose(self):
        sm.UnregisterNotify(self)

    def LoadStatusIcon(self, *args):
        data = self.sr.node
        self.sr.statusIconCont.Flush()
        iconPath = data.icon
        hint = data.hint
        icon = eveIcon.Icon(icon=iconPath, parent=self.sr.statusIconCont, align=uiconst.CENTER, pos=(0, 2, 16, 16))
        icon.hint = hint

    def GetHeight(self, node, width):
        labelWidth, labelHeight = eveLabel.EveLabelMedium.MeasureTextSize(node.label)
        timeWidth, timeHeight = eveLabel.EveLabelMedium.MeasureTextSize(FmtDate(node.eventInfo.eventDateTime, 'ls'))
        return CalendarListEntry.TEXTMARGIN * 2 + labelHeight + timeHeight

    def SetTime(self, eventDateTime, *args):
        self.sr.timeLabel.text = FmtDate(eventDateTime, 'ls')

    def OnDblClick(self, *args):
        sm.GetService('calendar').OpenEventWnd(self.sr.node.eventInfo)


class CalendarUpdatedEntry(CalendarListEntry):
    __guid__ = 'listentry.CalendarUpdatedEntry'

    def GetEventHint(self, eventInfo, myResponse, *args):
        eventDateTime = FmtDate(eventInfo.eventDateTime, 'ls')
        lastUpdatedTime = FmtDate(eventInfo.dateModified, 'ls')
        hint = localization.GetByLabel('UI/Calendar/EventWindow/LastUpdateHint', eventDateTime=eventDateTime, eventTitle=eventInfo.eventTitle, lastUpdatedTime=lastUpdatedTime)
        return hint
