#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\factionwarfare\activity\client\requestMessenger.py
import logging
from eveProto.generated.eve_public.faction.activity.activity_pb2 import GetSolarSystemScoresRequest
from eveProto.generated.eve_public.faction.activity.activity_pb2 import GetSolarSystemScoresResponse
from eveProto.generated.eve_public.solarsystem.solarsystem_pb2 import Identifier as SolarSystemId
from factionwarfare.activity import SolarSystemScores, Score
from publicGateway.grpc.exceptions import GenericException
TIMEOUT_SECONDS = 10
logger = logging.getLogger(__name__)

class PublicRequestsMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get_solar_system_scores(self, solar_system_id):
        request = GetSolarSystemScoresRequest(solar_system=SolarSystemId(sequential=solar_system_id))
        request_wrapper, response_wrapper, response_payload = self.blocking_request(request, GetSolarSystemScoresResponse)
        if response_wrapper.status_code != 200:
            raise GenericException(request_primitive=request_wrapper, response_primitive=response_wrapper)
        scores = []
        for score in response_payload.scores:
            scores.append(Score(faction_id=score.faction.sequential, contribution=score.contribution, floor=score.floor))

        solar_system_scores = SolarSystemScores(solar_system_id=response_payload.solar_system.sequential, scores=scores)
        return solar_system_scores

    def blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        return (request_primitive, response_primitive, payload)
