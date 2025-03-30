#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipSkinComponentTradingRequestMessenger.py
import logging
import uuid
from cosmetics.client.ships.skins.errors import STATUS_CODE_TO_LISTING_PURCHASE_OPERATION_ERROR
from cosmetics.client.ships.skins.static_data.component_listing import ComponentListing
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException
from eveProto.generated.eve_public.cosmetic.market.component.listing.listing_pb2 import Identifier as ListingIdentifier
from eveProto.generated.eve_public.cosmetic.market.component.listing.api.api_pb2 import GetAllRequest, GetAllResponse, InitiatePurchaseListingRequest, InitiatePurchaseListingResponse
_TIMEOUT_SECONDS = 3
logger = logging.getLogger(__name__)

class PublicShipComponentTradingRequestMessenger(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get_all_listings_request(self):
        request = GetAllRequest()
        info_log = 'SKIN COMPONENT TRADING - Get all listings requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetAllResponse)
            if response_payload is None:
                info_log += 'Response: no listings found'
                return
            listings = {}
            for entry in response_payload.listings:
                listing_id = uuid.UUID(bytes=entry.id.uuid)
                listings[listing_id] = ComponentListing.build_from_proto(entry.attributes, listing_id)

            info_log += 'Response: {amount} listings found:'.format(amount=len(response_payload.listings))
            for listing in listings.itervalues():
                info_log += '%s\n ' % str(listing)

            return listings
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get all listings: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get all listings: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def initiate_purchase_listing_request(self, listing_id, quantity, immediately_activate):
        request = InitiatePurchaseListingRequest(listing=ListingIdentifier(uuid=listing_id.bytes), quantity=quantity, immediately_activate=immediately_activate)
        info_log = 'SKIN COMPONENT TRADING - initiate purchase {quantity} x listing {identifier} request. '.format(quantity=quantity, identifier=listing_id)
        info_log += 'request message: {request} '.format(request=request)
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
            logger.exception('Unexpected exception when requesting to initiate listing purchase: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to initiate listing purchase: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def _blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, _TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code != 200:
            raise GenericException(request_primitive, response_primitive)
        return (response_primitive, payload)
