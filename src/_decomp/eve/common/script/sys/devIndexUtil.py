#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\sys\devIndexUtil.py
import utillib
from eve.common.lib import appConst as const
timeIndexLevels = {1: 7,
 2: 21,
 3: 35,
 4: 65,
 5: 100}
devIndexDecayRate = 100000
devIndexDecayTime = 96

def GetDevIndexLevels():
    totalLevels = 5
    developmentIndexDecayRate = {}
    for indexID in [const.attributeDevIndexMilitary, const.attributeDevIndexIndustrial]:
        nextFloor = 0
        developmentIndexDecayRate[indexID] = {}
        for i in xrange(totalLevels + 1):
            developmentIndexDecayRate[indexID][i] = kv = utillib.KeyVal(level=i, minLevel=nextFloor, maxLevel=nextFloor + devIndexDecayRate * devIndexDecayTime)
            nextFloor = kv.maxLevel

    for i, (militaryModifier, industrialModifier) in enumerate([(5, 7.2),
     (3, 2.36),
     (2, 1.649),
     (1.5, 1.2),
     (1, 0.7),
     (0.8, 0.35)]):
        developmentIndexDecayRate[const.attributeDevIndexMilitary][i].modifier = militaryModifier
        developmentIndexDecayRate[const.attributeDevIndexIndustrial][i].modifier = industrialModifier

    return developmentIndexDecayRate


def GetTimeIndexLevels():
    day = 86400
    ret = []
    for i in xrange(1, 6):
        ret.append(timeIndexLevels[i] * day)

    return ret


def GetTimeIndexLevelForDays(days):
    daysInSeconds = days * 24 * 60
    for level in xrange(5, 0, -1):
        if days >= timeIndexLevels[level]:
            return level

    return 0
