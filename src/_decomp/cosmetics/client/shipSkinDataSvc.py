#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\shipSkinDataSvc.py
import logging
from cosmetics.client.messengers.cosmetics.ship.shipSkinDataRequestMessenger import PublicShipSkinDataRequestMessenger
from cosmetics.client.ships.skins.live_data.skin_design import SkinDesign
from cosmetics.common.ships.skins.static_data.pattern_blend_mode import NO_SECONDARY_COLOR_BLEND_MODES
from cosmetics.common.ships.skins.static_data.slot_name import SlotID
logger = logging.getLogger(__name__)
_instance = None

def get_ship_skin_data_svc():
    global _instance
    if _instance is None:
        _instance = _ShipSkinDataSvc()
    return _instance


class _ShipSkinDataSvc(object):
    __startupdependencies__ = ['publicGatewaySvc']
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self):
        self._cache = {}
        public_gateway = sm.GetService('publicGatewaySvc')
        self._request_messenger = PublicShipSkinDataRequestMessenger(public_gateway)
        sm.RegisterNotify(self)

    def OnSessionChanged(self, _isRemote, _sess, change):
        if 'charid' in change:
            self._clear_cache()

    def _clear_cache(self):
        self._cache = {}

    def cache_skin_data(self, design_hex, design_data):
        self._cache[design_hex] = design_data

    def clear_skin_data(self, design_hex):
        if design_hex in self._cache:
            self._cache.pop(design_hex)

    def get_skin_data(self, design_hex, force_refresh = False):
        if design_hex not in self._cache or force_refresh:
            skin_design = self._request_messenger.get_skin_data_request(design_hex)
            skin_design.design_hex = design_hex
            self._cache[design_hex] = skin_design
        return self._cache.get(design_hex, None)

    def clean_up_skin(self, skin_data):
        if skin_data is None or skin_data.slot_layout is None:
            return skin_data
        if skin_data.slot_layout.pattern_blend_mode not in NO_SECONDARY_COLOR_BLEND_MODES:
            return skin_data
        skin_data.slot_layout.unfit_slot(SlotID.SECONDARY_PATTERN_MATERIAL, True)
        return skin_data
