#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\controllers\reinforceTimersBundle.py
from brennivin.itertoolsext import Bundle
from eve.client.script.ui.shared.eveCalendar import DAY_NAME_TEXT
from localization import GetByLabel
from structures import DEFAULT_REINFORCE_HOUR, DEFAULT_REINFORCE_WEEKDAY, NO_REINFORCEMENT_WEEKDAY

class ReinforcementBundle(Bundle):

    def GetReinforcementTime(self):
        return (self.GetReinforceWeekday(), self.GetReinforceHour())

    def GetReinforceWeekday(self):
        return getattr(self, 'reinforceWeekday', DEFAULT_REINFORCE_WEEKDAY)

    def GetReinforceHour(self):
        return getattr(self, 'reinforceHour', DEFAULT_REINFORCE_HOUR)

    def GetNextReinforcementTime(self):
        return (self.GetNextReinforceDay(), self.GetNextReinforceHour())

    def GetNextReinforceDay(self):
        return getattr(self, 'nextReinforceWeekday', None)

    def GetNextReinforceHour(self):
        return getattr(self, 'nextReinforceHour', None)

    def GetNextApply(self):
        return getattr(self, 'nextReinforceApply', None)


def GetDayAndHourText(day, hour):
    dayText = GetDayText(day)
    hourText = GetHourText(hour)
    return (dayText, hourText)


def GetHourText(hour):
    hourText = '%.2d:00' % hour if hour is not None else ''
    return hourText


def GetDayText(day):
    if day in (NO_REINFORCEMENT_WEEKDAY, None):
        return ''
    dayText = GetByLabel(DAY_NAME_TEXT[day])
    return dayText
