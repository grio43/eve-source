#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\location.py
import geo2
import evetypes
import eve.common.script.sys.eveCfg as eveCfg
from nodegraph.client.util import wait_for_session
from nodegraph.common.util import get_object_predicate
from .base import GetterAtom

class GetHomeStation(GetterAtom):
    atom_id = 184

    def get_values(self, **kwargs):
        import homestation.client
        return {'home_station_id': homestation.Service.instance().get_home_station().id}


class GetBirthStation(GetterAtom):
    atom_id = 185

    def get_values(self, **kwargs):
        import homestation.client
        return {'birth_station_id': homestation.Service.instance().get_school_hq_id()}


class GetDestination(GetterAtom):
    atom_id = 196

    def get_values(self, **kwargs):
        return {'destination_id': sm.GetService('starmap').GetDestination()}


class GetNextDestination(GetterAtom):
    atom_id = 197

    def get_values(self, **kwargs):
        return {'destination_id': sm.GetService('starmap').GetDestinationPath()[0]}


class GetDestinationPath(GetterAtom):
    atom_id = 451

    def get_values(self, **kwargs):
        return {'destination_path': sm.GetService('starmap').GetDestinationPath()}


class GetWaypointPath(GetterAtom):
    atom_id = 453

    def __init__(self, from_location_id = None, to_location_id = None):
        self.from_location_id = from_location_id
        self.to_location_id = to_location_id

    def get_values(self, **kwargs):
        if not self.to_location_id:
            return None
        return {'waypoint_path': sm.GetService('clientPathfinderService').GetWaypointPath([self.from_location_id or session.locationid, self.to_location_id])}


class FindNextInRoute(GetterAtom):
    atom_id = 222

    def get_values(self, **kwargs):
        return {'item_id': sm.GetService('autoPilot').GetDestinationItemID()}


class FindClosestLocationInSystem(GetterAtom):
    atom_id = 330

    def __init__(self, type_id = None, group_id = None, category_id = None):
        self.type_id = type_id
        self.group_id = group_id
        self.category_id = category_id

    def get_values(self, **kwargs):
        wait_for_session()
        if not eveCfg.InShipInSpace():
            return
        locations = cfg.GetLocationsLocalBySystem(solarSystemID=session.solarsystemid2, requireLocalizedTexts=False)
        ship = sm.GetService('michelle').GetBallpark().GetBall(session.shipid)
        ship_position = (ship.x, ship.y, ship.z)
        closest_location = None
        min_distance = float('inf')
        predicate = self._get_predicate()
        for location in locations:
            if not predicate(location):
                continue
            distance = geo2.Vec3Distance(ship_position, (location.x, location.y, location.z))
            if distance < min_distance:
                min_distance = distance
                closest_location = location

        if closest_location:
            return {'item_id': closest_location.itemID,
             'type_id': closest_location.typeID,
             'group_id': closest_location.groupID,
             'category_id': evetypes.GetCategoryID(closest_location.typeID)}

    def _get_predicate(self):
        if self.type_id:
            return get_object_predicate('typeID', self.type_id)
        if self.group_id:
            return get_object_predicate('groupID', self.group_id)
        if self.category_id:

            def predicate(location):
                return evetypes.GetCategoryID(location.typeID) == self.category_id

            return predicate

        def predicate(location):
            return True

        return predicate


class GetSolarSystem(GetterAtom):
    atom_id = 342

    def __init__(self, location_id = None):
        self.location_id = location_id

    def get_values(self, **kwargs):
        if self.location_id and self.location_id in cfg.evelocations:
            solar_system_id = cfg.evelocations[self.location_id].solarSystemID
        else:
            solar_system_id = session.solarsystemid2
        solar_system_info = sm.GetService('map').GetItem(solar_system_id)
        return {'solar_system_id': solar_system_id,
         'solar_system_info': solar_system_info}


class GetSystemSecurity(GetterAtom):
    atom_id = 343

    def __init__(self, solar_system_id = None):
        self.solar_system_id = solar_system_id

    def get_values(self, **kwargs):
        from eveuniverse.security import SecurityClassFromLevel
        security_level = sm.GetService('map').GetSecurityStatus(self.solar_system_id or session.solarsystemid2)
        security_class = SecurityClassFromLevel(security_level)
        return {'security_class': security_class,
         'security_level': security_level}


class GetStargateBetweenSystems(GetterAtom):
    atom_id = 470

    def __init__(self, from_solar_system_id = None, to_solar_system_id = None):
        self.from_solar_system_id = from_solar_system_id
        self.to_solar_system_id = to_solar_system_id

    def get_values(self, **kwargs):
        if not self.to_solar_system_id:
            return
        try:
            stargate_id = sm.GetService('autoPilot').GetGateIDToSolarsystemFromLocationID(self.to_solar_system_id, self.from_solar_system_id or session.solarsystemid2)
        except KeyError:
            stargate_id = None

        return {'stargate_id': stargate_id}


class GetAbyssalLocationInfo(GetterAtom):
    atom_id = 626

    def get_values(self, **kwargs):
        abyssalSvc = sm.GetService('abyss')
        return {'difficulty_tier': abyssalSvc.get_current_difficulty_tier(),
         'room_id': abyssalSvc.get_current_room_id()}


class GetDeathZoneInfo(GetterAtom):
    atom_id = 636

    def get_values(self, **kwargs):
        deathzoneService = sm.GetService('deathzoneSvc')
        return {'hull_damage_fraction': deathzoneService.GetHullDamageFraction()}


class GetInsurgencyInfo(GetterAtom):
    atom_id = 642

    def get_values(self, **kwargs):
        corruptionSuppresionSvc = sm.GetService('corruptionSuppressionSvc')
        return {'suppression_level': corruptionSuppresionSvc.GetCurrentSystemSuppressionStage(),
         'corruption_level': corruptionSuppresionSvc.GetCurrentSystemCorruptionStage()}
