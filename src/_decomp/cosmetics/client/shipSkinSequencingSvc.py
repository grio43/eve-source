#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\shipSkinSequencingSvc.py
import uthread2
import uuid
from assetholding.client.inventory.utils import are_items_available, get_items_available
from collections import defaultdict
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from cosmetics.client.shipSkinDataSvc import get_ship_skin_data_svc
from cosmetics.client.ships import ship_skin_svc_signals
from cosmetics.client.ships.feature_flag import ship_skin_sequencing_cost_discount
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.client.messengers.cosmetics.ship.shipSkinSequencingNoticeMessenger import PublicShipSkinSequencingNoticeMessenger
from cosmetics.client.messengers.cosmetics.ship.shipSkinSequencingRequestMessenger import PublicShipSkinSequencingRequestMessenger
from cosmetics.client.ships.skins.live_data.skin_design import SkinDesign
from cosmetics.client.ships.skins.live_data.sequencing_job import SequencingJob, SequencingJobState
from cosmetics.client.ships.skins.errors import SequencingJobError, GenericError, NoTimeRemainingException
import cosmetics.client.ships.ship_skin_signals as ship_skin_signals
from cosmetics.common.ships.skins import sequencing_util
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.static_data.component import ComponentsDataLoader
from logging import getLogger
from eve.client.script.ui.cosmetics.ship.pages.sequence import sequence_ui_signals
from eve.common.script.sys.idCheckers import IsSequenceBinder
from skills.client.util import get_skill_service
_instance = None
logger = getLogger(__name__)

def get_ship_skin_sequencing_svc():
    global _instance
    if _instance is None:
        _instance = _ShipSkinSequencingSvc()
    return _instance


