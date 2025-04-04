#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\sys\alert.py
import base64
import cStringIO
import copy
import gzip
import smtplib
import sys
import types
import zlib
import blue
import eve.common.lib.appConst as const
import log
import stackless
import uthread
import utillib
from carbon.common.script.net import machoNet
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_ANY, ROLE_PLAYER, ROLE_SERVICE, SERVICE_RUNNING, SERVICE_START_PENDING, SERVICE_STOP_PENDING, SERVICE_STOPPED
from carbon.common.script.util.format import FmtAmtEng, FmtDateEng, FmtTimeEng
from cluster import SERVICE_POLARIS
from eveexceptions import ExceptionEater, UnmarshalError
from eveprefs import prefs, boot
LOCATION_TQ = 1
LOCATION_BFC = 2
LOCATION_CCP = 3
LOCATION_OTHER = 4
ORIGIN_UNKNOWN = 0
ORIGIN_CLIENT = 1
ORIGIN_PROXY = 2
ORIGIN_SERVER = 3
LOGGING_BATCHED = 'B'
LOGGING_DETAILS = 'D'
MAX_DETAILED_USER_ERRORS_PER_HOUR = 50
originLabels = {ORIGIN_UNKNOWN: 'unknown',
 ORIGIN_CLIENT: 'client',
 ORIGIN_PROXY: 'proxy',
 ORIGIN_SERVER: 'server'}
BEAN_DELIVERY_TIME = 15

