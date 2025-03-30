#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdlite\monitor.py
import os
import logging
try:
    from watchdog.utils import platform
    if platform.is_windows():
        import watchdog.observers.winapi
        watchdog.observers.winapi.WATCHDOG_FILE_NOTIFY_FLAGS = 351
        import watchdog.observers.read_directory_changes

        def read_events(*args, **kwargs):
            try:
                return watchdog.observers.winapi.read_events(*args, **kwargs)
            except WindowsError:
                return []


        watchdog.observers.read_directory_changes.read_events = read_events
    import weakref
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    observers = weakref.WeakSet()

    class FileHandler(FileSystemEventHandler):

        def __init__(self, callback):
            self.callback = callback

        def on_any_event(self, event):
            if not event.is_directory:
                try:
                    self.callback(event.event_type, event.src_path)
                except Exception:
                    logging.exception('Error handling file monitor event')


    def start_file_monitor(path, callback = None, file_handler = None):
        if os.path.exists(path):
            if file_handler is not None:
                handler = file_handler
            elif callback is not None:
                handler = FileHandler(callback)
            else:
                logging.exception('Error when starting file monitor, key argument callback was None')
            observer = Observer()
            observer.schedule(handler, path, recursive=True)
            observer.start()
            observers.add(observer)
            return observer


    def stop_file_monitor(observer):
        if observer:
            observer.unschedule_all()
            observer.stop()
            observer.join()


    def stop_observers():
        for observer in observers:
            stop_file_monitor(observer)


except (ImportError, AttributeError):

    def start_file_monitor(path, callback = None, file_handler = None):
        return None


    def stop_file_monitor(observer):
        pass
