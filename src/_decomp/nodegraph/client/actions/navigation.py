#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\navigation.py
from carbon.common.script.util.format import FmtDist
import eve.common.script.sys.eveCfg as eveCfg
import eve.client.script.ui.services.menuSvcExtras.movementFunctions as movement_functions
import eve.client.script.ui.services.menuSvcExtras.menuFunctions as menu_functions
from eve.client.script.ui.util.defaultRangeUtils import ORBIT_SETTING, UpdateRangeSettingForShipType
from evetypes import GetName
from inventorycommon.const import flagHangar, containerHangar
from nodegraph.client.util import get_location_name, wait_for_session
from .base import Action

class ApproachTarget(Action):
    atom_id = 123

    def __init__(self, item_id = None, **kwargs):
        super(ApproachTarget, self).__init__(**kwargs)
        self.item_id = item_id

    def start(self, **kwargs):
        super(ApproachTarget, self).start(**kwargs)
        if self.item_id:
            movement_functions.Approach(targetID=self.item_id)


class BoardShip(Action):
    atom_id = 316

    def __init__(self, item_id = None, **kwargs):
        super(BoardShip, self).__init__(**kwargs)
        self.item_id = item_id

    def start(self, **kwargs):
        super(BoardShip, self).start(**kwargs)
        if not self.item_id:
            return
        wait_for_session()
        if eveCfg.InSpace():
            menu_functions.Board(self.item_id)
        else:
            hangar_inventory = sm.GetService('invCache').GetInventory(containerHangar)
            items = hangar_inventory.List(flagHangar)
            for item in items:
                if item.itemID == self.item_id:
                    if not bool(item.singleton):
                        ship = sm.GetService('gameui').GetShipAccess()
                        ship.AssembleShip(item.itemID)
                    sm.GetService('station').TryActivateShip(item)
                    break


class LeaveShip(Action):
    atom_id = 317

    def start(self, **kwargs):
        super(LeaveShip, self).start(**kwargs)
        wait_for_session()
        if not eveCfg.InShip():
            return
        if eveCfg.InSpace():
            menu_functions.Eject(suppressConfirmation=True)
        elif eveCfg.IsDockedInStructure():
            sm.GetService('structureDocking').LeaveShip(session.shipid)
        else:
            ship = sm.GetService('godma').GetItem(session.shipid)
            if ship:
                sm.GetService('station').TryLeaveShip(ship)


class Dock(Action):
    atom_id = 193

    def __init__(self, item_id = None, **kwargs):
        super(Dock, self).__init__(**kwargs)
        self.item_id = item_id

    def start(self, **kwargs):
        super(Dock, self).start(**kwargs)
        if self.item_id:
            wait_for_session()
            sm.GetService('menu').Dock(self.item_id)


class Undock(Action):
    atom_id = 315

    def start(self, **kwargs):
        super(Undock, self).start(**kwargs)
        wait_for_session()
        sm.GetService('undocking').ExitDockableLocation()


class JumpDockActivate(Action):
    atom_id = 194

    def __init__(self, item_id = None, **kwargs):
        super(JumpDockActivate, self).__init__(**kwargs)
        self.item_id = item_id

    def start(self, **kwargs):
        super(JumpDockActivate, self).start(**kwargs)
        if self.item_id:
            wait_for_session()
            movement_functions.DockOrJumpOrActivateGate(self.item_id)


class KeepTargetAtRange(Action):
    atom_id = 124

    def __init__(self, item_id = None, distance = None, **kwargs):
        super(KeepTargetAtRange, self).__init__(**kwargs)
        self.item_id = item_id
        self.distance = distance

    def start(self, **kwargs):
        super(KeepTargetAtRange, self).start(**kwargs)
        if self.item_id:
            movement_functions.KeepAtRange(targetID=self.item_id, followRange=self.distance)

    @classmethod
    def get_subtitle(cls, distance = None, **kwargs):
        if distance:
            return 'Distance: {}'.format(FmtDist(distance))
        return 'Distance: player settings'


class OrbitTarget(Action):
    atom_id = 125

    def __init__(self, item_id = None, distance = None, **kwargs):
        super(OrbitTarget, self).__init__(**kwargs)
        self.item_id = item_id
        self.distance = distance

    def start(self, **kwargs):
        super(OrbitTarget, self).start(**kwargs)
        if self.item_id:
            movement_functions.Orbit(targetID=self.item_id, followRange=self.distance)

    @classmethod
    def get_subtitle(cls, distance = None, **kwargs):
        if distance:
            return 'Distance: {}'.format(FmtDist(distance))
        return 'Distance: player settings'


class SetDestination(Action):
    atom_id = 195

    def __init__(self, destination_id = None, clear_waypoints = None, **kwargs):
        super(SetDestination, self).__init__(**kwargs)
        self.destination_id = destination_id
        self.clear_waypoints = self.get_atom_parameter_value('clear_waypoints', clear_waypoints)

    def start(self, **kwargs):
        super(SetDestination, self).start(**kwargs)
        if self.destination_id:
            sm.GetService('starmap').SetWaypoint(self.destination_id, clearOtherWaypoints=self.clear_waypoints)

    @classmethod
    def get_subtitle(cls, destination_id = None, clear_waypoints = None, **kwargs):
        return u'{} {}'.format(get_location_name(destination_id), '- Clear waypoints' if cls.get_atom_parameter_value('clear_waypoints', clear_waypoints) else '')


class WarpTo(Action):
    atom_id = 192

    def __init__(self, item_id = None, warp_range = None, cancel_autopilot = None, **kwargs):
        super(WarpTo, self).__init__(**kwargs)
        self.item_id = item_id
        self.warp_range = self.get_atom_parameter_value('warp_range', warp_range)
        self.cancel_autopilot = self.get_atom_parameter_value('cancel_autopilot', cancel_autopilot)

    def start(self, **kwargs):
        super(WarpTo, self).start(**kwargs)
        if self.item_id:
            movement_functions.WarpToItem(self.item_id, warpRange=self.warp_range, cancelAutoNavigation=self.cancel_autopilot)

    @classmethod
    def get_subtitle(cls, warp_range = None, **kwargs):
        if warp_range:
            return 'WarpRange: {}'.format(FmtDist(warp_range))
        return 'WarpRange: player settings'


class StopShip(Action):
    atom_id = 126

    def start(self, **kwargs):
        super(StopShip, self).start(**kwargs)
        sm.GetService('cmd').CmdStopShip()


class SetDefaultOrbitDistance(Action):
    atom_id = 231

    def __init__(self, type_id = None, default_orbit_distance = None, **kwargs):
        super(SetDefaultOrbitDistance, self).__init__(**kwargs)
        self.type_id = type_id
        self.default_orbit_distance = default_orbit_distance

    def start(self, **kwargs):
        super(SetDefaultOrbitDistance, self).start(**kwargs)
        UpdateRangeSettingForShipType(typeID=self.type_id, key=ORBIT_SETTING, newRange=self.default_orbit_distance)

    @classmethod
    def get_subtitle(cls, type_id = None, default_orbit_distance = None, **kwargs):
        if type_id:
            return 'Distance {distance} - {type_name} ({type_id})'.format(distance=FmtDist(default_orbit_distance), type_name=GetName(type_id), type_id=type_id)
        return 'Distance {distance}'.format(distance=FmtDist(default_orbit_distance))
