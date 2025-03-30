#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\structures\reinforce.py
import datetime
from random import randint
import datetimeutils
from structures import NO_REINFORCEMENT_WEEKDAY

class ReinforceTiming(object):
    reinforceWeekday = None
    reinforceHour = None
    nextReinforceWeekday = None
    nextReinforceHour = None
    applyAtTime = None

    def SetReinforceTimes(self, reinforceWeekday, reinforceHour):
        self.reinforceWeekday = reinforceWeekday
        self.reinforceHour = reinforceHour
        self.nextReinforceWeekday = None
        self.nextReinforceHour = None
        self.applyAtTime = None

    def SetNextReinforceTimes(self, nextReinforceWeekday, nextReinforceHour, applyAtTime):
        self.nextReinforceWeekday = nextReinforceWeekday
        self.nextReinforceHour = nextReinforceHour
        self.applyAtTime = applyAtTime

    def GetStateForClient(self):
        from carbon.common.script.util.format import DateToBlue
        return (self.reinforceWeekday,
         self.reinforceHour,
         self.nextReinforceWeekday,
         self.nextReinforceHour,
         DateToBlue(self.applyAtTime))

    def LoadFromRow(self, structureRow):
        from carbon.common.script.util.format import BlueToDate
        self.reinforceWeekday = structureRow.reinforce_weekday
        self.reinforceHour = structureRow.reinforce_hour
        self.nextReinforceWeekday = structureRow.next_reinforce_weekday
        self.nextReinforceHour = structureRow.next_reinforce_hour
        self.applyAtTime = BlueToDate(structureRow.next_reinforce_apply)

    def Persist(self, dbstructure, structureID):
        from carbon.common.script.util.format import DateToBlue
        dbstructure.Structures_UpdateReinforce(structureID, self.reinforceWeekday, self.reinforceHour, self.nextReinforceWeekday, self.nextReinforceHour, DateToBlue(self.applyAtTime))

    def GetEarliestTimeAfterDatetime(self, startDateTimeUTC):
        if self.reinforceHour is None:
            return startDateTimeUTC
        import gametime
        timezoneOffsetInHours = gametime.GetTimeOffsetInHours()
        startDateTimeLocal = startDateTimeUTC + datetime.timedelta(hours=timezoneOffsetInHours)
        exitTime = datetime.time(hour=self.reinforceHour)
        exitDateTimeLocal = datetimeutils.find_earliest_time_after_datetime(startDateTimeLocal, exitTime)
        return exitDateTimeLocal - datetime.timedelta(hours=timezoneOffsetInHours)

    def IsNextChangeReady(self, currentTime):
        if self.applyAtTime is None:
            return False
        return self.applyAtTime < currentTime

    def ApplyNextTiming(self):
        self.reinforceWeekday = self.nextReinforceWeekday
        self.reinforceHour = self.nextReinforceHour
        self.nextReinforceWeekday = None
        self.nextReinforceHour = None
        self.applyAtTime = None

    def SecondsUntilReinforceRollover(self, currentTime):
        if self.applyAtTime:
            return int((self.applyAtTime - currentTime).total_seconds())


def CheckReinforceTime(reinforceWeekday, reinforceHour, typeID = None):
    if typeID is None:
        if not 0 <= reinforceWeekday <= 6:
            raise ValueError('reinforceWeekday must be 0..6')
    elif reinforceWeekday != NO_REINFORCEMENT_WEEKDAY:
        raise ValueError('reinforceWeekday must be None')
    if not 0 <= reinforceHour <= 23:
        raise ValueError('reinforceHour must be 0..23')


def CheckReinforceHour(reinforceHour):
    if not 0 <= reinforceHour <= 23:
        raise ValueError('reinforceHour must be 0..23')


def GenerateJitterTimeDelta(jitterRange):
    seconds = randint(-jitterRange, jitterRange)
    return datetime.timedelta(seconds=seconds)
