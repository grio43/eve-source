#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\tracing.py
import logging
logger = logging.getLogger(__name__)

def propagate_trace(protobuf_message, trace_id, parent_span_id, sampled, sample_rate):
    if trace_id is not None:
        protobuf_message.trace_context.trace_id = trace_id.decode('hex')
        protobuf_message.trace_context.parent_id = parent_span_id.decode('hex')
        protobuf_message.trace_context.flags.sampled = sampled
        protobuf_message.trace_context.state.sample_rate = sample_rate


def extract_trace_context(protobuf_message):
    trace_id = protobuf_message.trace_context.trace_id.encode('hex') if protobuf_message.trace_context.trace_id else None
    parent_span_id = protobuf_message.trace_context.parent_id.encode('hex') if protobuf_message.trace_context.parent_id else None
    sampled = protobuf_message.trace_context.flags.sampled if trace_id is not None else None
    sample_rate = protobuf_message.trace_context.state.sample_rate
    if sample_rate == 0:
        sample_rate = 1
    return (trace_id,
     parent_span_id,
     sampled,
     sample_rate)
