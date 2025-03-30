#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uthread2_plugins\geventimpl.py
import gevent
import sys
from gevent import monkey
if 'shared_tools' not in sys.executable:
    monkey.patch_socket()
    monkey.patch_ssl()
import gevent.event as gevents
try:
    from gevent.lock import Semaphore
except ImportError:
    from gevent.coros import Semaphore

import weakref
try:
    from gevent.queue import Channel as GChannel
except ImportError:
    from gevent.queue import Queue as GChannel

from gevent.queue import LifoQueue
from . import BaseUthreadImpl, Tasklet, BaseSemaphore, BaseChannel

class GeventTasklet(Tasklet):

    def __init__(self, func, *args, **kwargs):

        def inner():
            gevent.getcurrent().uthread2_tasklet = weakref.ref(self)
            func(*args, **kwargs)

        self.tasklet = gevent.spawn(inner)

    def is_alive(self):
        return not self.tasklet.ready()

    def kill(self):
        self.tasklet.kill()

    def get(self):
        return self.tasklet.get()


class GeventSemaphore(BaseSemaphore):

    def __init__(self):
        self.__semaphore = Semaphore()

    def __enter__(self):
        self.__semaphore.__enter__()

    def __exit__(self, exc, val, tb):
        self.__semaphore.__exit__(exc, val, tb)

    def acquire(self):
        self.__semaphore.acquire()

    def release(self):
        self.__semaphore.release()


class _GeventAutoTasklet(GeventTasklet):

    def __init__(self, tasklet):
        self.tasklet = weakref.proxy(tasklet)
        self.tasklet.uthread2_tasklet = lambda : self

    def is_alive(self):
        return not self.tasklet.dead


class _GeventUthread(BaseUthreadImpl):

    def sleep(self, seconds):
        gevent.sleep(seconds)

    def start_tasklet(self, func, *args, **kwargs):
        return GeventTasklet(func, *args, **kwargs)

    def yield_(self):
        gevent.sleep(0)

    def get_current(self):
        current = gevent.getcurrent()
        try:
            return current.uthread2_tasklet()
        except AttributeError:
            return _GeventAutoTasklet(current)

    def wait(self, tasklets, timeout):
        greenlets = [ x.tasklet for x in tasklets ]
        gevent.wait(greenlets, timeout)

    def Event(self):
        return gevents.Event()

    def Semaphore(self):
        return GeventSemaphore()

    def BlockingChannel(self):
        return BlockingChannel()

    def PumpChannel(self):
        return PumpChannel()

    def QueueChannel(self):
        return QueueChannel()


class Channel(BaseChannel):

    def __init__(self):
        self.channel = GChannel()

    def _send(self, data, block = False, timeout = None):
        self.channel.put(data, block=block, timeout=timeout)

    def _receive(self, block = False, timeout = None):
        return self.channel.get(block=block, timeout=timeout)


class BlockingChannel(Channel):

    def send(self, data):
        self._send(data, block=True)

    def receive(self):
        return self._receive()


class PumpChannel(Channel):

    def send(self, data):
        self._send(data)

    def receive(self):
        return self._receive(block=True)


class QueueChannel(object):

    def __init__(self):
        self.queue = LifoQueue()

    def send(self, item):
        self.queue.put(item=item, block=False)

    def receive(self):
        return self.queue.get(block=True)

    def __len__(self):
        return self.queue.qsize()

    def __next__(self):
        return self.receive()


GeventImpl = _GeventUthread()
