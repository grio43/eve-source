#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\beeline\__init__.py
import functools
import logging
import os
import socket
from contextlib import contextmanager
from libhoney import Client
from beeline.trace import SynchronousTracer
from beeline.version import VERSION
from beeline import internal
import beeline.propagation.honeycomb
import sys
USER_AGENT_ADDITION = 'beeline-python/%s' % VERSION
_GBL = None
_INITPID = None
try:
    import asyncio
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        pass

    from beeline.aiotrace import AsyncioTracer, traced_impl, untraced

    def in_async_code():
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False


except (ImportError, AttributeError):
    from beeline.trace import traced_impl

    def in_async_code():
        return False


class Beeline(object):

    def __init__(self, writekey = '', dataset = '', service_name = '', tracer = None, sample_rate = 1, api_host = 'https://api.honeycomb.io', max_concurrent_batches = 10, max_batch_size = 100, send_frequency = 0.25, block_on_send = False, block_on_response = False, transmission_impl = None, sampler_hook = None, presend_hook = None, http_trace_parser_hook = beeline.propagation.honeycomb.http_trace_parser_hook, http_trace_propagation_hook = beeline.propagation.honeycomb.http_trace_propagation_hook, debug = False):
        self.client = None
        self.tracer_impl = None
        self.presend_hook = None
        self.sampler_hook = None
        self.http_trace_parser_hook = None
        self.http_trace_propagation_hook = None
        self.debug = debug
        if debug:
            self._init_logger()
        if not writekey:
            writekey = os.environ.get('HONEYCOMB_WRITEKEY', '')
        if not dataset:
            dataset = os.environ.get('HONEYCOMB_DATASET', '')
        if not service_name:
            service_name = os.environ.get('HONEYCOMB_SERVICE', dataset)
        self.client = Client(writekey=writekey, dataset=dataset, sample_rate=sample_rate, api_host=api_host, max_concurrent_batches=max_concurrent_batches, max_batch_size=max_batch_size, send_frequency=send_frequency, block_on_send=block_on_send, block_on_response=block_on_response, transmission_impl=transmission_impl, user_agent_addition=USER_AGENT_ADDITION, debug=debug)
        self.log('initialized honeycomb client: writekey=%s dataset=%s service_name=%s', writekey, dataset, service_name)
        if not writekey:
            self.log('writekey not set! set the writekey if you want to send data to honeycomb')
        if not dataset:
            self.log('dataset not set! set a value for dataset if you want to send data to honeycomb')
        self.client.add_field('service_name', service_name)
        self.client.add_field('meta.beeline_version', VERSION)
        self.client.add_field('meta.local_hostname', socket.gethostname())
        if in_async_code():
            self.tracer_impl = AsyncioTracer(self.client)
        else:
            self.tracer_impl = SynchronousTracer(self.client)
        self.tracer_impl.register_hooks(presend=presend_hook, sampler=sampler_hook, http_trace_parser=http_trace_parser_hook, http_trace_propagation=http_trace_propagation_hook)
        self.sampler_hook = sampler_hook
        self.presend_hook = presend_hook
        self.http_trace_parser_hook = http_trace_parser_hook
        self.http_trace_propagation_hook = http_trace_propagation_hook

    def send_now(self, data):
        ev = self.client.new_event()
        if data:
            ev.add(data)
        self._run_hooks_and_send(ev)

    def add_field(self, name, value):
        span = self.tracer_impl.get_active_span()
        if span is None:
            return
        span.add_context_field(name, value)

    def add(self, data):
        span = self.tracer_impl.get_active_span()
        if span is None:
            return
        span.add_context(data)

    def tracer(self, name, trace_id = None, parent_id = None):
        return self.tracer_impl(name=name, trace_id=trace_id, parent_id=parent_id)

    def new_event(self, data = None, trace_name = ''):
        if trace_name:
            data['name'] = trace_name
        if self.tracer_impl.get_active_trace_id():
            self.tracer_impl.start_span(context=data)
        else:
            self.tracer_impl.start_trace(context=data)

    def send_event(self):
        span = self.tracer_impl.get_active_span()
        if span:
            if span.is_root():
                self.tracer_impl.finish_trace(span)
                return
            self.tracer_impl.finish_span(span)

    def send_all(self):
        span = self.tracer_impl.get_active_span()
        while span:
            if span.is_root():
                self.tracer_impl.finish_trace(span)
                return
            self.tracer_impl.finish_span(span)
            span = self.tracer_impl.get_active_span()

    def traced(self, name, trace_id = None, parent_id = None):
        return traced_impl(tracer_fn=self.tracer, name=name, trace_id=trace_id, parent_id=parent_id)

    def traced_thread(self, fn):
        trace_copy = self.tracer_impl._trace.copy()

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            self.tracer_impl._trace = trace_copy
            return fn(*args, **kwargs)

        return wrapped

    def _run_hooks_and_send(self, ev):
        presampled = False
        if self.sampler_hook:
            self.log('executing sampler hook on event ev = %s', ev.fields())
            keep, new_rate = self.sampler_hook(ev.fields())
            if not keep:
                self.log('skipping event due to sampler hook sampling ev = %s', ev.fields())
                return
            ev.sample_rate = new_rate
            presampled = True
        if self.presend_hook:
            self.log('executing presend hook on event ev = %s', ev.fields())
            self.presend_hook(ev.fields())
        if presampled:
            self.log('enqueuing presampled event ev = %s', ev.fields())
            ev.send_presampled()
        else:
            self.log('enqueuing event ev = %s', ev.fields())
            ev.send()

    def _init_logger(self):
        self._logger = logging.getLogger('honeycomb-beeline')
        self._logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

    def log(self, msg, *args, **kwargs):
        if self.debug:
            self._logger.debug(msg, *args, **kwargs)

    def get_responses_queue(self):
        return self.client.responses()

    def close(self):
        if self.client:
            self.client.close()


