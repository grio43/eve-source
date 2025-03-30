#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\location\field.py
import proper
from eveui.autocomplete.field import AutocompleteField
from eveui.autocomplete.location.provider import RegionProvider, ConstellationProvider, SolarSystemProvider, StationProvider
from eveui.autocomplete.location.suggestion import LocationSuggestion

class LocationField(AutocompleteField):

    def __init__(self, location_id = None, include_region = True, include_constellation = True, include_solar_system = True, include_station = True, region_filter = None, constellation_filter = None, solar_system_filter = None, station_filter = None, **kwargs):
        providers = []
        if include_region:
            providers.append(RegionProvider(filter=region_filter))
        if include_constellation:
            providers.append(ConstellationProvider(filter=constellation_filter))
        if include_solar_system:
            providers.append(SolarSystemProvider(filter=solar_system_filter))
        if include_station:
            providers.append(StationProvider(filter=station_filter))
        kwargs['provider'] = providers
        completed_suggestion = None
        if location_id:
            completed_suggestion = LocationSuggestion(location_id)
        kwargs['completed_suggestion'] = completed_suggestion
        kwargs.setdefault('suggestion_list_min_width', 260)
        super(LocationField, self).__init__(**kwargs)

    @proper.alias
    def location_id(self):
        if self.completed_suggestion:
            return self.completed_suggestion.location_id

    @location_id.setter
    def location_id(self, location_id):
        if location_id is None:
            suggestion = None
        else:
            suggestion = LocationSuggestion(location_id)
        self.complete(suggestion)


class SolarSystemField(LocationField):

    def __init__(self, location_id = None, filter = None, **kwargs):
        super(SolarSystemField, self).__init__(location_id=location_id, include_region=False, include_constellation=False, include_station=False, solar_system_filter=filter, **kwargs)
