#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\controller.py
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.uicore import uicore
from evelink.client import owner_link, location_link, type_link
from gametime import MSEC, SEC
from localization import GetByLabel
from logging import getLogger
from sovereignty.mercenaryden.client import mercenary_den_signals
from sovereignty.mercenaryden.client.checkers import is_mercenary_den_close_enough_to_configure
from sovereignty.mercenaryden.client.data.mercenary_den import MercenaryDenInfo
from sovereignty.mercenaryden.client.feature_flag import is_contraband_mlp_version_enabled
from sovereignty.mercenaryden.client.ui import ui_signals
from sovereignty.mercenaryden.client.ui.qa_settings import SETTING_SHOULD_FORCE_DATA_FAILURE, SETTING_SHOULD_FORCE_MMP_VERSION, SETTING_SHOULD_FORCE_MLP_VERSION, SETTING_SHOULD_FORCE_LEVELS_MAXED_OUT, SETTING_SHOULD_FORCE_INFORMORPH_EXTRACTION_SUCCESS, SETTING_SHOULD_FORCE_DISABLED_STATE, SETTING_SHOULD_FORCE_SKILLS_MISSING
from sovereignty.mercenaryden.client.repository import get_mercenary_den_repository
from sovereignty.mercenaryden.common.errors import GenericError, ServiceUnavailable, UnknownMercenaryDen
logger = getLogger('mercenary_den')
SECONDS_BETWEEN_EVOLUTION_PROGRESS_UPDATES = 1
SECONDS_BETWEEN_CARGO_DISTANCE_UPDATES = 1

