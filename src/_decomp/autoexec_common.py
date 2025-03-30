#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\autoexec_common.py
import datetime
import os
import sys
import blue
from carbon.common.script.sys.buildversion import GetBuildVersionAsInt
import logmodule
import sysinfo
from eveprefs import prefs, boot
try:
    import marshalstrings
except ImportError:
    pass

DATETIME_FORMAT_STR = '%m/%d/%Y %H:%M:%S'

def LogStarting(mode):
    startedat = '%s %s version %s build %s starting %s' % (boot.appname,
     mode,
     boot.version,
     boot.build,
     datetime.datetime.utcnow().strftime(DATETIME_FORMAT_STR))
    print startedat
    logmodule.general.Log(startedat, logmodule.LGNOTICE)
    logmodule.general.Log('Python version: ' + sys.version, logmodule.LGNOTICE)
    if blue.sysinfo.isWine:
        logmodule.general.Log('Running on Wine', logmodule.LGNOTICE)
        logmodule.general.Log('Wine host OS: %s' % blue.sysinfo.wineHostOs, logmodule.LGNOTICE)
        logmodule.general.Log('Wine version: %s' % blue.sysinfo.wineVersion, logmodule.LGNOTICE)
    if blue.sysinfo.isRosetta:
        logmodule.general.Log('Running through Rosetta', logmodule.LGNOTICE)
    logmodule.general.Log('Process bits: ' + repr(blue.sysinfo.processBitCount), logmodule.LGNOTICE)
    logmodule.general.Log('Wow64 process? ' + ('yes' if blue.sysinfo.processBitCount != blue.sysinfo.systemBitCount else 'no'), logmodule.LGNOTICE)
    if blue.sysinfo.os.platform == blue.OsPlatform.WINDOWS:
        logmodule.general.Log('System info: ' + repr(blue.win32.GetSystemInfo()), logmodule.LGNOTICE)
        if blue.sysinfo.processBitCount != blue.sysinfo.systemBitCount:
            logmodule.general.Log('Native system info: ' + repr(blue.win32.GetNativeSystemInfo()), logmodule.LGNOTICE)
    logmodule.general.Log(repr(sysinfo.get_os_platform_information()))


def LogStarted(mode):
    startedat = '%s %s version %s build %s started %s' % (boot.appname,
     mode,
     boot.version,
     boot.build,
     datetime.datetime.utcnow().strftime(DATETIME_FORMAT_STR))
    print strx(startedat)
    logmodule.general.Log(startedat, logmodule.LGINFO)
    logmodule.general.Log(startedat, logmodule.LGNOTICE)
    logmodule.general.Log(startedat, logmodule.LGWARN)
    logmodule.general.Log(startedat, logmodule.LGERR)


try:
    osName = 'Unknown'
    if blue.sysinfo.isWine:
        host = blue.sysinfo.wineHostOs
        if host.startswith('Darwin'):
            osName = 'MacWine'
        else:
            osName = 'Linux'
    elif sys.platform.startswith('darwin'):
        osName = 'macOS'
    else:
        osName = 'Windows'
    blue.SetCrashKeyValues('OS', osName)
    blue.SetCrashKeyValues('rosetta', 'yes' if blue.sysinfo.isRosetta else 'no')
except RuntimeError:
    pass

logdestination = prefs.ini.GetValue('networkLogging', '')
if logdestination:
    networklogport = prefs.ini.GetValue('networkLoggingPort', 12201)
    networklogThreshold = prefs.ini.GetValue('networkLoggingThreshold', 1)
    blue.EnableNetworkLogging(logdestination, networklogport, boot.role, networklogThreshold)
fileLoggingDirectory = None
fileLoggingThreshold = 0
args = blue.pyos.GetArg()
for arg in args:
    if arg.startswith('/fileLogDirectory'):
        try:
            fileLoggingDirectory = arg.split('=')[1]
        except IndexError:
            fileLoggingDirectory = None

if not fileLoggingDirectory:
    fileLoggingDirectory = prefs.ini.GetValue('fileLogDirectory', None)
    fileLoggingThreshold = int(prefs.ini.GetValue('fileLoggingThreshold', 1))
if fileLoggingDirectory:
    if not hasattr(blue, 'EnableFileLogging'):
        print 'File Logging configured but not supported'
    else:
        fileLoggingDirectory = os.path.normpath(fileLoggingDirectory)
        blue.EnableFileLogging(fileLoggingDirectory, boot.role, fileLoggingThreshold)
