#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\structures\requestMessenger.py
import logging
import uuid
import blue
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
import eveProto.generated.eve_public.cosmetic.structure.paintwork.api.api_pb2 as api
from eveProto.generated.eve_public.structure.structure_pb2 import Identifier as StructureIdentifier
from eveProto.generated.eve_public.solarsystem.solarsystem_pb2 import Identifier as SolarSystemIdentifier
from cosmetics.client.structures.fitting import create_structure_paintwork_from_proto_slot_config
import cosmetics.client.messengers.entitlements.corporation.structure.qaconst as qa
from publicGateway.grpc.exceptions import GenericException
TIMEOUT_SECONDS = 10
logger = logging.getLogger(__name__)

class PublicRequestsMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get_request(self, structure_id, solar_system_id):
        if session and session.role & ROLE_PROGRAMMER:
            if qa.FORCE_STRUCTURE_GET_COSMETIC_STATE_DELAY > 0:
                blue.synchro.Sleep(qa.FORCE_STRUCTURE_GET_COSMETIC_STATE_DELAY * 1000)
            if qa.FORCE_STRUCTURE_GET_COSMETIC_STATE_ERRORS:
                raise Exception
        request = api.GetRequest(structure=StructureIdentifier(sequential=structure_id), solar_system=SolarSystemIdentifier(sequential=solar_system_id))
        response_primitive, response_payload = self.blocking_request(request, api.GetResponse)
        if response_payload is None:
            return (None, None)
        license_id = uuid.UUID(bytes=response_payload.license.uuid)
        paintwork = create_structure_paintwork_from_proto_slot_config(response_payload.paintwork)
        return (license_id, paintwork)

    def get_all_in_solar_system_request(self):
        if session and session.role & ROLE_PROGRAMMER:
            if qa.FORCE_STRUCTURE_GET_COSMETIC_STATE_DELAY > 0:
                blue.synchro.Sleep(qa.FORCE_STRUCTURE_GET_COSMETIC_STATE_DELAY * 1000)
            if qa.FORCE_STRUCTURE_GET_COSMETIC_STATE_ERRORS:
                raise Exception
        request = api.GetAllInSolarSystemRequest()
        response_primitive, response_payload = self.blocking_request(request, api.GetAllInSolarSystemResponse)
        if response_payload is None:
            return {}
        results = {}
        for structure_paintwork in response_payload.paintworks:
            results[structure_paintwork.structure.sequential] = create_structure_paintwork_from_proto_slot_config(structure_paintwork.paintwork)

        return results

    def blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code == 404:
            return (response_primitive, None)
        if response_primitive.status_code != 200:
            raise GenericException(request_primitive, response_primitive)
        return (response_primitive, payload)
