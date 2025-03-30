#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\codereloading.py
import __builtin__
import inspect
import logging
import os
import Queue
import sys
import time
import traceback
import weakref
import blue
import signals
import uthread
from codereload import xreload
from eveprefs import prefs
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class CodeReloadHandler(FileSystemEventHandler):
    EXCLUDED_FOLDERS = [ os.path.normpath(folder) for folder in ['packages/audio2',
     'packages/d3dinfo',
     'packages/destiny',
     'packages/eveLocalization',
     'packages/geo2',
     'packages/geo2helpers',
     'packages/imageutils',
     'packages/inputmethod',
     'packages/pyFSD',
     'packages/spacemouse',
     'packages/videoplayer'] ]

    def __init__(self):
        super(CodeReloadHandler, self).__init__()
        self._reload_queue = Queue.Queue()
        self.on_file_reloaded = signals.Signal()
        self.on_file_reload_failed = signals.Signal()
        uthread.new(self._monitor_reload_queue, weakref.ref(self))

    @staticmethod
    def _monitor_reload_queue(self_ref):
        while True:
            self = self_ref()
            if self is None:
                return
            while not self._reload_queue.empty():
                try:
                    filename = self._reload_queue.get_nowait()
                except Queue.Empty:
                    break

                self.reload_file(filename)

            del self
            blue.pyos.synchro.Yield()

    def on_modified(self, event):
        super(CodeReloadHandler, self).on_modified(event)
        if event.is_directory:
            return
        logger.debug('File modification detected: %s', event)
        self._reload_queue.put(event.src_path, block=False)

    def on_moved(self, event):
        super(CodeReloadHandler, self).on_moved(event)
        if event.is_directory:
            return
        logger.debug('File move modification detected: %s', event)
        self._reload_queue.put(event.dest_path, block=False)

    def reload_file(self, filename):
        orig_filename = filename
        logger.debug('enter reload_file(%s)', orig_filename)
        filename = os.path.normpath(os.path.abspath(filename))
        for excluded_folder in self.EXCLUDED_FOLDERS:
            if excluded_folder in filename:
                logger.debug('reload_file[%s] excluded because of excluded_folder[%s]' % (filename, excluded_folder))
                return

        if filename[-3:] != '.py':
            return

        def find_module(filename):
            filename = os.path.normpath(filename)
            normalized_case_filename = os.path.normcase(filename)
            for prefix in sys.path[1:]:
                prefix = os.path.normcase(os.path.normpath(prefix))
                if not normalized_case_filename.startswith(prefix):
                    continue
                p, f = os.path.split(filename)
                if not f:
                    logger.error('Unexpected missing module name for filename %s', filename)
                    continue
                p = p[len(prefix) + len(os.path.sep):]
                p = p.replace(os.path.sep, '.')
                f = f[:-3]
                if f != '__init__':
                    if p:
                        p = p + '.' + f
                    else:
                        p = f
                m = sys.modules.get(p, None)
                if m is not None:
                    return m

        module = find_module(filename)
        if module is None:
            logger.error('Could not find module to reload for filename %s', orig_filename)
        else:
            try:
                t = time.time()
                with open(filename) as stream:
                    source = stream.read() + '\n'
                seconds_read = time.time() - t
                logger.info('Compiling %s using source %s', module.__name__, filename)
                code = compile(source, filename, 'exec')
                logger.info('Reloading %s', module)
                seconds_compile = time.time() - t - seconds_read
                xreload(module, code)
                uthread.new(self.on_file_reloaded, filename, module)
                seconds_total = time.time() - t
                seconds_xreload = seconds_total - seconds_compile
                logger.info('Reloaded %s in %.3f seconds (read: %.3f seconds, compile: %.3f seconds, xreload: %.3f seconds)', module, seconds_total, seconds_read, seconds_compile, seconds_xreload)
            except Exception:
                logger.exception('reload_file failed for %s', filename)
                self.on_file_reload_failed(filename, sys.exc_info())


class FsdReloadHandler(FileSystemEventHandler):

    def __init__(self):
        super(FsdReloadHandler, self).__init__()

    def on_modified(self, event):
        super(FsdReloadHandler, self).on_modified(event)
        logger.debug('FSD modification detected: %s', event.src_path)
        try:
            from fsdBuiltData.common.base import BuiltDataLoader
        except ImportError:
            logger.exception('Failed importing fsdBuiltData')
            return

        for subClass in BuiltDataLoader.__subclasses__():
            try:
                if subClass.CheckReloadDataFromDisk():
                    logger.info('Reloaded FSD data for %s: %s', subClass.__name__, subClass.GetAutobuildFilePath())
            except Exception:
                logger.exception('Failed to reload FSD data')


