#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\machonet_tracing\__init__.py
from stackless_tracing.attributes import SPAN_NAME, SPAN_KIND, SERVICE_NAME, STATUS_MESSAGE, STATUS_CODE, ERROR, MACHO_CACHE_OK
from stackless_tracing.attributes import RPC_SYSTEM, RPC_SERVICE, RPC_METHOD
from stackless_tracing.attributes import SESSION_CALL_MS, WRITE_MS, PROXY
from stackless_tracing.attributes import BIND_PARAMS
import stackless_tracing
import monolithconfig
import logging
import time
from contextlib import contextmanager
from cluster import CLUSTER_INGRESS_ORIGIN_CLIENT, MACHONETMSG_TYPE_CALL_REQ
from carbon.common.lib.const import ADDRESS_TYPE_CLIENT
TRACED_REQUEST_TYPES = {MACHONETMSG_TYPE_CALL_REQ}
CALL_SERVICE_NAME = CALL_RPC_SYSTEM = 'machoNet'
RPC_METHOD_BIND = 'MachoBindObject'
logger = logging.getLogger(__name__)

def propagate_trace_context(packet):
    if monolithconfig.on_proxy():
        return
    tracer, trace_id, parent_id, sampled, ingress_id, sample_rate = stackless_tracing.get_trace_from_store()
    cut_parent = None
    if tracer is not None:
        cut_parent = tracer.has_cut_parent()
    _set_packet_trace_context(packet, trace_id, parent_id, ingress_id, sampled, sample_rate, cut_parent)


def _get_span_name(rpc_service, rpc_method):
    return '{}.{}'.format(rpc_service, rpc_method)


def _set_packet_trace_context(packet, trace_id, parent_span_id, ingress_id, sampled, sample_rate, cut_parent):
    if trace_id is not None:
        packet.trace_id = trace_id
        packet.parent_span_id = parent_span_id
        packet.ingress_id = ingress_id
        packet.sampled = sampled
        packet.sample_rate = sample_rate
        packet.cut_parent = cut_parent
        packet.Changed()


def _get_active_span():
    tracer = stackless_tracing.get_tracer_from_store()
    if tracer is None:
        return
    span = tracer.get_active_span()
    return span


def _is_macho_bind_method(rpc_method):
    return rpc_method == RPC_METHOD_BIND


def _get_bind_inner_payload(packet):
    try:
        return packet.payload[2][-1]
    except StandardError:
        return None


class EgressTracer(object):
    span_kind = 'client'

    def __init__(self, packet, rpc_service, rpc_method, force_trace = False):
        self.packet = packet
        self.force_trace = force_trace
        self.rpc_service = rpc_service
        self.rpc_method = rpc_method
        self.tracer = self.span = None
        self.sampled = False

    def __enter__(self):
        if not self._is_tracable():
            return self
        span_name = _get_span_name(self.rpc_service, self.rpc_method)
        self.tracer, self.span, trace_context = stackless_tracing.start_trace(span_name=span_name, service_name=CALL_SERVICE_NAME, ingress_id=CLUSTER_INGRESS_ORIGIN_CLIENT, sampled=None, store_context=True)
        self._set_packet_trace_context(trace_context)
        self.sampled = stackless_tracing.get_sampled_from_context(trace_context)
        if not self.sampled:
            return self
        if self._is_macho_bind_method():
            inner_payload = self._get_bind_inner_payload()
            self.rpc_method = inner_payload[0]
        self.span.add_context({SPAN_KIND: self.span_kind,
         RPC_SYSTEM: CALL_RPC_SYSTEM,
         RPC_SERVICE: self.rpc_service,
         RPC_METHOD: self.rpc_method})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.sampled:
            return
        stackless_tracing.end_trace(self.tracer)

    def _is_tracable(self):
        if not monolithconfig.on_client():
            return False
        if self.packet.command not in TRACED_REQUEST_TYPES:
            return False
        if self._is_macho_bind_method():
            if self._get_bind_inner_payload() is None:
                return False
        if _get_active_span() is not None:
            return False
        return True

    def set_bind_parameters(self, bind_params):
        if self.span is None:
            return
        self.span.add_context_field(BIND_PARAMS, bind_params)

    def _set_packet_trace_context(self, trace_context):
        propagate_trace_context(self.packet)

    def _get_bind_inner_payload(self):
        return _get_bind_inner_payload(self.packet)

    def _is_macho_bind_method(self):
        return _is_macho_bind_method(self.rpc_method)


