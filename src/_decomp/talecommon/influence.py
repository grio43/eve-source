#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\talecommon\influence.py
from carbon.common.lib.const import MIN
import gametime

def CalculateDecayedInfluence(info):
    currentTime = gametime.GetWallclockTime()
    return CalculateDecayedInfluenceWithTime(info.influence, info.lastUpdated, currentTime, info.decayRate, info.graceTime)


def CalculateDecayedInfluenceWithTime(influence, lastUpdated, currentTime, decayRate, graceTime):
    if decayRate > 0.0 and currentTime - graceTime * MIN > lastUpdated:
        timePastGrace = (currentTime - lastUpdated) / MIN - graceTime
        hourPast = max(timePastGrace / 60.0, 0.0)
        decay = decayRate * hourPast
        influence = influence - decay
    else:
        influence = influence
    if influence < 0.0001:
        influence = 0.0
    return influence
