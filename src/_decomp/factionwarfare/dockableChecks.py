#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\factionwarfare\dockableChecks.py
import evetypes
from eve.common.script.util.facwarCommon import IsOccupierEnemyFaction
import eve.common.lib.appConst as appConst

def IsDockableStructureUsageRestrictedByOccupationState(occupationState, shipFactionID):
    if not occupationState or occupationState.isFrontline:
        return False
    occupierID = occupationState.occupierID
    if shipFactionID and IsOccupierEnemyFaction(occupierID, shipFactionID):
        return True
    return False


def IsShipExemptFromDockingRestrictions(shipTypeID):
    if evetypes.GetGroupID(shipTypeID) == appConst.groupCapsule:
        return True
    return False
