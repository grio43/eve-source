#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stackless_response_router\stackless_response_router.py
import logging
import sentry_sdk
import time
import uthread2
import uuid
from exceptions import TimeoutException, UnpackException
DEFAULT_TIMEOUT_SECONDS = 10
MIN_TIMEOUT_SECONDS = 0.1
logger = logging.getLogger(__name__)

class StacklessResponseRouter:

    def __init__(self, span_manager):
        self.response_handlers = {}
        self.span_manager = span_manager

    def add_response_handler(self, request, expected_response_class, timeout_seconds = None):
        if timeout_seconds is None:
            timeout_seconds = DEFAULT_TIMEOUT_SECONDS
        elif timeout_seconds < MIN_TIMEOUT_SECONDS:
            timeout_seconds = MIN_TIMEOUT_SECONDS
        rh = ResponseHandler(request, expected_response_class, timeout_seconds)
        self.response_handlers[request.correlation_uuid] = rh
        return rh.response_channel

    def handle_response(self, response_id_bytes, response):
        try:
            rh = self.response_handlers.pop(response_id_bytes)
            if rh is None:
                return
            rh.handle(response)
        except KeyError:
            return

    def handle_request_timeouts(self):
        try:
            timed_out_request_ids = []
            now = time.time()
            for request_id, rh in self.response_handlers.iteritems():
                if now > rh.deadline:
                    timed_out_request_ids.append(request_id)

            for request_id_bytes in timed_out_request_ids:
                rh = self.response_handlers.pop(request_id_bytes)
                rh.timeout()
                self.span_manager.timeout_request_trace(request_id_bytes)

        except Exception as e:
            logger.error(e)

    @staticmethod
    def report_timeout_exception(request_id_bytes, details):
        with sentry_sdk.push_scope() as scope:
            request_uuid = uuid.UUID(bytes=request_id_bytes)
            scope.set_tag('request_uuid', request_uuid)
            for key, val in details.iteritems():
                scope.set_tag(key, val)

            sentry_sdk.capture_message('request timed out', 'error')


class ResponseHandler(object):
    __slots__ = ('request', 'response_channel', 'deadline', 'expected_response_class')

    def __init__(self, request, expected_response_class, timeout_seconds):
        self.request = request
        self.response_channel = uthread2.queue_channel()
        self.deadline = time.time() + timeout_seconds
        self.expected_response_class = expected_response_class

    def unpack_failure(self, payload_type_url, exception):
        msg = 'Delivered Response Type: {} Expected Response Class: {} Exception: {}'.format(payload_type_url, self.expected_response_class, exception)
        self.response_channel.send_exception(UnpackException, msg)
        self.response_channel.close()

    def handle(self, response_primitive):
        payload = None
        if response_primitive.payload.type_url:
            try:
                payload = self.expected_response_class()
                unpacked = response_primitive.payload.Unpack(payload)
                if not unpacked:
                    self.unpack_failure(response_primitive.payload.type_url, None)
                    return
            except Exception as e:
                self.unpack_failure(response_primitive.payload.type_url, e)
                return

        self.response_channel.send((response_primitive, payload))
        self.response_channel.close()

    def timeout(self):
        self.response_channel.send_exception(TimeoutException)
        self.response_channel.close()
