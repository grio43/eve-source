#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\fleetbroadcastexports.py
from eve.client.script.ui.shared.fleet.fleetBroadcastConst import broadcastNames, LISTEN_BROADCAST_SETTING, broadcastScopes, broadcastRanges, defaultBroadcastRange, broadcastRangeNames
from evefleet import BROADCAST_LOCATION, BROADCAST_JUMP_BEACON, BROADCAST_TRAVEL_TO, BROADCAST_JUMP_TO, BROADCAST_ALIGN_TO, BROADCAST_NEED_BACKUP, BROADCAST_WARP_TO, BROADCAST_HEAL_CAPACITOR, BROADCAST_HEAL_SHIELD, BROADCAST_HEAL_ARMOR, BROADCAST_TARGET, BROADCAST_ENEMY_SPOTTED, BROADCAST_IN_POSITION
from eve.client.script.util.bubble import SlimItemFromCharID
from eve.common.script.sys.eveCfg import InShipInSpace
import evefleet
from evefleet.client.util import GetSelectedFormationName
import localization
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem
from eveservices.menu import GetMenuService
from menu import MenuLabel
from menucheckers import SessionChecker

def ShouldListen(gbName, senderRole, senderJob, senderWingID, senderSquadID):
    return settings.user.ui.Get(LISTEN_BROADCAST_SETTING % gbName, True) or senderRole == evefleet.fleetRoleLeader or senderJob == evefleet.fleetJobCreator or senderRole == evefleet.fleetRoleWingCmdr and senderWingID == session.wingid or senderRole == evefleet.fleetRoleSquadCmdr and senderSquadID == session.squadid


def FilteredBroadcast(f, name):

    def deco(self, senderID, *args, **kw):
        rec = sm.GetService('fleet').GetMembers().get(senderID)
        if not rec or ShouldListen(name, rec.role, rec.job, rec.wingID, rec.squadID):
            f(self, senderID, *args, **kw)

    return deco


def MenuGetter(gbType, *args):
    GetMenu = globals()['GetMenu_%s' % gbType]
    return lambda : GetMenu(*args)


def GetMenu_EnemySpotted(charID, locationID, nearID):
    where = Where(charID, locationID)
    menuSvc = GetMenuService()
    m = []
    if where in (inSystem, inBubble):
        defaultWarpDist = menuSvc.GetDefaultActionDistance(BROADCAST_WARP_TO)
        formationName = {'fleetFormation': GetSelectedFormationName()}
        m.extend([[MenuLabel('UI/Fleet/WarpToMember'), menuSvc.WarpToMember, (charID, float(defaultWarpDist))],
         [MenuLabel('UI/Fleet/WarpToMemberSubmenuOption'), menuSvc.WarpToMenu(menuSvc.WarpToMember, charID)],
         [MenuLabel('UI/Fleet/WarpFleetToMember', formationName), menuSvc.WarpFleetToMember, (charID, float(defaultWarpDist))],
         [MenuLabel('UI/Fleet/FleetSubmenus/WarpFleetToMember', formationName), menuSvc.WarpToMenu(menuSvc.WarpFleetToMember, charID)]])
    else:
        m.extend(GetMenu_TravelTo(charID, locationID, nearID))
    return m


GetMenu_NeedBackup = GetMenu_InPosition = GetMenu_EnemySpotted

def GetMenu_TravelTo(charID, solarSystemID, destinationID):
    destinationID = destinationID or solarSystemID
    starmapSvc = sm.GetService('starmap')
    waypoints = starmapSvc.GetWaypoints()
    m = [[MenuLabel('UI/Inflight/SetDestination'), starmapSvc.SetWaypoint, (destinationID, True)]]
    if destinationID in waypoints:
        m.append([MenuLabel('UI/Inflight/RemoveWaypoint'), starmapSvc.ClearWaypoints, (destinationID,)])
    else:
        m.append([MenuLabel('UI/Inflight/AddWaypoint'), starmapSvc.SetWaypoint, (destinationID,)])
    return m


def GetMenu_Location(charID, solarSystemID, nearID):
    if solarSystemID != session.solarsystemid2:
        m = GetMenu_TravelTo(charID, solarSystemID, None)
        m.append([MenuLabel('UI/Fleet/FleetSubmenus/ShowDistance'), sm.GetService('fleet').DistanceToFleetMate, (solarSystemID, nearID)])
    else:
        m = GetMenu_WarpTo(charID, solarSystemID, nearID)
    return m


