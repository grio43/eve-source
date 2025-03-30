#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\shipSkinTradingSvc.py
import datetime
import gametime
import logging
import uthread2
import uuid
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from cosmetics.client.messengers.cosmetics.ship.shipSkinTradingRequestMessenger import PublicShipSkinTradingRequestMessenger
from cosmetics.client.shipCosmeticTransactionSvc import get_ship_cosmetic_transaction_svc
from cosmetics.client.shipSkinDataSvc import get_ship_skin_data_svc
from cosmetics.client.ships.feature_flag import are_skin_hub_offers_enabled
from cosmetics.client.ships.link.validators.paste import ShipSkinListingLinkValidator
from cosmetics.client.ships.ship_skin_signals import on_skin_listing_cache_invalidated, on_skin_hub_offers_availability_changed, on_skin_listing_expired
from cosmetics.client.ships.skins.errors import GenericError, ListingError
from cosmetics.client.ships.skins.live_data.skin_listing_buyer_fee import ListingBuyerFeeType, ListingBuyerFee
from cosmetics.client.ships.skins.live_data.skin_listing_target import ListingTarget, ListedTo
from cosmetics.client.ships.skins.live_data.skin_listing_target import ListingTargetType
from cosmetics.client.skinListingsPaginationController import SkinListingsPaginationController
from cosmetics.common.ships.skins.util import SkinListingOrder, Currency
from eve.common.script.sys.idCheckers import IsCharacter, IsPlayerCorporation, IsAlliance, IsNPCCorporation
from stackless_response_router.exceptions import TimeoutException
logger = logging.getLogger(__name__)
_instance = None
_EXPIRY_WATCHDOG_FREQUENCY = 5

def get_ship_skin_trading_svc():
    global _instance
    if _instance is None:
        _instance = _ShipSkinTradingSvc()
    return _instance


