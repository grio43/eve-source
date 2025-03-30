#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\bountyUtil.py
import blue
from eve.common.script.sys import idCheckers
from eve.common.lib import appConst as const

def GetMinimumBountyAmount(ownerID):
    if idCheckers.IsCharacter(ownerID):
        return const.MIN_BOUNTY_AMOUNT_CHAR
    if idCheckers.IsCorporation(ownerID):
        return const.MIN_BOUNTY_AMOUNT_CORP
    if idCheckers.IsAlliance(ownerID):
        return const.MIN_BOUNTY_AMOUNT_ALLIANCE
    return 0


def CacheBounties(bountyDict, bountiesToCache):
    for bounty in bountiesToCache:
        bountyDict[bounty.targetID] = (bounty, blue.os.GetWallclockTime())
