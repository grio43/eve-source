#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\repository.py
import uthread2
from carbon.common.script.util.format import FmtTimeInterval
from datetime import datetime
from datetimeutils import filetime_to_datetime
from eveexceptions import UserError
from gametime import GetSecondsSinceWallclockTime, GetWallclockTimeAfterSeconds, SEC
from inventorycommon.const import flagCargo
from logging import getLogger
from sovereignty.mercenaryden.client.data.activity import MercenaryDenActivity
from sovereignty.mercenaryden.client.data.evolution_definition import EvolutionDefinitionInfo
from sovereignty.mercenaryden.client.data.evolution_simulation import EvolutionSimulationInfo
from sovereignty.mercenaryden.client.data.mercenary_den import MercenaryDenInfo
from sovereignty.mercenaryden.client.activity_cache import ActivityCache
from sovereignty.mercenaryden.client.mercenary_den_signals import on_evolution_simulation_changed, on_activity_expiry_changed_notice, on_activity_added_notice, on_activity_removed_notice, on_activity_completed_notice, on_activity_started_notice, on_activities_loaded, on_start_activity_failed_unknown, on_mercenary_den_removed, on_mercenary_den_added, on_mercenary_den_definition_updated
from sovereignty.mercenaryden.client.notice_listener import ExternalNoticeListener, CompletedActivity
from sovereignty.mercenaryden.client.request_messenger import PublicMercenaryDenRequestMessenger
from sovereignty.mercenaryden.client.mocks.request_messenger_mock import MockMercenaryDenRequestMessenger
from sovereignty.mercenaryden.common.errors import UnknownActivity, GenericError, ServiceUnavailable
from uthread2 import StartTasklet
from uuid import UUID
logger = getLogger('mercenary_den')
_instance = None
if False:
    from typing import Dict, List, Set

def setup_singleton(public_gateway, volume_getter, cargo_volume_getter, infomorph_extractor, mock_setting):
    global _instance
    if _instance is None:
        _instance = _MercenaryDenRepository(public_gateway, volume_getter, cargo_volume_getter, infomorph_extractor, mock_setting)


def get_mercenary_den_repository():
    if _instance is None:
        raise AttributeError('Mercenary Den repository has not been started')
    return _instance


