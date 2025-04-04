#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\stacklesslib\locks.py
from __future__ import with_statement
from __future__ import absolute_import
import stackless
from .main import set_channel_pref, elapsed_time
from .util import atomic, channel_wait, WaitTimeoutError

def lock_channel_wait(chan, timeout):
    try:
        channel_wait(chan, timeout)
        return True
    except WaitTimeoutError:
        return False


class LockMixin(object):

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc, val, tb):
        self.release()


class Lock(LockMixin):

    def __init__(self):
        self.channel = stackless.channel()
        set_channel_pref(self.channel)
        self.owning = None

    def acquire(self, blocking = True, timeout = None):
        with atomic():
            got_it = self._try_acquire()
            if got_it or not blocking:
                return got_it
            wait_until = None
            while True:
                if timeout is not None:
                    if wait_until is None:
                        wait_until = elapsed_time() + timeout
                    else:
                        timeout = wait_until - elapsed_time()
                        if timeout < 0:
                            return False
                try:
                    lock_channel_wait(self.channel, timeout)
                except:
                    self._safe_pump()
                    raise

                if self._try_acquire():
                    return True

    def _try_acquire(self):
        if self.owning is None:
            self.owning = stackless.getcurrent()
            return True
        return False

    def release(self):
        with atomic():
            self.owning = None
            self._pump()

    def _pump(self):
        if not self.owning and self.channel.balance:
            self.channel.send(None)

    def _safe_pump(self):
        try:
            self._pump()
        except Exception:
            pass


class RLock(Lock):

    def __init__(self):
        Lock.__init__(self)
        self.recursion = 0

    def _try_acquire(self):
        if self.owning is None or self.owning is stackless.getcurrent():
            self.owning = stackless.getcurrent()
            self.recursion += 1
            return True
        return False

    def release(self):
        if self.owning is not stackless.getcurrent():
            raise RuntimeError('cannot release un-aquired lock')
        with atomic():
            self.recursion -= 1
            if not self.recursion:
                self.owning = None
                self._pump()

    def _is_owned(self):
        return self.owning is stackless.getcurrent()

    def _release_save(self):
        r = (self.owning, self.recursion)
        self.owning, self.recursion = (None, 0)
        self._pump()
        return r

    def _acquire_restore(self, r):
        self.acquire()
        self.owning, self.recursion = r


def wait_for_condition(cond, predicate, timeout = None):
    result = predicate()
    if result:
        return result
    endtime = None
    while not result:
        if timeout is not None:
            if endtime is None:
                endtime = elapsed_time() + timeout
            else:
                timeout = endtime - elapsed_time()
                if timeout < 0:
                    return result
        cond.wait(timeout)
        result = predicate()

    return result


class Condition(LockMixin):

    def __init__(self, lock = None):
        if not lock:
            lock = RLock()
        self.lock = lock
        self.sem = Semaphore(0)
        self.nWaiting = 0
        self.acquire = lock.acquire
        self.release = lock.release
        try:
            self._release_save = lock._release_save
            self._acquire_restore = lock._acquire_restore
            self._is_owned = lock._is_owned
        except AttributeError:
            pass

    def _release_save(self):
        self.lock.release()

    def _acquire_restore(self, x):
        self.lock.acquire()

    def _is_owned(self):
        if self.lock.acquire(False):
            self.lock.release()
            return False
        else:
            return True

    def wait(self, timeout = None):
        if not self._is_owned():
            raise RuntimeError('cannot wait on un-aquired lock')
        self.nWaiting += 1
        saved = self._release_save()
        try:
            got_it = self.sem.acquire(timeout=timeout)
            if not got_it:
                self.nWaiting -= 1
        finally:
            self._acquire_restore(saved)

        return got_it

    def wait_for(self, predicate, timeout = None):
        return wait_for_condition(self, predicate, timeout)

    def notify(self, n = 1):
        if not self._is_owned():
            raise RuntimeError('cannot notify on un-acquired lock')
        n = min(n, self.nWaiting)
        if n > 0:
            self.nWaiting -= n
            self.sem.release(n)

    def notify_all(self):
        self.notify(self.nWaiting)

    notifyAll = notify_all


class NLCondition(LockMixin):

    def __init__(self):
        self._chan = stackless.channel()
        set_channel_pref(self._chan)

    def wait(self, timeout = None):
        return lock_channel_wait(self._chan, timeout)

    def wait_for(self, predicate, timeout = None):
        return wait_for_condition(self, predicate, timeout)

    def notify(self):
        with atomic():
            if self._chan.balance:
                self._chan.send(None)

    def notify_all(self):
        with atomic():
            for i in xrange(-self._chan.balance):
                if self._chan.balance:
                    self._chan.send(None)

    notifyAll = notify_all

    def acquire(self):
        pass

    release = acquire


class Semaphore(LockMixin):

    def __init__(self, value = 1):
        if value < 0:
            raise ValueError
        self._value = value
        self._chan = stackless.channel()
        set_channel_pref(self._chan)
        self._signaling = []

    def acquire(self, blocking = True, timeout = None):
        with atomic():
            if self._value > 0:
                self._value -= 1
                return True
            if not blocking:
                return False
            try:
                result = lock_channel_wait(self._chan, timeout)
            except:
                if stackless.getcurrent() in self._signaling:
                    self._signaling.remove(stackless.getcurrent())
                    self.release()
                raise

            if result:
                self._signaling.remove(stackless.getcurrent())
            return result

    def release(self, count = 1):
        with atomic():
            for i in xrange(count):
                if self._chan.balance:
                    self._signaling.append(self._chan.queue)
                    self._chan.send(None)
                else:
                    self._value += 1


class BoundedSemaphore(Semaphore):

    def __init__(self, value = 1):
        Semaphore.__init__(self, value)
        self._max_value = value

    def release(self, count = 1):
        with atomic():
            for i in xrange(count):
                if self._chan.balance:
                    self._signaling.append(self._chan.queue)
                    self._chan.send(None)
                else:
                    if self._value == self._max_value:
                        raise ValueError
                    self._value += 1


class Event(object):

    def __init__(self):
        self._is_set = False
        self.chan = stackless.channel()
        set_channel_pref(self.chan)

    def is_set(self):
        return self._is_set

    isSet = is_set

    def clear(self):
        self._is_set = False

    def wait(self, timeout = None):
        with atomic():
            if self._is_set:
                return True
            lock_channel_wait(self.chan, timeout)
            return self._is_set

    def set(self):
        with atomic():
            self._is_set = True
            for i in range(-self.chan.balance):
                self.chan.send(None)
