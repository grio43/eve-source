#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipSkinTradingRequestMessenger.py
import logging
import uuid
from cosmetics.client.ships.skins.errors import STATUS_CODE_TO_LISTING_OPERATION_ERROR, STATUS_CODE_TO_LISTING_PURCHASE_OPERATION_ERROR
from cosmetics.client.ships.skins.live_data.skin_listing import SkinListing
from cosmetics.client.ships.skins.live_data.skin_listing_buyer_fee import ListingBuyerFee, ListingBuyerFeeType
from cosmetics.client.ships.skins.live_data.skin_listing_target import ListingTargetType, SellerMembershipType
from cosmetics.common.ships.skins.util import Currency, SkinListingOrder
from eveProto import split_precision, get_single_value_from_split_precision_message
from eveProto.generated.eve_public.character.character_pb2 import Identifier as CharacterIdentifier
from eveProto.generated.eve_public.cosmetic.market.api.api_pb2 import GetBrokerFeesRequest, GetBrokerFeesResponse, GetTaxRateRequest, GetTaxRateResponse, GetBuyerFeeRequest, GetBuyerFeeResponse, GetBuyerFeesDefinitionRequest, GetBuyerFeesDefinitionResponse
from eveProto.generated.eve_public.cosmetic.market.skin.listing.api.admin.requests_pb2 import SetExpirationRequest, SetExpirationResponse
from eveProto.generated.eve_public.cosmetic.market.skin.listing.api.api_pb2 import GetRequest, GetResponse, GetAllRequest, GetAllResponse, GetAllOwnedRequest, GetAllOwnedResponse, InitiatePurchaseListingRequest, InitiatePurchaseListingResponse, InitiateCreateListingRequest, InitiateCreateListingResponse, CancelListingRequest, CancelListingResponse
from eveProto.generated.eve_public.cosmetic.market.skin.listing.listing_pb2 import Identifier as ListingIdentifier
from eveProto.generated.eve_public.cosmetic.market.skin.search.search_pb2 import Filter, ShipTypeFilter, Order
from eveProto.generated.eve_public.cosmetic.market.skin.search.search_pb2 import ListingTarget, TargetPublic, TargetMyCharacter, TargetMyCorporation, TargetMyAlliance, TargetAll
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.license.license_pb2 import Identifier as LicenseIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.thirdparty_pb2 import Identifier as SkinIdentifier
from eveProto.generated.eve_public.isk.isk_pb2 import Currency as IskCurrency
from eveProto.generated.eve_public.plex.plex_pb2 import Currency as PlexCurrency
from eveProto.generated.eve_public.public_pb2 import Page
from eveProto.generated.eve_public.ship.ship_type_pb2 import Identifier as ShipTypeIdentifier
from google.protobuf.duration_pb2 import Duration
from google.protobuf.timestamp_pb2 import Timestamp
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException
_TIMEOUT_SECONDS = 3
logger = logging.getLogger(__name__)

