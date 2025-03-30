#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\storylines\client\objectives\base\bookmark.py
from eve.common.script.sys.idCheckers import IsSolarSystem, IsStation
from inventorycommon.const import typeSolarSystem
from utillib import KeyVal

def create_bookmark(location_id):
    if IsStation(location_id):
        station = sm.GetService('map').GetStation(location_id)
        return KeyVal(bookmarkID=location_id, itemID=location_id, typeID=station.stationTypeID, locationID=station.solarSystemID, solarsystemID=station.solarSystemID, locationType='agenthomebase', x=0, y=0, z=0)
    elif IsSolarSystem(location_id):
        return KeyVal(bookmarkID=location_id, itemID=location_id, typeID=typeSolarSystem, locationID=location_id, solarsystemID=location_id, locationType='dungeon', x=0, y=0, z=0)
    else:
        return None
