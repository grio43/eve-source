#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\service.py
import collections
import weakref
import caching
import carbon.common.lib.whitelist
import characterdata.schools
import locks
import signals
from carbon.common.script.sys import service
from carbon.common.script.sys.serviceManager import ServiceManager
from homestation.client import text
from homestation.client.candidate import ValidationToken, StationCandidate
from homestation.client.error import NotLoggedInError
from homestation.client.prompt import prompt_set_home_station_remotely
from homestation.client.station import Station
from homestation.error import RemoteChangeNotExpectedError
from homestation.session import get_global_session, is_logged_in
from homestation.whitelist import whitelist
UNCACHED = object()

class Service(service.Service):
    __guid__ = 'svc.home_station'
    __servicename__ = 'home_station'
    __notifyevents__ = ('OnHomeStationChanged', 'OnHomeStationMovedFromStructure', 'OnSessionChanged', 'OnSessionReset')
    __dependencies__ = ('corp', 'sessionMgr')

    def __init__(self):
        super(Service, self).__init__()
        self._home_station = UNCACHED
        self._next_remote_change_time = UNCACHED
        self._school_hq_id = UNCACHED
        self._validation_tokens = weakref.WeakSet()
        self._fetch_home_station_lock = locks.Lock('fetch_home_station_lock')
        self._fetch_school_hq_lock = locks.Lock('fetch_school_hq_lock')
        self._confirmation_checks = []
        for cls in whitelist:
            carbon.common.lib.whitelist.add_to_whitelist(cls)

    @classmethod
    def instance(cls):
        return ServiceManager.Instance().GetService(cls.__servicename__)

    @property
    def remote(self):
        return ServiceManager.Instance().RemoteSvc('home_station')

    @caching.lazy_property
    def on_home_station_changed(self):
        return signals.Signal()

    @caching.lazy_property
    def on_home_station_data_loaded(self):
        return signals.Signal()

    @property
    def is_home_station_data_loaded(self):
        return self._home_station is not UNCACHED

    def get_home_station(self):
        if self._home_station is UNCACHED:
            if not is_logged_in():
                raise NotLoggedInError()
            with self._fetch_home_station_lock:
                if self._home_station is not UNCACHED:
                    return self._home_station
                data = self.remote.get_home_station()
                self._home_station = Station(station_id=data.id, type_id=data.type_id, solar_system_id=data.solar_system_id, is_fallback=data.is_fallback)
            self.on_home_station_data_loaded()
        return self._home_station

    def is_home_station(self, station_id):
        home_station = self.get_home_station()
        return home_station and home_station.id == station_id

    def get_home_station_candidates(self):
        is_valid = False
        while not is_valid:
            token = ValidationToken(home_station_service=self, service_manager=ServiceManager.Instance(), session=get_global_session())
            home_station = self.get_home_station()
            candidates = self.remote.get_home_station_candidates()
            is_valid = token.is_valid

        self._validation_tokens.add(token)
        text.prime_station_names([ candidate.id for candidate in candidates ])
        return CandidatesResult(candidates=[ StationCandidate(station_id=data.id, type_id=data.type_id, solar_system_id=data.solar_system_id, is_current_station=data.is_current_station, is_school_hq=data.is_school_hq, is_home_station=home_station.id == data.id, validation_token=token, errors=data.errors) for data in candidates ], token=token)

    def get_next_remote_change_time(self):
        if self._next_remote_change_time is UNCACHED:
            self._next_remote_change_time = self.remote.get_next_remote_change_time()
        return self._next_remote_change_time

    def set_home_station(self, new_home_station_id, allow_remote = False):
        for confirmation_check in self._confirmation_checks:
            if not confirmation_check(new_home_station_id):
                return

        try:
            self.remote.set_home_station(new_home_station_id, allow_remote)
        except RemoteChangeNotExpectedError:
            if prompt_set_home_station_remotely():
                self.set_home_station(new_home_station_id, allow_remote=True)

    def self_destruct_clone(self):
        self.sessionMgr.PerformSessionChange('clonejump', self.remote.self_destruct_clone)

    def get_school_hq_id(self):
        if self._school_hq_id is UNCACHED:
            with self._fetch_school_hq_lock:
                if self._school_hq_id is not UNCACHED:
                    return self._school_hq_id
                character_id = get_global_session().charid
                character_manager = ServiceManager.Instance().RemoteSvc('charMgr')
                character_info = character_manager.GetPublicInfo(character_id)
                school = characterdata.schools.get_school(character_info.schoolID)
                school_corporation = self.corp.GetCorporation(school.corporationID)
                self._school_hq_id = school_corporation.stationID
        return self._school_hq_id

    def add_confirmation_check(self, callback):
        self._confirmation_checks.append(callback)

    def remove_confirmation_check(self, callback):
        if callback in self._confirmation_checks:
            self._confirmation_checks.remove(callback)

    def clear_cache(self):
        self._clear_home_station_cache()
        self._clear_remote_change_time_cache()
        self._clear_school_hq_cache()
        self._invalidate_validation_tokens()

    def reset_remote_change_time(self):
        self._clear_remote_change_time_cache()
        self.remote.reset_remote_change_time()
        self._invalidate_validation_tokens()

    def _clear_home_station_cache(self):
        self._home_station = UNCACHED

    def _clear_remote_change_time_cache(self):
        self._next_remote_change_time = UNCACHED

    def _clear_school_hq_cache(self):
        self._school_hq_id = UNCACHED

    def _invalidate_validation_tokens(self):
        for token in self._validation_tokens:
            token.invalidate()

    def OnHomeStationChanged(self, new_home_station_id):
        self.clear_cache()
        self.on_home_station_changed()

    def OnHomeStationMovedFromStructure(self):
        self._clear_home_station_cache()
        self.on_home_station_changed()

    def OnSessionChanged(self, is_remote, session, change):
        if 'corpid' in change:
            self._clear_home_station_cache()
            self._invalidate_validation_tokens()
        if self._next_remote_change_time is not None and 'corpid' in change:
            self._clear_remote_change_time_cache()

    def OnSessionReset(self):
        self.clear_cache()


CandidatesResult = collections.namedtuple('CandidatesResult', ['candidates', 'token'])
