#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdlite\storage.py
import os
import time
import fnmatch
import fsdlite
import threading
import weakref
import collections
import logging
from fsd import GetBranchRoot, AbsJoin, GetFullName
try:
    from watchdog.events import FileSystemEventHandler
except ImportError:
    FileSystemEventHandler = object

try:
    from scandir import walk
except ImportError:
    from os import walk

from eveprefs import boot
logger = logging.getLogger(__name__)
try:
    import P4
except ImportError:
    P4 = None

try:
    from blinker import signal
except ImportError:
    signal = None

FORCE_FILE_MONITOR = None

class Storage(collections.MutableMapping):

    def __init__(self, data = None, cache = None, mapping = None, indexes = None, monitor = False, coerce = None, readonly = False):
        self.extension = '.staticdata'
        self.cache_path = cache
        self.cache_filename = self._get_cache_filename(self.cache_path)
        self.subscribe_close_cache_signal()
        self.coerce = coerce or str
        self.immutable = True
        self.file_monitor = None
        self._files = None
        self._fileLoaderThread = None
        self.objects = {}
        self._path = GetFullName(os.path.abspath(data)) if data else None
        self._cache = None
        self._mapping = mapping
        self._indexes = indexes
        if FORCE_FILE_MONITOR is None:
            self.monitor = monitor
        else:
            self.monitor = FORCE_FILE_MONITOR
        self.waiting = False
        self.readonly = readonly

    def initializeFileIndex(self):
        if self._fileLoaderThread is None:
            self._fileLoaderThread = FileLoaderThread(self)
            self._fileLoaderThread.start()

    def invalidateFileIndex(self):
        if self._fileLoaderThread is not None:
            self._fileLoaderThread.kill()
        self._files = None
        self._fileLoaderThread = None

    def resetFileIndex(self):
        self.invalidateFileIndex()
        self.initializeFileIndex()

    @property
    def files(self):
        self.initializeFileIndex()
        if self._fileLoaderThread.isAlive():
            self._fileLoaderThread.join()
        return self._files

    def __getitem__(self, key):
        if key is None:
            raise KeyError
        try:
            return self._object_load(key)
        except KeyError:
            pass

        try:
            file_time = self._file_time(key)
            cache_time = self._cache_time(key)
            if cache_time >= file_time:
                return self._cache_load(key)
        except KeyError:
            pass

        return self._file_load(key)

    def __setitem__(self, key, item):
        if self.immutable:
            raise RuntimeError('FSD Storage is Immutable')
        old_monitor, self.monitor = self.monitor, False
        self._file_save(key, item)
        self._cache_save(key, item)
        self._object_save(key, item)
        self.monitor = old_monitor

    def __delitem__(self, key):
        if self.immutable:
            raise RuntimeError('FSD Storage is Immutable')
        if self.path:
            try:
                filepath = self._file_path(key)
                Delete(filepath)
                self._file_index(filepath)
                return
            except P4.P4Exception as exception:
                raise KeyError(exception)

    def __len__(self):
        return len(self.keys())

    def __iter__(self):
        return iter(self.keys())

    def __enter__(self):
        if not self.readonly:
            self.immutable = False

    def __exit__(self, *args):
        self.immutable = True

    def __contains__(self, key):
        try:
            key = self.coerce(key)
        except TypeError:
            return False

        if key in self.objects:
            return True
        elif self.files:
            return key in self.files
        elif self.cache:
            return key in self.cache
        else:
            return False

    @property
    def path(self):
        return self._path

    @property
    def mapping(self):
        return self._mapping

    @property
    def indexes(self):
        return self._indexes

    @path.setter
    def path(self, value):
        if self.objects:
            self.objects.clear()
        if self.cache:
            self.cache.clear()
        self._path = GetFullName(os.path.abspath(value))
        self.resetFileIndex()
        self.monitor = self.monitor

    def keys(self):
        if self.files:
            return [ self.coerce(key) for key in self.files.keys() ]
        if self.cache:
            return [ self.coerce(key) for key in self.cache.keys() ]
        return []

    def Get(self, key):
        return self[key]

    def _get_cache_filename(self, cache_path):
        if cache_path:
            _, filename = os.path.split(cache_path)
            return filename

    def prime(self, path = None):
        keys = set(self.keys())
        for key, (filename, timestamp) in self.files.iteritems():
            if path is None or fnmatch.fnmatch(filename, path):
                keys.add(self.coerce(key))

        for key in keys:
            self[key]

    def prime_key(self, key):
        self[key]

    def prime_file(self, file_path):
        self._file_index(file_path)

    def filter_keys(self, name, key):
        if self.cache:
            return [ self.coerce(key) for key in self.cache.index('{}.{}'.format(name, key)) ]
        return []

    def filter(self, name, key):
        return [ self[key] for key in self.filter_keys(name, key) ]

    def index(self, name, key):
        try:
            return self.filter(name, key)[0]
        except IndexError:
            raise KeyError

    def key_path(self, key):
        return self._file_path(key)

    def signal_receiver(self, filepaths):
        if self.cache_path in filepaths:
            self.close_cache_connection()

    def subscribe_close_cache_signal(self):
        if signal is not None:
            sub = signal('building_static_datafiles')
            sub.connect(self.signal_receiver)

    def disable_cache(self):
        if self._cache:
            self._cache.close()
            self._cache = None
        if self.cache_path:
            self.cache_path = None

    @classmethod
    def close_cache_connections(cls):
        for _, connection in fsdlite.Cache._connections.iteritems():
            connection.commit()
            connection.close()

        fsdlite.Cache._connections = {}

    def close_cache_connection(self):
        if self._cache is not None:
            connection = self._cache._connections.get(self.cache_path, None)
            if connection:
                connection.commit()
                connection.close()
            if self.cache_path in fsdlite.Cache._connections:
                del fsdlite.Cache._connections[self.cache_path]

    def _object_load(self, key):
        return self.objects[self.coerce(key)]

    def _object_save(self, key, obj):
        key = self.coerce(key)
        self.objects[key] = obj

    def _object_discard(self, key):
        key = self.coerce(key)
        self.objects.pop(key, None)

    def _cache_load(self, key):
        if self.cache:
            data = self.cache[self.coerce(key)]
            obj = fsdlite.decode(data, mapping=self.mapping, json=True)
            self._object_save(key, obj)
            return obj
        raise KeyError('No Cache')

    def _cache_save(self, key, obj):
        if self.cache:
            key = self.coerce(key)
            self.cache[key] = fsdlite.encode(obj, json=True)
            self.cache.index_clear(key)
            for indexName, indexKeys in fsdlite.index(obj, self.indexes).iteritems():
                for indexKey in indexKeys:
                    self.cache.index_set('{}.{}'.format(indexName, indexKey), key)

    def _cache_discard(self, key):
        if self.cache:
            try:
                key = self.coerce(key)
                del self.cache[key]
                self.cache.index_clear(key)
            except KeyError:
                pass

    def _cache_time(self, key):
        if self.cache:
            try:
                return self.cache.time(self.coerce(key))
            except KeyError:
                pass

        return 0

    def _set_cache(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError('Cache path must be a string')
        self.cache_path = value
        self._cache = None

    def _get_cache(self):
        if self.cache_path and self._cache is None:
            self._cache = fsdlite.Cache(self.cache_path)
        return self._cache

    cache = property(_get_cache, _set_cache)

    def file_init(self):
        if self._files is None:
            logger.debug("Initializing file cache for path '{}'".format(self.path))
            self._files = {}
            if self.path and os.path.isdir(self.path):
                for base, directories, files in walk(self.path):
                    for filename in files:
                        self._file_index(os.path.join(base, filename))

            logger.debug('File cache initialization complete')

    def _file_index(self, filename):
        if fnmatch.fnmatch(filename, '*' + self.extension):
            key = self.coerce(self._file_key(filename))
            if os.path.exists(filename):
                modified = os.path.getmtime(filename)
                self._files[key] = (filename, modified)
            else:
                self._files.pop(key, None)
            return key

    def _file_changed(self, event, filename):
        key = self._file_index(filename)
        if key is not None:
            self._object_discard(key)
            self._cache_discard(key)
            self.prime_key(key)
            self._on_file_load(key)
            self.waiting = False

    def _file_deleted(self, event, filepath):
        if not os.path.exists(filepath):
            key = self._file_index(filepath)
            if key is not None:
                self._object_discard(key)
                self._cache_discard(key)

    def _on_file_load(self, key):
        pass

    def _file_index_on_key(self, key):
        file_path = self._file_path(key)
        if not os.path.exists(file_path):
            return
        self._file_index(file_path)

    def _file_load(self, key):
        if self.path:
            try:
                key = self.coerce(key)
                if key not in self.files:
                    self._file_index_on_key(key)
                filepath, modified = self.files[key]
                with open(filepath, 'r') as stream:
                    data = fsdlite.load(stream.read())
                    self._cache_save(key, data)
                    obj = fsdlite.decode(data, mapping=self.mapping)
                    self._object_save(key, obj)
                    return obj
            except IOError as exception:
                raise KeyError(exception)

        raise KeyError('No Static Data')

    def _file_save(self, key, obj):
        if self.path:
            try:
                filepath = self._file_path(key)
                Checkout(filepath)
                with open(filepath, 'w') as stream:
                    stream.write(fsdlite.dump(fsdlite.strip(obj)))
                self._file_index(filepath)
                return
            except IOError as exception:
                raise KeyError(exception)

        raise KeyError('No Static Data')

    def _file_time(self, key):
        if self.path:
            try:
                return self.files[self.coerce(key)][1]
            except KeyError:
                return time.time()

        return 0

    def _file_path(self, key):
        if self.path:
            return GetFullName(AbsJoin(self.path, str(key) + self.extension))
        raise RuntimeError('Unable to determine file path, no data path provided')

    def _file_key(self, path):
        if self.path:
            key, _ = os.path.splitext(os.path.relpath(path, self.path))
            return key.replace('\\', '/')
        raise RuntimeError('Unable to determine file key, no data path provided')

    def _get_monitor(self):
        return self.file_monitor is not None

    def _set_monitor(self, value):
        monitor = getattr(self, 'file_monitor', None)
        if monitor:
            fsdlite.stop_file_monitor(monitor)
            self.file_monitor = None
        if value and self.path:
            file_handler = FileHandler(fsdlite.WeakMethod(self._file_changed), fsdlite.WeakMethod(self._file_deleted))
            self.file_monitor = fsdlite.start_file_monitor(self.path, file_handler=file_handler)

    monitor = property(_get_monitor, _set_monitor)

    def wait(self):
        self.waiting = True
        while self.waiting:
            pass


class FileHandler(FileSystemEventHandler):

    def __init__(self, modified_callback, deleted_callback):
        self.modified_callback = modified_callback
        self.deleted_callback = deleted_callback

    def on_created(self, event):
        if not event.is_directory:
            try:
                self.modified_callback(event.event_type, event.src_path)
            except Exception:
                logging.exception('Error handling file monitor on created event')

    def on_modified(self, event):
        if not event.is_directory and os.path.exists(event.src_path):
            try:
                self.modified_callback(event.event_type, event.src_path)
            except Exception:
                logging.exception('Error handling file monitor on modified event')

    def on_moved(self, event):
        if not event.is_directory:
            try:
                self.modified_callback(event.event_type, event.src_path)
            except Exception:
                logging.exception('Error handling file monitor on moved event')

    def on_deleted(self, event):
        if not event.is_directory:
            try:
                self.deleted_callback(event.event_type, event.src_path)
            except Exception:
                logging.exception('Error handling file monitor on deleted event')


class WeakStorage(Storage):

    def __init__(self, *args, **kwargs):
        Storage.__init__(self, *args, **kwargs)
        self.objects = weakref.WeakValueDictionary()


class EveStorage(Storage):

    def __init__(self, data, cache, on_file_load = None, *args, **kwargs):
        monitor = kwargs.get('monitor', True)
        try:
            import blue
            if blue.pyos.packaged:
                monitor = False
                data = None
                if boot.role == 'client':
                    import remotefilecache
                    logger.info('Prefetching %s', cache)
                    cache = remotefilecache.prefetch_single_file('res:/staticdata/' + cache, verify=True)
                    kwargs['readonly'] = True
                    logger.info('Prefetched %s', cache)
                else:
                    cache = os.path.join(blue.paths.ResolvePath(u'res:/staticdata'), cache)
            elif ShouldUseSource():
                data = os.path.join(blue.paths.ResolvePath(u'root:/staticData'), data)
                cache = os.path.join(blue.paths.ResolvePath(u'root:/autobuild/staticData/server'), cache)
            elif os.path.exists(blue.paths.ResolvePath(u'res:/staticdata')):
                data = None
                cache = os.path.join(blue.paths.ResolvePath(u'res:/staticdata'), cache)
            else:
                raise ImportError
        except ImportError:
            if data is not None and ShouldUseSource():
                data = AbsJoin(GetBranchRoot(), 'eve/staticData/', data)
                if not os.path.exists(data):
                    data = None
            if cache is not None:
                cache = AbsJoin(GetBranchRoot(), 'eve/autobuild/staticData/server', cache)
                if not os.path.exists(os.path.dirname(cache)):
                    cache = None
            if on_file_load is not None:
                self._on_file_load = on_file_load

        kwargs['monitor'] = monitor
        Storage.__init__(self, data, cache, *args, **kwargs)


class FileLoaderThread(threading.Thread):

    def __init__(self, storage):
        super(FileLoaderThread, self).__init__()
        self._storage = storage

    def run(self):
        self._storage.file_init()


SHOULD_USE_SOURCE = None

def ShouldUseSource():
    global SHOULD_USE_SOURCE
    if SHOULD_USE_SOURCE is None:
        SHOULD_USE_SOURCE = bool(int(os.environ.get('EVE_FSDLITE_USE_SOURCE', '1')))
        if not SHOULD_USE_SOURCE:
            print 'FsdLite Storage will not use source files for this run as environment variable is set to False'
    try:
        import blue
    except ImportError:
        return True

    return SHOULD_USE_SOURCE and os.path.exists(blue.paths.ResolvePath(u'root:/staticData'))


def DontUseSource():
    global SHOULD_USE_SOURCE
    SHOULD_USE_SOURCE = False


def UseSource():
    global SHOULD_USE_SOURCE
    SHOULD_USE_SOURCE = True


def Connection():
    if not hasattr(Connection, 'connection'):
        connection = P4.P4()
        connection.connect()
        Connection.connection = connection
    return Connection.connection


def Checkout(path):
    if P4:
        try:
            connection = Connection()
            try:
                connection.run_edit(path)
            except P4.P4Exception:
                connection.run_add(path)

        except P4.P4Exception as e:
            logger.exception('Perforce error.. %s', e)


def Delete(path):
    if P4:
        try:
            connection = Connection()
            connection.run_delete(path)
        except P4.P4Exception as e:
            logger.exception('Perforce error.. %s', e)
