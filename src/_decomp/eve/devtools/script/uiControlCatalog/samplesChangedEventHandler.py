#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\samplesChangedEventHandler.py
import os
import uthread2
from signals import Signal
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
PATH = os.path.abspath(os.path.dirname(__file__)) + '\\controls'
OBSERVER = None
_on_samples_added_or_removed = Signal('_on_samples_added_or_removed')
_on_sample_modified = Signal('_on_sample_file_modified')

def register_for_sample_modified_event(callback):
    _initialize_observer()
    _on_sample_modified.clear()
    _on_sample_modified.connect(callback)


def register_for_sample_added_or_removed(callback):
    _initialize_observer()
    _on_samples_added_or_removed.clear()
    _on_samples_added_or_removed.connect(callback)


def _initialize_observer():
    global OBSERVER
    if not OBSERVER:
        OBSERVER = Observer()
        handler = _SamplesChangedEventHandler()
        OBSERVER.schedule(handler, PATH, recursive=True)
        OBSERVER.start()


def is_py_file(event):
    return event.src_path.split('.')[-1] == 'py'


class _SamplesChangedEventHandler(FileSystemEventHandler):
    _modified_pending = None
    _add_or_remove_pending = None

    def __init__(self):
        uthread2.start_tasklet(self.callback_thread)

    def callback_thread(self):
        while True:
            if self._modified_pending:
                _on_sample_modified(self._modified_pending)
                self._modified_pending = None
            if self._add_or_remove_pending:
                _on_samples_added_or_removed(self._add_or_remove_pending)
                self._add_or_remove_pending = None
            uthread2.sleep(0.1)

    def on_modified(self, event):
        self._on_modified(event)

    def _on_modified(self, event):
        if is_py_file(event):
            self._modified_pending = event

    def on_moved(self, event):
        self._on_add_or_remove(event)

    def on_deleted(self, event):
        self._on_add_or_remove(event)

    def on_created(self, event):
        self._on_add_or_remove(event)

    def _on_add_or_remove(self, event):
        if is_py_file(event):
            self._add_or_remove_pending = event
