#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\util.py
from caching import Memoize
from eve.client.script.ui import eveColor
from fwwarzone.client.dashboard.const import FACTION_ID_TO_COLOR

def GetAttackerDefenderColors(solarSystemID):
    fwOccupationState = sm.GetService('fwWarzoneSvc').GetOccupationState(solarSystemID)
    if not fwOccupationState:
        return (None, None)
    occupierID = fwOccupationState.occupierID
    attackerID = fwOccupationState.attackerID
    attackerColor = FACTION_ID_TO_COLOR.get(attackerID, None)
    defenderColor = FACTION_ID_TO_COLOR.get(occupierID, None)
    return (attackerColor, defenderColor)


def GetSystemCaptureStatusColorFromVp(victoryPointState):
    if victoryPointState.isVulnerable:
        textColor = eveColor.DANGER_RED
    elif victoryPointState.isContested:
        textColor = eveColor.WARNING_ORANGE
    else:
        textColor = eveColor.SUCCESS_GREEN
    return textColor


@Memoize(3)
def CachedGetBattlefieldInstances():
    return sm.GetService('fwWarzoneSvc').GetBattlefieldInstances()
