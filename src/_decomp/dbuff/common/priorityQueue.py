#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dbuff\common\priorityQueue.py
import heapq

class BuffPriorityQueue(object):
    _REMOVED = '<removed-buff>'

    def __init__(self):
        self._queue = []
        self._entries = {}

    def Add(self, buff, evaluationTimestamp):
        entry = self._entries.get(buff)
        if entry:
            if entry[0] == evaluationTimestamp:
                return
            self.Remove(buff)
        entry = [evaluationTimestamp, buff]
        heapq.heappush(self._queue, entry)
        self._entries[buff] = entry

    def Remove(self, buff):
        entry = self._entries.pop(buff)
        entry[1] = self._REMOVED

    def PopNextReadyBuff(self, now):
        while self._queue:
            evaluationTimestamp, buff = self._queue[0]
            if buff is self._REMOVED:
                heapq.heappop(self._queue)
            else:
                if evaluationTimestamp < now:
                    heapq.heappop(self._queue)
                    del self._entries[buff]
                    return buff
                return None
