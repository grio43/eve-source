#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipSkinStateRequestMessenger.py
from cosmetics.client.ships.skins.live_data.ship_skin_state import ShipSkinState
from publicGateway.grpc.exceptions import GenericException
from eveProto.generated.eve_public.cosmetic.ship.api.request_pb2 import GetRequest, GetResponse, GetAllInBubbleRequest, GetAllInBubbleResponse
from eveProto.generated.eve_public.ship.ship_pb2 import Identifier as ShipIdentifier
from logging import getLogger
logger = getLogger(__name__)
TIMEOUT_SECONDS = 3

class ShipSkinStateRequestsMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get_request(self, ship_instance_id):
        request = GetRequest(ship=ShipIdentifier(sequential=ship_instance_id))
        response_primitive, response_payload = self._blocking_request(request, GetResponse)
        skin_state = ShipSkinState.build_from_proto(response_payload.state) if response_payload is not None else None
        logger.info('SKIN STATES - GetRequest for ship %s. Response is %s' % (ship_instance_id, skin_state))
        return skin_state

    def get_all_in_bubble_request(self):
        request = GetAllInBubbleRequest()
        response_primitive, response_payload = self._blocking_request(request, GetAllInBubbleResponse)
        if response_payload is None:
            return
        logger.info('SKIN STATES - GetAllInBubbleRequest. Response contains %s skin states' % len(response_payload.states) if response_payload is not None else 0)
        return [ ShipSkinState.build_from_proto(x) for x in response_payload.states ]

    def _blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code == 404:
            return (response_primitive, None)
        if response_primitive.status_code != 200:
            raise GenericException(request_primitive, response_primitive)
        return (response_primitive, payload)