class PublicShipSkinTradingRequestMessenger(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get_listing_request(self, listing_id):
        request = GetRequest(listing=ListingIdentifier(uuid=listing_id.bytes))
        info_log = 'SKIN LICENSE TRADING - Get listing {listing_id}'.format(listing_id=listing_id)
        try:
            response_primitive, response_payload = self._blocking_request(request, GetResponse)
            if response_payload is None:
                info_log += 'Listing not found'
                return (None, None)
            proto_listing = response_payload.listing
            listing = SkinListing.build_from_proto(proto_listing.attributes, uuid.UUID(bytes=proto_listing.id.uuid))
            info_log += 'Listing found.'
            return (listing, None)
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            listing_error = STATUS_CODE_TO_LISTING_OPERATION_ERROR.get(status_code, None)
            if listing_error:
                info_log += 'ERROR {status_code}'.format(status_code=status_code)
                return (None, listing_error)
            logger.exception('Unexpected exception when requesting to get listing: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            return (None, None)
        finally:
            logger.info(info_log)

    def get_all_listings_request(self, ship_types_filter, order_by, ascending, listing_target_type = None, seller_membership_type = None, page_token = None, page_size = 12):
        first_page = page_token is None
        page = Page(size=page_size, token=page_token if not first_page else '')
        request_filter = Filter()
        if len(ship_types_filter) > 0:
            ship_type_filter = ShipTypeFilter(ship_types=[ ShipTypeIdentifier(sequential=x) for x in ship_types_filter ])
            request_filter.ship_type_filter.CopyFrom(ship_type_filter)
        if order_by == SkinListingOrder.EXPIRES_AT:
            order = Order(field=Order.OrderField.EXPIRES_AT, ascending=ascending)
        else:
            order = Order(field=Order.OrderField.ORDER_FIELD_UNSPECIFIED, ascending=ascending)
        target = self.get_listing_target_proto(listing_target_type, seller_membership_type)
        request = GetAllRequest(page=page, filter=request_filter, order=order, listing_target=target)
        if first_page is None:
            info_log = 'SKIN LICENSE TRADING - Get all listings requested - first page. '
        else:
            info_log = 'SKIN LICENSE TRADING - Get all listings requested - page {token}. '.format(token=page_token)
        info_log += 'Requested {count} items per page, ordered by {order}, {ascending}. '.format(count=page_size, order=order_by, ascending='ascending' if ascending else 'descending')
        try:
            response_primitive, response_payload = self._blocking_request(request, GetAllResponse)
            if response_payload is None:
                if first_page:
                    info_log += 'Response: no listings found. '
                else:
                    info_log += 'Response: no listings found on page {token}. '.format(token=page_token)
                return ([], None, None)
            if first_page:
                info_log += 'Response: {amount} listings found on first page. '.format(amount=len(response_payload.listings))
            else:
                info_log += 'Response: {amount} listings found on page {token}. '.format(amount=len(response_payload.listings), token=page_token)
            next_page_token = response_payload.next_page.token if response_payload.next_page.token else None
            listings = [ SkinListing.build_from_proto(entry.attributes, uuid.UUID(bytes=entry.id.uuid)) for entry in response_payload.listings ]
            return (listings, next_page_token, None)
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            listing_error = STATUS_CODE_TO_LISTING_OPERATION_ERROR.get(status_code, None)
            info_log += 'ERROR (status_code={status_code}, error={error})'.format(status_code=status_code, error=listing_error)
            if listing_error:
                logger.exception(exc)
                return (None, None, listing_error)
            if first_page:
                logger.exception('Unexpected exception when requesting to get all listings (first page): %s', exc)
            else:
                logger.exception('Unexpected exception when requesting to get all listings (page %s): %s', (page_token, exc))
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            if first_page:
                logger.exception('Timed out when requesting to get all listings (first page): %s', exc)
            else:
                logger.exception('Timed out when requesting to get all listings (page %s): %s', (page_token, exc))
            raise
        finally:
            logger.info(info_log)

    def get_listing_target_proto(self, listing_target_type, seller_membership_type):
        if listing_target_type == ListingTargetType.PUBLIC:
            return ListingTarget(public=TargetPublic())
        elif listing_target_type == ListingTargetType.CHARACTER:
            return ListingTarget(my_character=TargetMyCharacter())
        elif listing_target_type == ListingTargetType.CORPORATION:
            if seller_membership_type is None:
                seller_membership_type = SellerMembershipType.UNSPECIFIED
            return ListingTarget(my_corporation=TargetMyCorporation(required_membership=seller_membership_type))
        elif listing_target_type == ListingTargetType.ALLIANCE:
            if seller_membership_type is None:
                seller_membership_type = SellerMembershipType.UNSPECIFIED
            return ListingTarget(my_alliance=TargetMyAlliance(required_membership=seller_membership_type))
        else:
            return ListingTarget(all=TargetAll())

    def get_all_owned_listings_request(self):
        request = GetAllOwnedRequest()
        info_log = 'SKIN LICENSE TRADING - Get all owned listings requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetAllOwnedResponse)
            if response_payload is None:
                info_log += 'Response: no owned listings found. '
                return []
            info_log += 'Response: {amount} owned listings found. '.format(amount=len(response_payload.listings))
            listings = [ SkinListing.build_from_proto(entry.attributes, uuid.UUID(bytes=entry.id.uuid)) for entry in response_payload.listings ]
            return listings
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get all owned listings: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get all owned listings: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def initiate_place_listing_request(self, character_id, currency, price, skin_hex, duration_in_seconds, quantity, target):
        request = InitiateCreateListingRequest(skin=LicenseIdentifier(character=CharacterIdentifier(sequential=character_id), skin=SkinIdentifier(hex=skin_hex)), duration=Duration(seconds=duration_in_seconds), quantity=quantity, target=target.to_proto())
        if currency == Currency.PLEX:
            request.price_plex.CopyFrom(PlexCurrency(total_in_cents=price * 100))
        elif currency == Currency.ISK:
            units, nanos = split_precision(price)
            request.price_isk.CopyFrom(IskCurrency(units=units, nanos=nanos))
        else:
            raise Exception('unknown currency %s type when attempting to create a listing for skin %s' % (currency, skin_hex))
        info_log = 'SKIN LICENSE TRADING - initiate create listing request for {quantity} x skin {hex} for {price} {currency}, with a duration of {duration} seconds, target: {target}'.format(quantity=quantity, hex=skin_hex, price=price, currency=currency, duration=duration_in_seconds, target=target)
        try:
            response_primitive, response_payload = self._blocking_request(request, InitiateCreateListingResponse)
            transaction_id = uuid.UUID(bytes=response_payload.transaction.uuid)
            info_log += 'Response: listing creation initialized with transaction id {identifier}. '.format(identifier=transaction_id)
            return (transaction_id, None)
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            purchase_listing_error = STATUS_CODE_TO_LISTING_OPERATION_ERROR.get(status_code, None)
            info_log += 'ERROR (status_code={status_code}, error={error}).'.format(status_code=status_code, error=purchase_listing_error)
            if purchase_listing_error:
                return (None, purchase_listing_error)
            logger.exception('Unexpected exception when requesting to initiate listing purchase: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to initiate listing purchase: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def cancel_listing_request(self, listing_id):
        request = CancelListingRequest(listing=ListingIdentifier(uuid=listing_id.bytes))
        info_log = 'SKIN LICENSE TRADING - cancel listing {identifier} request.'.format(identifier=listing_id)
        try:
            response_primitive, response_payload = self._blocking_request(request, CancelListingResponse)
            info_log += 'Response: listing {identifier} canceled'.format(identifier=listing_id)
            return
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            listing_operation_error = STATUS_CODE_TO_LISTING_OPERATION_ERROR.get(status_code, None)
            info_log += 'ERROR (status_code={status_code}, error={error}).'.format(status_code=status_code, error=listing_operation_error)
            if listing_operation_error:
                return listing_operation_error
            logger.exception('Unexpected exception when requesting listing cancellation: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting listing cancellation: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def initiate_purchase_listing_request(self, listing_id, quantity, buyer_fees_version):
        request = InitiatePurchaseListingRequest(listing=ListingIdentifier(uuid=listing_id.bytes), quantity=quantity, buyer_fees_version=buyer_fees_version)
        info_log = 'SKIN LICENSE TRADING - initiate purchase {quantity} x listing {identifier} request. '.format(quantity=quantity, identifier=listing_id)
        try:
            response_primitive, response_payload = self._blocking_request(request, InitiatePurchaseListingResponse)
            transaction_id = uuid.UUID(bytes=response_payload.transaction.uuid)
            info_log += 'Response: listing purchase initialized with transaction id {identifier} '.format(identifier=transaction_id)
            return (transaction_id, None)
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            purchase_listing_error = STATUS_CODE_TO_LISTING_PURCHASE_OPERATION_ERROR.get(status_code, None)
            info_log += 'ERROR (status_code={status_code}, error={error}).'.format(status_code=status_code, error=purchase_listing_error)
            if purchase_listing_error:
                return (None, purchase_listing_error)
            logger.exception('Unexpected exception when requesting to initiate listing creation: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to initiate listing creation: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def get_broker_fees_and_available_durations_request(self, target):
        request = GetBrokerFeesRequest(target=target.to_proto())
        info_log = 'SKIN LICENSE TRADING - Get all broker fees and durations requested for target %s. ' % target
        try:
            response_primitive, response_payload = self._blocking_request(request, GetBrokerFeesResponse)
            if response_payload is None:
                info_log += 'Response: no broker fees and durations found. '
                return {}
            broker_fees_per_durations = {x.duration.seconds:get_single_value_from_split_precision_message(x.broker_fee.fee) for x in response_payload.broker_fees_per_duration}
            info_log += 'Response: broker fees and durations: {result}. '.format(result=broker_fees_per_durations)
            return broker_fees_per_durations
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting broker fees and durations: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting broker fees and durations: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def get_tax_rate_request(self, target):
        request = GetTaxRateRequest(target=target.to_proto())
        info_log = 'SKIN LICENSE TRADING - Get tax rate requested for target %s. ' % target
        try:
            response_primitive, response_payload = self._blocking_request(request, GetTaxRateResponse)
            if response_payload is None:
                info_log += 'Response: no tax rate found. '
                return 0.0
            tax_rate = get_single_value_from_split_precision_message(response_payload.tax_rate)
            info_log += 'Response: tax rate: {result}. '.format(result=tax_rate)
            return tax_rate
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting tax rate: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting tax rate: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def get_buyer_fee_request(self, skin_hex, target):
        request = GetBuyerFeeRequest(target=target.to_proto(), skin=SkinIdentifier(hex=skin_hex))
        info_log = 'SKIN LICENSE TRADING - Get buyer fee requested for skin %s, target %s. ' % (skin_hex, target)
        try:
            response_primitive, response_payload = self._blocking_request(request, GetBuyerFeeResponse)
            if response_payload is None:
                info_log += 'Response: no buyer fee found. '
                return
            lp_corp = response_payload.buyer_fee.loyalty_points.associated_corporation.sequential
            lp_amount = response_payload.buyer_fee.loyalty_points.amount
            info_log += 'Response: buyer fee: {amount} LP from {corp}. '.format(amount=lp_amount, corp=lp_corp)
            return ListingBuyerFee(lp_amount, lp_corp)
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting buyer fee: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting buyer fee: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def get_buyer_fees_definition_request(self):
        request = GetBuyerFeesDefinitionRequest()
        info_log = 'SKIN LICENSE TRADING - Get buyer fee definitions requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetBuyerFeesDefinitionResponse)
            if response_payload is None:
                info_log += 'Response: no buyer fee definitions found. '
                return ('', {})
            version = response_payload.buyer_fees_version
            fees_definition = {}
            for buyer_fees in response_payload.buyer_fees:
                fees_definition[buyer_fees.skin_tier.level] = {ListingBuyerFeeType.BRANDED_LISTING_BUYER_FEE: ListingBuyerFee.from_proto(buyer_fees.branded_fee),
                 ListingBuyerFeeType.REGULAR_LISTING_BUYER_FEE: ListingBuyerFee.from_proto(buyer_fees.default_fee)}

            info_log += 'Response: buyer fee definitions version {ver}: {table}. '.format(ver=version, table=fees_definition)
            return (version, fees_definition)
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting buyer fee definitions: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting buyer fee definitions: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def set_expiration_request(self, listing_id, timestamp):
        expires = Timestamp()
        expires.FromDatetime(timestamp)
        request = SetExpirationRequest(listing=ListingIdentifier(uuid=listing_id.bytes), expires=expires)
        info_log = 'SKIN LICENSE TRADING - ADMIN set expiration to {time} for listing {identifier} request. '.format(time=timestamp, identifier=listing_id)
        try:
            self._blocking_request(request, SetExpirationResponse)
            info_log += 'Response: listing expiration set.'
            return
        except GenericException as exc:
            info_log += 'ERROR (status_code={status_code}).'.format(status_code=exc.response_primitive.status_code)
            logger.exception('Unexpected exception when requesting to set listing expiration: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to set listing expiration: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def _blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, _TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code != 200:
            raise GenericException(request_primitive, response_primitive)
        return (response_primitive, payload)
