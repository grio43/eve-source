#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\libhoney\transmission.py
from datetime import timedelta
import uthread2
from six.moves import queue
from urlparse import urljoin
import gzip
import io
import json
import requests
import sys
import time
import collections
from libhoney.version import VERSION
from libhoney.internal import json_default_handler
try:
    from tornado import ioloop, gen
    from tornado.httpclient import AsyncHTTPClient, HTTPRequest
    from tornado.locks import Semaphore
    from tornado.queues import Queue, QueueFull
    from tornado.util import TimeoutError
    has_tornado = True
except ImportError:
    has_tornado = False

destination = collections.namedtuple('destination', ['writekey', 'dataset', 'api_host'])
import blue
import monolithmetrics
METRIC_PREFIX = 'libhoney_'

class Transmission:

    def __init__(self, max_concurrent_batches = 10, block_on_send = False, block_on_response = False, max_batch_size = 100, send_frequency = 0.25, user_agent_addition = '', debug = False, gzip_enabled = True, gzip_compression_level = 1, proxies = {}, max_pending = 1000, max_responses = 2000):
        self.max_concurrent_batches = max_concurrent_batches
        self.block_on_send = block_on_send
        self.block_on_response = block_on_response
        self.max_batch_size = max_batch_size
        self.send_frequency = send_frequency
        self.gzip_compression_level = gzip_compression_level
        self.gzip_enabled = gzip_enabled
        user_agent = 'libhoney-py/' + VERSION
        if user_agent_addition:
            user_agent += ' ' + user_agent_addition
        session = requests.Session()
        session.headers.update({'User-Agent': user_agent})
        if self.gzip_enabled:
            session.headers.update({'Content-Encoding': 'gzip'})
        if proxies:
            session.proxies.update(proxies)
        self.session = session
        self.pending = queue.Queue(maxsize=max_pending)
        self.responses = queue.Queue(maxsize=max_responses)
        self.debug = debug
        if debug:
            self._init_logger()

    def _init_logger(self):
        import logging
        self._logger = logging.getLogger('honeycomb-sdk-xmit')
        self._logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

    def log(self, msg, *args, **kwargs):
        if self.debug:
            self._logger.debug(msg, *args, **kwargs)

    def start(self):
        uthread2.StartTasklet(self._sender)

    def send(self, ev):
        monolithmetrics.gauge(METRIC_PREFIX + 'queue_length', self.pending.qsize())
        try:
            if self.block_on_send:
                self.pending.put(ev)
            else:
                self.pending.put_nowait(ev)
            monolithmetrics.increment(METRIC_PREFIX + 'messages_queued')
        except queue.Full:
            response = {'status_code': 0,
             'duration': 0,
             'metadata': ev.metadata,
             'body': '',
             'error': 'event dropped; queue overflow'}
            if self.block_on_response:
                self.responses.put(response)
            else:
                try:
                    self.responses.put_nowait(response)
                except queue.Full:
                    pass

            monolithmetrics.increment(METRIC_PREFIX + 'queue_overflow')

    def _sender(self):
        events = []
        last_flush = time.time()
        while True:
            blue.pyos.BeNice()
            try:
                ev = self.pending.get(block=False)
                if ev is None:
                    self._flush(events)
                    return
                events.append(ev)
                if len(events) > self.max_batch_size or time.time() - last_flush > self.send_frequency:
                    self._flush(events)
                    events = []
                    last_flush = time.time()
            except queue.Empty:
                self._flush(events)
                events = []
                last_flush = time.time()

    def _flush(self, events):
        if not events:
            uthread2.Sleep(0.1)
            return
        for dest, group in group_events_by_destination(events).items():
            self._send_batch(dest, group)
            blue.pyos.BeNice()

        uthread2.Sleep(0.1)

    def _send_batch(self, destination, events):
        start = time.time()
        status_code = 0
        try:
            url = urljoin(urljoin(destination.api_host, '/1/batch/'), destination.dataset)
            payload = []
            for ev in events:
                event_time = ev.created_at.isoformat()
                if ev.created_at.tzinfo is None:
                    event_time += 'Z'
                payload.append({'time': event_time,
                 'samplerate': ev.sample_rate,
                 'data': ev.fields()})

            data = json.dumps(payload, default=json_default_handler)
            if self.gzip_enabled:
                stream = io.BytesIO()
                compressor = gzip.GzipFile(fileobj=stream, mode='wb', compresslevel=self.gzip_compression_level)
                compressor.write(data.encode())
                compressor.close()
                data = stream.getvalue()
                stream.close()
            self.log('firing batch, size = %d', len(payload))
            resp = self.session.post(url, headers={'X-Honeycomb-Team': destination.writekey,
             'Content-Type': 'application/json'}, data=data, timeout=10.0)
            status_code = resp.status_code
            resp.raise_for_status()
            statuses = [ {'status': d.get('status'),
             'error': d.get('error')} for d in resp.json() ]
            for ev, status in zip(events, statuses):
                self._enqueue_response(status.get('status'), '', status.get('error'), start, ev.metadata)

        except Exception as e:
            self._enqueue_errors(status_code, e, start, events)

    def _enqueue_errors(self, status_code, error, start, events):
        for ev in events:
            monolithmetrics.increment(METRIC_PREFIX + 'send_errors')
            self._enqueue_response(status_code, '', error, start, ev.metadata)

    def _enqueue_response(self, status_code, body, error, start, metadata):
        resp = {'status_code': status_code,
         'body': body,
         'error': error,
         'duration': (time.time() - start) * 1000,
         'metadata': metadata}
        self.log('enqueuing response = %s', resp)
        if self.block_on_response:
            self.responses.put(resp)
        else:
            try:
                self.responses.put_nowait(resp)
            except queue.Full:
                pass

    def close(self):
        try:
            self.pending.put(None, True, 10)
        except queue.Full:
            pass

        try:
            self.responses.put(None, True, 10)
        except queue.Full:
            pass

    def get_response_queue(self):
        return self.responses


