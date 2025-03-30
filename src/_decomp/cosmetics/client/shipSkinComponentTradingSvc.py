#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\shipSkinComponentTradingSvc.py
import log
import logging
from collections import defaultdict
import uthread2
from cosmetics.client.messengers.cosmetics.ship.shipSkinComponentTradingRequestMessenger import PublicShipComponentTradingRequestMessenger
from cosmetics.client.shipCosmeticTransactionSvc import get_ship_cosmetic_transaction_svc
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from cosmetics.client.ships.ship_skin_signals import on_component_listing_cache_invalidated, on_are_st_patrick_component_listings_available_changed
from cosmetics.client.ships.skins.errors import ListingError
from cosmetics.common.ships.skins.static_data.component import ComponentsDataLoader
from stackless_response_router.exceptions import TimeoutException
from cosmetics.client.ships.feature_flag import are_st_patrick_component_listings_available
logger = logging.getLogger(__name__)
_POPULATE_CACHE_TIMEOUT_IN_SECONDS = 5
_POPULATE_CACHE_INCREMENT_IN_SECONDS = 0.1
_instance = None

def get_ship_skin_component_trading_svc():
    global _instance
    if _instance is None:
        _instance = _ShipSkinComponentTradingSvc()
    return _instance


class _ShipSkinComponentTradingSvc(object):
    __startupdependencies__ = ['publicGatewaySvc']
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self):
        self._fetching = False
        ComponentsDataLoader.get_components_data()
        self._component_listing_by_id = {}
        self._component_listings_by_category = defaultdict(list)
        public_gateway = sm.GetService('publicGatewaySvc')
        self._request_messenger = PublicShipComponentTradingRequestMessenger(public_gateway)
        self._notice_messenger = None
        are_st_patrick_component_listings_available()
        self._connect_signals()

    def __del__(self):
        self._disconnect_signals()

    def _connect_signals(self):
        on_are_st_patrick_component_listings_available_changed.connect(self._on_are_st_patrick_component_listings_available_changed)
        sm.RegisterNotify(self)

    def _disconnect_signals(self):
        on_are_st_patrick_component_listings_available_changed.disconnect(self._on_are_st_patrick_component_listings_available_changed)
        sm.UnregisterNotify(self)

    def OnSessionChanged(self, _isRemote, _sess, change):
        if 'charid' in change:
            self._clear_cache()

    def _clear_cache(self):
        self._component_listing_by_id = {}
        self._component_listings_by_category = defaultdict(list)
        self._fetching = False
        on_component_listing_cache_invalidated()

    def _populate_cache(self):
        if self._fetching:
            logger.info('SKIN COMPONENT TRADING - cache is already being populated, waiting for results')
            timeout = 0
            while self._fetching:
                if timeout >= _POPULATE_CACHE_TIMEOUT_IN_SECONDS:
                    raise TimeoutException
                timeout += _POPULATE_CACHE_INCREMENT_IN_SECONDS
                uthread2.Sleep(_POPULATE_CACHE_INCREMENT_IN_SECONDS)

            return
        try:
            self._fetching = True
            self._component_listing_by_id = {}
            self._component_listings_by_category = defaultdict(list)
            entries = self._request_messenger.get_all_listings_request()
            for listing_id, listing_data in entries.iteritems():
                component_data = listing_data.get_component_data()
                if component_data is None:
                    logger.warning('could not find component data for listing id %s, skipping', listing_id)
                    continue
                category_id = component_data.category
                self._component_listing_by_id[listing_id] = listing_data
                self._component_listings_by_category[category_id].append(listing_data)

        finally:
            self._fetching = False

    def _on_are_st_patrick_component_listings_available_changed(self, *args):
        logger.info('SKIN COMPONENT TRADING - feature flag switched for st patrick components availability, clearing cache')
        self._clear_cache()

    def get_all_listings(self, force_refresh = True):
        self._check_populate_cache(force_refresh)
        return self._component_listing_by_id.values()

    def get_component_listings(self, component_id):
        listings = self.get_all_listings()
        return [ l for l in listings if l.component_id == component_id ]

    def _check_populate_cache(self, force_refresh = False):
        if len(self._component_listing_by_id) == 0 or force_refresh:
            self._populate_cache()

    def get_category_listings(self, category, force_refresh = False):
        self._check_populate_cache(force_refresh)
        return self._component_listings_by_category[category]

    def purchase_listing(self, listing, quantity = 1, immediately_activate = False):
        self._check_populate_cache()
        transaction_id, error = self._request_messenger.initiate_purchase_listing_request(listing.identifier, quantity, immediately_activate)
        if error is not None:
            return error
        try:
            transaction_result = get_ship_cosmetic_transaction_svc().process_transaction(transaction_id)
            if transaction_result:
                if immediately_activate:
                    get_ship_skin_component_svc().clear_cache([listing.component_id])
                return
            return ListingError.UNKNOWN
        except TimeoutException as e:
            logger.warning('transaction timed out for listing %s purchase' % listing.identifier)
            raise e
