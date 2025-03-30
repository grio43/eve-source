#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\libhoney\builder.py
import libhoney.state as state
from libhoney.event import Event
from libhoney.fields import FieldHolder

class Builder(object):

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

    def add_field(self, name, val):
        self._fields.add_field(name, val)

    def add_dynamic_field(self, fn):
        self._fields.add_dynamic_field(fn)

    def add(self, data):
        self._fields.add(data)

    def send_now(self, data):
        ev = self.new_event()
        ev.add(data)
        ev.send()

    def new_event(self):
        ev = Event(fields=self._fields, client=self.client)
        ev.writekey = self.writekey
        ev.dataset = self.dataset
        ev.api_host = self.api_host
        ev.sample_rate = self.sample_rate
        return ev

    def clone(self):
        c = Builder(fields=self._fields, client=self.client)
        c.writekey = self.writekey
        c.dataset = self.dataset
        c.sample_rate = self.sample_rate
        c.api_host = self.api_host
        return c
