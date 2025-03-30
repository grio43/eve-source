#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\grpc\spanManager.py
import logging
import uuid
import launchdarkly
import stackless_tracing
from tracing import propagate_trace
from eveProto import get_message_type_url
from stackless_tracing.attributes import SPAN_KIND, MESSAGE_ARRIVAL_TIME
from stackless_tracing.attributes import PAYLOAD_TYPE, PAYLOAD_BYTES, PRIMITIVE, DOMAIN
from stackless_tracing.attributes import EXTERNAL_ORIGIN, ISSUED, MESSAGE_ID, APPLICATION
from stackless_tracing.attributes import RESPONSE_PAYLOAD, RESPONSE_PAYLOAD_BYTES, INTERNAL_ORIGIN, DISPATCHED, GATEWAY
from stackless_tracing.attributes import STATUS_MESSAGE, STATUS_CODE, ERROR
from stackless_tracing.attributes import RPC_SYSTEM
logger = logging.getLogger(__name__)
_FALLBACK_SAMPLE_RATE = 1000
_SAMPLE_RATE_FLAG_KEY = 'eve-desktop-client-request-tracing-sample-rate'

class SpanManager:
    service_name = 'publicGatewaySvc'
    kind = 'client'
    domain = 'eve_public'
    primitive = 'request'

    def __init__(self):
        self._tracers = {}
        self._trace_ids = {}
        self._sample_rate = _FALLBACK_SAMPLE_RATE
        launchdarkly.get_client().notify_flag(_SAMPLE_RATE_FLAG_KEY, _FALLBACK_SAMPLE_RATE, self.update_sample_rate)

    def update_sample_rate(self, ld_client, feature_key, fallback, flag_deleted):
        self._sample_rate = ld_client.get_int_variation(feature_key=feature_key, fallback=fallback)
        logger.info('request tracing sample rate set to: %d', self._sample_rate)

    def start_request_trace(self, request, payload):
        span_name = '{} send'.format(payload.DESCRIPTOR.full_name)
        tracer, span, context = stackless_tracing.start_trace(span_name=span_name, service_name=self.service_name, store_context=False, sample_rate=self._sample_rate)
        trace_id = stackless_tracing.get_trace_id_from_context(context)
        span_id = stackless_tracing.get_span_id_from_context(context)
        sampled = stackless_tracing.get_sampled_from_context(context)
        sample_rate = stackless_tracing.get_sample_rate_from_context(context)
        propagate_trace(request, trace_id, span_id, sampled, sample_rate)
        if not sampled:
            return
        payload_name = get_message_type_url(payload.DESCRIPTOR.full_name)
        span.add_context({SPAN_KIND: self.kind,
         PAYLOAD_TYPE: payload_name,
         PAYLOAD_BYTES: payload.ByteSize(),
         DOMAIN: self.domain,
         PRIMITIVE: self.primitive,
         RPC_SYSTEM: 'grpc',
         EXTERNAL_ORIGIN: request.external_origin,
         ISSUED: request.issued,
         MESSAGE_ID: str(uuid.UUID(bytes=request.correlation_uuid)),
         APPLICATION: str(uuid.UUID(bytes=request.application_instance_uuid))})
        self._tracers[trace_id] = (tracer, span)
        self._trace_ids[request.correlation_uuid] = trace_id

    def end_request_trace(self, response, arrival_datetime):
        trace_id = response.trace_context.trace_id.encode('hex')
        correlation_uuid = response.correlation_uuid
        if trace_id is None:
            logger.warn('missing trace decision in eve_public response: {}'.format(response))
            return
        if trace_id not in self._tracers:
            if correlation_uuid not in self._trace_ids:
                return
            logger.error('unexpected trace_id for request {}\n\twant: {}\n\thave: {}'.format(correlation_uuid.encode('hex'), self._trace_ids.get(correlation_uuid), trace_id))
            trace_id = self._trace_ids.get(correlation_uuid)
        tracer, span = self._tracers.get(trace_id)
        if tracer is None:
            return
        span.add_context({RESPONSE_PAYLOAD: response.payload.TypeName(),
         RESPONSE_PAYLOAD_BYTES: response.payload.ByteSize(),
         INTERNAL_ORIGIN: response.internal_origin,
         DISPATCHED: response.dispatched,
         GATEWAY: str(uuid.UUID(bytes=response.gateway_instance_uuid)),
         MESSAGE_ARRIVAL_TIME: arrival_datetime.isoformat('T') + 'Z'})
        stackless_tracing.end_trace(tracer)
        del self._tracers[trace_id]
        del self._trace_ids[response.correlation_uuid]

    def timeout_request_trace(self, correlation_id):
        if correlation_id is None:
            return
        if correlation_id not in self._trace_ids:
            return
        trace_id = self._trace_ids.get(correlation_id)
        del self._trace_ids[correlation_id]
        if trace_id not in self._tracers:
            return
        tracer, span = self._tracers.get(trace_id)
        del self._tracers[span.trace_id]
        if tracer is None:
            return
        span.add_context({STATUS_CODE: 2,
         STATUS_MESSAGE: 'span timeout',
         ERROR: True})
        stackless_tracing.end_trace(tracer)
