#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evefleet\util.py
from evefleet.const import fleetRoleLeader, fleetRoleMember, fleetRoleWingCmdr, BROADCAST_ALL, BROADCAST_UP, BROADCAST_DOWN, INVITE_CORP, INVITE_ALLIANCE, INVITE_MILITIA, INVITE_PUBLIC, INVITE_PUBLIC_OPEN

def IsSuperior(member, myself):
    if member.charID == myself.charID:
        return True
    if myself.role == fleetRoleLeader:
        return False
    if member.role == fleetRoleLeader:
        return True
    if myself.squadID > 0:
        if member.role != fleetRoleMember and member.wingID == myself.wingID:
            return True
    return False


def IsSubordinateOrEqual(member, myself):
    if member.charID == myself.charID:
        return True
    if myself.role == fleetRoleLeader:
        return True
    if myself.squadID > 0:
        if member.squadID == myself.squadID:
            return True
    if myself.role == fleetRoleWingCmdr:
        if member.wingID == myself.wingID:
            return True
    return False


def ShouldSendBroadcastTo(member, myself, scope):
    if scope == BROADCAST_ALL:
        return True
    if scope == BROADCAST_UP and IsSuperior(member, myself):
        return True
    if scope == BROADCAST_DOWN and IsSubordinateOrEqual(member, myself):
        return True
    return False


def IsOpenToCorp(fleet):
    return IsOpenToCorpFromMask(GetInviteScope(fleet))


def IsOpenToCorpFromMask(inviteScope):
    return inviteScope & INVITE_CORP == INVITE_CORP


def IsOpenToAlliance(fleet):
    return IsOpenToAllianceFromMask(GetInviteScope(fleet))


def IsOpenToAllianceFromMask(inviteScope):
    return inviteScope & INVITE_ALLIANCE == INVITE_ALLIANCE


def IsOpenToMilitia(fleet):
    return IsOpenToMilitiaFromMask(GetInviteScope(fleet))


def IsOpenToMilitiaFromMask(inviteScope):
    return inviteScope & INVITE_MILITIA == INVITE_MILITIA


def IsOpenToPublic(fleet):
    return IsOpenToPublicFromMask(GetInviteScope(fleet))


def IsOpenToPublicFromMask(inviteScope):
    return inviteScope & INVITE_PUBLIC == INVITE_PUBLIC


def GetInviteScope(fleet):
    return fleet.get('inviteScope', 0)


def IsOpenToAllPublic(fleet):
    return IsOpenToAllPublicFromMask(GetInviteScope(fleet))


def IsOpenToAllPublicFromMask(inviteScope):
    return inviteScope & INVITE_PUBLIC_OPEN == INVITE_PUBLIC_OPEN
