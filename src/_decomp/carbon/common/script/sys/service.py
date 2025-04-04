#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\sys\service.py
import types
import weakref
import sys
import cPickle
import binascii
import traceback
import blue
import locks
import log
import stackless
import uthread
from carbon.common.script.sys.serviceConst import *
from carbon.common.script.util.logUtil import supersafestr
from carbon.common.script.util.timerstuff import ClockThisWithoutTheStars
from cluster import SERVICE_BEYONCE, SERVICE_STATION, SERVICE_CHARACTER, SERVICE_CHATX, SERVICE_USER, SERVICE_CLUSTERSINGLETON
from eve.common.lib.appConst import CHARNODE_MOD
from eveexceptions import UserError
from stdlogutils import LineWrap
from eveprefs import prefs, boot
consts = {}
for k, v in globals().items():
    if type(v) in (types.IntType, types.LongType):
        consts[k] = v

callWrapperLocks = {}
callWrapperID = 0
allCallWrappers = weakref.WeakValueDictionary({})

def GetCallWrappers():
    global allCallWrappers
    return allCallWrappers


class CachedResult():

    def __init__(self, result):
        self.result = result


class FastCallWrapper(object):

    def __init__(self, session, obj, method, parent):
        self.session = session
        self.callable = getattr(obj, method)
        self.parent = parent

    def __repr__(self):
        return '<FastCallWrapper session:%r, callable:%r>' % (self.session, self.callable)

    def __call__(self, *args, **keywords):
        with self.session.Masquerade({'base.caller': weakref.ref(self.parent)}):
            return self.callable(*args, **keywords)


