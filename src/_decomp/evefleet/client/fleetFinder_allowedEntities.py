#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evefleet\client\fleetFinder_allowedEntities.py
from brennivin.itertoolsext import Bundle

def GetDiffInAllowedAndBanned(currentAd, allowedInfoFromStandings):
    membergroupsAllowedEntities = allowedInfoFromStandings['membergroupsAllowedEntities']
    publicAllowedEntities = allowedInfoFromStandings['publicAllowedEntities']
    membergroupsDisallowedEntities = allowedInfoFromStandings['membergroupsDisallowedEntities']
    publicDisallowedEntities = allowedInfoFromStandings['publicDisallowedEntities']
    membergroupsToAddToAllowed, membergroupsToRemoveFromAllowed = _FindDiff(currentAd.membergroups_minStanding, membergroupsAllowedEntities, currentAd.membergroups_allowedEntities)
    membergroupsToAddToDisallowed, membergroupsToRemoveFromDisallowed = _FindDiff(currentAd.membergroups_minStanding, membergroupsDisallowedEntities, currentAd.membergroups_disallowedEntities)
    publicToAddToAllowed, publicToRemoveFromAllowed = _FindDiff(currentAd.public_minStanding, publicAllowedEntities, currentAd.public_allowedEntities)
    publicToAddToDisallowed, publicToRemoveFromDisallowed = _FindDiff(currentAd.public_minStanding, publicDisallowedEntities, currentAd.public_disallowedEntities)
    return Bundle(membergroupsToAddToAllowed=membergroupsToAddToAllowed, membergroupsToRemoveFromAllowed=membergroupsToRemoveFromAllowed, membergroupsToAddToDisallowed=membergroupsToAddToDisallowed, membergroupsToRemoveFromDisallowed=membergroupsToRemoveFromDisallowed, publicToAddToAllowed=publicToAddToAllowed, publicToRemoveFromAllowed=publicToRemoveFromAllowed, publicToAddToDisallowed=publicToAddToDisallowed, publicToRemoveFromDisallowed=publicToRemoveFromDisallowed)


def _FindDiff(minStandingSetting, currentAllowed, oldAllowed):
    if minStandingSetting is None:
        return (set(), set())
    currentAllowed = currentAllowed or set()
    oldAllowed = oldAllowed or set()
    toAdd = currentAllowed - oldAllowed
    toRemove = oldAllowed - currentAllowed
    return (toAdd, toRemove)
