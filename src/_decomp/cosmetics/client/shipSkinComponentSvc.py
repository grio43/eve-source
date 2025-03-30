#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\shipSkinComponentSvc.py
import logging
import random
import evetypes
import uthread
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from cosmetics.client.messengers.cosmetics.ship.shipSkinComponentLicenseNoticeMessenger import PublicShipComponentLicenseNoticeMessenger
from cosmetics.client.messengers.cosmetics.ship.shipSkinComponentLicenseRequestMessenger import PublicShipComponentLicenseRequestMessenger
from cosmetics.client.ships import ship_skin_signals, ship_skin_svc_signals
from cosmetics.client.ships.skins.errors import ConsumeComponentItemConflict
from cosmetics.client.ships.skins.live_data.component_license import ComponentLicense
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from cosmetics.common.ships.skins.static_data.component import ComponentsDataLoader
from cosmetics.common.ships.skins.static_data.slot import SlotsDataLoader
from inventorycommon.const import groupShipSkinDesignComponents
from localization import GetByLabel
from stackless_response_router.exceptions import TimeoutException
_instance = None
logger = logging.getLogger(__name__)
_POPULATE_CACHE_TIMEOUT_IN_SECONDS = 5
_POPULATE_CACHE_INCREMENT_IN_SECONDS = 0.1
_MAX_CONCURRENT_COMPONENT_ITEM_ACTIVATIONS = 10

def get_ship_skin_component_svc():
    global _instance
    if _instance is None:
        _instance = _ShipSkinComponentSvc()
    return _instance


