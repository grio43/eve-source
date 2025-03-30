#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\watchdog\utils\bricks.py
from .compat import queue

class SkipRepeatsQueue(queue.Queue, object):

    def _init(self, maxsize):
        super(SkipRepeatsQueue, self)._init(maxsize)
        self._last_item = None

    def _put(self, item):
        if item != self._last_item:
            super(SkipRepeatsQueue, self)._put(item)
            self._last_item = item
        else:
            self.unfinished_tasks -= 1

    def _get(self):
        item = super(SkipRepeatsQueue, self)._get()
        if item is self._last_item:
            self._last_item = None
        return item
