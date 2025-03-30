#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\libhoney\__init__.py
import atexit
import random
import libhoney.state as state
from libhoney.client import Client
from libhoney.builder import Builder
from libhoney.event import Event
from libhoney.fields import FieldHolder
from libhoney.errors import SendError
random.seed()

def init(writekey = '', dataset = '', sample_rate = 1, api_host = 'https://api.honeycomb.io', max_concurrent_batches = 10, max_batch_size = 100, send_frequency = 0.25, block_on_send = False, block_on_response = False, transmission_impl = None, debug = False):
    state.G_CLIENT = Client(writekey=writekey, dataset=dataset, sample_rate=sample_rate, api_host=api_host, max_concurrent_batches=max_concurrent_batches, max_batch_size=max_batch_size, send_frequency=send_frequency, block_on_send=block_on_send, block_on_response=block_on_response, transmission_impl=transmission_impl, debug=debug)


def responses():
    return None


def add_field(name, val):
    if state.G_CLIENT is None:
        state.warn_uninitialized()
        return
    state.G_CLIENT.add_field(name, val)


def add_dynamic_field(fn):
    if state.G_CLIENT is None:
        state.warn_uninitialized()
        return
    state.G_CLIENT.add_dynamic_field(fn)


def add(data):
    if state.G_CLIENT is None:
        state.warn_uninitialized()
        return
    state.G_CLIENT.add(data)


def new_event(data = {}):
    return Event(data=data, client=state.G_CLIENT)


def send_now(data):
    if state.G_CLIENT is None:
        state.warn_uninitialized()
        return
    ev = Event(client=state.G_CLIENT)
    ev.add(data)
    ev.send()


def flush():
    if state.G_CLIENT:
        state.G_CLIENT.flush()


def close():
    if state.G_CLIENT:
        state.G_CLIENT.close()
    state.G_CLIENT = None


atexit.register(close)
__all__ = ['Builder',
 'Event',
 'Client',
 'FieldHolder',
 'SendError',
 'add',
 'add_dynamic_field',
 'add_field',
 'close',
 'init',
 'responses',
 'send_now']
