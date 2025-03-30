#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\station.py
import evelink.client
from homestation.client import text

class StationMixin(object):

    @property
    def name(self):
        return text.station_name(self.id)

    @property
    def trace(self):
        return text.solar_system_trace(self.solar_system_id)

    @property
    def link(self):
        return evelink.type_link(type_id=self.type_id, item_id=self.id, link_text=self.name)


class Station(StationMixin):

    def __init__(self, station_id, type_id, solar_system_id, is_fallback):
        self.id = station_id
        self.type_id = type_id
        self.solar_system_id = solar_system_id
        self.is_fallback = is_fallback