class MercenaryDenController(object):
    LABEL_PATH_MERCENARY_DEN_NAME = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/MercenaryDenName'

    def __init__(self, item_id, type_id, mercenary_den = None):
        self.item_id = item_id
        self.type_id = type_id
        self.mercenary_den = mercenary_den
        self.is_observable = True
        self.is_accessible = True
        self.is_paused = False
        self._repository = get_mercenary_den_repository()
        self._update_thread_for_infomorphs = None
        self._update_thread_for_evolution_progress = None
        self._update_thread_for_cargo_range = None
        self._within_range_for_extraction = None
        self._load_data()

    def __del__(self):
        self.clear()

    def reload_data(self):
        self.clear()
        self._load_data(should_force=True)

    def clear(self):
        self._stop_infomorph_generation_timer()
        self._stop_evolution_progress_timer()
        self._stop_cargo_distance_check_timer()
        self._disconnect_signals()
        logger.info('UI: Controller: Cleared')

    def pause(self):
        if self.is_paused:
            return
        self.is_paused = True
        self.clear()

    def resume(self):
        if not self.is_paused:
            return
        self.is_paused = False
        self._load_data(should_force=True)

    def _load_data(self, should_force = False):
        if self.mercenary_den is None or should_force:
            self._fetch_mercenary_den()
        if self.is_observable:
            self._connect_signals()
            if self.is_accessible:
                self._start_infomorph_generation_timer()
                self._start_evolution_progress_timer()
                self._start_cargo_distance_check_timer()

    def _fetch_mercenary_den(self):
        self.is_observable = True
        self.is_accessible = False
        try:
            if SETTING_SHOULD_FORCE_DATA_FAILURE.is_enabled():
                raise ServiceUnavailable('Mocking that the service is not available')
            else:
                self.mercenary_den = self._repository.get_mercenary_den(self.item_id)
                self.is_accessible = True
        except UnknownMercenaryDen:
            uicore.Message('MercenaryDenUnknown')
            self.is_observable = False
        except (GenericError, ServiceUnavailable):
            uicore.Message('MercenaryDenServiceUnavailable')
        except Exception as exc:
            logger.exception('Failed to open Mercenary Den window: %s', exc)
            uicore.Message('MercenaryDenServiceUnavailable')

        logger.info('UI: Controller: Fetched Mercenary Den data, is_observable=%s, is_accessible=%s', self.is_observable, self.is_accessible)

    def _connect_signals(self):
        mercenary_den_signals.on_evolution_simulation_changed.connect(self._on_evolution_simulation_changed)
        mercenary_den_signals.on_mercenary_den_definition_updated.connect(self._on_mercenary_den_definition_changed)
        mercenary_den_signals.on_activity_completed_notice.connect(self._on_activity_completed)
        SETTING_SHOULD_FORCE_MMP_VERSION.on_change.connect(self._on_qa_data_changed)
        SETTING_SHOULD_FORCE_MLP_VERSION.on_change.connect(self._on_qa_data_changed)
        SETTING_SHOULD_FORCE_DATA_FAILURE.on_change.connect(self._on_qa_data_changed)
        SETTING_SHOULD_FORCE_DISABLED_STATE.on_change.connect(self._on_qa_data_changed)
        SETTING_SHOULD_FORCE_SKILLS_MISSING.on_change.connect(self._on_qa_data_changed)
        SETTING_SHOULD_FORCE_LEVELS_MAXED_OUT.on_change.connect(self._on_qa_data_changed)
        SETTING_SHOULD_FORCE_INFORMORPH_EXTRACTION_SUCCESS.on_change.connect(self._on_qa_data_changed)

    def _disconnect_signals(self):
        mercenary_den_signals.on_evolution_simulation_changed.disconnect(self._on_evolution_simulation_changed)
        mercenary_den_signals.on_mercenary_den_definition_updated.disconnect(self._on_mercenary_den_definition_changed)
        mercenary_den_signals.on_activity_completed_notice.disconnect(self._on_activity_completed)
        SETTING_SHOULD_FORCE_MMP_VERSION.on_change.disconnect(self._on_qa_data_changed)
        SETTING_SHOULD_FORCE_MLP_VERSION.on_change.disconnect(self._on_qa_data_changed)
        SETTING_SHOULD_FORCE_DATA_FAILURE.on_change.disconnect(self._on_qa_data_changed)
        SETTING_SHOULD_FORCE_DISABLED_STATE.on_change.disconnect(self._on_qa_data_changed)
        SETTING_SHOULD_FORCE_SKILLS_MISSING.on_change.disconnect(self._on_qa_data_changed)
        SETTING_SHOULD_FORCE_LEVELS_MAXED_OUT.on_change.disconnect(self._on_qa_data_changed)
        SETTING_SHOULD_FORCE_INFORMORPH_EXTRACTION_SUCCESS.on_change.disconnect(self._on_qa_data_changed)

    def _on_qa_data_changed(self, *args):
        ui_signals.on_qa_settings_changed()

    def _on_activity_completed(self, activity):
        if self.mercenary_den is None or self.mercenary_den.item_id != activity.den_id:
            return
        self._update_mercenary_den()

    def _on_evolution_simulation_changed(self, mercenary_den_id, new_evolution_simulation):
        if not self.mercenary_den or self.mercenary_den.item_id != mercenary_den_id:
            return
        current_evolution_simulation = self.mercenary_den.evolution_info.simulation
        if current_evolution_simulation == new_evolution_simulation:
            return
        logger.info('UI: Controller: Update due to evolution change:\nFrom:\n%s\nTo:\n%s', current_evolution_simulation, new_evolution_simulation)
        self.mercenary_den.evolution_info.simulation = new_evolution_simulation
        self._start_evolution_progress_timer()
        ui_signals.on_evolution_data_changed()

    def _on_mercenary_den_definition_changed(self, mercenary_den_id, evolution_definition_info, infomorphs_definition):
        if not self.mercenary_den or self.mercenary_den.item_id != mercenary_den_id:
            return
        self.mercenary_den.evolution_info.definition = evolution_definition_info
        self.mercenary_den.infomorphs_info.set_definition(infomorphs_definition)
        self._start_evolution_progress_timer()
        self._start_infomorph_generation_timer()
        ui_signals.on_mercenary_den_data_changed()

    def get_mercenary_den_name(self, should_show_link = False):
        solar_system_id = self.mercenary_den.solar_system_id if self.mercenary_den else session.solarsystemid2
        if should_show_link:
            solar_system = location_link(solar_system_id)
        else:
            solar_system = cfg.evelocations.Get(solar_system_id).name
        return GetByLabel(self.LABEL_PATH_MERCENARY_DEN_NAME, typeID=self.type_id, solarSystem=solar_system)

    def get_owner_name(self):
        owner_id = self.mercenary_den.owner_id
        try:
            return owner_link(owner_id)
        except ValueError:
            return None

    def get_skyhook_owner_name(self):
        owner_id = self.mercenary_den.skyhook_owner_id
        try:
            return owner_link(owner_id)
        except ValueError:
            return None

    def get_infomorphs_collected(self):
        return self.mercenary_den.infomorphs

    def get_infomorph_capacity(self):
        return self.mercenary_den.infomorphs_info.capacity

    def get_infomorph_type_id(self):
        return self.mercenary_den.infomorphs_info.type_id

    def get_infomorph_type_name(self):
        return type_link(self.mercenary_den.infomorphs_info.type_id)

    def get_infomorph_tick_progress(self):
        time_left, _, tick_progress = self._repository.get_generation_tick_progress(self.mercenary_den.infomorphs_info)
        return (time_left, tick_progress)

    def is_enabled(self):
        if SETTING_SHOULD_FORCE_DISABLED_STATE.is_enabled():
            return False
        return self.mercenary_den.is_enabled

    def is_cargo_extraction_enabled(self):
        if SETTING_SHOULD_FORCE_SKILLS_MISSING.is_enabled():
            return False
        return self.mercenary_den.is_cargo_extraction_enabled

    @property
    def is_within_range_for_extraction(self):
        if self._within_range_for_extraction is None:
            self._within_range_for_extraction = is_mercenary_den_close_enough_to_configure(self.mercenary_den.item_id)
        return self._within_range_for_extraction

    @is_within_range_for_extraction.setter
    def is_within_range_for_extraction(self, value):
        if self._within_range_for_extraction == value:
            return
        should_send_signal = self._within_range_for_extraction is not None
        self._within_range_for_extraction = value
        if should_send_signal:
            mercenary_den_signals.on_mercenary_den_changed(self.mercenary_den.item_id)

    def get_current_workforce_cost(self):
        return self.mercenary_den.evolution_info.get_current_workforce_cost()

    def get_next_workforce_cost(self):
        return self.mercenary_den.evolution_info.get_next_workforce_cost()

    def get_workforce_cost(self, stage):
        return self.mercenary_den.evolution_info.get_workforce_cost_by_anarchy_stage(stage)

    def get_current_workforce_cost_as_percentage(self):
        workforce_cost = self.get_current_workforce_cost()
        return self._repository.get_workforce_cost_as_percentage(self.mercenary_den, workforce_cost)

    def get_workforce_cost_as_percentage(self, stage):
        workforce_cost = self.get_workforce_cost(stage)
        return self._repository.get_workforce_cost_as_percentage(self.mercenary_den, workforce_cost)

    def get_current_infomorph_generation_rates_per_second(self):
        return self.mercenary_den.get_current_infomorph_generation_rates_per_second()

    def get_infomorph_generation_rates_per_second(self, stage):
        return self.mercenary_den.get_infomorph_generation_rates_per_second_by_development_stage(stage)

    def extract_infomorphs(self, quantity_to_extract):
        if SETTING_SHOULD_FORCE_INFORMORPH_EXTRACTION_SUCCESS.is_enabled():
            return quantity_to_extract
        else:
            return self._repository.extract_infomorphs(mercenary_den_item_id=self.item_id, infomorph_type_id=self.mercenary_den.infomorphs_info.type_id, quantity=quantity_to_extract)

    def is_development_maxed_out(self):
        if self.should_force_levels_maxed_out():
            return True
        current_level = self.get_current_development_level()
        max_level = self.get_maximum_development_level()
        return current_level >= max_level

    def is_anarchy_maxed_out(self):
        if self.should_force_levels_maxed_out():
            return True
        current_level = self.get_current_anarchy_level()
        max_level = self.get_maximum_anarchy_level()
        return current_level >= max_level

    def is_development_at_minimum(self):
        if self.should_force_levels_maxed_out():
            return False
        current_level = self.get_current_development_level()
        min_level = self.get_minimum_development_level()
        return current_level <= min_level

    def is_anarchy_at_minimum(self):
        if self.should_force_levels_maxed_out():
            return False
        current_level = self.get_current_anarchy_level()
        min_level = self.get_minimum_anarchy_level()
        return current_level <= min_level

    def get_maximum_development_level(self):
        stages_and_level_bands = self.get_development_stages_and_level_bands()
        return self._get_maximum_level(stages_and_level_bands)

    def get_maximum_anarchy_level(self):
        stages_and_level_bands = self.get_anarchy_stages_and_level_bands()
        return self._get_maximum_level(stages_and_level_bands)

    def get_minimum_development_level(self):
        stages_and_level_bands = self.get_development_stages_and_level_bands()
        return self._get_minimum_level(stages_and_level_bands)

    def get_minimum_anarchy_level(self):
        stages_and_level_bands = self.get_anarchy_stages_and_level_bands()
        return self._get_minimum_level(stages_and_level_bands)

    def _get_maximum_level(self, stages_and_level_bands):
        maximum_stage = self._get_maximum_stage(stages_and_level_bands)
        _, upper = stages_and_level_bands[maximum_stage]
        return upper

    def _get_maximum_stage(self, stages_and_level_bands):
        all_stages = sorted(stages_and_level_bands.keys(), reverse=True)
        return all_stages[0]

    def _get_minimum_level(self, stages_and_level_bands):
        minimum_stage = self._get_minimum_stage(stages_and_level_bands)
        lower, _ = stages_and_level_bands[minimum_stage]
        return lower

    def _get_minimum_stage(self, stages_and_level_bands):
        all_stages = sorted(stages_and_level_bands.keys())
        return all_stages[0]

    def get_development_stages_and_level_bands(self):
        stages_and_level_bands = {}
        for stage, level_bands in self.mercenary_den.evolution_info.development_level_bands_by_stage.iteritems():
            level_lower, level_upper = level_bands
            if level_lower < level_upper:
                stages_and_level_bands[stage] = (level_lower, level_upper + 1)
            elif level_lower == level_upper:
                pass
            else:
                logger.error('Failed to display development stage %s as level bands are lower=%s > upper=%s', stage, level_lower, level_upper)

        return stages_and_level_bands

    def get_anarchy_stages_and_level_bands(self):
        stages_and_level_bands = {}
        for stage, level_bands in self.mercenary_den.evolution_info.anarchy_level_bands_by_stage.iteritems():
            level_lower, level_upper = level_bands
            if level_lower < level_upper:
                stages_and_level_bands[stage] = (level_lower, level_upper + 1)
            elif level_lower == level_upper:
                pass
            else:
                logger.error('Failed to display anarchy stage %s as level bands are lower=%s > upper=%s', stage, level_lower, level_upper)

        return stages_and_level_bands

    def get_current_development_stage(self):
        return self.mercenary_den.evolution_info.development_stage

    def get_current_development_level(self):
        return self.mercenary_den.evolution_info.development_level

    def get_current_development_level_bands(self):
        return self.mercenary_den.evolution_info.get_level_bands_for_current_development_stage()

    def get_current_anarchy_stage(self):
        return self.mercenary_den.evolution_info.anarchy_stage

    def get_current_anarchy_level(self):
        return self.mercenary_den.evolution_info.anarchy_level

    def get_current_anarchy_level_bands(self):
        return self.mercenary_den.evolution_info.get_level_bands_for_current_anarchy_stage()

    def get_next_activity_generation(self):
        _, next_generation = self._repository.get_all_mercenary_den_activities(self.item_id)
        return next_generation

    def get_activity_limit(self):
        return self._repository.get_activity_limit_for_character()

    def should_show_mtos(self):
        if SETTING_SHOULD_FORCE_MLP_VERSION.is_enabled():
            return True
        if SETTING_SHOULD_FORCE_MMP_VERSION.is_enabled():
            return False
        return is_contraband_mlp_version_enabled()

    def should_force_levels_maxed_out(self):
        return SETTING_SHOULD_FORCE_LEVELS_MAXED_OUT.is_enabled()

    def _start_infomorph_generation_timer(self):
        self._stop_infomorph_generation_timer()
        if not self.mercenary_den:
            return
        seconds_to_next_tick, next_tick, _ = self._repository.get_generation_tick_progress(self.mercenary_den.infomorphs_info)
        logger.info('UI: Controller: Queueing infomorph autoupdate in %s secs (%s)', seconds_to_next_tick, next_tick.isoformat())
        self._update_thread_for_infomorphs = AutoTimer(interval=(seconds_to_next_tick + 5) * SEC / MSEC, method=self._update_mercenary_den)

    def _update_mercenary_den(self):
        self.reload_data()
        if self.mercenary_den:
            mercenary_den_signals.on_mercenary_den_changed(self.mercenary_den.item_id)

    def _stop_infomorph_generation_timer(self):
        if self._update_thread_for_infomorphs:
            logger.info('UI: Controller: Stopping infomorph autoupdate')
            self._update_thread_for_infomorphs.KillTimer()
            self._update_thread_for_infomorphs = None

    def _start_evolution_progress_timer(self):
        self._stop_evolution_progress_timer()
        self._update_evolution_progress(should_notify_on_changes=False)
        if self.mercenary_den and not self.mercenary_den.is_evolution_paused:
            logger.info('UI: Controller: Queueing evolution progress autoupdate in %s secs', SECONDS_BETWEEN_EVOLUTION_PROGRESS_UPDATES)
            self._update_thread_for_evolution_progress = AutoTimer(interval=SECONDS_BETWEEN_EVOLUTION_PROGRESS_UPDATES * SEC / MSEC, method=self._update_evolution_progress)

    def _update_evolution_progress(self, should_notify_on_changes = True):
        if not self.mercenary_den:
            return
        has_changed = self._repository.update_evolution_levels_based_on_natural_progression(self.mercenary_den)
        if has_changed and should_notify_on_changes:
            ui_signals.on_evolution_data_changed()

    def _stop_evolution_progress_timer(self):
        if self._update_thread_for_evolution_progress:
            logger.info('UI: Controller: Stopping evolution progress autoupdate')
            self._update_thread_for_evolution_progress.KillTimer()
            self._update_thread_for_evolution_progress = None

    def _start_cargo_distance_check_timer(self):
        if self._update_thread_for_cargo_range is not None:
            return
        self._update_thread_for_cargo_range = AutoTimer(interval=SECONDS_BETWEEN_CARGO_DISTANCE_UPDATES * SEC / MSEC, method=self._update_cargo_distance_check_timer)

    def _update_cargo_distance_check_timer(self):
        self.is_within_range_for_extraction = is_mercenary_den_close_enough_to_configure(self.mercenary_den.item_id)

    def _stop_cargo_distance_check_timer(self):
        if self._update_thread_for_cargo_range is None:
            return
        self._update_thread_for_cargo_range.KillTimer()
        self._update_thread_for_cargo_range = None
