#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stackless_tracing\__init__.py
import clonable_tracer
import attributes
import beeline
import monolithconfig
import monolithhoneycomb
import stackless
import blue
import logging
from datetimeutils.RFC3339 import blue_to_datetime_micro
from journey.tracker import get_journey_id_for_event
from cluster import CLUSTER_INGRESS_ORIGIN_NAME
CLUSTER_INGRESS_ORIGIN_IDS = {v:k for k, v in CLUSTER_INGRESS_ORIGIN_NAME.iteritems()}
CONFIG_GROUP = 'gc'
CONFIG_ENABLED = 'stackless_tracing_enabled'
CONFIG_SAMPLE_RATE = 'stackless_tracing_sample_rate'
CONFIG_SUPPRESSED_LIST = 'tracing_machonet_suppressed_traces'
CONFIG_CUT_LIST = 'tracing_machonet_cut_spans'
CONFIG_CLIENT_PARTICIPATION = 'stackless_tracing_client_participation'
SETTINGS_GROUP = 'tracing'
SETTING_SERVER_PARTICIPATION = 'server_participation'
CLIENT_NAME = 'monolithhoneycomb_tracing'
_client = None
_enabled = False
_sample_rate = monolithhoneycomb.SAFE_SAMPLE_RATE
_participation = False
_suppressed_trace_names = set()
logger = logging.getLogger(__name__)

def init():
    monolithconfig.add_global_config_callback(update_config)
    monolithconfig.add_watch_group_callback(update_config, SETTINGS_GROUP)


def update_config():
    global _suppressed_trace_names
    global _participation
    global _enabled
    global _sample_rate
    _enabled = monolithconfig.enabled(CONFIG_ENABLED, CONFIG_GROUP)
    _sample_rate = monolithconfig.get_value(CONFIG_SAMPLE_RATE, CONFIG_GROUP)
    _participation = _get_participation()
    _suppressed_trace_names = _get_suppressed_trace_names()
    clonable_tracer.set_cut_span_names(_get_cut_span_names())
    try:
        _sample_rate = int(_sample_rate)
    except (TypeError, ValueError):
        _sample_rate = monolithhoneycomb.SAFE_SAMPLE_RATE

    _ensure_client()


def get_trace_from_store():
    return _get_trace_from_store()


def get_tracer_from_store():
    return _get_tracer_from_store()


def get_sampled_from_context(context):
    return context.get(attributes.SAMPLED, None)


def get_ingress_id_from_context(context):
    ingress_name = context.get(attributes.INGRESS, None)
    return CLUSTER_INGRESS_ORIGIN_IDS.get(ingress_name)


def get_trace_id_from_context(context):
    return context.get(attributes.TRACE_ID, None)


def get_span_id_from_context(context):
    return context.get(attributes.SPAN_ID, None)


def get_sample_rate_from_context(context):
    return context.get(attributes.SAMPLE_RATE, None)


def _get_participation_from_context(context):
    return context.get(attributes.PARTICIPATION, True)


def is_suppressed(span_name):
    return span_name in _suppressed_trace_names


