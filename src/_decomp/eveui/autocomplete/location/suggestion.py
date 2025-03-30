#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\location\suggestion.py
import localization
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from carbon.common.script.util.commonutils import StripTags
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.shared.maps.solarSystemMapIcon import SolarSystemMapIcon, ConstellationMapIcon, RegionMapIcon
import eveformat.client
import eveicon
from eveui import dragdata
from eveui.primitive.sprite import Sprite
from eveui.autocomplete.suggestion import Suggestion
from carbonui import TextColor

class LocationSuggestion(Suggestion):
    __slots__ = ('location_id',)
    key_attributes = __slots__

    def __init__(self, location_id):
        self.location_id = location_id

    @property
    def type_id(self):
        if self.is_solar_system:
            return appConst.typeSolarSystem
        if self.is_constellation:
            return appConst.typeConstellation
        if self.is_region:
            return appConst.typeRegion
        if self.is_station:
            station = cfg.stations.Get(self.location_id)
            return station.stationTypeID

    @property
    def is_region(self):
        return idCheckers.IsRegion(self.location_id)

    @property
    def is_constellation(self):
        return idCheckers.IsConstellation(self.location_id)

    @property
    def is_solar_system(self):
        return idCheckers.IsSolarSystem(self.location_id)

    @property
    def is_station(self):
        return idCheckers.IsStation(self.location_id)

    @property
    def text(self):
        location = cfg.evelocations.Get(self.location_id)
        if location.locationNameID:
            return localization.GetByMessageID(location.locationNameID, important=False)
        else:
            return StripTags(location.locationName)

    @property
    def subtext(self):
        if self.is_solar_system:
            return self._get_location_subtext()
        if self.is_constellation:
            return self._get_constellation_subtext()
        if self.is_region:
            return self._get_region_subtext()
        if self.is_station:
            return self._get_location_subtext()
        return ''

    def render_icon(self, size):
        if self.is_solar_system:
            return self._render_solar_system_icon(size)
        if self.is_constellation:
            return self._render_constellation_icon(size)
        if self.is_region:
            return self._render_region_icon(size)
        if self.is_station:
            return self._render_station_icon(size)

    def get_drag_data(self):
        return dragdata.Location(location_id=self.location_id)

    def get_menu(self):
        return sm.GetService('menu').CelestialMenu(self.location_id)

    def has_show_info(self):
        return True

    def show_info(self):
        sm.GetService('info').ShowInfo(itemID=self.location_id, typeID=self.type_id)

    def _get_location_subtext(self):
        location = cfg.evelocations.Get(self.location_id)
        solar_system_id = location.solarSystemID
        solar_system = cfg.mapSystemCache.Get(solar_system_id)
        constellation = cfg.mapConstellationCache.Get(solar_system.constellationID)
        constellation_name = cfg.evelocations.Get(solar_system.constellationID).name
        region_name = cfg.evelocations.Get(constellation.regionID).name
        if self.location_id != solar_system_id:
            solar_system_name = cfg.evelocations.Get(solar_system_id).name
            return u'{} > {} > {}'.format(region_name, constellation_name, solar_system_name)
        else:
            return u'{} - {} > {}'.format(eveformat.solar_system_security_status(self.location_id), region_name, constellation_name)

    def _get_constellation_subtext(self):
        constellation = cfg.mapConstellationCache.Get(self.location_id)
        return cfg.evelocations.Get(constellation.regionID).name

    def _get_region_subtext(self):
        return localization.GetByLabel('UI/Common/LocationTypes/Region')

    def _render_solar_system_icon(self, size):
        if size < 32:
            color = sm.GetService('map').GetSystemColor(self.location_id)
            return self._render_icon(eveicon.solar_system, size, color)
        map_icon = SolarSystemMapIcon(width=size, height=size)
        map_icon.Draw(self.location_id, size)
        return map_icon

    def _render_station_icon(self, size):
        return ItemIcon(typeID=self.type_id, width=size, height=size)

    def _render_constellation_icon(self, size):
        if size < 32:
            return self._render_icon(eveicon.constellation, size)
        return ConstellationMapIcon(location_id=self.location_id, size=size, lineColors=[(0.2, 0.75, 0.2, 1), (0.2, 0.2, 0.75, 1), (0.75, 0.2, 0.2, 1)], dotColor=(0.7, 0.7, 0.7), dotSizeMultiplier=0.7)

    def _render_region_icon(self, size):
        if size < 32:
            return self._render_icon(eveicon.region, size)
        return RegionMapIcon(location_id=self.location_id, size=size, lineColors=[(0.2, 0.75, 0.2, 1), (0.2, 0.2, 0.75, 1), (0.75, 0.2, 0.2, 1)], dotColor=(0.7, 0.7, 0.7))

    def _render_icon(self, icon, size, color = None):
        return Sprite(width=min(16, size), height=min(16, size), texturePath=icon, color=color or TextColor.SECONDARY)
