#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\grpc\eventPublisher.py
import logging
import uthread2
import time
from eveProto import get_grpc_module
from eveProto.module_states import channel_states, publisher_states
from publicGateway.events.event import Event
from publicGateway.grpc.streamLogger import StreamLogger
from publicGateway.grpc.tracing import PublishEventTracer

class EventPublisher(object):

    def __init__(self, connection, tenant, origin, application_instance_uuid_bytes):
        self.logger = logging.getLogger(__name__)
        self.native_publisher = self.get_native_publisher()
        self.native_publisher.set_connection(connection)
        self.cached_rtt = -1
        self.ping_active = False
        self.active_character = None
        self.authenticated_user = None
        self.tenant = tenant
        self.origin = origin
        self.application_instance_uuid_bytes = application_instance_uuid_bytes
        self.stream_logger = StreamLogger(self.logger, self.native_publisher)

    def get_details(self):
        if self.native_publisher is None:
            return {'native_publisher': 'None'}
        return {'publisher': publisher_states.get(self.native_publisher.get_publisher_state(), {'Name': 'undefined'})['Name'],
         'channel': channel_states.get(self.native_publisher.get_channel_state(), {'Name': 'undefined'})['Name'],
         'pending_messages': str(self.native_publisher.num_pending_messages()),
         'connection_id': str(self.native_publisher.get_connection_id())}

    def get_native_publisher(self):
        grpc_module = get_grpc_module()
        if grpc_module is not None:
            self.logger.info('creating new event publisher')
            return grpc_module.EventPublisher()

    def get_rtt(self):
        if self.ping_active:
            return self.cached_rtt
        self.ping_active = True
        if self.native_publisher is None:
            self.ping_active = False
            return -1
        self.native_publisher.ping()
        start = time.time()
        while self.native_publisher.ping_in_progress() is True:
            uthread2.Sleep(0.1)
            if time.time() - start > 1:
                self.cached_rtt = -1
                self.ping_active = False
                return self.cached_rtt

        self.cached_rtt = self.native_publisher.ping_result_millis()
        self.ping_active = False
        return self.cached_rtt

    def set_active_character_id(self, character_id):
        self.active_character = character_id

    def set_authenticated_user_id(self, user_id):
        self.authenticated_user = user_id

    def new_event(self, journey_id = None):
        new_event = Event()
        new_event.set_external_origin(self.origin)
        new_event.set_active_character(self.active_character)
        new_event.set_authenticated_user(self.authenticated_user)
        new_event.set_tenant(self.tenant)
        new_event.set_application_instance_uuid(self.application_instance_uuid_bytes)
        if journey_id:
            new_event.set_journey_id(journey_id.bytes)
        return new_event

    def publish(self, payload, journey_id = None):
        self.publish_event_payload(payload.protobuf_message, journey_id=journey_id)

    def publish_event_payload(self, event_payload, journey_id = None):
        if self.native_publisher is None:
            self.logger.warn('native publisher is None, event lost: %s', event_payload.__name__)
            return
        new_event = self.new_event(journey_id=journey_id)
        with PublishEventTracer(new_event, event_payload) as span:
            try:
                self.native_publisher.publish_message(new_event.protobuf_message, event_payload)
            except Exception as e:
                payload_name = 'unknown'
                if event_payload:
                    payload_name = event_payload.DESCRIPTOR.full_name
                self.logger.exception('failed to publish event', extra={'payload.name': payload_name})
                span.set_error_status(e)

    def connect(self):
        if self.connection_config:
            self.connection_config.connect()