def start_trace(context = None, span_name = None, service_name = None, trace_id = None, parent_span_id = None, sampled = None, ingress_id = None, sample_rate = None, store_context = True, create_new_tracer = False):
    global _client
    tracer = span = None
    trace_context = _create_trace_context(None, None, None, None, None)
    if not _tracing_active():
        return (tracer, span, trace_context)
    if context is None:
        context = {}
    if sampled is None or not trace_id:
        context['eve.sampling_strategy'] = 'deterministic'
        if _decision_suppressed(span_name):
            return (tracer, span, trace_context)
        trace_id = beeline.trace.generate_trace_id()
        if sample_rate is None:
            sample_rate = getattr(_client, 'sample_rate', monolithhoneycomb.SAFE_SAMPLE_RATE)
        sampled = _should_trace(trace_id, span_name, sample_rate)
    else:
        context['eve.sampling_strategy'] = 'sampled parent'
    if sampled:
        tracer = _get_tracer_from_store()
        if tracer is None or create_new_tracer:
            tracer = clonable_tracer.CloneableTracer(_client)
        context.update(_get_stackless_context(ingress_id, sample_rate))
        context.update({attributes.SPAN_NAME: span_name,
         attributes.SERVICE_NAME: attributes.SERVICE_NAME_PREFIX + service_name})
        tracer.sampler_hook = lambda _fields: (sampled, sample_rate)
        span = tracer.start_or_cut_trace(span_name=span_name, context=context, trace_id=trace_id, parent_id=parent_span_id)
    if span is None:
        span_id = beeline.trace.generate_span_id()
    else:
        span_id = span.id
    if store_context:
        _store_trace(tracer, trace_id, span_id, sampled, ingress_id, sample_rate)
    trace_context = _create_trace_context(trace_id, span_id, sampled, ingress_id, sample_rate)
    return (tracer, span, trace_context)


def end_trace(tracer = None, remove_from_store = True):
    if tracer is None:
        tracer = _get_tracer_from_store()
    if tracer is None:
        return
    span = tracer.get_active_span()
    _set_ending_attributes(span)
    tracer.finish_trace(span)
    if remove_from_store:
        _remove_trace()


def start_span(span_name = None, service_name = None, span_context = None):
    span = None
    if not _tracing_active():
        trace_context = _create_trace_context(None, None, None, None, None)
        return (span, trace_context)
    tracer, trace_id, parent_id, sampled, ingress_id, sample_rate = _get_trace_from_store()
    if tracer is None:
        trace_context = _create_trace_context(trace_id, parent_id, sampled, ingress_id, sample_rate)
        return (span, trace_context)
    if span_context is None:
        span_context = {}
    span_context['eve.sampling_strategy'] = 'sampled parent'
    span_context.update(_get_stackless_context(ingress_id, sample_rate))
    span_context.update({attributes.SPAN_NAME: span_name,
     attributes.SERVICE_NAME: attributes.SERVICE_NAME_PREFIX + service_name})
    span = tracer.start_or_cut_span(span_name=span_name, context=span_context, trace_id=trace_id, parent_id=parent_id)
    _store_trace(tracer, trace_id, span.id, sampled, ingress_id, sample_rate)
    trace_context = _create_trace_context(trace_id, span.id, sampled, ingress_id, sample_rate)
    return (span, trace_context)


def end_span(span):
    if span is None:
        return
    tracer, trace_id, parent_id, sampled, ingress_id, sample_rate = _get_trace_from_store()
    if tracer is None:
        return
    _set_ending_attributes(span)
    tracer.finish_span(span)
    active_span_id = None
    active_span = tracer.get_active_span()
    if active_span is not None:
        active_span_id = active_span.id
    _store_trace(tracer, trace_id, active_span_id, sampled, ingress_id, sample_rate)


def _set_ending_attributes(span):
    current = stackless.getcurrent()
    if not hasattr(current, 'GetRunTime'):
        return
    run_time_ms = current.GetRunTime() * 1000
    span.add_context({attributes.TASKLET_RUNTIME_MS: run_time_ms})


def _should_trace(trace_id, span_name, sample_rate):
    if is_suppressed(span_name):
        return False
    return _deterministic_sample(trace_id, sample_rate)


def _deterministic_sample(trace_id, sample_rate):
    return beeline.trace._should_sample(trace_id, sample_rate)


def _decision_suppressed(span_name):
    if not _participation:
        return True
    if clonable_tracer.is_cut(span_name):
        return True
    return False


def _create_trace_context(trace_id, parent_id, sampled, ingress_id, sample_rate):
    return {attributes.TRACE_ID: trace_id,
     attributes.SPAN_ID: parent_id,
     attributes.SAMPLED: sampled,
     attributes.INGRESS_ID: ingress_id,
     attributes.SAMPLE_RATE: sample_rate}


