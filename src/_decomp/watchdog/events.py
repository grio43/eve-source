#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\watchdog\events.py
import os.path
import logging
import re
from pathtools.patterns import match_any_paths
from watchdog.utils import has_attribute
from watchdog.utils import unicode_paths
EVENT_TYPE_MOVED = 'moved'
EVENT_TYPE_DELETED = 'deleted'
EVENT_TYPE_CREATED = 'created'
EVENT_TYPE_MODIFIED = 'modified'
EVENT_TYPE_CLOSED = 'closed'

class FileSystemEvent(object):
    event_type = None
    is_directory = False
    is_synthetic = False

    def __init__(self, src_path):
        self._src_path = src_path

    @property
    def src_path(self):
        return self._src_path

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<%(class_name)s: event_type=%(event_type)s, src_path=%(src_path)r, is_directory=%(is_directory)s>' % dict(class_name=self.__class__.__name__, event_type=self.event_type, src_path=self.src_path, is_directory=self.is_directory)

    @property
    def key(self):
        return (self.event_type, self.src_path, self.is_directory)

    def __eq__(self, event):
        return self.key == event.key

    def __ne__(self, event):
        return self.key != event.key

    def __hash__(self):
        return hash(self.key)


class FileSystemMovedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_MOVED

    def __init__(self, src_path, dest_path):
        super(FileSystemMovedEvent, self).__init__(src_path)
        self._dest_path = dest_path

    @property
    def dest_path(self):
        return self._dest_path

    @property
    def key(self):
        return (self.event_type,
         self.src_path,
         self.dest_path,
         self.is_directory)

    def __repr__(self):
        return '<%(class_name)s: src_path=%(src_path)r, dest_path=%(dest_path)r, is_directory=%(is_directory)s>' % dict(class_name=self.__class__.__name__, src_path=self.src_path, dest_path=self.dest_path, is_directory=self.is_directory)


class FileDeletedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_DELETED


class FileModifiedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_MODIFIED


class FileCreatedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_CREATED


class FileMovedEvent(FileSystemMovedEvent):
    pass


class FileClosedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_CLOSED


class DirDeletedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_DELETED
    is_directory = True


class DirModifiedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_MODIFIED
    is_directory = True


class DirCreatedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_CREATED
    is_directory = True


class DirMovedEvent(FileSystemMovedEvent):
    is_directory = True


class FileSystemEventHandler(object):

    def dispatch(self, event):
        self.on_any_event(event)
        {EVENT_TYPE_CREATED: self.on_created,
         EVENT_TYPE_DELETED: self.on_deleted,
         EVENT_TYPE_MODIFIED: self.on_modified,
         EVENT_TYPE_MOVED: self.on_moved,
         EVENT_TYPE_CLOSED: self.on_closed}[event.event_type](event)

    def on_any_event(self, event):
        pass

    def on_moved(self, event):
        pass

    def on_created(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        pass

    def on_closed(self, event):
        pass


class PatternMatchingEventHandler(FileSystemEventHandler):

    def __init__(self, patterns = None, ignore_patterns = None, ignore_directories = False, case_sensitive = False):
        super(PatternMatchingEventHandler, self).__init__()
        self._patterns = patterns
        self._ignore_patterns = ignore_patterns
        self._ignore_directories = ignore_directories
        self._case_sensitive = case_sensitive

    @property
    def patterns(self):
        return self._patterns

    @property
    def ignore_patterns(self):
        return self._ignore_patterns

    @property
    def ignore_directories(self):
        return self._ignore_directories

    @property
    def case_sensitive(self):
        return self._case_sensitive

    def dispatch(self, event):
        if self.ignore_directories and event.is_directory:
            return
        paths = []
        if has_attribute(event, 'dest_path'):
            paths.append(unicode_paths.decode(event.dest_path))
        if event.src_path:
            paths.append(unicode_paths.decode(event.src_path))
        if match_any_paths(paths, included_patterns=self.patterns, excluded_patterns=self.ignore_patterns, case_sensitive=self.case_sensitive):
            super(PatternMatchingEventHandler, self).dispatch(event)


class RegexMatchingEventHandler(FileSystemEventHandler):

    def __init__(self, regexes = None, ignore_regexes = None, ignore_directories = False, case_sensitive = False):
        super(RegexMatchingEventHandler, self).__init__()
        if regexes is None:
            regexes = ['.*']
        if ignore_regexes is None:
            ignore_regexes = []
        if case_sensitive:
            self._regexes = [ re.compile(r) for r in regexes ]
            self._ignore_regexes = [ re.compile(r) for r in ignore_regexes ]
        else:
            self._regexes = [ re.compile(r, re.I) for r in regexes ]
            self._ignore_regexes = [ re.compile(r, re.I) for r in ignore_regexes ]
        self._ignore_directories = ignore_directories
        self._case_sensitive = case_sensitive

    @property
    def regexes(self):
        return self._regexes

    @property
    def ignore_regexes(self):
        return self._ignore_regexes

    @property
    def ignore_directories(self):
        return self._ignore_directories

    @property
    def case_sensitive(self):
        return self._case_sensitive

    def dispatch(self, event):
        if self.ignore_directories and event.is_directory:
            return
        paths = []
        if has_attribute(event, 'dest_path'):
            paths.append(unicode_paths.decode(event.dest_path))
        if event.src_path:
            paths.append(unicode_paths.decode(event.src_path))
        if any((r.match(p) for r in self.ignore_regexes for p in paths)):
            return
        if any((r.match(p) for r in self.regexes for p in paths)):
            super(RegexMatchingEventHandler, self).dispatch(event)


class LoggingEventHandler(FileSystemEventHandler):

    def __init__(self, logger = None):
        super(LoggingEventHandler, self).__init__()
        self.logger = logger or logging.root

    def on_moved(self, event):
        super(LoggingEventHandler, self).on_moved(event)
        what = 'directory' if event.is_directory else 'file'
        self.logger.info('Moved %s: from %s to %s', what, event.src_path, event.dest_path)

    def on_created(self, event):
        super(LoggingEventHandler, self).on_created(event)
        what = 'directory' if event.is_directory else 'file'
        self.logger.info('Created %s: %s', what, event.src_path)

    def on_deleted(self, event):
        super(LoggingEventHandler, self).on_deleted(event)
        what = 'directory' if event.is_directory else 'file'
        self.logger.info('Deleted %s: %s', what, event.src_path)

    def on_modified(self, event):
        super(LoggingEventHandler, self).on_modified(event)
        what = 'directory' if event.is_directory else 'file'
        self.logger.info('Modified %s: %s', what, event.src_path)


def generate_sub_moved_events(src_dir_path, dest_dir_path):
    for root, directories, filenames in os.walk(dest_dir_path):
        for directory in directories:
            full_path = os.path.join(root, directory)
            renamed_path = full_path.replace(dest_dir_path, src_dir_path) if src_dir_path else None
            event = DirMovedEvent(renamed_path, full_path)
            event.is_synthetic = True
            yield event

        for filename in filenames:
            full_path = os.path.join(root, filename)
            renamed_path = full_path.replace(dest_dir_path, src_dir_path) if src_dir_path else None
            event = FileMovedEvent(renamed_path, full_path)
            event.is_synthetic = True
            yield event


def generate_sub_created_events(src_dir_path):
    for root, directories, filenames in os.walk(src_dir_path):
        for directory in directories:
            event = DirCreatedEvent(os.path.join(root, directory))
            event.is_synthetic = True
            yield event

        for filename in filenames:
            event = FileCreatedEvent(os.path.join(root, filename))
            event.is_synthetic = True
            yield event
