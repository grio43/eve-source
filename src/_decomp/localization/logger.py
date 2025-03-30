#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\logger.py
import logmodule
from stringutil import strx
LOG_TRACEBACKS = True
logChannel = logmodule.GetChannel('Localization')

def LogInfo(*args):
    logChannel.Log('Localization module: ' + ''.join(map(strx, args)), logChannel.flags['INFO'])


def LogWarn(*args):
    logChannel.Log('Localization module: ' + ''.join(map(strx, args)), logChannel.flags['WARN'])


def LogError(*args):
    logChannel.Log('Localization module: ' + ''.join(map(strx, args)), logChannel.flags['ERR'])


def LogTraceback(*args):
    logChannel.Log('Localization module: ' + ''.join(map(strx, args)), logChannel.flags['ERR'])
    if LOG_TRACEBACKS:
        logmodule.LogTraceback('Localization module: ' + ''.join(map(strx, args)), channel='Localization', toConsole=0, toAlertSvc=0, severity=1, show_locals=0)
