#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\grpc\tracing.py
import stackless_tracing
from eveProto import get_message_type_url
from eveProto.tracing import propagate_trace
from stackless_tracing.attributes import SPAN_NAME, SPAN_KIND, SERVICE_NAME, STATUS_CODE, STATUS_MESSAGE, ERROR
from stackless_tracing.attributes import RPC_SYSTEM
from stackless_tracing.attributes import PAYLOAD_TYPE, PAYLOAD_BYTES, PRIMITIVE, DOMAIN
from stackless_tracing.attributes import MESSAGE_ID
from stackless_tracing.attributes import EXTERNAL_ORIGIN, OCCURRED, APPLICATION
import uuid

class PublishEventTracer(object):
    span_name = '/eve_public.public_gateway.Events/Publish send'
    service_name = 'publicGatewaySvc'
    span_type = 'server'
    rpc_system = 'grpc'
    domain = 'eve_public'
    primitive = 'event'

    def __init__(self, event_class, payload):
        self.event = event_class.protobuf_message
        self.payload = payload
        self.tracer = self.span = None

    def __enter__(self):
        self.tracer, self.span, trace_context = stackless_tracing.start_trace(span_name=self.span_name, service_name=self.service_name, store_context=False)
        trace_id = stackless_tracing.get_trace_id_from_context(trace_context)
        span_id = stackless_tracing.get_span_id_from_context(trace_context)
        sampled = stackless_tracing.get_sampled_from_context(trace_context)
        sample_rate = stackless_tracing.get_sample_rate_from_context(trace_context)
        propagate_trace(self.event, trace_id, span_id, sampled, sample_rate)
        if not sampled:
            return self
        self.span.add_context({SPAN_KIND: self.span_type,
         RPC_SYSTEM: self.rpc_system,
         PAYLOAD_TYPE: get_message_type_url(self.payload.DESCRIPTOR.full_name),
         PAYLOAD_BYTES: self.payload.ByteSize(),
         DOMAIN: self.domain,
         PRIMITIVE: self.primitive,
         EXTERNAL_ORIGIN: self.event.external_origin,
         OCCURRED: self.event.occurred,
         MESSAGE_ID: str(uuid.UUID(bytes=self.event.uuid)),
         APPLICATION: str(uuid.UUID(bytes=self.event.application_instance_uuid))})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        stackless_tracing.end_trace(self.tracer)

    def set_error_status(self, e):
        if self.span is None:
            return
        status_message = getattr(e, 'message', '')
        if not len(status_message):
            status_message = type(e)
        self.span.add_context({STATUS_CODE: 2,
         STATUS_MESSAGE: status_message,
         ERROR: True})
