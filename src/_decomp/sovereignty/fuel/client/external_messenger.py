#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\fuel\client\external_messenger.py
import httplib
from eveProto import timestamp_to_blue
from eveProto.generated.eve_public.sovereignty.hub.fuel.api import requests_pb2
from eveProto.generated.eve_public.sovereignty.hub.hub_pb2 import Identifier as HubIdentifier
from publicGateway.grpc.exceptions import GenericException
from sovereignty.client.base_external_messenger import BaseClientExternalMessenger
from eveProto.generated.eve_public.inventory.generic_item_pb2 import Identifier as ItemID
import sovereignty.fuel.client.errors as errors
from sovereignty.fuel.client.data_types import Fuel

class SovFuelExternalMessenger(BaseClientExternalMessenger):

    def get(self, hub_id):
        try:
            request = requests_pb2.GetRequest(hub=HubIdentifier(sequential=hub_id))
            request_wrapper, response_wrapper, response_payload = self._send_request(request, requests_pb2.GetResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.FORBIDDEN:
                raise errors.SovFuelGetLevelsForbiddenError(e)
            if e.response_primitive.status_code == httplib.INTERNAL_SERVER_ERROR:
                raise errors.SovFuelGetLevelInternalError(e)
            raise errors.SovFuelGetLevelsError(e)

        fuels = response_payload.fuels
        last_updated = timestamp_to_blue(response_payload.last_updated)
        fuel_by_type_id = {x.fuel_type.sequential:Fuel(x.fuel_type.sequential, x.amount, x.burned_per_hour, last_updated) for x in fuels}
        return fuel_by_type_id

    def add_fuel(self, fuel_item_id, amount, hub_id):
        try:
            request = requests_pb2.AddRequest(fuel_item=ItemID(sequential=fuel_item_id), amount=amount, hub=HubIdentifier(sequential=hub_id))
            request_wrapper, response_wrapper, response_payload = self._send_request(request, requests_pb2.AddResponse)
        except GenericException as e:
            if e.response_primitive.status_code == httplib.FORBIDDEN:
                raise errors.SovFuelAddRequestForbiddenError(e)
            if e.response_primitive.status_code == httplib.NOT_FOUND:
                raise errors.SovFuelAddRequestNotFoundError(e)
            if e.response_primitive.status_code == httplib.INTERNAL_SERVER_ERROR:
                raise errors.SovFuelAddRequestInternalError(e)
            raise errors.SovFuelAddRequestError(e)


class FakseSovFuelExternalMessenger(object):

    def get(self, hub_id):
        from datetimeutils.RFC3339 import datetime_to_blue
        last_updated = datetime_to_blue('2000-01-01T00:00:00Z')
        return {81144: Fuel(81144, 5123, 10, last_updated),
         81143: Fuel(81143, 53, 15, last_updated)}

    def add_fuel(self, fuel_item_id, amount, hub_id):
        print 'fuel added'