class _ShipSkinSequencingSvc(object):
    __startupdependencies__ = ['publicGatewaySvc']
    __notifyevents__ = ['OnSessionChanged', 'OnItemsChanged']

    def __init__(self):
        self._sequencing_jobs_cache = {}
        self._my_sequencing_jobs_fetched_already = False
        self._cached_plex_by_tier_level = None
        self._cached_sequencing_cost_discount = None
        self._cached_time_limits_and_prices = None
        self._cached_licenses_used = {}
        self._num_runs = 1
        self._expedited_jobs = set()
        ship_skin_sequencing_cost_discount()
        self._connect_signals()
        public_gateway = sm.GetService('publicGatewaySvc')
        self._request_messenger = PublicShipSkinSequencingRequestMessenger(public_gateway)
        self._notice_messenger = PublicShipSkinSequencingNoticeMessenger(public_gateway)
        sm.RegisterNotify(self)

    def __del__(self):
        self._disconnect_signals()

    def _connect_signals(self):
        ship_skin_svc_signals.on_sequencing_started_internal.connect(self._on_sequencing_started_internal)
        ship_skin_svc_signals.on_sequencing_failed_internal.connect(self._on_sequencing_failed_internal)
        ship_skin_svc_signals.on_sequencing_completed_internal.connect(self._on_sequencing_completed_internal)
        ship_skin_signals.on_ship_skin_sequencing_cost_discount_changed.connect(self._on_ship_skin_sequencing_cost_discount_changed)

    def _disconnect_signals(self):
        ship_skin_svc_signals.on_sequencing_started_internal.disconnect(self._on_sequencing_started_internal)
        ship_skin_svc_signals.on_sequencing_failed_internal.disconnect(self._on_sequencing_failed_internal)
        ship_skin_svc_signals.on_sequencing_completed_internal.disconnect(self._on_sequencing_completed_internal)
        ship_skin_signals.on_ship_skin_sequencing_cost_discount_changed.disconnect(self._on_ship_skin_sequencing_cost_discount_changed)

    def OnSessionChanged(self, _isRemote, _sess, change):
        if 'charid' in change:
            self._sequencing_jobs_cache = {}
            self._my_sequencing_jobs_fetched_already = False
            self._cached_plex_by_tier_level = None
            self._cached_sequencing_cost_discount = None
            self._cached_time_limits_and_prices = None
            self._expedited_jobs = set()
        sequence_ui_signals.on_sequence_binders_changed()

    def OnItemsChanged(self, items, _change, _location):
        if any([ IsSequenceBinder(item.groupID) for item in items ]):
            sequence_ui_signals.on_sequence_binders_changed()

    def _clear_cache(self):
        self._sequencing_jobs_cache = {}
        self._my_sequencing_jobs_fetched_already = False
        self._cached_plex_by_tier_level = None
        self._cached_sequencing_cost_discount = None
        self._cached_licenses_used = {}
        self.set_num_runs(1)
        ship_skin_signals.on_skin_sequencing_cache_invalidated()

    def get_all_my_active_sequencing_jobs(self, force_refresh = False):
        if force_refresh or not self._my_sequencing_jobs_fetched_already:
            self._sequencing_jobs_cache = {}
            jobs = self._request_messenger.get_all_active_sequencing_jobs_request()
            for job_id, job in jobs.items():
                self._sequencing_jobs_cache[job_id] = job

            self._my_sequencing_jobs_fetched_already = True
        return {k:v for k, v in self._sequencing_jobs_cache.items() if v.is_active()}

    def get_sequencing_job(self, job_id, force_refresh = False):
        if job_id not in self._sequencing_jobs_cache or force_refresh:
            job = self._request_messenger.get_sequencing_job_request(job_id)
            self._sequencing_jobs_cache[job_id] = job
        return self._sequencing_jobs_cache[job_id]

    def validate_design_for_sequencing(self, design):
        errors = []
        number_of_runs = self.get_num_runs()
        if not current_skin_design.get().name:
            errors.append(SequencingJobError.SKIN_NAME_MISSING)
        price, _ = self.get_sequencing_plex_price(design, number_of_runs)
        if price > sm.GetService('vgsService').GetPLEXBalance():
            errors.append(SequencingJobError.INSUFFICIENT_FUNDS)
        if not self.can_sequence_for_hull(design.ship_type_id):
            errors.append(SequencingJobError.INSUFFICIENT_SKILLS_FOR_SHIP_TYPE)
        if number_of_runs > sequencing_util.get_maximum_runs_per_job(get_skill_service().GetMyLevel):
            errors.append(SequencingJobError.MASS_SEQUENCING_LIMIT_REACHED)
        if len(self.get_all_my_active_sequencing_jobs()) >= sequencing_util.get_maximum_concurrent_sequencing_jobs(get_skill_service().GetMyLevel):
            errors.append(SequencingJobError.MAX_CONCURRENT_SEQUENCING_JOBS_REACHED)
        if not design.validate_layout():
            errors.append(SequencingJobError.INVALID_DESIGN)
        if not design.validate_licenses(number_of_runs):
            errors.append(SequencingJobError.INSUFFICIENT_COMPONENT_LICENSES)
        amount_required_by_type = design.get_sequence_binder_amounts_required(number_of_runs)
        if not are_items_available(items=amount_required_by_type, sourceLocationsOptionsList=[(None, True, None)]):
            errors.append(SequencingJobError.INSUFFICIENT_SEQUENCE_BINDERS)
        return errors

    def _update_limited_license_amount(self, design):
        number_of_runs = self.get_num_runs()
        for component_instance in design.slot_layout.slots.itervalues():
            if component_instance is not None:
                license_data = component_instance.component_license_to_use
                license_type = license_data.license_type
                if license_type != ComponentLicenseType.LIMITED:
                    continue
                remaining_uses = license_data.remaining_license_uses
                license_data.set_remaining_license_uses(remaining_uses - number_of_runs)

    def sequence_design(self, design):
        if design is not None:
            design.clean_up_skin()
        number_of_runs = self.get_num_runs()
        component_licenses = []
        component_quantity_by_id_and_license_type = defaultdict(int)
        component_category_by_id = {}
        for component_instance in design.slot_layout.slots.itervalues():
            if component_instance is not None:
                if component_instance.component_license_to_use is None:
                    return SequencingJobError.INSUFFICIENT_COMPONENT_LICENSES
                license_data = component_instance.component_license_to_use
                if license_data is None:
                    return SequencingJobError.INSUFFICIENT_COMPONENT_LICENSES
                component_id = component_instance.component_id
                license_type = license_data.license_type
                component_data = ComponentsDataLoader.get_component_data(component_id)
                if component_data is None:
                    return GenericError.UNKNOWN
                component_category_by_id[component_id] = component_data.category
                component_quantity_by_id_and_license_type[component_id, license_type] += number_of_runs
                component_licenses.append(license_data)

        job, error = self._request_messenger.initiate_sequencing_request(design, component_quantity_by_id_and_license_type, component_category_by_id, number_of_runs)
        if error is not None:
            return error
        elif job is not None and job.state == SequencingJobState.PENDING:
            self._update_limited_license_amount(design)
            self._sequencing_jobs_cache[job.job_id] = job
            self._cached_licenses_used[job.job_id] = component_licenses
            return
        else:
            return GenericError.UNKNOWN

    def set_num_runs(self, value):
        self._num_runs = value
        sequence_ui_signals.on_num_skins_changed(value)

    def get_num_runs(self):
        return self._num_runs

    def expedite_sequencing(self, job_id):
        if job_id in self._expedited_jobs:
            return
        self._expedited_jobs.add(job_id)
        try:
            error = self._request_messenger.expedite_sequencing(job_id)
            if error is not None:
                self._expedited_jobs.remove(job_id)
            return error
        except Exception as e:
            self._expedited_jobs.remove(job_id)
            raise e

    def can_sequence_for_hull(self, ship_type_id):
        is_type_restricted_to_clone_state = sm.GetService('cloneGradeSvc').IsRequirementsRestricted(ship_type_id)
        return not is_type_restricted_to_clone_state

    def get_predicted_job_duration(self, design):
        tier_durations = self._request_messenger.get_tier_durations_request()
        duration = tier_durations[design.tier_level]
        logger.info('SKIN SEQUENCING - predicted job duration for skin tier %s is %s seconds, taking skills into consideration' % (design.tier_level, duration))
        return duration

    def get_sequencing_plex_price(self, design, nb_runs):
        if self._cached_plex_by_tier_level is None:
            self._get_tier_pricing_and_discount()
        logger.info('SKIN SEQUENCING - Get sequencing PLEX price requested for tier level %s, returned: %s', design.tier_level, self._cached_plex_by_tier_level[design.tier_level])
        return (self._cached_plex_by_tier_level[design.tier_level] * nb_runs, self._cached_sequencing_cost_discount)

    def get_sequencing_cost_discount(self):
        if self._cached_sequencing_cost_discount is None:
            self._get_tier_pricing_and_discount()
        return self._cached_sequencing_cost_discount

    def get_early_completion_cost(self, job_id):
        job = self.get_sequencing_job(job_id)
        plex = self._get_early_completion_cost_from_job(job)
        logger.info('SKIN SEQUENCING - Get early completion cost requested, returned: %s', plex)
        return plex

    def _get_early_completion_cost_from_job(self, job):
        time_remaining = job.time_remaining
        if time_remaining is None:
            raise NoTimeRemainingException('Cannot calculate early completion cost as no time remains for this job')
        if self._cached_time_limits_and_prices is None:
            self._cached_time_limits_and_prices = self._request_messenger.get_early_completion_pricing_request()
            logger.info('SKIN SEQUENCING - Get early completion cost table requested. Time remaining: %s. Returned: %s', time_remaining.total_seconds(), self._cached_time_limits_and_prices)
        for remaining_greater, remaining_lesser_or_equal, plex in self._cached_time_limits_and_prices:
            if (remaining_greater < 0 or remaining_greater < time_remaining.total_seconds()) and (remaining_lesser_or_equal < 0 or time_remaining.total_seconds() < remaining_lesser_or_equal):
                return plex

    def _get_tier_pricing_and_discount(self):
        self._cached_plex_by_tier_level, self._cached_sequencing_cost_discount = self._request_messenger.get_tier_pricing_request()
        logger.info('SKIN SEQUENCING - Get sequencing PLEX price table requested, returned: %s', self._cached_plex_by_tier_level)
        logger.info('SKIN SEQUENCING - Sequencing cost discount requested, returned: %s' % self._cached_sequencing_cost_discount)

    def _update_cached_job(self, job_id):
        uthread2.start_tasklet(self._update_cached_job_thread, job_id)

    def _update_cached_job_thread(self, job_id):
        if job_id in self._sequencing_jobs_cache:
            job = self._request_messenger.get_sequencing_job_request(job_id)
            if job is not None:
                if job != self._sequencing_jobs_cache[job_id]:
                    self._sequencing_jobs_cache[job_id].copy_data_from_other(job)
                    ship_skin_signals.on_skin_sequencing_job_updated(job_id)

    def _on_sequencing_started_internal(self, job_id):
        logger.info('SKIN SEQUENCING - job %s started notice received' % job_id)
        self._update_cached_job(job_id)
        self._invalidate_component_licenses_after_sequencing(job_id)

    def _on_sequencing_failed_internal(self, job_id, reason):
        logger.info('SKIN SEQUENCING - job %s failed notice received. Reason: %s', job_id, reason)
        self._update_cached_job(job_id)
        ship_skin_signals.on_skin_sequencing_job_failed(job_id, reason)
        self._invalidate_component_licenses_after_sequencing(job_id)

    def _on_sequencing_completed_internal(self, job_id):
        logger.info('SKIN SEQUENCING - job %s completed notice received' % job_id)
        self._update_cached_job(job_id)
        ship_skin_signals.on_skin_sequencing_job_completed(job_id)

    def _invalidate_component_licenses_after_sequencing(self, job_id):
        if job_id in self._cached_licenses_used:
            get_ship_skin_component_svc().clear_cache([ x.component_id for x in self._cached_licenses_used[job_id] if x.license_type == ComponentLicenseType.LIMITED ])
            self._cached_licenses_used.pop(job_id)

    def get_available_at_active_location(self, quantity_by_type_id):
        return get_items_available(quantity_by_type_id=quantity_by_type_id, sourceLocationOptions=(None, True, None))

    def _on_ship_skin_sequencing_cost_discount_changed(self, *args):
        logger.info('SKIN SEQUENCING - sequencing cost discount flag changed, clearing cache')
        self._clear_cache()
