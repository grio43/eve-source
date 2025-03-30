#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\autoexec_client_core.py
from eveprefs import prefs, boot
import __builtin__
import os
import platform
import sys
from . import autoexec_common
import blue
import bluepy
from . import builtinmangler
import carbon.common.script.util.numerical as numerical
from . import whitelist
from journey.tracker import reset_journey_id
import logmodule
import trinity
import remotefilecache
import monolithconfig
import monolithhoneycomb
import monolithhoneycomb_events
import stackless_tracing
sentry_io_dsn = os.getenv('EVE_CLIENT_SENTRY_DSN', 'https://56cd429e46214b8988ddae6a88e50ae3@sentry.io/1436728')
INLINE_SERVICES = ('DB2', 'machoNet', 'config', 'objectCaching', 'dataconfig', 'dogmaIM', 'device')

def Startup(appCacheDirs, userCacheDirs, servicesToRun):
    blue.os.sleeptime = 0
    InitializeRemoteFileCacheIfNeeded()
    args = blue.pyos.GetArg()[1:]
    if '/thinclient' in args:
        import thinclients, thinclients.clientsetup
        if thinclients.HEADLESS in args:
            thinclients.clientsetup.patch_all()
        elif thinclients.HEADED in args:
            thinclients.clientsetup.enable_live_updates()
            thinclients.clientsetup.install_commands()
        else:
            raise RuntimeError('Bad params.')
    import monolithsentry
    monolithsentry.init(sentry_io_dsn)
    monolithsentry.set_geo_tags()
    autoexec_common.LogStarting('Client')
    builtinmangler.add_system_module_extras()
    whitelist.InitWhitelist()
    import localization
    localization.LoadLanguageData()
    errorMsg = {'resetsettings': [localization.GetByLabel('UI/ErrorDialog/CantClearSettings'), localization.GetByLabel('UI/ErrorDialog/CantClearSettingsHeader'), localization.GetByLabel('UI/ErrorDialog/CantClearSettings')],
     'clearcache': [localization.GetByLabel('UI/ErrorDialog/CantClearCache'), localization.GetByLabel('UI/ErrorDialog/CantClearCacheHeader'), localization.GetByLabel('UI/ErrorDialog/CantClearCache')]}
    if not getattr(prefs, 'disableLogInMemory', 0):
        blue.logInMemory.capacity = 4096
        blue.logInMemory.Start()
    for clearType, clearPath in [('resetsettings', blue.paths.ResolvePath(u'settings:/')), ('clearcache', blue.paths.ResolvePath(u'cache:/'))]:
        if getattr(prefs, clearType, 0):
            if clearType == 'resetsettings':
                prefs.DeleteValue(clearType)
            if os.path.exists(clearPath):
                i = 0
                while 1:
                    newDir = clearPath[:-1] + '_backup%s' % i
                    if not os.path.isdir(newDir):
                        try:
                            os.makedirs(newDir)
                        except:
                            blue.os.ShowErrorMessageBox(errorMsg[clearType][1], errorMsg[clearType][0])
                            bluepy.Terminate(1, errorMsg[clearType][2])
                            return False

                        break
                    i += 1

                for filename in os.listdir(clearPath):
                    if filename != 'Settings':
                        try:
                            os.rename(clearPath + filename, '%s_backup%s/%s' % (clearPath[:-1], i, filename))
                        except:
                            blue.os.ShowErrorMessageBox(errorMsg[clearType][1], errorMsg[clearType][0])
                            bluepy.Terminate(1, errorMsg[clearType][2])
                            return False

                prefs.DeleteValue(clearType)

    mydocs = blue.sysinfo.GetUserDocumentsDirectory()
    try:
        os.listdir(mydocs)
    except OSError as e:
        logmodule.general.Log('Access to {} was denied by the user, certain features may not work'.format(mydocs), logmodule.LGWARN)

    paths = [blue.paths.ResolvePath(u'cache:/')]
    for dir in appCacheDirs:
        paths.append(blue.paths.ResolvePath(u'cache:/') + dir)

    for dir in userCacheDirs:
        paths.append(mydocs + dir)

    for path in paths:
        try:
            os.makedirs(path)
        except OSError as e:
            sys.exc_clear()

    from carbon.common.script.sys import basesession
    from carbon.common.lib.session import SESSION_TYPE_GAME
    session = basesession.CreateSession(None, SESSION_TYPE_GAME)
    __builtin__.session = session
    __builtin__.charsession = session
    basesession.EnableCallTimers(2)
    _InitializeEveBuiltin()
    autoexec_common.LogStarted('Client')
    bluepy.frameClock = numerical.FrameClock()
    blue.os.frameClock = bluepy.frameClock
    reset_journey_id()
    from carbon.common.script.sys.serviceManager import ServiceManager
    srvMng = ServiceManager(startInline=INLINE_SERVICES)
    if hasattr(prefs, 'http') and prefs.http:
        logmodule.general.Log('Running http', logmodule.LGINFO)
        srvMng.Run(('http',))
    srvMng.Run(servicesToRun)
    monolithconfig.set_service_manager(srvMng)
    monolithhoneycomb.init(srvMng)
    monolithhoneycomb_events.init(srvMng)
    stackless_tracing.init()
    if boot.region == 'optic' and platform.system() == 'Windows':
        srvMng.StartService('eveGuardSvc')
    title = '[%s] %s %s %s.%s pid=%s' % (boot.region.upper(),
     boot.codename,
     boot.role,
     boot.version,
     boot.build,
     blue.os.pid)
    blue.os.SetAppTitle(title)
    try:
        blue.EnableCrashReporting(prefs.GetValue('breakpadUpload', 1) == 1)
    except RuntimeError:
        pass

    blue.os.frameTimeTimeout = prefs.GetValue('frameTimeTimeout', 30000)
    blue.os.sleeptime = 250
    if '/skiprun' not in args:
        srvMng.GetService('gameui').StartupUI(0)


