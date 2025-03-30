#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\workforce\client\external_messenger.py
from publicGateway.grpc.exceptions import GenericException
from sovereignty.client.base_external_messenger import BaseClientExternalMessenger
import httplib
from eveProto.generated.eve_public.sovereignty.hub.workforce.api import requests_pb2
from eveProto.generated.eve_public.sovereignty.hub.hub_pb2 import Identifier as HubIdentifier
from eveProto.generated.eve_public.sovereignty.hub.workforce.workforce_pb2 import Configuration, ImportConfiguration, ExportConfiguration
from eveProto.generated.eve_public.solarsystem.solarsystem_pb2 import Identifier as SolarSystemID
import sovereignty.workforce.client.errors as errors
from sovereignty.workforce.client.data_types import WorkforceConfiguration, WorkforceState, WorkforceNetworkedHub
MODE_IDLE = 1
MODE_IMPORT = 2
MODE_EXPORT = 3
MODE_TRANSIT = 4

class WorkforceExternalMessenger(BaseClientExternalMessenger):

    def get_configuration(self, hub_id):
        try:
            request = requests_pb2.GetConfigurationRequest(hub=HubIdentifier(sequential=hub_id))
            request_wrapper, response_wrapper, response_payload = self._send_request(request, requests_pb2.GetConfigurationResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.FORBIDDEN:
                raise errors.SovWorkforceGetConfigForbiddenError(e)
            if e.response_primitive.status_code == httplib.INTERNAL_SERVER_ERROR:
                raise errors.SovWorkforceGetConfigInternalError(e)
            raise errors.SovWorkforceGetConfigError(e)

        configuration = response_payload.configuration
        workforceConfiguration = WorkforceConfiguration.create_from_proto(hub_id, configuration)
        return workforceConfiguration

    def configure(self, hub_id, workforceConfiguration):
        try:
            newConfiguration = self._get_new_configuration(workforceConfiguration)
            if newConfiguration:
                request = requests_pb2.ConfigureRequest(hub=HubIdentifier(sequential=hub_id), configuration=newConfiguration)
                request_wrapper, response_wrapper, response_payload = self._send_request(request, requests_pb2.ConfigureResponse)
                return True
        except GenericException as e:
            if e.response_primitive.status_code == httplib.FORBIDDEN:
                raise errors.SovWorkforceConfigureForbiddenError(e)
            if e.response_primitive.status_code == httplib.INTERNAL_SERVER_ERROR:
                raise errors.SovWorkforceConfigureInternalError(e)
            raise errors.SovWorkforceConfigureError(e)

    def _get_new_configuration(self, workforceConfiguration):
        import_configuration = workforceConfiguration.import_configuration
        if import_configuration:
            source_system_ids = import_configuration.source_system_ids
            source_system_ids_list = sorted(source_system_ids)
            importSources = [ ImportConfiguration.Source(source=SolarSystemID(sequential=x)) for x in source_system_ids_list ]
            return Configuration(import_settings=ImportConfiguration(sources=importSources))
        export_configuration = workforceConfiguration.export_configuration
        if export_configuration:
            if export_configuration.destination_system_id is None:
                return Configuration(export_settings=ExportConfiguration(no_destination=True, amount=export_configuration.amount))
            else:
                return Configuration(export_settings=ExportConfiguration(destination_system=SolarSystemID(sequential=export_configuration.destination_system_id), amount=export_configuration.amount))
        inactive = workforceConfiguration.inactive
        if inactive:
            return Configuration(inactive=True)
        transit = workforceConfiguration.transit
        if transit:
            return Configuration(transit=True)

    def get_state(self, hub_id):
        try:
            request = requests_pb2.GetStateRequest(hub=HubIdentifier(sequential=hub_id))
            request_wrapper, response_wrapper, response_payload = self._send_request(request, requests_pb2.GetStateResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.FORBIDDEN:
                raise errors.SovWorkforceGetStateForbiddenError(e)
            if e.response_primitive.status_code == httplib.INTERNAL_SERVER_ERROR:
                raise errors.SovWorkforceGetStateInternalError(e)
            raise errors.SovWorkforceGetStateError(e)

        state = response_payload.state
        workforceState = WorkforceState.create_from_proto(hub_id, state)
        return workforceState

    def get_networkable_hubs(self, hub_id):
        try:
            request = requests_pb2.GetNetworkableHubsRequest(hub=HubIdentifier(sequential=hub_id))
            request_wrapper, response_wrapper, response_payload = self._send_request(request, requests_pb2.GetNetworkableHubsResponse)
        except GenericException as e:
            raise errors.SovWorkforceGetNetworkableHubsError(e)

        hubs = response_payload.hubs
        networkedHubs = [ WorkforceNetworkedHub.create_from_proto(x.hub.sequential, x.system.sequential, x.configuration, x.state) for x in hubs ]
        return networkedHubs


class FakeWorkforceExternalMessenger(BaseClientExternalMessenger):
    workforceByHubID = {}

    def _GetConfiguration(self, hubID):
        if hubID in self.workforceByHubID:
            return self.workforceByHubID[hubID]
        rem = hubID % 2
        if rem == 0:
            return WorkforceConfiguration(hubID, transit=True)
        return WorkforceConfiguration(hubID, inactive=True)

    def get_configuration(self, hub_id):
        return self._GetConfiguration(hub_id)

    def configure(self, hub_id, workforceConfiguration):
        self.workforceByHubID[hub_id] = workforceConfiguration
        return True

    def get_state(self, hub_id):
        pass
