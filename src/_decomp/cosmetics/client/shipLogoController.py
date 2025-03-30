#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\shipLogoController.py
import launchdarkly
from shipcosmetics.common.const import CosmeticsType, GetSupportedCosmeticsTypes
from shipcosmetics.client.factory import ShipCosmeticGatewayFactory
from shipcosmetics.client.fittingsgateway.fittingsSignals import on_ship_cosmetics_changed
from shipcosmetics.client.fittingsgateway.quasar import on_ship_cosmetics_changed_internal
from shipcosmetics.common.const import DISABLE_ALL_SHIP_EMBLEMS_FLAG, DISABLE_ALL_SHIP_EMBLEMS_FLAG_DEFAULT
from shipcosmetics.structs import *

class ShipLogoController(object):

    def __init__(self):
        self._cache = {}
        self._fittings_gateway = ShipCosmeticGatewayFactory().fittings_gateway
        on_ship_cosmetics_changed_internal.connect(self._on_ship_cosmetics_changed)
        ld_client = launchdarkly.get_client()
        self._disable_all_ship_emblems = DISABLE_ALL_SHIP_EMBLEMS_FLAG_DEFAULT
        ld_client.notify_flag(DISABLE_ALL_SHIP_EMBLEMS_FLAG, DISABLE_ALL_SHIP_EMBLEMS_FLAG_DEFAULT, self._on_disable_all_ship_emblems_flag_changed)

    def _refresh_cache(self, ship_id):
        self._cache[ship_id] = self._fittings_gateway.getShipCosmeticFitting(ship_id)

    def flush_cache(self, ship_id = None):
        if ship_id is None:
            self._cache = {}
        elif ship_id in self._cache:
            self._cache.pop(ship_id)

    def enable_ship_cosmetic_license(self, license, slot_index, group_index, enable):
        if self.are_ship_emblems_disabled():
            return True
        if license.shipTypeID != sm.GetService('godma').GetItem(session.shipid).typeID:
            return False
        if license.cosmeticType in GetSupportedCosmeticsTypes():
            module = ShipCosmeticLogo(license) if enable else None
            return self._fittings_gateway.setShipCosmeticFittingModule(module, slot_index, group_index, session.shipid)
        return False

    def get_enabled_ship_cosmetics(self, ship_id, force_refresh = False):
        if self.are_ship_emblems_disabled():
            return []
        if force_refresh or ship_id not in self._cache:
            self._refresh_cache(ship_id)
        fitting = self._cache[ship_id]
        enabled_cosmetics = fitting.get_ship_cosmetic_fitting_types()
        if CosmeticsType.ALLIANCE_LOGO in enabled_cosmetics and session.allianceid is None:
            enabled_cosmetics.remove(CosmeticsType.ALLIANCE_LOGO)
        return enabled_cosmetics

    def _on_ship_cosmetics_changed(self, ship_id, cosmetics_types):
        self.flush_cache(ship_id)
        if CosmeticsType.ALLIANCE_LOGO in cosmetics_types and session.allianceid is None:
            cosmetics_types.remove(CosmeticsType.ALLIANCE_LOGO)
        on_ship_cosmetics_changed(ship_id, cosmetics_types)

    def are_ship_emblems_disabled(self):
        return self._disable_all_ship_emblems

    def _on_disable_all_ship_emblems_flag_changed(self, launchDarklyClient, _featureKey, _fallback, _flagDeleted):
        previousValue = self._disable_all_ship_emblems
        self._disable_all_ship_emblems = launchDarklyClient.get_bool_variation(feature_key=DISABLE_ALL_SHIP_EMBLEMS_FLAG, fallback=DISABLE_ALL_SHIP_EMBLEMS_FLAG_DEFAULT)
        if self._disable_all_ship_emblems != previousValue:
            self.flush_cache()