class CallWrapper():
    if boot.role == 'client':
        __precall__ = ['PreCall_IsExportedCall', 'PreCall_CheckPreArgs', 'PreCall_CachedMethodCall']
    else:
        __precall__ = ['PreCall_IsExportedCall',
         'PreCall_RoleCheck',
         'PreCall_CheckPreArgs',
         'PreCall_CachedMethodCall',
         'PreCall_Lock']
    __postcall__ = ['PostCall_CachedMethodCall', 'PostCall_LogCompletedMethodCall', 'PostCall_UnLock']

    def __init__(self, session, object, method, parent, logname = None):
        global callWrapperID
        if logname is None:
            import carbon.common.script.net.machobase as macho
            logname = macho.GetLogName(object)
        self.__logname__ = logname
        self.__session__ = session
        self.__method__ = method
        if method.endswith('_Ex'):
            self.__method_without_Ex__ = method[:-3]
        else:
            self.__method_without_Ex__ = method
        self.__callable__ = object
        self.__parent__ = parent
        self.__metadata__ = getattr(self.__callable__, '__exportedcalls__', {}).get(self.__method_without_Ex__, [])
        self.__thread__ = stackless.getcurrent()
        self.requiredRole = ROLE_SERVICE
        callWrapperID += 1
        allCallWrappers[callWrapperID] = self

    def __call__(self, *args, **keywords):
        machoNet = sm.GetServiceIfRunning('machoNet')
        if machoNet and machoNet.IsClusterShuttingDown() and session.userid:
            log.general.Log('Cluster shutting down, rejecting service call from %s' % session.userid, log.LGNOTICE)
            return
        from carbon.common.script.net.objectCaching import CacheOK
        from carbon.common.script.sys.basesession import CallTimer
        with CallTimer(self.__logname__ + '::' + self.__method_without_Ex__):
            self.__arguments__ = args
            mask = self.__session__.Masquerade({'base.caller': weakref.ref(self.__parent__)})
            try:
                cookies = {}
                result = None
                tb = None
                try:
                    try:
                        for method in self.__precall__:
                            if type(self.__metadata__) == types.DictType:
                                extra = self.__metadata__.get('callhandlerargs', {})
                            else:
                                extra = {}
                            cookieName = method
                            if type(method) == types.StringType:
                                method = getattr(self.__callable__, method, getattr(self, method, None))
                            cookies[cookieName] = apply(method, (self.__method__, args, keywords), extra)

                    except CacheOK as result:
                        tb = sys.exc_info()[2]
                        sys.exc_clear()
                    except CachedResult as result:
                        tb = sys.exc_info()[2]
                        sys.exc_clear()
                    except Exception as result:
                        tb = sys.exc_info()[2]
                        sys.exc_clear()
                    except:
                        log.LogTraceback('Bummer in service.py, all bets are off')
                        raise

                    try:
                        if result is None:
                            args2 = args
                            if self.__method_without_Ex__ == self.__method__ or not session.role & ROLE_SERVICE:
                                preargs = []
                                if type(self.__metadata__) == types.DictType:
                                    if 'preargs' in self.__metadata__:
                                        preargs = self.__metadata__['preargs']
                                elif len(self.__metadata__) > 1:
                                    preargs = self.__metadata__[1:]
                                if preargs:
                                    args2 = len(preargs) * [None] + list(args)
                                    for i in range(len(preargs)):
                                        args2[i] = getattr(session, preargs[i])

                            try:
                                if boot.role == 'server' and self.requiredRole in (ROLE_ANY, ROLE_PLAYER) and getattr(session, 'clientID', None) is not None:
                                    if prefs.GetValue('enableSecurityMonitor', 0):
                                        sm.GetService('securityMonitor').LogCallFromClient(getattr(self.__callable__, '__guid__', 'guid not found'), self.__method_without_Ex__, args2, keywords)
                            except Exception as e:
                                log.LogException('Exception invoking the security monitor. Continuing processing the call')
                                sys.exc_clear()

                            if hasattr(self.__callable__, 'PreCallAction'):
                                self.__callable__.PreCallAction(self.__method_without_Ex__)
                            result = apply(getattr(self.__callable__, self.__method_without_Ex__), args2, keywords)
                    except UserError as result:
                        tb = sys.exc_info()[2]
                        sys.exc_clear()
                    except Exception as result:
                        tb = sys.exc_info()[2]
                        sys.exc_clear()
                    except:
                        log.LogTraceback('OMG caught something else during call')
                        raise

                    for method in self.__postcall__:
                        try:
                            if type(self.__metadata__) == types.DictType:
                                extra = self.__metadata__.get('callhandlerargs', {})
                            else:
                                extra = {}
                            if type(method) == types.StringType:
                                method = getattr(self.__callable__, method, getattr(self, method, None))
                            apply(method, (cookies,
                             result,
                             self.__method__,
                             args,
                             keywords), extra)
                        except CacheOK as result:
                            tb = sys.exc_info()[2]
                            sys.exc_clear()
                        except CachedResult as result:
                            tb = sys.exc_info()[2]
                            sys.exc_clear()
                        except Exception as result:
                            tb = sys.exc_info()[2]
                            sys.exc_clear()
                        except:
                            log.LogTraceback('argh!  caught something else during call')
                            raise

                    if result is not None:
                        if isinstance(result, Exception):
                            raise result, None, tb
                        elif isinstance(result, CachedResult):
                            return result.result
                finally:
                    tb = None

            finally:
                mask.UnMask()
                self.__dict__.clear()

            return result

    def PreCall_StartCallTimer(self, method, args, keywords, **mykeywords):
        from carbon.common.script.sys.basesession import CallTimer
        return CallTimer(self.__logname__ + '::' + self.__method_without_Ex__)

    def PostCall_StopCallTimer(self, cookies, result, method, args, keywords, **mykeywords):
        sct = cookies.get('PreCall_StartCallTimer', None)
        if sct is not None:
            sct.Done()

    __machomethods__ = ('MachoResolve', 'MachoBindObject', 'MachoResolveObject', 'MachoGetObjectBoundToSession')

    def PreCall_IsExportedCall(self, method, args, keywords, **mykeywords):
        if method in ('SetLogInfo', 'SetLogWarning', 'SetLogNotice'):
            return
        if method not in self.__callable__.__exportedcalls__ and method not in self.__machomethods__:
            if not (self.__method__ != self.__method_without_Ex__ and self.__method_without_Ex__ in self.__callable__.__exportedcalls__):
                raise RuntimeError('In %s, method %s is not exported' % (self.__logname__, self.__method_without_Ex__))

    def PreCall_RoleCheck(self, method, args, keywords, **mykeywords):
        if not session.role & ROLE_SERVICE:
            if type(self.__metadata__) == types.DictType:
                role = self.__metadata__.get('role', ROLE_SERVICE)
            elif len(self.__metadata__):
                role = self.__metadata__[0]
            elif method in self.__machomethods__:
                role = ROLE_ANY
            else:
                role = ROLE_SERVICE
            self.requiredRole = role
            if not role & session.role:
                session.LogSessionError("Called %s::%s, which requires role 0x%x, which the user doesn't have. User has role 0x%x" % (self.__logname__,
                 method,
                 role,
                 session.role))
                raise RuntimeError('RoleNotAssigned', "%s::%s requires role 0x%x, which the user doesn't have. User has role 0x%x. Calling session: %s" % (self.__logname__,
                 method,
                 role,
                 session.role,
                 str(session)))

    def PreCall_CheckPreArgs(self, method, args, keywords, **mykeywords):
        if not (session.role & ROLE_SERVICE and method.endswith('_Ex')):
            if type(self.__metadata__) == types.DictType:
                preargs = self.__metadata__.get('preargs', [])
            elif len(self.__metadata__):
                preargs = self.__metadata__[1:]
            else:
                preargs = []
            for each in preargs:
                prearg = getattr(session, each)
                if prearg is None:
                    session.LogSessionError('A required parameter exception occurred while the user was calling %s::%s.  The missing parameter was %s' % (self.__logname__, self.__method_without_Ex__, each))
                    raise RuntimeError('RequiredParameterException', "%s::%s requires parameter %s, which the session doesn't have.  Calling session: %s" % (self.__logname__,
                     self.__method_without_Ex__,
                     each,
                     str(session)))

    def PostCall_LogCompletedMethodCall(self, cookies, result, method, args, keywords, **mykeywords):
        logChannel = log.methodcalls
        if logChannel.IsOpen(log.LGINFO):
            if isinstance(result, Exception):
                eorr = ', EXCEPTION='
            else:
                eorr = ', retval='
            if keywords:
                logwhat = [self.__logname__,
                 '::',
                 method,
                 ' args=',
                 args,
                 ', keywords={',
                 keywords,
                 '}',
                 eorr,
                 result]
            else:
                logwhat = [self.__logname__,
                 '::',
                 method,
                 ' args=',
                 args,
                 eorr,
                 result]
            try:
                s = ''.join(map(supersafestr, logwhat))
                if len(s) > 2500:
                    s = s[:2500]
                logChannel.Log(s, log.LGINFO, 1)
            except TypeError:
                logChannel.Log('[X]'.join(map(supersafestr, logwhat)).replace('\x00', '\\0'), log.LGINFO, 1)
                sys.exc_clear()
            except UnicodeEncodeError:
                logChannel.Log('[U]'.join(map(lambda x: x.encode('ascii', 'replace'), map(unicode, logwhat))), log.LGINFO, 1)
                sys.exc_clear()

    def PreCall_Lock(self, method, args, keywords, **mykeywords):
        lock = mykeywords.get('lock.lock', 1)
        if lock:
            scope = mykeywords.get('lock.scope', 'usersession')
            if scope == 'usersession' and self.__session__.role & ROLE_SERVICE:
                return
            useargs = mykeywords.get('lock.useargs', 0)
            try:
                group = mykeywords['lock.group']
            except KeyError:
                group = (self.__logname__, method)
                if scope == 'instance':
                    group = self.__logname__

            if useargs:
                k = ('PreCall_Lock', group, args)
            else:
                k = ('PreCall_Lock', group)
            if scope in ('usersession', 'session'):
                k = (k, 'session', self.__session__.sid)
            elif scope == 'connection':
                k = (k, 'connection', self.__parent__.__c2ooid__)
            elif scope == 'instance':
                k = (k, 'instance', self.__parent__.GetInstanceID())
            elif scope == 'service':
                if isinstance(self.__callable__, CoreService):
                    k = (k, 'service', self.__parent__.GetInstanceID())
                else:
                    srv = sm.StartService(self.__parent__.__serviceName__)
                    k = (k, 'service', srv.startedWhen)
            elif scope in ('class', 'global'):
                if scope == 'class':
                    try:
                        k = (k, scope, self.__callable__.__class__.__name__)
                    except:
                        k = (k,
                         scope,
                         'logname',
                         self.__logname__)

            l = callWrapperLocks.get(k, None)
            if not l:
                l = [uthread.Semaphore(k), None]
                callWrapperLocks[k] = l
                cool = True
            else:
                cool = l[0].IsCool()
            if not cool:
                reaction = mykeywords.get('lock.reaction', 'block')
                if reaction == 'raise':
                    othermethod = '<unknown>'
                    if l[1] is not None:
                        othermethod = l[1][0]
                    raise UserError(mykeywords.get('lock.raisemsg', 'CallGroupLocked'), {'thismethod': method,
                     'group': group,
                     'scope': scope,
                     'othermethod': othermethod})
                else:
                    if reaction == 'inform':
                        keywords['reentrancy'] = l[1]
                        return
                    if reaction == 'ignore':
                        raise CachedResult(None)
            sys.exc_clear()
            l[0].acquire()
            l[1] = (method, args, keywords)
            return k

    def PostCall_UnLock(self, cookies, result, method, args, keywords, **mykeywords):
        k = cookies.get('PreCall_Lock', None)
        if k is not None:
            l = callWrapperLocks[k]
            l[1] = None
            l[0].release()
            if l[0].IsCool():
                try:
                    if callWrapperLocks[k] is l:
                        del callWrapperLocks[k]
                except KeyError:
                    pass

    def PreCall_CachedMethodCall(self, method, args, keywords, **mykeywords):
        machoVersion = keywords.get('machoVersion', None)
        if machoVersion and not mykeywords.get('PreCall_CachedMethodCall.retainMachoVersion', 0):
            if len(keywords) == 1:
                keywords.clear()
            else:
                del keywords['machoVersion']
        cacheInfo = sm.GetService('objectCaching').PerformCachedMethodCall(self.__callable__, self.__logname__, self.__method_without_Ex__, args, machoVersion)
        cachable, versionCheck, throwOK, cachedResultRecord, cacheKey, cacheDetails = cacheInfo
        if cachable and not versionCheck:
            if throwOK:
                from carbon.common.script.net.objectCaching import CacheOK
                raise CacheOK()
            elif cachedResultRecord:
                if machoVersion:
                    raise CachedResult(cachedResultRecord['rret'])
                else:
                    raise CachedResult(cachedResultRecord['lret'])
        return (cacheInfo, machoVersion)

    def PostCall_CachedMethodCall(self, cookies, result, method, args, keywords, **mykeywords):
        cookie = cookies.get('PreCall_CachedMethodCall', None)
        if cookie is not None:
            if not isinstance(result, Exception):
                cacheInfo, machoVersion = cookie
                if cacheInfo[0]:
                    srv = sm.StartService('objectCaching')
                    from carbon.common.script.net.objectCaching import CachedMethodCallResult, CacheOK
                    cachable, versionCheck, throwOK, cachedResultRecord, cacheKey, cacheDetails = cacheInfo
                    cmcr = CachedMethodCallResult(cacheKey, cacheDetails, result)
                    srv.CacheMethodCall(self.__logname__, self.__method_without_Ex__, args, cmcr)
                    if machoVersion is not None:
                        if machoVersion != 1 and cmcr.GetVersion()[1] == machoVersion[1]:
                            srv.LogInfo('ObjectCaching ', self.__logname__, '::', self.__method_without_Ex__, '(', args, ') is the correct version.  raising CacheOK')
                            raise CacheOK()
                        else:
                            srv.LogInfo('ObjectCaching ', self.__logname__, '::', self.__method_without_Ex__, '(', args, ') is not the correct version.  returning a cachable result.  caller=', machoVersion, ', server=', cmcr.GetVersion())
                        raise CachedResult(cmcr)
                    else:
                        errorDesc = "ObjectCaching %s::%s (%s) - the client didn't provide a macho version, not even the default value.  Probably an unbound call to a cached method call, which is NOT supported." % (self.__logname__, self.__method_without_Ex__, args)
                        log.LogTraceback(errorDesc)


