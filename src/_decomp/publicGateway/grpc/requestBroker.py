#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\grpc\requestBroker.py
import logging
import time
import uthread2
import uuid
from datetime import datetime
from eveProto import get_grpc_module
from eveProto.generated.eve_public.public_pb2 import Request as EvePublicRequestProto
from eveProto.module_states import channel_states, broker_states
from eveProto.monolith_converters import datetime_to_timestamp
from publicGateway.grpc.streamLogger import StreamLogger
from stackless_response_router import StacklessResponseRouter as Router
from publicGateway.grpc.spanManager import SpanManager
from publicGateway.grpc import exceptions
RESPONSE_POLL_INTERVAL_SECONDS = 1
RESPONSE_SLEEP_SECONDS = 0.001
RESPONSE_BATCH_SIZE = 100

class RequestBroker(object):

    def __init__(self, connection, tenant, origin, application_instance_uuid):
        self.logger = logging.getLogger(__name__)
        self.native_broker = self.get_native_broker()
        self.native_broker.set_connection(connection)
        self.stream_logger = StreamLogger(self.logger, self.native_broker)
        self.tenant = tenant
        self.origin = origin
        self.application_instance_uuid = application_instance_uuid
        self.authenticated_user = None
        self.authorized_character = None
        self.ping_active = False
        self.cached_rtt = -1
        self.span_manager = SpanManager()
        self.router = Router(span_manager=self.span_manager)
        self._buffered_user_requests = []
        self._buffered_character_requests = []
        uthread2.StartTasklet(self.consume_responses)

    def get_native_broker(self):
        module = get_grpc_module()
        if module is not None:
            self.logger.info('creating request cqrsBroker')
            return module.CqrsBroker()

    def new_eve_public_request(self):
        epr = EvePublicRequestProto()
        epr_correlation_uuid = uuid.uuid4()
        epr.correlation_uuid = epr_correlation_uuid.bytes
        datetime_to_timestamp(datetime.utcnow(), epr.issued)
        epr.external_origin = self.origin
        epr.application_instance_uuid = self.application_instance_uuid.bytes
        epr.authoritative_context.tenant = self.tenant
        if self.authenticated_user is None:
            epr.authoritative_context.no_authenticated_user = True
        else:
            epr.authoritative_context.authenticated_user.sequential = self.authenticated_user
        if self.authorized_character is None:
            epr.authoritative_context.no_active_identity = True
        else:
            epr.authoritative_context.identity.character.sequential = self.authorized_character
        return epr

    def set_active_character_id(self, character_id):
        self.authorized_character = character_id
        if self.authorized_character is not None and len(self._buffered_character_requests):
            uthread2.StartTasklet(self._update_and_send_buffered_character_requests)

    def set_authenticated_user_id(self, user_id):
        self.authenticated_user = user_id
        if self.authenticated_user is not None and len(self._buffered_user_requests):
            uthread2.StartTasklet(self._update_and_send_buffered_user_requests)

    def connect(self):
        if self.connection_config:
            self.connection_config.connect()

    def get_details(self):
        if self.native_broker is None:
            return {'native_broker': 'None'}
        last_status_code = -1
        last_status_code_stream_id = -1
        breadcrumbs = self.stream_logger.get_log_breadcrumbs()
        if len(breadcrumbs) > 0:
            last_status_code_stream_id = breadcrumbs[-1][0]
            last_status_code = breadcrumbs[-1][1]
        return {'broker_state': broker_states.get(self.native_broker.get_broker_state(), {'Name': 'undefined'})['Name'],
         'channel_state': channel_states.get(self.native_broker.get_channel_state(), {'Name': 'undefined'})['Name'],
         'pending_requests': self.native_broker.num_pending_requests(),
         'pending_responses': self.native_broker.num_responses_ready(),
         'connection_id': self.native_broker.get_connection_id(),
         'stream_id': self.native_broker.get_stream_id(),
         'stream_status_log_breadcrumbs': breadcrumbs,
         'last_status_code_stream_id': last_status_code_stream_id,
         'last_status_code': last_status_code}

    def get_rtt(self):
        if self.ping_active:
            return self.cached_rtt
        self.ping_active = True
        if self.native_broker is None:
            self.ping_active = False
            return -1
        self.native_broker.ping()
        start = time.time()
        while self.native_broker.ping_in_progress() is True:
            uthread2.Sleep(0.1)
            if time.time() - start > RESPONSE_POLL_INTERVAL_SECONDS:
                self.cached_rtt = -1
                self.ping_active = False
                return self.cached_rtt

        self.cached_rtt = self.native_broker.ping_result_millis()
        self.ping_active = False
        return self.cached_rtt

    def consume_responses(self):
        while True:
            uthread2.sleep(RESPONSE_SLEEP_SECONDS)
            if not self.native_broker:
                return
            responses = self.native_broker.get_responses(RESPONSE_BATCH_SIZE)
            for response_tuple in responses:
                _, response, arrival_time = response_tuple
                self.span_manager.end_request_trace(response, arrival_time.ToDatetime())
                self.router.handle_response(response.correlation_uuid, response)

            self.router.handle_request_timeouts()

    def send_character_request(self, eve_public_request_payload, expected_response_class, timeout_seconds):
        eve_public_request = self.new_eve_public_request()
        response_channel = self.router.add_response_handler(eve_public_request, expected_response_class, timeout_seconds)
        if self.authorized_character is None:
            self._buffered_character_requests.append((eve_public_request, eve_public_request_payload))
        else:
            self._send_request(eve_public_request, eve_public_request_payload)
        return (eve_public_request, response_channel)

    def send_user_request(self, eve_public_request_payload, expected_response_class, timeout_seconds):
        eve_public_request = self.new_eve_public_request()
        response_channel = self.router.add_response_handler(eve_public_request, expected_response_class, timeout_seconds)
        if self.authenticated_user is None:
            self._buffered_user_requests.append((eve_public_request, eve_public_request_payload))
        else:
            self._send_request(eve_public_request, eve_public_request_payload)
        return (eve_public_request, response_channel)

    def _send_request(self, eve_public_request, eve_public_request_payload):
        try:
            self.span_manager.start_request_trace(eve_public_request, eve_public_request_payload)
            self.native_broker.send_request(eve_public_request, eve_public_request_payload)
        except Exception as e:
            payload_name = 'unknown'
            if eve_public_request_payload:
                payload_name = eve_public_request_payload.DESCRIPTOR.full_name
            self.logger.exception('failed to send request', extra={'payload.name': payload_name})
            raise e

    def _update_and_send_buffered_user_requests(self):
        for request_tuple in self._buffered_user_requests:
            request, payload = request_tuple
            request.authoritative_context.authenticated_user.sequential = self.authenticated_user
            self._send_request(request, payload)

    def _update_and_send_buffered_character_requests(self):
        for request_tuple in self._buffered_character_requests:
            request, payload = request_tuple
            request.authoritative_context.authenticated_user.sequential = self.authenticated_user
            request.authoritative_context.identity.character.sequential = self.authorized_character
            self._send_request(request, payload)


class ResponseChannel(object):

    def __init__(self, request_primitive, channel):
        self.request_primitive = request_primitive
        self.channel = channel
        self._open = True

    def receive(self):
        if not self._open:
            raise IOError("You've already used this request channel. Make a new messenger request!")
        response_primitive, payload = self.channel.receive()
        self._open = False
        if response_primitive.status_code != 200:
            raise exceptions.GenericException(request_primitive=self.request_primitive, response_primitive=response_primitive)
        return (response_primitive, payload)
