#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\tacticalNavigation\tacticalNavigationService.py
from carbon.common.script.sys.service import Service
import caching
from eve.common.lib.appConst import approachRange
from eve.common.script.sys.eveCfg import InSpace
import evetypes
import eveicon
import localization
from tacticalNavigation.actionDisplay import ActionDisplay
from tacticalNavigation.const import NAVIGATION_MODES_BY_STATE
from tacticalNavigation.ui.navigationPoint import NavigationPointContainer
from tacticalNavigation.ui.pendingMove import PendingMoveIndication

class TravelState(object):
    label_map = {'warping': 'UI/Inflight/Warping',
     'jumping': 'UI/Inflight/Messages/Jumping',
     'docking': 'UI/Inflight/Messages/Docking',
     'undocking': 'UI/Station/Undocking'}
    icon_map = {'warping': eveicon.warp_to,
     'jumping': eveicon.jump_to,
     'docking': eveicon.dock,
     'undocking': None}

    def __init__(self):
        self._action = None
        self._target = None

    @property
    def action(self):
        return self._action

    @property
    def target(self):
        return self._target

    def get_label(self):
        if self._action:
            return localization.GetByLabel(self.label_map[self._action])
        else:
            return ''

    def get_icon(self):
        if self._action:
            return self.icon_map.get(self._action, None)
        else:
            return None

    def is_traveling(self):
        return bool(self._action)

    def is_jumping(self):
        return self._action == 'jumping'

    def is_jumping_to(self, solar_system_id):
        if not self.is_jumping():
            return False
        return self._target.get('destination_id') == solar_system_id

    def is_jumping_through(self, gate_id):
        if not self.is_jumping():
            return False
        return self._target.get('gate_id') == gate_id

    def is_warping(self):
        return self._action == 'warping'

    def is_warping_to(self, item_id = None, type_id = None, group_id = None, category_id = None):
        if not self.is_warping():
            return False
        if item_id:
            return self._target.get('item_id') == item_id
        return self._check_target_type(self._target.get('type_id'), type_id, group_id, category_id)

    def is_docking(self):
        return self._action == 'docking'

    def is_docking_at(self, item_id = None, type_id = None, group_id = None, category_id = None):
        if not self.is_docking():
            return False
        if item_id:
            return self._target.get('location_id') == item_id
        location = sm.GetService('map').GetItem(self._target.get('location_id'))
        if not location:
            return True
        return self._check_target_type(location.typeID, type_id, group_id, category_id)

    def is_undocking(self, location_id = None, solar_system_id = None):
        return self._action == 'undocking'

    def is_undocking_from(self, item_id = None, type_id = None, group_id = None, category_id = None):
        if not self.is_undocking():
            return False
        if item_id:
            return self._target.get('location_id') == item_id
        location = sm.GetService('map').GetItem(self._target.get('location_id'))
        if not location:
            return True
        return self._check_target_type(location.typeID, type_id, group_id, category_id)

    def is_undocking_in_system(self, solar_system_id):
        if not self.is_undocking():
            return False
        return solar_system_id == session.solarsystemid2

    def set_jumping(self, gate_id, destination_id):
        self._action = 'jumping'
        self._target = {'gate_id': gate_id,
         'destination_id': destination_id}
        self._notify_state_changed()

    def clear_jumping(self):
        self._clear('jumping')

    def set_warping(self, item_id, type_id):
        self._action = 'warping'
        self._target = {'item_id': item_id,
         'type_id': type_id}
        self._notify_state_changed()

    def clear_warping(self):
        self._clear('warping')

    def set_docking(self, location_id):
        self._action = 'docking'
        self._target = {'location_id': location_id}
        self._notify_state_changed()

    def clear_docking(self):
        self._clear('docking')

    def set_undocking(self):
        self._action = 'undocking'
        self._target = {'location_id': session.locationid}
        self._notify_state_changed()

    def clear_undocking(self):
        self._clear('undocking')

    def _check_target_type(self, target_type_id, type_id = None, group_id = None, category_id = None):
        if not target_type_id:
            return True
        if type_id:
            return target_type_id == type_id
        if group_id:
            target_group_id = evetypes.GetGroupID(target_type_id)
            return target_group_id == group_id
        if category_id:
            target_category_id = evetypes.GetCategoryID(target_type_id)
            return target_category_id == category_id
        return True

    def _clear(self, action = None):
        if not action or action == self._action:
            self._action = None
            self._target = None
            self._notify_state_changed()

    def _notify_state_changed(self):
        sm.ScatterEvent('OnTravelStateChanged', self._action, self._target)


