#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\eveCalendarsvc.py
import time
import utillib
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING, SERVICE_START_PENDING
from carbon.common.script.util.format import GetTimeParts, GetYearMonthFromTime
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.eveCalendar import CalendarNewEventWnd, CalendarSingleDayWnd, CalendarWnd
from eve.client.script.ui.shared.stateFlag import AddAndSetFlagIcon, FlagIcon
import blue
from eve.client.script.parklife import states as state
import localization
import eveLocalization
from carbonui.uicore import uicore
from eve.client.script.util import eveMisc
from eveexceptions import UserError
from menu import MenuLabel
from eveexceptions.exceptionEater import ExceptionEater
from localization import GetByLabel
from notifications.client.notificationSettings.notificationSettingHandler import NotificationSettingData
from notifications.common.formatters.calendar import CalendarNotificationFormatter
import eve.common.script.util.notificationconst as notificationConst
from timeDateHelpers.const import MONTHANDYEAR_NAME_TEXT
import eve.common.lib.appConst as const
RESPONSETYPES = {const.eventResponseAccepted: 'UI/Calendar/ResponseTypes/Accepted',
 const.eventResponseDeclined: 'UI/Calendar/ResponseTypes/Declined',
 const.eventResponseDeleted: 'UI/Calendar/ResponseTypes/Canceled',
 const.eventResponseUninvited: 'UI/Calendar/ResponseTypes/Uninvited',
 const.eventResponseUndecided: 'UI/Calendar/ResponseTypes/NotResponded',
 const.eventResponseMaybe: 'UI/Calendar/ResponseTypes/MaybeReply'}
EVENTTYPES = {const.calendarTagPersonal: 'UI/Calendar/CalendarWindow/GroupPersonal',
 const.calendarTagCorp: 'UI/Calendar/CalendarWindow/GroupCorp',
 const.calendarTagAlliance: 'UI/Calendar/CalendarWindow/GroupAlliance',
 const.calendarTagCCP: 'UI/Calendar/CalendarWindow/GroupCcp',
 const.calendarTagAutomated: 'UI/Calendar/CalendarWindow/GroupAutomated'}
TAGLIST = [const.calendarTagPersonal,
 const.calendarTagCorp,
 const.calendarTagAlliance,
 const.calendarTagCCP,
 const.calendarTagAutomated]