class ServiceCallWrapper(CallWrapper):
    if boot.role == 'client':
        __precall__ = ['PreCall_WaitForRunningState',
         'PreCall_IsExportedCall',
         'PreCall_CheckPreArgs',
         'PreCall_CachedMethodCall']
    else:
        __precall__ = ['PreCall_WaitForRunningState',
         'PreCall_IsExportedCall',
         'PreCall_RoleCheck',
         'PreCall_CheckPreArgs',
         'PreCall_CachedMethodCall',
         'PreCall_Lock']

    def PreCall_WaitForRunningState(self, method, args, keywords, **mykeywords):
        i = 0
        while self.__callable__.state != SERVICE_RUNNING:
            if self.__callable__.state == SERVICE_STOPPED:
                raise RuntimeError('ServiceStopped', self.__callable__)
            blue.pyos.synchro.SleepWallclock(100)
            if i % 600 == 0 and i > 0:
                self.__callable__.LogWarn('PreCallHandler:  ', method, args, keywords, ' has been sleeping for a long time waiting for ', self.__logname__, ' to either get to running state, or to stopped state')


class UnlockedServiceCallWrapper(ServiceCallWrapper):
    if boot.role == 'client':
        __precall__ = ['PreCall_WaitForRunningState',
         'PreCall_IsExportedCall',
         'PreCall_CheckPreArgs',
         'PreCall_CachedMethodCall']
    else:
        __precall__ = ['PreCall_WaitForRunningState',
         'PreCall_IsExportedCall',
         'PreCall_RoleCheck',
         'PreCall_CheckPreArgs',
         'PreCall_CachedMethodCall']


globalMiniTraceStats = {}

class MiniTraceCallWrapper():

    def __init__(self, service, func, funcName, depth):
        self.service = weakref.proxy(service)
        self.func = func
        self.funcName = funcName
        self.depth = depth

    def __call__(self, *args, **kw):
        if self.service.logChannel.IsOpen(1):
            stats = globalMiniTraceStats[self.service.__guid__, self.funcName]
            l = self.depth
            if l == -1:
                l = 2
            tb = traceback.extract_stack(limit=l)[:-1]
            tb = [ (i[0], i[2], i[1]) for i in tb ]
            k0 = tb[-1]
            for k in tb:
                stats[k] = stats.get(k, 0) + 1

            self.service.LogInfo(self.funcName, args, kw, ' is being called by ', k0[1], ' in line ', k0[2], ' of ', k0[0])
            return apply(self.func, args, kw)
        else:
            return apply(self.func, args, kw)


MiniTraceStats = globalMiniTraceStats

