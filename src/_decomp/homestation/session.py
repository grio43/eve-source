#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\session.py
import __builtin__

def is_logged_in():
    return get_global_session().charid is not None


def get_global_session():
    return __builtin__.session


def get_docked_id(session):
    station_id = getattr(session, 'stationid', None)
    structure_id = getattr(session, 'structureid', None)
    ship_id = getattr(session, 'shipid', None)
    if station_id is not None:
        return station_id
    if structure_id is not None and structure_id != ship_id:
        return structure_id
