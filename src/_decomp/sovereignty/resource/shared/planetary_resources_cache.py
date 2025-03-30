#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\resource\shared\planetary_resources_cache.py
import datetime
from carbon.common.script.util.timerstuff import AutoTimer
from locks import RLock
from stackless_response_router.exceptions import TimeoutException

class ResourceVersionUnchanged(Exception):
    pass


class DataUnavailableError(Exception):
    pass


class VersionNumberTooLargeError(Exception):
    pass


class ResourceVersionNotFound(Exception):
    pass


class DataAccessError(Exception):
    pass


TTL = datetime.timedelta(minutes=15)
TTL_CHECK_MS = 60000

class PlanetaryResourcesCache(object):

    def __init__(self, get_data_current, get_data_version, current_ttl):
        self._get_data_current = get_data_current
        self._get_data_version = get_data_version
        self._current_max_version = None
        self._current_ttl = current_ttl
        self._data_by_version = {}
        self._expiry_by_version = {}
        self._data_lock = RLock('Cache')
        self._expiry_timer = AutoTimer(TTL_CHECK_MS, self._check_expiry_and_remove)

    def _check_expiry_and_remove(self):
        now = datetime.datetime.utcnow()
        versions_to_remove = []
        for version, expiry in self._expiry_by_version.iteritems():
            if version == self._current_max_version:
                continue
            if now < expiry:
                continue
            versions_to_remove.append(version)

        for version in versions_to_remove:
            del self._expiry_by_version[version]
            del self._data_by_version[version]

    def _should_update_current_version(self):
        return self._current_max_version is None or self._expiry_by_version[self._current_max_version] <= datetime.datetime.utcnow()

    def _renew_current_version_expiry(self, now):
        self._expiry_by_version[self._current_max_version] = now + self._current_ttl

    def _load_current_data(self):
        if not self._should_update_current_version():
            return
        with self._data_lock:
            if not self._should_update_current_version():
                return
            try:
                new_version = self._get_data_current(self._current_max_version)
            except ResourceVersionUnchanged:
                self._renew_current_version_expiry(datetime.datetime.utcnow())
                return
            except (TimeoutException, DataAccessError) as e:
                raise DataUnavailableError(e)

            self._data_by_version[new_version.version] = new_version
            self._current_max_version = new_version.version
            self._renew_current_version_expiry(datetime.datetime.utcnow())

    def _load_versioned_data(self, version):
        if version > self._current_max_version:
            raise VersionNumberTooLargeError
        if version in self._data_by_version:
            return
        with self._data_lock:
            if version in self._data_by_version:
                return
            try:
                data = self._get_data_version(version)
            except (TimeoutException, DataAccessError) as e:
                raise DataUnavailableError(e)

            self._data_by_version[data.version] = data
            self._expiry_by_version[data.version] = datetime.datetime.utcnow() + self._current_ttl

    def _ensure_cache_primed(self, version = None):
        if self._current_max_version is None:
            self._load_current_data()
        if version is None or version == self._current_max_version:
            self._load_current_data()
        else:
            self._load_versioned_data(version)

    def get_data(self, version = None):
        self._ensure_cache_primed(version)
        version = version if version is not None else self._current_max_version
        return self._data_by_version[version]
