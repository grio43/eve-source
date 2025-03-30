#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\resource\client\messenger.py
import httplib
import eveProto.generated.eve_public.sovereignty.resource.planet.api.requests_pb2 as SovResourcePlanetAPI
import eveProto.generated.eve_public.sovereignty.resource.star.api.requests_pb2 as SovResourceStarAPI
import eveProto.generated.eve_public.sovereignty.hub.api.requests_pb2 as HubAPI
from publicGateway.grpc.exceptions import GenericException
from sovereignty.client.base_external_messenger import BaseClientExternalMessenger
from sovereignty.resource.client.data_types import AvailableHubResources, ReagentDefinition, HarvestSplitConfiguration
import sovereignty.resource.client.errors as errors
from semantic_version import SemanticVersion
from sovereignty.resource.shared.planetary_resources_cache import ResourceVersionUnchanged, ResourceVersionNotFound
import logging
logger = logging.getLogger('sov_resources')
TIMEOUT_SECONDS = 10

class SkyhookNotFoundError(Exception):
    pass


class SovereigntyResourceMessenger(BaseClientExternalMessenger):

    def __init__(self, public_gateway):
        super(SovereigntyResourceMessenger, self).__init__(public_gateway)
        self.public_gateway = public_gateway

    def get_all_planet_definitions(self, current_known_version = None):
        request = SovResourcePlanetAPI.GetAllDefinitionsRequest()
        if current_known_version is not None:
            request.known_version.CopyFrom(current_known_version.to_eve_public_proto())
        else:
            request.no_known_version = True
        logger.info('get_all_planet_definitions %s', request)
        try:
            request_wrapper, response_wrapper, response_payload = self._send_request(request, SovResourcePlanetAPI.GetAllDefinitionsResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.NOT_MODIFIED:
                raise ResourceVersionUnchanged()
            raise

        logger.info('get_all_planet_definitions response %s', response_payload)
        power_by_planet, workforce_by_planet, reagents_by_planet = self._parse_definitions(response_payload.definitions)
        resource_version = SemanticVersion.from_proto(response_payload.version)
        logger.info('get_all_planet_definitions resource version %s', resource_version)
        return (power_by_planet,
         workforce_by_planet,
         reagents_by_planet,
         resource_version)

    def get_all_planet_definitions_by_version(self, requested_version):
        request = SovResourcePlanetAPI.GetDefinitionsVersionRequest()
        request.version.CopyFrom(requested_version.to_eve_public_proto())
        logger.info('get_all_planet_definitions_by_version %s', request)
        try:
            request_wrapper, response_wrapper, response_payload = self._send_request(request, SovResourcePlanetAPI.GetDefinitionsVersionResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.NOT_FOUND:
                raise ResourceVersionNotFound()
            raise

        return self._parse_definitions(response_payload.definitions)

    def _parse_definitions(self, definition_protos):
        power_by_planet = {}
        workforce_by_planet = {}
        reagents_by_planet = {}
        for definition in definition_protos:
            power_by_planet[definition.planet.sequential] = definition.power
            workforce_by_planet[definition.planet.sequential] = definition.workforce
            reagents_definitions = []
            for reagent_definition_response in definition.reagent_definitions:
                reagent_definition = ReagentDefinition.create_from_proto(reagent_definition_response.type.sequential, reagent_definition_response.definition)
                reagents_definitions.append(reagent_definition)

            reagents_by_planet[definition.planet.sequential] = reagents_definitions

        return (power_by_planet, workforce_by_planet, reagents_by_planet)

    def get_all_star_configurations(self):
        request = SovResourceStarAPI.GetAllConfigurationsRequest()
        request_wrapper, response_wrapper, response_payload = self._send_request(request, SovResourceStarAPI.GetAllConfigurationsResponse)
        power_by_star = {}
        for configuration in response_payload.configurations:
            power_by_star[configuration.star.sequential] = configuration.power

        return power_by_star

    def get_available_hub_resources(self, hubID):
        try:
            request = HubAPI.GetResourcesRequest()
            request.hub.sequential = hubID
            request_wrapper, response_wrapper, response_payload = self._send_request(request, HubAPI.GetResourcesResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.FORBIDDEN:
                raise errors.SovGetResourcesResponseForbiddenError(e)
            raise errors.SovGetResourcesResponseError(e)

        power = response_payload.power
        workforce = response_payload.workforce
        return AvailableHubResources(power.allocated, power.available, power.local_harvest, workforce.allocated, workforce.available, workforce.local_harvest)

    def _send_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code != httplib.OK:
            raise GenericException(request_primitive=request_primitive, response_primitive=response_primitive)
        return (request_primitive, response_primitive, payload)


class FakeResourceExternalMessenger(object):

    def _GetAllPlanetsInSovNull(self):
        from eve.common.script.sys.idCheckers import IsNullSecSystem
        allPlanetsInSovNull = set()
        for ssID, solarSystem in cfg.mapSystemCache.iteritems():
            if not IsNullSecSystem(ssID):
                continue
            if getattr(solarSystem, 'factionID', None):
                continue
            allPlanetsInSovNull.update(solarSystem.planetItemIDs)

        return allPlanetsInSovNull

    def _GetAllStarsInSovNull(self):
        from eve.common.script.sys.idCheckers import IsNullSecSystem, IsKnownSpaceSystem
        allStarsInSovNull = set()
        for ssID, solarSystem in cfg.mapSystemCache.iteritems():
            if not IsNullSecSystem(ssID) or not IsKnownSpaceSystem(ssID):
                continue
            if getattr(solarSystem, 'factionID', None):
                continue
            allStarsInSovNull.add(cfg.mapSolarSystemContentCache[ssID].star.id)

        return allStarsInSovNull

    def get_all_planet_definitions(self):
        allPlanetsInSovNull = self._GetAllPlanetsInSovNull()
        fakeData = FakeResourceDataForPlanets()
        power_data_by_planet = {}
        workforce_data_by_planet = {}
        reagent_data_by_planet_id = {}
        for planetID in allPlanetsInSovNull:
            planetInfo = fakeData.GetData(planetID)
            if planetInfo.power:
                power_data_by_planet[planetID] = planetInfo.power
            if planetInfo.workforce:
                workforce_data_by_planet[planetID] = planetInfo.workforce
            if planetInfo.staticReagents:
                reagent_data_by_planet_id[planetID] = [planetInfo.staticReagents]

        return (power_data_by_planet, workforce_data_by_planet, reagent_data_by_planet_id)

    def get_all_star_configurations(self):
        allStarsInSovNull = self._GetAllStarsInSovNull()
        power_by_star = {}
        for starID in allStarsInSovNull:
            power_by_star[starID] = 100

        return power_by_star

    def get_production_state(self, planetID):
        fakeData = FakeResourceDataForPlanets()
        planetInfo = fakeData.GetData(planetID)
        return planetInfo.isProducing

    def get_available_hub_resources(self, hubID):
        fakeData = FakeResources()
        return fakeData.GetData(hubID)


class FakePlanetData(object):

    def __init__(self, power, workforce, isProducing):
        self.power = power
        self.workforce = workforce
        self.reagent_type_id = None
        self.staticReagents = None
        self.isProducing = isProducing


class FakePlanetDataSplitReagents(object):

    def __init__(self, power, workforce, reagent_type_id, isProducing, secure_amount, unsecure_amount, amount_per_period, period, secure_ratio, secure_capacity, unsecure_capacity):
        splitStatic = HarvestSplitConfiguration(amount_per_period, period, secure_ratio, secure_capacity, unsecure_capacity)
        self.power = power
        self.workforce = workforce
        self.secure_amount = secure_amount
        self.insecure_amount = unsecure_amount
        self.reagent_type_id = reagent_type_id
        self.staticReagents = ReagentDefinition(reagent_type_id, splitStatic)
        self.isProducing = isProducing


class FakeResourceDataForPlanets(object):
    planetInfoByRemainder = {}
    planetInfoByRemainder[0] = FakePlanetDataSplitReagents(power=None, workforce=None, reagent_type_id=81143, isProducing=True, secure_amount=40, amount_per_period=2001, period=161, secure_ratio=50, secure_capacity=501, unsecure_amount=60, unsecure_capacity=601)
    planetInfoByRemainder[1] = FakePlanetData(power=100, workforce=0, isProducing=True)
    planetInfoByRemainder[2] = FakePlanetData(power=0, workforce=500, isProducing=True)
    planetInfoByRemainder[3] = FakePlanetDataSplitReagents(power=None, workforce=None, reagent_type_id=81144, isProducing=True, secure_amount=10, amount_per_period=1, period=10, secure_ratio=60, secure_capacity=50, unsecure_amount=100, unsecure_capacity=1001)
    planetInfoByPlanetID = {}
    planetInfoByPlanetID[40030269] = planetInfoByRemainder[0]
    planetInfoByPlanetID[40239111] = planetInfoByRemainder[0]
    planetInfoByPlanetID[40239179] = planetInfoByRemainder[3]
    planetInfoByPlanetID[40239204] = planetInfoByRemainder[2]
    planetInfoByPlanetID[40239109] = planetInfoByRemainder[1]
    planetInfoByPlanetID[40239114] = planetInfoByRemainder[1]
    planetInfoByPlanetID[40267883] = FakePlanetData(power=0, workforce=500, isProducing=True)
    planetInfoByPlanetID[40267600] = FakePlanetData(power=0, workforce=400, isProducing=True)
    planetInfoByPlanetID[40267943] = FakePlanetData(power=0, workforce=375, isProducing=True)
    planetInfoByPlanetID[40267881] = FakePlanetData(power=0, workforce=200, isProducing=True)
    planetInfoByPlanetID[40267593] = FakePlanetData(power=0, workforce=150, isProducing=True)
    planetInfoByPlanetID[40267589] = FakePlanetData(power=0, workforce=100, isProducing=True)
    planetInfoByPlanetID[40267590] = FakePlanetData(power=0, workforce=50, isProducing=True)
    planetInfoByPlanetID[40267886] = FakePlanetData(power=100, workforce=0, isProducing=True)
    planetInfoByPlanetID[40267909] = FakePlanetData(power=50, workforce=0, isProducing=True)
    planetInfoByPlanetID[40267915] = FakePlanetData(power=25, workforce=0, isProducing=True)
    planetInfoByPlanetID[40267940] = planetInfoByRemainder[3]
    planetInfoByPlanetID[40267586] = planetInfoByRemainder[3]
    planetInfoByPlanetID[40267597] = planetInfoByRemainder[0]
    planetInfoByPlanetID[40267585] = planetInfoByRemainder[0]

    def GetData(self, planetID):
        if planetID in self.planetInfoByPlanetID:
            return self.planetInfoByPlanetID[planetID]
        return self.planetInfoByRemainder[planetID % 4]


class FakeResources(object):
    resourcesByRemainder = {}
    resourcesByRemainder[0] = (100, 5000, 2000, 15000)
    resourcesByRemainder[1] = (10, 25000, 0, 5000)
    resourcesByRemainder[2] = (500, 1000, 10, 500)
    resourcesByRemainder[3] = (220, 7500, 100, 1000)
    resourcesByHubID = {1016094683696L: resourcesByRemainder[0],
     1016094694774L: resourcesByRemainder[0]}

    def GetData(self, hubID):
        if hubID in self.resourcesByHubID:
            return self.resourcesByHubID[hubID]
        return self.resourcesByRemainder[hubID % 4]
