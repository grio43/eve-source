#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\notice\notice_routing_cache.py
from datetime import datetime, timedelta
import collections
from logging import getLogger
EXPIRY_DELAY_SECS = 10
MAX_SIZE_BYTES = 2000000
session_to_target_group = {'solarsystemid2': 'solar_system',
 'userid': 'user',
 'corpid': 'corporation',
 'allianceid': 'alliance',
 'charid': 'character'}

class CacheMemoryTracker(object):

    def __init__(self, max_bytes):
        self.current_bytes = 0
        self.max_bytes = max_bytes

    def will_fit(self, notice):
        notice_size = notice.ByteSize()
        if notice_size + self.current_bytes <= self.max_bytes:
            return 0
        return notice_size + self.current_bytes - self.max_bytes

    def track_bytes(self, bytes):
        if bytes + self.current_bytes > self.max_bytes:
            raise CacheOOMException()
        self.current_bytes += bytes

    def release_bytes(self, bytes):
        self.current_bytes = max(0, self.current_bytes - bytes)


class NoticeCacheEntry(object):

    def __init__(self, notice, target_group, target_group_id, expiry):
        self.notice = notice
        self.target_group = target_group
        self.target_group_id = target_group_id
        self.expiry = expiry
        self.bytes = notice.ByteSize()


class NoticeCache(object):

    def __init__(self, memory_tracker):
        self.deque = collections.deque()
        self.memory_tracker = memory_tracker

    def add_notice_entry(self, notice_entry):
        self.memory_tracker.track_bytes(notice_entry.bytes)
        self.deque.append(notice_entry)

    def evict_for_bytes(self, bytes_needed):
        bytes_recovered = 0
        while len(self.deque) > 0:
            entry = self.deque.popleft()
            bytes_recovered += entry.bytes
            self.memory_tracker.release_bytes(entry.bytes)
            if bytes_recovered >= bytes_needed:
                break

        if bytes_recovered < bytes_needed:
            raise CacheOOMException()

    def remove_by_expiry(self, expiry):
        while len(self.deque) > 0:
            entry = self.deque[0]
            if entry.expiry > expiry:
                break
            self.memory_tracker.release_bytes(entry.bytes)
            self.deque.popleft()

    def get_newly_valid_notices(self, notices_to_dispatch, targets):
        requeue_entries = []
        while len(self.deque) > 0:
            entry = self.deque.popleft()
            if (entry.target_group, entry.target_group_id) not in targets:
                requeue_entries.append(entry)
                continue
            notices_to_dispatch.append(entry.notice)
            self.memory_tracker.release_bytes(entry.bytes)

        requeue_entries.reverse()
        self.deque.extendleft(requeue_entries)

    def empty(self):
        return len(self.deque) == 0

    def peek_first(self):
        return self.deque[0]

    def num_entries(self):
        return len(self.deque)


class UnhandledTargetGroupException(Exception):
    pass


class CacheOOMException(Exception):
    pass


class NoticeRoutingCache(object):

    def __init__(self):
        self._memory_tracker = CacheMemoryTracker(MAX_SIZE_BYTES)
        self._notice_cache = NoticeCache(self._memory_tracker)
        self._logger = getLogger(__name__)

    def remove_expired_entries(self):
        now = datetime.utcnow()
        self._notice_cache.remove_by_expiry(now)

    def add_notice(self, notice, target_group, target_group_id, override_expiry = None):
        expiry = override_expiry if override_expiry is not None else datetime.utcnow()
        expiry += timedelta(seconds=EXPIRY_DELAY_SECS)
        if target_group not in session_to_target_group.values():
            raise UnhandledTargetGroupException
        remaining_bytes = self._memory_tracker.will_fit(notice)
        if remaining_bytes > 0:
            self._notice_cache.evict_for_bytes(remaining_bytes)
        self._notice_cache.add_notice_entry(NoticeCacheEntry(notice, target_group, target_group_id, expiry))

    def get_newly_valid_notices(self, session_change):
        self.remove_expired_entries()
        notices_to_dispatch = []
        targets = []
        _populate_targets(targets, session_change)
        self._notice_cache.get_newly_valid_notices(notices_to_dispatch, targets)
        return notices_to_dispatch


def _populate_targets(targets, session_change):
    for key in session_to_target_group.iterkeys():
        if key not in session_change:
            continue
        target_group = session_to_target_group[key]
        _, target_group_id = session_change[key]
        targets.append((target_group, target_group_id))
