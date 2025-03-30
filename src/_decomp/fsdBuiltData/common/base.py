#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\base.py
import os
import logging
import time
from fsd import AbsJoin, GetBranchRoot
from fsdBuiltData.common.paths import get_file_contents_with_yield, resolve_path
try:
    import monolithconfig
except ImportError:
    monolithconfig = None

from errors import NoBinaryLoaderError
from signals import Signal
log = logging.getLogger('fsdBuiltData')
IS_PACKAGED = False
IS_INTERPRETER = False
FSD_DATA_RELOAD = bool(int(os.getenv('FSD_DATA_RELOAD', '1')))
NO_BINARY_LOADER = object()

def ShouldUseResData():
    if monolithconfig is None:
        return False
    return monolithconfig.on_client() or monolithconfig.on_proxy() or monolithconfig.on_server()


def EnableUseResFileServer():
    UseResFileServer.__enabled__ = True


def DisableUseResFileServer():
    UseResFileServer.__enabled__ = False


def UseResFileServer():
    return getattr(UseResFileServer, '__enabled__', False)


useResData = ShouldUseResData()
if useResData:
    import blue
    IS_PACKAGED = blue.pyos.packaged
    IS_INTERPRETER = blue.pyos.interpreterMode
try:
    import fsd.schemas.binaryLoader as binaryLoader
except ImportError:
    import site
    branchRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    site.addsitedir(os.path.abspath(os.path.join(branchRoot, 'packages')))
    import fsd.schemas.binaryLoader as binaryLoader

class BuiltDataLoader(object):
    __binary__ = None
    __resBuiltFile__ = None
    __clientAutobuildBuiltFile__ = None
    __serverAutobuildBuiltFile__ = None
    __loader__ = NO_BINARY_LOADER
    __autoBuildFileTimeStamp__ = 0
    onReload = None

    @classmethod
    def _GetAutobuildBuiltFilePath(cls, name):
        if not name:
            return None
        autobuildFilePath = AbsJoin(GetBranchRoot(), name)
        if os.path.isfile(autobuildFilePath):
            return autobuildFilePath

    @classmethod
    def __LoadBinaryFromResFolder(cls):
        if cls.IsReloadEnabled():
            autobuild_file = cls.GetAutobuildFilePath()
            if autobuild_file:
                cls.__autoBuildFileTimeStamp__ = os.path.getmtime(autobuild_file)
        if cls.__loader__ is not NO_BINARY_LOADER:
            if cls.__loader__ is None:
                raise NoBinaryLoaderError()
            resolvedBuiltFile = resolve_path(cls.__resBuiltFile__)
            log.info('Trying to load cFSD file at %s', resolvedBuiltFile)
            if not IS_INTERPRETER or UseResFileServer():
                try:
                    get_file_contents_with_yield(cls.__resBuiltFile__)
                except RuntimeError as exc:
                    if str(exc) != 'Tasklet killed':
                        log.exception('Could not get cFSD file at %s', resolvedBuiltFile)
                    return

            if not os.path.exists(resolvedBuiltFile):
                log.error('Could not find cFSD file at %s', resolvedBuiltFile)
                return
            loaded = cls.__loader__.load(resolvedBuiltFile)
            if loaded is None:
                log.error('Could not load cFSD file at %s', resolvedBuiltFile)
            return loaded
        else:
            log.info('Trying to load regular FSD file at %s', cls.__resBuiltFile__)
            return binaryLoader.LoadFSDDataForCFG(cls.__resBuiltFile__)

    @classmethod
    def GetAutobuildFilePath(cls):
        clientAutobuildFilePath = cls._GetAutobuildBuiltFilePath(cls.__clientAutobuildBuiltFile__)
        serverAutobuildFilePath = cls._GetAutobuildBuiltFilePath(cls.__serverAutobuildBuiltFile__)
        if not clientAutobuildFilePath and not serverAutobuildFilePath:
            log.error("Failed to import binary autobuild data for BuiltDataLoader class '%s'", cls.__name__)
            return None
        tryClientFirst = not monolithconfig.on_proxy() and not monolithconfig.on_server()
        if tryClientFirst:
            return clientAutobuildFilePath or serverAutobuildFilePath
        return serverAutobuildFilePath or clientAutobuildFilePath

    @classmethod
    def __LoadBinaryFromAutobuildFolder(cls):
        autobuildFilePath = cls.GetAutobuildFilePath()
        if cls.__loader__ is not NO_BINARY_LOADER:
            if cls.__loader__ is None:
                raise NoBinaryLoaderError()
            log.info('Trying to load cFSD file from autobuild folder at %s', autobuildFilePath)
            loaded = cls.__loader__.load(autobuildFilePath)
            if loaded is None:
                log.error('Could not load cFSD file from autobuild folder at %s', autobuildFilePath)
            return loaded
        log.info('Trying to load regular FSD file from autobuild folder at %s', autobuildFilePath)
        return binaryLoader.LoadFSDDataInPython(autobuildFilePath)

    @classmethod
    def __LoadBinary(cls):
        if useResData:
            return cls.__LoadBinaryFromResFolder()
        return cls.__LoadBinaryFromAutobuildFolder()

    @classmethod
    def GetData(cls):
        if cls.__binary__ is None:
            cls.__binary__ = cls.__LoadBinary()
        return cls.__binary__

    @classmethod
    def IsReloadEnabled(cls):
        return not IS_PACKAGED and FSD_DATA_RELOAD

    @classmethod
    def CheckReloadDataFromDisk(cls):
        if not cls.__binary__ or not cls.IsReloadEnabled():
            return False
        autobuildFilePath = cls.GetAutobuildFilePath()
        if autobuildFilePath:
            timeStamp = os.path.getmtime(autobuildFilePath)
            if timeStamp > cls.__autoBuildFileTimeStamp__:
                cls.__autoBuildFileTimeStamp__ = timeStamp
                log.info('%s: Reloading FSD data from autoBuild folder', cls.__name__)
                tries = 10
                while tries:
                    try:
                        cls.ReloadDataFromDisk()
                        return True
                    except IOError as error:
                        tries -= 1
                        if not tries:
                            raise
                        log.debug('%s: Failed to reload FSD data from autoBuild folder. %s. Retries left: %d', cls.__name__, error, tries)
                        time.sleep(0.1)

    @classmethod
    def ReloadDataFromDisk(cls, *args):
        cls.__binary__ = cls.__LoadBinaryFromAutobuildFolder()
        if cls.onReload:
            cls.onReload()

    @classmethod
    def ConnectToOnReload(cls, callback):
        if not cls.onReload:
            cls.onReload = Signal()
        cls.onReload.connect(callback)