def GetMenu_JumpBeacon(charID, solarSystemID, beaconID, typeID):
    menuSvc = GetMenuService()
    starmapSvc = sm.GetService('starmap')
    waypoints = starmapSvc.GetWaypoints()
    m = []
    if session.solarsystemid and session.shipid:
        sessionChecker = SessionChecker(session, sm)
        if sessionChecker.isShipJumpCapable():
            m.append([MenuLabel('UI/Inflight/JumpToFleetMember'), menuSvc.JumpToFleetModuleBeacon, (charID,
              solarSystemID,
              beaconID,
              typeID)])
            if sessionChecker.canOpenJumpPortal():
                m.append([MenuLabel('UI/Fleet/BridgeToMember'), menuSvc.BridgeToFleetModuleBeacon, (charID,
                  solarSystemID,
                  beaconID,
                  typeID)])
            if sessionChecker.canPerformGroupJump():
                m.append([MenuLabel('UI/Fleet/ConduitJumpToFleetMember'), menuSvc.GroupJumpToFleetModuleBeacon, (charID,
                  solarSystemID,
                  beaconID,
                  typeID)])
    m.append(None)
    m.append([MenuLabel('UI/Inflight/SetDestination'), starmapSvc.SetWaypoint, (solarSystemID, True)])
    if solarSystemID in waypoints:
        m.append([MenuLabel('UI/Inflight/RemoveWaypoint'), starmapSvc.ClearWaypoints, (solarSystemID,)])
    else:
        m.append([MenuLabel('UI/Inflight/AddWaypoint'), starmapSvc.SetWaypoint, (solarSystemID,)])
    return m


def GetMenu_WarpTo(charID, solarSystemID, locationID):
    return GetWarpLocationMenu(locationID)


def GetWarpLocationMenu(locationID):
    if not InShipInSpace():
        return []
    menuSvc = GetMenuService()
    defaultWarpDist = menuSvc.GetDefaultActionDistance(BROADCAST_WARP_TO)
    ret = [[MenuLabel('UI/Inflight/WarpToBookmark'), WarpToItem, (locationID, float(defaultWarpDist))], [MenuLabel('UI/Inflight/Submenus/WarpToWithin'), menuSvc.WarpToMenu(WarpToItem, locationID)], [MenuLabel('UI/Inflight/AlignTo'), menuSvc.AlignTo, (locationID,)]]
    formationName = {'fleetFormation': GetSelectedFormationName()}
    if session.fleetrole == evefleet.fleetRoleLeader:
        ret.extend([[MenuLabel('UI/Fleet/WarpFleetToLocation', formationName), menuSvc.WarpFleet, (locationID, float(defaultWarpDist))], [MenuLabel('UI/Fleet/FleetSubmenus/WarpFleetToLocationWithin', formationName), menuSvc.WarpToMenu(menuSvc.WarpFleet, locationID)]])
    elif session.fleetrole == evefleet.fleetRoleWingCmdr:
        ret.extend([[MenuLabel('UI/Fleet/WarpWingToLocation', formationName), menuSvc.WarpFleet, (locationID, float(defaultWarpDist))], [MenuLabel('UI/Fleet/FleetSubmenus/WarpWingToLocationWithin', formationName), menuSvc.WarpToMenu(menuSvc.WarpFleet, locationID)]])
    elif session.fleetrole == evefleet.fleetRoleSquadCmdr:
        ret.extend([[MenuLabel('UI/Fleet/WarpSquadToLocation', formationName), menuSvc.WarpFleet, (locationID, float(defaultWarpDist))], [MenuLabel('UI/Fleet/FleetSubmenus/WarpSquadToLocationWithin', formationName), menuSvc.WarpToMenu(menuSvc.WarpFleet, locationID)]])
    return ret


def GetMenu_Target(charID, solarSystemID, shipID):
    m = []
    targetSvc = sm.GetService('target')
    targets = targetSvc.GetTargets()
    if not targetSvc.BeingTargeted(shipID) and shipID not in targets:
        m = [(MenuLabel('UI/Inflight/LockTarget'), targetSvc.TryLockTarget, (shipID,))]
    return m


def GetMenu_Member(charID):
    m = [(MenuLabel('UI/Fleet/Ranks/FleetMember'), GetMenuService().FleetMenu(charID, unparsed=False))]
    return m


def GetMenu_Ignore(name):
    isListen = settings.user.ui.Get(LISTEN_BROADCAST_SETTING % name, True)
    if isListen:
        m = [(MenuLabel('UI/Fleet/FleetBroadcast/IgnoreBroadcast'), sm.GetService('fleet').SetListenBroadcast, (name, False))]
    else:
        m = [(MenuLabel('UI/Fleet/FleetBroadcast/UnignoreBroadcast'), sm.GetService('fleet').SetListenBroadcast, (name, True))]
    return m


def GetMenu_HealArmor(charID, solarSystemID, shipID):
    return GetMenu_Target(charID, solarSystemID, shipID)


def GetMenu_HealShield(charID, solarSystemID, shipID):
    return GetMenu_Target(charID, solarSystemID, shipID)


def GetMenu_HealCapacitor(charID, solarSystemID, shipID):
    return GetMenu_Target(charID, solarSystemID, shipID)


def GetMenu_Heal_Target(charID, solarSystemID, shipID):
    return GetMenu_Target(charID, solarSystemID, shipID)


def GetMenu_JumpTo(charID, solarSystemID, locationID):
    return GetMenu_WarpTo(charID, solarSystemID, locationID)


def GetMenu_AlignTo(charID, solarSystemID, locationID):
    return GetMenu_WarpTo(charID, solarSystemID, locationID)