class _ShipSkinTradingSvc(object):
    __startupdependencies__ = ['publicGatewaySvc']
    __notifyevents__ = ['OnSessionChanged', 'OnSkillsChanged']

    def __init__(self):
        self._skin_listing_by_id = {}
        self._cached_broker_fees_per_duration = {}
        self._cached_broker_fees_listing_target = None
        self._cached_tax_rate = None
        self._cached_tax_rate_listing_target = None
        self._cached_buyer_fees = {}
        self._cached_buyer_fee_definitions = None
        self._cached_buyer_fee_definitions_version = None
        self._listing_expiry_watcher_thread = None
        self._already_expired = []
        public_gateway = sm.GetService('publicGatewaySvc')
        self._request_messenger = PublicShipSkinTradingRequestMessenger(public_gateway)
        self._connect_signals()
        self._listing_expiry_watcher_thread = uthread2.start_tasklet(self._watch_for_expired_listings)
        sm.GetService('chat').add_paste_validator(ShipSkinListingLinkValidator())

    def __del__(self):
        self._disconnect_signals()
        if self._listing_expiry_watcher_thread:
            self._listing_expiry_watcher_thread.kill()
            self._listing_expiry_watcher_thread = None

    def _connect_signals(self):
        sm.RegisterNotify(self)
        on_skin_hub_offers_availability_changed.connect(self._on_skin_hub_offers_availability_changed)

    def _disconnect_signals(self):
        sm.UnregisterNotify(self)
        on_skin_hub_offers_availability_changed.disconnect(self._on_skin_hub_offers_availability_changed)

    def OnSessionChanged(self, _isRemote, _sess, change):
        if 'charid' in change or 'corpid' in change or 'allianceid' in change or 'corprole' in change:
            self._clear_cache()

    def OnSkillsChanged(self, *args):
        self._cached_tax_rate = None
        self._cached_tax_rate_listing_target = None

    def _on_skin_hub_offers_availability_changed(self, *args):
        logger.info('SKIN LICENSE TRADING - feature flag switched for SKIN trading availability, clearing cache')
        self._clear_cache()

    def _clear_cache(self):
        self._skin_listing_by_id = {}
        self._already_expired = []
        self._cached_broker_fees_listing_target = None
        self._cached_broker_fees_per_duration = {}
        self._cached_tax_rate = None
        self._cached_tax_rate_listing_target = None
        self._cached_buyer_fee_definitions = None
        self._cached_buyer_fee_definitions_version = None
        self._cached_buyer_fees = {}
        on_skin_listing_cache_invalidated()

    def _watch_for_expired_listings(self):
        while True:
            uthread2.Sleep(_EXPIRY_WATCHDOG_FREQUENCY)
            for listing_id, listing in self._skin_listing_by_id.iteritems():
                if listing and listing.is_expired and listing_id not in self._already_expired:
                    logger.info('SKIN LICENSE TRADING - watchdog found expired listing %s (expired at %s)' % (listing_id, listing.valid_until))
                    self._already_expired.append(listing_id)
                    on_skin_listing_expired(listing_id)

    def get_broker_fees_per_duration(self, target_id = None):
        try:
            target_type = self.get_listing_target_type(target_id)
            target = ListingTarget(target_type, target_id)
            if len(self._cached_broker_fees_per_duration) > 0 and self._cached_tax_rate_listing_target and self._cached_broker_fees_listing_target == target:
                return (self._cached_broker_fees_per_duration, None)
            self._cached_broker_fees_listing_target = target
            self._cached_broker_fees_per_duration = self._request_messenger.get_broker_fees_and_available_durations_request(self._cached_broker_fees_listing_target)
            return (self._cached_broker_fees_per_duration, None)
        except Exception as e:
            logger.exception('exception in get_broker_fees_per_duration: %s' % e)
            return ({}, ListingError.UNKNOWN)

    def get_tax_rate(self, target_id = None):
        try:
            target_type = self.get_listing_target_type(target_id)
            target = ListingTarget(target_type, target_id)
            if self._cached_tax_rate is not None and self._cached_tax_rate_listing_target and self._cached_tax_rate_listing_target == target:
                return (self._cached_tax_rate, None)
            self._cached_tax_rate_listing_target = target
            self._cached_tax_rate = self._request_messenger.get_tax_rate_request(self._cached_tax_rate_listing_target)
            return (self._cached_tax_rate, None)
        except Exception as e:
            logger.exception('exception in get_tax_rate: %s' % e)
            return (None, ListingError.UNKNOWN)

    def get_predicted_buyer_fee(self, skin_hex, target_id = None):
        try:
            target_type = self.get_listing_target_type(target_id)
            target = ListingTarget(target_type, target_id)
            if skin_hex in self._cached_buyer_fees:
                for cached_target, cached_buyer_fee in self._cached_buyer_fees[skin_hex].iteritems():
                    if cached_target == target:
                        return (cached_buyer_fee, None)

            else:
                self._cached_buyer_fees[skin_hex] = {}
            self._cached_buyer_fees[skin_hex][target] = self._request_messenger.get_buyer_fee_request(skin_hex, target)
            return (self._cached_buyer_fees[skin_hex][target], None)
        except Exception as e:
            logger.exception('exception in get_predicted_buyer_fee: %s' % e)
            return (None, ListingError.UNKNOWN)

    def get_buyer_fee_for_listing(self, listing):
        if listing is None:
            return (None, ListingError.UNKNOWN)
        try:
            _, err = self._get_buyer_fees_definitions()
            if err is not None:
                return (None, err)
            skin_data = get_ship_skin_data_svc().get_skin_data(listing.skin_hex)
            if skin_data and skin_data.tier_level in self._cached_buyer_fee_definitions:
                if listing.branded:
                    return (self._cached_buyer_fee_definitions[skin_data.tier_level].get(ListingBuyerFeeType.BRANDED_LISTING_BUYER_FEE, None), None)
                else:
                    return (self._cached_buyer_fee_definitions[skin_data.tier_level].get(ListingBuyerFeeType.REGULAR_LISTING_BUYER_FEE, None), None)
        except Exception as e:
            logger.exception('exception in get_buyer_fee_for_listing: %s' % e)
            return (None, ListingError.UNKNOWN)

    def get_available_listing_durations(self):
        self.get_broker_fees_per_duration()
        return sorted(self._cached_broker_fees_per_duration.keys())

    def get_listing_target_type(self, type_id):
        if type_id is None:
            return ListingTargetType.PUBLIC
        if IsCharacter(type_id):
            return ListingTargetType.CHARACTER
        if IsPlayerCorporation(type_id) or IsNPCCorporation(type_id):
            return ListingTargetType.CORPORATION
        if IsAlliance(type_id):
            return ListingTargetType.ALLIANCE
        return ListingTargetType.PUBLIC

    def get_pagination_controller(self):
        pagination_controller = SkinListingsPaginationController(get_page_method=self._fetch_page_from_server)
        return pagination_controller

    def get_owned_listings(self, listed_to = ListedTo.PUBLIC):
        if not are_skin_hub_offers_enabled():
            logger.info('SKIN LICENSE TRADING - Skip fetching owned SKIN listings, feature currently disabled')
            return []
        listings = self._request_messenger.get_all_owned_listings_request()
        if listed_to == ListedTo.MY_CORP:
            listings = [ l for l in listings if l.target.target_type == ListingTargetType.CORPORATION and l.target.target_id == session.corpid ]
        elif listed_to == ListedTo.MY_ALLIANCE:
            listings = [ l for l in listings if l.target.target_type == ListingTargetType.ALLIANCE and l.target.target_id == session.allianceid ]
        elif listed_to == ListedTo.SPECIFIC:
            listings = [ l for l in listings if l.target.target_type in (ListingTargetType.CHARACTER, ListingTargetType.CORPORATION, ListingTargetType.ALLIANCE) ]
        return listings

    def get_listing(self, listing_id):
        if not are_skin_hub_offers_enabled():
            logger.info('SKIN LICENSE TRADING - Skip fetching SKIN listing, feature currently disabled')
            return (None, ListingError.FEATURE_FLAG_OFF)
        listing, error = self._request_messenger.get_listing_request(listing_id)
        return (listing, error)

    def purchase_listing(self, listing_id, quantity = 1):
        if not are_skin_hub_offers_enabled():
            logger.info('SKIN LICENSE TRADING - Forbid SKIN listing purchase, feature currently disabled')
            return ListingError.FEATURE_FLAG_OFF
        if self._cached_buyer_fee_definitions_version is None:
            _, err = self._get_buyer_fees_definitions(force_refresh=True)
            if err is not None:
                return err
        try:
            transaction_id, error = self._request_messenger.initiate_purchase_listing_request(listing_id, quantity, self._cached_buyer_fee_definitions_version)
            if error is not None:
                if error == ListingError.INVALID_VERSION:
                    self._cached_buyer_fee_definitions_version = None
                return error
            try:
                transaction_result = get_ship_cosmetic_transaction_svc().process_transaction(transaction_id)
                if transaction_result:
                    return
                return ListingError.UNKNOWN
            except TimeoutException as e:
                logger.warning('transaction timed out for listing %s purchase' % listing_id)
                return GenericError.TIMEOUT

        except TimeoutException as e:
            logger.warning('transaction timed out for initiating listing %s purchase' % listing_id)
            return GenericError.TIMEOUT

    def cancel_listing(self, listing_id):
        try:
            error = self._request_messenger.cancel_listing_request(listing_id)
            if error is not None:
                return error
            self._clear_cache()
        except TimeoutException as e:
            logger.warning('transaction timed out for requesting listing {listing_id} cancellation'.format(listing_id=listing_id))
            return GenericError.TIMEOUT

    def create_listing(self, currency, price, skin_hex, duration_in_seconds, quantity = 1, target_id = None):
        if not are_skin_hub_offers_enabled():
            logger.info('SKIN LICENSE TRADING - Forbid SKIN listing creation, feature currently disabled')
            return ListingError.FEATURE_FLAG_OFF
        target_type = self.get_listing_target_type(target_id)
        target = ListingTarget(target_type, target_id)
        try:
            transaction_id, error = self._request_messenger.initiate_place_listing_request(session.charid, currency, price, skin_hex, duration_in_seconds, quantity, target)
            if error is not None:
                return error
            try:
                transaction_result = get_ship_cosmetic_transaction_svc().process_transaction(transaction_id)
                if transaction_result:
                    return
                return ListingError.UNKNOWN
            except TimeoutException as e:
                logger.warning('transaction timed out for creating listing for skin_hex %s' % skin_hex)
                return GenericError.TIMEOUT

        except TimeoutException as e:
            logger.warning('transaction timed out for initiating listing request for skin_hex %s' % skin_hex)
            return GenericError.TIMEOUT

    def admin_expire_listing(self, listing_id, minutes_to_expiry):
        if session and session.role & ROLE_PROGRAMMER:
            if minutes_to_expiry > 0:
                timestamp = gametime.now() + datetime.timedelta(minutes=minutes_to_expiry)
                self._request_messenger.set_expiration_request(listing_id, timestamp)
                self._clear_cache()

    def _fetch_page_from_server(self, ship_types_filter, order_by, ascending, listing_target_type, seller_membership_type, page_token, num_per_page):
        self._skin_listing_by_id.clear()
        if not are_skin_hub_offers_enabled():
            logger.info('SKIN LICENSE TRADING - Skip fetching SKIN listings, feature currently disabled')
            return ([], None, None)
        try:
            listings, next_page_token, error = self._request_messenger.get_all_listings_request(ship_types_filter, order_by, ascending, listing_target_type, seller_membership_type, page_token, num_per_page)
        except Exception as e:
            logging.exception(e)
            return ([], None, None)

        if error:
            logging.exception(error)
            return ([], None, error)
        for listing in listings:
            self._skin_listing_by_id[listing.identifier] = listing

        return (listings, next_page_token, None)

    def _get_buyer_fees_definitions(self, force_refresh = False):
        try:
            if force_refresh or self._cached_buyer_fee_definitions is None:
                self._cached_buyer_fee_definitions_version, self._cached_buyer_fee_definitions = self._request_messenger.get_buyer_fees_definition_request()
            return (self._cached_buyer_fee_definitions, None)
        except Exception as e:
            logger.exception('exception in _get_buyer_fees_definitions: %s' % e)
            return ({}, ListingError.UNKNOWN)
