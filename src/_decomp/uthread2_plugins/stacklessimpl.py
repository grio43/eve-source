#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uthread2_plugins\stacklessimpl.py
import stackless
import sys
import time
import weakref
import uthread
from stacklesslib import locks, main
try:
    from stacklesslib.util import qchannel
except ImportError:
    from stacklesslib.util import QueueChannel as qchannel

from . import BaseUthreadImpl, Tasklet, stackless_sleep, BaseSemaphore, BaseChannel

def is_main():
    return stackless.getcurrent() == stackless.getmain()


_tasklets = weakref.WeakKeyDictionary()

class StacklessTasklet(Tasklet):

    def __init__(self, func, *args, **kwargs):

        def inner():
            _tasklets[stackless.getcurrent()] = self
            func(*args, **kwargs)

        self.tasklet = stackless.tasklet(inner)()

    def is_alive(self):
        return self.tasklet.alive

    def kill(self):
        self.tasklet.kill()

    def get(self):
        while self.tasklet.alive:
            stackless_sleep.sleep(0.005)


class StacklessSemaphore(BaseSemaphore):

    def __init__(self):
        self.__semaphore = uthread.Semaphore()

    def __enter__(self):
        self.__semaphore.__enter__()

    def __exit__(self, exc, val, tb):
        self.__semaphore.__exit__(exc, val, tb)

    def acquire(self):
        self.__semaphore.acquire()

    def release(self):
        self.__semaphore.release()


class StacklessEvent(locks.Event):

    def wait(self, timeout = None):
        if not is_main():
            res = locks.Event.wait(self, timeout)
            return res
        if self.is_set():
            return True
        if timeout is None:
            timeout = sys.maxint
        endtime = time.time() + timeout
        while not self.is_set() and time.time() < endtime:
            stackless_sleep.sleep(0.005)

        return self.is_set()


class Channel(BaseChannel):

    def __init__(self, preference):
        self.channel = stackless.channel()
        self.channel.preference = preference

    def send(self, data):
        self.channel.send(data)

    def receive(self):
        return self.channel.receive()


class _StacklessUthread(BaseUthreadImpl):

    def sleep(self, seconds):
        stackless_sleep.sleep(seconds)

    def start_tasklet(self, func, *args, **kwargs):
        return StacklessTasklet(func, *args, **kwargs)

    def yield_(self):
        main.mainloop.wakeup_tasklets(None)
        if stackless.getcurrent() == stackless.getmain():
            stackless.run()

    def get_current(self):
        return _tasklets.get(stackless.getcurrent(), None)

    def wait(self, tasklets, timeout):
        deadline = time.time() + timeout
        while time.time() < deadline:
            alive = [ tasklet.is_alive() for tasklet in tasklets ]
            if not all(alive):
                return
            self.sleep(0.005)

        for tasklet in tasklets:
            try:
                tasklet.kill()
            except Exception as e:
                pass

    def Event(self):
        return StacklessEvent()

    def Semaphore(self):
        return StacklessSemaphore()

    def BlockingChannel(self):
        return Channel(-1)

    def PumpChannel(self):
        return Channel(1)

    def QueueChannel(self):
        return QueueChannel()


class QueueChannel(qchannel):

    def __len__(self):
        return len(self.data_queue)


StacklessImpl = _StacklessUthread()
