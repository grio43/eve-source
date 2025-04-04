#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\logmodule\__init__.py
import sys
import datetime
import traceback2
import __builtin__
from cStringIO import StringIO
import os
import blue
import localstorage
from stdlogutils import GetStack, NextTraceID
from stdlogutils.logserver import LGINFO, LGNOTICE, LGWARN, LGERR
from stdlogutils.logserver import ChannelWrapper, LogChannelStream
from eveexceptions import UserError
DATETIME_FORMAT_STR = '%m/%d/%Y %H:%M:%S'
Suppress = ChannelWrapper.Suppress
Unsuppress = ChannelWrapper.Unsuppress
SuppressAllChannels = ChannelWrapper.SuppressAllChannels
UnsuppressAllChannels = ChannelWrapper.UnsuppressAllChannels
channelDict = ChannelWrapper.channelDict
uiMessageFunc = None
sentry_client = None
_WIN_EBADF = 9
Channel = ChannelWrapper
for f in Channel.flags:
    globals()[f] = Channel.flags[f]
    globals()[f.lower()] = Channel.flags[f]

baseName = ''
channels = {}
logExceptionLevel = 0
postStackTraceAll = None

def MsgWindowStreamToMsgWindow():
    from eveprefs import prefs
    if hasattr(session, 'userid') and session.userid and settings.generic:
        return settings.generic.Get('exceptionPopups', 0)
    if prefs:
        return prefs.GetValue('exceptionPopups', 0)
    return 0


def SetUiMessageFunc(func):
    global uiMessageFunc
    uiMessageFunc = func


def SetStackFileNameSubPaths(filePaths):
    pass


def DefaultUIMessage(*args):
    print args


def init(base_name = '', prefs = None):
    global baseName
    baseName = base_name
    if prefs is not None:
        ChannelWrapper.Initialize(prefs)
    SetUiMessageFunc(DefaultUIMessage)


def AddGlobalChannels(channels):
    g = globals()
    for channel in channels:
        if channel.lower() not in g:
            g[channel.lower()] = GetChannel(channel)


def GetChannel(name):
    if '.' not in name:
        name = baseName + '.' + name
    if name not in channels:
        s = name.split('.')
        facility = '.'.join(s[:-1])
        obj = s[-1]
        channels[name] = Channel(facility.encode('utf-8'), obj.encode('utf-8'))
    return channels[name]


ui = GetChannel('UI')
general = GetChannel('General')
methodcalls = GetChannel('MethodCalls')
unittest = GetChannel('Unittest')

def LogException(extraText = '', channel = 'general', toConsole = 1, toLogServer = 1, toAlertSvc = None, toMsgWindow = 1, exctype = None, exc = None, tb = None, severity = None, show_locals = 1):
    global logExceptionLevel
    if logExceptionLevel > 0:
        return
    _tmpctx = blue.pyos.taskletTimer.EnterTasklet('logmodule::LogException')
    logExceptionLevel += 1
    if not exctype:
        exctype, exc, tb = sys.exc_info()
    try:
        try:
            _LogException((exctype, exc, tb), extraText, channel, toConsole, toLogServer, toAlertSvc, toMsgWindow, severity, show_locals)
            return
        except Exception:
            try:
                traceback2.print_exc(show_locals=3)
                stream = LogChannelStream(GetChannel('general'), ERR)
                traceback2.print_exc(show_locals=3, file=stream)
                stream.close()
            except Exception:
                pass

        try:
            traceback2.print_exception(exctype, exc, tb, file=sys.stdout, show_locals=show_locals)
            stream = LogChannelStream(GetChannel(channel), ERR)
            print >> stream, 'retrying traceback log, got an error in _LogException'
            traceback2.print_exception(exctype, exc, tb, file=stream, show_locals=show_locals)
            stream.close()
        except Exception:
            try:
                traceback2.print_exc(show_locals=3)
            except:
                pass

    finally:
        del tb
        logExceptionLevel -= 1
        blue.pyos.taskletTimer.ReturnFromTasklet(_tmpctx)


