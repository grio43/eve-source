#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\client\base_external_messenger.py
import httplib
from publicGateway.grpc.exceptions import GenericException
DEFAULT_TIMEOUT_SECONDS = 10

class BaseClientExternalMessenger(object):

    def __init__(self, public_gateway, timeout_seconds = DEFAULT_TIMEOUT_SECONDS):
        self.public_gateway = public_gateway
        self.timeout_seconds = timeout_seconds

    def _send_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, self.timeout_seconds)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code != httplib.OK:
            raise GenericException(request_primitive=request_primitive, response_primitive=response_primitive)
        return (request_primitive, response_primitive, payload)
