#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\skyhook\client\data_sources.py
import gametime
import logging
import traceback
from sovereignty.resource.client.data_types import ReagentProductionSplitDynamicData, ReagentDefinition
from sovereignty.skyhook.client.errors import SkyhookAccessForbiddenError, SkyhookNotFoundError
if False:
    from typing import Dict, List
from locks import RLock
from publicGateway.grpc.exceptions import GenericException, BackedOffException
from signals import Signal
from sovereignty.resource.shared.planetary_resources_cache import DataUnavailableError
from sovereignty.skyhook.client.messenger import SkyhookMessenger
from sovereignty.skyhook.data_type import Skyhook
from stackless_response_router.exceptions import TimeoutException
UNKNOWN_PLANET_ID = 0
logger = logging.getLogger('skyhook')

class SkyhooksLocalDataSource(object):
    _data_lock = RLock('_SkyhooksLocalDataSource')
    _is_primed = False

    def __init__(self, skyhook_messenger):
        self._skyhook_messenger = skyhook_messenger
        self._skyhook_by_instance_id = {}
        self._solar_system_id = None
        self.on_theft_vulnerability_status_changed = Signal()

    def flush_all_data(self):
        with self._data_lock:
            self._is_primed = False
            self._skyhook_by_instance_id.clear()
            self._solar_system_id = None

    def on_solarsystem_changed(self, solar_system_id):
        if solar_system_id != self._solar_system_id:
            self.flush_all_data()

    def prime_from_notice(self, solar_system_id, skyhook_data):
        if self._is_primed:
            return
        with self._data_lock:
            if self._is_primed:
                return
            self._solar_system_id = solar_system_id
            self._set_system_skyhooks(skyhook_data)
            self._is_primed = True

    def _prime_data_from_external_source(self):
        if self._is_primed:
            return
        with self._data_lock:
            if self._is_primed:
                return
            try:
                solar_system_id, local_skyhooks = self._skyhook_messenger.get_all_local()
            except (GenericException, TimeoutException) as e:
                raise DataUnavailableError(e)

            if solar_system_id != session.solarsystemid2:
                return
            self._solar_system_id = solar_system_id
            self._set_system_skyhooks(local_skyhooks)
            self._is_primed = True

    def _check_for_stale_vulnerability_data(self):
        stale_hooks = []
        now = gametime.GetWallclockTime()
        for skyhook in self._skyhook_by_instance_id.itervalues():
            is_stale = skyhook.is_vulnerability_stale(now)
            if not is_stale:
                continue
            stale_hooks.append(skyhook.ID)

        num_stale_hooks = len(stale_hooks)
        if num_stale_hooks == 0:
            return
        if len(stale_hooks) > 1:
            self.flush_all_data()
            self._prime_data_from_external_source()
            return
        with self._data_lock:
            try:
                skyhook = self._skyhook_messenger.get(stale_hooks[0])
            except (GenericException, TimeoutException, SkyhookAccessForbiddenError) as e:
                logger.warning('Failed to get stale skyhook: %s - %s', stale_hooks[0], traceback.format_exc())
                raise DataUnavailableError(e)

            self._skyhook_by_instance_id[skyhook.ID] = skyhook
        self.on_theft_vulnerability_status_changed(skyhook.ID, skyhook.vulnerability_data)

    def _set_system_skyhooks(self, skyhooks):
        for skyhook in skyhooks:
            self._skyhook_by_instance_id[skyhook.ID] = skyhook
            self.on_theft_vulnerability_status_changed(skyhook.ID, skyhook.vulnerability_data)

    def update_skyhook_simulations(self, skyhook_id, reagent_production_data_list):
        with self._data_lock:
            if not self._is_primed:
                return
            skyhook = self.get_skyhook(skyhook_id)
            if skyhook:
                skyhook.set_simulations(reagent_production_data_list)

    def update_skyhook_configurations(self, skyhook_id, data_list, resource_version):
        with self._data_lock:
            if not self._is_primed:
                return
            skyhook = self.get_skyhook(skyhook_id)
            if skyhook:
                skyhook.resource_version = resource_version
                skyhook.set_configurations(data_list)

    def get_skyhooks(self):
        logger.info('cache get_skyhooks %s', skyhook_id)
        self._prime_data_from_external_source()
        self._check_for_stale_vulnerability_data()
        return self._skyhook_by_instance_id.values()

    def get_skyhook(self, skyhook_id):
        logger.info('cache get_skyhook %s', skyhook_id)
        self._prime_data_from_external_source()
        self._check_for_stale_vulnerability_data()
        skyhook = self._skyhook_by_instance_id.get(skyhook_id, None)
        return skyhook

    def get_skyhook_vulnerability(self, skyhook_id):
        logger.info('cache get_skyhook_vulnerability %s', skyhook_id)
        self._prime_data_from_external_source()
        self._check_for_stale_vulnerability_data()
        skyhook = self._skyhook_by_instance_id.get(skyhook_id, None)
        if skyhook is None:
            raise SkyhookNotFoundError()
        return skyhook.vulnerability_data

    def get_skyhook_workforce(self, skyhook_id):
        self._prime_data_from_external_source()
        self._check_for_stale_vulnerability_data()
        skyhook = self._skyhook_by_instance_id.get(skyhook_id, None)
        if skyhook is None:
            return
        return skyhook.workforce

    def update_skyhook_vulnerability_schedule(self, skyhook_id, start_datetime, end_datetime):
        with self._data_lock:
            skyhook = self._get_skyhook_if_primed(skyhook_id)
            if skyhook is None:
                return
            skyhook.set_vulnerability_schedule(start_datetime, end_datetime)
            self.on_theft_vulnerability_status_changed(skyhook.ID, skyhook.vulnerability_data)

    def update_skyhook_vulnerability(self, skyhook_id, vulnerability):
        with self._data_lock:
            skyhook = self._get_skyhook_if_primed(skyhook_id)
            if skyhook is None:
                return
            skyhook.set_vulnerability(vulnerability)
            self.on_theft_vulnerability_status_changed(skyhook.ID, skyhook.vulnerability_data)

    def update_skyhook_vulnerability_endtime(self, skyhook_id, end_datetime, vulnerability = False):
        with self._data_lock:
            skyhook = self._get_skyhook_if_primed(skyhook_id)
            if skyhook is None:
                return
            skyhook.set_vulnerability_end(end_datetime, vulnerability)
            self.on_theft_vulnerability_status_changed(skyhook.ID, skyhook.vulnerability_data)

    def update_skyhook_activation_status(self, skyhook_id, activation_status):
        with self._data_lock:
            if not self._is_primed:
                return
            skyhook = self._skyhook_by_instance_id.get(skyhook_id, None)
            if skyhook is None:
                return
            skyhook.set_activation_status(activation_status)

    def update_workforce(self, skyhook_id, workforce):
        with self._data_lock:
            skyhook = self._get_skyhook_if_primed(skyhook_id)
            if skyhook is None:
                return
            skyhook.workforce = workforce

    def _get_skyhook_if_primed(self, skyhook_id):
        if not self._is_primed:
            return None
        return self._skyhook_by_instance_id.get(skyhook_id, None)