if has_tornado:

    class TornadoTransmissionException(Exception):
        pass


    class TornadoTransmission:

        def __init__(self, max_concurrent_batches = 10, block_on_send = False, block_on_response = False, max_batch_size = 100, send_frequency = timedelta(seconds=0.25), user_agent_addition = '', max_pending = 1000, max_responses = 2000):
            if not has_tornado:
                raise ImportError('TornadoTransmission requires tornado, but it was not found.')
            self.block_on_send = block_on_send
            self.block_on_response = block_on_response
            self.max_batch_size = max_batch_size
            self.send_frequency = send_frequency
            user_agent = 'libhoney-py/' + VERSION
            if user_agent_addition:
                user_agent += ' ' + user_agent_addition
            self.http_client = AsyncHTTPClient(force_instance=True, defaults=dict(user_agent=user_agent))
            self.pending = Queue(maxsize=max_pending)
            self.responses = Queue(maxsize=max_responses)
            self.batch_data = {}
            self.batch_sem = Semaphore(max_concurrent_batches)

        def start(self):
            ioloop.IOLoop.current().spawn_callback(self._sender)

        def send(self, ev):
            try:
                if self.block_on_send:
                    self.pending.put(ev)
                else:
                    self.pending.put_nowait(ev)
            except QueueFull:
                response = {'status_code': 0,
                 'duration': 0,
                 'metadata': ev.metadata,
                 'body': '',
                 'error': 'event dropped; queue overflow'}
                if self.block_on_response:
                    self.responses.put(response)
                else:
                    try:
                        self.responses.put_nowait(response)
                    except QueueFull:
                        pass

        @gen.coroutine
        def _sender(self):
            events = []
            last_flush = time.time()
            while True:
                try:
                    ev = yield self.pending.get(timeout=self.send_frequency)
                    if ev is None:
                        yield self._flush(events)
                        return
                    events.append(ev)
                    if len(events) > self.max_batch_size or time.time() - last_flush > self.send_frequency.total_seconds():
                        yield self._flush(events)
                        events = []
                except TimeoutError:
                    yield self._flush(events)
                    events = []
                    last_flush = time.time()

        @gen.coroutine
        def _flush(self, events):
            if not events:
                return
            for dest, group in group_events_by_destination(events).items():
                yield self._send_batch(dest, group)

        @gen.coroutine
        def _send_batch(self, destination, events):
            start = time.time()
            status_code = 0
            try:
                yield self.batch_sem.acquire()
                url = urljoin(urljoin(destination.api_host, '/1/batch/'), destination.dataset)
                payload = []
                for ev in events:
                    event_time = ev.created_at.isoformat()
                    if ev.created_at.tzinfo is None:
                        event_time += 'Z'
                    payload.append({'time': event_time,
                     'samplerate': ev.sample_rate,
                     'data': ev.fields()})

                req = HTTPRequest(url, method='POST', headers={'X-Honeycomb-Team': destination.writekey,
                 'Content-Type': 'application/json'}, body=json.dumps(payload, default=json_default_handler))
                self.http_client.fetch(req, self._response_callback)
                self.batch_data[req] = {'start': start,
                 'events': events}
            except Exception as e:
                self._enqueue_errors(status_code, e, start, events)
            finally:
                self.batch_sem.release()

        def _enqueue_errors(self, status_code, error, start, events):
            for ev in events:
                self._enqueue_response(status_code, '', error, start, ev.metadata)

        def _response_callback(self, resp):
            events = self.batch_data[resp.request]['events']
            start = self.batch_data[resp.request]['start']
            try:
                status_code = resp.code
                resp.rethrow()
                statuses = [ d['status'] for d in json.loads(resp.body) ]
                for ev, status in zip(events, statuses):
                    self._enqueue_response(status, '', None, start, ev.metadata)

            except Exception as e:
                self._enqueue_errors(status_code, e, start, events)
            finally:
                del self.batch_data[resp.request]

        def _enqueue_response(self, status_code, body, error, start, metadata):
            resp = {'status_code': status_code,
             'body': body,
             'error': error,
             'duration': (time.time() - start) * 1000,
             'metadata': metadata}
            if self.block_on_response:
                self.responses.put(resp)
            else:
                try:
                    self.responses.put_nowait(resp)
                except QueueFull:
                    pass

        def close(self):
            try:
                self.pending.put(None, 10)
            except QueueFull:
                pass

            try:
                self.responses.put(None, 10)
            except QueueFull:
                pass

        def get_response_queue(self):
            return self.responses


class FileTransmission:

    def __init__(self, user_agent_addition = '', output = sys.stderr):
        self._output = output
        self._user_agent = 'libhoney-py/' + VERSION
        if user_agent_addition:
            self._user_agent += ' ' + user_agent_addition

    def start(self):
        pass

    def send(self, ev):
        event_time = ev.created_at.isoformat()
        if ev.created_at.tzinfo is None:
            event_time += 'Z'
        payload = {'time': event_time,
         'samplerate': ev.sample_rate,
         'dataset': ev.dataset,
         'user_agent': self._user_agent,
         'data': ev.fields()}
        self._output.write(json.dumps(payload, default=json_default_handler) + '\n')

    def close(self):
        pass

    def flush(self):
        self._output.flush()

    def get_response_queue(self):
        pass


def group_events_by_destination(events):
    ret = collections.defaultdict(list)
    for ev in events:
        ret[destination(ev.writekey, ev.dataset, ev.api_host)].append(ev)

    return ret


def _safe_submit(pool, *args, **kwargs):
    try:
        pool.submit(*args, **kwargs)
    except RuntimeError:
        pass