def _store_trace(tracer, trace_id, parent_id, sampled, ingress_id, sample_rate):
    current = stackless.getcurrent()
    try:
        setattr(current, 'tracer', tracer)
        setattr(current, 'trace_id', trace_id)
        setattr(current, 'parent_id', parent_id)
        setattr(current, 'sampled', sampled)
        setattr(current, 'ingress_id', ingress_id)
        setattr(current, 'sample_rate', sample_rate)
    except StandardError:
        pass


def _remove_trace():
    current = stackless.getcurrent()
    try:
        setattr(current, 'tracer', None)
        setattr(current, 'trace_id', None)
        setattr(current, 'parent_id', None)
        setattr(current, 'sampled', None)
        setattr(current, 'ingress_id', None)
        setattr(current, 'sample_rate', None)
    except StandardError:
        pass


def _get_trace_from_store():
    current = stackless.getcurrent()
    tracer = trace_id = parent_id = sampled = ingress_id = sample_rate = None
    try:
        tracer = getattr(current, 'tracer', None)
        trace_id = getattr(current, 'trace_id', None)
        parent_id = getattr(current, 'parent_id', None)
        sampled = getattr(current, 'sampled', None)
        ingress_id = getattr(current, 'ingress_id', None)
        sample_rate = getattr(current, 'sample_rate', None)
    except StandardError:
        pass

    return (tracer,
     trace_id,
     parent_id,
     sampled,
     ingress_id,
     sample_rate)


def _get_tracer_from_store():
    trace_data = _get_trace_from_store()
    return trace_data[0]


def _ensure_client():
    global _client
    if _client is None:
        _client = monolithhoneycomb.new_client(CLIENT_NAME, _sample_rate)
    else:
        _client.sample_rate = _sample_rate


def _get_participation():
    if monolithconfig.on_client():
        return monolithconfig.enabled(CONFIG_CLIENT_PARTICIPATION, CONFIG_GROUP)
    if monolithconfig.on_proxy():
        return False
    if monolithconfig.on_server():
        return monolithconfig.enabled(SETTING_SERVER_PARTICIPATION, SETTINGS_GROUP)


def _get_suppressed_trace_names():
    return _get_list_from_config(CONFIG_SUPPRESSED_LIST)


def _get_cut_span_names():
    return _get_list_from_config(CONFIG_CUT_LIST)


def _get_list_from_config(config_name):
    span_names = set()
    raw = monolithconfig.get_value(config_name, CONFIG_GROUP)
    if raw is None:
        return span_names
    raw_list = raw.split(';')
    for span_name in raw_list:
        if len(span_name) == 0:
            continue
        span_names.add(span_name)

    return span_names


def _tracing_active():
    return _enabled & (_client is not None)


def _get_stackless_context(ingress_id, sample_rate):
    current = stackless.getcurrent()
    tasklet_id = getattr(current, 'tasklet_id', None)
    wallclock = blue.os.GetWallclockTime()
    journey_id = get_journey_id_for_event()
    creation_datetime = getattr(current, 'creation_datetime', None)
    stackless_context = {attributes.TIME_DILATION: blue.os.simDilation,
     attributes.INGRESS: CLUSTER_INGRESS_ORIGIN_NAME.get(ingress_id, None)}
    if creation_datetime is not None:
        stackless_context[attributes.TASKLET_CREATION_DATETIME] = creation_datetime.isoformat('T') + 'Z'
    if sample_rate is not None:
        stackless_context[attributes.SAMPLE_RATE] = int(sample_rate)
    if tasklet_id is not None:
        stackless_context[attributes.TASKLET] = int(tasklet_id)
    if wallclock is not None:
        stackless_context[attributes.BLUE_TIME] = blue_to_datetime_micro(wallclock)
    if journey_id is not None:
        stackless_context[attributes.JOURNEY] = journey_id
    return stackless_context