class _MercenaryDenRepository(object):
    __notifyevents__ = ['OnCharacterSessionChanged',
     'OnMyMercenaryDenRemoved',
     'OnMercenaryDenRegistrationInvalid',
     'OnMercenaryDenRegistrationSuccess']

    def __init__(self, public_gateway, volume_getter, cargo_volume_getter, infomorph_extractor, mock_setting):
        self._public_gateway = public_gateway
        self._volume_getter = volume_getter
        self._cargo_volume_getter = cargo_volume_getter
        self._infomorph_extractor = infomorph_extractor
        self._mock_setting = mock_setting
        self._subscribe_to_notices()
        self._request_messenger = None
        self._activity_cache = ActivityCache()
        self._activity_limit = None
        self._activity_sync_thread = None
        self._are_activities_loaded = False
        self._get_service_manager().RegisterNotify(self)
        logger.info('MercenaryDenRepository started')

    def __del__(self):
        self._disconnect_signals()
        self._get_service_manager().UnregisterNotify(self)

    @property
    def request_messenger(self):
        if self._request_messenger is None:
            self._load_messenger()
        return self._request_messenger

    @request_messenger.setter
    def request_messenger(self, value):
        self._request_messenger = value

    @property
    def activity_cache(self):
        if not self._are_activities_loaded:
            self.load_activities_now()
        return self._activity_cache

    def OnCharacterSessionChanged(self, _old_character_id, new_character_id):
        if new_character_id:
            self._are_activities_loaded = False
            self.load_activities_async()

    def OnMyMercenaryDenRemoved(self, notifyMsg, notifyArgs):
        mercenary_den_id = notifyArgs.get('itemID', None)
        on_mercenary_den_removed(mercenary_den_id)

    def OnMercenaryDenRegistrationInvalid(self, notifyMsg, notifyArgs):
        uthread2.StartTasklet(eve.Message, notifyMsg, notifyArgs)

    def OnMercenaryDenRegistrationSuccess(self, notifyMsg, notifyArgs):
        uthread2.StartTasklet(eve.Message, notifyMsg, notifyArgs)
        itemID = notifyArgs.get('itemID', None)
        on_mercenary_den_added(itemID)

    @classmethod
    def _get_service_manager(cls):
        return sm

    def _stop_activity_sync(self):
        if self._activity_sync_thread:
            self._activity_sync_thread.kill()
            self._activity_sync_thread = None

    def _reload_activities_cache(self, activities):
        self._activity_limit = None
        with self._activity_cache.write_lock():
            self._activity_cache.remove_all_activities()
            self._activity_cache.add_activities(activities)
            self._are_activities_loaded = True
            logger.info('Loaded activities')

    def load_activities_now(self):
        self._stop_activity_sync()
        activities = self.request_messenger.get_all_activities_request_without_retries()
        self._reload_activities_cache(activities)

    def load_activities_async(self):
        self._stop_activity_sync()
        self._activity_sync_thread = StartTasklet(self._load_activities_async)

    def _load_activities_async(self):
        try:
            activities = self.request_messenger.get_all_activities_request_with_retries()
        except ServiceUnavailable as exc:
            logger.info('Service unavailable when attempting to load activities async: %s', exc)
        except GenericError as exc:
            logger.exception('Failed to load activities async: %s', exc)
        else:
            self._reload_activities_cache(activities)
            on_activities_loaded()

        self._activity_sync_thread = None

    def _load_messenger(self):
        self._connect_messenger_signals()
        if self._mock_setting.is_enabled():
            self.request_messenger = MockMercenaryDenRequestMessenger()
        else:
            self.request_messenger = PublicMercenaryDenRequestMessenger(self._public_gateway)

    def _subscribe_to_notices(self):
        self._notice_listener = ExternalNoticeListener(self._public_gateway)
        self._connect_signals()

    def _connect_signals(self):
        self._notice_listener.on_evolution_simulation_changed_notice.connect(self._on_evolution_changed)
        self._notice_listener.on_added_notice.connect(self._on_activity_added_notice)
        self._notice_listener.on_removed_notice.connect(self._on_activity_removed_notice)
        self._notice_listener.on_completed_notice.connect(self._on_activity_completed_notice)
        self._notice_listener.on_started_notice.connect(self._on_activity_started_notice)
        self._notice_listener.on_expiry_changed_notice.connect(self._on_activity_expiry_changed_notice)
        self._notice_listener.on_mercenary_den_definitions_updated_notice.connect(self._on_mercenary_den_definitions_updated_notice)

    def _connect_messenger_signals(self):
        if not self._request_messenger:
            self._mock_setting.register_to_updates(self._on_mocking_changed)

    def _disconnect_signals(self):
        self._notice_listener.on_evolution_simulation_changed_notice.disconnect(self._on_evolution_changed)
        self._notice_listener.on_added_notice.disconnect(self._on_activity_added_notice)
        self._notice_listener.on_removed_notice.disconnect(self._on_activity_removed_notice)
        self._notice_listener.on_completed_notice.disconnect(self._on_activity_completed_notice)
        self._notice_listener.on_started_notice.disconnect(self._on_activity_started_notice)
        self._notice_listener.on_expiry_changed_notice.disconnect(self._on_activity_expiry_changed_notice)
        self._notice_listener.on_mercenary_den_definitions_updated_notice.disconnect(self._on_mercenary_den_definitions_updated_notice)
        self._disconnect_messenger_signals()

    def _disconnect_messenger_signals(self):
        if self._request_messenger:
            self._mock_setting.unregister_from_updates(self._on_mocking_changed)

    def _on_mocking_changed(self, *args):
        self._load_messenger()

    def _on_evolution_changed(self, mercenary_den_id, new_evolution_simulation_info):
        on_evolution_simulation_changed(mercenary_den_id, new_evolution_simulation_info)

    def _on_activity_added_notice(self, solar_system_id, activity):
        logger.info('activity added to solar system %s', solar_system_id)
        try:
            self.activity_cache.add_activity_for_solar_system(solar_system_id, activity)
        except Exception as exc:
            logger.exception('Failed to add activity to cache on notice: %s', exc)
            return

        on_activity_added_notice(solar_system_id, activity)

    def _on_activity_expiry_changed_notice(self, previous_expiry_datetime, activity):
        logger.info('activity added on expiry')
        try:
            self.activity_cache.add_activity(activity)
        except Exception as exc:
            logger.exception('Failed to add activity to cache on notice: %s', exc)
            return

        on_activity_expiry_changed_notice(previous_expiry_datetime, activity)

    def _on_activity_started_notice(self, activity):
        logger.info('activity started')
        try:
            self.activity_cache.add_activity(activity)
        except Exception as exc:
            logger.exception('Failed to add started activity to cache on notice: %s', exc)
            return

        on_activity_started_notice(activity)

    def _on_activity_completed_notice(self, completed_activity):
        logger.info('activity completed')
        try:
            self.activity_cache.remove_activity_by_id(completed_activity.activity_id)
        except Exception as exc:
            logger.exception('Failed to remove completed activity from cache on notice: %s', exc)
            return

        on_activity_completed_notice(completed_activity)

    def _on_activity_removed_notice(self, mercenary_den_id, activity_id):
        logger.info('activity removed')
        try:
            self.activity_cache.remove_activity_by_id(activity_id)
        except Exception as exc:
            logger.exception('Failed to remove activity from cache on notice: %s', exc)
            return

        on_activity_removed_notice(mercenary_den_id, activity_id)

    def _on_mercenary_den_definitions_updated_notice(self, mercenary_den_id, evolution_definition_info, infomorphs_definition):
        on_mercenary_den_definition_updated(mercenary_den_id, evolution_definition_info, infomorphs_definition)

    def get_mercenary_den(self, item_id):
        return self.request_messenger.get_mercenary_den_request(item_id)

    def get_all_mercenary_den_activities_for_character(self):
        return self.activity_cache.get_activities()

    def get_mercenary_den_activity_for_character(self, activity_id):
        return self.activity_cache.get_activity_by_id(activity_id)

    def get_all_mercenary_den_activities_for_solar_system(self, solar_system_id):
        return self.activity_cache.get_activities_in_solar_system(solar_system_id)

    def get_all_mercenary_den_activities(self, item_id):
        return self.request_messenger.get_all_activities_for_den_request(item_id)

    def start_activity(self, activity_id):
        try:
            activity = self.request_messenger.start_activity_request(activity_id)
            return activity
        except UnknownActivity:
            on_start_activity_failed_unknown(activity_id)
            raise

    def get_activity_limit_for_character(self):
        if self._activity_limit is None:
            self._activity_limit = self.request_messenger.get_activity_capacity_request()
        return self._activity_limit

    def get_generation_tick_progress(self, infomorph_info):
        seconds_between_ticks = infomorph_info.generation_rate_tick_seconds
        if seconds_between_ticks <= 0:
            return (0, None, 0.0)
        last_tick = infomorph_info.last_generation_tick
        seconds_since_last_tick = max(0, int(GetSecondsSinceWallclockTime(last_tick)))
        seconds_to_next_tick = max(0, seconds_between_ticks - seconds_since_last_tick)
        tick_progress = max(0.0, min(1.0, float(seconds_to_next_tick) / seconds_between_ticks))
        next_tick = GetWallclockTimeAfterSeconds(seconds_to_next_tick)
        next_tick_datetime = filetime_to_datetime(next_tick)
        return (seconds_to_next_tick, next_tick_datetime, tick_progress)

    def update_evolution_levels_based_on_natural_progression(self, mercenary_den):
        is_paused = mercenary_den.evolution_info.simulation.is_paused
        base_development = mercenary_den.evolution_info.simulation.base_development_level
        last_development_tick = mercenary_den.evolution_info.simulation.development_last_simulated_at
        seconds_to_increase_development = mercenary_den.evolution_info.definition.development_unit_increase_time_seconds
        old_development = mercenary_den.evolution_info.simulation.development_level
        new_development = self._calculate_level_based_on_natural_progression(is_paused=is_paused, base_level=base_development, last_tick=last_development_tick, seconds_to_increase_unit=seconds_to_increase_development)
        base_anarchy = mercenary_den.evolution_info.simulation.base_anarchy_level
        last_anarchy_tick = mercenary_den.evolution_info.simulation.anarchy_last_simulated_at
        seconds_to_increase_anarchy = mercenary_den.evolution_info.definition.anarchy_unit_increase_time_seconds
        old_anarchy = mercenary_den.evolution_info.simulation.anarchy_level
        new_anarchy = self._calculate_level_based_on_natural_progression(is_paused=is_paused, base_level=base_anarchy, last_tick=last_anarchy_tick, seconds_to_increase_unit=seconds_to_increase_anarchy)
        mercenary_den.evolution_info.simulation.development_level = new_development
        mercenary_den.evolution_info.simulation.anarchy_level = new_anarchy
        has_changed = (old_development, old_anarchy) != (new_development, new_anarchy)
        if has_changed:
            self._log_evolution_update(old_development, old_anarchy, new_development, new_anarchy, is_paused, base_development, base_anarchy, last_development_tick, last_anarchy_tick, seconds_to_increase_development, seconds_to_increase_anarchy)
        return has_changed

    def _calculate_level_based_on_natural_progression(self, is_paused, base_level, last_tick, seconds_to_increase_unit):
        if is_paused or seconds_to_increase_unit <= 0 or last_tick is None:
            return base_level
        seconds_since_last_tick = max(0, int(GetSecondsSinceWallclockTime(last_tick)))
        new_level = base_level + seconds_since_last_tick / seconds_to_increase_unit
        return new_level

    def _log_evolution_update(self, old_development, old_anarchy, new_development, new_anarchy, is_paused, base_development, base_anarchy, last_development_tick, last_anarchy_tick, seconds_to_increase_development, seconds_to_increase_anarchy):
        info = 'MercenaryDenService: Updated development level from %s to %s and anarchy level from %s to %s.' % (old_development,
         new_development,
         old_anarchy,
         new_anarchy)
        info += '\nSimulation: IsPaused=%s.' % is_paused
        info += '\nDevelopment: Base=%s, LastTick=%s, TimeToIncreaseUnit=%s.' % (base_development, filetime_to_datetime(last_development_tick) if last_development_tick else '-', FmtTimeInterval(seconds_to_increase_development * SEC))
        info += '\nAnarchy: Base=%s, LastTick=%s, TimeToIncreaseUnit=%s.' % (base_anarchy, filetime_to_datetime(last_anarchy_tick) if last_anarchy_tick else '-', FmtTimeInterval(seconds_to_increase_anarchy * SEC))
        logger.info(info)

    def get_workforce_cost_as_percentage(self, mercenary_den_info, workforce_cost):
        planet_id = mercenary_den_info.planet_id
        sovereignty_resource_svc = sm.GetService('sovereigntyResourceSvc')
        total_workforce = sovereignty_resource_svc.GetPlanetWorkforceProduction(planet_id)
        if total_workforce <= 0:
            return 0.0
        return max(0.0, float(workforce_cost) / total_workforce * 100.0)

    def extract_infomorphs(self, mercenary_den_item_id, infomorph_type_id, quantity):
        if quantity <= 0:
            raise UserError('MercenaryDenNotEnoughUnits')
        infomorph_volume = self._volume_getter(infomorph_type_id)
        volume_available = self._cargo_volume_getter()
        volume_to_extract = quantity * infomorph_volume
        quantity_to_extract = quantity
        if volume_to_extract > volume_available:
            quantity_to_extract = int(volume_available / infomorph_volume)
        if quantity_to_extract <= 0:
            raise UserError('MercenaryDenNoUnitsFitInShipCargo')
        try:
            quantity_extracted = self._infomorph_extractor(mercenary_den_item_id, flagCargo, quantity_to_extract)
        except UserError:
            raise
        except Exception:
            raise UserError('MercenaryDenExtractionFailed')

        return quantity_extracted

    def get_my_mercenary_dens_ids(self):
        return self.request_messenger.get_all_owned_mercenary_dens_request()

    def get_maximum_dens_for_character(self):
        try:
            return self.request_messenger.get_maximum_dens_info_dens_request()
        except Exception:
            logger.exception('Failed to get maximum dens for character')
            return (None, None)