def init(writekey = '', dataset = '', service_name = '', tracer = None, sample_rate = 1, api_host = 'https://api.honeycomb.io', transmission_impl = None, sampler_hook = None, presend_hook = None, debug = False, *args, **kwargs):
    global _INITPID
    global _GBL
    pid = os.getpid()
    if _GBL:
        if pid == _INITPID:
            _GBL.log('beeline already initialized! skipping initialization')
            return
        _GBL.log('beeline already initialized, but process ID has changed (was {}, now {}). Reinitializing.'.format(_INITPID, pid))
        _GBL.close()
    _GBL = Beeline(writekey=writekey, dataset=dataset, sample_rate=sample_rate, api_host=api_host, transmission_impl=transmission_impl, debug=debug, presend_hook=presend_hook, sampler_hook=sampler_hook, service_name=service_name, *args, **kwargs)
    _INITPID = pid


def send_now(data):
    bl = get_beeline()
    if bl:
        bl.send_now(data)


def add_field(name, value):
    if _GBL:
        _GBL.add_field(name, value)


def add(data):
    bl = get_beeline()
    if bl:
        bl.add(data)


def add_context(data):
    bl = get_beeline()
    if bl:
        bl.tracer_impl.add_context(data=data)


def add_context_field(name, value):
    bl = get_beeline()
    if bl:
        bl.tracer_impl.add_context_field(name=name, value=value)


def remove_context_field(name):
    bl = get_beeline()
    if bl:
        bl.tracer_impl.remove_context_field(name=name)


def add_rollup_field(name, value):
    bl = get_beeline()
    if bl:
        bl.tracer_impl.add_rollup_field(name=name, value=value)


def add_trace_field(name, value):
    bl = get_beeline()
    if bl:
        bl.tracer_impl.add_trace_field(name=name, value=value)


def remove_trace_field(name):
    bl = get_beeline()
    if bl:
        bl.tracer_impl.remove_trace_field(name=name)


def tracer(name, trace_id = None, parent_id = None):
    bl = get_beeline()
    if bl:
        return bl.tracer(name=name, trace_id=trace_id, parent_id=parent_id)

    @contextmanager
    def _noop_cm():
        yield

    return _noop_cm()


def start_trace(context = None, trace_id = None, parent_span_id = None):
    bl = get_beeline()
    if bl:
        return bl.tracer_impl.start_trace(context=context, trace_id=trace_id, parent_span_id=parent_span_id)


def finish_trace(span):
    bl = get_beeline()
    if bl:
        bl.tracer_impl.finish_trace(span=span)


def start_span(context = None, parent_id = None):
    bl = get_beeline()
    if bl:
        return bl.tracer_impl.start_span(context=context, parent_id=parent_id)


def finish_span(span):
    bl = get_beeline()
    if bl:
        bl.tracer_impl.finish_span(span=span)


def propagate_and_start_trace(context, request):
    bl = get_beeline()
    if bl:
        return bl.tracer_impl.propagate_and_start_trace(context, request)


def http_trace_parser_hook(headers):
    bl = get_beeline()
    if bl:
        return bl.tracer_impl.http_trace_parser_hook(headers)


def http_trace_propagation_hook():
    bl = get_beeline()
    if bl:
        try:
            return bl.tracer_impl.http_trace_propagation_hook(bl.tracer_impl.get_propagation_context())
        except Exception:
            err = sys.exc_info()
            bl.log('error: http_trace_propagation_hook returned exception: %s', err)


def marshal_trace_context():
    bl = get_beeline()
    if bl:
        return bl.tracer_impl.marshal_trace_context()


def new_event(data = None, trace_name = ''):
    bl = get_beeline()
    if bl:
        bl.new_event(data=data, trace_name=trace_name)


def send_event():
    bl = get_beeline()
    if bl:
        bl.send_event()


def send_all():
    bl = get_beeline()
    if bl:
        bl.send_all()


def get_beeline():
    return _GBL


def get_responses_queue():
    bl = get_beeline()
    if bl:
        return bl.get_responses_queue()


def close():
    global _GBL
    if _GBL:
        _GBL.close()
    _GBL = None


def traced(name, trace_id = None, parent_id = None):
    return traced_impl(tracer_fn=tracer, name=name, trace_id=trace_id, parent_id=parent_id)


def traced_thread(fn):
    bl = get_beeline()
    if bl is None or bl.tracer_impl.get_active_trace_id() is None:

        @functools.wraps(fn)
        def noop(*args, **kwargs):
            return fn(*args, **kwargs)

        return noop
    trace_copy = bl.tracer_impl._trace.copy()

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        bl.tracer_impl._trace = trace_copy
        return fn(*args, **kwargs)

    return wrapped
