#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\sys\basesession.py
import copy
import random
import sys
import types
import weakref
from collections import deque, defaultdict
import blue
import bluepy
import carbon.common.script.net.machobase as machobase
import carbon.common.script.util.format as formatUtil
import localstorage
import log
import uthread
from carbon.common.script.sys.service import CallWrapper, FastCallWrapper, ServiceCallWrapper, UnlockedServiceCallWrapper
from carbon.common.script.sys.serviceConst import ROLE_LOGIN, ROLE_PLAYER, ROLE_REMOTESERVICE, ROLE_SERVICE, SERVICE_FAILED, SERVICE_RUNNING, SERVICE_STOPPED
from carbon.common.script.sys.serviceProxy import ServiceProxy
from carbon.common.lib import const
from eveexceptions import UserError
from eveprefs import prefs
from eveservices.roles import has_any_role, remove_role, add_role
from markers import PopMark, PushMark
from stringutil import strx
SESSIONCHANGEDELAY = 10 * const.SEC
allObjectConnections = weakref.WeakSet()
allConnectedObjects = weakref.WeakSet()
service_sessions = {}
local_sid = 0
sessionsByAttribute = {'userid': defaultdict(set),
 'userType': defaultdict(set),
 'charid': defaultdict(set),
 'objectID': defaultdict(dict)}
sessionsBySID = {}
allSessionsBySID = weakref.WeakValueDictionary({})
__contextOnlyTypes__ = []
dyingObjects = deque()

def ObjectKillah():
    n = 0
    while 1:
        maxNumObjects = prefs.GetValue('objectKillahMaxObjects', -1)
        sleepTime = prefs.GetValue('objectKilla.SleepWallclockTime', 30)
        if dyingObjects and (maxNumObjects <= 0 or n < maxNumObjects):
            delay = (dyingObjects[0][0] - blue.os.GetWallclockTime()) / const.SEC
            delay = min(delay, 30)
            if delay > 0:
                blue.pyos.synchro.SleepWallclock(1000 * delay)
            else:
                dietime, diediedie = dyingObjects.popleft()
                try:
                    with bluepy.Timer('sessions::' + diediedie.GetObjectConnectionLogClass()):
                        diediedie.DisconnectObject()
                except Exception:
                    log.LogException()
                    sys.exc_clear()

                del diediedie
                n += 1
        else:
            if maxNumObjects > 0 and n >= maxNumObjects:
                log.general.Log("ObjectKillah killed the maximum number of allowed objects for this round, %d, which means that we're lagging behind! Sleeping for %d seconds" % (maxNumObjects, sleepTime), log.LGWARN)
            elif n > 0:
                if maxNumObjects > 0:
                    log.general.Log('ObjectKillah killed %d objects for this round out of a maximum of %d. Sleeping for %d seconds' % (n, maxNumObjects, sleepTime), log.LGINFO)
                else:
                    log.general.Log('ObjectKillah killed %d objects for this round. Sleeping for %d seconds' % (n, sleepTime), log.LGINFO)
            n = 0
            blue.pyos.synchro.SleepWallclock(1000 * sleepTime)


objectKillaThread = uthread.new(ObjectKillah)
objectKillaThread.context = 'sessions::ObjectKillah'

