#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\recommendation\message_bus\recommendationMessenger.py
import httplib
import logging
import uthread2
from eve.client.script.ui.shared.recommendation.const import UPDATE_TIMEOUT_SECONDS
from eveProto.generated.eve_public.app.eveonline.operation.recommendation.recommendation_pb2 import Accepted, Dismissed
from eveProto.generated.eve_public.app.eveonline.operation.recommendation.ui_pb2 import Displayed
from eveProto.generated.eve_public.operation.recommendation.recommendation_pb2 import GetRequest, GetResponse
from stackless_response_router.exceptions import TimeoutException
logger = logging.getLogger(__name__)

class RecommendationMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def accepted(self, operation_id, journey_id):
        event = Accepted()
        event.operation.sequential = int(operation_id)
        self.public_gateway.publish_event_payload(event, journey_id)

    def dismissed(self, operation_id, journey_id):
        event = Dismissed()
        event.operation.sequential = int(operation_id)
        self.public_gateway.publish_event_payload(event, journey_id)

    def displayed(self, operation_id, journey_id):
        event = Displayed()
        event.operation.sequential = int(operation_id)
        self.public_gateway.publish_event_payload(event, journey_id)

    def request_recommendations(self, amount, allow_old, response_function, timeout_function):
        request = GetRequest()
        request.amount = amount
        request.allow_old = allow_old

        def _response_handler(primitive, payload):
            if primitive.status_code != httplib.OK:
                logger.error('unexpected error when requesting recommendations - statusCode: %d, statusMessage: %s', primitive.status_code, primitive.status_message)
            else:
                response_function(payload.operation_recommendations)

        def _timeout_handler(timeout_exception):
            logger.error('request_recommendations timed out: %s' % timeout_exception, exc_info=True)
            timeout_function()

        uthread2.StartTasklet(self._send_request_and_wait_for_response, request, GetResponse, _response_handler, _timeout_handler)

    def _send_request_and_wait_for_response(self, request, expected_response_class, response_handler, timeout_handler = None):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, expected_response_class, UPDATE_TIMEOUT_SECONDS)
        try:
            response_primitive, payload = response_channel.receive()
            response_handler(response_primitive, payload)
        except TimeoutException as e:
            if timeout_handler is not None:
                timeout_handler(e)
