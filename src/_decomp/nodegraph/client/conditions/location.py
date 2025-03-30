#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\location.py
import evetypes
import eve.common.script.sys.eveCfg as eveCfg
from eve.common.script.sys.idCheckers import IsAbyssalSpaceSystem, IsTriglavianSystem, IsZarzakh
from nodegraph.client.util import get_location_name
from .base import Condition

class AtLocation(Condition):
    atom_id = 24

    def __init__(self, location_id = None, **kwargs):
        super(AtLocation, self).__init__(**kwargs)
        self.location_id = location_id

    def validate(self, **kwargs):
        return self.location_id == session.locationid

    @classmethod
    def get_subtitle(cls, location_id = None, **kwargs):
        return get_location_name(location_id)


class InDungeon(Condition):
    atom_id = 146

    def __init__(self, dungeon_id = None, **kwargs):
        super(InDungeon, self).__init__(**kwargs)
        self.dungeon_id = dungeon_id

    def validate(self, **kwargs):
        current_dungeon_id = sm.GetService('dungeonTracking').GetCurrentDungeonID()
        if not self.dungeon_id:
            return bool(current_dungeon_id)
        else:
            return current_dungeon_id == self.dungeon_id

    @classmethod
    def get_subtitle(cls, dungeon_id = None, **kwargs):
        return dungeon_id


class InRegion(Condition):
    atom_id = 25

    def __init__(self, region_id = None, **kwargs):
        super(InRegion, self).__init__(**kwargs)
        self.region_id = region_id

    def validate(self, **kwargs):
        return self.region_id == session.regionid

    @classmethod
    def get_subtitle(cls, region_id = None, **kwargs):
        return get_location_name(region_id)


class InConstellation(Condition):
    atom_id = 26

    def __init__(self, contellation_id = None, **kwargs):
        super(InConstellation, self).__init__(**kwargs)
        self.contellation_id = contellation_id

    def validate(self, **kwargs):
        return self.contellation_id == session.constellationid

    @classmethod
    def get_subtitle(cls, contellation_id = None, **kwargs):
        return get_location_name(contellation_id)


class InSolarSystem(Condition):
    atom_id = 27

    def __init__(self, solar_system_id = None, **kwargs):
        super(InSolarSystem, self).__init__(**kwargs)
        self.solar_system_id = solar_system_id

    def validate(self, **kwargs):
        return self.solar_system_id == session.solarsystemid2

    @classmethod
    def get_subtitle(cls, solar_system_id = None, **kwargs):
        return get_location_name(solar_system_id)


class InSpace(Condition):
    atom_id = 28

    def __init__(self, solar_system_id = None, **kwargs):
        super(InSpace, self).__init__(**kwargs)
        self.solar_system_id = solar_system_id

    def validate(self, **kwargs):
        if not eveCfg.InSpace():
            return False
        if self.solar_system_id and self.solar_system_id != session.solarsystemid2:
            return False
        return True

    @classmethod
    def get_subtitle(cls, solar_system_id = None, **kwargs):
        return get_location_name(solar_system_id)


class InStation(Condition):
    atom_id = 29

    def __init__(self, station_id = None, station_type_id = None, **kwargs):
        super(InStation, self).__init__(**kwargs)
        self.station_id = station_id
        self.station_type_id = station_type_id

    def validate(self, **kwargs):
        if not bool(session.stationid):
            return False
        if self.station_id:
            return self.station_id == session.stationid
        if self.station_type_id:
            station = cfg.stations.Get(session.stationid)
            return self.station_type_id == station.stationTypeID
        return True

    @classmethod
    def get_subtitle(cls, station_id = None, station_type_id = None, **kwargs):
        if station_id:
            return get_location_name(station_id)
        if station_type_id:
            return evetypes.GetName(station_type_id)
        return ''


class InCareerAgentSystem(Condition):
    atom_id = 221

    def validate(self, **kwargs):
        current_solar_system_id = session.solarsystemid2
        return sm.GetService('agents').IsCareerAgentSystem(current_solar_system_id)


class InCareerAgentStation(Condition):
    atom_id = 258

    def validate(self, **kwargs):
        current_station_id = session.stationid
        return sm.GetService('agents').IsCareerAgentStation(current_station_id)


class InTriglavianSystem(Condition):
    atom_id = 623

    def validate(self, **kwargs):
        current_solar_system_id = session.solarsystemid2
        return IsTriglavianSystem(current_solar_system_id)


class InAbyssalDeadspace(Condition):
    atom_id = 625

    def validate(self, **kwargs):
        current_solar_system_id = session.solarsystemid2
        return IsAbyssalSpaceSystem(current_solar_system_id)


class InAbyssalTier(Condition):
    atom_id = 627

    def __init__(self, abyssal_tier = None, **kwargs):
        super(InAbyssalTier, self).__init__(**kwargs)
        self.abyssal_tier = self.get_atom_parameter_value('abyssal_tier', abyssal_tier)

    def validate(self, **kwargs):
        return self.abyssal_tier == sm.GetService('abyss').get_current_difficulty_tier()

    @classmethod
    def get_subtitle(cls, abyssal_tier = None, **kwargs):
        abyssal_tier = cls.get_atom_parameter_value('abyssal_tier', abyssal_tier)
        if abyssal_tier is not None:
            return str(abyssal_tier)
        else:
            return 'No tier defined'


class InAbyssalRoom(Condition):
    atom_id = 628

    def __init__(self, abyssal_room = 0, **kwargs):
        super(InAbyssalRoom, self).__init__(**kwargs)
        self.abyssal_room = abyssal_room

    def validate(self, **kwargs):
        return self.abyssal_room == sm.GetService('abyss').get_current_room_id()

    @classmethod
    def get_subtitle(cls, abyssal_room = None, **kwargs):
        if abyssal_room:
            return abyssal_room
        else:
            return 'No room defined'


class InZarzakh(Condition):
    atom_id = 633

    def validate(self, **kwargs):
        current_solar_system_id = session.solarsystemid2
        return IsZarzakh(current_solar_system_id)


class InDeathZone(Condition):
    atom_id = 635

    def validate(self, **kwargs):
        return sm.GetService('deathzoneSvc').InDeathZone()


class InInsurgencySystem(Condition):
    atom_id = 637

    def validate(self, **kwargs):
        return sm.GetService('insurgencyDashboardSvc').IsSystemAffectedByInsurgency(session.solarsystemid2)
