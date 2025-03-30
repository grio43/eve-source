#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\res_live_reload.py
import logging
import os
import stat
import time
import blue
from carbon.common.lib.codereloading import FileSystemObserver
from watchdog.events import FileSystemEventHandler
log = logging.getLogger(__name__)

class ResLiveReloader(FileSystemEventHandler):

    def __init__(self):
        super(ResLiveReloader, self).__init__()
        self._started_at = int(time.time())
        self._processed = {}
        self._watches = []
        self._filesystem_observer = None

    def start(self):
        if not self._watches:
            self._watches = self._start_watching_res_folders()

    def stop(self):
        for watch in self._watches:
            FileSystemObserver().unschedule(watch)

        self.watches = []

    def toggle(self):
        if not self._watches:
            self.start()
        else:
            self.stop()

    def on_modified(self, event):
        super(ResLiveReloader, self).on_modified(event)
        if not event.is_directory:
            return
        to_reload = []
        for resource_path, resource in blue.motherLode.items():
            if resource_path.endswith('atlas'):
                resource_path = resource_path[:-len('atlas')]
            file_path = blue.paths.ResolvePathForWriting(resource_path)
            if not os.path.exists(file_path):
                continue
            file_date = get_modified_time(file_path)
            last_update = self._processed.get(file_path, self._started_at)
            if file_date > last_update:
                to_reload.append(resource)
                self._processed[file_path] = file_date

        for resource in to_reload:
            self._reload_resource(resource)

    def _reload_resource(self, resource):
        try:
            if resource and hasattr(resource, 'Reload'):
                resource.Reload()
        except Exception:
            log.exception('Failed to reload resource')

    def _start_watching_res_folders(self):
        paths = [blue.paths.ResolvePathForWriting('res:/')]
        watches = []
        for path in paths:
            watches.append(FileSystemObserver().schedule(self, path, recursive=True))

        return watches

    def __del__(self):
        self.stop()


def get_modified_time(path):
    return os.stat(path)[stat.ST_MTIME]
