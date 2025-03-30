#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\types.py


class StationData(object):

    def __init__(self, station_id, type_id, solar_system_id, is_fallback):
        self.id = station_id
        self.type_id = type_id
        self.solar_system_id = solar_system_id
        self.is_fallback = is_fallback

    def __repr__(self):
        return 'StationData(station_id={}, type_id={}, solar_system_id={}, is_fallback={})'.format(self.id, self.type_id, self.solar_system_id, self.is_fallback)


class StationCandidateData(object):

    def __init__(self, station_id, type_id, solar_system_id, is_current_station, is_school_hq, errors):
        self.id = station_id
        self.type_id = type_id
        self.solar_system_id = solar_system_id
        self.is_current_station = is_current_station
        self.is_school_hq = is_school_hq
        self.errors = errors
