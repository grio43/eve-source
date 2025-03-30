#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corruptionsuppression\client\systemEffectsClient.py
from corruptionsuppression.systemEffects import BaseCorruptionWarpSpeedIncreaserChecker, WARP_SPEED_INCREASE_STAGE_THRESHOLD

class CorruptionWarpSpeedIncreaserCheckerClient(BaseCorruptionWarpSpeedIncreaserChecker):

    def DoesSystemHaveCorruptionWarpIncrease(self, solarSystemID):
        if solarSystemID != session.solarsystemid2:
            return False
        corruptionStage = sm.GetService('corruptionSuppressionSvc').GetSystemCorruptionStage(solarSystemID)
        if corruptionStage >= WARP_SPEED_INCREASE_STAGE_THRESHOLD:
            return True
        return False