class IngressTracer(object):
    span_kind = 'server'

    def __init__(self, packet):
        self.packet = packet
        self.sampled = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_trace()

    @staticmethod
    def start_macho_bind_trace(packet, object_name, method_name, bind_start, bind_end):
        inner_payload = _get_bind_inner_payload(packet)
        if inner_payload is None:
            return
        tracer, span = IngressTracer.start_trace(packet, object_name, method_name)
        if span is not None:
            span.add_context_field('eve.machonet.object_bind_ms', (bind_end - bind_start) * 1000)

    @staticmethod
    def start_trace(packet, rpc_service, rpc_method):
        context = {}
        tracer = span = None
        if not IngressTracer._is_traceable(packet):
            return (tracer, span)
        span_name = _get_span_name(rpc_service, rpc_method)
        trace_id, parent_span_id, sampled, ingress_id, sample_rate = IngressTracer.extract_trace_context(packet)
        if IngressTracer.has_cut_parent(packet):
            context['eve.tracing.has_removed_parents'] = True
        if sampled is None and packet.source.addressType != ADDRESS_TYPE_CLIENT:
            return (tracer, span)
        tracer, span, trace_context = stackless_tracing.start_trace(context=context, span_name=span_name, service_name=CALL_SERVICE_NAME, trace_id=trace_id, parent_span_id=parent_span_id, sampled=sampled, ingress_id=ingress_id, sample_rate=sample_rate, store_context=True)
        IngressTracer._set_packet_trace_context(packet, trace_context)
        if not stackless_tracing.get_sampled_from_context(trace_context):
            return (tracer, span)
        span.event.created_at = packet.read_time
        span.add_context({SPAN_KIND: IngressTracer.span_kind,
         RPC_SYSTEM: CALL_RPC_SYSTEM,
         RPC_METHOD: rpc_method,
         RPC_SERVICE: rpc_service})
        return (tracer, span)

    @staticmethod
    def end_trace():
        tracer, _trace_id, _parent_id, sampled, ingress_id, _sample_rate = stackless_tracing.get_trace_from_store()
        if not sampled or tracer is None:
            return
        stackless_tracing.end_trace(tracer)

    @staticmethod
    def _is_traceable(packet):
        if not monolithconfig.on_server():
            return False
        if packet.command not in TRACED_REQUEST_TYPES:
            return False
        return True

    @staticmethod
    def extract_trace_context(packet):
        trace_id = packet.trace_id
        parent_span_id = packet.parent_span_id
        sampled = packet.sampled
        ingress_id = packet.ingress_id or CLUSTER_INGRESS_ORIGIN_CLIENT
        sample_rate = packet.sample_rate
        return (trace_id,
         parent_span_id,
         sampled,
         ingress_id,
         sample_rate)

    @staticmethod
    def has_cut_parent(packet):
        return packet.cut_parent

    @staticmethod
    def _set_packet_trace_context(packet, trace_context):
        propagate_trace_context(packet)

    @staticmethod
    def set_error_state(description):
        span = _get_active_span()
        if span is None:
            return
        span.add_context({STATUS_MESSAGE: description,
         STATUS_CODE: 2,
         ERROR: True})

    @staticmethod
    def set_object_cache_ok():
        span = _get_active_span()
        if span is None:
            return
        span.add_context({MACHO_CACHE_OK: True})

    @staticmethod
    def record_ingress_proxy_id(proxy_node_id):
        span = _get_active_span()
        if span is None:
            return
        span.add_context_field(PROXY, proxy_node_id)

    @staticmethod
    @contextmanager
    def record_write_response_ms():
        start_time = time.time()
        yield
        span = _get_active_span()
        if span is None:
            return
        span.add_context_field(WRITE_MS, (time.time() - start_time) * 1000)

    @staticmethod
    @contextmanager
    def record_process_call_ms():
        start_time = time.time()
        yield
        span = _get_active_span()
        if span is None:
            return
        span.add_context_field(SESSION_CALL_MS, (time.time() - start_time) * 1000)
