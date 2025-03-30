#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\watchdog\utils\delayed_queue.py
import time
import threading
from collections import deque

class DelayedQueue(object):

    def __init__(self, delay):
        self.delay_sec = delay
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._queue = deque()
        self._closed = False

    def put(self, element, delay = False):
        self._lock.acquire()
        self._queue.append((element, time.time(), delay))
        self._not_empty.notify()
        self._lock.release()

    def close(self):
        self._closed = True
        self._not_empty.acquire()
        self._not_empty.notify()
        self._not_empty.release()

    def get(self):
        while True:
            self._not_empty.acquire()
            while len(self._queue) == 0 and not self._closed:
                self._not_empty.wait()

            if self._closed:
                self._not_empty.release()
                return
            head, insert_time, delay = self._queue[0]
            self._not_empty.release()
            if delay:
                time_left = insert_time + self.delay_sec - time.time()
                while time_left > 0:
                    time.sleep(time_left)
                    time_left = insert_time + self.delay_sec - time.time()

            with self._lock:
                if len(self._queue) > 0 and self._queue[0][0] is head:
                    self._queue.popleft()
                    return head

    def remove(self, predicate):
        with self._lock:
            for i, (elem, t, delay) in enumerate(self._queue):
                if predicate(elem):
                    del self._queue[i]
                    return elem
