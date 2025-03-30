#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\remotefilecache\__init__.py
import sys
__author__ = 'snorri.sturluson'
import platform
import logging
import os
import blue
import uthread2
import walk
from backgrounddownloadmanager import BackgroundDownloadManager
log = logging.getLogger('remotefilecache')

def ccp_platform_id():
    if platform.system() == 'Darwin':
        platform_id = 'macOS'
    elif platform.system() == 'Windows':
        platform_id = 'Windows'
    else:
        RuntimeError('Platform %s not supported!' % platform.system())
    return platform_id


def get_default_resource_index_file_list():
    resfileIndices = ['resfileindex.txt']
    suffix = ccp_platform_id()
    resfileIndices.append('resfileindex_%s.txt' % suffix)
    return resfileIndices


def get_default_cache_folder():
    if sys.platform == 'darwin':
        program_data_folder = blue.sysinfo.GetUserApplicationDataDirectory()
        return os.path.join(program_data_folder, 'EVE Online', 'SharedCache', 'ResFiles')
    else:
        program_data_folder = blue.sysinfo.GetSharedApplicationDataDirectory()
        if not program_data_folder:
            program_data_folder = 'C:\\'
        folder = os.path.join(program_data_folder, 'CCP', 'EVE', 'SharedCache', 'ResFiles')
        return folder


def prepare_for_package_tests():
    blue.paths.RegisterFileSystemAfterLocal('Remote')
    set_cache_folder(get_default_cache_folder())
    resfileIndices = get_default_resource_index_file_list()
    resfileIndices = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eve', 'client', indexfile) for indexfile in resfileIndices ]
    prepare(resfileIndices)


def set_cache_folder(location):
    blue.remoteFileCache.cacheFolder = location
    for i in xrange(256):
        folder_name = os.path.join(location, '%2.2x' % i)
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)


def prepare(index_list, server = 'http://res.eveprobe.ccpgames.com/', prefix = ''):
    blue.remoteFileCache.server = server
    blue.remoteFileCache.prefix = prefix
    blue.remoteFileCache.backupServer = 'https://clientresources.eveonline.com/'
    for index in index_list:
        log.debug('Loading index from %s' % index)
        stream = blue.paths.open(index, 'r')
        blue.remoteFileCache.AddFileIndex(stream.Read())


def gather_files_to_prefetch(folder, file_set):
    if not blue.paths.IsFileSystemRegistered('Remote'):
        return
    for path, dirs, files in walk.walk(folder):
        for f in files:
            filename = path + '/' + f
            if not blue.paths.FileExistsLocally(filename):
                file_set.add(filename)


def add_file_if_needs_download(file_set, filename):
    if blue.remoteFileCache.FileExists(filename) and not blue.paths.FileExistsLocally(filename):
        file_set.add(filename)


def gather_files_conditionally_to_prefetch(folder, condition, file_set, dependency_map):
    for path, dirs, files in walk.walk(folder):
        for f in files:
            blue.pyos.BeNice()
            basename, extension = os.path.splitext(f)
            if extension == '.red':
                f = basename + '.black'
            if not condition(f):
                continue
            filename = path + '/' + f
            add_file_if_needs_download(file_set, filename)
            dependencies = dependency_map.get(filename, [])
            for each in dependencies:
                blue.pyos.BeNice()
                add_file_if_needs_download(filename, each)


def prefetch_single_file(filename, verify = False):
    basename, extension = os.path.splitext(filename)
    if extension == '.red':
        filename = basename + '.black'
    if blue.paths.IsFileSystemRegistered('Remote'):
        if blue.remoteFileCache.FileExists(filename):
            if not blue.paths.FileExistsLocally(filename) or verify:
                blue.paths.GetFileContentsWithYield(filename)
    return blue.paths.ResolvePath(filename)


def prefetch_files(file_set):
    uthread2.map(prefetch_single_file, file_set)


def prefetch_folder(folder):
    file_set = set()
    gather_files_to_prefetch(folder, file_set)
    prefetch_files(file_set)


_bgdm = BackgroundDownloadManager()

def schedule(key, file_set):
    _bgdm.schedule(key, file_set)


def cancel(key):
    _bgdm.cancel(key)


def pull_to_front(key):
    _bgdm.pull_to_front(key)


def push_to_back(key):
    _bgdm.push_to_back(key)


def get_queue():
    return _bgdm.sets


def pause():
    _bgdm.stop()


def resume():
    _bgdm.start()
