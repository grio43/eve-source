#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\ballparkCommon\jumpdelay.py
from eve.common.lib.appConst import invulnerabilityJumping
from eve.common.script.sys.idCheckers import IsTriglavianSystem
import gametime
ABYSSAL_JUMP_DELAY_MS = 4000

def GetStargateJumpDelayMilliseconds(solarSystemID):
    if IsTriglavianSystem(solarSystemID):
        return ABYSSAL_JUMP_DELAY_MS
    return invulnerabilityJumping


def GetStargateJumpDelayBlueTime(solarSystemID):
    return GetStargateJumpDelayMilliseconds(solarSystemID) * gametime.MSEC
