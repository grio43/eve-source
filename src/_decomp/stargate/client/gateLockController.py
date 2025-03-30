#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stargate\client\gateLockController.py
import gametime
import uthread2
from stargate.client.const import RESTRICTED_SYSTEMS_WAIT_DELAY
from stargate.client.gate_signals import on_lock_changed, on_restricted_systems_updated, on_lock_removed, on_lock_added, on_lock_changed_in_restricted_system
from carbon.common.lib.const import SEC
import logging
log = logging.getLogger(__name__)

def _is_invalid_lock_change(lock_details):
    return lock_details.solar_system_id != session.solarsystemid2


class GateLockController(object):
    _instance = None
    _last_instance_id = 0

    @classmethod
    def get_instance(cls, messenger, wait_delay = RESTRICTED_SYSTEMS_WAIT_DELAY):
        if cls._instance is None:
            cls._last_instance_id += 1
            cls._instance = GateLockController(messenger, wait_delay)
        return cls._instance

    def __init__(self, messenger, wait_delay = RESTRICTED_SYSTEMS_WAIT_DELAY):
        if GateLockController._last_instance_id > 1:
            raise Exception('GateLockController instance already exists')
        self._messenger = messenger
        self._wait_delay = wait_delay
        self._restricted_systems = None
        self._cached_system_lock = None
        self._expiry_timers_by_solarsystem_id = {}
        self._solar_system_to_lock_details_dict = {}
        self._messenger.subscribe_to_restricted_systems_notice(self.on_restricted_systems_notice)
        self._messenger.subscribe_to_activated_lock_notice(self.on_lock_activated)
        self._messenger.subscribe_to_deactivated_lock_notice(self.on_lock_deactivated)

    def on_character_changed(self):
        if self._restricted_systems is not None:
            return
        uthread2.StartTasklet(self._wait_and_check_restricted_systems)

    def get_restricted_systems(self):
        return self._restricted_systems or []

    def get_solar_system_to_lock_details_dict(self):
        return self._solar_system_to_lock_details_dict

    def _wait_and_check_restricted_systems(self):
        uthread2.Sleep(self._wait_delay)
        if self._restricted_systems is not None:
            return
        restricted_systems = self._messenger.get_restricted_systems_request()
        self.on_restricted_systems_notice(restricted_systems)

    def on_restricted_systems_notice(self, restricted_systems):
        self._restricted_systems = restricted_systems
        on_restricted_systems_updated(self._restricted_systems)

    def on_lock_activated(self, lock_details):
        if _is_invalid_lock_change(lock_details):
            return
        self._cached_system_lock = lock_details
        self._solar_system_to_lock_details_dict[lock_details.solar_system_id] = lock_details
        self.start_expiry_timer(lock_details)
        on_lock_added(self._cached_system_lock)

    def on_lock_deactivated(self, lock_details):
        if _is_invalid_lock_change(lock_details):
            return
        self._cached_system_lock = None
        self._solar_system_to_lock_details_dict.pop(lock_details.solar_system_id, None)
        self.kill_expiry_timer(lock_details)
        on_lock_removed(self._cached_system_lock)

    def on_entered_system(self, solar_system_id):
        if self._restricted_systems is None:
            restricted_systems = self._messenger.get_restricted_systems_request()
            self.on_restricted_systems_notice(restricted_systems)
        if solar_system_id != session.solarsystemid2:
            return
        self._solar_system_to_lock_details_dict.clear()
        previous_lock = self._cached_system_lock
        self._cached_system_lock = None
        self.kill_expiry_timer(previous_lock)
        if solar_system_id in self._restricted_systems:
            lock_details = self._messenger.get_request()
            if lock_details is not None:
                self.on_lock_activated(lock_details)
            else:
                on_lock_changed_in_restricted_system(self._cached_system_lock, previous_lock)
        else:
            on_lock_changed(self._cached_system_lock, previous_lock)

    def get_current_system_lock(self):
        return self._cached_system_lock

    def start_expiry_timer(self, lock_details):
        existing_thread = self._expiry_timers_by_solarsystem_id.pop(lock_details.solar_system_id, None)
        if existing_thread and existing_thread.IsAlive():
            existing_thread.Kill()
        secs_until_expiry = max(gametime.GetTimeUntilNowFromDateTime(lock_details.expiry_time) / SEC, 0)
        secs_until_expiry += 1
        expiry_thread = uthread2.call_after_wallclocktime_delay(self._expire_gate_lock, secs_until_expiry, lock_details)
        self._expiry_timers_by_solarsystem_id[lock_details.solar_system_id] = expiry_thread

    def kill_expiry_timer(self, previous_lock_details):
        if previous_lock_details is None:
            return
        expiry_thread = self._expiry_timers_by_solarsystem_id.pop(previous_lock_details.solar_system_id, None)
        if expiry_thread and expiry_thread.IsAlive():
            expiry_thread.Kill()

    def _expire_gate_lock(self, lock_details):
        self._expiry_timers_by_solarsystem_id.pop(lock_details.solar_system_id, None)
        if lock_details != self.get_current_system_lock():
            return
        self.on_lock_deactivated(lock_details)
