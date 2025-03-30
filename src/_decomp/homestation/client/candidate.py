#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\candidate.py
import signals
from homestation import validation
from homestation.client.station import StationMixin

class ValidationToken(object):
    __notifyevents__ = ('OnCorporationChanged', 'OnOfficeRentalChanged', 'OnSessionChanged')

    def __init__(self, home_station_service, service_manager, session):
        self._is_valid = True
        self._home_station_service = home_station_service
        self._service_manager = service_manager
        self._session = session
        self.on_invalidated = signals.Signal()
        self._service_manager.RegisterNotify(self)
        self._home_station_service.on_home_station_changed.connect(self._on_home_station_changed)

    @property
    def is_valid(self):
        return self._is_valid

    def invalidate(self):
        if self._is_valid:
            self._is_valid = False
            self._service_manager.UnregisterNotify(self)
            self._home_station_service.on_home_station_changed.disconnect(self._on_home_station_changed)
            self.on_invalidated()
            self.on_invalidated.clear()

    def _on_home_station_changed(self):
        self.invalidate()

    def OnCorporationChanged(self, corporation_id, change):
        if corporation_id == self._session.corpid:
            if 'stationID' in change:
                self.invalidate()

    def OnOfficeRentalChanged(self, corporation_id, office_id):
        if corporation_id == self._session.corpid:
            self.invalidate()

    def OnSessionChanged(self, is_remote, session, change):
        if any((name in change for name in ('corpid', 'solarsystemid', 'stationid', 'structureid'))):
            self.invalidate()
        elif 'shipid' in change and session.structureid in change['shipid']:
            self.invalidate()


class StationCandidate(StationMixin):

    def __init__(self, station_id, type_id, solar_system_id, is_current_station, is_school_hq, is_home_station, validation_token, errors):
        self.id = station_id
        self.type_id = type_id
        self.solar_system_id = solar_system_id
        self.is_current_station = is_current_station
        self.is_school_hq = is_school_hq
        self.is_home_station = is_home_station
        self.validation_token = validation_token
        self.errors = errors

    @property
    def is_remote(self):
        return validation.is_remote(self.is_current_station, self.is_school_hq)

    def __repr__(self):
        return 'StationCandidate(station_id={}, type_id={}, solar_system_id={}, is_current_station={}, is_school_hq={}, is_home_station={}, validation_token={!r}, errors={!r})'.format(self.id, self.type_id, self.solar_system_id, self.is_current_station, self.is_school_hq, self.is_home_station, self.validation_token, self.errors)
