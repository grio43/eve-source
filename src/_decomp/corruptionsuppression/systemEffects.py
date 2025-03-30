#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corruptionsuppression\systemEffects.py
import appConst
from crimewatch.const import targetGroupsWithSuspectPenaltyInHighSec
from eve.common.script.util.facwarCommon import IsPirateFWFaction
import logging
WARP_SPEED_INCREASE_STAGE_THRESHOLD = 4

def DoesConcordReact(dogmaLM, targetGroupID, isHighSec):
    if not isHighSec:
        return False
    if targetGroupID == appConst.groupCapsule:
        return True
    if targetGroupID in targetGroupsWithSuspectPenaltyInHighSec:
        return False
    if dogmaLM.IsFullyCorrupted():
        return False
    return True


class BaseCorruptionWarpSpeedIncreaserChecker(object):

    def __init__(self, solarSystemID):
        self._solarSystemID = solarSystemID
        self.defaultIncrease = 0.0
        self.doesSystemHaveCorruptionIncrease = None

    def GetWarpSpeedIncrease(self, charWarFactionID):
        if not charWarFactionID:
            return self.defaultIncrease
        try:
            if self.doesSystemHaveCorruptionIncrease is None:
                self.doesSystemHaveCorruptionIncrease = self.DoesSystemHaveCorruptionWarpIncrease(self._solarSystemID)
            if not self.doesSystemHaveCorruptionIncrease:
                return self.defaultIncrease
            if IsPirateFWFaction(charWarFactionID):
                return 2.0
            return self.defaultIncrease
        except StandardError:
            logging.exception('GetWarpSpeedIncrease failed')

        return self.defaultIncrease

    def DoesSystemHaveCorruptionWarpIncrease(self, solarSystemID):
        return False
