#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\gametime\delays.py
from gametime import GetSecondsUntilWallclockTime
from uthread2 import Sleep

def SleepUntilWallclockTime(wakeUpTime, minSleepSeconds = 0):
    duration = GetSecondsUntilWallclockTime(wakeUpTime)
    while duration > 86400:
        Sleep(86400)
        duration -= 86400

    Sleep(max(duration, minSleepSeconds))