class CoreService(object):
    __startupdependencies__ = []
    __dependencies__ = []
    __required__ = ['Sessions']
    __name__ = 'service'
    __displayname__ = 'Basic Service'
    __persistvars__ = []
    __nonpersistvars__ = []
    __exportedcalls__ = {}
    __notifyevents__ = []
    __configvalues__ = {}
    __counters__ = {}
    __machocacheobjects__ = 1
    __machoresolve__ = None

    def __init__(self):
        super(CoreService, self).__init__()
        self.boundObjects = {}
        self.serviceLocks = {}
        self.startedWhen = blue.os.GetWallclockTimeNow()
        self.__servicename__ = getattr(self, '__replaceservice__', self.__guid__.split('.')[1])
        self.__logname__ = self.__servicename__
        self.logChannel = log.GetChannel(self.__guid__)
        self.InitService()
        if len(self.__counters__) and 'counter' not in self.__startupdependencies__:
            self.__startupdependencies__.append('counter')
        self.isLogInfo = bool(prefs.GetValue('logInfo', 1))
        self.isLogNotice = bool(prefs.GetValue('logNotice', 1))
        self.isLogWarning = bool(prefs.GetValue('logWarning', 1))
        self.logContexts = {}
        for each in ('Info', 'Warn', 'Error', 'Perf'):
            self.logContexts[each] = 'Logging::' + each

    def SetLogInfo(self, b):
        if not b and self.isLogInfo:
            self.LogInfo('*** LogInfo stopped for ', self.__guid__)
        old = self.isLogInfo
        self.isLogInfo = b
        if b and not old:
            self.LogInfo('*** LogInfo started for ', self.__guid__)

    def SetLogNotice(self, b):
        if not b and self.isLogNotice:
            self.LogNotice('*** LogNotice stopped for ', self.__guid__)
        old = self.isLogNotice
        self.isLogNotice = b
        if b and not old:
            self.LogNotice('*** LogNotice started for ', self.__guid__)

    def SetLogWarning(self, b):
        if not b and self.isLogWarning:
            self.LogWarn('*** LogWarn stopped for ', self.__guid__)
        old = self.isLogWarning
        self.isLogWarning = b
        if b and not old:
            self.LogWarn('*** LogWarn started for ', self.__guid__)

    def MachoResolve(self, sess):
        if self.__machoresolve__ is not None:
            return self._MachoResolveAdditional(sess)

    def _MachoResolveAdditional(self, sess):
        if self.__machoresolve__ is None:
            return
        if sess.role & ROLE_SERVICE:
            return
        macho = sm.GetService('machoNet')
        if self.__machoresolve__ == 'station':
            if not sess.stationid:
                return 'You must be located at a station to use this service'
            return macho.GetNodeFromAddress(SERVICE_STATION, sess.stationid)
        if self.__machoresolve__ == 'solarsystem':
            if not sess.solarsystemid:
                return 'You must be located in a solar system to use this service'
            return macho.GetNodeFromAddress(SERVICE_BEYONCE, sess.solarsystemid)
        if self.__machoresolve__ == 'solarsystem2':
            if not sess.solarsystemid2:
                return 'Your location must belong to a known solarsystem'
            return macho.GetNodeFromAddress(SERVICE_BEYONCE, sess.solarsystemid2)
        if self.__machoresolve__ in ('location', 'locationPreferred'):
            if not sess.locationid:
                if self.__machoresolve__ == 'locationPreferred':
                    return
                return 'You must be located in a solar system or at station to use this service'
            if sess.solarsystemid:
                return macho.GetNodeFromAddress(SERVICE_BEYONCE, sess.solarsystemid)
            if sess.stationid:
                return macho.GetNodeFromAddress(SERVICE_STATION, sess.stationid)
            raise RuntimeError('machoresolving a location bound service with without a location session')
        if self.__machoresolve__ in ('character',):
            if sess.charid is None:
                return
            else:
                return macho.GetNodeFromAddress(SERVICE_CHARACTER, sess.charid % CHARNODE_MOD)
        if self.__machoresolve__ in ('corporation',):
            if sess.corpid is None:
                return 'You must have a corpid in your session to use this service'
            else:
                return macho.GetNodeFromAddress(SERVICE_CHATX, sess.corpid % 200)
        if self.__machoresolve__.startswith('clustersingleton'):
            return GetClusterSingletonNodeFromAddress(macho, self.__machoresolve__)
        if self.__machoresolve__ == 'user':
            if sess.userid is None:
                return 'You must have a userid in your session to use this service'
            return macho.GetNodeFromAddress(SERVICE_USER, sess.userid % const.USERNODE_MOD)
        raise RuntimeError('__machoresolve__ = %s on service %s is bogus.' % (self.__machoresolve__, self.__logname__))

    def __GetCachedObject(self, key):
        return self.boundObjects.get(key, None)

    def __SetCachedObject(self, key, object):
        if self.__machocacheobjects__:
            self.boundObjects[key] = object

    def __DelCachedObject(self, key):
        try:
            del self.boundObjects[key]
        except KeyError:
            pass

    def MachoGetObjectBoundToSession(self, bindParams, callerSession):
        with self.LockedService(bindParams):
            obj = self.__GetCachedObject(bindParams)
            if obj is None:
                obj = self.MachoBindObject(bindParams)
                if not hasattr(obj, 'sessionConnections'):
                    obj.objectConnections = {}
                    obj.sessionConnections = weakref.WeakValueDictionary({})
                    obj.machoInstanceID = blue.os.GetWallclockTimeNow()
                    obj.boundBy = bindParams
                self.__SetCachedObject(bindParams, obj)
        return ClockThisWithoutTheStars('CoreService::ConnectToObject', callerSession.ConnectToObject, (obj, self.__servicename__, bindParams))

    def RemoveSessionConnectionFromObject(self, connection):
        boundObject = connection.__object__
        sessionID = connection.__session__.sid
        connectionID = connection.__c2ooid__
        try:
            del boundObject.objectConnections[sessionID][connectionID]
        except KeyError:
            pass
        except StandardError:
            log.LogException()

        try:
            if not boundObject.objectConnections[sessionID]:
                try:
                    connection.PseudoMethodCall(boundObject, 'OnSessionDetach')
                except StandardError:
                    log.LogException()

                try:
                    del boundObject.sessionConnections[sessionID]
                except KeyError:
                    self.LogError('Hmmm, session', sessionID, 'missing from', boundObject.sessionConnections.keys(), 'disconnected?', connection.__disconnected__)

        except KeyError:
            self.LogError('Woot? Session', sessionID, "isn't in", boundObject.objectConnections.keys())

        try:
            del connection.__session__.connectedObjects[connectionID]
        except KeyError:
            log.LogException()

        with self.LockedService(boundObject.boundBy):
            if hasattr(boundObject, 'sessionConnections'):
                if len(boundObject.sessionConnections) == 0:
                    delattr(boundObject, 'sessionConnections')
                    self.__DelCachedObject(boundObject.boundBy)
                    if len(boundObject.objectConnections):
                        boundObject.objectConnections.clear()
                    connection.PseudoMethodCall(boundObject, 'OnStop')
                    if hasattr(boundObject, 'service'):
                        delattr(boundObject, 'service')
                    if hasattr(boundObject, 'session'):
                        delattr(boundObject, 'session')
                    for dependency in getattr(boundObject, 'dependencies', []):
                        delattr(boundObject, dependency)

    def LockService(self, lockID):
        try:
            lock = self.serviceLocks[lockID]
        except KeyError:
            lock = locks.RLock(('service::serviceLock', self.__logname__, lockID))
            self.serviceLocks[lockID] = lock

        lock.acquire()
        return lock

    def ServiceLockCheck(self, lockID):
        if lockID not in self.serviceLocks or self.serviceLocks[lockID].IsCool():
            return 0
        else:
            return max(1, (blue.os.GetWallclockTime() - self.serviceLocks[lockID].lockedWhen) / const.SEC)

    def UnLockService(self, lockID, lock):
        lock.release()
        if lock.IsCool():
            del self.serviceLocks[lockID]

    class LockedServiceCtxt(object):

        def __init__(self, svc, lockKey):
            self.svc = svc
            self.lockKey = lockKey

        def __enter__(self):
            self.lock = self.svc.LockService(self.lockKey)

        def __exit__(self, e, v, tb):
            self.svc.UnLockService(self.lockKey, self.lock)

    def LockedService(self, lockKey):
        return self.LockedServiceCtxt(self, lockKey)

    def StartMiniTrace(self, funcName, depth = 16):
        if funcName not in globalMiniTraceStats:
            globalMiniTraceStats[self.__guid__, funcName] = {}
            setattr(self, funcName, MiniTraceCallWrapper(self, getattr(self, funcName), funcName, depth))

    def StopMiniTrace(self, funcName, depth = 16):
        if funcName not in globalMiniTraceStats:
            del globalMiniTraceStats[self.__guid__, funcName]
            setattr(self, funcName, getattr(self, funcName).func)

    def GetDependants(self):
        dependants = []
        myName = self.__servicename__
        for i in sm.services:
            if myName in sm.services[i].__dependencies__:
                dependants.append(sm.services[i].__servicename__)

        return dependants

    def GetDeepDependants(self, theArr):
        newbies = []
        for each in self.GetDependants():
            if each not in theArr:
                newbies.append(each)
                theArr.append(each)

        for each in newbies:
            sm.services[each].GetDeepDependants(theArr)

    def GetDeepDependencies(self, theArr):
        newbies = []
        for each in self.__dependencies__:
            if each not in theArr:
                newbies.append(each)
                theArr.append(each)

        for each in newbies:
            sm.services[each].GetDeepDependencies(theArr)

    def InitService(self):
        self.state = SERVICE_STOPPED

    def __getattr__(self, key):
        if key in self.__configvalues__:
            daKey = '%s.%s' % (self.__logname__, key)
            return prefs.GetValue(daKey, boot.GetValue(daKey, self.__configvalues__[key]))
        if key in self.__counters__:
            self.__dict__[key] = self.counter.CreateCounter(key, self.__counters__[key])
            return self.__dict__[key]
        if hasattr(self.__class__, key):
            return getattr(self.__class__, key)
        raise AttributeError, key

    def __setattr__(self, key, value):
        super(CoreService, self).__setattr__(key, value)
        if key in self.__configvalues__:
            value = self.OnSetConfigValue(key, value)
            prefs.SetValue('%s.%s' % (self.__logname__, key), value)
            return
        self.__dict__[key] = value

    def ControlMessage(self, control):
        if control == SERVICE_CONTROL_STOP:
            self.state = SERVICE_STOPPED
        elif control == SERVICE_CONTROL_PAUSE:
            self.state = SERVICE_PAUSED
        elif control == SERVICE_CONTROL_CONTINUE:
            self.state = SERVICE_RUNNING
        elif control == SERVICE_CONTROL_INTERROGATE:
            pass
        elif control == SERVICE_CONTROL_SHUTDOWN:
            self.state = SERVICE_STOPPED

    def DudLogger(self, *args, **keywords):
        pass

    def LogMethodCall(self, *args, **keywords):
        logChannel = log.methodcalls
        if logChannel.IsOpen(log.LGINFO):
            try:
                s = ' '.join(map(supersafestr, args))
                logChannel.Log(s, log.LGINFO, 1)
            except TypeError:
                logChannel.Log('[X]'.join(map(supersafestr, args)).replace('\x00', '\\0'), log.LGINFO, 1)
                sys.exc_clear()
            except UnicodeEncodeError:
                logChannel.Log('[U]'.join(map(lambda x: x.encode('ascii', 'replace'), map(unicode, args))), log.LGINFO, 1)
                sys.exc_clear()

        else:
            self.LogMethodCall = self.DudLogger

    def LogInfo(self, *args, **keywords):
        if getattr(self, 'isLogInfo', 0) and self.logChannel.IsLogChannelOpen(1):
            try:
                s = ' '.join(map(supersafestr, args))
                self.logChannel.Log(s, 1, 1, force=True)
            except TypeError:
                self.logChannel.Log('[X]'.join(map(supersafestr, args)).replace('\x00', '\\0'), 1, 1, force=True)
                sys.exc_clear()
            except UnicodeEncodeError:
                self.logChannel.Log('[U]'.join(map(lambda x: x.encode('ascii', 'replace'), map(unicode, args))), 1, 1, force=True)
                sys.exc_clear()

    def LogWarn(self, *args, **keywords):
        if self.isLogWarning and self.logChannel.IsLogChannelOpen(2) or charsession and not boot.role == 'client':
            try:
                s = ' '.join(map(supersafestr, args))
                if self.logChannel.IsOpen(2):
                    self.logChannel.Log(s, 2, 1, force=True)
                for x in LineWrap(s, 10):
                    if charsession and not boot.role == 'client':
                        charsession.LogSessionHistory(x, None, 1)

            except TypeError:
                sys.exc_clear()
                x = '[X]'.join(map(supersafestr, args)).replace('\x00', '\\0')
                if self.logChannel.IsOpen(2):
                    self.logChannel.Log(x, 2, 1, force=True)
                if charsession and not boot.role == 'client':
                    charsession.LogSessionHistory(x, None, 1)
            except UnicodeEncodeError:
                sys.exc_clear()
                x = '[U]'.join(map(lambda x: x.encode('ascii', 'replace'), map(unicode, args)))
                if self.logChannel.IsOpen(2):
                    self.logChannel.Log(x, 2, 1, force=True)
                if charsession and not boot.role == 'client':
                    charsession.LogSessionHistory(x, None, 1)

    def LogError(self, *args, **keywords):
        if self.logChannel.IsOpen(4) or charsession:
            try:
                s = ' '.join(map(supersafestr, args))
                if self.logChannel.IsOpen(4):
                    self.logChannel.Log(s, 4, 1)
                for x in LineWrap(s, 40):
                    if charsession:
                        charsession.LogSessionHistory(x, None, 1)

            except TypeError:
                sys.exc_clear()
                x = '[X]'.join(map(supersafestr, args)).replace('\x00', '\\0')
                if self.logChannel.IsOpen(4):
                    self.logChannel.Log(x, 4, 1)
                if charsession:
                    charsession.LogSessionHistory(x, None, 1)
            except UnicodeEncodeError:
                sys.exc_clear()
                x = '[U]'.join(map(lambda x: x.encode('ascii', 'replace'), map(unicode, args)))
                if self.logChannel.IsOpen(4):
                    self.logChannel.Log(x, 4, 1)
                if charsession and not boot.role == 'client':
                    charsession.LogSessionHistory(x, None, 1)

    def LogNotice(self, *args, **_unused_keywords):
        if getattr(self, 'isLogNotice', 0) and self.logChannel.IsLogChannelOpen(log.LGNOTICE):
            try:
                s = ' '.join(map(supersafestr, args))
                self.logChannel.Log(s, log.LGNOTICE, 1, force=True)
            except TypeError:
                s = '[X]'.join(map(supersafestr, args)).replace('\x00', '\\0')
                self.logChannel.Log(s, log.LGNOTICE, 1, force=True)
                sys.exc_clear()
            except UnicodeEncodeError:
                s = '[U]'.join(map(lambda x: x.encode('ascii', 'replace'), map(unicode, args)))
                self.logChannel.Log(s, log.LGNOTICE, 1, force=True)
                sys.exc_clear()

    def LogException(self, extraText = ''):
        log.LogException(extraText, channel=self.__guid__)
        sys.exc_clear()

    def LogTraceback(self, extraText = ''):
        log.LogTraceback(extraText, show_locals=2, channel=self.__guid__)

    def Run(self, memStream = None):
        self.LogInfo('Service: %s starting' % (self.__guid__,))
        self.boundObjects = {}

    def Entering(self):
        pass

    def Stop(self, memStream = None):
        for bo in self.boundObjects.values():
            for sess in bo.sessionConnections.values():
                sess.DisconnectObject(bo)

        self.boundObjects = {}

    def IsRunning(self):
        return getattr(self, 'state', SERVICE_STOPPED) == SERVICE_RUNNING

    def GetSessionState(self, session_ = None):
        if session_ is not None:
            session = session_
        if session is None:
            raise RuntimeError('No session')
        return session.GetBag(self.__guid__)

    def GetServiceState(self):
        states = {SERVICE_STOPPED: 'Stopped',
         SERVICE_START_PENDING: 'Start Pending',
         SERVICE_STOP_PENDING: 'Stop Pending',
         SERVICE_RUNNING: 'Running',
         SERVICE_CONTINUE_PENDING: 'Continue Pending',
         SERVICE_PAUSE_PENDING: 'Pause Pending',
         SERVICE_PAUSED: 'Paused',
         SERVICE_FAILED: 'Failed to start'}
        return states.get(self.state, 'unknown')

    def GetHtmlState(self, writer, session = None, request = None):
        from carbon.common.script.util import htmlwriter
        wr = htmlwriter.HtmlWriter()
        if writer is None:
            return '(no info available)'
        writer.Write(self.HTMLDumpProperties('Basic Service properties', 'wpServiceProperties', self, session, request))
        if len(self.__configvalues__):
            hd = ['Key',
             'Pretty Name',
             'Value',
             'Default Value',
             'Info']
            li = []
            for each in self.__configvalues__.iterkeys():
                prettyname = each
                info = None
                value = getattr(self, each)
                if hasattr(self, 'GetHtmlStateDetails'):
                    r = self.GetHtmlStateDetails(each, value, 0)
                    if r:
                        prettyname, info = r[0], r[1]
                if value != self.__configvalues__[each]:
                    value = '<b>%s</b>' % value
                li.append([each,
                 prettyname,
                 value,
                 self.__configvalues__[each],
                 info])

            li.sort(lambda a, b: -(a[0].upper() < b[0].upper()))
            edit = '<a href="/admin/services.py?action=EditConfigValues&svcname=%s">Click to edit</a>' % (self.__servicename__,)
            writer.Write(htmlwriter.WebPart('Service Config Values - ' + edit, wr.GetTable(hd, li, useFilter=True), 'wpServiceConfigValues'))
        if len(self.__counters__):
            hd = ['Key',
             'Pretty Name',
             'Type',
             'Current Value',
             'Description']
            li = []
            for each in self.__counters__.iterkeys():
                cname = each
                prettyname = cname
                ctype = self.__counters__[each]
                cvalue = 0
                if hasattr(self, each):
                    cvalue = getattr(self, each).Value()
                info = ''
                if hasattr(self, 'GetHtmlStateDetails'):
                    r = self.GetHtmlStateDetails(each, cvalue, 0)
                    if r:
                        prettyname, info = r[0], r[1]
                li.append([cname,
                 prettyname,
                 ctype,
                 cvalue,
                 info])

            li.sort(lambda a, b: -(a[0].upper() < b[0].upper()))
            reset = '<a href="/admin/services.py?action=ResetCounters&svcname=%s" onClick="return confirm(\'Are you sure?\')">Click to reset</a>' % (self.__servicename__,)
            writer.Write(htmlwriter.WebPart('Service Counters - ' + reset, wr.GetTable(hd, li, useFilter=True), 'wpServiceCounters'))
        det = '<a href="/admin/services.py?svcname=%s&propertyDetail=yes">Click to view details</a><br>' % self.__servicename__
        writer.Write(htmlwriter.WebPart('Service Member Variables - %s' % det, self.HTMLDumpGenericMembers(self, session, request), 'wpServiceMemberVariables'))
        if hasattr(self, 'boundObjects'):
            if request:
                objectDetail = request.QueryString('objectDetail')
                if objectDetail is not None:
                    objectDetail = cPickle.loads(binascii.a2b_hex(objectDetail))
            else:
                objectDetail = None
            object = self.boundObjects.get(objectDetail, None)
            if object:
                writer.WriteH2('Bound Object %s' % unicode(objectDetail))
                if object.__doc__ is not None:
                    writer.Write(htmlwriter.Swing(object.__doc__).replace('\n', '<br>'))
                writer.Write(self.HTMLDumpProperties('Properties of Bound Object %s' % unicode(objectDetail), 'wpBoundObjectProperties %s' % unicode(objectDetail), object, session, request))
                writer.Write(self.HTMLDumpGenericMembers(object, session, request))
        self.HTMLWriteServiceMethods(writer, session, request)
        self.HTMLWriteExtraState(writer, session, request)

    def HTMLWriteExtraState(self, writer, session, request):
        pass

    def HTMLWriteServiceMethods(self, writer, session, request):
        from carbon.common.script.util import htmlwriter
        hd = ['Method', 'Roles']
        li = []
        for method in self.__exportedcalls__:
            details = self.__exportedcalls__[method]
            if type(details) == types.DictType:
                role = details.get('role', 0)
            elif len(details) > 0:
                role = details[0]
            else:
                role = 0
            from carbon.common.script.sys import serviceConst
            if role == serviceConst.ROLE_ANY:
                rolestr = 'ANY'
            else:
                rolestr = ''
                for each in dir(serviceConst):
                    if each.startswith('ROLE_') and getattr(serviceConst, each) & role != 0:
                        rolestr += each[5:] + ', '

                rolestr = rolestr[:-2]
            li.append([writer.Link('', method, {'action': 'WebExec',
              'service': self.__guid__.split('.')[1],
              'method': method}), rolestr])

        li.sort()
        wr = htmlwriter.HtmlWriter()
        writer.Write(htmlwriter.WebPart('Service Methods', wr.GetTable(hd, li, useFilter=True), 'wpServiceMethods'))
        svcname = self.__servicename__
        txt = '<table>'
        txt += '\n            <tr><td>Info Logging:</td><td> %s</td><td>\n            &nbsp;|&nbsp;&nbsp;<a href="?action=ToggleInfoLog&svcname=%s&which=%s">Toggle</a>\n            &nbsp;&middot;&nbsp;&nbsp;<a href="?action=ToggleInfoLog&svcname=%s&allnodes=1&which=1" OnClick="return confirm(\'Are you sure?\');">Start on All Nodes</a>\n            &nbsp;&middot;&nbsp;&nbsp;<a href="?action=ToggleInfoLog&svcname=%s&allnodes=1&which=0">Stop on All Nodes</a></tr>\n            ' % (['OFF', '<font color=red><b>ON</b></font>'][self.isLogInfo],
         svcname,
         int(not self.isLogInfo),
         svcname,
         svcname)
        txt += '\n            <tr><td>Notice Logging:</td><td> %s</td><td>\n            &nbsp;|&nbsp;&nbsp;<a href="?action=ToggleNoticeLog&svcname=%s&which=%s">Toggle</a>\n            &nbsp;&middot;&nbsp;&nbsp;<a href="?action=ToggleNoticeLog&svcname=%s&allnodes=1&which=1" OnClick="return confirm(\'Are you sure?\');">Start on All Nodes</a>\n            &nbsp;&middot;&nbsp;&nbsp;<a href="?action=ToggleNoticeLog&svcname=%s&allnodes=1&which=0">Stop on All Nodes</a></tr>\n            ' % (['OFF', '<font color=red><b>ON</b></font>'][self.isLogNotice],
         svcname,
         int(not self.isLogNotice),
         svcname,
         svcname)
        txt += '\n            <tr><td>Warning Logging:</td><td> %s</td><td>\n            &nbsp;|&nbsp;&nbsp;<a href="?action=ToggleWarningLog&svcname=%s&which=%s">Toggle</a>\n            &nbsp;&middot;&nbsp;&nbsp;<a href="?action=ToggleWarningLog&svcname=%s&allnodes=1&which=1">Start on All Nodes</a>\n            &nbsp;&middot;&nbsp;&nbsp;<a href="?action=ToggleWarningLog&svcname=%s&allnodes=1&which=0">Stop on All Nodes</a></tr>\n            ' % (['OFF', '<b>ON</b>'][self.isLogWarning],
         svcname,
         int(not self.isLogWarning),
         svcname,
         svcname)
        txt += '</table>'
        writer.Write(htmlwriter.WebPart('Logging', '<div style="padding:5px;">%s</div>' % txt, 'wpServiceLogging'))

    def HTMLDumpGenericMembers(self, dumpWho, session, request):
        from carbon.common.script.util import htmlwriter
        wr = htmlwriter.HtmlWriter()
        if request:
            detail = request.QueryString('detail')
        else:
            detail = None
        if request:
            propertyDetails = request.QueryString('propertyDetail') == 'yes'
            from carbon.common.script.util.profiling import CalcMemoryUsage
        else:
            propertyDetails = False

        def Str(v):
            from carbon.common.script.util import htmlwriter
            try:
                return htmlwriter.Swing(unicode(v))
            except:
                sys.exc_clear()
                return '(?)'

        li = []
        theItems = dumpWho.__dict__.keys()
        theItems.sort(lambda a, b: -(a.upper() < b.upper()))
        something = 0
        for k in theItems:
            v = dumpWho.__dict__[k]
            if hasattr(dumpWho, '__dependencies__') and k in dumpWho.__dependencies__:
                continue
            if hasattr(dumpWho, '__configvalues__') and k in dumpWho.__configvalues__:
                continue
            if hasattr(dumpWho, '__exportedcalls__') and k in dumpWho.__exportedcalls__:
                continue
            if hasattr(dumpWho, '__counters__') and k in dumpWho.__counters__:
                continue
            if k in ('state', 'startedWhen', 'serviceLocks', 'logChannel', 'session', 'boundObjects', '__servicelock__', 'objectConnections', 'sessionConnections', '__sessionfilter__', '__logname__', 'logContexts'):
                continue
            if k.startswith('_' + dumpWho.__class__.__name__ + '__'):
                k = k[len('_' + dumpWho.__class__.__name__):]
            r = None
            ok = k
            if hasattr(dumpWho, 'GetHtmlStateDetails'):
                r = dumpWho.GetHtmlStateDetails(k, v, k == detail)
            if r:
                if propertyDetails and type(r[1]) in types.StringTypes:
                    xtra = ' [type: %s]' % type(v).__name__
                    length = None
                    try:
                        length = len(v)
                        xtra += ' [length: %d]' % len(v)
                    except:
                        pass

                    try:
                        xtra += ' [memusage: %d]' % CalcMemoryUsage(v)[2]
                    except:
                        pass

                    k, v = r[0], r[1]
                else:
                    k, v = r[0], r[1]
            elif k != detail:
                if type(v) in (types.ListType,
                 types.TupleType,
                 types.DictType,
                 types.InstanceType) or isinstance(v, dict):
                    xtra = ''
                    if propertyDetails and (type(v) in (types.ListType, types.TupleType, types.DictType) or isinstance(v, dict)):
                        xtra = ' - length: %d' % len(v)
                        try:
                            xtra += ' [memusage: %d kB]' % int(int(CalcMemoryUsage(v)[2]) / 1024)
                        except Exception as e:
                            xtra += ' [memusage: ??] %s' % e

                    v = '&lt;click details to view&gt; [type: %s]%s' % (type(v).__name__, xtra)
                else:
                    v = Str(v)
            else:
                var = getattr(dumpWho, detail, None)
                if type(var) in [types.ListType, types.TupleType]:
                    lines = []
                    for i in var:
                        lines.append([Str(i)])

                    v = htmlwriter.GetTable([], lines)
                elif isinstance(v, dict):
                    lines = []
                    for key, val in var.iteritems():
                        lines.append([Str(key), Str(val)])

                    v = htmlwriter.GetTable([], lines)
                else:
                    v = Str(v)
                    v = '<pre>%s</pre>' % v
            k = htmlwriter.Link('', k, [request.query, {'detail': ok}])
            li.append([k, v])
            something = 1

        if not something:
            return 'This service does not have any custom member variables'
        return wr.GetTable([], li)

    def HTMLDumpProperties(self, title, page, dumpWho, session, request):
        from carbon.common.script.util import htmlwriter

        def Str(v):
            from carbon.common.script.util import htmlwriter
            try:
                return htmlwriter.Swing(unicode(v))
            except:
                sys.exc_clear()
                return '(?)'

        hd = ['Property', 'Value']
        deepdependencies = []
        if hasattr(dumpWho, 'GetDeepDependencies'):
            dumpWho.GetDeepDependencies(deepdependencies)
        deepdependants = []
        if hasattr(dumpWho, 'GetDeepDependendants'):
            dumpWho.GetDeepDependants(deepdependants)
        dependencies = []
        if hasattr(dumpWho, '__dependencies__'):
            dependencies = dumpWho.__dependencies__
        dependants = []
        if hasattr(dumpWho, 'GetDependants'):
            dependants = dumpWho.GetDependants()
        persistvars = []
        if hasattr(dumpWho, '__persistvars__'):
            persistvars = dumpWho.__persistvars__
        nonpersistvars = []
        if hasattr(dumpWho, '__nonpersistvars__'):
            nonpersistvars = dumpWho.__nonpersistvars__
        notifyevents = []
        if hasattr(dumpWho, '__notifyevents__'):
            notifyevents = list(dumpWho.__notifyevents__)
        exportedcalls = []
        if hasattr(dumpWho, '__exportedcalls__'):
            exportedcalls = dumpWho.__exportedcalls__.keys()
        objectConnections = []
        for connectionByC2OOID in getattr(dumpWho, 'objectConnections', {}).itervalues():
            for connection in connectionByC2OOID.itervalues():
                objectConnections.append(Str(connection))

        sessionConnections = []
        for each in getattr(dumpWho, 'sessionConnections', {}).itervalues():
            sessionConnections.append(Str(each))

        boundObjects = []
        if hasattr(dumpWho, 'boundObjects'):
            boundObjects = dumpWho.boundObjects.keys()
        sessionfilter = []
        if hasattr(dumpWho, '__sessionfilter__'):
            sessionfilter = dumpWho.__sessionfilter__

        def Alphabetize(arr, objectDetail = False, dependency = False):
            try:
                li = arr[:]
                li.sort(lambda a, b: -(Str(a).upper() < Str(b).upper()))
                if objectDetail:
                    li = [ htmlwriter.Link('', unicode(val), [request.query, {'objectDetail': binascii.b2a_hex(cPickle.dumps(val, 1))}]) for val in li ]
                elif dependency:
                    li = [ htmlwriter.Link('', unicode(val), [request.query, {'svcname': unicode(val)}]) for val in li ]
                else:
                    li = [ unicode(val) for val in li ]
                if len(li) > 100:
                    return '&lt; %d entries &gt;' % len(li)
                return ', '.join(li)
            except:
                log.LogException()
                sys.exc_clear()
                return ', '.join(arr)

        li = [['Objects bound to me', Alphabetize(boundObjects, objectDetail=True)],
         ['Sessions using me', Alphabetize(sessionConnections)],
         ['Objects using me', Alphabetize(objectConnections)],
         ['Session Filter', Alphabetize(sessionfilter)],
         ['I depend on', Alphabetize(dependencies, dependency=True)],
         ['<nobr>I depend on - recursively</nobr>', Alphabetize(deepdependencies, dependency=True)],
         ['Who depends on me', Alphabetize(dependants, dependency=True)],
         ['Who depends on me - recursively', Alphabetize(deepdependants, dependency=True)],
         ['Persistant Variables', Alphabetize(persistvars)],
         ['Non-persistant Variables', Alphabetize(nonpersistvars)],
         ['I listen to these events', Alphabetize(notifyevents)],
         ['I export these calls', Alphabetize(exportedcalls)]]
        if hasattr(dumpWho, 'GetServiceState'):
            li.append(['Service State', dumpWho.GetServiceState()])
        if hasattr(dumpWho, 'session'):
            li.append(['Service Session', htmlwriter.Swing(repr(dumpWho.session))])
        if hasattr(dumpWho, '__servicelock__'):
            li.append(['Service Lock', htmlwriter.Swing(unicode(getattr(dumpWho, '__servicelock__', None)))])
        li.sort(lambda a, b: -(a[0].upper() < b[0].upper()))
        li = [ each for each in li if each[1] ]
        wr = htmlwriter.HtmlWriter()
        return htmlwriter.WebPart(title, wr.GetTable(hd, li, useFilter=True), page)

    def OnSetConfigValue(self, key, value):
        return value

    def GetSPConfigValues(self):
        r = []
        for a in sorted(self.__configvalues__.keys()):
            v = getattr(self, a)
            t = type(getattr(self, a))
            r.append((a, v, t))

        return r

    def SetSPConfigValues(self, values):
        for a in self.__configvalues__.keys():
            if a in values:
                setattr(self, a, values[a])