def GetMenuFunc(broadcastName):
    if broadcastName == BROADCAST_ENEMY_SPOTTED:
        return GetMenu_EnemySpotted
    if broadcastName == BROADCAST_TARGET:
        return GetMenu_Target
    if broadcastName == evefleet.BROADCAST_REP_TARGET:
        return GetMenu_Heal_Target
    if broadcastName == BROADCAST_HEAL_ARMOR:
        return GetMenu_HealArmor
    if broadcastName == BROADCAST_HEAL_SHIELD:
        return GetMenu_HealShield
    if broadcastName == BROADCAST_HEAL_CAPACITOR:
        return GetMenu_HealCapacitor
    if broadcastName == BROADCAST_WARP_TO:
        return GetMenu_WarpTo
    if broadcastName == BROADCAST_NEED_BACKUP:
        return GetMenu_NeedBackup
    if broadcastName == BROADCAST_ALIGN_TO:
        return GetMenu_AlignTo
    if broadcastName == BROADCAST_JUMP_TO:
        return GetMenu_JumpTo
    if broadcastName == BROADCAST_TRAVEL_TO:
        return GetMenu_TravelTo
    if broadcastName == BROADCAST_IN_POSITION:
        return GetMenu_InPosition
    if broadcastName == BROADCAST_JUMP_BEACON:
        return GetMenu_JumpBeacon
    if broadcastName == BROADCAST_LOCATION:
        return GetMenu_Location


def _Rank(role):
    if not hasattr(_Rank, 'ranks'):
        _Rank.ranks = {evefleet.fleetRoleLeader: 4,
         evefleet.fleetRoleWingCmdr: 3,
         evefleet.fleetRoleSquadCmdr: 2,
         evefleet.fleetRoleMember: 1}
    return _Rank.ranks.get(role, -1)


def GetRankName(member):
    if member.job & evefleet.fleetJobCreator:
        if member.role == evefleet.fleetRoleLeader:
            return localization.GetByLabel('UI/Fleet/Ranks/FleetCommanderBoss')
        elif member.role == evefleet.fleetRoleWingCmdr:
            return localization.GetByLabel('UI/Fleet/Ranks/WingCommanderBoss')
        elif member.role == evefleet.fleetRoleSquadCmdr:
            return localization.GetByLabel('UI/Fleet/Ranks/SquadCommanderBoss')
        elif member.role == evefleet.fleetRoleMember:
            return localization.GetByLabel('UI/Fleet/Ranks/SquadMemberBoss')
        else:
            return localization.GetByLabel('UI/Fleet/Ranks/NonMember')
    else:
        return GetRoleName(member.role)


def GetRoleName(role):
    if role == evefleet.fleetRoleLeader:
        return localization.GetByLabel('UI/Fleet/Ranks/FleetCommander')
    elif role == evefleet.fleetRoleWingCmdr:
        return localization.GetByLabel('UI/Fleet/Ranks/WingCommander')
    elif role == evefleet.fleetRoleSquadCmdr:
        return localization.GetByLabel('UI/Fleet/Ranks/SquadCommander')
    elif role == evefleet.fleetRoleMember:
        return localization.GetByLabel('UI/Fleet/Ranks/SquadMember')
    else:
        return localization.GetByLabel('UI/Fleet/Ranks/NonMember')


def _ICareAbout(*args):

    def MySuperior(role, wingID, squadID):
        return _Rank(role) > _Rank(session.fleetrole) and wingID in (session.wingid, -1) and squadID in (session.squadid, -1)

    def SubordinateICareAbout(role, wingID, squadID):
        return role != evefleet.fleetRoleMember and _Rank(role) == _Rank(session.fleetrole) - 1 and session.wingid in (-1, wingID)

    return MySuperior(*args) or SubordinateICareAbout(*args)


inBubble = 1
inSystem = 2
exSystem = 3

def Where(charID, locationID = None):
    if SlimItemFromCharID(charID) is not None:
        return inBubble
    elif locationID in (None, session.solarsystemid):
        return inSystem
    else:
        return exSystem


def GetRoleIconFromCharID(charID):
    if charID is None:
        return
    info = sm.GetService('fleet').GetMemberInfo(int(charID))
    if info is None:
        return
    if info.job & evefleet.fleetJobCreator:
        iconRole = '73_20'
    else:
        iconRole = {evefleet.fleetRoleLeader: '73_17',
         evefleet.fleetRoleWingCmdr: '73_18',
         evefleet.fleetRoleSquadCmdr: '73_19'}.get(info.role, None)
    return iconRole


def GetBroadcastScopeName(scope, where = evefleet.BROADCAST_UNIVERSE):
    labelName = broadcastScopes.get(scope, {}).get(where, 'UI/Fleet/FleetBroadcast/BroadcastRangeAll')
    return localization.GetByLabel(labelName)


def GetBroadcastWhere(name):
    return broadcastRanges.get(name, defaultBroadcastRange)


def GetBroadcastWhereName(scope):
    return localization.GetByLabel(broadcastRangeNames[scope])


def GetBroadcastName(broadcastType):
    return localization.GetByLabel(broadcastNames[broadcastType])


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('fleetbr', locals())
