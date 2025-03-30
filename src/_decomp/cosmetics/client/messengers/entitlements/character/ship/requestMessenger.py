#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\entitlements\character\ship\requestMessenger.py
import logging
from publicGateway.grpc.exceptions import GenericException
from cosmetics.client.messengers.entitlements.character.ship import new_entitlement_from_type
from eveProto.generated.eve_public.entitlement.character.character_pb2 import GetAllRequest, GetAllResponse
TIMEOUT_SECONDS = 10
logger = logging.getLogger(__name__)

class PublicEntitlementsRequestsMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get_owned_ship_logos(self):
        owned_ship_logos = []
        request = GetAllRequest()
        request_wrapper, response_wrapper, response_payload = self.blocking_request(request, GetAllResponse)
        if response_wrapper.status_code != 200:
            raise GenericException(request_primitive=request_wrapper, response_primitive=response_wrapper)
        for logo_entitlement in response_payload.entitlements:
            owned_ship_logos.append(new_entitlement_from_type(logo_entitlement))

        return owned_ship_logos

    def blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        return (request_primitive, response_primitive, payload)
