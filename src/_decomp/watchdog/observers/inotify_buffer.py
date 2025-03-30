#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\watchdog\observers\inotify_buffer.py
import logging
from watchdog.utils import BaseThread
from watchdog.utils.delayed_queue import DelayedQueue
from watchdog.observers.inotify_c import Inotify
logger = logging.getLogger(__name__)

class InotifyBuffer(BaseThread):
    delay = 0.5

    def __init__(self, path, recursive = False):
        BaseThread.__init__(self)
        self._queue = DelayedQueue(self.delay)
        self._inotify = Inotify(path, recursive)
        self.start()

    def read_event(self):
        return self._queue.get()

    def on_thread_stop(self):
        self._inotify.close()
        self._queue.close()

    def close(self):
        self.stop()
        self.join()

    def _group_events(self, event_list):
        grouped = []
        for inotify_event in event_list:
            logger.debug('in-event %s', inotify_event)

            def matching_from_event(event):
                return not isinstance(event, tuple) and event.is_moved_from and event.cookie == inotify_event.cookie

            if inotify_event.is_moved_to:
                for index, event in enumerate(grouped):
                    if matching_from_event(event):
                        grouped[index] = (event, inotify_event)
                        break
                else:
                    from_event = self._queue.remove(matching_from_event)
                    if from_event is not None:
                        grouped.append((from_event, inotify_event))
                    else:
                        logger.debug('could not find matching move_from event')
                        grouped.append(inotify_event)
            else:
                grouped.append(inotify_event)

        return grouped

    def run(self):
        deleted_self = False
        while self.should_keep_running() and not deleted_self:
            inotify_events = self._inotify.read_events()
            grouped_events = self._group_events(inotify_events)
            for inotify_event in grouped_events:
                delay = not isinstance(inotify_event, tuple) and inotify_event.is_moved_from
                self._queue.put(inotify_event, delay)
                if not isinstance(inotify_event, tuple) and inotify_event.is_delete_self and inotify_event.src_path == self._inotify.path:
                    deleted_self = True
