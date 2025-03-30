#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\settings.py
import datetime
import locks
import threadutils
import uthread2
UNCACHED = object()

class EssSettings(object):

    def __init__(self, service_manager):
        self._service_manager = service_manager
        self._is_version_checking = False
        self._reserve_bank_pulse_interval = UNCACHED

    @property
    def reserve_bank_pulse_interval(self):
        self._version_check(self._reserve_bank_pulse_interval)
        return self._reserve_bank_pulse_interval

    @locks.SingletonCall
    def prime(self):
        cache = self._service_manager.RemoteSvc('dynamicResourceCacheMgr')
        data = cache.GetDynamicResourceSettings()
        self._update_from_cache_data(data)

    def _version_check(self, value):
        if value is UNCACHED:
            self.prime()
        else:
            self._perform_async_version_check()

    @uthread2.debounce(leading=True, max_wait=10.0)
    @threadutils.threaded
    def _perform_async_version_check(self):
        if self._is_version_checking:
            return
        self._is_version_checking = True
        try:
            self.prime()
        finally:
            self._is_version_checking = False

    def _update_from_cache_data(self, data):
        self._reserve_bank_pulse_interval = datetime.timedelta(seconds=data['reservePulseIntervalSeconds'])
