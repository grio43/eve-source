#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterskills\queue.py
import carbon.common.lib.const as const
from characterskills.util import GetSPForLevelRaw
import gametime
from clonegrade import CLONE_STATE_ALPHA
from eveprefs import boot
SKILLQUEUE_TIME_LIMIT = 10 * const.YEAR365
SKILLQUEUE_MAX_NUM_SKILLS = 150
USER_TYPE_NOT_ENFORCED = -1

def HasShortSkillqueue(cloneState):
    return cloneState == CLONE_STATE_ALPHA


def GetSkillQueueTimeLength(cloneState):
    return SKILLQUEUE_TIME_LIMIT


def GetQueueEntry(skillTypeID, skillLevel, queuePosition, currentSkill, currentQueue, GetTimeForTraining, KeyVal, activate, trainingStartTime = None):
    trainingEndTime = None
    if trainingStartTime is None and activate:
        if queuePosition == 0 or len(currentQueue) == 0:
            trainingStartTime = gametime.GetWallclockTime()
        else:
            trainingStartTime = currentQueue[queuePosition - 1].trainingEndTime
        trainingTime = GetTimeForTraining(skillTypeID, skillLevel)
        trainingEndTime = long(trainingStartTime) + long(trainingTime)
    if currentSkill.trainedSkillLevel == skillLevel - 1:
        trainingStartSP = currentSkill.trainedSkillPoints
    else:
        trainingStartSP = GetSPForLevelRaw(currentSkill.skillRank, skillLevel - 1)
    trainingDestinationSP = GetSPForLevelRaw(currentSkill.skillRank, skillLevel)
    return SkillQueueEntry(queuePosition, skillTypeID, skillLevel, trainingStartSP, trainingStartTime, trainingDestinationSP, trainingEndTime, KeyVal)


def SkillQueueEntry(queuePosition, skillTypeID, skillLevel, trainingStartSP, trainingStartTime, trainingDestinationSP, trainingEndTime, KeyVal):
    return KeyVal(queuePosition=queuePosition, trainingStartTime=trainingStartTime, trainingEndTime=trainingEndTime, trainingTypeID=skillTypeID, trainingToLevel=skillLevel, trainingStartSP=trainingStartSP, trainingDestinationSP=trainingDestinationSP)
