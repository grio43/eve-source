#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\action.py
from homestation.client.error import handle_change_home_station_validation_error
from homestation.client.prompt import prompt_set_home_station_remotely
from homestation.client.service import Service
from homestation.client.validation import is_remote
from homestation.validation import ChangeHomeStationValidationError

def set_home_station(station_id):
    allow_remote = False
    if is_remote(station_id):
        allow_remote = prompt_set_home_station_remotely()
        if not allow_remote:
            return
    try:
        Service.instance().set_home_station(station_id, allow_remote)
    except ChangeHomeStationValidationError as error:
        handle_change_home_station_validation_error(error)


def get_home_station():
    return Service.instance().get_home_station().id


def get_home_station_solar_system():
    return Service.instance().get_home_station().solar_system_id
