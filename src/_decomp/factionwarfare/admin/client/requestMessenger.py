#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\factionwarfare\admin\client\requestMessenger.py
import logging
from eveProto.generated.eve_public.faction.activity.admin_pb2 import IncrementContributionScoreRequest
from eveProto.generated.eve_public.faction.activity.admin_pb2 import IncrementContributionScoreResponse
from eveProto.generated.eve_public.faction.activity.admin_pb2 import SetContributionScoreRequest
from eveProto.generated.eve_public.faction.activity.admin_pb2 import SetContributionScoreResponse
from eveProto.generated.eve_public.faction.faction_pb2 import Identifier as FactionId
from eveProto.generated.eve_public.solarsystem.solarsystem_pb2 import Identifier as SolarSystemId
from publicGateway.grpc.exceptions import GenericException
TIMEOUT_SECONDS = 10
logger = logging.getLogger(__name__)

class PublicRequestsMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def increment_contribution_score(self, solar_system_id, faction_id, adjustment):
        request = IncrementContributionScoreRequest(target_system=SolarSystemId(sequential=solar_system_id), target_faction=FactionId(sequential=faction_id), adjustment=adjustment)
        request_wrapper, response_wrapper, response_payload = self.blocking_request(request, IncrementContributionScoreResponse)
        if response_wrapper.status_code != 200:
            raise GenericException(request_primitive=request_wrapper, response_primitive=response_wrapper)

    def set_contribution_score(self, solar_system_id, faction_id, override):
        request = SetContributionScoreRequest(target_system=SolarSystemId(sequential=solar_system_id), target_faction=FactionId(sequential=faction_id), override=override)
        request_wrapper, response_wrapper, response_payload = self.blocking_request(request, SetContributionScoreResponse)
        if response_wrapper.status_code != 200:
            raise GenericException(request_primitive=request_wrapper, response_primitive=response_wrapper)

    def blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        return (request_primitive, response_primitive, payload)
