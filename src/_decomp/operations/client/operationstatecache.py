#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\client\operationstatecache.py
from collections import defaultdict
from contextlib import contextmanager
try:
    from locks import Lock
except ImportError:
    Lock = None

class OperationStateLock(object):

    def __init__(self):
        self._state = OperationStateCache()
        self._lock = Lock('OperationStateCacheLock')

    @contextmanager
    def Lock(self):
        with self._lock:
            yield self._state

    def get_active_category_id(self):
        return self._state.active_category_id

    def get_active_operation_id(self):
        return self._state.active_operation_id


class OperationStateCache(object):

    def __init__(self):
        self.active_category_id = None
        self.active_operation_id = None
        self.tasks_by_category_and_operation_id = defaultdict(dict)
        self.tree_keeper = None
