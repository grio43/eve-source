#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\lib\autoexec_evecore.py
from eveprefs import prefs, boot
__all__ = ['SetupEveSpecificLogging', 'SetupForChina']
import blue
import log
import eveLocalization

def SetupForChina(forceEnglishIfNotChina = False):
    if boot.region == 'optic':
        eveLocalization.SetTimeDelta(28800)
        prefs.languageID = 'ZH'
    elif forceEnglishIfNotChina:
        prefs.languageID = 'EN'
    blue.os.languageID = prefs.GetValue('languageID', 'EN')


globalChannelsList = ['Combat',
 'Environment',
 'Movement',
 'NPC',
 'Navigation',
 'UI',
 'Macho',
 'Update',
 'General',
 'MethodCalls',
 'Models',
 'Connection',
 'Turrets',
 'Fitting',
 'Unittest',
 'SP']

def evePostStacktraceCallback(out):
    try:
        import log
        from carbon.common.script.sys.serviceConst import ROLE_SERVICE
        from carbon.common.script.sys.sessions import GetSessions
        from carbon.common.script.util.format import FmtDate
        sessions = []
        for sess in GetSessions():
            if getattr(sess, 'userid') and not sess.role & ROLE_SERVICE:
                sessions.append(sess)

        if sessions:
            out.write('\nActive client sessions:\n\n')
            out.write('------------------------------------------------------------------------------------------------------\n')
            out.write('| userid |       role |     charid |     shipid | locationid | last remote call    | address         |\n')
            out.write('------------------------------------------------------------------------------------------------------\n')
            for sess in sessions:
                fmt = '| %6s | %10s | %10s | %10s | %10s | %19s | %15s |\n'
                try:
                    out.write(fmt % (sess.userid,
                     sess.role,
                     sess.charid,
                     sess.shipid,
                     sess.locationid,
                     FmtDate(sess.lastRemoteCall, 'll') if sess.lastRemoteCall is not None else 'No info on last call',
                     sess.address.split(':')[0] if sess.address is not None else 'No address'))
                except:
                    out.write('!error writing out session %s\n' % str(sess))
                    log.LogException()

            out.write('------------------------------------------------------------------------------------------------------\n')
            out.write('%s sessions total.\n' % len(sessions))
        else:
            out.write('There were no active client sessions.\n')
    except:
        log.LogException()


def EveUIMessage(*args):
    eve.Message(*args)


def SetupEveSpecificLogging():
    log.AddGlobalChannels(globalChannelsList)
    log.SetStackFileNameSubPaths(('/server/', '/client/', '/proxy/', '/common/'))
    log.RegisterPostStackTraceAll(evePostStacktraceCallback)
    log.SetUiMessageFunc(EveUIMessage)