def _LogException(exc_info, extraText, channel, toConsole, toLogServer, toAlertSvc, toMsgWindow, severity, show_locals):
    from eveprefs import boot
    if sentry_client:
        sentry_client(message=extraText, exc_info=exc_info)
    exctype, exc, tb = exc_info
    exception_list = traceback2.extract_tb(tb, extract_locals=show_locals)
    if tb:
        caught_list = traceback2.extract_stack(tb.tb_frame)
    else:
        caught_list = traceback2.extract_stack(up=2)
    stack, stackID = GetStack(exception_list, caught_list, show_locals=show_locals)
    if severity is None:
        severity = (ERR, WARN)[isinstance(exc, UserError)]
    if toAlertSvc is None:
        toAlertSvc = severity in (ERR,)
    if toMsgWindow and isinstance(exc, UserError) and boot.role == 'client':
        toMsgWindow = 0
        uiMessageFunc(*exc.args)
    out = GetMultiplex(channel, severity, toConsole, toLogServer, toMsgWindow, toAlertSvc, stackID)
    formatted_exception = traceback2.format_exception_only(exctype, exc)
    if not extraText:
        try:
            extraText = 'Info: %s' % formatted_exception[-1].strip()
        except:
            extraText = 'Info: <none>'

    prefix = 'REMOTE ' if channel == 'remote.exc' else ''
    traceID = NextTraceID()
    print >> out, '%sEXCEPTION #%d logged at %s : %s ' % (prefix,
     traceID,
     datetime.datetime.utcnow().strftime(DATETIME_FORMAT_STR),
     extraText)
    print >> out, ' '
    print >> out, 'Formatted exception info:',
    for line in formatted_exception:
        print >> out, line,

    print >> out, ' '
    for line in stack:
        print >> out, line,

    print >> out, ' '
    if exctype is MemoryError:
        try:
            DumpMemoryStatus(out)
            DumpMemHistory(out)
        except:
            pass

    try:
        _LogThreadLocals(out)
    except MemoryError:
        pass

    if boot.role != 'client':
        try:
            ram = blue.sysinfo.GetMemory().pageFile / 1024 / 1024
            cpuLoad = sm.GetService('machoNet').GetCPULoad()
            memLeft = blue.sysinfo.GetMemory().availablePhysical / 1024 / 1024
            txt = 'System Information: '
            txt += ' Node ID: %s' % sm.GetService('machoNet').GetNodeID()
            if boot.role == 'server':
                txt += ' | Node Name: %s' % sm.GetService('machoNet').GetLocalHostName()
            txt += ' | Total CPU load: %s%%' % int(cpuLoad)
            txt += ' | Process memory in use: %s MB' % ram
            txt += ' | Physical memory left: %s MB' % memLeft
            print >> out, txt
        except Exception as e:
            sys.exc_clear()

    try:
        print >> out, 'Stackhash: %s' % stackID[0]
    except Exception:
        pass

    print >> out, 'Reported from: ', __name__
    print >> out, '%sEXCEPTION END' % (prefix,)
    out.flush()
    if toConsole:
        if toLogServer:
            print >> sys.stderr, '#nolog: An exception has occurred. It has been logged in the log server as exception #%d' % traceID
        else:
            print >> sys.stderr, 'There is no useful information accompanying this exception in the log server'


def DumpMemHistory(out):
    from eveprefs import boot
    try:
        if boot.role != 'client':
            import blue, cPickle
            fname = blue.paths.ResolvePath(u'root:/') + 'logs/memhist.b%d.%s.pikl' % (boot.build, blue.os.pid)
            print >> out, 'dumping cpu and memory history in ' + fname
            f = file(fname, 'w')
            cPickle.dump(blue.pyos.cpuUsage, f)
            f.close()
            print >> out, 'dump done.'
    except StandardError:
        pass