class Alert(Service):
    __guid__ = 'svc.alert'
    __displayname__ = 'Alert Service'
    __exportedcalls__ = {'Alert': [ROLE_SERVICE],
     'SendSimpleEmailAlert': [ROLE_SERVICE],
     'SendMail': [ROLE_SERVICE],
     'SendProxyStackTraceAlert': [ROLE_SERVICE],
     'SendClientStackTraceAlert': [ROLE_PLAYER],
     'BeanCount': [ROLE_ANY],
     'BeanDelivery': [ROLE_ANY],
     'GroupBeanDelivery': [ROLE_ANY],
     'GetCPULoad': [ROLE_SERVICE],
     'LogModeChanged': [ROLE_SERVICE],
     'GetLogModeForError': [ROLE_ANY]}
    if boot.role in ('server',):
        __startupdependencies__ = ['DB2', 'machoNet']
    elif boot.role in ('client', 'proxy'):
        __startupdependencies__ = ['machoNet']
    else:
        raise RuntimeError('Unkown boot role: ' + boot.role)
    __dependencies__ = ['machoNet']
    __notifyevents__ = ['OnBeanPrime']

    def Run(self, memStream = None):
        self.throttles = {}
        self.stacktraceLogMode = {}
        self.stacktracebeancounts = {}
        self.stacktracebeangroupcounts = {}
        self.stackTraceUserCount = {}
        self.healthStats = utillib.KeyVal(nextBeanDelivery=0, totalBeanCount=0, totalErrorCount=0, lastBeanCount=0, lastErrorCount=0)
        self.schema = None
        self.computername = blue.pyos.GetEnv().get('COMPUTERNAME', '?')
        self.mail_defaultrecpt = prefs.GetValue('alertEmailAddress', '').split(';')
        domain = blue.pyos.GetEnv().get('USERDNSDOMAIN', '?').upper()
        if domain == 'EVE.COM':
            self.location = LOCATION_TQ
            location = ' Tranquility'
            self.mail_defaultrecpt = prefs.GetValue('alertEmailAddress', 'stacktraces@ccpgames.com').split(';')
        elif domain == 'SISI.EVE.LOCAL':
            self.location = LOCATION_BFC
            location = ' Singularity'
        elif domain == 'CCP.AD.LOCAL':
            self.location = LOCATION_CCP
            location = ' CCP %s' % domain
        else:
            self.location = LOCATION_OTHER
            location = ''
        self.mail_sender = 'Alert Service on%s %s <alerts@ccpgames.com>' % (location, self.computername)
        self.mail_queue = uthread.Queue()
        self.mail_server = None
        self.tasklets = []
        self.bytesSent = 0
        self.beanServerWrites = 0
        self.groupBeanServerWrites = 0
        self.isLiveCluster = None
        self.errorTypes = {'Info': 'I',
         'Warning': 'W',
         'Error': 'E',
         'Delivering Error To Remote Host': 'D'}
        self.origins = {ORIGIN_SERVER: 'S',
         ORIGIN_PROXY: 'P',
         ORIGIN_CLIENT: 'C'}
        self.tasklets.append(uthread.new(self.__mailqueue))
        self.tasklets.append(uthread.new(self.__BeanDeliveryBoy))
        self.LogInfo('Alert service will deliver errors up to the next tier every', prefs.GetValue('beanDeliveryTime', BEAN_DELIVERY_TIME), 'minutes (prefs.beanDeliveryTime)')

    def Stop(self, stream):
        r = Service.Stop(self, stream)
        for t in self.tasklets:
            t.kill()

        return r

    def IsLiveCluster(self):
        if self.isLiveCluster is None and sm.IsServiceRunning('cache'):
            cacheSvc = sm.GetService('cache')
            if boot.role == 'server' and prefs.clusterMode == 'LIVE' and cacheSvc.Setting('zcluster', 'DB_NAME') == cacheSvc.Setting('zcluster', 'Database'):
                self.isLiveCluster = True
            else:
                self.isLiveCluster = False
                self.LogInfo('This is not a live cluster. Will use detailed logMode for errors.')
        return self.isLiveCluster

    def DbZCluster(self):
        if self.schema is not None:
            return self.schema
        if machoNet.mode != 'client':
            self.schema = self.DB2.GetSchema('zcluster')
            return self.schema
        self.LogError('No DB on Client! ')

    def __GetMailServer(self):
        if not self.mail_server:
            try:
                local_hostname = blue.pyos.GetEnv().get('COMPUTERNAME', '?')
                self.mail_server = None
                server = None
                if hasattr(prefs, 'alertEmailServer'):
                    server = str(prefs.alertEmailServer)
                    self.LogInfo('Alert service using mail server from prefs.ini:', prefs.alertEmailServer)
                elif self.location == LOCATION_TQ:
                    server = '10.210.10.251'
                    self.LogInfo('Alert service using default TQ mailserver', server)
                elif self.location == LOCATION_BFC:
                    server = '10.210.10.251'
                    self.LogInfo('Alert service using default BFC mailserver', server)
                elif self.location == LOCATION_CCP:
                    server = 'rkv-it-exch.ccp.ad.local'
                    self.LogInfo('Alert service using default CCP mailserver', server)
                if server:
                    if sys.version_info[:3] == (2, 2, 1):
                        self.mail_server = smtplib.SMTP(server)
                    else:
                        self.mail_server = smtplib.SMTP(server, local_hostname=local_hostname)
            except StandardError:
                log.LogTraceback('Mail server not working.', severity=log.LGWARN)
                sys.exc_clear()
                self.mail_server = None

        return self.mail_server

    def Alert(self, sender, subject, message, throttle = None, recipients = None, html = 0, sysinfo = 0, attachments = []):
        if throttle:
            if sender in self.throttles and self.throttles[sender] > blue.os.GetWallclockTime():
                return self.throttles[sender]
            self.throttles[sender] = blue.os.GetWallclockTime() + throttle
        return self.SendSimpleEmailAlert(message=message, subject=subject, sysinfo=sysinfo, html=html, recipients=recipients, attachments=attachments)

    def GetSysInfo(self):
        pyinfo = [('pythonver', sys.version)]
        env = blue.pyos.GetEnv()
        created = blue.sysinfo.processStartTime
        kernel = blue.sysinfo.GetProcessTimes().systemTime
        user = blue.sysinfo.GetProcessTimes().userTime
        cputime = kernel + user
        uptime = blue.os.GetWallclockTime() - created
        memInfo = blue.sysinfo.GetMemory()
        workingSetSize = memInfo.workingSet
        pagefileUsage = memInfo.pageFile
        ram = 1 + memInfo.totalPhysical / 1024 / 1024
        hostinfo = [('hostname', env.get('COMPUTERNAME', '?')),
         ('domain', env.get('USERDNSDOMAIN', '?')),
         ('cpuid', env.get('PROCESSOR_IDENTIFIER', '?')),
         ('cpucount', env.get('NUMBER_OF_PROCESSORS', '?')),
         ('cpuspeed', '%s MHz' % blue.sysinfo.cpu.frequency),
         ('starttime', FmtDateEng(created)),
         ('uptime', FmtTimeEng(uptime)),
         ('cputime', FmtTimeEng(cputime)),
         ('kerneltime', FmtTimeEng(kernel)),
         ('usertime', FmtTimeEng(user)),
         ('currentcpu', '%.1f%%' % (self.GetCPULoad(35) * 100.0)),
         ('ram', '%s MB' % ram),
         ('memusage', '%s K' % FmtAmtEng(workingSetSize / 1024)),
         ('vmsize', '%s K' % FmtAmtEng(pagefileUsage / 1024)),
         ('nodeid', sm.services['machoNet'].nodeID)]
        buildinfo = [('version', boot.version),
         ('build', boot.build),
         ('codename', str(boot.codename)),
         ('region', str(boot.region)),
         ('role', machoNet.mode)]
        return pyinfo + hostinfo + buildinfo

    def BeanCount(self, stackIDHash):
        errorID, logMode = self.stacktraceLogMode.get(stackIDHash, (None, None))
        if machoNet.mode == 'proxy' or errorID is None:
            return (errorID, logMode)
        for i in range(30):
            errorID, logMode = self.stacktraceLogMode[stackIDHash]
            if errorID is None:
                blue.pyos.synchro.SleepWallclock(5000)
                continue
            break

        if errorID is not None:
            if logMode == LOGGING_BATCHED:
                self.stacktracebeancounts[errorID] = (self.stacktracebeancounts.get(errorID, [0])[0] + 1, blue.os.GetWallclockTime())
            else:
                self.LogError('Invalid Bean Counting mode: ', logMode)
        return (errorID, logMode)

    def OnClusterStartup(self):
        if machoNet.mode != 'server':
            return
        beans = self.DbZCluster().Errors_Prime()
        self.OnBeanPrime(beans)
        if all([not self.machoNet.IsResurrectedNode(), self.machoNet.GetNodeID() == self.machoNet.GetNodeFromAddress(SERVICE_POLARIS, 0)]):
            self.machoNet.ProxyBroadcast('OnBeanPrime', beans)

    def OnBeanPrime(self, beans):
        if type(beans) == types.DictType:
            self.stacktraceLogMode.update(beans)
        else:
            for bean in beans:
                self.stacktraceLogMode[bean.errorKeyHash] = (bean.errorID, bean.logMode)

    def ConvertFloodingGroupBeansToBeans(self, floodingErrors):
        if len(floodingErrors) == 0:
            return
        groupData = self.stacktracebeangroupcounts
        toDelete = []
        for errorID, usersData in groupData.iteritems():
            if errorID not in floodingErrors:
                continue
            for userID, errorData in usersData.iteritems():
                if errorID in self.stacktracebeancounts:
                    self.stacktracebeancounts[errorID] = (self.stacktracebeancounts.get(errorID, [0])[0] + errorData[0], min(blue.os.GetWallclockTime(), max(self.stacktracebeancounts.get(errorID, [0])[1], errorData[1])))
                else:
                    self.stacktracebeancounts[errorID] = (errorData[0], errorData[1])

            toDelete.append(errorID)

        for errorID in toDelete:
            del self.stacktracebeangroupcounts[errorID]

    def CompressGroupBeans(self, groupBeans):
        res = zlib.compress(blue.marshal.Save(groupBeans))
        return res

    def ExpandGroupBeans(self, compressedGroupBeans):
        if isinstance(compressedGroupBeans, dict):
            return compressedGroupBeans
        res = None
        try:
            res = blue.marshal.Load(zlib.decompress(compressedGroupBeans))
        except (UnmarshalError, zlib.error):
            firstBit = '<error encoding>'
            with ExceptionEater('Encoding some badness in the beancounter'):
                firstBit = base64.b64encode(compressedGroupBeans[:1000])
            self.LogError('BeanDelivery recieved a non-standard bean payload, likely not exefile in origin.  Session:', repr(session), 'First 1000char of compressed payload:', firstBit)
            log.LogException('BeanDelivery recieved a non-standard bean payload')
            with ExceptionEater('Reporting BeanDelivery error to Alert'):
                message = 'The following session sent us a set of Beans that are probably all attacky:\n%s\n\n' % (repr(session),)
                message += 'The compressed payload follows (base64 encoded):\n%s' % (base64.b64encode(compressedGroupBeans),)
                self.Alert('BeanDelivery', 'Non-standard BeanCounting payload', message)

        return res

    def __BeanDeliveryBoy(self):
        while self.state == SERVICE_RUNNING:
            beanDeliveryTime = prefs.GetValue('beanDeliveryTime', BEAN_DELIVERY_TIME)
            self.healthStats.nextBeanDelivery = blue.os.GetWallclockTime() + beanDeliveryTime * const.MIN
            blue.pyos.synchro.SleepWallclock(beanDeliveryTime * 60000)
            try:
                self.CheckAndExpireUserCounts()
                startTime = blue.os.GetWallclockTime()
                try:
                    self.healthStats.lastBeanCount = 0
                    self.healthStats.lastErrorCount = 0
                    for errorID in self.stacktracebeancounts.keys():
                        errorCount, lastDate = self.stacktracebeancounts[errorID]
                        self.healthStats.lastBeanCount += 1
                        self.healthStats.lastErrorCount += errorCount
                        self.healthStats.totalBeanCount += 1
                        self.healthStats.totalErrorCount += errorCount

                except:
                    raise

                if self.stacktracebeancounts or self.stacktracebeangroupcounts:
                    self.LogInfo(machoNet.mode, 'Delivering beans. been count', len(self.stacktracebeancounts), ' group bean count', len(self.stacktracebeangroupcounts))
                    if machoNet.mode == 'client':
                        floodingErrors = self.UpdateLogModes()
                        self.ConvertFloodingGroupBeansToBeans(floodingErrors)
                        beans = self.stacktracebeancounts
                        self.stacktracebeancounts = {}
                        self.bytesSent += len(str(beans))
                        sm.ProxySvc('alert').BeanDelivery(beans)
                        groupBeans = self.stacktracebeangroupcounts
                        self.stacktracebeangroupcounts = {}
                        compressedBeans = self.CompressGroupBeans(groupBeans)
                        self.bytesSent += len(str(compressedBeans))
                        sm.ProxySvc('alert').GroupBeanDelivery(compressedBeans)
                    elif machoNet.mode == 'proxy':
                        beans = self.stacktracebeancounts
                        self.stacktracebeancounts = {}
                        if getattr(self, 'solalert', None) is None:
                            self.solalert = self.session.ConnectToSolServerService('alert')
                        self.bytesSent += len(str(beans))
                        self.solalert.BeanDelivery(beans)
                        groupBeans = self.stacktracebeangroupcounts
                        self.stacktracebeangroupcounts = {}
                        compressedBeans = self.CompressGroupBeans(groupBeans)
                        self.bytesSent += len(str(compressedBeans))
                        self.solalert.GroupBeanDelivery(compressedBeans)
                    elif machoNet.mode == 'server':
                        polarisNodeID = self.machoNet.GetNodeFromAddress(SERVICE_POLARIS, 0)
                        if self.machoNet.GetNodeID() != polarisNodeID:
                            beans = self.stacktracebeancounts
                            self.stacktracebeancounts = {}
                            if getattr(self, 'polarisalert', None) is None:
                                self.polarisalert = self.session.ConnectToSolServerService('alert', polarisNodeID)
                            self.bytesSent += len(str(beans))
                            self.polarisalert.BeanDelivery(beans)
                            groupBeans = self.stacktracebeangroupcounts
                            self.stacktracebeangroupcounts = {}
                            compressedBeans = self.CompressGroupBeans(groupBeans)
                            self.bytesSent += len(str(compressedBeans))
                            self.polarisalert.GroupBeanDelivery(compressedBeans)
                        else:
                            for errorID in self.stacktracebeancounts.keys():
                                errorCount, lastDate = self.stacktracebeancounts[errorID]
                                if lastDate < startTime - const.DAY or lastDate > startTime:
                                    lastDate = startTime
                                del self.stacktracebeancounts[errorID]
                                self.DbZCluster().Errors_Update(errorID, errorCount, lastDate)
                                self.beanServerWrites += 1

                            nodeID = self.machoNet.GetNodeID()
                            beanGroups = self.stacktracebeangroupcounts
                            self.stacktracebeangroupcounts = {}
                            for errorID, userReports in beanGroups.iteritems():
                                for userID, data in userReports.iteritems():
                                    cnt, tm, charID, locationID1, locationID2, argsStr, errNodeID = data
                                    if type(argsStr) == types.UnicodeType:
                                        argsStr = argsStr.encode('ascii', 'replace')
                                    if userID > 0:
                                        self.DbZCluster().ErrorUserDates_Update(errorID, userID, charID, cnt, argsStr, errNodeID, locationID1, locationID2)
                                    self.groupBeanServerWrites += 1
                                    blue.pyos.BeNice()

                    else:
                        self.LogError('WTF??? ', machoNet.mode, '????')
                    self.LogInfo('|', machoNet.mode, '| Delivery of beans #Bytes:', self.bytesSent, '# DB bean writes', self.beanServerWrites, '# DB group writes', self.groupBeanServerWrites, ' time (ms):', blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTime()))
                    self.bytesSent = 0
                    self.bytesSent = 0
                    self.groupBeanServerWrites = 0
            except Exception as e:
                self.LogError('An exception has occurred: ', e)
                raise
                sys.exc_clear()

    def BeanDelivery(self, beans):
        for errorID, v in beans.iteritems():
            c, l = v
            if errorID in self.stacktracebeancounts:
                self.stacktracebeancounts[errorID] = (self.stacktracebeancounts.get(errorID, [0])[0] + c, min(blue.os.GetWallclockTime(), max(self.stacktracebeancounts.get(errorID, [0])[1], l)))
            else:
                self.stacktracebeancounts[errorID] = v

    def GroupBeanDelivery(self, compressedGroupBeans, nodeID = None):
        groupBeans = self.ExpandGroupBeans(compressedGroupBeans)
        for errorID, userReports in groupBeans.iteritems():
            for userID, data in userReports.iteritems():
                if errorID not in self.stacktracebeangroupcounts:
                    self.stacktracebeangroupcounts[errorID] = {}
                cnt, tm, charID, locationID1, locationID2, argsStr, errNodeID = data
                if userID in self.stacktracebeangroupcounts[errorID]:
                    currentCount = self.stacktracebeangroupcounts[errorID].get(userID, [0])[0]
                    currentTime = min(blue.os.GetWallclockTime(), max(self.stacktracebeangroupcounts[errorID].get(userID, [0])[1], tm))
                    self.stacktracebeangroupcounts[errorID][userID] = (currentCount + cnt,
                     currentTime,
                     charID,
                     locationID1,
                     locationID2,
                     argsStr,
                     errNodeID or self.machoNet.GetNodeID())
                else:
                    self.stacktracebeangroupcounts[errorID][userID] = (cnt,
                     tm,
                     charID,
                     locationID1,
                     locationID2,
                     argsStr,
                     errNodeID or self.machoNet.GetNodeID())
                if machoNet.mode == 'proxy':
                    if errorID in self.stackTraceUserCount:
                        self.stackTraceUserCount[errorID].users.add(userID)
                    else:
                        self.stackTraceUserCount[errorID] = utillib.KeyVal(timestamp=blue.os.GetWallclockTime(), users=set([userID]))
                blue.pyos.BeNice()

    def SendStackTraceAlert(self, stackID, stackTrace, mode, **kw):
        if getattr(self, 'state', SERVICE_START_PENDING) != SERVICE_RUNNING:
            return
        if 'machoNet' not in sm.services:
            return
        if machoNet.mode == 'client':
            if not sm.services['machoNet'].IsConnected():
                return
        elif sm.GetService('machoNet').IsClusterShuttingDown():
            return
        f = stackless.getcurrent().frame
        try:
            while f:
                f = f.f_back
                if f and f.f_code.co_filename.endswith('alert.py') and f.f_code.co_name == '__SendStackTraceAlert':
                    return

        finally:
            f = None

        uthread.pool('AlertSvc::__SendStackTraceAlert', self.SendStackTraceAlert_thread, stackID, stackTrace, mode, kw)

    def SendStackTraceAlert_thread(self, stackID, stackTrace, mode, kw):
        if getattr(self, 'state', SERVICE_START_PENDING) != SERVICE_RUNNING:
            return
        try:
            if machoNet.mode != 'client' and 'nodeID' not in kw:
                kw = copy.copy(kw)
                kw['nodeID'] = self.machoNet.GetNodeID()
            self.__SendStackTraceAlert(stackID, stackTrace, mode, **kw)
        except StandardError:
            log.LogException('Exception in Error Logging, preventing infinite recursion', toAlertSvc=0)
            sys.exc_clear()

    def SendProxyStackTraceAlert(self, stackID, stackTrace, mode, **kw):
        if 'origin' not in kw:
            kw['origin'] = ORIGIN_PROXY
        return self.__SendStackTraceAlert(stackID, stackTrace, mode, **kw)

    def SendClientStackTraceAlert(self, stackID, stackTrace, mode, nextErrorKeyHash = None):
        userID, charID, locationID1, locationID2 = self._GetSessionInfo()
        return self.__SendStackTraceAlert(stackID, stackTrace, mode, userID=userID, nextErrorKeyHash=nextErrorKeyHash, origin=ORIGIN_CLIENT)

    def __SendStackTraceAlert(self, stackID, stackTrace, mode, nodeID = None, userID = None, nextErrorKeyHash = None, origin = ORIGIN_SERVER):

        def GetArgumentsFromStackTrace(stackTrace):
            argPos = stackTrace.find('Arguments:')
            if argPos > 0:
                return stackTrace[argPos:]
            return ''

        uthread.Lock(self, 'SendStackTraceAlert', stackID[0])
        try:
            if machoNet.mode == 'client':
                if stackID[0] not in self.stacktraceLogMode:
                    self.LogInfo(machoNet.mode, "Don't know what beancounting method to use, crossing the wire.")
                    errorID, logMode = sm.ProxySvc('alert').BeanCount(stackID[0])
                    if errorID is None:
                        self.LogInfo(machoNet.mode, 'The proxy wants a trace.')
                        self.bytesSent += len(str(stackID)) + len(str(stackTrace))
                        self.stacktraceLogMode[stackID[0]] = sm.ProxySvc('alert').SendClientStackTraceAlert(stackID, stackTrace, mode, nextErrorKeyHash)
                        return
                    self.stacktraceLogMode[stackID[0]] = (errorID, logMode)
                for i in range(30):
                    errorID, logMode = self.stacktraceLogMode[stackID[0]]
                    if errorID is None:
                        self.LogInfo(machoNet.mode, "we're already crossing the wire to acquire this dude's beancounting properties")
                        blue.pyos.synchro.SleepWallclock(5000)
                        continue
                    break

                if errorID is None:
                    self.LogInfo(machoNet.mode, "Couldn't beancount it, so just bugger it.")
                elif logMode == LOGGING_BATCHED:
                    self.stacktracebeancounts[errorID] = (self.stacktracebeancounts.get(errorID, [0])[0] + 1, blue.os.GetWallclockTime())
                elif logMode == LOGGING_DETAILS:
                    self.stacktracebeancounts[errorID] = (self.stacktracebeancounts.get(errorID, [0])[0] + 1, blue.os.GetWallclockTime())
                    if errorID not in self.stacktracebeangroupcounts:
                        self.stacktracebeangroupcounts[errorID] = {}
                    sessionUserID, charID, locationID1, locationID2 = self._GetSessionInfo()
                    if userID is None:
                        userID = sessionUserID
                    argStr = GetArgumentsFromStackTrace(stackTrace)
                    if userID in self.stacktracebeangroupcounts[errorID]:
                        self.stacktracebeangroupcounts[errorID][userID] = (self.stacktracebeangroupcounts[errorID].get(userID, [0])[0] + 1,
                         blue.os.GetWallclockTime(),
                         charID,
                         locationID1,
                         locationID2,
                         argStr,
                         None)
                    else:
                        self.stacktracebeangroupcounts[errorID][userID] = (1,
                         blue.os.GetWallclockTime(),
                         charID,
                         locationID1,
                         locationID2,
                         argStr,
                         None)
                else:
                    self.LogError('Strange... unknown bean counting method specified ', logMode, errorID)
            elif machoNet.mode == 'proxy':
                if getattr(self, 'solalert', None) is None:
                    self.solalert = self.session.ConnectToSolServerService('alert')
                if nodeID and nodeID in self.machoNet.GetConnectedSolNodes():
                    solalert = self.session.ConnectToSolServerService('alert', nodeID)
                else:
                    solalert = self.solalert
                try:
                    userID, charID, locationID1, locationID2 = self._GetSessionInfo()
                    if stackID[0] not in self.stacktraceLogMode:
                        self.LogInfo(machoNet.mode, "Don't know what beancounting method to use, crossing the wire.")
                        errorID, logMode = solalert.BeanCount(stackID[0])
                        if errorID is None:
                            self.LogInfo(machoNet.mode, 'The sol node wants a trace.')
                            self.bytesSent += len(str(stackID)) + len(str(stackTrace))
                            self.stacktraceLogMode[stackID[0]] = solalert.SendProxyStackTraceAlert(stackID, stackTrace, mode, nodeID=self.machoNet.GetNodeID(), userID=userID, nextErrorKeyHash=nextErrorKeyHash, origin=origin)
                        else:
                            self.stacktraceLogMode[stackID[0]] = (errorID, logMode)
                    else:
                        for i in range(30):
                            errorID, logMode = self.stacktraceLogMode[stackID[0]]
                            if errorID is None:
                                self.LogInfo(machoNet.mode, "we're already crossing the wire to acquire this dude's beancounting properties")
                                blue.pyos.synchro.SleepWallclock(5000)
                                continue
                            break

                        if errorID is None:
                            self.LogInfo(machoNet.mode, "Couldn't beancount it, so just bugger it.")
                        elif logMode == LOGGING_BATCHED:
                            self.LogInfo(machoNet.mode, 'Batched beancounting selected')
                            self.stacktracebeancounts[errorID] = (self.stacktracebeancounts.get(errorID, [0])[0] + 1, blue.os.GetWallclockTime())
                        elif logMode == LOGGING_DETAILS:
                            self.LogInfo(machoNet.mode, 'Grouped beancounting selected')
                            self.stacktracebeancounts[errorID] = (self.stacktracebeancounts.get(errorID, [0])[0] + 1, blue.os.GetWallclockTime())
                            argStr = GetArgumentsFromStackTrace(stackTrace)
                            ID = userID or 0
                            if errorID not in self.stacktracebeangroupcounts:
                                self.stacktracebeangroupcounts[errorID] = {}
                            if ID in self.stacktracebeangroupcounts[errorID]:
                                self.stacktracebeangroupcounts[errorID][ID] = (self.stacktracebeangroupcounts[errorID].get(ID, [0])[0] + 1,
                                 blue.os.GetWallclockTime(),
                                 charID,
                                 locationID1,
                                 locationID2,
                                 argStr,
                                 nodeID or self.machoNet.GetNodeID())
                            else:
                                self.stacktracebeangroupcounts[errorID][ID] = (1,
                                 blue.os.GetWallclockTime(),
                                 charID,
                                 locationID1,
                                 locationID2,
                                 argStr,
                                 nodeID or self.machoNet.GetNodeID())
                        else:
                            self.LogError('Strange... unknown bean counting method specified ', logMode)
                except StandardError as e:
                    self.LogError('Error during error handling:', e)
                    self.solalert = None
                    sys.exc_clear()

            elif stackID[0] not in self.stacktraceLogMode:
                k = stackID[1].encode('ascii', 'replace')
                if type(stackTrace) == types.UnicodeType:
                    stackTrace = unicode(stackTrace).encode('ascii', 'replace')
                self.beanServerWrites += 1
                errorTypeChar = self.errorTypes.get(mode, 'U')
                originChar = self.origins.get(origin, 'U')
                if self.IsLiveCluster():
                    logMode = 'B'
                else:
                    logMode = 'D'
                r = self.DbZCluster().Errors_Insert(k[:4000], stackTrace, stackID[0], nextErrorKeyHash, errorTypeChar, originChar, logMode)[0]
                self.stacktraceLogMode[stackID[0]] = (r.errorID, r.logMode)
                self.machoNet.ClusterBroadcast('OnBeanPrime', {stackID[0]: (r.errorID, r.logMode)})
            else:
                errorID, logMode = self.stacktraceLogMode[stackID[0]]
                if logMode == LOGGING_BATCHED:
                    self.BeanDelivery({errorID: (1, blue.os.GetWallclockTime())})
                elif logMode == LOGGING_DETAILS:
                    self.BeanDelivery({errorID: (1, blue.os.GetWallclockTime())})
                    argStr = GetArgumentsFromStackTrace(stackTrace)
                    ID = userID or 0
                    self.GroupBeanDelivery({errorID: {ID: (1,
                                    blue.os.GetWallclockTime(),
                                    0,
                                    0,
                                    0,
                                    argStr,
                                    nodeID or self.machoNet.GetNodeID())}})
                else:
                    self.LogError('Strange... unknown bean counting method specified ', logMode)
            if not sm.IsServiceRunning('machoNet'):
                return
            return self.stacktraceLogMode.get(stackID[0], (None, None))
        finally:
            uthread.UnLock(self, 'SendStackTraceAlert', stackID[0])

    def SendSimpleEmailAlert(self, message, recipients = None, subject = None, sysinfo = 1, html = 0, attachments = [], subjectonly = 0):
        self.LogInfo('SendSimpleEmailAlert ', (len(message),
         recipients,
         subject,
         sysinfo,
         html))
        if recipients is None:
            recipients = self.mail_defaultrecpt
        elif type(recipients) in types.StringTypes:
            recipients = [recipients]
        elif type(recipients) != types.ListType:
            raise RuntimeError("SendSimpleEmailAlert: 'recipients' must be a list of strings")
        if not recipients:
            self.LogInfo('Not sending alert, no recipient specified', subject)
            return
        timestamp = FmtDateEng(blue.os.GetWallclockTime(), 'ns')
        if subject is None:
            subject = 'Server Alert: Alert from node %s on %s at %s' % (sm.services['machoNet'].nodeID, self.computername, timestamp)
        elif subjectonly == 0:
            subject = 'Server Alert: %s at %s' % (subject, timestamp)
        if sysinfo:
            if html:
                message += '<br>\n<br>\nSysinfo:<br><table border=1>\n'
                for k, v in self.GetSysInfo():
                    message += '<tr><td>%s</td><td>%s</td></tr>\n' % (k, v)

            else:
                message += '\n\n' + '-' * 78 + '\n'
                for k, v in self.GetSysInfo():
                    message += '%-15s%s\n' % (k + ':', v)

        from email.MIMEText import MIMEText
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEBase import MIMEBase
        from email import encoders
        msg = MIMEMultipart()
        if html:
            subtype = 'html'
            charset = 'iso8859'
        else:
            subtype = 'plain'
            charset = 'us-ascii'
        if type(message) is unicode:
            message = message.encode('utf-8')
            charset = 'utf-8'
        att = MIMEText(message, subtype, charset)
        msg.attach(att)
        subject = subject.replace('\n', '').replace('\r', '')
        msg['Subject'] = subject
        msg['From'] = self.mail_sender
        msg['To'] = ', '.join(recipients)
        for attName, attData in attachments:
            io = cStringIO.StringIO()
            zipfile = gzip.GzipFile(attName, 'w', 9, io)
            zipfile.write(attData)
            zipfile.close()
            att = MIMEBase('application', 'gz')
            att.set_payload(io.getvalue())
            encoders.encode_base64(att)
            att.add_header('Content-Disposition', 'attachment', filename=attName + '.gz')
            msg.attach(att)

        self.SendMail(self.mail_sender, recipients, msg.as_string(0))

    def SendMail(self, *args, **kw):
        channel = None
        if kw.get('wait', False):
            del kw['wait']
            channel = stackless.channel()
        self.mail_queue.put((channel, args, kw))
        if channel:
            return channel.receive()

    def __mailqueue(self):
        self.LogInfo('Alert:  Starting Mail Queue thread')
        try:
            while self.state != SERVICE_STOPPED:
                try:
                    channel, args, kw = self.mail_queue.get()
                    self.LogInfo('Alert:  Got mail from Mail Queue')
                    srv = self.__GetMailServer()
                    if srv:
                        self.LogInfo('Alert:  Sending mail')
                        srv.sendmail(*args, **kw)
                        self.LogInfo('Alert:  Mail sent')
                        if channel:
                            channel.send(True)
                    else:
                        self.LogWarn('Alert:  No mail server available, mail not sent.  sendmail args=', args, 'kw=', kw)
                        if channel:
                            channel.send(False)
                except smtplib.SMTPServerDisconnected as e:
                    self.mail_server = None
                    self.mail_queue.put((channel, args, kw))
                    self.LogWarn('Failed to send alert, SMTP server disconnected. Will try again in 1 minute. SMTP Error: %s' % str(e))
                    sys.exc_clear()
                    blue.pyos.synchro.SleepWallclock(60000)
                except TaskletExit:
                    if 'channel' in locals() and channel is not None:
                        channel.send(False)
                    raise
                except:
                    if 'channel' in locals() and channel is not None:
                        channel.send(False)
                    self.LogError('Alert:  Unexpected error during mailqueue processing')

        except TaskletExit:
            if hasattr(self, 'state') and self.state not in (SERVICE_STOPPED, SERVICE_STOP_PENDING):
                raise
        finally:
            self.LogInfo('Alert:  Stopping Mail Queue thread')

    def GetCPULoad(self, seconds = 300):
        now = blue.os.GetWallclockTime()
        then = now - seconds * const.SEC
        total = 0L
        lastTime = now
        i = len(blue.pyos.cpuUsage) - 1
        while i > 0 and blue.pyos.cpuUsage[i].timestamp >= then:
            total += blue.pyos.cpuUsage[i].userProcessCpuUsage
            lastTime = blue.pyos.cpuUsage[i].timestamp
            i -= 1

        if lastTime == now:
            return 0.0
        return min(float(total) / (float(now) - float(lastTime)), 1.0)

    def _GetSessionInfo(self):
        if session:
            return (session.userid,
             session.charid,
             None,
             None)
        return (None, None, None, None)

    def NotifyAllSolAndProxyOfLogModeChange(self, errorID, logMode):
        res = self.session.ConnectToAllServices('alert').LogModeChanged(errorID, logMode)

    def LogModeChanged(self, errorID, logMode):
        self.LogInfo(machoNet.mode, ' LogModeChanged ', errorID, ' to mode ', logMode)
        for k, v in self.stacktraceLogMode.iteritems():
            if v[0] == errorID:
                self.stacktraceLogMode[k] = (v[0], logMode)

    def UpdateLogModes(self):
        self.LogInfo(machoNet.mode, 'UpdateLogModes')
        changes, flooded = sm.ProxySvc('alert').GetLogModeForError(self.stacktraceLogMode)
        self.LogInfo(machoNet.mode, 'UpdateLogModes got changes =', changes)
        self.LogInfo(machoNet.mode, 'UpdateLogModes got These Flooded =', flooded)
        for errorHash, newLogMode in changes.iteritems():
            errorID = self.stacktraceLogMode[errorHash][0]
            self.stacktraceLogMode[errorHash] = (errorID, newLogMode)
            if newLogMode != LOGGING_DETAILS and errorID in self.stacktracebeangroupcounts:
                del self.stacktracebeangroupcounts[errorID]

        return flooded

    def GetLogModeForError(self, errorIDs):
        self.LogInfo(machoNet.mode, 'GetLogModeForError', self.stacktraceLogMode)
        result = {}
        flooded = []
        for errorID, logMode in errorIDs.iteritems():
            if errorID in self.stacktraceLogMode:
                if logMode[1] != self.stacktraceLogMode[errorID][1]:
                    result[errorID] = self.stacktraceLogMode[errorID][1]
            if logMode[1] == LOGGING_DETAILS:
                if logMode[0] in self.stackTraceUserCount and len(self.stackTraceUserCount[logMode[0]].users) > MAX_DETAILED_USER_ERRORS_PER_HOUR:
                    flooded.append(logMode[0])

        return (result, flooded)

    def CheckAndExpireUserCounts(self):
        for errorID, userData in self.stackTraceUserCount.iteritems():
            if blue.os.TimeDiffInMs(userData.timestamp, blue.os.GetWallclockTime()) > const.HOUR / const.MSEC:
                userData.timestamp = blue.os.GetWallclockTime()
                userData.users = set()

    def DoNastyLoggingTest(self, randomUser = False, maxLoops = 500000, showProgress = False):
        if prefs.clusterMode not in ('LOCAL', 'TEST'):
            print 'BAD BAD BOY!, you are not to call this on a live server!!!'
            return
        self.tasklets.append(uthread.new(self.__DoNastyErrorLogSimulation, randomUser, maxLoops, showProgress))

    def __DoNastyErrorLogSimulation(self, randomUser = False, maxLoops = 50000, showProgress = False):
        import random
        if prefs.clusterMode not in ('LOCAL', 'TEST'):
            print 'BAD BAD BOY!, you are not to call this on a live server!!!'
            return
        if randomUser:
            print 'DoNastyErrorLogSimulation is generating many errors with !!RANDOM!! User IDs'
        else:
            print 'DoNastyErrorLogSimulation is generatijng many errors with session User ID'
        userIDStart = 10000
        userIDRange = 25
        cnt = 0
        while self.state == SERVICE_RUNNING and cnt < maxLoops:
            blue.pyos.BeNice()
            errorKey = '============ TEST EXCEPTION %d ============'
            errorStack = '\n                            TEST EXCEPTION %d logged at  MM/DD/YYYY HH:MM:SS Unhandled exception in <TaskletExt object at 226a9588, abps=1001, ctxt=\'Tick:.SleepWallclock\'> \n                            Caught at: /common/lib/Fakebluepy.py(37) in CallWrapper \n                            Thrown at: /common/lib/Fakebluepy.py(24) in CallWrapper \n                                       /common/lib/Fakenasty.py(1344) in OnFileModified_ \n                                       /common/lib/Fakenasty.py(1595) in Bootstrap \n                                       /common/lib/Fakenasty.py(2295) in ImportFromFile \n                                       /common/lib/Fakenasty.py(468) in GetCode \n                                       /common/lib/Fakenasty.py(517) in Compile \n                                       /common/lib/Fakenasty.py(556) in Compile_int \n                                       Exception:     \n                                       File "D:/depot/games/EVE-DEV/eve/server/script/../../../carbon/common/script/sys/alert.py", line 329     \n\n\n                                       def SendStackTraceAlert(self, stackID, stackTrace, mode, **kw):       \n                                       ^    IndentationError: expected an indented block  \n                                       Arguments:    \n                                       self :  <nasty.Compilor object at 0x037D5F88>    \n                                       pathname :  \'script:/../../../carbon/common/script/sys/alert.py\' \n                                       Locals:     Lots! #%d\n                                       Thread Locals:   session was None  System Information:  Node ID: 1733 \n                                       | Node Name: RobertPC | Total CPU load: 0%% | Process memory in use: 420 MB | Physical memory left: 213 MB \n                         '
            testUserID = None
            cnt += 1
            if randomUser:
                testUserID = random.randint(userIDStart, userIDStart + userIDRange)
                if cnt % 100000 == 0:
                    userIDStart += userIDRange
            for i in range(10, 15):
                self.SendStackTraceAlert((2000 + i, errorKey % i), errorStack % (i, cnt), 'error', userID=testUserID)

            if showProgress:
                print '.',
                if cnt % 100 == 0:
                    print ''
                    print 'cnt = ', cnt

        print '============================== all done'
