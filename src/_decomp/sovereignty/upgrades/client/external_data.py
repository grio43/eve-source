#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\upgrades\client\external_data.py
import locks
import logging
from sovereignty.upgrades.client.data_types import InstalledUpgradeData
from sovereignty.upgrades.client.external_messenger import SovUpgradesExternalMessenger
from sovereignty.upgrades.client.errors import SovUpgradeNotFoundError, SovUpgradeDataUnavailableError
from stackless_response_router.exceptions import TimeoutException
logger = logging.getLogger(__name__)

class UpgradesStaticDataSource(object):
    _is_primed = False

    def __init__(self, sov_upgrades_external_messenger):
        self._sov_upgrades_external_messenger = sov_upgrades_external_messenger
        self._upgrade_data_by_type_id = {}

    def prime_data(self):
        return self._prime_data_from_external_source()

    def _prime_data_from_external_source(self):
        if self._is_primed:
            return
        with locks.TempLock('prime_sov_upgrades'):
            if self._is_primed:
                return
            upgrade_static_data = self._sov_upgrades_external_messenger.get_data_for_upgrades()
            for upgrade in upgrade_static_data:
                self._upgrade_data_by_type_id[upgrade.type_id] = upgrade

            self._is_primed = True

    def reset_cache(self):
        self._is_primed = False
        self._upgrade_data_by_type_id.clear()

    def get_static_data(self, type_id):
        self._prime_data_from_external_source()
        return self._upgrade_data_by_type_id.get(type_id)

    def get_power_required(self, type_id):
        data = self.get_static_data(type_id)
        if data:
            return data.power

    def get_workforce_required(self, type_id):
        data = self.get_static_data(type_id)
        if data:
            return data.workforce


class InstalledUpgradesLocalDataSource(object):
    _data_lock = locks.RLock('_InstalledUpgradesLocalDataSource')
    _is_primed = False

    def __init__(self, sovUpgradesExternalMessenger):
        self._sovUpgradesExternalMessenger = sovUpgradesExternalMessenger
        self._installed_upgrades_local = []
        self._local_hub_id = None
        self._local_fuel_last_updated = None

    def flush_all_data(self):
        with self._data_lock:
            self._is_primed = False
            self._installed_upgrades_local = []
            self._local_hub_id = None
            self._local_fuel_last_updated = None

    def _prime_local_data_from_external_source(self, hub_id):
        if self._is_primed and self._local_hub_id == hub_id:
            return True
        with self._data_lock:
            if self._is_primed and self._local_hub_id == hub_id:
                return True
            solar_system_id = session.solarsystemid2
            try:
                installed_upgrades, fuel_last_updated = self._sovUpgradesExternalMessenger.get_installed_upgrades(hub_id)
            except (SovUpgradeDataUnavailableError, TimeoutException) as e:
                logger.warn('Failed to get SovHub upgrades for local hub %s - %s', hub_id, e)
                installed_upgrades = []
                fuel_last_updated = None

            if solar_system_id != session.solarsystemid2:
                return False
            self._set_installed_upgrades(hub_id, installed_upgrades, fuel_last_updated)
            self._is_primed = True
            return True

    def _set_installed_upgrades(self, hub_id, installed_upgrades, fuel_last_updated):
        self._local_hub_id = hub_id
        self._installed_upgrades_local = installed_upgrades
        self._local_fuel_last_updated = fuel_last_updated

    def get_installed_upgrades_in_local(self, hub_id):
        successfullyPrimed = self._prime_local_data_from_external_source(hub_id)
        if not successfullyPrimed:
            self._prime_local_data_from_external_source(hub_id)
        return self._installed_upgrades_local

    def get_local_fuel_last_updated(self, hub_id):
        successfullyPrimed = self._prime_local_data_from_external_source(hub_id)
        if not successfullyPrimed:
            self._prime_local_data_from_external_source(hub_id)
        return self._local_fuel_last_updated

    def update_installed_upgrades_if_already_primed(self, hub_id, installed_upgrades, fuel_last_updated):
        if not (self._is_primed and self._local_hub_id == hub_id):
            return
        with self._data_lock:
            if not (self._is_primed and self._local_hub_id == hub_id):
                return
            self._set_installed_upgrades(hub_id, installed_upgrades, fuel_last_updated)


class InstalledUpgradesDataSource(object):

    def __init__(self, sovUpgradesExternalMessenger):
        self._sovUpgradesExternalMessenger = sovUpgradesExternalMessenger

    def get_installed_upgrades(self, hub_id):
        installed_upgrades, fuel_last_updated = self._sovUpgradesExternalMessenger.get_installed_upgrades(hub_id)
        return installed_upgrades