def _SetupClientJWT():
    token = None
    for arg in blue.pyos.GetArg()[1:]:
        if arg.startswith('/ssoToken'):
            try:
                _, token = arg.split('=')
            finally:
                break


def _InitializeEveBuiltin():
    import eve.client.script.sys.eveinit as eveinit
    eve_inst = eveinit.Eve()
    eve_inst.session = session
    __builtin__.eve = eve_inst


def _GetResfileServerAndIndexFromArgs():
    if boot.region == 'optic':
        resfileServer = 'http://ma79.gdl.netease.com/eve/resources/'
    else:
        resfileServer = 'https://clientresources.eveonline.com/'
    resfileIndices = remotefilecache.get_default_resource_index_file_list()
    resfileIndices = [ 'app:/' + indexfile for indexfile in resfileIndices ]
    if blue.os.HasStartupArg('resfileserver'):
        argValue = blue.os.GetStartupArgValue('resfileserver')
        if argValue:
            params = argValue.split(',')
            resfileServer = params[0]
            if len(params) > 1:
                resfilepath = params[1]
                resfileIndices[0] = resfilepath
                split = resfilepath.split('.')
                suffix = remotefilecache.ccp_platform_id()
                platformRespath = split[0] + '_%s.txt' % suffix
                resfileIndices[1] = platformRespath
    if resfileServer:
        if not resfileServer.startswith('http'):
            resfileServer = str('http://%s' % resfileServer)
    return (resfileIndices, resfileServer)


def _GetSharedCacheFolderFromRegistry():
    try:
        return blue.win32.RegistryGetValue('HKEY_CURRENT_USER\\SOFTWARE\\CCP\\EVEONLINE', 'CACHEFOLDER', 1)
    except (OSError, AttributeError):
        return None


def _SetRemoteFileCacheFolderFromArgs():
    folder = blue.os.GetStartupArgValue('remotefilecachefolder')
    if not folder:
        shared_cache_folder = _GetSharedCacheFolderFromRegistry()
        if shared_cache_folder:
            folder = os.path.join(shared_cache_folder, 'ResFiles')
        else:
            folder = remotefilecache.get_default_cache_folder()
    remotefilecache.set_cache_folder(folder)


def _InitializeRemoteFileCache(resfileServer, resfileIndices):
    _SetRemoteFileCacheFolderFromArgs()
    remotefilecache.prepare(resfileIndices, resfileServer)


def InitializeRemoteFileCacheIfNeeded():
    resfileIndices, resfileServer = _GetResfileServerAndIndexFromArgs()
    if resfileServer and resfileIndices:
        _InitializeRemoteFileCache(resfileServer, resfileIndices)
        logmodule.general.Log('Remote file caching enabled', logmodule.LGINFO)


def StartClient(appCacheDirs, userCacheDirs, servicesToRun):
    t = blue.pyos.CreateTasklet(Startup, (appCacheDirs, userCacheDirs, servicesToRun), {})
    t.context = '^boot::autoexec_client'
