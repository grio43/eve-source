#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\libhoney\event.py
import datetime
import random
from contextlib import contextmanager
import libhoney.state as state
from libhoney.fields import FieldHolder

class Event(object):

    def __init__(self, data = {}, dyn_fields = [], fields = FieldHolder(), client = None):
        if client is None:
            client = state.G_CLIENT
        self.client = client
        if self.client:
            self.writekey = client.writekey
            self.dataset = client.dataset
            self.api_host = client.api_host
            self.sample_rate = client.sample_rate
        else:
            self.writekey = None
            self.dataset = None
            self.api_host = 'https://api.honeycomb.io'
            self.sample_rate = 1
        self._fields = FieldHolder()
        if self.client:
            self._fields += self.client.fields
        self._fields.add(data)
        [ self._fields.add_dynamic_field(fn) for fn in dyn_fields ]
        self._fields += fields
        self.created_at = datetime.datetime.utcnow()
        self.metadata = None
        for fn in self._fields._dyn_fields:
            self._fields.add_field(fn.__name__, fn())

    def add_field(self, name, val):
        self._fields.add_field(name, val)

    def add_metadata(self, md):
        self.metadata = md

    def add(self, data):
        self._fields.add(data)

    @contextmanager
    def timer(self, name):
        start = datetime.datetime.now()
        yield
        duration = datetime.datetime.now() - start
        self.add_field(name, duration.total_seconds() * 1000)

    def send(self):
        if self.client is None:
            state.warn_uninitialized()
            return
        if _should_drop(self.sample_rate):
            self.client.send_dropped_response(self)
            return
        self.send_presampled()

    def send_presampled(self):
        if self._fields.is_empty():
            self.client.log("No metrics added to event. Won't send empty event.")
            return
        if self.api_host == '':
            self.client.log("No api_host for Honeycomb. Can't send to the Great Unknown.")
            return
        if self.writekey == '':
            self.client.log("No writekey specified. Can't send event.")
            return
        if self.dataset == '':
            self.client.log("No dataset for Honeycomb. Can't send event without knowing which dataset it belongs to.")
            return
        if self.client:
            self.client.send(self)
        else:
            state.warn_uninitialized()

    def __str__(self):
        return str(self._fields)

    def fields(self):
        return self._fields._data


def _should_drop(rate):
    return random.randint(1, rate) != 1
