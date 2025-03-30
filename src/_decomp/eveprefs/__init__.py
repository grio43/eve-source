#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveprefs\__init__.py
import abc
import os
import types
import sys
DEFAULT_ENCODING = 'cp1252'
_unsupplied = object()

def get_filename(blue, shortname, ext, root = None):
    if root is None:
        root = blue.paths.ResolvePath(u'settings:/')
    if root[-1] not in ('\\', '/'):
        root += '\\'
    if shortname[-len(ext):] != ext:
        filename = root + shortname + ext
    else:
        filename = root + shortname
    return filename


def strip_spaces(d):
    result = {}
    for k, v in d.iteritems():
        realv = v
        if isinstance(v, types.StringTypes):
            realv = v.strip()
        result[k.strip()] = realv

    return result


class BaseIniFile(object):
    __metaclass__ = abc.ABCMeta

    def HasKey(self, key):
        return self.FixKey(key) in self._GetKeySet()

    @abc.abstractmethod
    def _GetKeySet(self):
        pass

    def GetKeys(self, beginWith = None):
        if beginWith is None:
            keys = list(self._GetKeySet())
        else:
            beginWith = self.FixKey(beginWith)
            keys = [ key for key in self._GetKeySet() if key[:len(beginWith)] == beginWith ]
        return keys

    @abc.abstractmethod
    def _GetValue(self, key):
        pass

    def GetValue(self, key, default = _unsupplied, flushDef = False):
        key = self.FixKey(key)
        if key not in self._GetKeySet():
            if default is _unsupplied:
                raise KeyError(key)
            if flushDef:
                self.SetValue(key, default)
            return default
        return self._GetValue(key)

    @abc.abstractmethod
    def _SetValue(self, key, value, forcePickle):
        pass

    def SetValue(self, key, value, forcePickle = False):
        key = self.FixKey(key)
        self._SetValue(key, value, forcePickle)

    def _SpoofKey(self, key, value):
        raise NotImplementedError()

    def SpoofKey(self, key, value):
        key = self.FixKey(key)
        self._SpoofKey(key, value)

    def FixKey(self, key):
        try:
            key.decode('ascii')
        except UnicodeDecodeError:
            raise ValueError('key must be ascii')

        return str(key).strip()

    @abc.abstractmethod
    def _DeleteValue(self, key):
        pass

    def DeleteValue(self, key):
        key = self.FixKey(key)
        if key in self._GetKeySet():
            self._DeleteValue(key)


class Handler(object):

    def __init__(self, inifile):
        self.__dict__['ini'] = inifile

    def __getattr__(self, key):
        if hasattr(self.__dict__['ini'], key):
            return getattr(self.__dict__['ini'], key)
        try:
            return self.__dict__['ini'].GetValue(key)
        except KeyError:
            raise AttributeError, key

    def __setattr__(self, key, value):
        self.__dict__['ini'].SetValue(key, value)

    def __str__(self):
        ini = self.__dict__['ini']
        clsname = type(ini).__name__
        filename = ''
        if hasattr(ini, 'filename'):
            filename = ini.filename + ' '
        count = len(ini.GetKeys())
        return '%(clsname)s %(filename)swith %(count)s entries' % locals()

    def __eq__(self, _):
        return NotImplemented


def SetClusterPrefs(prefsinst):
    import blue
    if prefsinst.GetValue('clusterName', None) is None:
        prefsinst.clusterName = blue.pyos.GetEnv().get('COMPUTERNAME', 'LOCALHOST') + '@' + blue.pyos.GetEnv().get('USERDOMAIN', 'NODOMAIN')
    if prefsinst.GetValue('clusterMode', None) is None:
        prefsinst.clusterMode = 'LOCAL'
    prefsinst.clusterName = prefsinst.clusterName.upper()
    prefsinst.clusterMode = prefsinst.clusterMode.upper()


boot = None
prefs = None

def Init():
    global prefs
    global boot
    import blue
    from eveprefs.iniformat import IniIniFile
    if blue.pyos.packaged and 'client' in blue.paths.ResolvePath(u'app:/'):
        handler = Handler(IniIniFile('start', blue.paths.ResolvePath(u'root:/'), 1))
    else:
        handler = Handler(IniIniFile('start', blue.paths.ResolvePath(u'app:/'), 1))
    boot = handler
    packagedClient = blue.pyos.packaged and handler.role == 'client'
    commonPath = blue.paths.ResolvePath(u'root:/common/')
    if packagedClient:
        commonPath = blue.paths.ResolvePath(u'root:/')
    handler.keyval.update(IniIniFile('common', commonPath, 1).keyval)
    settingsProfile = blue.os.GetStartupArgValue('settingsprofile')
    if settingsProfile != '':
        settingsProfile = '_' + settingsProfile
    settingsProfile = settingsProfile.replace('\\', '_').replace('/', '_')
    if '/LUA:OFF' in blue.pyos.GetArg() or boot.GetValue('role', None) != 'client':
        if boot.GetValue('role', None) == 'client':
            blue.paths.SetSearchPath('cache', blue.paths.ResolvePathForWriting(u'root:/cache'))
            blue.paths.SetSearchPath('settings', blue.paths.ResolvePathForWriting(u'root:/settings%s' % settingsProfile))
        else:
            blue.paths.SetSearchPath('cache', blue.paths.ResolvePathForWriting(u'app:/cache'))
            blue.paths.SetSearchPath('settings', blue.paths.ResolvePathForWriting(u'app:/settings%s' % settingsProfile))
        cachepath = blue.paths.ResolvePathForWriting(u'cache:/')
        settingspath = blue.paths.ResolvePathForWriting(u'settings:/')
        prefsfilepath = cachepath
    else:
        import utillib as util
        cachedir = util.GetClientUniqueFolderName()
        root = blue.sysinfo.GetUserApplicationDataDirectory() + u'\\CCP\\EVE\\'
        root = root.replace('\\', '/')
        root = root + cachedir + u'/'
        settingspath = root + u'settings%s/' % settingsProfile
        cachepath = root + u'cache/'
        blue.paths.SetSearchPath('cache', cachepath)
        blue.paths.SetSearchPath('settings', settingspath)
        prefsfilepath = settingspath.replace('\\', '/')
    for path in (settingspath, cachepath):
        try:
            os.makedirs(path)
        except OSError:
            pass

    handler = Handler(IniIniFile('prefs', prefsfilepath))
    prefs = handler
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding(DEFAULT_ENCODING)
    if boot.GetValue('role', None) == 'server':
        if '/proxy' in blue.pyos.GetArg():
            boot.role = 'proxy'
    SetClusterPrefs(handler)
    if boot.GetValue('role', None) in ('proxy', 'server') and prefs.GetValue('mpi', False):
        import MPI
    return (boot, prefs)
