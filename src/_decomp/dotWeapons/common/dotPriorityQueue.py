#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dotWeapons\common\dotPriorityQueue.py
import heapq

class DotPriorityQueue(object):
    _REMOVED = '<removed-dot>'

    def __init__(self):
        self._queue = []
        self._entries = {}

    def Add(self, dotApplication):
        applicationID = dotApplication.id
        queueEntry = self._entries.get(applicationID)
        if queueEntry:
            return
        queueEntry = QueueEntry((dotApplication.expiryTime, dotApplication))
        heapq.heappush(self._queue, queueEntry)
        self._entries[applicationID] = queueEntry

    def Remove(self, applicationID):
        entry = self._entries.pop(applicationID, None)
        if entry is None:
            return
        entry.dotApplication = self._REMOVED

    def ExpireDotApplications(self, now):
        while self._queue:
            expiryTime, dotApplication = self._queue[0]
            if dotApplication is self._REMOVED:
                heapq.heappop(self._queue)
            elif expiryTime <= now:
                heapq.heappop(self._queue)
                del self._entries[dotApplication.id]
            else:
                return

    def IterateDotApplications(self):
        for entry in self._entries.itervalues():
            yield entry.dotApplication

    def IsEmpty(self):
        return not bool(self._entries)


class QueueEntry(list):

    @property
    def expiryTime(self):
        return self[0]

    @property
    def dotApplication(self):
        return self[1]

    @dotApplication.setter
    def dotApplication(self, value):
        self[1] = value