def GetClusterSingletonNodeFromAddress(mn, machoresolve):
    try:
        num = int(machoresolve.split('_')[1])
    except:
        log.general.Log('clustersingleton machoresolve without mod number. Using 0')
        num = 0

    numMod = num % const.CLUSTERSINGLETON_MOD
    if num >= const.CLUSTERSINGLETON_MOD:
        log.general.Log('clustersingleton machoresolve with out-of-bounds mod number', num, 'rolling over to', numMod, log.LGWARN)
    return mn.GetNodeFromAddress(SERVICE_CLUSTERSINGLETON, numMod)


class AppProxyService(CoreService):
    __solservice__ = None

    def __init__(self):
        self.solNodeID = None
        CoreService.__init__(self)

    def GetSolNodeService(self):
        if not getattr(self, '__solservice__'):
            self.LogError('Application Proxy Service incorrectly configured. The service requires the __solservice__ attribute which is a tuple of (solServiceName, serviceMask, serviceBucket)')
            return
        solServiceName, serviceMask, bucket = self.__solservice__
        if self.solNodeID is not None:
            if self.solNodeID not in sm.services['machoNet'].transportIDbySolNodeID:
                self.LogWarn('Sol node', self.solNodeID, ' is no longer available. Finding a new one...')
                self.solNodeID = None
        if self.solNodeID is None:
            svc = self.session.ConnectToSolServerService('machoNet', None)
            nodeID = svc.GetNodeFromAddress(serviceMask, bucket)
            if nodeID is None or nodeID <= 0:
                raise RuntimeError('Could not find any sol nodes with mask %s' % serviceMask)
            self.LogInfo('Found a new sol node at', nodeID)
            self.solNodeID = nodeID
        svc = self.session.ConnectToSolServerService(solServiceName, nodeID=self.solNodeID)
        return svc


