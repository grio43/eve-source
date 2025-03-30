#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\libhoney\client.py
from six.moves import queue
from libhoney.event import Event
from libhoney.builder import Builder
from libhoney.fields import FieldHolder
from libhoney.transmission import Transmission
import uthread2
import time

class Client(object):

    def __init__(self, writekey = '', dataset = '', sample_rate = 1, api_host = 'https://api.honeycomb.io', max_concurrent_batches = 10, max_batch_size = 100, send_frequency = 0.25, block_on_send = False, block_on_response = False, transmission_impl = None, user_agent_addition = '', debug = False):
        self.xmit = transmission_impl
        if self.xmit is None:
            self.xmit = Transmission(max_concurrent_batches=max_concurrent_batches, block_on_send=block_on_send, block_on_response=block_on_response, user_agent_addition=user_agent_addition, debug=debug)
        self.xmit.start()
        self.writekey = writekey
        self.dataset = dataset
        self.api_host = api_host
        self.sample_rate = sample_rate
        self._responses = self.xmit.get_response_queue()
        self.block_on_response = block_on_response
        self.fields = FieldHolder()
        self.debug = debug
        if debug:
            self._init_logger()
        self.log('initialized honeycomb client: writekey=%s dataset=%s', writekey, dataset)
        if not writekey:
            self.log('writekey not set! set the writekey if you want to send data to honeycomb')
        if not dataset:
            self.log('dataset not set! set a value for dataset if you want to send data to honeycomb')

    def __enter__(self):
        return self

    def __exit__(self, typ, value, tb):
        self.close()

    def _init_logger(self):
        import logging
        self._logger = logging.getLogger('honeycomb-sdk')
        self._logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

    def log(self, msg, *args, **kwargs):
        if self.debug:
            self._logger.debug(msg, *args, **kwargs)

    def responses(self):
        return self._responses

    def add_field(self, name, val):
        self.fields.add_field(name, val)

    def add_dynamic_field(self, fn):
        self.fields.add_dynamic_field(fn)

    def add(self, data):
        self.fields.add(data)

    def send(self, event):
        if self.xmit is None:
            self.log('tried to send on a closed or uninitialized libhoney client, ev = %s', event.fields())
            return
        self.log('send enqueuing event ev = %s', event.fields())
        self.xmit.send(event)

    def send_now(self, data):
        ev = self.new_event()
        ev.add(data)
        self.log('send_now enqueuing event ev = %s', ev.fields())
        ev.send()

    def send_dropped_response(self, event):
        response = {'status_code': 0,
         'duration': 0,
         'metadata': event.metadata,
         'body': '',
         'error': 'event dropped due to sampling'}
        self.log('enqueuing response = %s', response)
        try:
            if self.block_on_response:
                self._responses.put(response)
            else:
                self._responses.put_nowait(response)
        except queue.Full:
            pass

    def close(self):
        if self.xmit:
            self.xmit.close()
        self.xmit = None

    def flush(self):
        if self.xmit and isinstance(self.xmit, Transmission):
            self.xmit.close()
            self.xmit.start()

    def stackless_close(self, sleep_ms = 0, max_total_sleep_ms = 0):

        def is_populated(queue):
            if queue is None:
                return False
            if queue.qsize() > 0:
                return True
            return False

        start_time_seconds = time.time()
        if sleep_ms > 0:
            sleep_seconds = float(sleep_ms) / 1000
        else:
            sleep_seconds = 0
        queue = None
        start_size = 0
        i = 0
        if self.xmit is not None and self.xmit.pending is not None:
            queue = self.xmit.pending
            start_size = queue.qsize()
        self.close()
        if start_size == 0:
            return (time.time() - start_time_seconds,
             start_size,
             start_size,
             i)
        while is_populated(queue):
            if (time.time() - start_time_seconds) * 1000 >= max_total_sleep_ms:
                break
            uthread2.sleep(sleep_seconds)
            i += 1

        duration_ms = (time.time() - start_time_seconds) * 1000
        if queue is not None:
            end_size = queue.qsize()
        else:
            end_size = 0
        return (duration_ms,
         start_size,
         end_size,
         i)

    def new_event(self, data = {}):
        ev = Event(data=data, client=self)
        return ev

    def new_builder(self, data = None, dyn_fields = None, fields = None):
        if data is None:
            data = {}
        if dyn_fields is None:
            dyn_fields = []
        if fields is None:
            fields = FieldHolder()
        builder = Builder(data, dyn_fields, fields, self)
        return builder
