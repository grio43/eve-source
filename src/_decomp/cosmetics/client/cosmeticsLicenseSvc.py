#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\cosmeticsLicenseSvc.py
import launchdarkly
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_QA
from cosmetics.client.shipEmblemLicensesController import ShipEmblemLicensesController
from cosmetics.client.structurePaintworkLicensesController import StructurePaintworkLicensesController
from shipcosmetics.common.const import REMOVE_EMBLEMS_LP_COST_FLAG_DEFAULT, ENABLE_LP_HERALDRY_PURCHASES_FLAG_DEFAULT, ENABLE_LP_HERALDRY_PURCHASES_FLAG, REMOVE_EMBLEMS_LP_COST_FLAG
from shipcosmetics.client.licensegateway.licenseSignals import on_enable_heraldry_purchase_flag_change

class CosmeticsLicenseService(Service):
    __guid__ = 'svc.cosmeticsLicenseSvc'
    __startupdependencies__ = ['publicGatewaySvc']
    __notifyevents__ = ['OnSessionChanged']

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        self._ship_emblems_licenses_controller = ShipEmblemLicensesController()
        self._structure_paintwork_licenses_controller = StructurePaintworkLicensesController(self._get_public_gateway())
        ld_client = launchdarkly.get_client()
        self._remove_emblems_lp_cost = REMOVE_EMBLEMS_LP_COST_FLAG_DEFAULT
        ld_client.notify_flag(REMOVE_EMBLEMS_LP_COST_FLAG, REMOVE_EMBLEMS_LP_COST_FLAG_DEFAULT, self._on_emblems_flag_changed)
        self._enable_lp_heraldry_purchases = ENABLE_LP_HERALDRY_PURCHASES_FLAG_DEFAULT
        ld_client.notify_flag(ENABLE_LP_HERALDRY_PURCHASES_FLAG, ENABLE_LP_HERALDRY_PURCHASES_FLAG_DEFAULT, self._on_heraldry_purchase_flag_changed)

    def OnSessionChanged(self, _isRemote, _session, change):
        if 'charid' in change:
            self._ship_emblems_licenses_controller.flush_cache()
        if 'corpid' in change:
            self._structure_paintwork_licenses_controller.flush_cache()

    def _get_public_gateway(self):
        return sm.GetService('publicGatewaySvc')

    def is_emblem_lp_cost_removed(self):
        return self._remove_emblems_lp_cost

    def are_heraldry_purchases_enabled(self):
        return self._enable_lp_heraldry_purchases

    def _on_emblems_flag_changed(self, launchDarklyClient, _featureKey, _fallback, _flagDeleted):
        self._remove_emblems_lp_cost = launchDarklyClient.get_bool_variation(feature_key=REMOVE_EMBLEMS_LP_COST_FLAG, fallback=REMOVE_EMBLEMS_LP_COST_FLAG_DEFAULT)

    def _on_heraldry_purchase_flag_changed(self, launchDarklyClient, _featureKey, _fallback, _flagDeleted):
        previous_value = self._enable_lp_heraldry_purchases
        self._enable_lp_heraldry_purchases = launchDarklyClient.get_bool_variation(feature_key=ENABLE_LP_HERALDRY_PURCHASES_FLAG, fallback=ENABLE_LP_HERALDRY_PURCHASES_FLAG_DEFAULT)
        if self._enable_lp_heraldry_purchases != previous_value:
            on_enable_heraldry_purchase_flag_change(self._enable_lp_heraldry_purchases)

    def is_ship_license_owned(self, license_id):
        return self._ship_emblems_licenses_controller.is_ship_license_owned(license_id)

    def get_all_ship_licenses(self):
        return self._ship_emblems_licenses_controller.get_all_ship_licenses()

    def get_all_licensed_ship_groups(self):
        return self._ship_emblems_licenses_controller.get_all_licensed_ship_groups()

    def get_owned_ship_licenses(self, force_refresh = False):
        return self._ship_emblems_licenses_controller.get_owned_ship_licenses(force_refresh=force_refresh)

    def get_unowned_ship_licenses(self, force_refresh = False):
        return self._ship_emblems_licenses_controller.get_unowned_ship_licenses(force_refresh=force_refresh)

    def get_owned_ship_licenses_for_ship(self, ship_id, force_refresh = False):
        return self._ship_emblems_licenses_controller.get_owned_ship_licenses_for_ship(ship_id, force_refresh=force_refresh)

    def get_ship_licenses_for_ship_type(self, ship_type_id):
        return self._ship_emblems_licenses_controller.get_ship_licenses_for_ship_type(ship_type_id)

    def get_by_ship_license_type_id(self, license_id):
        return self._ship_emblems_licenses_controller.get_by_ship_license_type_id(license_id)

    def debug_grant_ship_cosmetics_license(self, license_id):
        return self._ship_emblems_licenses_controller.debug_grant_ship_cosmetics_license(license_id)

    def debug_revoke_ship_cosmetics_license(self, license_id):
        return self._ship_emblems_licenses_controller.debug_revoke_ship_cosmetics_license(license_id)

    def request_license_for_structures(self, structure_ids, paintwork, duration):
        return self._structure_paintwork_licenses_controller.request_license_for_structures(structure_ids, paintwork, duration)

    def get_structure_paintwork_license(self, structure_id, license_id):
        return self._structure_paintwork_licenses_controller.get_license(structure_id, license_id)

    def request_revoke_license_for_structure(self, license_id):
        return self._structure_paintwork_licenses_controller.request_revoke_license(license_id)

    def get_structure_paintwork_licenses_catalogue(self):
        return self._structure_paintwork_licenses_controller.get_structure_paintwork_licenses_catalogue()

    def get_structure_licenses_for_corporation(self):
        return self._structure_paintwork_licenses_controller.get_licenses_for_corporation()

    def flush_paintwork_cache(self):
        self._structure_paintwork_licenses_controller.flush_cache()

    def admin_request_license_for_structures(self, structure_ids, paintwork, duration, lp_cost = -1):
        if session.role & ROLE_QA:
            return self._structure_paintwork_licenses_controller.admin_request_license_for_structures(structure_ids, paintwork, duration, lp_cost)