class ClusterSingletonService(CoreService):
    __ready__ = 0
    __startupdependencies__ = ['machoNet']

    def __init__(self):
        for dep in ClusterSingletonService.__startupdependencies__:
            if dep not in self.__startupdependencies__:
                self.__startupdependencies__.append(dep)

        CoreService.__init__(self)

    def Run(self, *args):
        CoreService.Run(self, *args)
        sm.RegisterForNotifyEvent(self, 'OnClusterStartup')
        sm.RegisterForNotifyEvent(self, 'OnNodeDeath')
        if self.machoNet.IsClusterStarted():
            uthread.new(self.__ConditionallyPrime)

    def PrimeService(self):
        raise NotImplementedError('You cannot inherit from ClusterSingletonService without implementing PrimeService()')

    def _MachoResolveClusterSingleton(self):
        if getattr(self, '__machoresolve__', None):
            serviceNodeID = GetClusterSingletonNodeFromAddress(self.machoNet, self.__machoresolve__)
        else:
            serviceNodeID = self.MachoResolve(session)
        return serviceNodeID

    def _ShouldPrimeService(self):
        if self.__ready__:
            return False
        serviceNodeID = self._MachoResolveClusterSingleton()
        myNodeID = self.machoNet.GetNodeID()
        if serviceNodeID and myNodeID != serviceNodeID:
            return False
        return True

    def _PrimeService(self):
        with locks.TempLock((self, 'PrimeService')):
            if not self.__ready__:
                try:
                    self.LogInfo('Priming clustersingleton service...')
                    startTime = blue.os.GetWallclockTimeNow()
                    self.PrimeService()
                    self.LogNotice('Done priming clustersingleton service %s in %.3f seconds.' % (self.__logname__, (blue.os.GetWallclockTimeNow() - startTime) / float(const.SEC)))
                except Exception as e:
                    log.LogException('Error priming Cluster Singleton service %s' % self.__logname__)
                finally:
                    self.__ready__ = 1

    def PreCallAction(self, methodName):
        if not self._ShouldPrimeService():
            return
        self._PrimeService()

    def OnClusterStartup(self):
        self.__ConditionallyPrime()

    def __ConditionallyPrime(self):
        sm.WaitForServiceObjectState(self, (SERVICE_RUNNING,))
        if not self._ShouldPrimeService():
            return
        self.LogNotice('I am the right node for this cluster singleton service at startup. Priming the service...')
        self._PrimeService()

    def OnNodeDeath(self, nodeID, confirmed, reason = None):
        if not self._ShouldPrimeService():
            return
        self.LogWarn('Old Cluster Singleton node %s for this service has died. I will now service calls. Starting by priming Service' % nodeID)
        self._PrimeService()


Service = CoreService
