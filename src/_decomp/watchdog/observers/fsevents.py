#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\watchdog\observers\fsevents.py
import logging
import os
import sys
import threading
import unicodedata
import _watchdog_fsevents as _fsevents
from watchdog.events import FileDeletedEvent, FileModifiedEvent, FileCreatedEvent, FileMovedEvent, DirDeletedEvent, DirModifiedEvent, DirCreatedEvent, DirMovedEvent, generate_sub_created_events, generate_sub_moved_events
from watchdog.observers.api import BaseObserver, EventEmitter, DEFAULT_EMITTER_TIMEOUT, DEFAULT_OBSERVER_TIMEOUT
from watchdog.utils import unicode_paths
logger = logging.getLogger('fsevents')

class FSEventsEmitter(EventEmitter):

    def __init__(self, event_queue, watch, timeout = DEFAULT_EMITTER_TIMEOUT):
        EventEmitter.__init__(self, event_queue, watch, timeout)
        self._lock = threading.Lock()

    def on_thread_stop(self):
        if self.watch:
            _fsevents.remove_watch(self.watch)
            _fsevents.stop(self)
            self._watch = None

    def queue_event(self, event):
        logger.info('queue_event %s', event)
        EventEmitter.queue_event(self, event)

    def queue_events(self, timeout, events):
        if logger.getEffectiveLevel() <= logging.DEBUG:
            for event in events:
                flags = ', '.join((attr for attr in dir(event) if getattr(event, attr) is True))
                logger.debug('%s: %s', event, flags)

        while events:
            event = events.pop(0)
            src_path = self._encode_path(event.path)
            if event.is_renamed:
                dest_event = next(iter((e for e in events if e.is_renamed and e.inode == event.inode)), None)
                if dest_event:
                    events.remove(dest_event)
                    logger.debug('Destination event for rename is %s', dest_event)
                    cls = DirMovedEvent if event.is_directory else FileMovedEvent
                    dst_path = self._encode_path(dest_event.path)
                    self.queue_event(cls(src_path, dst_path))
                    self.queue_event(DirModifiedEvent(os.path.dirname(src_path)))
                    self.queue_event(DirModifiedEvent(os.path.dirname(dst_path)))
                    for sub_event in generate_sub_moved_events(src_path, dst_path):
                        logger.debug('Generated sub event: %s', sub_event)
                        self.queue_event(sub_event)

                elif os.path.exists(event.path):
                    cls = DirCreatedEvent if event.is_directory else FileCreatedEvent
                    self.queue_event(cls(src_path))
                    self.queue_event(DirModifiedEvent(os.path.dirname(src_path)))
                    for sub_event in generate_sub_created_events(src_path):
                        self.queue_event(sub_event)

                else:
                    cls = DirDeletedEvent if event.is_directory else FileDeletedEvent
                    self.queue_event(cls(src_path))
                    self.queue_event(DirModifiedEvent(os.path.dirname(src_path)))
            if event.is_created:
                cls = DirCreatedEvent if event.is_directory else FileCreatedEvent
                if not event.is_coalesced or event.is_coalesced and not event.is_renamed and not event.is_modified and not event.is_inode_meta_mod and not event.is_xattr_mod:
                    self.queue_event(cls(src_path))
                    self.queue_event(DirModifiedEvent(os.path.dirname(src_path)))
            if event.is_modified and not event.is_coalesced and os.path.exists(src_path):
                cls = DirModifiedEvent if event.is_directory else FileModifiedEvent
                self.queue_event(cls(src_path))
            if event.is_inode_meta_mod or event.is_xattr_mod:
                if os.path.exists(src_path) and not event.is_coalesced:
                    cls = DirModifiedEvent if event.is_directory else FileModifiedEvent
                    self.queue_event(cls(src_path))
            if event.is_removed:
                cls = DirDeletedEvent if event.is_directory else FileDeletedEvent
                if not event.is_coalesced or event.is_coalesced and not os.path.exists(event.path):
                    self.queue_event(cls(src_path))
                    self.queue_event(DirModifiedEvent(os.path.dirname(src_path)))
                    if src_path == self.watch.path:
                        logger.debug('Stopping because root path was removed')
                        self.stop()
            if event.is_root_changed:
                self.queue_event(DirDeletedEvent(self.watch.path))
                logger.debug('Stopping because root path was changed')
                self.stop()

    def run(self):
        try:

            def callback(paths, inodes, flags, ids, emitter = self):
                try:
                    with emitter._lock:
                        events = [ _fsevents.NativeEvent(path, inode, event_flags, event_id) for path, inode, event_flags, event_id in zip(paths, inodes, flags, ids) ]
                        emitter.queue_events(emitter.timeout, events)
                except Exception:
                    logger.exception('Unhandled exception in fsevents callback')

            self.pathnames = [self.watch.path]
            _fsevents.add_watch(self, self.watch, callback, self.pathnames)
            _fsevents.read_events(self)
        except Exception:
            logger.exception('Unhandled exception in FSEventsEmitter')

    def _encode_path(self, path):
        if isinstance(self.watch.path, unicode_paths.bytes_cls):
            return path.encode('utf-8')
        return path


class FSEventsObserver(BaseObserver):

    def __init__(self, timeout = DEFAULT_OBSERVER_TIMEOUT):
        BaseObserver.__init__(self, emitter_class=FSEventsEmitter, timeout=timeout)

    def schedule(self, event_handler, path, recursive = False):
        if isinstance(path, unicode_paths.str_cls):
            path = unicodedata.normalize('NFC', path)
            if sys.version_info < (3,):
                path = path.encode('utf-8')
        return BaseObserver.schedule(self, event_handler, path, recursive)