class TacticalNavigationService(Service):
    __guid__ = 'svc.tacticalNavigation'
    __servicename__ = 'tacticalNavigationService'
    __displayname__ = 'Tactical Navigation Service'
    __startupdependencies__ = ['michelle', 'fighters']
    __notifyevents__ = ['OnFighterAddedToController',
     'OnFighterRemovedFromController',
     'OnSessionChanged',
     'DoBallRemove',
     'DoBallsRemove',
     'OnWarpStarted',
     'OnWarpFinished',
     'OnJumpStarted',
     'OnJumpExecuted',
     'OnJumpFinished',
     'OnDockingAccepted',
     'OnDockingFinished',
     'OnUndockingStarted',
     'OnUndockingCompleted',
     'OnUndockingAborted',
     'OnBallparkCall']

    def __init__(self):
        super(TacticalNavigationService, self).__init__()
        self._navPointContainer = None
        self._actionDisplay = None
        self._pendingMoveCommands = {}
        self.actionDisplayEnabled = False
        self.travel_state = TravelState()

    def Run(self, *args):
        super(TacticalNavigationService, self).Run(*args)
        self._InitializeWarpingData()

    @caching.lazy_property
    def menu_service(self):
        return sm.GetService('menu')

    @caching.lazy_property
    def space_service(self):
        return sm.GetService('space')

    def GetNavigationTargetID(self):
        ball = self._GetShipBall()
        if ball:
            return ball.followId

    def IsTraveling(self):
        return self.travel_state.is_traveling()

    def IsDocking(self):
        return self.travel_state.is_docking()

    def IsDockingAt(self, item_id = None, type_id = None, group_id = None, category_id = None):
        return self.travel_state.is_docking_at(item_id=item_id, type_id=type_id, group_id=group_id, category_id=category_id)

    def IsUndocking(self):
        return self.travel_state.is_undocking()

    def IsUndockingFrom(self, item_id = None, type_id = None, group_id = None, category_id = None):
        return self.travel_state.is_undocking_from(item_id=item_id, type_id=type_id, group_id=group_id, category_id=category_id)

    def IsUndockingInSystem(self, solar_system_id):
        return self.travel_state.is_undocking_in_system(solar_system_id)

    def IsJumping(self):
        return self.travel_state.is_jumping()

    def IsJumpingThrough(self, gate_id):
        return self.travel_state.is_jumping_through(gate_id)

    def IsJumpingTo(self, solar_system_id):
        return self.travel_state.is_jumping_to(solar_system_id)

    def IsWarping(self):
        return self.travel_state.is_warping()

    def IsWarpingTo(self, item_id = None, type_id = None, group_id = None, category_id = None):
        return self.travel_state.is_warping_to(item_id=item_id, type_id=type_id, group_id=group_id, category_id=category_id)

    def IsApproaching(self):
        return self._IsInShipBall() and self._IsShipInNavigationModeForState('Approach') and self._IsShipSetToFollowRange(self._GetApproachRange())

    def IsApproachingTarget(self, item_id = None, type_id = None, group_id = None, category_id = None, owner_id = None, dungeon_object_id = None):
        return self.IsApproaching() and self._IsShipNavigatingTowards(item_id, type_id, group_id, category_id, owner_id, dungeon_object_id)

    def IsKeepingAtRange(self):
        return self._IsInShipBall() and self._IsShipInNavigationModeForState('KeepAtRange') and not self._IsShipSetToFollowRange(self._GetApproachRange())

    def IsKeepingTargetAtRange(self, item_id = None, type_id = None, group_id = None, category_id = None, owner_id = None, dungeon_object_id = None):
        return self.IsKeepingAtRange() and self._IsShipNavigatingTowards(item_id, type_id, group_id, category_id, owner_id, dungeon_object_id)

    def IsOrbiting(self):
        return self._IsInShipBall() and self._IsShipInNavigationModeForState('Orbit')

    def IsOrbitingTarget(self, item_id = None, type_id = None, group_id = None, category_id = None, owner_id = None, dungeon_object_id = None):
        return self.IsOrbiting() and self._IsShipNavigatingTowards(item_id, type_id, group_id, category_id, owner_id, dungeon_object_id)

    def IsMovingTowards(self):
        return self._IsInShipBall() and self._IsShipInNavigationModeForState('MoveTowards')

    def IsMovingTowardsTarget(self, item_id = None, type_id = None, group_id = None, category_id = None, owner_id = None, dungeon_object_id = None):
        return self.IsMovingTowards() and self._IsShipNavigatingTowards(item_id, type_id, group_id, category_id, owner_id, dungeon_object_id)

    def IsMovingTowardsPoint(self):
        return self._IsInShipBall() and self._IsShipInNavigationModeForState('MoveTowardsPoint')

    def IsAligning(self):
        return self._IsInShipBall() and self._IsShipInNavigationModeForState('Align') and self.GetAlignTarget() is not None

    def IsAligningTo(self, itemID):
        self.IsAligning() and self.GetAlignTarget() == itemID

    def GetAlignTarget(self):
        from eveservices.menu import GetMenuService
        target_id, bookmark_id = GetMenuService().GetLastAlignTarget()
        return target_id or bookmark_id

    def IsStopped(self):
        return self._IsInShipBall() and self._IsShipInNavigationModeForState('Stop')

    def IsMoving(self):
        if self.IsMovingTowards() or self.IsMovingTowardsPoint():
            return True
        return False

    @property
    def navPointContainer(self):
        if self._navPointContainer is None:
            self._navPointContainer = NavigationPointContainer(self._ClearPendingMove)
        return self._navPointContainer

    @property
    def actionDisplay(self):
        if self._actionDisplay is None:
            self._actionDisplay = ActionDisplay(self.navPointContainer)
        return self._actionDisplay

    def SetMaxMoveRange(self, range):
        self.actionDisplay.SetMaxMoveRange(range)

    def EnableActionDisplay(self, enable):
        if enable == self.actionDisplayEnabled:
            return
        self.actionDisplayEnabled = enable
        self.actionDisplay.Enable(enable)
        if enable:
            self._ReloadFighters()
        else:
            for key in self._pendingMoveCommands.keys():
                self._ClearPendingMove(key)

    def _ReloadFighters(self):
        if not self.actionDisplayEnabled:
            return
        if not (session.shipid and session.solarsystemid2):
            return
        _, fighters, _ = self.fighters.GetFightersForShip()
        for fighter in fighters:
            _, fighterID, _, _ = fighter
            self.actionDisplay.AddFighter(fighterID)

    def _ClearPendingMove(self, ballID, forGlobalPosition = None):
        if ballID in self._pendingMoveCommands:
            pendingMove = self._pendingMoveCommands[ballID]
            if forGlobalPosition is None or pendingMove.globalPosition == forGlobalPosition:
                del self._pendingMoveCommands[ballID]
                pendingMove.Destroy()

    def IndicateMoveCommand(self, IDs, destination):
        if not self.actionDisplayEnabled:
            return
        for ballID in IDs:
            self._ClearPendingMove(ballID)
            pendingCommand = PendingMoveIndication(ballID, destination, self.navPointContainer, self._ClearPendingMove)
            pendingCommand.Show()
            self._pendingMoveCommands[ballID] = pendingCommand

    def OnSessionChanged(self, isremote, session, change):
        if 'shipid' not in change:
            return
        self._ReloadFighters()

    def OnFighterAddedToController(self, fighterID, fighterTypeID, tubeFlagID, squadronSize, abilitySlotStates):
        if self.actionDisplayEnabled:
            self.actionDisplay.AddFighter(fighterID)

    def OnFighterRemovedFromController(self, fighterID, tubeFlagID):
        if self.actionDisplayEnabled:
            self.actionDisplay.RemoveFighter(fighterID)

    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        self.actionDisplay.RemoveBall(ball.id)

    def _GetShipBall(self):
        if not InSpace():
            return None
        return sm.GetService('michelle').GetBall(session.shipid)

    def _IsInShipBall(self):
        return self._GetShipBall() is not None

    def _GetNavigationModes(self, state):
        return NAVIGATION_MODES_BY_STATE.get(state, None)

    def _IsShipInNavigationModeForState(self, state):
        navigation_modes = self._GetNavigationModes(state)
        return self._IsShipInAnyNavigationMode(navigation_modes)

    def _IsShipInAnyNavigationMode(self, navigation_modes):
        if not navigation_modes:
            return True
        ball = self._GetShipBall()
        if not ball or ball.mode not in navigation_modes:
            return False
        return True

    def _GetApproachRange(self):
        return approachRange

    def _IsShipNavigatingTowards(self, item_id = None, type_id = None, group_id = None, category_id = None, owner_id = None, dungeon_object_id = None):
        target_id = self.GetNavigationTargetID()
        if not target_id:
            return False
        if item_id:
            return item_id == target_id
        target = sm.GetService('michelle').GetItem(target_id)
        if not target:
            return False
        if dungeon_object_id:
            return dungeon_object_id == target.dunObjectID
        if type_id and type_id != target.typeID:
            return False
        if group_id and group_id != target.groupID:
            return False
        if category_id and category_id != target.categoryID:
            return False
        if owner_id and owner_id != target.ownerID:
            return False
        return True

    def _IsShipSetToFollowRange(self, range):
        ball = self._GetShipBall()
        return ball.followRange == range

    def _InitializeWarpingData(self):
        if self._GetShipBall() is None:
            return
        if self.space_service.IsWarping():
            itemID, typeID = self.space_service.GetWarpDestinationItemIDAndTypeID()
            self.travel_state.set_warping(itemID, typeID)

    def IsDestinationSetToCareerAgentStation(self):
        destinationID = sm.GetService('starmap').GetDestination()
        return sm.GetService('agents').IsCareerAgentStation(destinationID)

    def IsBallparkLoaded(self):
        return sm.GetService('jumpMonitor').IsBallparkLoaded()

    def OnJumpStarted(self, gateID, destinationID):
        self.travel_state.set_jumping(gateID, destinationID)
        sm.ScatterEvent('OnClientEvent_JumpStarted', gateID, destinationID)

    def OnJumpExecuted(self, itemID):
        sm.ScatterEvent('OnClientEvent_JumpExecuted', itemID)

    def OnJumpFinished(self, gateID, originID):
        self.travel_state.clear_jumping()
        sm.ScatterEvent('OnClientEvent_JumpFinished', gateID, originID)

    def OnWarpStarted(self, itemID, typeID):
        self.travel_state.set_warping(itemID, typeID)
        sm.ScatterEvent('OnClientEvent_WarpStarted', itemID, typeID)

    def OnWarpFinished(self, itemID, typeID):
        self.travel_state.clear_warping()
        sm.ScatterEvent('OnClientEvent_WarpFinished', itemID, typeID)

    def OnDockingAccepted(self, locationID):
        self.travel_state.set_docking(locationID)
        sm.ScatterEvent('OnClientEvent_DockingStarted', locationID)

    def OnDockingFinished(self, itemID):
        self.travel_state.clear_docking()
        sm.ScatterEvent('OnClientEvent_DockingFinished', itemID)

    def OnUndockingStarted(self, itemID):
        self.travel_state.set_undocking()
        sm.ScatterEvent('OnClientEvent_UndockingStarted', itemID)

    def OnUndockingCompleted(self, itemID):
        self.travel_state.clear_undocking()
        sm.ScatterEvent('OnClientEvent_UndockingFinished', itemID)

    def OnUndockingAborted(self, itemID):
        self.travel_state.clear_undocking()
        sm.ScatterEvent('OnClientEvent_UndockingAborted', itemID)

    def NotifyOfApproachCommand(self, slimItem = None):
        itemID = slimItem.itemID if slimItem else None
        sm.ScatterEvent('OnClientEvent_ApproachCommand', slimItem)
        sm.ScatterEvent('OnClientEvent_MoveTowardsCommand', itemID)

    def NotifyOfKeepAtRangeCommand(self, targetID, distance):
        sm.ScatterEvent('OnClientEvent_KeepAtRangeCommand', targetID, distance)
        sm.ScatterEvent('OnClientEvent_MoveTowardsCommand', targetID)

    def NotifyOfOrbitCommand(self, targetID, distance, slimItem):
        sm.ScatterEvent('OnClientEvent_OrbitCommand', targetID, distance, slimItem)
        sm.ScatterEvent('OnClientEvent_MoveTowardsCommand', targetID)

    def NotifyOfAlignCommand(self, targetID):
        sm.ScatterEvent('OnClientEvent_AlignCommand', targetID)

    def NotifyOfMoveTowardsPointCommand(self, direction):
        sm.ScatterEvent('OnClientEvent_MoveTowardsPointCommand', direction)

    def OnBallparkCall(self, event, eventArguments):
        if eventArguments[0] != session.shipid:
            return
        if event not in ('FollowBall', 'Orbit', 'Stop', 'GotoPoint', 'GotoDirection'):
            return
        targetID = eventArguments[1] if len(eventArguments) > 1 else None
        distance = eventArguments[2] if len(eventArguments) > 2 else None
        if event == 'FollowBall':
            if distance == self._GetApproachRange():
                sm.ScatterEvent('OnClientEvent_ApproachExecuted', targetID)
            else:
                sm.ScatterEvent('OnClientEvent_KeepAtRangeExecuted', targetID, distance)
        elif event == 'Orbit':
            sm.ScatterEvent('OnClientEvent_OrbitExecuted', targetID, distance)
        elif event == 'GotoPoint':
            alignTargetID, bookmarkID = self.menu_service.GetLastAlignTarget()
            alignTargetID = alignTargetID or bookmarkID
            if alignTargetID:
                sm.ScatterEvent('OnClientEvent_AlignExecuted', alignTargetID)
        elif event == 'Stop':
            sm.ScatterEvent('OnClientEvent_StopExecuted')
        if event in ('FollowBall', 'Orbit'):
            sm.ScatterEvent('OnClientEvent_MoveTowardsExecuted', targetID, distance)
        if event in ('GotoPoint', 'GotoDirection'):
            sm.ScatterEvent('OnClientEvent_MoveTowardsPointExecuted')
