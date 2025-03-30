#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\client\script\util\cacheDirectoryLimitSvc.py
import datetime
import os
import stat
import blue
import telemetry
import threading
import uthread
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_ANY
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class AutoPrunedDirectory(object):

    def __init__(self, directory, maxDirectorySizeInMB, maxAgeInDays = None):
        self.directory = directory
        self.maxDirectorySizeInMB = maxDirectorySizeInMB
        self.maxAgeInDays = maxAgeInDays
        self.currentSize = 0
        self.lastChecked = None


@telemetry.ZONE_FUNCTION
def ProcessCacheDirectory(cacheSvc, rootPath, d):
    filesInDirectory = []
    now = datetime.datetime.now()
    five_minutes = datetime.timedelta(minutes=5)
    max_age = None if d.maxAgeInDays is None else datetime.timedelta(days=d.maxAgeInDays)
    if d.lastChecked is not None:
        if now - d.lastChecked < five_minutes:
            return
    d.lastChecked = now
    d.currentSize = 0
    for r, _, files in os.walk(rootPath):
        for f in files:
            fullpath = os.path.join(r, f)
            fileSize = os.stat(fullpath)[stat.ST_SIZE]
            lastAccessed = datetime.datetime.fromtimestamp(os.path.getmtime(fullpath))
            if max_age is not None and now - lastAccessed > max_age:
                cacheSvc.LogInfo('Removing %s from cache. It was last accessed: %s' % (fullpath, lastAccessed))
                try:
                    os.remove(fullpath)
                except OSError:
                    continue

            else:
                d.currentSize += fileSize
                filesInDirectory.append((lastAccessed, fileSize, fullpath))

    currentSize = d.currentSize
    maxSize = d.maxDirectorySizeInMB * 1024 * 1024
    if currentSize > maxSize:
        cacheSvc.LogNotice('Cache Directory %s is over the allocated file size (%sMB, currently %sMB)' % (d.directory, d.maxDirectorySizeInMB, currentSize / 1048576.0))
        filesInDirectory.sort(reverse=True)
        while currentSize > maxSize:
            fileToDelete = filesInDirectory.pop()
            if now - fileToDelete[0] < five_minutes:
                break
            cacheSvc.LogInfo('Removing %s from cache. It was last accessed: %s' % (fileToDelete[2], fileToDelete[0]))
            try:
                os.remove(fileToDelete[2])
                currentSize -= fileToDelete[1]
            except OSError:
                continue

    else:
        cacheSvc.LogInfo('Cache Directory %s is currently %sMB (max %sMB)' % (d.directory, currentSize / 1048576.0, d.maxDirectorySizeInMB))


class FileHandler(FileSystemEventHandler):

    def __init__(self, cacheSvc, rootPath, dirInfo):
        self.cacheSvc = cacheSvc
        self.rootPath = rootPath
        self.dirInfo = dirInfo

    def _ProcessDirectoryInThreadClosure(self):
        ProcessCacheDirectory(self.cacheSvc, self.rootPath, self.dirInfo)

    def on_any_event(self, event):
        now = datetime.datetime.now()
        five_minutes = datetime.timedelta(minutes=5)
        if self.dirInfo.lastChecked is not None:
            if now - self.dirInfo.lastChecked < five_minutes:
                return
        thread = threading.Thread(target=self._ProcessDirectoryInThreadClosure)
        thread.start()


class CacheDirectoryLimitService(Service):
    __guid__ = 'svc.cacheDirectoryLimit'
    __exportedcalls__ = {'PruneCache': {'role': ROLE_ANY},
     'RegisterCacheDirectory': {'role': ROLE_ANY}}

    def __init__(self):
        super(CacheDirectoryLimitService, self).__init__()
        self.autoPruneDirectories = []
        self._observers = []

    def Run(self, *etc):
        Service.Run(self, *etc)
        self.RegisterCacheDirectory('Avatars', 1024, 5)
        self.PruneCache()

    def PruneCache(self):
        uthread.new(self._PruneCache_t)

    def _PruneCache_t(self):
        cacheDir = blue.paths.ResolvePath(u'cache:/')
        for d in self.autoPruneDirectories:
            rootPath = os.path.join(cacheDir, d.directory)
            uthread.CallOnThread(ProcessCacheDirectory, args=(self, rootPath, d))

    def RegisterCacheDirectory(self, directory, maxSize, maxLastAccessedAgeInDays = None):
        for d in self.autoPruneDirectories:
            if d.directory == directory:
                d.maxDirectorySizeInMB = maxSize
                d.maxAgeInDays = maxLastAccessedAgeInDays
                return

        cacheDir = blue.paths.ResolvePath(u'cache:/')
        rootPath = os.path.join(cacheDir, directory)
        d = AutoPrunedDirectory(directory, maxSize, maxLastAccessedAgeInDays)
        self.autoPruneDirectories.append(d)
        self.LogNotice('Setting up cache directory watch on %s' % rootPath)
        observer = Observer()
        try:
            observer.schedule(FileHandler(self, rootPath, d), rootPath, recursive=True)
            observer.start()
        except OSError:
            return

        self._observers.append(observer)
