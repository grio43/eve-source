#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stargate\client\localGates.py
import appConst as const
from inventorycommon.const import groupUpwellJumpGate

def FindLocalStargate(destinationID, *args):
    if session.solarsystemid is None:
        return
    michelle = sm.GetService('michelle')
    solarSystemItems = cfg.GetLocationsLocalBySystem(session.solarsystemid, requireLocalizedTexts=False)
    for ssItem in solarSystemItems:
        if ssItem.groupID != const.groupStargate:
            continue
        slimItem = michelle.GetItem(ssItem.itemID)
        if not slimItem:
            continue
        if slimItem.jumps[0].locationID == destinationID:
            return slimItem


def FindLocalJumpGateForDestinationPath(destinationID, *args):
    bp = sm.GetService('michelle').GetBallpark()
    if not bp:
        return
    destinationPath = sm.GetService('starmap').GetDestinationPath()
    if not destinationPath:
        return
    if destinationID != destinationPath[0]:
        return
    for slimItem in bp.slimItems.itervalues():
        if slimItem.groupID == groupUpwellJumpGate:
            jumpToLocationID = getattr(slimItem, 'targetSolarsystemID', None)
            if jumpToLocationID == destinationPath[0]:
                return slimItem