def LogTraceback(extraText = '', channel = 'general', toConsole = 1, toAlertSvc = None, toLogServer = 1, nthParent = 0, daStack = None, severity = LGERR, show_locals = 1, limit = None):
    if logExceptionLevel > 0:
        return
    _tmpctx = blue.pyos.taskletTimer.EnterTasklet('logmodule::LogTraceback')
    try:
        if daStack is None:
            daStack = traceback2.extract_stack(limit=limit, up=nthParent + 1, extract_locals=show_locals)
        stack, stackID = GetStack(daStack, None, show_locals, True)
        if toAlertSvc is None:
            toAlertSvc = severity in (ERR,)
        toMsgWindow = False
        multiplexToConsole = False if toLogServer else toConsole
        out = GetMultiplex(channel, severity, multiplexToConsole, toLogServer, toMsgWindow, toAlertSvc, stackID)
        traceID = NextTraceID()
        logMessage = StringIO()
        logMessage.write('STACKTRACE #%d logged at %s : %s\n' % (traceID, datetime.datetime.utcnow().strftime(DATETIME_FORMAT_STR), extraText))
        logMessage.write(' \n')
        for line in stack:
            logMessage.write(line)

        logMessage.write(' \n')
        _LogThreadLocals(logMessage)
        logMessage.write('Stackhash: %s\n' % stackID[0])
        logMessage.write('Reported from: ' + __name__ + '\n')
        logMessage.write('STACKTRACE END')
        print >> out, logMessage.getvalue()
        out.flush()
        if toConsole:
            if toLogServer:
                if '/jessica' in blue.pyos.GetArg():
                    print >> sys.stderr, '#nolog: ' + logMessage.getvalue()
                else:
                    print >> sys.stderr, '#nolog: A traceback has been generated. It has been logged in the log server as stacktrace #%d' % traceID
            else:
                print >> sys.stderr, 'There is no useful information accompanying this traceback in the log server'
    finally:
        blue.pyos.taskletTimer.ReturnFromTasklet(_tmpctx)


def LogMemoryStatus(extraText = '', channel = 'general'):
    out = GetMultiplex(channel, WARN, 0, 1, 0, 0, 0)
    print >> out, 'Logging memory status : ', extraText
    DumpMemoryStatus(out)


def WhoCalledMe(up = 3):
    try:
        trc = traceback2.extract_stack(limit=1, up=up)[0]
        fileName = os.path.basename(trc[0])
        lineNum = trc[1]
        funcName = trc[2]
        ret = '%s(%s) in %s' % (fileName, lineNum, funcName)
    except:
        ret = 'unknown'

    return ret


def DumpMemoryStatus(out):
    if blue.sysinfo.os.platform == blue.OsPlatform.WINDOWS:
        m = blue.win32.GlobalMemoryStatus()
        print >> out, 'GlobalMemoryStatus:'
        for k, v in m.items():
            print >> out, '%s : %r' % (k, v)

        print >> out, 'ProcessMemoryInfo:'
        m = blue.win32.GetProcessMemoryInfo()
        for k, v in m.items():
            print >> out, '%s : %r' % (k, v)

    print >> out, 'Python memory usage: %r' % sys.getpymalloced()
    try:
        print >> out, 'blue WriteStreams: %s, mem use: %s' % (blue.marshal.GetNWriteStreams(), blue.marshal.GetWriteStreamMem())
    except:
        pass

    print >> out, 'end of memory status'
    out.flush()


def _LogThreadLocals(out):
    out.write('Thread Locals:')
    if hasattr(__builtin__, 'session'):
        out.write('  session was ')
        out.write(str(session))
    else:
        out.write('sorry, no session for ya.')
    try:
        ctk = localstorage.GetLocalStorage().get('calltimer.key', None)
    except NameError:
        return

    if ctk:
        out.write('  calltimer.key was ')
        out.write(ctk)
    currentcall = localstorage.GetLocalStorage().get('base.currentcall', None)
    if currentcall:
        try:
            currentcall = currentcall()
            out.write('  currentcall was: ')
            out.write(str(currentcall))
        except ReferenceError:
            pass

    out.write('\n')


def GetMultiplex(channel, mode, toConsole, toLogServer, toMsgWindow, toAlertSvc, stackID):
    to = []
    if toConsole:
        if mode == INFO:
            to.append(sys.__stdout__)
        else:
            to.append(sys.__stderr__)
    if toLogServer:
        to.append(LogChannelStream(GetChannel(channel), mode))
    if toMsgWindow and hasattr(__builtin__, 'session'):
        to.append(MsgWindowStream())
    if toAlertSvc and hasattr(__builtin__, 'sm') and 'machoNet' in sm.services:
        to.append(LogAlertServiceStream(GetChannel(channel), mode, stackID))
    return Multiplex(to)