def _OnFileReloaded(filename, module):
    try:
        sm = getattr(__builtin__, 'sm', None)
        if sm is None:
            logger.warn(' sm not defined, cannot reload services.')
            return
        guids = [ cls.__guid__[4:] for name, cls in inspect.getmembers(module, inspect.isclass) if getattr(cls, '__guid__', '').startswith('svc.') ]
        sm.Reload(set(guids))
        reloadHook = getattr(module, '__SakeReloadHook', None)
        if reloadHook is not None:
            reloadHook()
        logger.info('Reloaded %s', filename)
        print 'Reloaded', filename
    except Exception:
        logger.exception('Unhandled exception in _OnFileReloaded')


def _OnFileReloadFailed(filename, exc_info):
    sys.stderr.write('Failed to reload: %s\n' % filename)
    traceback.print_exception(*exc_info)


__SAKE_INSTALLATION_ATTEMPTED = False
__OBSERVER = None
__WATCHES = []

def FileSystemObserver():
    global __OBSERVER
    if __OBSERVER is None:
        __OBSERVER = Observer()
    return __OBSERVER


def InstallSakeAutocompiler():
    global __SAKE_INSTALLATION_ATTEMPTED
    if not __SAKE_INSTALLATION_ATTEMPTED:
        if prefs.clusterMode == 'LOCAL' and not blue.pyos.packaged:
            try:
                InitializeCodeReloadSpy()
                InitializeFSDReloadSpy()
            except Exception:
                logger.exception('sake AutoCompiler failed to install.')

        else:
            logger.info('Skipping sake AutoCompiler installation.')
        if __OBSERVER is not None:
            __OBSERVER.start()
            logger.info('AutoCompiler installation complete.')
        __SAKE_INSTALLATION_ATTEMPTED = True
    else:
        logger.info('Tried to install sake AutoCompiler but already installed.')


def InitializeCodeReloadSpy(onFileReloaded = _OnFileReloaded, onFileReloadFailed = _OnFileReloadFailed):
    global __WATCHES
    blueSpy = CodeReloadHandler()
    blueSpy.on_file_reloaded.connect(onFileReloaded)
    blueSpy.on_file_reload_failed.connect(onFileReloadFailed)

    def filterOutSubPaths(paths):
        newPaths = []
        for absPath, relPath in sorted([ (os.path.normcase(os.path.abspath(path) + os.sep), path) for path in paths ]):
            if not len([ path for path, _ in newPaths if absPath.startswith(path) ]):
                newPaths.append((absPath, relPath))

        return [ path for _, path in newPaths ]

    paths = filterOutSubPaths(blue.paths.GetExpandedSearchPaths()['lib'])
    for path in paths:
        logger.info('Observing: %s', path)
        __WATCHES.append(FileSystemObserver().schedule(blueSpy, path, recursive=True))

    logger.info('Installed sake AutoCompiler.' + repr(paths))


def InitializeFSDReloadSpy(boot_role = None):
    from fsd import GetBranchRoot, GetFullName, AbsJoin
    from eveprefs import boot
    branch_root = GetBranchRoot()
    if boot_role is None:
        boot_role = boot.role
    if boot_role == 'server':
        paths = [GetFullName(AbsJoin(branch_root, 'eve/autobuild/staticData/server'))]
    elif boot_role == 'client':
        paths = [GetFullName(AbsJoin(branch_root, 'eve/autobuild/staticData/client'))]
    else:
        return
    handler = FsdReloadHandler()
    for path in paths:
        __WATCHES.append(FileSystemObserver().schedule(handler, path, recursive=True))


def OnFSDReload(path):
    from fsdBuiltData.common.base import BuiltDataLoader
    for subClass in BuiltDataLoader.__subclasses__():
        try:
            if subClass.CheckReloadDataFromDisk():
                print 'Reloaded FSD data for %s: %s' % (subClass.__name__, subClass.GetAutobuildFilePath())
        except:
            logger.exception('Failed to reload FSD data')
