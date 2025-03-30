#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\calendar.py
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
from utillib import KeyVal

class CalendarNotificationFormatter(BaseNotificationFormatter):

    @staticmethod
    def MakeData(eventInfo):
        data = {'eventInfo': eventInfo}
        return data

    def Format(self, notification):
        data = notification.data
        self._FormatSubject(data, notification)

    def _FormatSubject(self, data, notification):
        eventInfo = data['eventInfo']
        notification.subject = GetByLabel('Notifications/NotificationSettings/CalendarEvent', eventTitle=eventInfo.eventTitle)
        try:
            eventDetails = sm.GetService('calendar').GetEventDetails(eventInfo.eventID, eventInfo.ownerID)
            text = eventDetails.eventTex
        except AttributeError:
            text = ''

        notification.subtext = text

    @staticmethod
    def MakeSampleData(variant = 0):
        eventInfo = KeyVal({'eventTitle': 'Calendar Event Title Example'})
        return CalendarNotificationFormatter.MakeData(eventInfo)