class _ShipSkinComponentSvc(object):
    __startupdependencies__ = ['publicGatewaySvc']
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self):
        self._licenses_by_element_type = {}
        self._owned_licenses_already_fetched = False
        self._owned_licenses_is_fetching = False
        self._items_being_consumed = set()
        self._components_flagged_as_new = set()
        public_gateway = sm.GetService('publicGatewaySvc')
        self._request_messenger = PublicShipComponentLicenseRequestMessenger(public_gateway)
        self._notice_messenger = PublicShipComponentLicenseNoticeMessenger(public_gateway)
        sm.RegisterNotify(self)
        ship_skin_svc_signals.on_component_license_granted_internal.connect(self._on_component_license_granted_internal)

    def __del__(self):
        ship_skin_svc_signals.on_component_license_granted_internal.disconnect(self._on_component_license_granted_internal)

    def OnSessionChanged(self, _isRemote, _sess, change):
        if 'charid' in change:
            self.clear_cache()
            self._items_being_consumed = set()

    def _check_populate_cache(self, force_refresh = False):
        if not self._owned_licenses_already_fetched or force_refresh:
            self._populate_cache()

    def clear_cache(self, licenses_to_flush = None):
        if licenses_to_flush is None:
            logger.info('SKIN COMPONENT LICENSES MANAGEMENT - flushing all component licenses cache')
            self._licenses_by_element_type = {}
            self._components_flagged_as_new.clear()
        elif len(licenses_to_flush) > 0:
            logger.info('SKIN COMPONENT LICENSES MANAGEMENT - flushing cache for component licenses for components %s' % licenses_to_flush)
            for component_id in licenses_to_flush:
                if component_id in self._licenses_by_element_type:
                    self._licenses_by_element_type.pop(component_id)

        else:
            return
        self._owned_licenses_already_fetched = False
        ship_skin_signals.on_component_license_cache_invalidated(licenses_to_flush or [])

    def _populate_cache(self):
        if self._owned_licenses_is_fetching:
            logger.info('SKIN COMPONENT LICENSES MANAGEMENT - cache is already being populated, waiting for results')
            timeout = 0
            while self._owned_licenses_is_fetching:
                if timeout >= _POPULATE_CACHE_TIMEOUT_IN_SECONDS:
                    raise TimeoutException
                timeout += _POPULATE_CACHE_INCREMENT_IN_SECONDS
                uthread2.Sleep(_POPULATE_CACHE_INCREMENT_IN_SECONDS)

            return
        try:
            self._owned_licenses_is_fetching = True
            self._licenses_by_element_type = {}
            component_ids_per_license_type = self._request_messenger.get_owned_licenses_request()
            self._get_licenses_parallel(component_ids_per_license_type)
            self._owned_licenses_already_fetched = True
        finally:
            self._owned_licenses_is_fetching = False

    def _get_licenses_parallel(self, component_ids_per_license_type):
        ComponentsDataLoader.load_components_data()
        parallel_calls = []
        for license_type, component_ids in component_ids_per_license_type.iteritems():
            for component_id in component_ids:
                component_data = ComponentsDataLoader.get_component_data(component_id)
                if component_data:
                    parallel_calls.append((self.get_license, (component_id, component_data.category, license_type)))
                else:
                    logger.warning('SKIN COMPONENT LICENSES MANAGEMENT - could not find component data for component %s' % component_id)

        uthread.parallel(parallel_calls) if len(parallel_calls) > 0 else []

    def _cache_license(self, component_id, license_type, license):
        if license_type == ComponentLicenseType.LIMITED and license is not None and license.remaining_license_uses == 0:
            logger.info('SKIN COMPONENT LICENSES MANAGEMENT - %s %s not cached, bound license with 0 remaining uses' % (license_type, component_id))
            return
        if component_id not in self._licenses_by_element_type:
            self._licenses_by_element_type[component_id] = {}
        self._licenses_by_element_type[component_id][license_type] = license
        logger.info('SKIN COMPONENT LICENSES MANAGEMENT - cached %s %s' % (license_type, component_id))

    def get_license(self, component_id, component_type, license_type, force_refresh = False):
        if license_type == ComponentLicenseType.LIMITED:
            return self.get_bound_license(component_id, component_type, force_refresh)
        elif license_type == ComponentLicenseType.UNLIMITED:
            return self.get_unbound_license(component_id, component_type, force_refresh)
        else:
            return None

    def get_all_owned_licenses(self):
        self._check_populate_cache()
        licenses = []
        for component_id, license_types in self._licenses_by_element_type.iteritems():
            for license_type, license in license_types.iteritems():
                if license:
                    licenses.append(license)

        return licenses

    def get_all_owned_licenses_in_category(self, category):
        licenses = self.get_all_owned_licenses()
        licenses = [ x for x in licenses if x is not None and x.get_component_data().category == category ]
        return licenses

    def get_owned_licenses_by_type(self, component_id):
        self._check_populate_cache()
        return self._licenses_by_element_type.get(component_id, {})

    def get_bound_license(self, component_id, component_type, force_refresh = False):
        if not force_refresh and component_id in self._licenses_by_element_type and ComponentLicenseType.LIMITED in self._licenses_by_element_type[component_id]:
            logger.info('SKIN COMPONENT LICENSES MANAGEMENT - returning cached license for %s %s' % (ComponentLicenseType.LIMITED, component_id))
            return self._licenses_by_element_type[component_id][ComponentLicenseType.LIMITED]
        license = self._request_messenger.get_finite_license_request(session.charid, component_id, component_type)
        self._cache_license(component_id, ComponentLicenseType.LIMITED, license)
        return self._licenses_by_element_type.get(component_id, {}).get(ComponentLicenseType.LIMITED, None)

    def get_unbound_license(self, component_id, component_type, force_refresh = False):
        if not force_refresh and component_id in self._licenses_by_element_type and ComponentLicenseType.UNLIMITED in self._licenses_by_element_type[component_id]:
            logger.info('SKIN COMPONENT LICENSES MANAGEMENT - returning cached license for %s %s' % (ComponentLicenseType.UNLIMITED, component_id))
            return self._licenses_by_element_type[component_id][ComponentLicenseType.UNLIMITED]
        license = self._request_messenger.get_infinite_license_request(session.charid, component_id, component_type)
        self._cache_license(component_id, ComponentLicenseType.UNLIMITED, license)
        return self._licenses_by_element_type.get(component_id, {}).get(ComponentLicenseType.UNLIMITED, None)

    def get_default_license_to_use(self, component_id, component_type):
        license = self.get_unbound_license(component_id, component_type)
        if license:
            return license
        return self.get_bound_license(component_id, component_type)

    def consume_component_items(self, items):
        if len(self._items_being_consumed) > 0:
            return GetByLabel('UI/Personalization/ShipSkins/DesignComponents/UnableToActivateComponentsTooFast')
        if len(items) > _MAX_CONCURRENT_COMPONENT_ITEM_ACTIVATIONS:
            return GetByLabel('UI/Personalization/ShipSkins/DesignComponents/UnableToActivateTooManyComponents', max_designs=_MAX_CONCURRENT_COMPONENT_ITEM_ACTIVATIONS)
        error_msg = None
        item_ids_to_consume = set([ item_id for item_id, _, _ in items ])
        item_ids_to_consume = item_ids_to_consume.difference(self._items_being_consumed)
        self._items_being_consumed.update(item_ids_to_consume)
        items_to_consume = [ (item_id, type_id, qty) for item_id, type_id, qty in items if item_id in item_ids_to_consume ]
        try:
            first_exception = None
            for item in items_to_consume:
                try:
                    itemID, typeID, quantity = item
                    self._consume_component_item(itemID, typeID, quantity)
                except Exception as e:
                    if first_exception is None:
                        first_exception = e

            if first_exception:
                if isinstance(first_exception, ConsumeComponentItemConflict):
                    error_msg = GetByLabel('UI/Personalization/ShipSkins/DesignComponents/FailedToConsumeSKINDesignComponentItemAlreadyOwned')
                else:
                    error_msg = GetByLabel('UI/Personalization/ShipSkins/DesignComponents/FailedToConsumeSKINDesignComponentItem')
        finally:
            for item_id in item_ids_to_consume:
                self._items_being_consumed.remove(item_id)

            return error_msg

    def get_random_component_license(self, slot_id):
        component_data = self.get_random_component_data(slot_id)
        if not component_data:
            return None
        bound_license = self.get_bound_license(component_id=component_data.component_id, component_type=component_data.category)
        unbound_license = self.get_unbound_license(component_id=component_data.component_id, component_type=component_data.category)
        if unbound_license:
            return unbound_license
        if bound_license:
            return bound_license

    def get_random_component_data(self, slot_id, only_owned = True):
        allowed_components = SlotsDataLoader.get_allowed_component(slot_id).values()
        if only_owned:
            owned_licenses = self.get_all_owned_licenses()
            owned_ids = {l.component_id for l in owned_licenses}
            components = [ c for c in allowed_components if c.component_id in owned_ids and c.published == True ]
        else:
            components = [ c for c in allowed_components if c and c.published == True ]
        components = sorted(components, key=lambda component: component.color_shade_sort_index, reverse=False)
        if len(components) == 0:
            return None
        component_data = random.choice(components)
        return component_data

    def _consume_component_item(self, item_id, type_id, quantity):
        group_id = evetypes.GetGroupID(type_id)
        if group_id == groupShipSkinDesignComponents:
            if self._is_license_type(type_id, ComponentLicenseType.UNLIMITED):
                quantity = 1
            self._request_messenger.consume_request(item_id, quantity)
            if self._is_license_type(type_id, ComponentLicenseType.LIMITED):
                component_id = self._get_component_id_by_type(type_id)
                if component_id:
                    self.clear_cache([component_id])
        else:
            raise Exception('item %s must be of group %s to be consumed for skin component licenses' % (item_id, group_id))

    def _is_license_type(self, type_id, license_type):
        component_data = ComponentsDataLoader.get_component_for_component_type(type_id)
        if component_data:
            return component_data.get_license_type(type_id) == license_type
        return False

    def _get_component_id_by_type(self, type_id):
        component_data = ComponentsDataLoader.get_component_for_component_type(type_id)
        if component_data:
            return component_data.component_id

    def admin_grant_license(self, component_id, license_type, component_type, license_count = None):
        if session and session.role & ROLE_PROGRAMMER:
            if license_type == ComponentLicenseType.LIMITED:
                self._request_messenger.admin_grant_finite_request(component_id, component_type, license_count)
            elif license_type == ComponentLicenseType.UNLIMITED:
                self._request_messenger.admin_grant_infinite_request(component_id, component_type)
            self.clear_cache([component_id])

    def admin_revoke_license(self, component_id, license_type, component_type):
        if session and session.role & ROLE_PROGRAMMER:
            if license_type == ComponentLicenseType.LIMITED:
                self._request_messenger.admin_revoke_finite_request(session.charid, component_id, component_type)
            elif license_type == ComponentLicenseType.UNLIMITED:
                self._request_messenger.admin_revoke_infinite_request(session.charid, component_id, component_type)
            self.clear_cache([component_id])

    def set_component_is_new_flag(self, component_id, is_new):
        if is_new:
            self._components_flagged_as_new.add(component_id)
        else:
            self._components_flagged_as_new.discard(component_id)

    def is_component_new(self, component_id):
        return component_id in self._components_flagged_as_new

    def _on_component_license_granted_internal(self, component_id, quantity):
        component_data = ComponentsDataLoader.get_component_data(component_id)
        if component_data:
            license_type = ComponentLicenseType.LIMITED if quantity is not None else ComponentLicenseType.UNLIMITED
            license = self.get_license(component_id, component_data.category, license_type, force_refresh=True)
            self._set_component_is_new_flag(component_data, license, quantity)
            logger.info('SKIN COMPONENT LICENSES MANAGEMENT - license %s granted' % license)
            ship_skin_signals.on_component_license_granted(component_id, license_type, quantity)
        else:
            raise Exception('could not find component data for component %s' % component_id)

    def _set_component_is_new_flag(self, component_data, license, quantity):
        if license.license_type == ComponentLicenseType.UNLIMITED:
            existing_limited_license = self.get_license(component_data.component_id, component_data.category, ComponentLicenseType.LIMITED)
            if not existing_limited_license:
                self.set_component_is_new_flag(component_data.component_id, is_new=True)
        elif license.license_type == ComponentLicenseType.LIMITED:
            existing_unlimited_license = self.get_license(component_data.component_id, component_data.category, ComponentLicenseType.UNLIMITED)
            if not existing_unlimited_license:
                is_first_grant = license.remaining_license_uses - quantity == 0
                if is_first_grant:
                    self.set_component_is_new_flag(component_data.component_id, is_new=is_first_grant)

    def has_existing_license(self, component_id):
        component_data = ComponentsDataLoader.get_component_data(component_id)
        bound_license = self.get_bound_license(component_data.component_id, component_data.category)
        unbound_license = self.get_unbound_license(component_data.component_id, component_data.category)
        return bound_license is not None or unbound_license is not None
