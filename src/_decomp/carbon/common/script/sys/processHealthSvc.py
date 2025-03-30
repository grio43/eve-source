#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\sys\processHealthSvc.py
import _socket
import copy
import os
import subprocess
import sys
import blue
import bluepy
import uthread
import log
import monolithmetrics
import utillib
from carbon.common.script.net.ServiceCallGPCS import CoreServiceCall
from carbon.common.script.sys import sessions
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING
from carbon.common.script.sys.sessions import GetNumberOfCharacterSessions
from carbon.common.script.util.format import FmtDateEng
from eve.common.lib import appConst as const
from eveprefs import prefs, boot
METRIC_PROCESS_HEALTH = 'process_health'

class ProcessHealthSvc(Service):
    __guid__ = 'svc.processHealth'
    __servicename__ = 'processHealth'
    __displayname__ = 'Process Health Service'
    __startupdependencies__ = ['machoNet']
    __notifyevents__ = ['ProcessShutdown']

    def ProcessShutdown(self):
        self.WriteLog(20, True, useLogNotice=True)

    def __init__(self, *args):
        Service.__init__(self, *args)
        self.logLines = []
        self._SetStartTime()
        self.cache = utillib.KeyVal()
        self.cache.cacheTime = 0
        self.cache.minutes = 0
        self.cache.cache = []
        self.lastLoggedLine = 0
        self.lastStartPos = 0
        self.columnNames = ('dateTime', 'pyDateTime', 'procCpu', 'threadCpu', 'pyMem', 'virtualMem', 'taskletsProcessed', 'taskletsQueued', 'watchdog time', 'spf', 'serviceCalls', 'callsFromClient')

    def _SetStartTime(self):
        self.startDateTime = FmtDateEng(blue.os.GetWallclockTime(), 'ss')

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        self.nodeID = self.machoNet.GetNodeID()
        if self.nodeID is None:
            self.nodeID = 0
        self.nodeIndex = sm.GetService('machoNet').nodeIndex
        self.computerName = blue.pyos.GetEnv().get('COMPUTERNAME', 'unknown')
        if boot.role == 'server':
            machoNet = sm.GetService('machoNet')
            self._pid = os.getpid()
            self._nodeID = machoNet.GetNodeID()
            self._serviceMask = machoNet.serviceMask
            self._clusterGroup = machoNet.clusterGroup
        uthread.new(self.RunWorkerProcesses).context = 'svc.processHealth'

    def GetSeriesNames(self):
        names = []
        if len(self.logLines) > 0:
            names = self.logLines[0].keys()
            if names.count('dateTime') > 0:
                names.remove('dateTime')
        names.extend(['procCpu',
         'threadCpu',
         'pyMem',
         'virtualMem',
         'taskletsProcessed',
         'taskletsQueued',
         'watchdog time',
         'spf'])
        return names

    def GetSessionCount(self):
        allsc = sessions.GetSessions()
        sc = len(filter(lambda x: x.userid is not None and hasattr(x, 'clientID'), allsc))
        return sc

    def FindClosestPythonLine(self, blueLine, startPos = 0):
        logLinesCopy = copy.copy(self.logLines[startPos:])
        if len(logLinesCopy) == 0:
            return (None, 0)
        if blueLine['dateTime'] <= logLinesCopy[0]['pyDateTime']:
            return (logLinesCopy[0], 0)
        if blueLine['dateTime'] >= logLinesCopy[-1]['pyDateTime']:
            return (logLinesCopy[-1], len(logLinesCopy) + startPos)
        for line in xrange(0, len(logLinesCopy) - 1):
            blue.pyos.BeNice()
            t1 = logLinesCopy[line]['pyDateTime']
            t2 = logLinesCopy[line + 1]['pyDateTime']
            if t1 <= blueLine['dateTime'] < t2:
                return (logLinesCopy[line], line + startPos)

        return (None, 0, 0)

    def GetBlueDataAsDictList(self, minutes = 0):
        data = bluepy.GetBlueInfo(minutes, isYield=False)
        ret = []
        for i in xrange(0, len(data.timeData)):
            fps, taskletsProcessed, nrYielders, nrSleepWallclockers, watchDogTime, taskletsQueued = data.schedData[i]
            spf = 1.0 / fps if fps > 0.1 else 0
            ret.append({'dateTime': data.timeData[i],
             'procCpu': data.procCpuData[i],
             'threadCpu': data.threadCpuData[i],
             'pyMem': data.pymemData[i],
             'virtualMem': data.memData[i],
             'taskletsProcessed': taskletsProcessed,
             'taskletsQueued': taskletsQueued,
             'watchdog time': watchDogTime,
             'spf': spf})

        return ret

    def GetAllLogs(self, logAll = True):
        logs = self.GetProcessInfo()
        return self.FormatLog(logs, logAll)

    def GetProcessInfo(self, minutes = 0, useIncrementalStartPos = False):
        uthread.Lock(self)
        try:
            if blue.os.GetWallclockTime() - self.cache.cacheTime < 25 * const.SEC and self.cache.minutes == minutes:
                return self.cache.cache
            startTime = blue.os.GetWallclockTime()
            blueLines = self.GetBlueDataAsDictList(minutes)
            lastLine = {}
            if useIncrementalStartPos:
                startPos = self.lastStartPos
            else:
                startPos = 0
            for blueLine in blueLines:
                pyLine, startPos = self.FindClosestPythonLine(blueLine, startPos)
                if pyLine:
                    lastLine = pyLine
                    blueLine.update(pyLine)
                else:
                    blueLine.update(lastLine)

            self.lastStartPos = startPos
            self.cache.minutes = minutes
            self.cache.cacheTime = blue.os.GetWallclockTime()
            self.cache.cache = blueLines
            return blueLines
        finally:
            uthread.UnLock(self)

    def RunWorkerProcesses(self):
        seconds = 0
        while self.state == SERVICE_RUNNING:
            if prefs.GetValue('disableProcessHealthService', 0):
                self.LogWarn('Process Health Service is disabled in prefs. Disabling loop.')
                return
            blue.pyos.synchro.SleepWallclock(10000)
            try:
                seconds += 10
                self.DoOnceEvery10Secs()
                if seconds % 600 == 0:
                    self.DoOnceEvery10Minutes()
            except:
                log.LogException()
                sys.exc_clear()

    def send_to_monolithmetrics(self, net_bytes_rx, net_bytes_tx, net_packets_rx, net_packets_tx, service_calls, calls_from_client):
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.net.bytes_rx', value=net_bytes_rx)
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.net.bytes_tx', value=net_bytes_tx)
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.net.packets_rx', value=net_packets_rx)
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.net.packets_tx', value=net_packets_tx)
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.macho.service_calls', value=service_calls)
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.client.calls', value=calls_from_client)
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.tidi', value=blue.os.simDilation)
        blue_data = bluepy.get_blue_info_last_tick()
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.mem.virtual', value=blue_data['virtualmemory'])
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.mem.python', value=blue_data['pymemory'])
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.mem.working_set', value=blue_data['workingset'])
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.mem.pagefaults', value=blue_data['pagefaults'])
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.cpu.user.thread_time', value=blue_data['user_thread_time_micro'])
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.cpu.user.process_time', value=blue_data['user_process_time_micro'])
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.cpu.kernel.thread_time', value=blue_data['kernel_thread_time_micro'])
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.cpu.kernel.process_time', value=blue_data['kernel_process_time_micro'])
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.tasklets.processed', value=blue_data['tasklets_processed'])
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.tasklets.queued', value=blue_data['tasklets_queued'])
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.tasklets.scheduler.ticks', value=blue_data['tasklet_scheduler_duration'])
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.tasklets.sleeping', value=blue_data['tasklets_sleeping'])
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.tasklets.yielding', value=blue_data['tasklets_yielding'])
        monolithmetrics.gauge(metric=METRIC_PROCESS_HEALTH + '.spf', value=blue_data['spf'])

    def LogCpuMemNet(self):
        stats = _socket.getstats()
        netBytesRead = stats['BytesReceived']
        netBytesWritten = stats['BytesSent']
        netReadCalls = stats['PacketsReceived']
        netWriteCalls = stats['PacketsSent']
        sessionCount = self.GetSessionCount()
        serviceCalls = sum(CoreServiceCall.__recvServiceCallCount__.itervalues())
        callCounter = sm.GetService('machoNet').callCounter
        callsFromClient = 0
        for k in callCounter.iterkeys():
            if k[0] == const.ADDRESS_TYPE_CLIENT:
                callsFromClient = callCounter[k]
                break

        self.send_to_monolithmetrics(netBytesRead, netBytesWritten, netReadCalls, netWriteCalls, serviceCalls, callsFromClient)
        logline = {'pyDateTime': blue.os.GetWallclockTime(),
         'bytesReceived': netBytesRead,
         'bytesSent': netBytesWritten,
         'packetsReceived': netReadCalls,
         'packetsSent': netWriteCalls,
         'sessionCount': sessionCount,
         'tidiFactor': blue.os.simDilation,
         'serviceCalls': serviceCalls,
         'callsFromClient': callsFromClient}
        self.logLines.append(logline)

    def DoOnceEvery10Secs(self):
        self.LogCpuMemNet()

    def DoOnceEvery10Minutes(self):
        self.WriteLog(20, True)

    def FormatLog(self, logLines, logAll = False, logHeader = False):
        txt = ''
        allColumnNames = self.columnNames + tuple(sorted(set(logLines[0].iterkeys()).difference(self.columnNames)))
        if self.lastLoggedLine == 0 or logAll or logHeader:
            for name in allColumnNames:
                txt += '%s\t' % name

            txt += '\n'
        for l in xrange(0, len(logLines) - 1):
            logLine = logLines[l]
            if logLine['dateTime'] > self.lastLoggedLine or logAll:
                self.lastLoggedLine = logLine['dateTime']
                for name in allColumnNames:
                    if name in ('dateTime', 'pyDateTime'):
                        txt += '%s\t' % FmtDateEng(logLine[name])
                    elif round(logLine[name], 2).is_integer():
                        txt += '%s\t' % str(logLine[name])
                    else:
                        txt += '%.4f\t' % logLine[name]

                txt += '\n'

        return txt

    def WriteLog(self, minutes = 0, useIncrementalStartPos = False, useLogNotice = False):
        logger = self.LogInfo
        if useLogNotice:
            logger = self.LogNotice
        dumpPath = prefs.GetValue('ProcessHealthLogPath', None)
        if dumpPath is None:
            logger('Will not dump processhealth info since it is not configured in prefs (ProcessHealthLogPath)')
            return
        logger('WriteLog', minutes, useIncrementalStartPos)
        startTime = blue.os.GetWallclockTime()
        logLines = self.GetProcessInfo(minutes, useIncrementalStartPos)
        if not os.path.exists(dumpPath):
            os.makedirs(dumpPath)
        fileName = self._GetLogFileName(dumpPath, self.startDateTime)
        shouldCreateNewFile = not os.path.exists(fileName)
        txt = self.FormatLog(logLines, logHeader=shouldCreateNewFile)
        if shouldCreateNewFile:
            self._SetStartTime()
            fileName = self._GetLogFileName(dumpPath, self.startDateTime)
            with open(fileName, 'w') as f:
                f.write(txt)
        else:
            with open(fileName, 'a') as f:
                f.write(txt)
        diff = (blue.os.GetWallclockTime() - startTime) / float(const.SEC)
        logger('Finished writing out %s entries from processHealth into %s in %.3f seconds' % (len(logLines), fileName, diff))

    def _GetLogFileName(self, dumpPath, time):
        fileName = 'PHS %s %s %s %s %s %s.txt' % (self.computerName,
         self.nodeIndex,
         self.nodeID,
         boot.role,
         blue.os.pid,
         time)
        fileName = os.path.join(dumpPath, fileName.replace(':', '.').replace(' ', '.'))
        return fileName

    def DoOnceEveryHour(self):
        try:
            self.LogProcessMemoryAsSeenByTheOperatingSystem()
        except Exception:
            log.LogException('Failed Log memory')

    def LogProcessMemoryAsSeenByTheOperatingSystem(self):
        realMemory = self._GetProcessMemory(self._pid)
        numberOfEvePlayers = sm.GetService('machoNet').GetNumberOfEVEUsersConnected()
        self.LogNotice('OS Process Memory:', realMemory, 'serverName:', self.computerName, 'nodeID:', self._nodeID, 'serviceMask:', self._serviceMask, 'clusterGroup:', self._clusterGroup, 'nodeSessionCount:', GetNumberOfCharacterSessions(), 'clusterUserCount:', 0 if numberOfEvePlayers is None else numberOfEvePlayers)

    def _GetServerName(self, nodeID):
        machoNet = sm.GetService('machoNet')
        return machoNet.serverNames[nodeID]

    def _GetProcessMemory(self, pid):
        line = subprocess.Popen('tasklist /FO csv /FI "PID eq %s" /NH' % self._pid, stdout=subprocess.PIPE)
        memory = line.stdout.read().split('"')[9]
        return int(memory.split(' ')[0].replace(',', '').replace('.', '')) * 1024
