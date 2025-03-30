#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\ExceptionWrapperGPCS.py
import sys
import types
import zlib
import log
import traceback2
import blue
from carbon.common.lib import const
from carbon.common.script.net import machobase, machoNet, objectCaching
from carbon.common.script.net.machoNetExceptions import UnMachoDestination, MachoException, MachoWrappedException
from carbon.common.script.net.moniker import UpdateMoniker
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER, ROLE_QA
from cluster import MACHONETERR_WRAPPEDEXCEPTION
from eveexceptions import UserError
from inventorycommon import WrongInventoryLocation
from eveprefs import prefs
import monolithsentry
from stringutil import strx
from machonet_tracing import IngressTracer

class ExceptionWrapper:
    __guid__ = 'gpcs.ExceptionWrapper'

    def __init__(self):
        self.errornumber = 1L

    def GetErrorID(self):
        if machoNet.mode == 'client':
            theID = '{%s #%d}' % (machoNet.mode, self.errornumber)
        else:
            theID = '{%s-%s-%d #%d}' % (machoNet.mode,
             self.machoNet.GetLocalHostName(),
             self.machoNet.GetNodeID(),
             self.errornumber)
        self.errornumber += 1
        return theID

    def CallUp(self, packet):
        try:
            try:
                return self.ForwardCallUp(packet)
            except (UnMachoDestination,
             MachoException,
             objectCaching.CacheOK,
             UpdateMoniker,
             UserError) as e:
                if isinstance(e, objectCaching.CacheOK):
                    IngressTracer.set_object_cache_ok()
                if isinstance(e, UnMachoDestination) and getattr(packet.destination, 'nodeID', None):
                    if packet.destination.nodeID < const.maxNodeID and machoNet.mode == 'proxy':
                        self.machoNet.HandleUnMachoDestination(packet.destination.nodeID, packet)
                return packet.ErrorResponse(MACHONETERR_WRAPPEDEXCEPTION, (machobase.DumpsSanitized(e),))
            except Exception as e:
                exc_info = sys.exc_info()
                source = 'server' if hasattr(packet.source, 'nodeID') else 'client'
                monolithsentry.capture_exception('Failed to service remote call', exc_info, new_tags={'destination_service': packet.destination.service,
                 'macho_source': source,
                 'destination_method': packet.payload[1]})
                exctype, exc = exc_info[:2]
                stack, serverStackKey = log.GetStack(traceback2.extract_tb(sys.exc_info()[2], extract_locals=1), show_locals=1)
                dasID = self.GetErrorID()
                desc = ['%s caught an exception while handling a remote call.  The caller should send a traceback with ID %s, which hopefully arrive at the originating node.  Server info follows:' % (machoNet.mode, dasID)]
                desc += stack
                desc += traceback2.format_exception_only(exctype, exc)
                try:
                    memory = blue.sysinfo.GetMemory()
                    ram = memory.pageFile / 1024 / 1024
                    cpuLoad = self.machoNet.GetCPULoad()
                    memLeft = memory.availablePhysical / 1024 / 1024
                    txt = 'System Information: '
                    txt += 'Total CPU load: %s%%' % int(cpuLoad)
                    txt += ' | Process memory in use: %s MB' % ram
                    txt += ' | Physical memory left: %s MB\n' % memLeft
                    desc.append(txt)
                    sessionInfo = 'session was ' + str(session)
                    desc.append(sessionInfo)
                except Exception as e:
                    sys.exc_clear()

                self.machoNet.LogError('\n'.join(desc))
                session.LogSessionHistory('An exception occurred while handling a remote call.  Traceback ID=%s' % dasID)
                session.hasproblems = 1
                sm.GetService('alert').SendStackTraceAlert(serverStackKey, ''.join(desc), 'Delivering Error To Remote Host')
                variables = []
                if machoNet.mode == 'client':
                    variables += ['Context info logged on the client, session=%s\n' % (strx(session),)]
                elif prefs.clusterMode in ('LOCAL', 'MASTER', 'TRANSLATION') or session and 0 != session.role & (ROLE_QA | ROLE_PROGRAMMER):
                    variables += ['Context info logged on %s node %d, host=%s\n' % (machoNet.mode, self.machoNet.GetNodeID(), self.machoNet.GetLocalHostName())]
                    if isinstance(e, WrongInventoryLocation):
                        e = RuntimeError(e.args)
                else:
                    variables = []
                    if isinstance(e, WrongInventoryLocation):
                        item = e.args[-1]
                        itemInfo = item[:2] + ['owner redacted', 'location redacted'] + item[-7:]
                        exceptionInfo = e.args[:-1] + tuple(itemInfo)
                        e = RuntimeError(*exceptionInfo)
                    stack = ['//%s/host=%s/nodeID=%d/errorHashKey=%d\n' % (machoNet.mode,
                      self.machoNet.GetLocalHostName(),
                      self.machoNet.GetNodeID(),
                      serverStackKey[0])]
                return packet.ErrorResponse(MACHONETERR_WRAPPEDEXCEPTION, (machobase.DumpsSanitized(e), (1,
                  stack,
                  variables,
                  dasID,
                  serverStackKey,
                  self.machoNet.GetNodeID(),
                  machoNet.mode)))

        except:
            log.LogException('Could not create ErrorResponse, sending an empty one')
            return packet.ErrorResponse(MACHONETERR_WRAPPEDEXCEPTION, None)

    def CallDown(self, packet):
        try:
            return self.ForwardCallDown(packet)
        except UnMachoDestination as e:
            if getattr(packet.destination, 'nodeID', None):
                if packet.destination.nodeID < const.maxNodeID and machoNet.mode == 'server':
                    self.machoNet.HandleUnMachoDestination(packet.destination.nodeID, packet)
            raise
        except MachoWrappedException as e:
            serverStack = None
            if e.payload and len(e.payload) > 1:
                clientStack, clientStackKey = log.GetStack(traceback2.extract_stack())
                serverStack = e.payload[1][1]
                serverStackVariables = e.payload[1][2]
                fullReport = ['<-- top of local (%s) info -->\n' % machoNet.mode]
                fullReport += clientStack
                fullReport.append('<-- here we crossed the wire -->\n')
                fullReport += serverStack
                fullReport += serverStackVariables
                fullReport.append('<-- bottom of remote (%s) info -->\n' % e.payload[1][6])
                if e.payload[1][0]:
                    logfunc = self.machoNet.LogError
                    m = 'Error'
                else:
                    logfunc = self.machoNet.LogWarn
                    m = 'Warning'
                fullReport = ''.join(fullReport)
                logfunc('Exception traceback, origin %s:\n%s' % (e.payload[1][3], fullReport))
                serverStackKey = e.payload[1][4]
                combinedStack = clientStackKey[1] + serverStackKey[1]
                combinedStackKey = [zlib.adler32(combinedStack), combinedStack]
                sm.GetService('alert').SendStackTraceAlert(combinedStackKey, fullReport, m, nextErrorKeyHash=serverStackKey[0], nodeID=e.payload[1][5])
                if machoNet.mode == 'client':
                    windowStream = log.MsgWindowStream()
                    if windowStream:
                        print >> windowStream, 'Exception Traceback-'
                        print >> windowStream, fullReport,
                        windowStream.flush()
            newException = machobase.LoadsSanitized(e.payload[0])
            if prefs.clusterMode in ('LOCAL', 'TEST', 'MASTER'):
                if 'proxy' == machoNet.mode:
                    newException.serverStack = serverStack
            raise newException

    def NotifyUp(self, packet):
        try:
            self.ForwardNotifyUp(packet)
        except Exception:
            log.LogException('Exception during remote notification')

    def FormatException(self, etype, value):
        ret = []
        if type(etype) == types.ClassType:
            stype = etype.__name__
        else:
            stype = etype
        ret.append('Exception:')
        if value is None:
            ret.append(strx(stype))
        else:
            if etype is SyntaxError:
                try:
                    msg, (filename, lineno, offset, line) = value
                except StandardError:
                    sys.exc_clear()

                if line is None:
                    line = '<unknown>'
                else:
                    line = line.strip()
                item = '%s(%d) syntax error at position %s, of code:\t%s' % (filename,
                 lineno,
                 offset,
                 line)
                ret.append(item)
                pos = item.find(':')
                item = ' ' * pos + ' ' + ' ' * offset + '^'
            s = self._some_str(value)
            if s:
                ret.append('%s: %s' % (strx(stype), s))
            else:
                ret.append(strx(stype))
        return ret

    def _some_str(self, value):
        try:
            return strx(value)
        except StandardError:
            return '<unprintable %s object>' % type(value).__name__