class ObjectConnection():
    __passbyvalue__ = 0
    __restrictedcalls__ = {'PseudoMethodCall': 1,
     'LogPseudoMethodCall': 1,
     'GetObjectConnectionLogClass': 1,
     'RedirectObject': 1,
     'Objectcast': 1}

    def __init__(self, sess, object, c2ooid, serviceName = None, bindParams = None):
        if object is None:
            sess.LogSessionError('Establishing an object connection to None')
            log.LogTraceback()
        self.__dict__['__last_used__'] = blue.os.GetWallclockTime()
        self.__dict__['__constructing__'] = 1
        self.__dict__['__deleting__'] = 0
        self.__dict__['__machoObjectUUID__'] = GetObjectUUID(object)
        self.__dict__['__redirectObject__'] = None
        self.__dict__['__disconnected__'] = 1
        self.__dict__['__session__'] = weakref.proxy(sess)
        self.__dict__['__c2ooid__'] = c2ooid
        self.__dict__['__object__'] = object
        self.__dict__['__serviceName__'] = serviceName
        self.__dict__['__bindParams__'] = bindParams
        self.__dict__['__publicattributes__'] = getattr(object, '__publicattributes__')
        try:
            lock = None
            if not object.sessionConnections:
                if has_any_role(sess, ROLE_PLAYER):
                    sm.GetService(serviceName).LogInfo('Player session re-aquiring big lock.  Session:', sess)
                    lock = (sm.GetService(serviceName).LockService(bindParams), bindParams)
                object.service = weakref.proxy(sm.GetService(serviceName))
                object.session = weakref.proxy(object.service.session)
                for depServiceName in getattr(object, '__dependencies__', []):
                    if not hasattr(object.service, depServiceName):
                        dep = object.service.session.ConnectToService(depServiceName)
                        setattr(object.service, depServiceName, dep)
                    setattr(object, depServiceName, getattr(object.service, depServiceName))

                self.PseudoMethodCall(object, 'OnRun')
            if has_any_role(sess, ROLE_PLAYER) and lock is None:
                charid = sess.charid
                lock = (object.service.LockService((bindParams, charid)), (bindParams, charid))
            if sess.sid not in object.sessionConnections:
                object.sessionConnections[sess.sid] = sess
                object.objectConnections[sess.sid] = {}
                try:
                    self.PseudoMethodCall(object, 'OnSessionAttach')
                except Exception:
                    object.sessionConnections.pop(sess.sid, None)
                    object.objectConnections.pop(sess.sid, None)
                    log.LogTraceback('OnSessionAttach failed in ObjectConnection')
                    log.LogException()
                    raise

            else:
                self.PseudoMethodCall(object, 'OnSessionReattach')
            object.objectConnections[sess.sid][c2ooid] = self
            sess.connectedObjects[self.__c2ooid__] = (self,)
            self.__disconnected__ = 0
            self.__pendingDisconnect__ = 0
            allObjectConnections.add(self)
            allConnectedObjects.add(object)
        finally:
            if lock is not None:
                sm.GetService(serviceName).UnLockService(lock[1], lock[0])

        self.__dict__['__constructing__'] = 0

    def GetSession(self):
        return self.__session__

    def __del__(self):
        if not self.__deleting__:
            self.__deleting__ = 1
            if not self.__disconnected__:
                if log.methodcalls.IsOpen(2):
                    log.methodcalls.Log("Curious....   Disconnecting during __del__ wasn't entirely expected...", 2, 1)
                self.DisconnectObject(30)

    def __str__(self):
        return 'ObjectConnection to ' + strx(self.__object__)

    def __repr__(self):
        return self.__str__()

    def GetInstanceID(self):
        return self.__object__.machoInstanceID

    def PseudoMethodCall(self, object, method, *args, **keywords):
        global CallTimer
        self.__dict__['__last_used__'] = blue.os.GetWallclockTime()
        if hasattr(object, method):
            with self.__session__.Masquerade({'base.caller': weakref.ref(self)}):
                with CallTimer(machobase.GetLogName(object) + '::' + method):
                    try:
                        result = apply(getattr(object, method), args, keywords)
                    except Exception as e:
                        self.LogPseudoMethodCall(e, method)
                        raise

                    self.LogPseudoMethodCall(result, method)
            return result

    def LogPseudoMethodCall(self, result, method, *args, **keywords):
        logChannel = log.methodcalls
        if logChannel.IsOpen(log.LGINFO):
            logname = machobase.GetLogName(self.__object__)
            if isinstance(result, Exception):
                eorr = ', EXCEPTION='
            else:
                eorr = ', retval='
            if keywords:
                logwhat = [logname,
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
                logwhat = [logname,
                 '::',
                 method,
                 ' args=',
                 args,
                 eorr,
                 result]
            timer = PushMark(logname + '::LogPseudoMethodCall')
            try:
                s = ''.join(map(strx, logwhat))
                if len(s) > 2500:
                    s = s[:2500]
                while len(s) > 255:
                    logChannel.Log(s[:253], log.LGINFO, 1)
                    s = '- ' + s[253:]

                logChannel.Log(s, log.LGINFO, 1)
            except TypeError:
                logChannel.Log('[X]'.join(map(strx, logwhat)).replace('\x00', '\\0'), log.LGINFO, 1)
                sys.exc_clear()
            except UnicodeEncodeError:
                logChannel.Log('[U]'.join(map(lambda x: x.encode('ascii', 'replace'), map(unicode, logwhat))), log.LGINFO, 1)
                sys.exc_clear()
            finally:
                PopMark(timer)

    def GetObjectConnectionLogClass(self):
        return machobase.AssignLogName(self.__object__)

    def __GetObjectType(self):
        return 'ObjectConnection to ' + self.GetObjectConnectionLogClass()

    def RedirectObject(self, serviceName = None, bindParams = None):
        if serviceName is None:
            serviceName = self.__serviceName__
        if bindParams is None:
            bindParams = self.__bindParams__
        self.__redirectObject__ = (serviceName, bindParams)

    def DisconnectObject(self, delaySecs = 0):
        if delaySecs:
            if not self.__pendingDisconnect__:
                dyingObjects.append((blue.os.GetWallclockTime() + delaySecs * const.SEC, self))
                self.__pendingDisconnect__ = 1
            else:
                self.__pendingDisconnect__ += 1
                if self.__pendingDisconnect__ in (10, 100, 1000, 10000, 100000, 1000000, 10000000):
                    if not prefs.GetValue('suppressObjectKillahDupSpam', 0):
                        log.LogTraceback('Many duplicate requests (%d) to add object to objectKillah dyingObjects list - %r %r' % (self.__pendingDisconnect__, self, self.GetObjectConnectionLogClass()), severity=log.LGWARN)
            return
        if not self.__disconnected__:
            self.__disconnected__ = 1
            try:
                if not sm.IsServiceRunning(self.__serviceName__):
                    return
                service = sm.GetService(self.__serviceName__)
                lock = None
                if self.__session__.role & ROLE_PLAYER:
                    charid = getattr(self.__session__, 'charid')
                    lock = sm.GetService(self.__serviceName__).LockService((self.__bindParams__, charid))
                try:
                    objectID = GetObjectUUID(self)
                    if objectID in self.__session__.machoObjectsByID:
                        objectType = self.__GetObjectType()
                        self.__session__.LogSessionHistory('%s object %s disconnected from this session by the server' % (objectType, objectID), strx(self.__object__))
                        self.__session__.UnregisterMachoObject(objectID, None, 0)
                    service.RemoveSessionConnectionFromObject(self)
                finally:
                    if lock:
                        sm.GetService(self.__serviceName__).UnLockService((self.__bindParams__, charid), lock)

            except ReferenceError:
                pass
            except StandardError:
                log.LogException()

            self.__object__ = None

    def __getattr__(self, method):
        if method in self.__dict__:
            return self.__dict__[method]
        if not method.isupper():
            if method in self.__dict__['__publicattributes__']:
                return getattr(self.__object__, method)
            if method.startswith('__'):
                raise AttributeError(method)
        if self.__c2ooid__ not in self.__session__.connectedObjects:
            self.__session__.LogSessionHistory('Object no longer live:  c2ooid=' + strx(self.__c2ooid__) + ', serviceName=' + strx(self.__serviceName__) + ', bindParams=' + strx(self.__bindParams__) + ', uuid=' + strx(self.__machoObjectUUID__), None, 1)
            self.__session__.LogSessionError('This object connection is no longer live')
            raise RuntimeError('This object connection is no longer live')
        self.__dict__['__last_used__'] = blue.os.GetWallclockTime()
        if self.__session__.role & (ROLE_SERVICE | ROLE_REMOTESERVICE) == ROLE_SERVICE:
            if method.endswith('_Ex'):
                return FastCallWrapper(self.__session__, self.__object__, method[:-3], self)
            else:
                return FastCallWrapper(self.__session__, self.__object__, method, self)
        return CallWrapper(self.__session__, self.__object__, method, self, self.GetObjectConnectionLogClass())


def FindClientsAndHoles(attr, val, maxCount):
    ret = []
    nf = []
    attributes = attr.split('&')
    if attributes[0] not in sessionsByAttribute:
        log.LogWarn('FindClientsAndHoles by non-existent attribute ', attributes[0])
        return (0, ret, nf)
    if len(attributes) > 1:
        if len(attributes) != len(val):
            raise RuntimeError('For a complex session query, the value must be a tuple of equal length to the complex query params')
        for i in range(len(val[0])):
            f = 0
            r = []
            for sid in sessionsByAttribute[attributes[0]].get(val[0][i], set()):
                if sid in sessionsBySID:
                    sess = sessionsBySID[sid]
                    k = 1
                    for j in range(1, len(val)):
                        if attributes[j] in ('corprole', 'rolesAtAll', 'rolesAtHQ', 'rolesAtBase', 'rolesAtOther'):
                            corprole = getattr(sess, attributes[j])
                            k = 0
                            for r2 in val[j]:
                                if r2 and r2 & corprole == r2:
                                    k = 1
                                    break

                        elif getattr(sess, attributes[j]) not in val[j]:
                            k = 0
                        if not k:
                            break

                    if k:
                        f = 1
                        clientID = getattr(sessionsBySID[sid], 'clientID', None)
                        if clientID is not None:
                            if maxCount is not None and len(ret) >= maxCount:
                                return (1, [], [])
                            ret.append(clientID)
                else:
                    r.append(sid)

            for each in r:
                try:
                    sessionsByAttribute[attributes[0]][val[0][i]].discard(each)
                except AttributeError:
                    sessionsByAttribute[attributes[0]][val[0][i]].pop(each, None)

            if not f:
                nf.append(val[0][i])

        if len(nf):
            nf2 = list(copy.copy(val))
            nf2[0] = nf
            nf = nf2
        return (0, ret, nf)
    for v in val:
        f = 0
        r = []
        for sid in sessionsByAttribute[attr].get(v, set()):
            if sid in sessionsBySID:
                clientID = getattr(sessionsBySID[sid], 'clientID', None)
                if clientID is not None:
                    if maxCount is not None and len(ret) >= maxCount:
                        return (1, [], [])
                    ret.append(clientID)
                    f = 1
            else:
                r.append(sid)

        if r:
            sessionsWithAttribute = sessionsByAttribute[attr][v]
            for each in r:
                if isinstance(sessionsWithAttribute, dict):
                    sessionsWithAttribute.pop(each, None)
                else:
                    sessionsWithAttribute.discard(each)

        if not f:
            nf.append(v)

    return (0, ret, nf)


def FindSessions(attr, val):
    ret = []
    for v in val:
        try:
            r = []
            for sid in sessionsByAttribute[attr].get(v, set()):
                if sid in sessionsBySID:
                    ret.append(sessionsBySID[sid])
                else:
                    r.append(sid)

            if r:
                sessionsWithAttribute = sessionsByAttribute[attr][v]
                for each in r:
                    if isinstance(sessionsWithAttribute, dict):
                        sessionsWithAttribute.pop(each, None)
                    else:
                        sessionsWithAttribute.discard(each)

        except:
            srv = sm.services['sessionMgr']
            srv.LogError('Session map borked')
            srv.LogError('sessionsByAttribute=', sessionsByAttribute)
            srv.LogError('sessionsBySID=', sessionsBySID)
            log.LogTraceback()
            raise

    if len(ret) > 1 and attr in ('charid', 'userid'):
        return sorted(ret, key=lambda s: s.localSID, reverse=True)
    return ret


def FindSessionClient(attr, val):
    session = FindSessions(attr, val)
    if session:
        return getattr(session[0], 'clientID', None)


callTimerKeys = {}
serviceCallTimes = {}
webCallTimes = {}
userCallTimes = {}
outstandingCallTimers = []
methodCallHistory = deque(maxlen=1000)

class RealCallTimer():
    TimerType = 2

    def __init__(self, k):
        k = callTimerKeys.setdefault(k, k)
        self.key = k
        localstorage.UpdateLocalStorage({'calltimer.key': k})
        if not session:
            self.mask = GetServiceSession('DefaultCallTimer').Masquerade()
        else:
            self.mask = None
        self.start = blue.os.GetWallclockTimeNow()
        outstandingCallTimers.append((k, self.start))

    def Done(self):
        stop = blue.os.GetWallclockTimeNow()
        t = stop - self.start
        if t < 0:
            log.general.Log('blue.os.GetWallclockTimeNow() is running backwards... now=%s, start=%s' % (stop, self.start), 2, 1)
            t = 0
        if session and not session.role & ROLE_SERVICE:
            if getattr(session, 'clientID', 0):
                other = userCallTimes
            else:
                other = webCallTimes
        else:
            other = serviceCallTimes
        for calltimes in (session.calltimes, other):
            if self.key not in calltimes:
                theCallTime = [0,
                 0,
                 -1,
                 -1,
                 0,
                 0]
                calltimes[self.key] = theCallTime
            else:
                theCallTime = calltimes[self.key]
            theCallTime[0] += 1
            theCallTime[1] += t
            if theCallTime[2] == -1 or t < theCallTime[2]:
                theCallTime[2] = t
            if theCallTime[3] == -1 or t > theCallTime[3]:
                theCallTime[3] = t

        if self.mask:
            self.mask.UnMask()
        if machobase.mode == 'client':
            k = (self.key, self.start, t)
            methodCallHistory.append(k)
        try:
            outstandingCallTimers.remove((self.key, self.start))
        except:
            sys.exc_clear()

    def __enter__(self):
        pass

    def __exit__(self, e, v, tb):
        self.Done()


class BasicCallTimer(object):
    TimerType = 1

    def __init__(self, k):
        k = callTimerKeys.setdefault(k, k)
        self.key = k
        self.start = blue.os.GetWallclockTimeNow()

    def Done(self):
        stop = blue.os.GetWallclockTimeNow()
        elapsed = stop - self.start
        if session and not session.role & ROLE_SERVICE:
            if getattr(session, 'clientID', 0):
                callTimes = userCallTimes
            else:
                callTimes = webCallTimes
        else:
            callTimes = serviceCallTimes
        if elapsed < 0:
            log.general.Log('blue.os.GetWallclockTimeNow() is running backwards... now=%s, start=%s' % (stop, self.start), 2, 1)
            elapsed = 0
        if self.key not in callTimes:
            callEntry = [0,
             0,
             -1,
             -1,
             0,
             0]
            callTimes[self.key] = callEntry
        else:
            callEntry = callTimes[self.key]
        callEntry[0] += 1
        callEntry[1] += elapsed
        if callEntry[2] == -1 or elapsed < callEntry[2]:
            callEntry[2] = elapsed
        if callEntry[3] == -1 or elapsed > callEntry[3]:
            callEntry[3] = elapsed

    def __enter__(self):
        pass

    def __exit__(self, e, v, tb):
        self.Done()


class DummyCallTimer(object):
    TimerType = 0

    def __init__(self, k):
        pass

    def Done(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, e, v, tb):
        pass


CallTimer = DummyCallTimer

def EnableCallTimers(timerType):
    global CallTimer
    was = CallTimer.TimerType
    if timerType == 0:
        CallTimer = DummyCallTimer
    elif timerType == 1:
        CallTimer = BasicCallTimer
    else:
        CallTimer = RealCallTimer
    return was


def IsInClientContext():
    return 'base.ClientContext' in localstorage.GetLocalStorage()


def CallTimersEnabled():
    return CallTimer.TimerType


def GetCallTimes():
    return (userCallTimes, serviceCallTimes, webCallTimes)


def GetNewSid():
    return random.getrandbits(63)


def CloseSession(sess, isRemote = False):
    if sess is not None:
        if hasattr(sess, 'remoteServiceSessionRefCount'):
            sess.__dict__['remoteServiceSessionRefCount'] -= 1
            if sess.__dict__['remoteServiceSessionRefCount'] > 0:
                return
        if sess.sid in sessionsBySID:
            sess.ClearAttributes(isRemote)


class CoreSession():
    __persistvars__ = ['userid',
     'languageID',
     'role',
     'charid',
     'address',
     'userType',
     'maxSessionTime',
     'sessionType',
     'countryCode']
    __nonpersistvars__ = ['sid',
     'c2ooid',
     'connectedObjects',
     'connectedServices',
     'clientID',
     'localSID',
     'contextOnly',
     'receivedVersion',
     'irrelevanceTime']
    __attributesWithDefaultValueOfZero__ = []
    __characterDependantAttributes__ = {'objectID',
     'wingid',
     'constellationid',
     'regionid',
     'locationid',
     'shipid',
     'squadid',
     'solarsystemid',
     'charid',
     'corpid',
     'structureid',
     'stationid',
     'fleetid',
     'warfactionid',
     'allianceid',
     'solarsystemid2',
     'inDetention'}
    __userDependantAttributes__ = {'userid',
     'languageID',
     'address',
     'userType',
     'maxSessionTime',
     'countryCode',
     'role'}

    def __init__(self, sid, localSID, role, sessionType, defaultVarList = []):
        global __contextOnlyTypes__
        if sessionType not in const.session.VALID_SESSION_TYPES:
            raise ValueError('Trying to create a session with an invalid session type')
        d = self.__dict__
        d['additionalNoSetAttributes'] = []
        defaultVarList = self.__persistvars__ + defaultVarList
        for attName in defaultVarList:
            d[attName] = self.GetDefaultValueOfAttribute(attName)

        d['version'] = 1
        d['receivedVersion'] = 1
        d['irrelevanceTime'] = None
        d['sid'] = sid
        d['localSID'] = localSID
        d['role'] = None
        d['sessionType'] = sessionType
        d['c2ooid'] = 1
        d['connectedObjects'] = {}
        d['connectedServices'] = {}
        d['calltimes'] = {}
        d['notificationID'] = 0L
        d['machoObjectsByID'] = {}
        d['machoObjectConnectionsByObjectID'] = {}
        d['sessionVariables'] = {}
        d['lastRemoteCall'] = blue.os.GetWallclockTime()
        d['nextSessionChange'] = None
        d['sessionChangeReason'] = 'Initial State'
        d['rwlock'] = None
        d['sessionhist'] = []
        d['hasproblems'] = 0
        d['mutating'] = 0
        d['changing'] = None
        d['additionalDistributedProps'] = []
        d['additionalNonIntegralAttributes'] = []
        d['longAttributes'] = []
        d['additionalAttributesToPrint'] = []
        d['additionalHexAttributes'] = []
        d['callThrottling'] = {}
        d['contextOnly'] = machobase.mode == 'server' and sessionType in __contextOnlyTypes__
        d['countryCode'] = None
        self.__ChangeAttribute('role', role)
        self.LogSessionHistory('Session created')

    def Throttle(self, key, throttleTimes, throttleInterval, userErrorMessage, userErrorParams = None):
        lastKeyTimes = self.callThrottling.get(key, [])
        now = blue.os.GetWallclockTime()
        if len(lastKeyTimes) >= throttleTimes:
            temp = []
            earliestTime = None
            for time in lastKeyTimes:
                if now - time < throttleInterval:
                    temp.append(time)
                    if earliestTime is None or time < earliestTime:
                        earliestTime = time

            if len(temp) >= throttleTimes:
                self.callThrottling[key] = temp
                remainingTime = earliestTime + throttleInterval - now if earliestTime is not None else throttleInterval
                mergedErrorParams = {'remainingTime': max(0L, remainingTime)}
                if userErrorParams is not None:
                    mergedErrorParams.update(userErrorParams)
                raise UserError(userErrorMessage, mergedErrorParams)
            else:
                lastKeyTimes = temp
        lastKeyTimes.append(now)
        self.callThrottling[key] = lastKeyTimes

    def IsMutating(self):
        return self.mutating

    def IsChanging(self):
        return self.changing is not None

    def IsItSafe(self):
        return not (self.IsMutating() or self.IsChanging())

    def IsItSemiSafe(self):
        return self.IsItSafe() or self.IsMutating() and self.IsChanging()

    def WaitUntilSafe(self):
        if session.IsItSafe():
            return
        timeWaited = 0
        while timeWaited <= 30000 and not session.IsItSafe():
            blue.pyos.synchro.SleepWallclock(100)
            timeWaited += 100

        if not session.IsItSafe():
            raise RuntimeError('Session did not become safe within 30secs')

    def RegisterMachoObjectConnection(self, objectID, connection, refID):
        connectionID = GetObjectUUID(connection)
        if objectID not in self.machoObjectConnectionsByObjectID:
            self.machoObjectConnectionsByObjectID[objectID] = [0, weakref.WeakValueDictionary({})]
        self.machoObjectConnectionsByObjectID[objectID][1][connectionID] = connection
        self.machoObjectConnectionsByObjectID[objectID][0] = max(self.machoObjectConnectionsByObjectID[objectID][0], refID)

    def UnregisterMachoObjectConnection(self, objectID, connection):
        connectionID = GetObjectUUID(connection)
        if objectID not in self.machoObjectConnectionsByObjectID:
            return None
        else:
            if connectionID in self.machoObjectConnectionsByObjectID[objectID][1]:
                log.LogTraceback('Unexpected Crapola:  connectionID still found in machoObjectConnectionsByObjectID[objectID]')
                del self.machoObjectConnectionsByObjectID[objectID][1][connectionID]
            if not self.machoObjectConnectionsByObjectID[objectID][1]:
                refID = self.machoObjectConnectionsByObjectID[objectID][0]
                del self.machoObjectConnectionsByObjectID[objectID]
                return refID
            return None

    def RegisterMachoObject(self, objectID, object, refID):
        sessionsByAttribute['objectID'][objectID][self.sid] = max(refID, sessionsByAttribute['objectID'][objectID].get(self.sid, 0))
        if objectID in self.machoObjectsByID:
            self.machoObjectsByID[objectID][0] = max(refID, self.machoObjectsByID[objectID][0])
        else:
            self.machoObjectsByID[objectID] = [refID, object]

    def UnregisterMachoObject(self, objectID, refID, suppressnotification = 1):
        try:
            if objectID in self.machoObjectConnectionsByObjectID:
                del self.machoObjectConnectionsByObjectID[objectID]
            if objectID in sessionsByAttribute['objectID']:
                if self.sid in sessionsByAttribute['objectID'][objectID]:
                    if refID is None or refID >= sessionsByAttribute['objectID'][objectID][self.sid]:
                        del sessionsByAttribute['objectID'][objectID][self.sid]
                        if not sessionsByAttribute['objectID'][objectID]:
                            del sessionsByAttribute['objectID'][objectID]
            if objectID in self.machoObjectsByID:
                if refID is None or refID >= self.machoObjectsByID[objectID][0]:
                    object = self.machoObjectsByID[objectID][1]
                    del self.machoObjectsByID[objectID]
                    if machobase.mode != 'client' and not suppressnotification and getattr(self, 'clientID', 0) and not getattr(self, 'clearing_session', 0):
                        sm.services['machoNet'].Scattercast('+clientID', [self.clientID], 'OnMachoObjectDisconnect', objectID, self.clientID, refID)
                    if isinstance(object, ObjectConnection):
                        object.DisconnectObject()
        except StandardError:
            log.LogException()
            sys.exc_clear()

    def DumpSession(self, prefix, reason):
        loglines = [prefix + ':  ' + reason + ".  It's history is as follows:"]
        lastEntry = ''
        for eachHistoryRecord in self.sessionhist:
            header = prefix + ':  ' + formatUtil.FmtDateEng(eachHistoryRecord[0], 'll') + ': '
            lines = eachHistoryRecord[1].split('\n')
            tmp = eachHistoryRecord[2]
            if tmp == lastEntry:
                txt = '< same >'
            else:
                txt = tmp
            lastEntry = tmp
            footer = ', ' + txt
            for eachLine in lines[:len(lines) - 1]:
                loglines.append(header + eachLine)

            loglines.append(header + lines[len(lines) - 1] + footer)

        loglines.append(prefix + ':  Current Session Data:  %s' % strx(self))
        currentcall = localstorage.GetLocalStorage().get('base.currentcall', None)
        if currentcall:
            try:
                currentcall = currentcall()
                loglines.append('currentcall was: ' + strx(currentcall))
            except ReferenceError:
                sys.exc_clear()

        log.general.Log('\n'.join(loglines), 1, 2)

    def Masquerade(self, props = None):
        w = weakref.ref(self)
        if self.charid:
            tmp = {'base.session': w,
             'base.charsession': w}
        else:
            tmp = {'base.session': w}
        if props is not None:
            tmp.update(props)
        return MasqueradeMask(tmp)

    def GetActualSession(self):
        return self

    def LogSessionHistory(self, reason, details = None, noBlather = 0):
        if self.role & ROLE_SERVICE and not self.hasproblems:
            return
        timer = PushMark('LogSessionHistory')
        try:
            if details is None:
                details = ''
                for each in ['sid', 'clientID'] + self.__persistvars__:
                    if getattr(self, each, None) is not None:
                        details = details + each + ':' + strx(getattr(self, each)) + ', '

                details = 'session=' + details[:-2]
            else:
                details = 'info=' + strx(details)
            self.__dict__['sessionhist'].append((blue.os.GetWallclockTime(), strx(reason)[:255], strx(details)[:255]))
            if len(self.__dict__['sessionhist']) > 120:
                self.__dict__['sessionhist'] = self.__dict__['sessionhist'][70:]
            if not noBlather and log.general.IsOpen(1) and 'sm' in globals() and not sm.services['machoNet'].IsClusterShuttingDown():
                log.general.Log('SessionHistory:  reason=%s, %s' % (reason, strx(details)), 1, 1)
        finally:
            PopMark(timer)

    def LogSessionError(self, what, novalidate = 0):
        self.__LogSessionProblem(what, 4, novalidate)

    def __LogSessionProblem(self, what, how, novalidate = 0):
        self.hasproblems = 1
        self.LogSessionHistory(what)
        if log.general.IsOpen(how):
            lines = ['A session related error has occurred.  Session history:']
            for eachHistoryRecord in self.sessionhist:
                s = ''.join(map(strx, formatUtil.FmtDateEng(eachHistoryRecord[0], 'll') + ': ' + eachHistoryRecord[1] + ', ' + eachHistoryRecord[2]))
                if len(s) > 5000:
                    s = s[:5000]
                while len(s) > 255:
                    lines.append(s[:253])
                    s = '- ' + s[253:]

                lines.append(s)

            lines.append('Session Data (should be identical to last history record):  %s' % strx(self))
            try:
                currentcall = localstorage.GetLocalStorage().get('base.currentcall', None)
                if currentcall:
                    currentcall = currentcall()
                    lines.append('currentcall was: ' + strx(currentcall))
            except ReferenceError:
                sys.exc_clear()

            log.general.Log('\n'.join(lines), how, 2)
        if not novalidate:
            self.ValidateSession('session-error-dump')

    def SetSessionVariable(self, k, v):
        if v is None:
            try:
                del self.__dict__['sessionVariables'][k]
            except:
                sys.exc_clear()

        else:
            self.__dict__['sessionVariables'][k] = v

    def GetSessionVariable(self, k, defaultValue = None):
        try:
            return self.__dict__['sessionVariables'][k]
        except:
            sys.exc_clear()
            if defaultValue is not None:
                self.__dict__['sessionVariables'][k] = defaultValue
                return defaultValue
            return

    def GetDistributedProps(self, getAll):
        retval = []
        if self.role & ROLE_SERVICE == 0:
            for attribute in self.__persistvars__ + self.additionalDistributedProps:
                if getAll or self.__dict__[attribute] != self.GetDefaultValueOfAttribute(attribute):
                    retval.append(attribute)

        return retval

    __dependant_attributes__ = {'userid': ['role',
                'charid',
                'callback',
                'languageID',
                'userType',
                'maxSessionTime',
                'countryCode'],
     'sid': ['userid']}

    def DependantAttributes(self, attribute):
        retval = self.__dependant_attributes__.get(attribute, [])
        retval2 = set()
        for each in retval:
            retval2.add(each)
            for other in self.DependantAttributes(each):
                retval2.add(other)

        return list(retval2)

    def GetDefaultValueOfAttribute(self, attribute):
        if attribute == 'role':
            return ROLE_LOGIN
        if attribute == 'sessionType':
            return self.__dict__.get('sessionType', None)
        if attribute in self.__attributesWithDefaultValueOfZero__:
            return 0
        if attribute == 'languageID' and machobase.mode == 'client':
            return strx(prefs.GetValue('languageID', 'EN'))

    def _DisconnectSessionObjects(self):
        for each in self.__dict__['connectedObjects'].values():
            each[0].DisconnectObject()

        for objectID in copy.copy(self.__dict__['machoObjectsByID']):
            self.UnregisterMachoObject(objectID, None)

    def ClearCharacterDependantAttributes(self):
        machoNet = sm.GetServiceIfRunning('machoNet')
        if machoNet and machoNet.IsClusterShuttingDown() and self.userid:
            log.general.Log('Cluster shutting down, rejecting session clearing %s' % self.userid, log.LGINFO)
            return
        self.StartSessionChange(reason='ClearCharacterDependantAttributes')
        try:
            if getattr(self, 'clearing_session', 0):
                self.LogSessionHistory("Tried to clear a cleared/clearing session's attributes")
            else:
                self.LogSessionHistory('Clearing character dependant session attributes')
                self._DisconnectSessionObjects()
                if self.sid in sessionsBySID:
                    self.ValidateSession('pre-clear')
                    for attr in self.__characterDependantAttributes__:
                        v = getattr(self, attr, None)
                        try:
                            del sessionsByAttribute[attr][v][self.sid]
                            if not sessionsByAttribute[attr][v]:
                                del sessionsByAttribute[attr][v]
                        except KeyError:
                            sys.exc_clear()

                self.__dict__['clearing_session'] = 1
                try:
                    d = {}
                    for each in self.__persistvars__:
                        if each in self.__userDependantAttributes__:
                            d[each] = getattr(self, each, None)
                        elif each not in ('connectedObjects', 'c2ooid'):
                            d[each] = self.GetDefaultValueOfAttribute(each)

                    self.SetAttributes(d, False, True)
                    self.__dict__['connectedObjects'] = {}
                    self.__dict__['machoObjectsByID'] = {}
                    d['sessionVariables'] = {}
                    self.LogSessionHistory('Character dependant session attributes cleared')
                finally:
                    self.__dict__['clearing_session'] = 0

        finally:
            self.changing = None

    def ClearAttributes(self, isRemote = 0, dontSendMessage = False):
        machoNet = sm.GetServiceIfRunning('machoNet')
        if machoNet and machoNet.IsClusterShuttingDown() and self.userid:
            log.general.Log('Cluster shutting down, rejecting session clearing %s' % self.userid, log.LGINFO)
            return
        self.StartSessionChange(reason='ClearAttributes')
        try:
            if getattr(self, 'clearing_session', 0):
                self.LogSessionHistory("Tried to clear a cleared/clearing session's attributes")
            else:
                self.LogSessionHistory('Clearing session attributes')
                self._DisconnectSessionObjects()
                if self.sid in sessionsBySID:
                    self.ValidateSession('pre-clear')
                    sid = self.sid
                    del sessionsBySID[sid]
                    for attr in sessionsByAttribute:
                        val = getattr(self, attr, None)
                        try:
                            try:
                                sessionsByAttribute[attr][val].discard(sid)
                            except AttributeError:
                                del sessionsByAttribute[attr][val][sid]

                            if not sessionsByAttribute[attr][val]:
                                del sessionsByAttribute[attr][val]
                        except StandardError:
                            sys.exc_clear()

                self.__dict__['clearing_session'] = 1
                d = {}
                for each in self.__persistvars__:
                    if each not in ('connectedObjects', 'c2ooid'):
                        d[each] = self.GetDefaultValueOfAttribute(each)

                self.SetAttributes(d, isRemote, dontSendMessage=dontSendMessage)
                self.__dict__['connectedObjects'] = {}
                self.__dict__['machoObjectsByID'] = {}
                d['sessionVariables'] = {}
                sm.ScatterEvent('OnSessionEnd', self.sid)
                self.LogSessionHistory('Session attributes cleared')
        finally:
            self.changing = None

    def ValidateSession(self, prefix):
        bad = False
        if not self.contextOnly:
            if not getattr(self, 'clearing_session', 0):
                for attribute in sessionsByAttribute:
                    value = getattr(self, attribute, None)
                    if value:
                        valueSIDs = sessionsByAttribute[attribute]
                        if value not in valueSIDs:
                            self.LogSessionHistory('sessionsByAttribute[%s] broken, %s is not found' % (attribute, value))
                            bad = True
                        elif self.sid not in valueSIDs[value]:
                            self.LogSessionHistory('sessionsByAttribute[%s][%s] broken, %s is not found' % (attribute, value, self.sid))
                            bad = True
                        elif attribute in ('userid', 'charid') and len(valueSIDs[value]) != 1:
                            self.LogSessionHistory('sessionsByAttribute[%s][%s] broken, this user/char has multiple sessions (%d)' % (attribute, value, len(valueSIDs[value])))
                            bad = True

                if bad:
                    self.LogSessionError("The session failed it's %s validation check.  Session dump and stack trace follows." % (prefix,), 1)
                    log.LogTraceback()
        return bad

    def DisconnectFilteredObjects(self, disappeared):
        if disappeared:
            objects = []
            for oid in self.connectedObjects.iterkeys():
                objConn = self.connectedObjects[oid][0]
                object = objConn.__object__
                if object is not None and hasattr(object, '__sessionfilter__'):
                    for attribute in disappeared:
                        if attribute in object.__sessionfilter__:
                            objects.append((objConn, oid))
                            break

            for objConn, oid in objects:
                with self.Masquerade({'base.caller': weakref.ref(objConn)}):
                    try:
                        if oid in self.connectedObjects:
                            objConn.DisconnectObject()
                    except StandardError:
                        log.LogException()
                        sys.exc_clear()

    def CallProcessChangeOnObjects(self, notify, isRemote):
        objects = []
        notifyNodes = []
        for oid in self.connectedObjects.iterkeys():
            objConn = self.connectedObjects[oid][0]
            object = objConn.__object__
            if object is not None and hasattr(object, '__sessionfilter__') and hasattr(object, 'ProcessSessionChange'):
                for attribute in notify.iterkeys():
                    if attribute in object.__sessionfilter__:
                        objects.append((objConn, object, oid))
                        break

        for objConn, object, oid in objects:
            with self.Masquerade({'base.caller': weakref.ref(objConn)}):
                try:
                    if oid in self.connectedObjects:
                        notifyNodes.append(object.ProcessSessionChange(isRemote, self, notify))
                except StandardError:
                    log.LogException()
                    sys.exc_clear()

        return notifyNodes

    def ComputeNotifySets(self, changes, pairs):
        notify = {}
        disappeared = set()
        for attribute in changes.iterkeys():
            currentEffectiveValue = self.__dict__.get(attribute, self.GetDefaultValueOfAttribute(attribute))
            newValue = changes[attribute][1] if pairs else changes[attribute]
            if currentEffectiveValue != newValue:
                notify[attribute] = (currentEffectiveValue, newValue)
                if currentEffectiveValue and not newValue:
                    disappeared.add(attribute)

        return (notify, disappeared)

    def __ChangeAttribute(self, attribute, newValue):
        self.__dict__['nextSessionChange'] = blue.os.GetSimTime() + SESSIONCHANGEDELAY
        if getattr(self, 'clearing_session', 0):
            self.__dict__[attribute] = newValue
        else:
            valueSIDs = sessionsByAttribute.get(attribute, None)
            if valueSIDs is None:
                self.__dict__[attribute] = newValue
            else:
                try:
                    if newValue and newValue not in valueSIDs:
                        valueSIDs[newValue] = {}
                    oldValue = self.__dict__[attribute]
                    if not self.contextOnly:
                        if oldValue and oldValue in valueSIDs and self.sid in valueSIDs[oldValue]:
                            del valueSIDs[oldValue][self.sid]
                    self.__dict__[attribute] = newValue
                    if not self.contextOnly:
                        if newValue:
                            valueSIDs[newValue][self.sid] = 1
                        if oldValue and oldValue in valueSIDs and not len(valueSIDs[oldValue]):
                            del valueSIDs[oldValue]
                    if newValue and attribute == 'charid' and not charsession:
                        localstorage.UpdateLocalStorage({'base.charsession': weakref.ref(self)})
                except:
                    self.DumpSession('ARGH!!!', 'This session is blowing up during change attribute')
                    raise

    def RecalculateDependantAttributes(self, d):
        pass

    def StartSessionChange(self, reason):
        if not self.changing:
            self.changing = reason

    def SetAttributes(self, requestedChanges, isRemote = 0, dontSendMessage = False):
        machoNet = sm.GetServiceIfRunning('machoNet')
        if machoNet and machoNet.IsClusterShuttingDown() and getattr(self, 'userid', None):
            log.LogNotice('Cluster shutting down, rejecting session change %s' % self.userid)
            return
        self.StartSessionChange(reason='SetAttributes')
        try:
            self.LogSessionHistory('Setting session attributes')
            try:
                requestedChanges = copy.copy(requestedChanges)
                nonPersisted = []
                for attribute in requestedChanges:
                    if attribute not in self.__persistvars__:
                        nonPersisted.append(attribute)

                if nonPersisted:
                    log.LogTraceback(extraText=strx(nonPersisted), severity=log.LGWARN)
                    for attribute in nonPersisted:
                        del requestedChanges[attribute]

                dependantAttributes = []
                changes = {}
                for attribute in requestedChanges.iterkeys():
                    dependantAttributes += self.DependantAttributes(attribute)
                    if requestedChanges[attribute] is not None and attribute not in ['address', 'languageID', 'countryCode'] + self.additionalNonIntegralAttributes:
                        try:
                            if attribute in self.longAttributes:
                                changes[attribute] = long(requestedChanges[attribute])
                            else:
                                changes[attribute] = int(requestedChanges[attribute])
                        except TypeError:
                            log.general.Log('%s is not an integer %s' % (attribute, strx(requestedChanges[attribute])), 4, 1)
                            log.LogTraceback()
                            raise

                    else:
                        changes[attribute] = requestedChanges[attribute]

                charID = requestedChanges.get('charid', None)
                if charID is not None and charID != self.charid:
                    changes.update(sm.GetService('sessionMgr').GetInitialValuesFromCharID(charID))
                for attribute in dependantAttributes:
                    if attribute not in changes:
                        changes[attribute] = self.GetDefaultValueOfAttribute(attribute)

                self.RecalculateDependantAttributes(changes)
                self.ValidateSession('pre-change')
                notify, disappeared = self.ComputeNotifySets(changes, pairs=False)
                if notify:
                    if 'userid' in notify and notify['userid'][0] and notify['userid'][1]:
                        self.LogSessionError("A session's userID may not change, %s=>%s" % notify['userid'])
                        raise RuntimeError("A session's userID may not change")
                    mask = None
                    try:
                        if self.role & ROLE_SERVICE == 0:
                            mask = self.Masquerade()
                            if not self.contextOnly:
                                sm.NotifySessionChange('DoSessionChanging', isRemote, self, notify)
                            self.DisconnectFilteredObjects(disappeared)
                        for attribute in notify:
                            self.__ChangeAttribute(attribute, changes[attribute])

                        self.ValidateSession('post-change')
                        if self.role & ROLE_SERVICE == 0 and not dontSendMessage:
                            if not self.contextOnly:
                                notifyAdditionalNodes = list(sm.NotifySessionChange('ProcessSessionChange', isRemote, self, notify))
                                notifyAdditionalNodes.append(self.CallProcessChangeOnObjects(notify, isRemote))
                            else:
                                notifyAdditionalNodes = sm.GetService('sessionMgr').ProcessSessionChange(isRemote, self, notify)
                            clientID = getattr(self, 'clientID', None)
                            if clientID and not isRemote:
                                if not (self.role & (ROLE_LOGIN | ROLE_PLAYER) or self.role & (ROLE_SERVICE | ROLE_REMOTESERVICE)):
                                    self.LogSessionError("A distributed session's role should probably always have login and player rights, even before a change broadcast")
                                sessionChangeLayer = sm.services['machoNet'].GetGPCS('sessionchange')
                                if sessionChangeLayer is not None:
                                    sessionChangeLayer.SessionChanged(clientID, self.sid, notify, notifyAdditionalNodes)
                            if not self.contextOnly:
                                sm.NotifySessionChange('OnSessionChanged', isRemote, self, notify)
                    finally:
                        if mask is not None:
                            mask.UnMask()

            finally:
                self.LogSessionHistory('Session attributes set')

        finally:
            self.changing = None

    def RecalculateDependantAttributesWithChanges(self, changes):
        pass

    def ApplyRemoteAttributeChanges(self, changes, initialState):
        self.StartSessionChange(reason='ApplyInitialState' if initialState else 'ApplyRemoteAttributeChanges')
        try:
            self.LogSessionHistory('Receiving and performing %s' % self.changing)
            if self.role & ROLE_SERVICE:
                errorString = 'A service session may not change via %s, changes=%s' % (self.changing, strx(changes))
                self.LogSessionError(errorString)
                raise RuntimeError(errorString)
            if not self.role & (ROLE_LOGIN | ROLE_PLAYER):
                self.LogSessionError("A distributed session's role should probably always have login and player rights, even during a change broadcast")
            self.ValidateSession('pre-change')
            if initialState:
                self.RecalculateDependantAttributes(changes)
            else:
                self.RecalculateDependantAttributesWithChanges(changes)
            notify, disappeared = self.ComputeNotifySets(changes, pairs=not initialState)
            if notify:
                if 'userid' in notify and notify['userid'][0] and notify['userid'][1]:
                    self.LogSessionError("A session's userID may not change, %s=>%s" % notify['userid'])
                    raise RuntimeError("A session's userID may not change")
                if not initialState and 'role' in notify and self.charid and notify['role'][1] != self.role:
                    initial_roles, new_roles = changes['role']
                    if initial_roles and new_roles:
                        if new_roles not in (add_role(initial_roles, ROLE_PLAYER), remove_role(initial_roles, ROLE_PLAYER)):
                            self.LogSessionError("A session's role should probably not change for active characters, even in remote attribute stuff")
                mask = None
                try:
                    mask = self.Masquerade()
                    if not self.contextOnly:
                        sm.NotifySessionChange('DoSessionChanging', True, self, notify)
                    self.DisconnectFilteredObjects(disappeared)
                    for attribute in notify:
                        self.__ChangeAttribute(attribute, changes[attribute] if initialState else changes[attribute][1])

                    self.ValidateSession('post-change')
                    if not self.contextOnly:
                        sm.NotifySessionChange('ProcessSessionChange', True, self, notify)
                        self.CallProcessChangeOnObjects(notify, isRemote=True)
                        sm.NotifySessionChange('OnSessionChanged', True, self, notify)
                finally:
                    if mask is not None:
                        mask.UnMask()
                    self.LogSessionHistory(self.changing)

        finally:
            self.changing = None

    def DelayedInitialStateChange(self):
        if self.role & ROLE_SERVICE != 0:
            errorString = 'A service session may not change via DelayedInitialStateChange'
            self.LogSessionError(errorString)
            raise RuntimeError(errorString)
        if machobase.mode != 'server':
            raise RuntimeError('DelayedInitialStateChange called on %s, can only be called on server', machobase.mode)
        mask = None
        try:
            self.LogSessionHistory('CTXSESS: Performing a delayed initial state change on session', self.sid)
            self.StartSessionChange(reason='ApplyInitialState')
            changes = {attr:self.__dict__[attr] for attr in self.GetDistributedProps(False)}
            notify = {}
            for attribute, myValue in changes.iteritems():
                defaultValue = self.GetDefaultValueOfAttribute(attribute)
                if myValue != defaultValue:
                    notify[attribute] = (defaultValue, myValue)

            if notify:
                mask = self.Masquerade()
                sm.NotifySessionChange('DoSessionChanging', True, self, notify)
                for attribute, value in changes.iteritems():
                    valueSIDs = sessionsByAttribute.get(attribute, None)
                    if valueSIDs is not None:
                        if value not in valueSIDs:
                            valueSIDs[value] = {}
                        valueSIDs[value][self.sid] = 1

                sessionsBySID[self.sid] = self
                self.ValidateSession('post-delayedinitialstatechange')
                sm.NotifySessionChange('ProcessSessionChange', True, self, notify)
                self.CallProcessChangeOnObjects(notify, isRemote=True)
                sm.NotifySessionChange('OnSessionChanged', True, self, notify)
        finally:
            if mask is not None:
                mask.UnMask()
            self.LogSessionHistory('Delayed ApplyInitialState')
            self.changing = None

    def __repr__(self):
        ret = '<Session: ('
        for each in ['sid',
         'clientID',
         'changing',
         'mutating',
         'contextOnly'] + self.additionalAttributesToPrint + self.__persistvars__:
            if getattr(self, each, None) is not None:
                if each in ['role'] + self.additionalHexAttributes:
                    ret = ret + each + ':' + strx(hex(getattr(self, each))) + ', '
                else:
                    ret = ret + each + ':' + strx(getattr(self, each)) + ', '

        ret = ret[:-2] + ')>'
        return ret

    def __setattr__(self, attr, value):
        if attr in ['sid', 'clientID'] + self.additionalNoSetAttributes + self.__persistvars__:
            raise RuntimeError('ReadOnly', attr)
        else:
            self.__dict__[attr] = value

    def DisconnectObject(self, object, key = None, delaySecs = 1):
        if key is None:
            caller = localstorage.GetLocalStorage().get('base.caller', None)
            if caller:
                caller = caller()
                if isinstance(caller, ObjectConnection) and caller.__object__ is object:
                    caller.DisconnectObject(delaySecs)
                    return
        for k, v in self.connectedObjects.items():
            obConn, = v
            if obConn.__object__ is object and (key is None or key == (obConn.__dict__['__session__'].sid, obConn.__dict__['__c2ooid__'])):
                obConn.DisconnectObject(delaySecs)

    def RedirectObject(self, object, serviceName = None, bindParams = None, key = None):
        for k, v in self.connectedObjects.items():
            obConn, = v
            if obConn.__object__ is object and (key is None or key == (obConn.__dict__['__session__'].sid, obConn.__dict__['__c2ooid__'])):
                obConn.RedirectObject(serviceName, bindParams)

    def ConnectToObject(self, object, serviceName = None, bindParams = None):
        c2ooid = self.__dict__['c2ooid']
        self.__dict__['c2ooid'] += 1
        return ObjectConnection(self, object, c2ooid, serviceName, bindParams)

    def ConnectToClientService(self, svc, idtype = None, theID = None):
        if theID is None or idtype is None:
            if self.role & ROLE_SERVICE:
                log.LogTraceback()
                raise RuntimeError('You must specify an ID type and ID to identify the client')
            else:
                theID = self.clientID
                idtype = 'clientID'
        elif not self.role & ROLE_SERVICE and machobase.mode != 'client' and not IsInClientContext():
            log.LogTraceback()
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if currentcall:
            currentcall.UnLockSession()
        return sm.services['sessionMgr'].ConnectToClientService(svc, idtype, theID)

    def ConnectToService(self, svc, **keywords):
        return ServiceConnection(self, svc, **keywords)

    def ConnectToAllServices(self, svc, batchInterval = 0):
        if not self.role & ROLE_SERVICE and machobase.mode != 'client' and not IsInClientContext():
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        return sm.services['machoNet'].ConnectToAllServices(svc, self, batchInterval=batchInterval)

    def ConnectToRemoteService(self, svc, nodeID = None):
        if not self.role & ROLE_SERVICE and machobase.mode != 'client' and not IsInClientContext():
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if machobase.mode == 'server' and nodeID is None:
            nodeID = sm.GetService(svc).MachoResolve(self)
            if type(nodeID) == types.StringType:
                raise RuntimeError(nodeID)
            elif nodeID is None:
                return self.ConnectToService(svc)
        if nodeID is not None and nodeID == sm.services['machoNet'].GetNodeID():
            return self.ConnectToService(svc)
        return sm.services['machoNet'].ConnectToRemoteService(svc, nodeID, self)

    def ConnectToSolServerService(self, svc, nodeID = None):
        if not self.role & ROLE_SERVICE and machobase.mode != 'client' and not IsInClientContext():
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if machobase.mode == 'server' and nodeID is None:
            nodeID = sm.GetService(svc).MachoResolve(self)
            if type(nodeID) == types.StringType:
                raise RuntimeError(nodeID)
            elif nodeID is None:
                return self.ConnectToService(svc)
        if machobase.mode == 'server' and (nodeID is None or nodeID == sm.services['machoNet'].GetNodeID()):
            return self.ConnectToService(svc)
        else:
            return sm.services['machoNet'].ConnectToRemoteService(svc, nodeID, self)

    def ConnectToProxyServerService(self, svc, nodeID = None):
        if not self.role & ROLE_SERVICE and machobase.mode != 'client' and not IsInClientContext():
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if machobase.mode == 'proxy' and (nodeID is None or nodeID == sm.services['machoNet'].GetNodeID()):
            return self.ConnectToService(svc)
        else:
            return sm.services['machoNet'].ConnectToRemoteService(svc, nodeID, self)

    def ConnectToAnyService(self, svc):
        if not self.role & ROLE_SERVICE and machobase.mode != 'client' and not IsInClientContext():
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if svc in sm.services:
            return self.ConnectToService(svc)
        else:
            return self.ConnectToRemoteService(svc)

    def ConnectToAllNeighboringServices(self, svc, batchInterval = 0):
        if not self.role & ROLE_SERVICE and machobase.mode != 'client' and not IsInClientContext():
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        return sm.services['machoNet'].ConnectToAllNeighboringServices(svc, self, batchInterval=batchInterval)

    def ConnectToAllProxyServerServices(self, svc, batchInterval = 0):
        if not self.role & ROLE_SERVICE and machobase.mode != 'client' and not IsInClientContext():
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if machobase.mode == 'proxy':
            return sm.services['machoNet'].ConnectToAllSiblingServices(svc, self, batchInterval=batchInterval)
        else:
            return sm.services['machoNet'].ConnectToAllNeighboringServices(svc, self, batchInterval=batchInterval)

    def ConnectToAllSolServerServices(self, svc, batchInterval = 0):
        if not self.role & ROLE_SERVICE and machobase.mode != 'client' and not IsInClientContext():
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if machobase.mode == 'server':
            return sm.services['machoNet'].ConnectToAllSiblingServices(svc, self, batchInterval=batchInterval)
        else:
            return sm.services['machoNet'].ConnectToAllNeighboringServices(svc, self, batchInterval=batchInterval)

    def RemoteServiceCall(self, dest, service, method, *args, **keywords):
        return self.RemoteServiceCallWithoutTheStars(dest, service, method, args, keywords)

    def RemoteServiceCallWithoutTheStars(self, dest, service, method, *args, **keywords):
        if not self.role & ROLE_SERVICE and machobase.mode != 'client' and not IsInClientContext():
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        return sm.services['machoNet'].RemoteServiceCallWithoutTheStars(self, dest, service, method, args, keywords)

    def RemoteServiceNotify(self, dest, service, method, *args, **keywords):
        return self.RemoteServiceNotifyWithoutTheStars(dest, service, method, args, keywords)

    def RemoteServiceNotifyWithoutTheStars(self, dest, service, method, args, keywords):
        if not self.role & ROLE_SERVICE and machobase.mode != 'client' and not IsInClientContext():
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        sm.services['machoNet'].RemoteServiceNotifyWithoutTheStars(self, args, keywords)

    def ResetSessionChangeTimer(self, reason):
        sm.GetService('sessionMgr').LogInfo("Resetting next legal session change timer, reason='", reason, "', was ", formatUtil.FmtDateEng(self.nextSessionChange or blue.os.GetSimTime()))
        self.nextSessionChange = None

    def ServiceProxy(self, serviceName):
        return ServiceProxy(serviceName, self)


class ServiceConnection():
    __restrictedcalls__ = {'Lock': 1,
     'UnLock': 1,
     'GetMachoObjectBoundToSession': 1}

    def __init__(self, sess, service, **keywords):
        self.__session__ = weakref.proxy(sess)
        self.__service__ = service
        self.__remote__ = keywords.get('remote', 0)
        sm.StartService(self.__service__)

    def Lock(self, lockID):
        return sm.GetService(self.__service__).LockService(lockID)

    def UnLock(self, lockID, lock):
        sm.GetService(self.__service__).UnLockService(lockID, lock)

    def GetInstanceID(self):
        return sm.GetService(self.__service__).startedWhen

    def __getitem__(self, key):
        mn = sm.services['machoNet']
        if type(key) == types.TupleType:
            nodeID = mn.GetNodeFromAddress(key[0], key[1])
        elif type(key) == types.IntType:
            nodeID = key
        else:
            srv = sm.StartServiceAndWaitForRunningState(self.__service__)
            nodeID = self.MachoResolve(key)
        if nodeID == mn.GetNodeID():
            return self
        else:
            return self.__session__.ConnectToRemoteService(self.__service__, nodeID)

    def __nonzero__(self):
        return 1

    def __str__(self):
        sess = 'unknown'
        try:
            sess = strx(self.__session__)
        except:
            pass

        return 'ServiceConnection, Service:' + strx(self.__service__) + '. Session:' + sess

    def __repr__(self):
        return self.__str__()

    def __getattr__(self, method):
        if method in self.__dict__:
            return self.__dict__[method]
        if method.startswith('__'):
            raise AttributeError(method)
        svc = sm.StartService(self.__service__)
        if not self.__remote__ and (self.__session__.role & ROLE_SERVICE or machobase.mode == 'client' or method == 'MachoResolve'):
            self.__WaitForRunningState(svc)
            if method.endswith('_Ex'):
                return FastCallWrapper(self.__session__, svc, method[:-3], self)
            else:
                return FastCallWrapper(self.__session__, svc, method, self)
        if self.__session__.role & ROLE_SERVICE:
            return UnlockedServiceCallWrapper(self.__session__, svc, method, self, self.__service__)
        else:
            return ServiceCallWrapper(self.__session__, svc, method, self, self.__service__)

    def __WaitForRunningState(self, svc):
        desiredStates = (SERVICE_RUNNING,)
        errorStates = (SERVICE_FAILED, SERVICE_STOPPED)
        sm.WaitForServiceObjectState(svc, desiredStates, errorStates)


class MasqueradeMask(object):

    def __init__(self, props):
        self.__prevStorage = localstorage.UpdateLocalStorage(props)

    def __enter__(self):
        pass

    def __exit__(self, e, v, tb):
        self.UnMask()

    def UnMask(self):
        localstorage.SetLocalStorage(self.__prevStorage)
        self.__prevStorage = None


class Session(CoreSession):
    __persistvars__ = CoreSession.__persistvars__ + ['regionid',
     'constellationid',
     'allianceid',
     'warfactionid',
     'corpid',
     'fleetid',
     'fleetrole',
     'wingid',
     'squadid',
     'shipid',
     'stationid',
     'structureid',
     'solarsystemid',
     'solarsystemid2',
     'hqID',
     'baseID',
     'rolesAtAll',
     'rolesAtHQ',
     'rolesAtBase',
     'rolesAtOther',
     'genderID',
     'bloodlineID',
     'raceID',
     'corpAccountKey',
     'inDetention']
    __nonpersistvars__ = CoreSession.__nonpersistvars__ + ['locationid', 'corprole']
    __attributesWithDefaultValueOfZero__ = CoreSession.__attributesWithDefaultValueOfZero__ + ['corprole',
     'rolesAtAll',
     'rolesAtHQ',
     'rolesAtBase',
     'rolesAtOther']
    __dependant_attributes_eve__ = {'userid': ['inDetention'],
     'charid': ['corpid',
                'fleetid',
                'shipid',
                'stationid',
                'structureid',
                'solarsystemid',
                'bloodlineID',
                'raceID',
                'genderID'],
     'corpid': ['baseID',
                'rolesAtAll',
                'rolesAtHQ',
                'rolesAtBase',
                'rolesAtOther',
                'hqID',
                'allianceid',
                'corpAccountKey',
                'warfactionid'],
     'baseID': ['corprole'],
     'rolesAtAll': ['corprole'],
     'rolesAtHQ': ['corprole'],
     'rolesAtBase': ['corprole'],
     'rolesAtOther': ['corprole'],
     'hqID': ['corprole'],
     'corpAccountKey': [],
     'stationid': ['locationid'],
     'solarsystemid': ['locationid'],
     'locationid': ['solarsystemid2'],
     'solarsystemid2': ['constellationid'],
     'constellationid': ['regionid'],
     'fleetid': ['fleetrole', 'wingid', 'squadid'],
     'wingid': ['squadid'],
     'squadid': []}
    __dependant_attributes__ = {}
    for key, val in CoreSession.__dependant_attributes__.iteritems():
        __dependant_attributes__[key] = val + __dependant_attributes_eve__.get(key, [])

    for key, val in __dependant_attributes_eve__.iteritems():
        if key not in __dependant_attributes__:
            __dependant_attributes__[key] = val

    def __init__(self, sid, localSID, role, sessionType):
        CoreSession.__init__(self, sid, localSID, role, sessionType, ['locationid', 'corprole'])
        self.additionalNoSetAttributes = ['locationid', 'corprole']
        self.additionalDistributedProps = ['locationid', 'corprole']
        self.additionalNonIntegralAttributes = ['fleetid',
         'fleetrole',
         'wingid',
         'squadid']
        self.longAttributes = ['corprole']
        self.additionalAttributesToPrint = ['locationid', 'corprole']
        self.additionalHexAttributes = ['corprole',
         'rolesAtAll',
         'rolesAtHQ',
         'rolesAtBase',
         'rolesAtOther']

    def RecalculateDependantAttributes(self, d):
        if 'stationid' in d or 'solarsystemid' in d:
            d['locationid'] = d.get('stationid') or d.get('solarsystemid')
        for each in ('hqID', 'baseID', 'rolesAtAll', 'rolesAtHQ', 'rolesAtBase', 'rolesAtOther', 'stationid', 'solarsystemid'):
            if each in d:
                rolesAtAll = d.get('rolesAtAll', self.rolesAtAll)
                rolesAtHQ = d.get('rolesAtHQ', self.rolesAtHQ)
                rolesAtBase = d.get('rolesAtBase', self.rolesAtBase)
                rolesAtOther = d.get('rolesAtOther', self.rolesAtOther)
                hqID = d.get('hqID', self.hqID)
                baseID = d.get('baseID', self.baseID)
                stationid = d.get('stationid', self.stationid)
                solarsystemid = d.get('solarsystemid', self.solarsystemid)
                corprole = rolesAtAll | rolesAtOther
                if stationid:
                    if stationid == hqID:
                        corprole = rolesAtAll | rolesAtHQ
                    elif stationid == baseID:
                        corprole = rolesAtAll | rolesAtBase
                d['corprole'] = corprole
                break

    def RecalculateDependantAttributesWithChanges(self, changes):
        if 'stationid' in changes or 'solarsystemid' in changes:
            old = self.locationid
            new = changes.get('stationid', [None, None])[1]
            if not new:
                new = changes.get('solarsystemid', [None, None])[1]
            changes['locationid'] = (old, new)
        for each in ('hqID', 'baseID', 'rolesAtAll', 'rolesAtHQ', 'rolesAtBase', 'rolesAtOther', 'stationid', 'solarsystemid'):
            if each in changes:
                rolesAtAll = changes.get('rolesAtAll', [None, self.rolesAtAll])[1]
                rolesAtHQ = changes.get('rolesAtHQ', [None, self.rolesAtHQ])[1]
                rolesAtBase = changes.get('rolesAtBase', [None, self.rolesAtBase])[1]
                rolesAtOther = changes.get('rolesAtOther', [None, self.rolesAtOther])[1]
                hqID = changes.get('hqID', [None, self.hqID])[1]
                baseID = changes.get('baseID', [None, self.baseID])[1]
                stationid = changes.get('stationid', [None, self.stationid])[1]
                solarsystemid = changes.get('solarsystemid', [None, self.solarsystemid])[1]
                old = self.corprole
                corprole = rolesAtAll | rolesAtOther
                if stationid:
                    if stationid == hqID:
                        corprole = rolesAtAll | rolesAtHQ
                    elif stationid == baseID:
                        corprole = rolesAtAll | rolesAtBase
                if old != corprole:
                    changes['corprole'] = (old, corprole)
                break


def CreateSession(sid = None, sessionType = const.session.SESSION_TYPE_GAME, role = ROLE_LOGIN):
    global local_sid
    if sessionType not in const.session.VALID_SESSION_TYPES:
        raise ValueError('Trying to create a session with an invalid session type')
    local_sid += 1
    while sid is None:
        sid = GetNewSid()
        if sid in sessionsBySID:
            log.general.Log('Session SID random collision!', log.LGWARN)
            sid = None

    if sid in sessionsBySID:
        log.general.Log('Session SID collision!', log.LGERR)
        log.general.Log('Local session being broken %s' % (sessionsBySID[sid],), log.LGERR)
    s = Session(sid, local_sid, role, sessionType)
    if not s.contextOnly:
        sessionsBySID[sid] = s
    allSessionsBySID[sid] = s
    return s


def GetServiceSession(serviceKey, refcounted = False):
    if serviceKey not in service_sessions:
        ret = CreateSession(GetNewSid(), const.session.SESSION_TYPE_SERVICE, ROLE_SERVICE)
        ret.serviceName = serviceKey
        service_sessions[serviceKey] = ret
    else:
        ret = service_sessions[serviceKey]
    if refcounted:
        if not hasattr(ret, 'remoteServiceSessionRefCount'):
            ret.__dict__['remoteServiceSessionRefCount'] = 1
        else:
            ret.__dict__['remoteServiceSessionRefCount'] += 1
    return ret


class ObjectcastCallWrapper():

    def __init__(self, object):
        self.object = weakref.proxy(object)

    def __call__(self, method, *args):
        sm.services['machoNet'].ObjectcastWithoutTheStars(self.object, method, args)


class UpdatePublicAttributesCallWrapper():

    def __init__(self, object):
        self.object = weakref.proxy(object)

    def __call__(self, *args, **keywords):
        pa = {}
        k = keywords.get('partial', [])
        for each in getattr(self.object, '__publicattributes__', []):
            if k and each not in k:
                continue
            if hasattr(self.object, each):
                pa[each] = getattr(self.object, each)

        sm.services['machoNet'].Objectcast(self.object, 'OnObjectPublicAttributesUpdated', GetObjectUUID(self.object), pa, args, keywords)


objectsByUUID = weakref.WeakValueDictionary({})
objectUUID = 0L

def GetObjectUUID(object):
    global objectUUID
    global objectsByUUID
    if hasattr(object, '__machoObjectUUID__'):
        return object.__machoObjectUUID__
    else:
        objectUUID += 1L
        if machobase.mode == 'client':
            t = 'C=0:%s' % objectUUID
        else:
            t = 'N=%s:%s' % (sm.services['machoNet'].GetNodeID(), objectUUID)
        setattr(object, '__machoObjectUUID__', t)
        if not hasattr(object, '__publicattributes__'):
            setattr(object, '__publicattributes__', [])
        setattr(object, 'Objectcast', ObjectcastCallWrapper(object))
        setattr(object, 'UpdatePublicAttributes', UpdatePublicAttributesCallWrapper(object))
        objectsByUUID[t] = object
        return t


def GetObjectByUUID(uuid):
    try:
        return objectsByUUID.get(uuid, None)
    except ReferenceError:
        sys.exc_clear()
        return None


def ReadContextSessionTypesPrefs():
    global __contextOnlyTypes__
    PREFS_PARAMETER = 'ContextSessionTypes'
    try:
        __contextOnlyTypes__ = []
        prefValue = prefs.GetValue(PREFS_PARAMETER, None)
        if prefValue is not None:
            log.LogInfo('CTXSESS: %s = %s', PREFS_PARAMETER, prefValue)
            contextTypes = prefValue.split(',')
            for typeName in contextTypes:
                if typeName in const.session.SESSION_NAME_TO_TYPE:
                    __contextOnlyTypes__.append(const.session.SESSION_NAME_TO_TYPE[typeName])
                else:
                    log.LogError("Ignoring invalid session type '%s' in prefs parameter '%s'" % (typeName, PREFS_PARAMETER))

        else:
            log.LogInfo('CTXSESS: %s not provided, no context sessions will be created' % PREFS_PARAMETER)
    except StandardError:
        log.LogException("Exception while parsing prefs parameter '%s'" % PREFS_PARAMETER)


ReadContextSessionTypesPrefs()
