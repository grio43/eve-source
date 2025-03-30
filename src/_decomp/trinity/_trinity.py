#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\_trinity.py
import logging as _logging
import os as _os
import platform as _platform
import blue as _blue
try:
    from _trinity_dx11_internal_stub import *
except ImportError:
    pass

_logger = _logging.getLogger('trinity')
from d3dinfo import availablePlatforms
from . import _utils
if _platform.system() == 'Darwin':
    DEFAULT_TRI_PLATFORM = 'metal'
elif _platform.system() == 'Windows':
    DEFAULT_TRI_PLATFORM = 'dx11'
else:
    raise ImportError('Cannot import trinity on an unsupported platform')

def _RobustImport(moduleName, moduleNameForFallback = None):
    try:
        mod = _blue.LoadExtension(moduleName)
    except ImportError as ex:
        if moduleNameForFallback:
            _logger.warn('Import failed on %s, falling back to %s ...' % (moduleName, moduleNameForFallback))
            mod = _blue.LoadExtension(moduleNameForFallback)
        else:
            _utils.Quit('Failed to import %s (%r)' % (moduleName, repr(ex)))

    for memberName in dir(mod):
        globals()[memberName] = getattr(mod, memberName)

    del mod


def _ImportDll():
    triPlatform = _os.getenv('TRINITYPLATFORM', DEFAULT_TRI_PLATFORM)
    disablePlatformCheck = _os.getenv('TRINITYNOPLATFORMCHECK')
    for arg in _blue.pyos.GetArg():
        arg = arg.lower()
        if arg.startswith('/triplatform'):
            s = arg.split('=')
            triPlatform = s[1]
        elif arg == '/no-platform-check':
            disablePlatformCheck = True

    if not disablePlatformCheck:
        if triPlatform.startswith('dx'):
            availablePlatforms.InstallDirectXIfNeeded()
        validPlatforms = availablePlatforms.GetAvailablePlatforms()
        if triPlatform not in validPlatforms:
            _logger.warn('Invalid Trinity platform %s' % triPlatform)
            triPlatform = validPlatforms[0]
            _logger.info('Using Trinity platform %s instead' % triPlatform)
    else:
        _logger.info('Skipping platform check')
    dllName = '_trinity_%s' % triPlatform
    _logger.debug('Starting up Trinity through %s ...' % dllName)
    _RobustImport(dllName)
    return triPlatform


def Load(path, nonCached = False):
    if nonCached:
        _blue.resMan.loadObjectCache.Delete(path)
    obj = _blue.resMan.LoadObject(path)
    return obj
