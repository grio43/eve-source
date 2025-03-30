#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\shipSkinDesignSvc.py
import logging
import uthread
from cosmetics.client.messengers.cosmetics.ship.shipSkinDesignRequestMessenger import PublicShipSkinDesignRequestMessenger
from cosmetics.client.shipSkinDataSvc import get_ship_skin_data_svc
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships.link.validators.paste import ShipSkinDesignLinkValidator
from cosmetics.client.ships.skins.live_data.skin_design import SkinDesign
from cosmetics.common.ships.skins.static_data.component import ComponentsDataLoader
from eve.client.script.ui.control.message import ShowQuickMessage
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException
logger = logging.getLogger(__name__)
_instance = None

def get_ship_skin_design_svc():
    global _instance
    if _instance is None:
        _instance = _ShipSkinDesignSvc()
    return _instance


class _ShipSkinDesignSvc(object):
    __startupdependencies__ = ['publicGatewaySvc']
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self):
        self._designs_cache = {}
        self._owned_design_ids_cache = None
        self._cached_saved_design_capacity = None
        public_gateway = sm.GetService('publicGatewaySvc')
        self._request_messenger = PublicShipSkinDesignRequestMessenger(public_gateway)
        sm.RegisterNotify(self)
        sm.GetService('chat').add_paste_validator(ShipSkinDesignLinkValidator())

    def OnSessionChanged(self, _isRemote, _sess, change):
        if 'charid' in change:
            self._clear_cache()

    def _clear_cache(self):
        self._designs_cache = {}
        self._owned_design_ids_cache = None
        self._cached_saved_design_capacity = None

    def get_shared_design(self, character_id, design_id, force_refresh = False):
        if design_id in self._designs_cache and not force_refresh:
            design_hex = self._designs_cache[design_id]
        else:
            design_hex, error = self._request_messenger.get_shared_design_request(design_id, character_id)
            if error is not None:
                return (None, error)
            self._designs_cache[design_id] = design_hex
        return (self._get_design_data(design_hex, force_refresh), None)

    def get_saved_design(self, design_id, force_refresh = False):
        if design_id in self._designs_cache and not force_refresh:
            design_hex = self._designs_cache[design_id]
        else:
            design_hex = self._request_messenger.get_design_request(design_id)
            self._designs_cache[design_id] = design_hex
        return self._get_design_data(design_hex, force_refresh)

    def get_all_owned_designs(self, force_refresh = False):
        ComponentsDataLoader.get_components_data()
        if self._owned_design_ids_cache is None or force_refresh:
            owned_design_hexes = self._request_messenger.get_all_saved_designs_request()
            self._owned_design_ids_cache = owned_design_hexes
            for k, v in owned_design_hexes.iteritems():
                self._designs_cache[k] = v

            self._get_designs_data_parallel(owned_design_hexes, force_refresh)
        else:
            owned_design_hexes = self._owned_design_ids_cache
        return {design_id:self._get_design_data(design_hex, False) for design_id, design_hex in owned_design_hexes.iteritems()}

    def is_design_owned(self, design_id, force_refresh = False):
        if self._owned_design_ids_cache is None or force_refresh:
            owned_design_hexes = self._request_messenger.get_all_saved_designs_request()
            self._owned_design_ids_cache = owned_design_hexes
        if self._owned_design_ids_cache is not None:
            return design_id in self._owned_design_ids_cache
        return False

    def _get_designs_data_parallel(self, design_hexes, force_refresh = False):
        parallel_calls = []
        for design_hex in design_hexes.itervalues():
            parallel_calls.append((self._get_design_data, (design_hex, force_refresh)))

        if len(parallel_calls) > 0:
            return uthread.parallel(parallel_calls)
        return []

    def save_design(self, design, design_id = None):
        if design is not None:
            design.clean_up_skin()
        if design_id is None or not self.is_design_owned(design_id):
            logger.info('SKIN DESIGNS - saving new design:\n%s' % design)
            design_id, design_hex, error = self._request_messenger.save_design_request(design)
            if error is not None:
                return (None, error)
            logger.info('SKIN DESIGNS - new design saved with id %s, hex %s' % (design_id, design_hex))
            design_data = SkinDesign.copy_from_other(design, new_creator_character_id=session.charid, should_copy_components_to_use=True)
            design_data.design_hex = design_hex
            get_ship_skin_data_svc().cache_skin_data(design_hex, design_data)
            self._designs_cache[design_id] = design_hex
        else:
            logger.info('SKIN DESIGNS - updating existing design %s with %s' % (design_id, design))
            design_hex, error = self._request_messenger.update_design_request(design, design_id)
            if error is not None:
                return (None, error)
            self._designs_cache[design_id] = design_hex
            design_data = SkinDesign.copy_from_other(design, new_creator_character_id=session.charid, should_copy_components_to_use=True)
            design_data.design_hex = design_hex
            get_ship_skin_data_svc().cache_skin_data(design_hex, design_data)
        if self._owned_design_ids_cache is not None:
            self._owned_design_ids_cache[design_id] = design_hex
        ship_skin_signals.on_skin_design_saved(design_id)
        return (design_id, None)

    def is_saved(self, design):
        if not design.saved_skin_design_id:
            return False
        saved_design = self.get_saved_design(design.saved_skin_design_id)
        return saved_design and saved_design == design

    def delete_design(self, design_id):
        if design_id is not None:
            self._request_messenger.delete_design_request(design_id)
            if design_id in self._designs_cache:
                get_ship_skin_data_svc().clear_skin_data(self._designs_cache[design_id])
                self._designs_cache.pop(design_id)
            if design_id in self._owned_design_ids_cache:
                self._owned_design_ids_cache.pop(design_id)
                ship_skin_signals.on_skin_design_deleted(design_id)

    def get_saved_designs_capacity(self, force_refresh = False):
        if self._cached_saved_design_capacity is None or force_refresh:
            self._cached_saved_design_capacity = self._request_messenger.get_saved_designs_capacity_request()
        return self._cached_saved_design_capacity

    def _get_design_data(self, design_hex, force_refresh = False):
        try:
            return get_ship_skin_data_svc().get_skin_data(design_hex, force_refresh)
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            return None

    def admin_get_skin_design_cached_hex(self, saved_design_id):
        return self._designs_cache.get(saved_design_id, None)
