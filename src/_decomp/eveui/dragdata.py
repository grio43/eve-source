#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\dragdata.py
from carbon.common.script.util.commonutils import StripTags
from carbonui.util.bunch import Bunch
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
import evetypes
import localization
import caching

class Item(object):

    def __init__(self, item_id, type_id):
        self.__guid__ = 'listentry.Item'
        self.itemID = item_id
        self.typeID = type_id
        self.label = _get_type_name_raw(type_id)


class ItemType(object):

    def __init__(self, type_id):
        self.__guid__ = 'uicls.GenericDraggableForTypeID'
        self.typeID = type_id
        self.label = _get_type_name_raw(type_id)


class SolarSystem(object):

    def __init__(self, solar_system_id):
        self.__guid__ = 'listentry.LocationTextEntry'
        self.typeID = appConst.typeSolarSystem
        self.itemID = solar_system_id
        self.label = _get_solar_system_name_raw(solar_system_id)


class Location(object):

    def __init__(self, location_id):
        self.__guid__ = 'listentry.LocationTextEntry'
        self.typeID = _get_location_type_id(location_id)
        self.itemID = location_id

    @caching.lazy_property
    def label(self):
        return _get_location_name_raw(self.itemID)


class Character(object):

    def __init__(self, character_id):
        character_info = cfg.eveowners.Get(character_id)
        self.__guid__ = 'listentry.User'
        self.typeID = character_info.typeID
        self.itemID = character_id
        self.charID = character_id
        self.info = Bunch(typeID=character_info.typeID, name=cfg.eveowners.Get(character_id).name)


def _get_type_name_raw(type_id):
    return evetypes.GetName(type_id, important=False)


def _get_solar_system_name_raw(solar_system_id):
    solar_system = cfg.mapSystemCache.Get(solar_system_id)
    return localization.GetByMessageID(solar_system.nameID, important=False)


def _get_location_name_raw(location_id):
    location = cfg.evelocations.Get(location_id)
    if location.locationNameID:
        return localization.GetByMessageID(location.locationNameID, important=False)
    return StripTags(location.locationName)


def _get_location_type_id(location_id):
    if idCheckers.IsSolarSystem(location_id):
        return appConst.typeSolarSystem
    if idCheckers.IsStation(location_id):
        station = cfg.stations.Get(location_id)
        return station.stationTypeID
    if idCheckers.IsConstellation(location_id):
        return appConst.typeConstellation
    if idCheckers.IsRegion(location_id):
        return appConst.typeRegion
