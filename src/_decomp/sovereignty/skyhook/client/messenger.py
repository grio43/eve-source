#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\skyhook\client\messenger.py
import datetime
import httplib
import eveProto.generated.eve_public.sovereignty.skyhook.api.requests_pb2 as SkyhookAPI
import eveProto.generated.eve_public.sovereignty.skyhook.api.admin.admin_pb2 as SkyhookAdminAPI
from eveProto import blue_to_timestamp
from publicGateway.grpc.backoff import backoff_if_error
from publicGateway.grpc.exceptions import GenericException
from semantic_version import SemanticVersion
from sovereignty.resource.client.data_types import ReagentProductionSplitDynamicData, ReagentDefinition
from sovereignty.skyhook.data_type import Skyhook, get_skyhook_object, PlanetAndSkyhookTheftVulnerabilityData, SkyhookTheftVulnerabilityData
import sovereignty.skyhook.client.errors as errors
TIMEOUT_SECONDS = 10
import logging
logger = logging.getLogger('skyhook')

class SkyhookMessenger(object):

    def __init__(self, public_gateway):
        super(SkyhookMessenger, self).__init__()
        self.public_gateway = public_gateway

    @backoff_if_error(whitelist_errors=[errors.SkyhookAccessForbiddenError])
    def get(self, skyhook_id):
        logger.info('get %s', skyhook_id)
        request = SkyhookAPI.GetRequest()
        request.skyhook.sequential = skyhook_id
        try:
            _, _, response_payload = self._send_request(request, SkyhookAPI.GetResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.FORBIDDEN:
                raise errors.SkyhookAccessForbiddenError()
            else:
                raise

        vulnerability_data = None
        if response_payload.WhichOneof('vulnerability') == 'theft_vulnerability':
            vulnerability_data = response_payload.theft_vulnerability
        workforce = None
        if response_payload.workforce.WhichOneof('available') == 'amount':
            workforce = response_payload.workforce.amount
        resource_version = SemanticVersion.from_proto(response_payload.planet_resources_definitions_version)
        return get_skyhook_object(response_payload.skyhook.sequential, response_payload.active, response_payload.reagent_simulations, response_payload.reagent_definitions, vulnerability_data, workforce, resource_version)

    @backoff_if_error()
    def get_all_local(self):
        logger.info('get_all_local')
        request = SkyhookAPI.GetAllLocalRequest()
        _, _, response_payload = self._send_request(request, SkyhookAPI.GetAllLocalResponse)
        skyhooks = []
        for skyhook in response_payload.skyhooks:
            vulnerability_data = None
            if skyhook.WhichOneof('vulnerability') == 'theft_vulnerability':
                vulnerability_data = skyhook.theft_vulnerability
            workforce = None
            if skyhook.workforce.WhichOneof('available') == 'amount':
                workforce = skyhook.workforce.amount
            resource_version = SemanticVersion.from_proto(skyhook.planet_resources_definitions_version)
            skyhooks.append(get_skyhook_object(skyhook.skyhook.sequential, skyhook.active, skyhook.reagent_simulations, skyhook.reagent_definitions, vulnerability_data, workforce, resource_version))

        return (response_payload.solar_system.sequential, skyhooks)

    @backoff_if_error()
    def get_all_corporation(self, corporation_id):
        logger.info('get_all_corporation %s', corporation_id)
        request = SkyhookAPI.GetAllByCorporationRequest()
        request.corporation.sequential = corporation_id
        _, _, response_payload = self._send_request(request, SkyhookAPI.GetAllByCorporationResponse)
        skyhooks = {}
        for skyhook in response_payload.skyhooks:
            vulnerability_data = None
            if skyhook.WhichOneof('vulnerability') == 'theft_vulnerability':
                vulnerability_data = skyhook.theft_vulnerability
            workforce = None
            if skyhook.workforce.WhichOneof('available') == 'amount':
                workforce = skyhook.workforce.amount
            resource_version = SemanticVersion.from_proto(skyhook.planet_resources_definitions_version)
            skyhooks[skyhook.skyhook.sequential] = get_skyhook_object(skyhook.skyhook.sequential, skyhook.active, skyhook.reagent_simulations, skyhook.reagent_definitions, vulnerability_data, workforce, resource_version)

        return skyhooks

    @backoff_if_error()
    def activate(self, skyhook_id):
        request = SkyhookAPI.ActivateRequest()
        request.skyhook.sequential = skyhook_id
        try:
            _, _, _ = self._send_request(request, SkyhookAPI.ActivateResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.NOT_FOUND:
                raise errors.SkyhookNotFoundError()
            elif e.response_primitive.status_code == httplib.FORBIDDEN:
                raise errors.SkyhookActivateForbiddenError
            else:
                raise

        return True

    @backoff_if_error()
    def deactivate(self, skyhook_id):
        request = SkyhookAPI.DeactivateRequest()
        request.skyhook.sequential = skyhook_id
        try:
            _, _, _ = self._send_request(request, SkyhookAPI.DeactivateResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.NOT_FOUND:
                raise errors.SkyhookNotFoundError()
            elif e.response_primitive.status_code == httplib.FORBIDDEN:
                raise errors.SkyhookDeactivateForbiddenError
            elif e.response_primitive.status_code == httplib.INTERNAL_SERVER_ERROR:
                raise errors.SkyhookDeactivateInternalError
            else:
                raise

        return True

    @backoff_if_error()
    def get_solar_systems_with_theft_vulnerable_skyhooks(self):
        request = SkyhookAPI.GetSolarSystemsWithTheftVulnerableSkyhooksRequest()
        _, _, response_payload = self._send_request(request, SkyhookAPI.GetSolarSystemsWithTheftVulnerableSkyhooksResponse)
        solar_systems = [ solar_system.sequential for solar_system in response_payload.solar_systems ]
        return solar_systems

    @backoff_if_error()
    def get_theft_vulnerable_skyhooks_in_solar_system(self, solar_system_id):
        request = SkyhookAPI.GetTheftVulnerableSkyhooksInSolarSystemRequest()
        request.solar_system.sequential = solar_system_id
        _, _, response_payload = self._send_request(request, SkyhookAPI.GetTheftVulnerableSkyhooksInSolarSystemResponse)
        skyhooks = []
        for skyhook_data in response_payload.skyhooks:
            skyhooks.append(PlanetAndSkyhookTheftVulnerabilityData(skyhook_data.skyhook.sequential, skyhook_data.planet.sequential, skyhook_data.expiry.ToDatetime()))

        return skyhooks

    @backoff_if_error()
    def admin_modify_reagents(self, skyhook_id, reagent_type, secure_amount, insecure_amount, timestamp = None):
        request = SkyhookAdminAPI.ModifyReagentsRequest()
        request.skyhook.sequential = skyhook_id
        reagent = SkyhookAdminAPI.ModifyReagentsRequest.ReagentsSimulationState()
        reagent.reagent.sequential = reagent_type
        reagent.secured_stock = secure_amount
        reagent.unsecured_stock = insecure_amount
        if timestamp is None:
            reagent.now = True
        else:
            blue_to_timestamp(timestamp, reagent.timestamp)
        request.reagents.append(reagent)
        try:
            _, _, _ = self._send_request(request, SkyhookAdminAPI.ModifyReagentsResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.NOT_FOUND:
                raise errors.SkyhookNotFoundError()
            elif e.response_primitive.status_code == httplib.FORBIDDEN:
                raise errors.SkyhookDeactivateForbiddenError
            elif e.response_primitive.status_code == httplib.INTERNAL_SERVER_ERROR:
                raise errors.SkyhookDeactivateInternalError
            elif e.response_primitive.status_code == httplib.BAD_REQUEST:
                raise errors.SkyhookBadRequestError
            else:
                raise

        return True

    def _send_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code != httplib.OK:
            raise GenericException(request_primitive=request_primitive, response_primitive=response_primitive)
        return (request_primitive, response_primitive, payload)


class FakeSkyhookMessenger(object):

    def get(self, skyhook_id):
        from sovereignty.resource.client.messenger import FakeResourceDataForPlanets
        slimItem = sm.GetService('michelle').GetBallpark().GetInvItem(skyhook_id)
        d = FakeResourceDataForPlanets().GetData(slimItem.planetID)
        reagent_simulation_list = []
        reagent_configuration_list = []
        if d and d.staticReagents:
            from sovereignty.resource.client.data_types import HarvestSplitSimulationState
            import gametime
            reagent_simulation_list.append(ReagentProductionSplitDynamicData(reagent_type_id=d.reagent_type_id, split_function_dynamic=HarvestSplitSimulationState(d.secure_amount, d.insecure_amount, gametime.GetWallclockTime())))
            reagent_configuration_list.append(ReagentDefinition(type_id=d.reagent_type_id, split_configuration=d.staticReagents.split_configuration))
        theft_vulnerability = SkyhookTheftVulnerabilityData(False, datetime.datetime.utcnow() + datetime.timedelta(hours=1), datetime.datetime.utcnow() + datetime.timedelta(hours=1))
        skyhook = Skyhook(skyhook_id, True, reagent_simulation_list, reagent_configuration_list, theft_vulnerability)
        return skyhook

    def get_all_local(self):
        allSkyhooks = []
        for _, slimItem in sm.GetService('michelle').GetBallpark().GetBallsAndItems():
            if slimItem.typeID == 81080:
                allSkyhooks.append(self.get(slimItem.itemID))

        return (session.solarsystemid2, allSkyhooks)

    def get_solar_systems_with_theft_vulnerable_skyhooks(self):
        return [30004045,
         30000872,
         30004664,
         30004956,
         30000208]

    def get_theft_vulnerable_skyhooks_in_solar_system(self, solar_system_id):
        return [PlanetAndSkyhookTheftVulnerabilityData(1000000012512L, 40013231, datetime.datetime.utcnow() + datetime.timedelta(hours=1))]

    def activate(self, skyhook_id):
        return True

    def deactivate(self, skyhook_id):
        return False
