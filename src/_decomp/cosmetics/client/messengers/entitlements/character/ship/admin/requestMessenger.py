#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\entitlements\character\ship\admin\requestMessenger.py
from eveProto.generated.eve_public.entitlement.character.ship.admin import corplogo_pb2 as admin_corplogo_pb2
from eveProto.generated.eve_public.entitlement.character.ship.admin import alliancelogo_pb2 as admin_alliancelogo_pb2
from eveProto.generated.eve_public.entitlement.character.ship import corplogo_pb2
from eveProto.generated.eve_public.entitlement.character.ship import alliancelogo_pb2
from eveProto.generated.eve_public.character import character_pb2
from eveProto.generated.eve_public.ship import ship_type_pb2
from publicGateway.grpc import requestBroker
TIMEOUT_SECONDS = 10

class PublicEntitlementsAdministrativeRequestsMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def grant_corp_logo(self, character_id, ship_type_id):
        request = admin_corplogo_pb2.GrantRequest(entitlement=corplogo_pb2.Identifier(character=character_pb2.Identifier(sequential=character_id), ship_type=ship_type_pb2.Identifier(sequential=ship_type_id)))
        request_primitive, response_channel = self.send_async_request(request, admin_corplogo_pb2.GrantResponse)
        return requestBroker.ResponseChannel(request_primitive, response_channel)

    def grant_alliance_logo(self, character_id, ship_type_id):
        request = admin_alliancelogo_pb2.GrantRequest(entitlement=alliancelogo_pb2.Identifier(character=character_pb2.Identifier(sequential=character_id), ship_type=ship_type_pb2.Identifier(sequential=ship_type_id)))
        request_primitive, response_channel = self.send_async_request(request, admin_alliancelogo_pb2.GrantResponse)
        return requestBroker.ResponseChannel(request_primitive, response_channel)

    def revoke_corp_logo(self, character_id, ship_type_id):
        request = admin_corplogo_pb2.RevokeRequest(entitlement=corplogo_pb2.Identifier(character=character_pb2.Identifier(sequential=character_id), ship_type=ship_type_pb2.Identifier(sequential=ship_type_id)))
        request_primitive, response_channel = self.send_async_request(request, admin_corplogo_pb2.RevokeResponse)
        return requestBroker.ResponseChannel(request_primitive, response_channel)

    def revoke_alliance_logo(self, character_id, ship_type_id):
        request = admin_alliancelogo_pb2.RevokeRequest(entitlement=alliancelogo_pb2.Identifier(character=character_pb2.Identifier(sequential=character_id), ship_type=ship_type_pb2.Identifier(sequential=ship_type_id)))
        request_primitive, response_channel = self.send_async_request(request, admin_alliancelogo_pb2.RevokeResponse)
        return requestBroker.ResponseChannel(request_primitive, response_channel)

    def send_async_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, TIMEOUT_SECONDS)
        return (request_primitive, response_channel)