class LogAlertServiceStream(object):

    def __init__(self, channel, mode, stackID):
        self.channel, self.mode, self.buff, self.stackID = (channel,
         mode,
         StringIO(),
         stackID)

    def write(self, what):
        self.buff.write(what.encode('utf-8'))

    def flush(self):
        if not self.buff.tell():
            return
        try:
            self.buff.seek(0)
            buff = self.buff.read()
            sm.GetService('alert').SendStackTraceAlert(self.stackID, buff, {ERR: 'Error',
             WARN: 'Warning',
             INFO: 'Info'}.get(self.mode, 'Unknown'))
        except:
            print 'Exception in LogAlertServiceStream'

        self.buff = StringIO()


class MsgWindowStream(object):
    __bad_to_good__ = [('<', '&lt;'),
     ('>', '&gt;'),
     ('\r', ''),
     ('\n', '<br>')]

    def __init__(self):
        self.buff = []

    def write(self, what):
        for bad, good in self.__bad_to_good__:
            what = what.replace(bad, good)

        self.buff.append(what)

    def flush(self):
        if not self.buff:
            return
        try:
            if not MsgWindowStreamToMsgWindow():
                return
            buff = ''.join(self.buff)
            if len(buff) > 10000:
                buff = buff[:10000] + '... [long traceback clipped; more info in the logger]'
            import uthread
            uthread.new(uiMessageFunc, 'ErrSystemError', {'text': buff})
        except:
            pass

        self.buff = []


class Multiplex(object):

    def __init__(self, streams):
        self.streams = streams

    def __del__(self):
        self.flush()

    def write(self, what):
        for each in self.streams:
            each.write(what)

    def flush(self):
        for each in self.streams:
            try:
                getattr(each, 'flush', lambda : None)()
            except IOError as ioe:
                if each in (sys.__stderr__, sys.__stdout__) and ioe[0] == _WIN_EBADF and blue.os.HasStartupArg('noconsole'):
                    pass
                else:
                    raise

    def close(self):
        for each in self.streams:
            getattr(each, 'close', lambda : None)()


def RegisterPostStackTraceAll(func):
    global postStackTraceAll
    postStackTraceAll = func


def StackTraceAll(reason = '(no reason stated)'):
    import stackless, traceback2, os, time
    from eveprefs import boot
    logsFolder = blue.paths.ResolvePath(u'root:') + 'logs'
    if not os.path.exists(logsFolder):
        os.mkdir(logsFolder)
    y, m, wd, d, h, m, s, ms = blue.os.GetTimeParts(blue.os.GetWallclockTime())
    args = (boot.build,
     y,
     m,
     d,
     h,
     m,
     s)
    filename = logsFolder + '/#stacktrace b%d %.4d.%.2d.%.2d %.2d.%.2d.%.2d.txt' % args
    GetChannel('General').Log('Writing out stacktrace at ' + filename, LGERR)
    out = open(filename, 'w')
    out.write('Stack trace of all tasklets as requested: %s\n' % reason)
    out.write('Node ID: %s\n' % getattr(sm.services['machoNet'], 'nodeID', 'unknown'))
    out.write(time.ctime() + '\n\n')
    t = stackless.getcurrent()
    first = t
    no = 1
    while t:
        out.write('Tasklet #%s -------------------------------------------------' % no + '\n')
        no += 1
        if str(t.frame).find('cframe') == -1:
            traceback2.print_stack(t.frame, file=out)
        else:
            out.write('%s\n' % t.frame)
        out.write('\n')
        t = t.next
        if t is None or t == first:
            break

    if postStackTraceAll:
        postStackTraceAll(out)


def Quit(reason = '(no reason stated)'):
    try:
        StackTraceAll(reason)
    except:
        try:
            LogTraceback('Exception in stack-trace-all, shutdown bombing')
        except:
            pass

    try:
        import bluepy
        bluepy.Terminate(1, reason)
    except ImportError:
        sys.exit(1)
