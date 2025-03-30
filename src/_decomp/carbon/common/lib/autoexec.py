#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\autoexec.py
import eveprefs
boot, prefs = eveprefs.Init()
import sys
import warnings

class InstallWarningHandler(object):

    def __init__(self):
        self.oldhandler = warnings.showwarning
        warnings.showwarning = self.ShowWarning

    def __del__(self):
        if warnings:
            warnings.showwarning = self.oldhandler

    def ShowWarning(self, message, category, filename, lineno, file = None):
        import logmodule
        string = warnings.formatwarning(message, category, filename, lineno)
        logmodule.LogTraceback(extraText=string, severity=logmodule.LGWARN, nthParent=3)
        if not file:
            file = sys.stderr
        print >> file, string


warningHandler = InstallWarningHandler()
import blue
import iocp
import _slsocket as _socket
if iocp.UsingIOCP():
    import carbonio
    select = None
    _socket.use_carbonio(True)
    carbonio._socket = _socket
    print 'Network layer using: CarbonIO'
    if iocp.LoggingCarbonIO():
        print 'installing CarbonIO logging callbacks'
        blue.net.InstallLoggingCallbacks()
else:
    import stacklessio
    import slselect as select
    if hasattr(_socket, 'use_carbonio'):
        _socket.use_carbonio(False)
    stacklessio._socket = _socket
    print 'Network layer using: StacklessIO'
sys.modules['_socket'] = _socket
sys.modules['select'] = select
import logmodule
logmodule.init(boot.role, prefs)
import stdlogutils.logserver as stdlogserver
stdlogserver.InitLoggingToLogserver(stdlogserver.GetLoggingLevelFromPrefs())
from stacklesslib import monkeypatch
monkeypatch.patch_ssl()
import builtinmangler
builtinmangler.MangleBuiltins()
import os
os.stat_float_times(False)
import exceptions
if not hasattr(exceptions, 'WindowsError'):
    exceptions.WindowsError = OSError
    import __builtin__
    __builtin__.WindowsError = OSError
import whitelistpickle
whitelistpickle.patch_cPickle()
if blue.pyos.packaged:
    blue.paths.RegisterFileSystemBeforeLocal('Remote')
else:
    blue.paths.RegisterFileSystemAfterLocal('Remote')
if not blue.pyos.packaged:
    import __builtin__
    from platformtools.compatibility.exposure.debuggingutils import pydevdebugging
    __builtin__.GOPYCHARM = pydevdebugging.ConnectExeFileToDebugger3
    __builtin__.GOPYCHARM4 = pydevdebugging.ConnectExeFileToDebugger4
    __builtin__.GOPYCHARM5 = pydevdebugging.ConnectExeFileToDebugger5
    __builtin__.GOPYCHARM2017 = pydevdebugging.ConnectExeFileToDebugger2017
    __builtin__.GOPYCHARM2019 = pydevdebugging.ConnectExeFileToDebugger2019
    __builtin__.NOPYCHARM = pydevdebugging.StopPycharm
    allArgs = blue.pyos.GetArg()
    containsToolParam = False
    for arg in allArgs:
        if arg.startswith('/tools='):
            containsToolParam = True
            break

    if '/jessica' not in allArgs and not containsToolParam:
        import devenv
        sys.path.append(os.path.join(devenv.SHARED_TOOLS_PYTHONDIR, 'lib27xccp'))
        import packageaddwatcher
        packageaddwatcher.guard_metapath(boot.role)
if prefs.ini.GetValue('GOPYCHARM', False):
    GOPYCHARM()
try:
    blue.SetCrashKeyValues('role', boot.role)
    blue.SetCrashKeyValues('build', str(boot.build))
    args = blue.pyos.GetArg()
    if '/thinclient' not in args:
        import monolithsentry
        monolithsentry.set_sentry_crash_key()
    orgArgs = blue.pyos.GetArg()
    args = ''
    for each in orgArgs:
        if not each.startswith('/path') and not each.startswith('/ssoToken') and not each.startswith('/refreshToken'):
            args += each
            args += ' '

    blue.SetCrashKeyValues('startupArgs', args)
    bitCount = blue.sysinfo.cpu.bitCount
    computerInfo = {'memoryPhysical': blue.sysinfo.GetMemory().totalPhysical / 1024,
     'cpuArchitecture': blue.sysinfo.cpu.architecture,
     'cpuIdentifier': blue.sysinfo.cpu.identifier,
     'cpuLevel': blue.sysinfo.cpu.family,
     'cpuRevision': blue.sysinfo.cpu.revision,
     'cpuCount': blue.sysinfo.cpu.logicalCpuCount,
     'cpuMHz': blue.sysinfo.cpu.frequency,
     'cpuBitCount': bitCount,
     'osMajorVersion': blue.sysinfo.os.majorVersion,
     'osMinorVersion': blue.sysinfo.os.minorVersion,
     'osBuild': blue.sysinfo.os.buildNumber,
     'osPatch': blue.sysinfo.os.patch,
     'osPlatform': 2}
    for key, val in computerInfo.iteritems():
        blue.SetCrashKeyValues(key, str(val))

    blue.SetCrashKeyValues('PDMData', blue.sysinfo.GetPDMData().encode('utf-8'))
except RuntimeError:
    pass

if not blue.pyos.packaged and '/disableSake' not in blue.pyos.GetArg():
    if sys.platform == 'win32':
        import watchdog.observers.winapi
        watchdog.observers.winapi.WATCHDOG_FILE_NOTIFY_FLAGS = watchdog.observers.winapi.FILE_NOTIFY_CHANGE_LAST_WRITE | watchdog.observers.winapi.FILE_NOTIFY_CHANGE_FILE_NAME
    import codereloading
    codereloading.InstallSakeAutocompiler()
if blue.pyos.packaged:
    tool = None
else:
    import inittools
    tool = inittools.gettool()
if tool is None:
    __import__('autoexec_%s' % boot.role)
elif tool == 'zmqserver':
    platformToolsLib = blue.paths.ResolvePath(u'root:/../platformtools/external')
    if sys.platform == 'darwin':
        sys.path.append(os.path.join(platformToolsLib, 'macOS', 'x64', 'AppleClang'))
    elif sys.platform == 'win32':
        sys.path.append(os.path.join(platformToolsLib, 'x64'))
    else:
        raise RuntimeError('Unsupported platform for behaviour tests')
    import exefileterminal._serverstartup
    exefileterminal._serverstartup.Run()
else:

    def run():
        inittools.run_(tool)
