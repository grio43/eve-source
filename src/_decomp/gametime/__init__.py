#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\gametime\__init__.py
from carbon.common.lib.const import BLUE_TICK, HNSEC, uSEC, MSEC, SEC, MIN, HOUR, DAY, WEEK
EPOCH_BLUE_TIME = 116444736000000000L

class BlueTimeImplementation(object):

    def __init__(self):
        import blue
        self.GetSimTime = blue.os.GetSimTime
        self.GetWallclockTime = blue.os.GetWallclockTime
        self.GetWallclockTimeNow = blue.os.GetWallclockTimeNow


class PythonTimeImplementation(object):

    def __init__(self):
        import time
        GetTime = lambda : long(time.time() * SEC)
        self.GetSimTime = GetTime
        self.GetWallclockTime = GetTime
        self.GetWallclockTimeNow = GetTime


try:
    implementation = BlueTimeImplementation()
except ImportError:
    implementation = PythonTimeImplementation()

GetSimTime = implementation.GetSimTime
GetWallclockTime = implementation.GetWallclockTime
GetWallclockTimeNow = implementation.GetWallclockTimeNow

def GetTimeDiff(a, b, unit_conversion_to = BLUE_TICK, cast_to_class = long):
    return cast_to_class(float(b - a) / unit_conversion_to)


def GetTimeDiffInMs(a, b, cast_to_class = long):
    return GetTimeDiff(a, b, MSEC, cast_to_class)


def GetTimeSinceWallclockTime(time, unit_conversion_to = BLUE_TICK, cast_to_class = long):
    return cast_to_class(float(GetWallclockTime() - time) / unit_conversion_to)


def GetSecondsSinceWallclockTime(time, cast_to_class = float):
    return GetTimeSinceWallclockTime(time, SEC, cast_to_class)


def GetHoursSinceWallclockTime(time, cast_to_class = float):
    return GetTimeSinceWallclockTime(time, HOUR, cast_to_class)


def GetDaysSinceWallclockTime(time, cast_to_class = float):
    return GetTimeSinceWallclockTime(time, DAY, cast_to_class)


def GetWallclockTimeAfter(interval, unit_conversion_from = BLUE_TICK):
    return GetWallclockTime() + long(interval * unit_conversion_from)


def GetWallclockTimeAfterSeconds(seconds):
    return GetWallclockTimeAfter(seconds, SEC)


def GetTimeUntilWallclockTime(time, unit_conversion_to = BLUE_TICK, cast_to_class = long):
    return -GetTimeSinceWallclockTime(time, unit_conversion_to, cast_to_class)


def GetSecondsUntilWallclockTime(time, cast_to_class = float):
    return -GetSecondsSinceWallclockTime(time, cast_to_class)


def GetTimeSinceSimTime(time, unit_conversion_to = BLUE_TICK, cast_to_class = long):
    return cast_to_class(float(GetSimTime() - time) / unit_conversion_to)


def GetSecondsSinceSimTime(time):
    return GetTimeSinceSimTime(time, SEC, float)


def GetTimeUntilSimTime(time, unit_conversion_to = BLUE_TICK, cast_to_class = long):
    return -GetTimeSinceSimTime(time, unit_conversion_to, cast_to_class)


def GetSecondsUntilSimTime(time):
    return -GetSecondsSinceSimTime(time)


def GetSimTimeAfter(interval, unit_conversion_from = BLUE_TICK):
    return GetSimTime() + long(interval * unit_conversion_from)


def GetSimTimeAfterSeconds(seconds):
    return GetSimTimeAfter(seconds, SEC)


def GetTimeOffsetInHours():
    try:
        import eveLocalization
        return int(eveLocalization.GetTimeDelta() / 3600)
    except ImportError:
        return 0


def GetDurationInClient(startTime, duration):
    return duration + (startTime - GetSimTime()) / MSEC


class Timer(object):

    def __init__(self, GetTime, Sleep, maxSleepTime):
        self.maxSleepTime = maxSleepTime
        self.GetTime = GetTime
        self.Sleep = Sleep

    def SleepUntil(self, wakeUpTime, minSleep = 5000):
        sleepTime = wakeUpTime - self.GetTime()
        if sleepTime > 0:
            while True:
                sleepTime = wakeUpTime - self.GetTime()
                if sleepTime <= self.maxSleepTime:
                    self.Sleep(sleepTime / MSEC)
                    break
                else:
                    self.Sleep(self.maxSleepTime / MSEC)

        else:
            self.Sleep(minSleep)


def now():
    import datetimeutils
    return datetimeutils.filetime_to_datetime(GetWallclockTime())


def now_sim():
    import datetimeutils
    return datetimeutils.filetime_to_datetime(GetSimTime())


def GetTimeUntilNowFromDateTime(date_time, unit_conversion_to = BLUE_TICK, cast_to_class = long):
    return cast_to_class(float(SEC * (date_time - now()).total_seconds()) / unit_conversion_to)


def GetTimeSinceDateTime(date_time, unit_conversion_to = BLUE_TICK, cast_to_class = long):
    return -GetTimeUntilNowFromDateTime(date_time, unit_conversion_to, cast_to_class)


def GetSimTimeUntilNowFromDateTime(date_time, unit_conversion_to = BLUE_TICK, cast_to_class = long):
    return cast_to_class(float(SEC * (date_time - now_sim()).total_seconds()) / unit_conversion_to)


def GetSimTimeSinceDateTime(date_time, unit_conversion_to = BLUE_TICK, cast_to_class = long):
    return -GetSimTimeUntilNowFromDateTime(date_time, unit_conversion_to, cast_to_class)