class CalendarSvc(Service):
    __guid__ = 'svc.calendar'
    __displayname__ = 'Calendar service'
    __notifyevents__ = ['OnNewCalendarEvent',
     'OnEditCalendarEvent',
     'OnRemoveCalendarEvent',
     'OnSessionChanged',
     'OnEventResponseByExternal']
    __startupdependencies__ = ['settings', 'objectCaching']

    def Run(self, *etc):
        self.state = SERVICE_START_PENDING
        self.events = {}
        self.eventDetails = {}
        self.eventsNotified = set()
        self.nextEvents = {}
        self.eventResponses = None
        self.calendarMgr = sm.RemoteSvc('calendarMgr')
        self.state = SERVICE_RUNNING
        self._calendarProxy = None
        self.notificationThread = AutoTimer(60000, self.CheckForNewEvents_thread)

    def GetCalendarProxy(self):
        if self._calendarProxy is None:
            self._calendarProxy = sm.ProxySvc('calendarProxy')
        return self._calendarProxy

    def IsInPast(self, year, month, monthday, hour = 0, min = 0, allowToday = 0, *args):
        now = blue.os.GetWallclockTime()
        if allowToday:
            cyear, cmonth, cwd, cday, chour, cmin, csec, cms = GetTimeParts(now)
            now = blue.os.GetTimeFromParts(cyear, cmonth, cday, 0, 0, 0, 0)
        thisDay = blue.os.GetTimeFromParts(year, month, monthday, hour, min, 0, 0)
        return self.IsInPastFromBlueTime(thisDay, now)

    def IsInPastFromBlueTime(self, then, now = None, *args):
        if now is None:
            now = blue.os.GetWallclockTime() + eveLocalization.GetTimeDelta() * const.SEC
        inPast = now > then
        return inPast

    def IsTooFarInFuture(self, year, month):
        now = blue.os.GetWallclockTime()
        rlYear, rlMonth, wd, day, hour, min, sec, ms = GetTimeParts(now)
        nowNumMonths = rlYear * 12 + rlMonth
        thenNumMonths = year * 12 + month
        difference = thenNumMonths - nowNumMonths
        if difference > const.calendarViewRangeInMonths:
            return True
        return False

    def FlushCache(self):
        self.events = {}
        self.nextEvents = {}

    def GetMonthText(self, year, month, *args):
        return localization.GetByLabel(MONTHANDYEAR_NAME_TEXT[month - 1], year=year)

    def GetBrowsedMonth(self, direction, year, month):
        if direction == 1:
            if month == const.calendarDecember:
                year += 1
                month = const.calendarJanuary
            else:
                month += 1
        elif direction == -1:
            if month == const.calendarJanuary:
                year -= 1
                month = const.calendarDecember
            else:
                month -= 1
        return (year, month)

    def GetEventMenu(self, eventInfo, myResponse = None, getJumpOption = True, *args):
        m = []
        m.append((MenuLabel('/Carbon/UI/Calendar/ViewEvent'), self.OpenEventWnd, (eventInfo,)))
        if getattr(eventInfo, 'isDeleted', None):
            return m
        canDelete = 0
        if not self.IsInPastFromBlueTime(then=eventInfo.eventDateTime):
            if eventInfo.ownerID != session.charid:
                if eventInfo.flag in [const.calendarTagCorp, const.calendarTagAlliance]:
                    if eventInfo.ownerID in [session.corpid, session.allianceid] and session.corprole & const.corpRoleChatManager == const.corpRoleChatManager:
                        canDelete = 1
                        m.append((MenuLabel('/Carbon/UI/Calendar/EditEvent'), self.OpenEditEventWnd, (eventInfo,)))
                if myResponse is None:
                    iconPath, myResponse = self.GetMyResponseIconFromID(eventInfo.eventID)
                m.append(None)
                if eventInfo.flag is not const.calendarTagCCP:
                    if myResponse != const.eventResponseAccepted:
                        m.append((MenuLabel('/Carbon/UI/Calendar/Accept'), self.RespondToEvent, (eventInfo.eventID, eventInfo, const.eventResponseAccepted)))
                    if myResponse != const.eventResponseMaybe:
                        m.append((MenuLabel('/Carbon/UI/Calendar/MaybeReply'), self.RespondToEvent, (eventInfo.eventID, eventInfo, const.eventResponseMaybe)))
                    if myResponse != const.eventResponseDeclined:
                        m.append((MenuLabel('/Carbon/UI/Calendar/Decline'), self.RespondToEvent, (eventInfo.eventID, eventInfo, const.eventResponseDeclined)))
            elif eventInfo.flag == const.calendarTagPersonal:
                canDelete = 1
                m.append((MenuLabel('/Carbon/UI/Calendar/EditEvent'), self.OpenEditEventWnd, (eventInfo,)))
        if getJumpOption:
            m.append(None)
            m.append((MenuLabel('/Carbon/UI/Calendar/GotoDay'), self.JumpToDay, (eventInfo,)))
        if canDelete:
            m.append(None)
            m.append((MenuLabel('/Carbon/UI/Calendar/DeleteEvent'), self.DeleteEvent, (eventInfo.eventID, eventInfo.ownerID)))
        return m

    def JumpToDay(self, eventInfo):
        calendar = self.FindCalendar()
        if calendar:
            year, month, wd, monthday, hour, minute, sec, ms = blue.os.GetTimeParts(eventInfo.eventDateTime)
            calendar.SetMonth(year, month, updateInView=1)
            blue.synchro.Yield()
            if calendar and not calendar.destroyed:
                calendar.CrawlForAndSetMonthday(monthday)

    def OpenNewEventWnd(self, year, month, monthday, *args):
        configname = 'calendarNewEventWnd_%s_%s_%s' % (year, month, monthday)
        CalendarNewEventWnd.Open(windowID=configname, year=year, month=month, monthday=monthday)

    def CreateNewEvent(self, dateTime, duration, title, description, eventTag, important = 0, invitees = []):
        if not title.strip():
            raise UserError('CalendarEventMustSpecifyTitle')
        year, month, wd, day, hour, min, sec, ms = blue.os.GetTimeParts(dateTime)
        if self.IsTooFarInFuture(year, month):
            raise UserError('CalendarTooFarIntoFuture', {'numMonths': const.calendarViewRangeInMonths})
        if len(title) > const.calendarMaxTitleSize:
            raise UserError('CalendarTitleTooLong')
        newEventID = None
        if eventTag == const.calendarTagPersonal:
            if invitees:
                newEventID = eveMisc.CSPAChargedAction('CSPACalendarCheck', self.calendarMgr, 'CreatePersonalEvent', dateTime, duration, title, description, important, invitees)
            else:
                newEventID = self.calendarMgr.CreatePersonalEvent(dateTime, duration, title, description, important, invitees)
            if newEventID is not None:
                self.OnNewCalendarEvent(eventID=newEventID, ownerID=session.charid, eventDateTime=dateTime, eventDuration=duration, eventTitle=title, importance=important)
                if self.eventResponses is not None:
                    self.eventResponses[newEventID] = const.eventResponseAccepted
        elif eventTag == const.calendarTagCorp:
            newEventID = self.calendarMgr.CreateCorporationEvent(dateTime, duration, title, description, important)
        elif eventTag == const.calendarTagAlliance:
            newEventID = self.calendarMgr.CreateAllianceEvent(dateTime, duration, title, description, important)

    def UpdateEventParticipants(self, eventID, charsToAdd, charsToRemove):
        if eventID is not None:
            if len(charsToAdd) > 0:
                eveMisc.CSPAChargedAction('CSPACalendarCheck', self.calendarMgr, 'UpdateEventParticipants', eventID, charsToAdd, charsToRemove)
            elif len(charsToRemove) > 0:
                self.calendarMgr.UpdateEventParticipants(eventID, charsToAdd, charsToRemove)
            self.objectCaching.InvalidateCachedMethodCall('calendarMgr', 'GetResponsesToEvent', eventID, session.charid)

    def EditEvent(self, eventID, oldDateTime, dateTime, duration, title, description, eventTag, important = 0):
        year, month, wd, day, hour, min, sec, ms = blue.os.GetTimeParts(dateTime)
        if self.IsTooFarInFuture(year, month):
            raise UserError('CalendarTooFarIntoFuture', {'numMonths': const.calendarViewRangeInMonths})
        if oldDateTime != dateTime:
            if eve.Message('CalendarEventEditDate', {}, uiconst.YESNO) != uiconst.ID_YES:
                return False
        if eventTag == const.calendarTagPersonal:
            self.calendarMgr.EditPersonalEvent(eventID, oldDateTime, dateTime, duration, title, description, important)
        elif eventTag == const.calendarTagCorp:
            self.calendarMgr.EditCorporationEvent(eventID, oldDateTime, dateTime, duration, title, description, important)
        elif eventTag == const.calendarTagAlliance:
            self.calendarMgr.EditAllianceEvent(eventID, oldDateTime, dateTime, duration, title, description, important)
        return True

    def GetEventFlag(self, ownerID, autoEventType = None):
        if ownerID == session.corpid:
            if autoEventType is None:
                return const.calendarTagCorp
            return const.calendarTagAutomated
        elif ownerID == session.allianceid:
            return const.calendarTagAlliance
        elif ownerID == const.ownerSystem:
            return const.calendarTagCCP
        else:
            return const.calendarTagPersonal

    def GetEventsByMonthYear(self, month, year):
        eventList = self.events.get((month, year))
        if eventList is None:
            eventList = []
            dbRowList = self.GetCalendarProxy().GetEventList(month, year)
            for dbRows in dbRowList:
                if dbRows is not None:
                    eventList.extend([ utillib.KeyVal(x) for x in dbRows ])

            for x in eventList:
                x.flag = self.GetEventFlag(x.ownerID, x.Get('autoEventType', None))

            self.events[month, year] = eventList
        return eventList

    def GetEventResponses(self):
        if self.eventResponses is None:
            dbRows = self.calendarMgr.GetResponsesForCharacter()
            self.eventResponses = {}
            for dbRow in dbRows:
                self.eventResponses[dbRow.eventID] = dbRow.status

        return self.eventResponses

    def GetEventDetails(self, eventID, ownerID):
        if eventID not in self.eventDetails:
            self.eventDetails[eventID] = self.GetCalendarProxy().GetEventDetails(eventID, ownerID)
        return self.eventDetails[eventID]

    def OpenSingleDayWnd(self, header, year, month, monthday, events, isADay = 1, wndType = 'singleWndDay', *args):
        windowInstanceID = '%s_%s_%s_%s' % (wndType,
         year,
         month,
         monthday)
        wnd = CalendarSingleDayWnd.GetIfOpen(windowID=wndType, windowInstanceID=windowInstanceID)
        if wnd:
            wnd.Maximize()
            return
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if not shift:
            for someWnd in uicore.registry.GetWindows()[:]:
                if isinstance(someWnd, CalendarSingleDayWnd):
                    someWnd.CloseByUser()

        wnd = CalendarSingleDayWnd.Open(windowID=wndType, windowInstanceID=windowInstanceID, header=header, wndType=wndType, year=year, month=month, monthday=monthday, events=events, isADay=isADay)

    def OpenEditEventWnd(self, eventInfo, *args):
        self.OpenEventWnd(eventInfo, edit=1)

    def OpenEventWnd(self, eventInfo, edit = 0, *args):
        year, month, wd, monthday, hour, min, sec, ms = blue.os.GetTimeParts(eventInfo.eventDateTime)
        windowInstanceID = 'calendarEventWnd_%s' % eventInfo.eventID
        if edit:
            wnd = CalendarNewEventWnd.GetIfOpen(windowID='calendarEventWnd', windowInstanceID=windowInstanceID)
            if wnd and not wnd.inEditMode:
                wnd.CloseByUser()
        wnd = CalendarNewEventWnd.Open(windowID='calendarEventWnd', windowInstanceID=windowInstanceID, year=year, month=month, monthday=monthday, eventInfo=eventInfo, edit=edit)
        if wnd:
            wnd.Maximize()

    def RespondToEvent(self, eventID, eventKV, response):
        self.calendarMgr.SendEventResponse(eventID, eventKV.ownerID, response)
        self._RespondToEvent(eventID, eventKV, response)

    def _RespondToEvent(self, eventID, eventKV, response):
        if self.eventResponses is not None:
            self.eventResponses[eventID] = response
        if response != const.eventResponseDeclined:
            if eventKV.eventDateTime > blue.os.GetWallclockTime():
                year, month = GetYearMonthFromTime(eventKV.eventDateTime)
                if self.IsInNextEventsWindow(year, month):
                    self.nextEvents[eventID] = eventKV
        elif eventID in self.nextEvents:
            self.nextEvents.pop(eventID, None)
        self.objectCaching.InvalidateCachedMethodCall('calendarMgr', 'GetResponsesToEvent', eventID, eventKV.ownerID)
        sm.ScatterEvent('OnReloadToDo')
        sm.ScatterEvent('OnRespondToEvent')
        sm.ScatterEvent('OnReloadCalendar')

    def DeleteEvent(self, eventID, ownerID):
        if eve.Message('CalendarDeleteEvent', {}, uiconst.YESNO) != uiconst.ID_YES:
            return False
        self.calendarMgr.DeleteEvent(eventID, ownerID)
        name = 'calendarEventWnd_%s' % eventID
        CalendarNewEventWnd.CloseIfOpen(windowID=name)
        return True

    def IsInNextEventsWindow(self, eventYear, eventMonth):
        now = blue.os.GetWallclockTime() + eveLocalization.GetTimeDelta() * const.SEC
        nowYear, nowMonth = GetYearMonthFromTime(now)
        if eventYear == nowYear:
            return eventMonth in (nowMonth, nowMonth + 1)
        if eventYear == nowYear + 1:
            return nowMonth == const.calendarDecember and eventMonth == const.calendarJanuary
        return False

    def OnNewCalendarEvent(self, eventID, ownerID, eventDateTime, eventDuration, eventTitle, importance, autoEventType = None, doBlink = True):
        year, month = GetYearMonthFromTime(eventDateTime)
        now = blue.os.GetWallclockTime()
        eventList = self.events.get((month, year))
        if eventList is not None:
            if eventID not in [ x.eventID for x in eventList ]:
                eventKV = utillib.KeyVal(eventID=eventID, ownerID=ownerID, eventDateTime=eventDateTime, eventDuration=eventDuration, eventTitle=eventTitle, importance=importance, flag=self.GetEventFlag(ownerID, autoEventType))
                eventKV.isDeleted = False
                eventKV.dateModified = blue.os.GetWallclockTime()
                eventList.append(eventKV)
                self.events[month, year] = eventList
                if eventDateTime > now and self.IsInNextEventsWindow(year, month):
                    self.nextEvents[eventID] = eventKV
        if doBlink and ownerID != session.charid and eventDateTime > now and self.IsInNextEventsWindow(year, month):
            sm.GetService('neocom').Blink('calendar', GetByLabel('UI/Neocom/Blink/NewCalendarEvent'))
        sm.ScatterEvent('OnReloadCalendar')
        sm.ScatterEvent('OnReloadToDo')

    def OnEditCalendarEvent(self, eventID, ownerID, oldEventDateTime, eventDateTime, eventDuration, eventTitle, importance, autoEventType = None):
        oldYear, oldMonth = GetYearMonthFromTime(oldEventDateTime)
        if eventID in self.nextEvents:
            self.nextEvents.pop(eventID)
        if eventID in self.eventDetails:
            self.eventDetails.pop(eventID)
        if oldEventDateTime != eventDateTime:
            if self.eventResponses is None:
                self.GetEventResponses()
            if ownerID != session.charid:
                oldReply = self.eventResponses.get(eventID, const.eventResponseUndecided)
                if oldReply in (const.eventResponseUndecided, const.eventResponseAccepted, const.eventResponseMaybe):
                    self.eventResponses[eventID] = const.eventResponseUndecided
                    year, month = GetYearMonthFromTime(eventDateTime)
                    if eventDateTime > blue.os.GetWallclockTime() and self.IsInNextEventsWindow(year, month):
                        sm.GetService('neocom').Blink('calendar', GetByLabel('UI/Neocom/Blink/CalendarEventModified'))
            self.objectCaching.InvalidateCachedMethodCall('calendarMgr', 'GetResponsesToEvent', eventID, ownerID)
        eventList = self.events.get((oldMonth, oldYear))
        if eventList is not None:
            for evt in eventList:
                if eventID == evt.eventID:
                    eventList.remove(evt)

            self.events[oldMonth, oldYear] = eventList
        self.OnNewCalendarEvent(eventID, ownerID, eventDateTime, eventDuration, eventTitle, importance, autoEventType, doBlink=False)

    def OnRemoveCalendarEvent(self, eventID, eventDateTime, isDeleted):
        year, month, wd, monthday, hour, min, sec, ms = blue.os.GetTimeParts(eventDateTime)
        eventList = self.events.get((month, year))
        if eventList is not None:
            for x in eventList:
                if x.eventID == eventID:
                    if isDeleted:
                        x.isDeleted = True
                        x.dateModified = blue.os.GetWallclockTime()
                    else:
                        eventList.remove(x)
                    break

            self.events[month, year] = eventList
            if self.eventResponses and eventID in self.eventResponses and self.eventResponses.get(eventID, None) != const.eventResponseDeclined:
                self.eventResponses.pop(eventID)
        self.nextEventsFetched = False
        sm.ScatterEvent('OnReloadToDo')
        sm.ScatterEvent('OnReloadCalendar')

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' in change or 'allianceid' in change:
            self.events = {}
            self.nextEvents = {}
            self.nextEventsFetched = False
            sm.ScatterEvent('OnReloadToDo')
            sm.ScatterEvent('OnReloadCalendar')

    def OnEventResponseByExternal(self, eventID, eventKV, response):
        eventKV.flag = self.GetEventFlag(eventKV.flag)
        self._RespondToEvent(eventID, eventKV, response)

    def GetResponsesToEvent(self, eventID, ownerID):
        dbRows = self.calendarMgr.GetResponsesToEvent(eventID, ownerID)
        responseDict = {}
        for row in dbRows:
            if row.status != const.eventResponseUninvited:
                responseDict[row.characterID] = row.status

        return responseDict

    def GetResponsesToEventInStatusDict(self, eventID, responseDict):
        statusDict = {}
        accepted = []
        rejected = []
        noreply = []
        maybe = []
        for charID, response in responseDict.iteritems():
            if response == const.eventResponseUndecided:
                noreply.append(charID)
            elif response == const.eventResponseDeclined:
                rejected.append(charID)
            elif response == const.eventResponseAccepted:
                accepted.append(charID)
            elif response == const.eventResponseMaybe:
                maybe.append(charID)

        statusDict[const.eventResponseUndecided] = noreply
        statusDict[const.eventResponseDeclined] = rejected
        statusDict[const.eventResponseAccepted] = accepted
        statusDict[const.eventResponseMaybe] = maybe
        return statusDict

    def GetResponseIconNum(self, response):
        if response == const.eventResponseAccepted:
            return 'ui_38_16_193'
        if response in [const.eventResponseDeclined, const.eventResponseDeleted]:
            return 'ui_38_16_194'
        if response == const.eventResponseUndecided:
            return 'ui_38_16_177'
        if response == const.eventResponseMaybe:
            return 'ui_38_16_195'
        return 'ui_38_16_192'

    def GetLongResponseIconPath(self, response):
        return self.GetResponseIconNum(response)

    def GetMyResponseIconFromID(self, eventID, long = 0, getDeleted = 0):
        if getDeleted:
            myResponse = const.eventResponseDeleted
        else:
            myResponse = self.GetMyResponse(eventID)
        if long:
            icon = self.GetLongResponseIconPath(myResponse)
        else:
            icon = self.GetResponseIconNum(myResponse)
        return (icon, myResponse)

    def GetActiveTags(self, *args):
        showTags = 0
        for tag in TAGLIST:
            checked = settings.user.ui.Get('calendarTagCheked_%s' % tag, 1)
            if checked:
                showTags += tag

        return showTags

    def LoadTagIcon(self, tag):
        if tag not in [const.calendarTagCorp,
         const.calendarTagAlliance,
         const.calendarTagCCP,
         const.calendarTagAutomated]:
            return
        else:
            tagIconCont = Container(name='tagIconCont', parent=None, align=uiconst.TOPLEFT, pos=(0, 0, 14, 14))
            self.LoadTagIconInContainer(tag, tagIconCont, left=0, top=0)
            return tagIconCont

    def LoadTagIconInContainer(self, tag, cont, left = 2, top = 4, *args):
        cont.Flush()
        if tag == const.calendarTagCorp:
            AddAndSetFlagIcon(parentCont=cont, flag=state.flagSamePlayerCorp, top=top, left=left)
        elif tag == const.calendarTagAlliance:
            AddAndSetFlagIcon(parentCont=cont, flag=state.flagSameAlliance, top=top, left=left)
        elif tag == const.calendarTagCCP:
            self.LoadCCPIcon(cont, top, left)
        elif tag == const.calendarTagAutomated:
            self.LoadAutomatedIcon(cont, top, left)

    def LoadCCPIcon(self, container, top, left, *args):
        if getattr(container.sr, 'flag', None) is None or container.sr.flag.destroyed:
            container.sr.flag = FlagIcon(parent=container, left=left, top=top, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        container.sr.flag.SetBackgroundColor((0.7, 0.7, 0.7))
        container.sr.flag.SetIconTexturePath(iconIdx=2)

    def LoadAutomatedIcon(self, container, top, left, *args):
        if getattr(container.sr, 'flag', None) is None or container.sr.flag.destroyed:
            container.sr.flag = FlagIcon(parent=container, pos=(left,
             top,
             11,
             11), state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        container.sr.flag.flagIcon.texturePath = 'res:/UI/Texture/Icons/AutomatedEntry_Icon_Alpha.png'
        color = sm.GetService('stateSvc').GetStateFlagColor(state.flagSamePlayerCorp)
        container.sr.flag.SetBackgroundColor(color, opacity=0.75)

    def GetMyChangedEvents(self, monthsAhead = 1):
        events = self.GetEventsNextXMonths(monthsAhead)
        showTag = self.GetActiveTags()
        changedEvents = {}
        now = blue.os.GetWallclockTime() + eveLocalization.GetTimeDelta() * const.SEC
        for eventID, eventKV in events.iteritems():
            if self.IsInUpdateEventsList(now, eventKV) and (showTag is None or showTag & eventKV.flag != 0):
                changedEvents[eventID] = eventKV

        return changedEvents

    def GetMyNextEvents(self, monthsAhead = 1):
        events = self.GetEventsNextXMonths(monthsAhead)
        showTag = self.GetActiveTags()
        myNextEvents = {}
        now = blue.os.GetWallclockTime() + eveLocalization.GetTimeDelta() * const.SEC
        for eventID, eventKV in events.iteritems():
            if self.IsOnToDoList(now, eventKV) and (showTag is None or showTag & eventKV.flag != 0):
                myNextEvents[eventID] = eventKV

        return myNextEvents

    def GetEventsNextXMonths(self, monthsAhead = 1, force = 0):
        if getattr(self, 'nextEventsFetched', False) and not force:
            return self.nextEvents
        self.nextEvents = self.FetchNextEvents(monthsAhead=monthsAhead)
        self.nextEventsFetched = True
        return self.nextEvents

    def FetchNextEvents(self, monthsAhead = 1):
        now = blue.os.GetWallclockTime() + eveLocalization.GetTimeDelta() * const.SEC
        year, month, wd, day, hour, minute, sec, ms = blue.os.GetTimeParts(now)
        nextEvents = self.FetchNextEventsDict(month, year, now)
        for i in xrange(monthsAhead):
            monthsFromNow = i + 1
            y, m = self.GetBrowsedMonth(monthsFromNow, year, month)
            nextMonthEvents = self.FetchNextEventsDict(m, y, now)
            nextEvents.update(nextMonthEvents)

        return nextEvents

    def FetchNextEventsDict(self, month, year, now):
        dict = {}
        events = self.GetEventsByMonthYear(month, year)
        for eventKV in events:
            dict[eventKV.eventID] = eventKV

        return dict

    def IsOnToDoList(self, now, eventKV):
        if eventKV.eventDateTime < now:
            return False
        if eventKV.isDeleted:
            return False
        if self.GetMyResponse(eventKV.eventID) in [const.eventResponseDeclined]:
            return False
        return True

    def IsInUpdateEventsList(self, now, eventKV):
        if now > eventKV.eventDateTime:
            return False
        myResponse = self.GetMyResponse(eventKV.eventID)
        if eventKV.isDeleted and myResponse != const.eventResponseDeclined:
            return True
        if myResponse == const.eventResponseUndecided:
            return True
        return False

    def GetMyResponse(self, eventID):
        if self.eventResponses is None:
            self.GetEventResponses()
        myResponse = self.eventResponses.get(eventID, const.eventResponseUndecided)
        return myResponse

    def GetEventHint(self, eventInfo, myResponse):
        if eventInfo is None:
            return ''
        if eventInfo.eventDuration is None:
            durationLabel = localization.GetByLabel('UI/Calendar/EventWindow/DateNotSpecified')
        else:
            hours = eventInfo.eventDuration / 60
            durationLabel = localization.GetByLabel('UI/Calendar/EventWindow/DateSpecified', hours=hours)
        responseLabel = localization.GetByLabel(self.GetResponseType().get(myResponse, 'UI/Generic/Unknown'))
        if getattr(eventInfo, 'eventTimeStamp', None) is None:
            year, month, wd, day, hour, min, sec, ms = blue.os.GetTimeParts(eventInfo.eventDateTime)
            ts = time.struct_time((year,
             month,
             day,
             hour,
             min,
             sec,
             0,
             1,
             0))
            eventInfo.eventTimeStamp = localization.formatters.FormatDateTime(value=ts, dateFormat='none', timeFormat='short')
        et = self.GetEventTypes().get(eventInfo.flag, '-')
        if et != '-':
            et = localization.GetByLabel(et)
        hint = localization.GetByLabel('UI/Calendar/Hints/Event', time=eventInfo.eventTimeStamp, title=eventInfo.eventTitle, eventType=et, response=responseLabel, duration=durationLabel, owner=cfg.eveowners.Get(eventInfo.ownerID).name)
        if eventInfo.importance > 0:
            hint += localization.GetByLabel('UI/Calendar/Hints/EventImportant')
        return hint

    def GetResponseType(self, *args):
        return RESPONSETYPES

    def GetEventTypes(self, *args):
        return EVENTTYPES

    def ShowCharacterInfo(self, itemID):
        return sm.GetService('info').ShowInfo(const.typeCharacter, itemID)

    def FindCalendar(self, *args):
        calendar = None
        wnd = CalendarWnd.GetIfOpen()
        if wnd:
            calendar = wnd.sr.calendarForm
        return calendar

    def CheckForNewEvents_thread(self):
        if not session.charid:
            return
        showTagMask = self.GetActiveTags()
        if not showTagMask:
            return
        if not AreNotificationActiveForCalendarEvents():
            return
        events = self.GetEventsNextXMonths()
        now = blue.os.GetWallclockTime()
        newEnoughTime = now - 5 * const.MIN
        notificationSvc = sm.GetService('notificationSvc')
        for each in events.itervalues():
            if each.isDeleted:
                continue
            if each.eventID in self.eventsNotified:
                continue
            if showTagMask & each.flag == 0:
                continue
            if newEnoughTime < each.eventDateTime <= now:
                with ExceptionEater('NotificationSvc: CheckForNewEvents_thread'):
                    notificationData = CalendarNotificationFormatter.MakeData(each)
                    notificationSvc.MakeAndScatterNotification(type=notificationConst.notificationTypeCalendarEvent, data=notificationData)
                self.eventsNotified.add(each.eventID)


def AreNotificationActiveForCalendarEvents():
    notificationSetting = settings.char.notifications.Get('notificationSettingsData', {}).get(notificationConst.notificationTypeCalendarEvent)
    if not notificationSetting:
        return True
    settingData = NotificationSettingData.fromTuple(notificationSetting)
    if settingData.showPopup or settingData.showAtAll:
        return True
    return False
