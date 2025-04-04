#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\sys\serviceManager.py
import __builtin__
import sys
import threading
import time
import types
import weakref
from collections import defaultdict
import blue
import bluepy
import carbon.common.script.sys.basesession as base
import log
import monolithmetrics
import stackless
import telemetry
import uthread
from caching.memoize import Memoize
from carbon.common.script.net.machobase import GetLogName as GetMachoLogName
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_FAILED, SERVICE_RUNNING, SERVICE_STARTING_DEPENDENCIES, SERVICE_START_PENDING, SERVICE_STOPPED, SERVICE_STOP_PENDING
from carbon.common.script.util import logUtil
from carbon.common.script.util.commonutils import IsFullLogging
from carbon.common.script.util.timerstuff import ClockThisWithoutTheStars
from eveexceptions import MethodNotCalledFromClient, ServiceNotFound
from eveprefs import boot, prefs
from utillib import DAG

def ObjectShouldReceiveMessages(obj):
    return not isinstance(obj, Service) or obj.state == SERVICE_RUNNING


class ServiceManager(logUtil.LogMixin):
    __guid__ = 'service.ServiceManager'
    __instance = None
    __init_lock = threading.Semaphore()

    @staticmethod
    def Instance():
        if ServiceManager.__instance is None:
            raise RuntimeError('ServiceManager not initialized')
        return ServiceManager.__instance

    def __init__(self, startInline = []):
        with ServiceManager.__init_lock:
            if ServiceManager.__instance is not None:
                raise RuntimeError('Multiple instances of ServiceManager are not allowed in a process')
            logUtil.LogMixin.__init__(self, 'svc.ServiceManager')
            self.state = SERVICE_START_PENDING
            self.services = {}
            self.dependants = {}
            self.notify = defaultdict(list)
            self.notifyObs = defaultdict(list)
            self.startInline = startInline
            self.blockedServices = []
            self.startupTimes = {}
            blue.pyos.scatterEvent = self.ScatterEvent
            blue.pyos.sendEvent = self.SendEvent
            blue.pyos.chainEvent = self.ChainEvent
            ServiceManager.__instance = __builtin__.sm = self

    def _BuildClassMap(self):
        import svc
        self.classmap = {name:(name, getattr(svc, name)) for name in dir(svc)}
        self.classmapWithReplacements = self.classmap.copy()
        for name, svcclass in self.classmap.values():
            self.classmapWithReplacements[name] = (name, getattr(svc, self.GetServiceImplementation(name)))

    def _CreateDependencyGraph(self):
        dag = DAG()
        for k, v in self.services.iteritems():
            depends = v.__dependencies__ + getattr(v, '__startupdependencies__', [])
            for d in depends:
                if type(d) is not str:
                    d = d[0]
                if d in self.services:
                    dag.InsertEdge(k, d)

        dag.Invert()
        return dag

    def SaveDependencyGraph(self, filename = None):
        try:
            dag = self._CreateDependencyGraph()
            if filename is None:
                import os
                filename = '%s/service-dependencies-%s.dot' % (os.getcwd(), boot.role)
            with open(filename, 'w') as fp:
                fp.write(dag.ToDot())
        except Exception:
            log.LogException('Failed saving service dependency graph.')

    def Run(self, servicesToRun, servicesToBlock = []):
        self.run = 1
        if self.state not in (SERVICE_START_PENDING, SERVICE_RUNNING):
            if self.state == SERVICE_STOPPED:
                self.state = SERVICE_START_PENDING
            else:
                raise RuntimeError, "can't run a service when state is " + repr(self.state)
        self._BuildClassMap()
        blue.pyos.AddExitProc(self.Stop)
        for block in servicesToBlock:
            if block not in self.blockedServices:
                self.blockedServices.append(block)

        if len(servicesToRun):
            print 'Starting services'
            was = blue.pyos.taskletTimer.timesliceWarning
            try:
                blue.pyos.taskletTimer.timesliceWarning = 5000
                for each in servicesToRun:
                    self.StartService(each, reason='autoexec')

                for each in self.services.keys():
                    counter = 0
                    sleepTimeMs = 1
                    while self.services[each].state == SERVICE_START_PENDING:
                        counter += 1
                        if counter % 100 == 0:
                            print "Service start still pending: '%s', sleeping..." % self.services[each].__guid__
                        blue.pyos.synchro.SleepWallclock(sleepTimeMs)
                        sleepTimeMs *= 2
                        if sleepTimeMs > 100:
                            sleepTimeMs = 100

                for each in self.services.keys():
                    if hasattr(self.services[each], 'PostRun'):
                        self.services[each].PostRun()

            finally:
                blue.pyos.taskletTimer.timesliceWarning = was

            print 'Starting services - Done'
        self.state = SERVICE_RUNNING

    def Stop(self):
        self.logChannel.Log('ServiceManager.Stop(), stopping services')
        dag = self._CreateDependencyGraph()
        self.logChannel.Log('== BEGIN SERVICE LIST ==')
        order = []
        while dag.graph:
            leaves = dag.Leaves()
            if not leaves:
                break
            order.extend(leaves)
            for l in leaves:
                dag.RemoveNode(l)

            self.logChannel.Log('==leaves==')
            self.logChannel.Log(','.join(leaves))

        if dag.graph:
            leaves = dag.graph.keys()
            order.extend(leaves)
            self.logChannel.Log('==nonleaves==')
            self.logChannel.Log(','.join(leaves))
        self.logChannel.Log('== ENDOF SERVICE LIST ==')
        self.run = 0
        import blue
        old_block_trap = stackless.getcurrent().block_trap
        stackless.getcurrent().block_trap = 1
        self.state = SERVICE_STOP_PENDING
        try:
            for k in order:
                try:
                    v = self.services[k]
                except KeyError:
                    self.LogWarn('Warning, the service', k, 'has been stopped already but something that depends on it might still be running!')
                    sys.exc_clear()
                    continue

                if not hasattr(v, 'state'):
                    self.logChannel.Log("ServiceManager.Stop(), service '" + str(k) + " doesn't have state therefore has already stopped")
                elif v.state not in (SERVICE_STOPPED, SERVICE_STOP_PENDING):
                    self.logChannel.Log("ServiceManager.Stop(), stopping service '" + str(k) + "'")
                    try:
                        v.state = SERVICE_STOP_PENDING
                        for notify in v.__notifyevents__:
                            self.notify[notify].remove(v)

                        v.Stop(blue.MemStream())
                    except StandardError:
                        log.LogException()
                        sys.exc_clear()
                    finally:
                        v.state = SERVICE_STOPPED

                else:
                    self.logChannel.Log("ServiceManager.Stop(), service '" + str(k) + "' is already stopping")

        finally:
            stackless.getcurrent().block_trap = old_block_trap
            self.state = SERVICE_STOPPED

        for v in self.services.itervalues():
            for a in v.__dict__.keys():
                if a not in ('logChannel', 'logContexts', 'state'):
                    delattr(v, a)

        self.logChannel.Log('ServiceManager.Stop(), services stopped.')

    def ParseServiceClass(self, serviceName):
        return 'svc.' + serviceName

    def Reload(self, serviceNames):
        self._BuildClassMap()
        if not serviceNames:
            return
        self.LogWarn('Reloading services: %s' % ', '.join(serviceNames))
        for each in serviceNames:
            if each not in self.services:
                continue
            if getattr(self.services[each], '__update_on_reload__', True):
                continue
            ms = blue.MemStream()
            try:
                try:
                    self.StopService(each, 0, ms)
                finally:
                    if self.services.has_key(each):
                        del self.services[each]

                self.GetService(each, ms)
            except Exception:
                log.LogException('Trying to reload service: %s' % each)
                sys.exc_clear()

        self.LogWarn('Reloading services - Done')

    def StartServiceAndWaitForRunningState(self, serviceName, ms = None, reason = None):
        srv = self.StartService(serviceName, ms=None, reason=reason)
        desiredStates = (SERVICE_RUNNING,)
        errorStates = (SERVICE_FAILED, SERVICE_STOPPED)
        self.WaitForServiceObjectState(srv, desiredStates, errorStates)
        return srv

    @telemetry.ZONE_METHOD
    def WaitForServiceObjectState(self, svc, desiredStates, errorStates = (SERVICE_FAILED,)):
        i = 0
        sleepTimeMs = 1
        while svc.state not in desiredStates:
            if svc.state in errorStates:
                svc.LogError('Service ', svc.__logname__, ' got in an unexpected state', 'raising error')
                if svc.__error__:
                    raise svc.__error__[1], None, svc.__error__[2]
                else:
                    raise RuntimeError, 'Service %s made unexpected state transition' % svc.__logname__
            blue.pyos.synchro.SleepWallclock(sleepTimeMs)
            sleepTimeMs *= 2
            if sleepTimeMs > 100:
                sleepTimeMs = 100
            if i % 600 == 0 and i > 0:
                svc.LogWarn('WaitForServiceObjectState has been sleeping for a long time waiting for ', svc.__logname__, ' to either get to state ', desiredStates, 'current state is', svc.state)
            i += 1

    def GetServiceIfStarted(self, serviceName):
        if serviceName in self.services:
            srv = self.services[serviceName]
            self.WaitForServiceObjectState(srv, (SERVICE_RUNNING,))
            return srv

    def GetServiceIfRunning(self, serviceName):
        if self.IsServiceRunning(serviceName):
            srv = self.services[serviceName]
            return srv

    def GetService(self, serviceName, ms = None):
        srv = self.services.get(serviceName, None)
        if srv and srv.state == SERVICE_RUNNING:
            return srv
        if serviceName in self.services:
            if self.services[serviceName].state in (SERVICE_START_PENDING, SERVICE_STARTING_DEPENDENCIES):
                log.LogTraceback('Possible service deadlock detected!', toAlertSvc=False, severity=log.LGWARN)
        return self.StartServiceAndWaitForRunningState(serviceName, ms, reason='GetService')

    @telemetry.ZONE_METHOD
    def StartService(self, serviceName, ms = None, reason = 'StartService'):
        telemetry.APPEND_TO_ZONE(serviceName)
        srv = self.services.get(serviceName, None)
        if srv and srv.state == SERVICE_RUNNING:
            return srv
        if serviceName in self.services:
            srv = self.services[serviceName]
        else:
            if serviceName in self.blockedServices:
                raise RuntimeError('%s has been blocked from running on this system' % serviceName)
            srv = self.CreateServiceInstance(serviceName)
            self.services[serviceName] = srv
        if srv.state in (SERVICE_START_PENDING,):
            return srv
        if srv.state == SERVICE_STARTING_DEPENDENCIES:
            desiredStates = (SERVICE_START_PENDING, SERVICE_RUNNING)
            errorStates = (SERVICE_FAILED, SERVICE_STOPPED)
            self.WaitForServiceObjectState(srv, desiredStates, errorStates)
            return srv
        if self.state in (SERVICE_STOP_PENDING, SERVICE_STOPPED):
            raise RuntimeError, "Can't start service " + serviceName + ' when service manager is shutting down'
        if 'machoNet' in self.services and self.services['machoNet'].IsClusterShuttingDown():
            log.LogTraceback("Attempt to start service '%s' during cluster shutdown" % serviceName)
            raise RuntimeError("Cannot start service '%s' during cluster shutdown" % serviceName)
        if srv.state == SERVICE_FAILED:
            return srv
        try:
            r = reason
            if reason in ('GetService', 'StartService'):
                up = 4
                if reason == 'StartService':
                    up = 2
                r = '%s - called from %s' % (reason, log.WhoCalledMe(up))
            self.LogInfo('Starting', serviceName, '. Reason:', r)
        except:
            pass

        srv.state = SERVICE_STARTING_DEPENDENCIES
        srv.__error__ = None
        try:
            self.dependants[serviceName] = []
            if srv.__startupdependencies__:
                self.LogInfo('starting startup dependencies for %s, which are: %s' % (serviceName, str(srv.__startupdependencies__)))
                for each in srv.__startupdependencies__:
                    if each == srv.__guid__.split('.')[1]:
                        self.LogError('Found a service with a dependancy on it self:', each, '. The service reference will not be assigned, things will probaly blow up')
                        continue
                    if type(each) is str:
                        each = (each, each)
                    depname, asname = each
                    if not self.IsServiceRunning(depname):
                        self.LogInfo(serviceName, 'is waiting while', depname, 'is started')
                    depService = self.StartServiceAndWaitForRunningState(depname, reason='startup dependency for %s' % serviceName)
                    self.dependants[depname].append(serviceName)
                    if getattr(boot, 'replaceDependencyServiceWrappers', 'false').lower() != 'true' or not depService.IsRunning():
                        setattr(srv, asname, srv.session.ConnectToService(depname))
                    else:
                        setattr(srv, asname, depService)

            srv.state = SERVICE_START_PENDING
            if srv.__dependencies__:
                uthread.new(self._LoadServiceDependenciesAsych, srv, serviceName).context = serviceName + ' _LoadServiceDependenciesAsych'
            for notify in srv.__notifyevents__:
                if not hasattr(srv, notify):
                    raise RuntimeError('MissingSvcExportAttribute', serviceName, 'notify', notify)
                self.notify[notify].append(srv)

        except Exception as e:
            srv.state = SERVICE_FAILED
            srv.__error__ = sys.exc_info()
            raise

        if ms:
            ms.Seek(0)
        args = (ms,)
        if serviceName in self.startInline:
            self.StartServiceRun(srv, args, serviceName)
        else:
            uthread.pool(serviceName + ' StartServiceRun', self.StartServiceRun, srv, args, serviceName, stackless_tracing_enabled=False)
        return srv

    def _LoadServiceDependenciesAsych(self, srv, serviceName):
        self.LogInfo('starting dependencies for %s, which are: %s' % (serviceName, str(srv.__dependencies__)))
        for each in srv.__dependencies__:
            if type(each) is str:
                each = (each, each)
            depname, asname = each
            depService = self.StartService(depname, reason='dependency for %s' % serviceName)
            self.dependants[depname].append(serviceName)
            if getattr(boot, 'replaceDependencyServiceWrappers', 'false').lower() != 'true' or not depService.IsRunning():
                setattr(srv, asname, srv.session.ConnectToService(depname))
            else:
                setattr(srv, asname, depService)

    @Memoize
    def GetServiceImplementation(self, target):
        found = target
        foundPriority = -1
        for name, svcclass in self.classmap.itervalues():
            replaces = getattr(svcclass, '__replaceservice__', None)
            if replaces == target:
                priority = getattr(svcclass, '__replacepriority__', 0)
                if priority > foundPriority:
                    found = name
                    foundPriority = priority

        return found

    @telemetry.ZONE_METHOD
    def CreateServiceInstance(self, serviceName):
        old_block_trap = stackless.getcurrent().block_trap
        stackless.getcurrent().block_trap = 1
        try:
            try:
                createName, createClass = self.classmapWithReplacements[serviceName]
            except KeyError:
                self._BuildClassMap()
                try:
                    createName, createClass = self.classmapWithReplacements[serviceName]
                except KeyError:
                    raise ServiceNotFound(serviceName)

            if createName != serviceName:
                print 'Replacing service %r with %r' % (serviceName, createName)
            replaceService = getattr(createClass, '__replaceservice__', None)
            if replaceService is not None and replaceService != serviceName:
                raise RuntimeError('Must not start %s directly as it replaces %s' % (serviceName, replaceService))
            srv = createClass()
            if not isinstance(srv, Service):
                raise RuntimeError('Service name %r does not resolve to a service class (%r)' % (serviceName, createClass))
            srv.__servicename__ = serviceName
            srv.session = base.GetServiceSession(serviceName)
            self.VerifyServiceExports(srv, serviceName)
            return srv
        finally:
            stackless.getcurrent().block_trap = old_block_trap

    def VerifyServiceExports(self, srv, serviceName):
        for funcName, paramList in srv.__exportedcalls__.iteritems():
            if not hasattr(srv, funcName):
                raise RuntimeError('MissingSvcExportAttribute', serviceName, 'exported call', funcName)
            if type(paramList) == types.ListType:
                tmp = {}
                if len(paramList):
                    tmp['role'] = paramList[0]
                    tmp['preargs'] = paramList[1:]
                paramList = tmp
            if type(paramList) == types.DictType:
                for k, v in paramList.iteritems():
                    if k not in ('role', 'caching', 'preargs', 'fastcall', 'precall', 'postcall', 'callhandlerargs', 'input', 'resolve') or k == 'role' and type(v) not in (types.IntType, types.LongType):
                        self.LogError('Service %s has illegal function declaration for %s:  %s is not a valid metadata key' % (serviceName, funcName, k))
                    elif k == 'fastcall':
                        if int(v) not in (0, 1):
                            self.LogError('Service %s has illegal function declaration for %s:  %s is not a valid setting for fastcall' % (serviceName, funcName, v))
                    elif k == 'preargs':
                        for eachArg in v:
                            if type(eachArg) != types.StringType or eachArg not in srv.session.__persistvars__ and eachArg not in srv.session.__nonpersistvars__:
                                self.LogError('Service %s has illegal function declaration for %s:  %s is not a valid prearg' % (serviceName, funcName, eachArg))

                    elif k == 'caching' and 'objectCaching' in self.services:
                        if not v:
                            self.LogError('Service %s has illegal function declaration for %s:  caching must have subinfo' % (serviceName, funcName))
                        for k2, v2 in v.iteritems():
                            if k2 not in ('sessionInfo', 'versionCheck', 'client', 'server', 'proxy'):
                                self.LogError('Service %s has illegal function declaration for %s:  %s is not a valid caching subinfo key' % (serviceName, funcName, k2))
                            elif k2 == 'sessionInfo' and v2 not in srv.session.__persistvars__:
                                self.LogError('Service %s has illegal function declaration for %s:  %s is not a valid session info prearg' % (serviceName, funcName, v2))

            else:
                self.LogError('Service %s has illegal function declaration for %s:  %s is not a valid metadata info type' % (serviceName, funcName, type(paramList)))

    @telemetry.ZONE_METHOD
    def StartServiceRun(self, svc, args, namen):
        try:
            t0 = time.clock()
            try:
                if boot.role == 'client' and getattr(prefs, 'clientServicesWait', 'true').lower() != 'true':
                    svc.state = SERVICE_RUNNING
                    svc.Run(*args)
                else:
                    svc.state = SERVICE_START_PENDING
                    with bluepy.Timer('StartService::ServiceStartRun::' + namen):
                        svc.Run(*args)
                    svc.state = SERVICE_RUNNING
                    if getattr(boot, 'replaceDependencyServiceWrappers', 'false').lower() == 'true':
                        for depName in self.dependants[namen]:
                            depSvc = self.StartService(depName)
                            setattr(depSvc, namen, svc)

            finally:
                t = time.clock() - t0

        except Exception as e:
            svc.state = SERVICE_FAILED
            svc.__error__ = sys.exc_info()
            self.LogError('Failed to start service %s' % namen)
            raise

        self.startupTimes[namen] = t
        if t < 60:
            svc.LogInfo('Service', namen, 'required %-3.3f' % t, ' seconds to startup')
        else:
            svc.LogWarn('Service', namen, 'startup took %-3.3f' % t, ' seconds')
        serviceStartupTimeTxt = 'Service %-25s Startup time: %-3.3fs' % (namen, t)
        print serviceStartupTimeTxt
        self.LogNotice(serviceStartupTimeTxt)

    def StopService(self, serviceName, halt = 1, ms = None):
        self.LogInfo('Stopping %s' % serviceName)
        if not self.services.has_key(serviceName):
            return
        srv = self.services[serviceName]
        if srv.state in (SERVICE_STOP_PENDING, SERVICE_STOPPED):
            return
        oldstate = srv.state
        srv.state = SERVICE_STOP_PENDING
        for notify in srv.__notifyevents__:
            self.notify[notify].remove(srv)

        if halt:
            for each in self.dependants[serviceName]:
                self.StopService(each)

        try:
            srv.Stop(ms)
        except Exception:
            srv.state = oldstate
            log.LogException('Trying to stop service %s ' % serviceName)
            sys.exc_clear()

        if srv.state != SERVICE_STOPPED:
            srv.state = SERVICE_STOPPED
            del self.services[serviceName]

    def GetDependecyGraph(self, startupDependencies = False):
        depGraph = DAG()
        import svc
        depAttr = '__dependencies__'
        if startupDependencies:
            depAttr = '__startupdependencies__'
        for k, v in svc.__dict__.items():
            if hasattr(v, '__guid__'):
                depGraph.AddNode(k)
                for dep in getattr(v, depAttr, []):
                    depGraph.InsertEdge(k, dep)

        return depGraph

    def IsServiceRunning(self, serviceName):
        return serviceName in self.services and self.services[serviceName].IsRunning()

    def RemoteSvc(self, serviceName):
        if boot.role == 'client':
            return session.ConnectToRemoteService(serviceName)
        self.LogError('The method sm.RemoteSvc can be called from the client only.')
        raise MethodNotCalledFromClient('sm.RemoteSvc')

    def ProxySvc(self, serviceName):
        if boot.role == 'client':
            return session.ConnectToRemoteService(serviceName, self.services['machoNet'].myProxyNodeID)
        self.LogError('The method sm.ProxySvc can be called from the client only.')
        raise MethodNotCalledFromClient('sm.ProxySvc')

    def GetActiveServices(self):
        ret = []
        for k, srv in self.services.iteritems():
            if srv.state == SERVICE_RUNNING:
                ret.append(k)

        return ret

    def GetServicesState(self):
        ret = {}
        for k, srv in self.services.iteritems():
            ret[k] = srv.state

        return ret

    def GetLogName(self, thingie):
        if isinstance(thingie, weakref.ref):
            thingie = thingie()
        return getattr(thingie, '__logname__', GetMachoLogName(thingie))

    def SendEvent(self, eventid, *args, **keywords):
        return self.SendEventWithoutTheStars(eventid, args, keywords)

    def SendEventWithoutTheStars(self, eventid, args, keywords = None):
        if keywords is None:
            keywords = {}
        if not eventid.startswith('Do'):
            self.LogError('SendEvent called with event ', eventid, ".  All events sent via SendEvent should start with 'Do'")
            self.LogError("Not only is the programmer responsible for this a 10z3r, but he wears his mother's underwear as well")
            log.LogTraceback()
        if eventid not in self.notify and eventid not in self.notifyObs:
            self.LogInfo("Orphan'd event.  ", eventid, "doesn't have any listeners")
        shouldLogMethodCalls = self.ShouldLogMethodCalls()
        if shouldLogMethodCalls:
            if IsFullLogging():
                self.LogMethodCall('SendEvent(', eventid, ',*args=', args, ',**kw=', keywords, ')')
            else:
                self.LogMethodCall('SendEvent(', eventid, ')')
        prefix = blue.pyos.taskletTimer.GetCurrent() + '::SendEvent_' + eventid + '::'
        old_block_trap = stackless.getcurrent().block_trap
        stackless.getcurrent().block_trap = 1
        ret = []
        try:
            for srv in self.notify.get(eventid, []):
                try:
                    logname = prefix + self.GetLogName(srv)
                    if ObjectShouldReceiveMessages(srv):
                        if shouldLogMethodCalls:
                            self.LogMethodCall('Calling ', logname)
                        ret.append(ClockThisWithoutTheStars(logname, getattr(srv, eventid), args, keywords))
                    elif shouldLogMethodCalls:
                        self.LogMethodCall('Skipping ', logname, ' (service not running)')
                except StandardError:
                    self.LogError('In %s.%s' % (getattr(srv, '__guid__', logname), eventid))
                    log.LogException()
                    sys.exc_clear()

            notifiedToRemove = []
            for weakObj in self.notifyObs[eventid]:
                obj = weakObj()
                if obj is None:
                    notifiedToRemove.append(weakObj)
                else:
                    try:
                        if shouldLogMethodCalls:
                            logname = prefix + str(obj)
                            self.LogMethodCall('Calling ', logname)
                        apply(getattr(obj, eventid), args, keywords)
                    except StandardError:
                        self.LogError('In %s.%s' % (getattr(weakObj, '__guid__', self.GetLogName(weakObj)), eventid))
                        log.LogException()
                        sys.exc_clear()

            for toRemove in notifiedToRemove:
                if toRemove in self.notifyObs[eventid]:
                    self.notifyObs[eventid].remove(toRemove)

        finally:
            bt = 0
            if old_block_trap:
                bt = 1
            stackless.getcurrent().block_trap = bt
            return tuple(ret)

    def ChainEvent(self, eventid, *args, **keywords):
        return self.ChainEventWithoutTheStars(eventid, args, keywords)

    def ChainEventWithoutTheStars(self, eventid, args, keywords = None):
        if keywords is None:
            keywords = {}
        if not eventid.startswith('Process'):
            self.LogError('ChainEvent called with event ', eventid, ".  All events sent via ChainEvent should start with 'Process'")
            self.LogError("Not only is the programmer responsible for this a 10z3r, but he wears his mother's underwear as well")
            log.LogTraceback()
        if stackless.getcurrent().block_trap or stackless.getcurrent().is_main:
            raise RuntimeError("ChainEvent is blocking by design, but you're block trapped.  You have'll have to find some alternative means to do Your Thing, dude.")
        if eventid not in self.notify and eventid not in self.notifyObs:
            self.LogInfo("Orphan'd event.  ", eventid, "doesn't have any listeners")
        shouldLogMethodCalls = self.ShouldLogMethodCalls()
        if shouldLogMethodCalls:
            self.LogMethodCall('ChainEvent(', eventid, ',*args=', args, ',**kw=', keywords, ')')
        prefix = blue.pyos.taskletTimer.GetCurrent() + '::ChainEvent_' + eventid + '::'
        ret = []
        for srv in self.notify[eventid]:
            contextName = self.GetLogName(srv)
            try:
                logname = prefix + contextName
                if ObjectShouldReceiveMessages(srv):
                    if shouldLogMethodCalls:
                        self.LogMethodCall('Calling ', logname)
                    retval = ClockThisWithoutTheStars(logname, getattr(srv, eventid), args, keywords)
                    ret.append(retval)
                elif shouldLogMethodCalls:
                    self.LogMethodCall('Skipping ', logname, ' (service not running)')
            except StandardError:
                self.LogError('In %s.%s' % (contextName, eventid))
                log.LogException()
                sys.exc_clear()

        notifiedToRemove = []
        for weakObj in self.notifyObs[eventid]:
            obj = weakObj()
            if obj is None:
                notifiedToRemove.append(weakObj)
            else:
                contextName = self.GetLogName(weakObj)
                try:
                    logname = prefix + contextName
                    if shouldLogMethodCalls:
                        self.LogMethodCall('Calling ', prefix + str(obj))
                    ClockThisWithoutTheStars(logname, getattr(obj, eventid), args, keywords)
                except StandardError:
                    self.LogError('In %s.%s:' % (contextName, eventid))
                    log.LogException()
                    sys.exc_clear()

        for toRemove in notifiedToRemove:
            if toRemove in self.notifyObs[eventid]:
                self.notifyObs[eventid].remove(toRemove)

        return tuple(ret)

    def ScatterEvent(self, eventid, *args, **keywords):
        return self.ScatterEventWithoutTheStars(eventid, args, keywords)

    def ScatterEventWithoutTheStars(self, eventid, args, keywords = None):
        if keywords is None:
            keywords = {}
        if not eventid.startswith('On'):
            self.LogError('ScatterEvent called with event ', eventid, ".  All events sent via ScatterEvent should start with 'On'.")
            self.LogError("Not only is the programmer responsible for this a 10z3r, but he wears his mother's underwear as well")
            log.LogTraceback()
        shouldLogMethodCalls = self.ShouldLogMethodCalls()
        if shouldLogMethodCalls:
            if IsFullLogging():
                self.LogMethodCall('ScatterEvent(', eventid, ',*args=', args, ',**kw=', keywords, ')')
            else:
                self.LogMethodCall('ScatterEvent(', eventid, ')')
        prefix = blue.pyos.taskletTimer.GetCurrent() + '::ScatterEvent_' + eventid + '::'
        for srv in self.notify[eventid]:
            try:
                logname = prefix + self.GetLogName(srv)
                if ObjectShouldReceiveMessages(srv):
                    if shouldLogMethodCalls:
                        self.LogMethodCall('Calling ', logname)
                    srvGuid = getattr(srv, '__guid__', logname)
                    uthread.worker(prefix + srvGuid, self.MollycoddledUthread, srvGuid, eventid, getattr(srv, eventid), args, keywords)
                elif shouldLogMethodCalls:
                    self.LogMethodCall('Skipping ', logname, ' (service not running)')
            except Exception:
                log.LogException()

        notifiedToRemove = []
        for weakObj in self.notifyObs[eventid]:
            try:
                obj = weakObj()
                func = getattr(obj, eventid, None)
                if obj is None or func is None:
                    notifiedToRemove.append(weakObj)
                else:
                    if shouldLogMethodCalls:
                        logname = prefix + str(obj)
                        self.LogMethodCall('Calling ', logname)
                    uthread.workerWithoutTheStars('', func, args, keywords)
            except Exception:
                log.LogException()

        for toRemove in notifiedToRemove:
            if toRemove in self.notifyObs[eventid]:
                self.notifyObs[eventid].remove(toRemove)

    def NotifySessionChange(self, eventid, *args, **keywords):
        return self.NotifySessionChangeWithoutTheStars(eventid, args, keywords)

    def NotifySessionChangeWithoutTheStars(self, eventid, args, keywords = None):
        if keywords is None:
            keywords = {}
        if eventid not in ('DoSessionChanging', 'ProcessSessionChange', 'OnSessionChanged'):
            raise RuntimeError('NotifySessionChange called with eventid ', eventid, '. Must be one of DoSessionChanging, ProcessSessionChange or OnSessionChanged')
        if eventid == 'ProcessSessionChange' and stackless.getcurrent().block_trap or stackless.getcurrent().is_main:
            raise RuntimeError("ChainEvent (NotifySessionChange) is blocking by design, but you're block trapped.")
        ret = []
        if 'machoNet' in self.services and self.services['machoNet'].IsClusterShuttingDown():
            self.LogNotice('Not notifying anyone about %s as the cluster is shutting down' % eventid)
            return ret
        if eventid == 'DoSessionChanging':
            old_block_trap = stackless.getcurrent().block_trap
            stackless.getcurrent().block_trap = 1
        shouldLogMethodCalls = self.ShouldLogMethodCalls()
        if shouldLogMethodCalls:
            self.LogMethodCall('NotifySessionChange(', eventid, ',*args=', args, ',**kw=', keywords, ')')
        prefix = blue.pyos.taskletTimer.GetCurrent() + '::NotifySessionChange_' + eventid + '::'
        myNodeID = self.services['machoNet'].GetNodeID()
        isSessionRelevant = boot.role != 'server' or session.contextOnly
        try:
            for srv in self.notify[eventid]:
                try:
                    logname = prefix + self.GetLogName(srv)
                    if ObjectShouldReceiveMessages(srv):
                        if shouldLogMethodCalls:
                            self.LogMethodCall('Calling ' + logname)
                        if eventid == 'OnSessionChanged':
                            if not isSessionRelevant and srv.MachoResolve(session.GetActualSession()) == myNodeID:
                                isSessionRelevant = True
                            srvGuid = getattr(srv, '__guid__', logname)
                            uthread.worker(prefix + srvGuid, self.MollycoddledUthread, srvGuid, eventid, getattr(srv, eventid), args, keywords)
                        else:
                            retval = ClockThisWithoutTheStars(logname, getattr(srv, eventid), args, keywords)
                            ret.append(retval)
                    elif shouldLogMethodCalls:
                        self.LogMethodCall('Skipping ', logname, ' (service not running)')
                except StandardError:
                    log.LogException('In %s.%s' % (getattr(srv, '__guid__', self.GetLogName(srv)), eventid))
                    sys.exc_clear()

            notifiedToRemove = []
            for weakObj in self.notifyObs[eventid]:
                obj = weakObj()
                if obj is None or not getattr(obj, eventid, None):
                    notifiedToRemove.append(weakObj)
                else:
                    try:
                        if shouldLogMethodCalls:
                            logname = prefix + str(obj)
                            self.LogMethodCall('Calling ', logname)
                        if eventid == 'OnSessionChanged':
                            uthread.workerWithoutTheStars('', getattr(obj, eventid), args, keywords)
                        else:
                            ClockThisWithoutTheStars(prefix + self.GetLogName(weakObj), getattr(obj, eventid), args, keywords)
                    except StandardError:
                        self.LogError('In %s.%s' % (getattr(weakObj, '__guid__', self.GetLogName(srv)), eventid))
                        log.LogException()
                        sys.exc_clear()

            for toRemove in notifiedToRemove:
                if toRemove in self.notifyObs[eventid]:
                    self.notifyObs[eventid].remove(toRemove)

            if not session.contextOnly:
                if not isSessionRelevant:
                    if session.irrelevanceTime is None:
                        session.irrelevanceTime = blue.os.GetWallclockTime()
                        log.LogInfo('CTXSESS: session ', session.sid, ' = ', session, ' is no longer relevant to any service')
                elif session.irrelevanceTime is not None:
                    log.LogInfo('CTXSESS: session ', session.sid, ' became relevant again')
                    session.irrelevanceTime = None
        finally:
            if eventid == 'DoSessionChanging':
                bt = 0
                if old_block_trap:
                    bt = 1
                stackless.getcurrent().block_trap = bt

        return tuple(ret)

    def MollycoddledUthread(self, guid, eventid, func, args, keywords):
        try:
            apply(func, args, keywords)
        except:
            self.LogError('In %s.%s' % (guid, eventid))
            log.LogException()
            sys.exc_clear()

    def FavourMe(self, fn):
        self.notify[fn.__name__].remove(fn.im_self)
        self.notify[fn.__name__] = [fn.im_self] + self.notify[fn.__name__]

    def UnfavourMe(self, fn):
        if fn.im_self in self.notify[fn.__name__]:
            self.notify[fn.__name__].remove(fn.im_self)
            self.notify[fn.__name__] = self.notify[fn.__name__] + [fn.im_self]
        else:
            self.LogWarn('Cannot unfavour ', fn.im_self, ' from ', fn.__name__, ", since it's not a notification listener")

    def RegisterForNotifyEvent(self, ob, notify):
        if ob not in self.notify[notify]:
            self.LogInfo('Adding event', notify, 'for', ob)
            self.notify[notify].append(ob)

    def UnregisterForNotifyEvent(self, ob, notify):
        try:
            self.notify[notify].remove(ob)
        except ValueError:
            pass
        except KeyError:
            pass

    @telemetry.ZONE_METHOD
    def RegisterNotify(self, ob):
        if hasattr(ob, '__notifyevents__'):
            if isinstance(ob, Service):
                for notify in ob.__notifyevents__:
                    if ob not in self.notify[notify]:
                        self.notify[notify].append(ob)

            else:
                for notify in ob.__notifyevents__:
                    if weakref.ref(ob) not in self.notifyObs[notify]:
                        self.notifyObs[notify].append(weakref.ref(ob))

        else:
            self.LogError('An object is calling registernotify without there being any notifyevents, the object is ', ob)
            log.LogTraceback()

    def UnregisterNotify(self, ob):
        if hasattr(ob, '__notifyevents__'):
            if isinstance(ob, Service):
                for notify in ob.__notifyevents__:
                    if ob in self.notify[notify]:
                        self.notify[notify].remove(ob)

            else:
                for notify in ob.__notifyevents__:
                    self.notifyObs[notify] = filter(lambda x: x != weakref.ref(ob) and x() is not None, self.notifyObs[notify])

        else:
            self.LogError('An object is calling unregisternotify without there being any notifyevents, the object is ', ob)
            log.LogTraceback()
