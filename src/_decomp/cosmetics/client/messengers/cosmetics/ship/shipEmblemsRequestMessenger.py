#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipEmblemsRequestMessenger.py
import logging
from eveProto.generated.eve_public.cosmetic.ship.logo.logo_pb2 import DisplayRequest, DisplayResponse
from eveProto.generated.eve_public.cosmetic.ship.logo.logo_pb2 import ClearRequest, ClearResponse
from eveProto.generated.eve_public.cosmetic.ship.logo.logo_pb2 import Identifier as ShipLogoID
from eveProto.generated.eve_public.cosmetic.ship.logo.logo_pb2 import Attributes as ShipLogo
from eveProto.generated.eve_public.cosmetic.ship.logo.logo_pb2 import Alliance as AllianceLogo
from eveProto.generated.eve_public.cosmetic.ship.logo.logo_pb2 import Corporation as CorporationLogo
from eveProto.generated.eve_public.ship.ship_pb2 import Identifier as ShipID
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException, UnpackException
TIMEOUT_SECONDS = 180
logger = logging.getLogger(__name__)

class MessengerException(Exception):
    pass


class PublicShipEmblemsRequestsMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def display_corporation_logo(self, ship_id, logo_slot):
        request = DisplayRequest(id=ShipLogoID(ship=ShipID(sequential=ship_id), index=logo_slot), attr=ShipLogo(corporation=CorporationLogo()))
        primitive, _ = self.blocking_request(request, DisplayResponse)

    def display_alliance_logo(self, ship_id, logo_slot):
        request = DisplayRequest(id=ShipLogoID(ship=ShipID(sequential=ship_id), index=logo_slot), attr=ShipLogo(alliance=AllianceLogo()))
        primitive, _ = self.blocking_request(request, DisplayResponse)

    def clear_logo(self, ship_id, logo_slot):
        request = ClearRequest(logo=ShipLogoID(ship=ShipID(sequential=ship_id), index=logo_slot))
        primitive, _ = self.blocking_request(request, ClearResponse)

    def blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code != 200:
            raise GenericException(request_primitive, response_primitive)
        return (response_primitive, payload)
