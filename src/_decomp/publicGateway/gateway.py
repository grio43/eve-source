#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\gateway.py
import blue
from eve.common.script.util.retry import retry_with_exponential_backoff
from httplib import INTERNAL_SERVER_ERROR, BAD_GATEWAY, SERVICE_UNAVAILABLE, GATEWAY_TIMEOUT
from logging import getLogger
from stackless_response_router.exceptions import TimeoutException
from uthread2 import Sleep
logger = getLogger('PublicGatewaySvc')
STATUS_CODES_THAT_TRIGGER_RETRIES = [INTERNAL_SERVER_ERROR,
 BAD_GATEWAY,
 SERVICE_UNAVAILABLE,
 GATEWAY_TIMEOUT]

class PublicGateway(object):

    def __init__(self, grpc_module, connection_config, event_publisher, notice_signal_registry, notice_consumer, requests_broker):
        self.notice_signal_registry = notice_signal_registry
        self.grpc_module = grpc_module
        self.connection_config = connection_config
        self.grpc_event_publisher = event_publisher
        self.grpc_notice_consumer = notice_consumer
        self.grpc_requests_broker = requests_broker
        self.instantiationTime = blue.os.GetWallclockTimeNow()

    def get_uptime_ms(self):
        return blue.os.TimeDiffInMs(self.instantiationTime, blue.os.GetWallclockTimeNow())

    def get_event_publisher_rtt(self):
        if self.grpc_event_publisher is None:
            return -1
        return self.grpc_event_publisher.get_rtt()

    def get_event_publisher_details(self):
        if self.grpc_event_publisher is None:
            return
        return self.grpc_event_publisher.get_details()

    def publish_event(self, event_payload, journey_id = None):
        self.grpc_event_publisher.publish(event_payload, journey_id=journey_id)

    def publish_event_payload(self, event_payload, journey_id = None):
        self.grpc_event_publisher.publish_event_payload(event_payload, journey_id=journey_id)

    def get_notice_consumer_details(self):
        if self.grpc_notice_consumer is None:
            return
        return self.grpc_notice_consumer.get_details()

    def get_request_broker_rtt(self):
        if self.grpc_requests_broker is None:
            return -1
        return self.grpc_requests_broker.get_rtt()

    def get_request_broker_details(self):
        if self.grpc_requests_broker is None:
            return
        return self.grpc_requests_broker.get_details()

    def send_user_request(self, request_payload, expected_response_class, timeout_seconds):
        request_primitive, response_channel = self.grpc_requests_broker.send_user_request(request_payload, expected_response_class, timeout_seconds)
        logger.info('Request %s sent for user', self._get_request_id(request_payload))
        return (request_primitive, response_channel)

    def send_character_request(self, request_payload, expected_response_class, timeout_seconds):
        request_primitive, response_channel = self.grpc_requests_broker.send_character_request(request_payload, expected_response_class, timeout_seconds)
        logger.info('Request %s sent for character', self._get_request_id(request_payload))
        return (request_primitive, response_channel)

    def send_blocking_user_request_and_receive_response(self, request_payload, expected_response_class, timeout_seconds, max_attempts, retry_delay_in_seconds):
        sender = self.grpc_requests_broker.send_user_request
        response_primitive, response_payload = self._retry_on_timeout(max_attempts, sender, request_payload, expected_response_class, timeout_seconds, retry_delay_in_seconds)
        logger.info('Request %s sent for user', self._get_request_id(request_payload))
        return (response_primitive, response_payload)

    def send_blocking_character_request_and_receive_response(self, request_payload, expected_response_class, timeout_seconds, max_attempts, retry_delay_in_seconds):
        sender = self.grpc_requests_broker.send_character_request
        response_primitive, response_payload = self._retry_on_timeout(max_attempts, sender, request_payload, expected_response_class, timeout_seconds, retry_delay_in_seconds)
        logger.info('Request %s sent for character', self._get_request_id(request_payload))
        return (response_primitive, response_payload)

    def set_active_character_id(self, character_id):
        self.grpc_event_publisher.set_active_character_id(character_id)
        self.grpc_requests_broker.set_active_character_id(character_id)

    def set_authenticated_user_id(self, user_id):
        self.grpc_event_publisher.set_authenticated_user_id(user_id)
        self.grpc_requests_broker.set_authenticated_user_id(user_id)

    def set_auth_token(self, auth_token):
        if auth_token is None:
            return
        if auth_token is '':
            return
        self.grpc_module.set_auth_token(auth_token)

    def connect(self):
        self.connection_config.connect()

    def subscribe_to_notice(self, notice_payload, callback):
        self.notice_signal_registry.subscribe_to_notice(notice_payload, callback)

    def session_changed(self, change):
        self.grpc_notice_consumer.session_changed(change)

    def _retry_on_timeout(self, max_attempts, sender, request_payload, expected_response_class, timeout_seconds, retry_delay_in_seconds):

        def send_request():
            request_primitive, response_channel = sender(request_payload, expected_response_class, timeout_seconds)
            response_primitive, response_payload = response_channel.receive()
            return (response_primitive, response_payload)

        def should_retry(result_or_exception):
            if isinstance(result_or_exception, TimeoutException):
                return True
            if isinstance(result_or_exception, tuple):
                response_primitive, response_payload = result_or_exception
                if response_primitive.status_code in STATUS_CODES_THAT_TRIGGER_RETRIES:
                    return True
            return False

        return retry_with_exponential_backoff(func=send_request, max_attempts=max_attempts, retry_delay_in_seconds=retry_delay_in_seconds, jitter=True, should_retry=should_retry, waiter=self._wait)

    def _get_request_id(self, request_payload):
        return '{module}.{name}'.format(module=request_payload.__module__, name=type(request_payload).__name__)

    def _wait(self, delay):
        Sleep(delay)
