#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\objectCaching.py
import binascii
import cPickle
import os
import random
import sys
import types
import zlib
import blue
import carbon.common.lib.const as const
import carbon.common.script.net.machobase as macho
import log
import telemetry
import uthread
from carbon.common.script.net.cachedObject import CachedObject as utilCachedObject
from carbon.common.script.net.machoNetAddress import MachoAddress
from carbon.common.script.sys import basesession, service
from carbon.common.script.sys.serviceConst import ROLE_ANY, ROLE_SERVICE
from carbon.common.script.sys.sessions import CachedMethodCalled
from carbon.common.script.util.format import FmtDateEng
from carbon.common.script.util.timerstuff import ClockThis
from stringutil import strx
cacheSessionVariables = None

class CoreObjectCachingSvc(service.Service):
    __guid__ = 'svc.objectCaching'
    __displayname__ = 'Object Caching Service'
    __dependencies__ = ['machoNet']
    __exportedcalls__ = {'GetCachableObject': [ROLE_ANY],
     'GetCachedObject': [ROLE_ANY],
     'GetCachedObjectVersion': [ROLE_ANY],
     'InvalidateCachedObjects': [ROLE_SERVICE],
     'InvalidateCachedMethodCall': [ROLE_SERVICE],
     'CacheObject': [ROLE_SERVICE],
     'RefreshCache': [ROLE_SERVICE],
     'GetCachedMethodCallVersion': [ROLE_SERVICE]}
    __counters__ = {'cachedBytes': 'normal'}
    __versionchecktimes__ = {'year': const.YEAR360,
     '6 months': const.MONTH30 * 6,
     '3 months': const.MONTH30 * 3,
     'month': const.MONTH30,
     'week': const.DAY * 7,
     'day': const.DAY,
     '12 hours': const.HOUR * 12,
     '6 hours': const.HOUR * 6,
     '3 hours': const.HOUR * 3,
     '2 hours': const.HOUR * 2,
     '1 hour': const.HOUR * 1,
     '30 minutes': const.MIN * 30,
     '15 minutes': const.MIN * 15,
     '5 minutes': const.MIN * 5,
     '1 minute': const.MIN,
     '30 seconds': const.SEC * 30,
     '15 seconds': const.SEC * 15,
     '5 seconds': const.SEC * 5,
     '1 second': const.SEC}
    __cachedsessionvariables__ = ['languageID']

    def __init__(self):
        if macho.mode == 'server':
            self.__dependencies__.append('DB2')
        service.Service.__init__(self)
        self.runid = blue.os.GetWallclockTime()
        self.lastChange = {}
        self.cachedObjects = {}
        self.cachedMethodCalls = {}
        self.methodCallCachingDetails = {}
        self.cachedObjectReturnStatistics = {}
        self.lastFileWriteTime = {}
        self.downloadedCachedObjects = {}

    def GetHtmlStateDetails(self, k, v, detailed):
        from carbon.common.script.util import htmlwriter
        if k == 'cachedObjects':
            if detailed:
                hd = ['ObjectID',
                 'Time Stamp',
                 'Version',
                 'Shared',
                 'NodeID',
                 'Size']
                li = []
                for ik, iv in v.iteritems():
                    l = '???'
                    if iv.pickle:
                        l = '%d' % len(iv.pickle)
                        if iv.compressed:
                            l += ' (compressed)'
                    li.append([iv.objectID,
                     FmtDateEng(iv.version[0]),
                     iv.version[1],
                     iv.shared,
                     iv.nodeID,
                     l])

                return ('Object Cache', htmlwriter.GetTable(hd, li, useFilter=True))
            else:
                return ('Object Cache', '%d entries' % len(v))
        elif k == 'cachedObjectReturnStatistics':
            if detailed:
                hd = ['ObjectID', 'Count', 'Bytes']
                li = []
                for ik, iv in v.iteritems():
                    if type(ik) == types.TupleType and len(ik) == 2 and ik[0] in sm.services:
                        ik = '%s::%s' % ik
                    li.append([htmlwriter.Swing(str(ik)), iv[0], iv[1]])

                li.sort()
                return ('Object Cache Statistics', htmlwriter.GetTable(hd, li, useFilter=True))
            else:
                totCalls = 0
                totBytes = 0
                for each in v.itervalues():
                    totCalls += each[0]
                    totBytes += each[1]

                return ('Object Cache Statistics', '%d distinct objects returned via %d calls, totalling %d bytes' % (len(v), totCalls, totBytes))

    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        self.methodCallCachingDetails = {}
        self.cachedMethodCalls = {}
        self.cachedObjects = {}

    @telemetry.ZONE_METHOD
    def LoadCache(self, ipaddress):
        ipaddress = ipaddress.lower().split(':')[0]
        self.cachePath = blue.paths.ResolvePathForWriting(u'cache:/MachoNet/%s/%d/' % (ipaddress, macho.version))
        paths = [blue.paths.ResolvePath(u'cache:/'),
         blue.paths.ResolvePathForWriting(u'cache:/MachoNet/'),
         blue.paths.ResolvePathForWriting(u'cache:/MachoNet/%s' % ipaddress),
         self.cachePath,
         self.cachePath + 'CachedMethodCalls',
         self.cachePath + 'MethodCallCachingDetails',
         self.cachePath + 'CachedObjects']
        self.methodCallCachingDetails = {}
        self.cachedMethodCalls = {}
        self.cachedObjects = {}
        for path in paths:
            try:
                os.listdir(path)
            except OSError:
                os.mkdir(path)
                sys.exc_clear()

    def RefreshCache(self):
        self.cachedMethodCalls = {}

    def __CacheIsDirty(self, what, key):
        if macho.mode == 'client':
            ret = blue.os.GetWallclockTime()
            shouldFlush = len(self.lastChange) == 0
            self.lastChange[what, key] = ret
            filename = self.cachePath + what + '/%s.cache' % self.KeyToFileName(key)
            self.downloadedCachedObjects[key] = filename
            if shouldFlush:
                uthread.worker('objectCaching::FlushCache', self.__FlushCache, True)
            return ret

    def __FlushCache(self, yieldFirst):
        if yieldFirst:
            blue.pyos.synchro.Yield()
        while self.lastChange:
            flushWhat, lastChange = self.lastChange.items()[0]
            del self.lastChange[flushWhat]
            what, key = flushWhat
            filename = self.cachePath + what + '/%s.cache' % self.KeyToFileName(key)
            if os.access(filename, os.F_OK) and not os.access(filename, os.W_OK):
                try:
                    os.chmod(filename, 666)
                except StandardError:
                    self.LogWarn('Failed to reset access priviledges on file from file system (', filename, ')')
                    sys.exc_clear()

            try:
                store = getattr(self, what)
                if key not in store:
                    try:
                        os.unlink(filename)
                        self.LogInfo('Deleted ', key, ' from file system (', filename, ')')
                    except StandardError as e:
                        self.LogWarn('Failed to delete file from file system (', filename, '):', e)
                        sys.exc_clear()

                else:
                    ob = store[key]
                    if not isinstance(ob, uthread.Semaphore):
                        blue.AtomicFileWrite(filename, blue.marshal.Save((key, ob)))
                        self.LogInfo('Wrote ', key, ' to file (', filename, ')')
                        self.lastFileWriteTime[self.__KeyFromFileName(filename)] = os.path.getmtime(filename)
            except Exception:
                log.LogException('Error while writing cached data')
                sys.exc_clear()

    def KeyToFileName(self, key):
        pickle = cPickle.dumps(key)
        checksum = binascii.crc_hqx(pickle, 0)
        return '%x' % checksum

    def __KeyFromFileName(self, fileName):
        fileName = fileName.replace('\\', '/')
        i = fileName.rindex('/')
        if i >= 0:
            fileName = fileName[i:]
        i = fileName.rindex('.')
        if i >= 0:
            fileName = fileName[0:i]
        fileName = fileName.lower()
        return fileName

    def InvalidateCachedMethodCall(self, serviceOrObjectName, method, *args):
        return self.InvalidateCachedMethodCalls([(serviceOrObjectName, method, args)])

    def InvalidateCachedMethodCalls(self, methodcalls):
        invalidate = []
        for serviceOrObjectName, method, args in methodcalls:
            si = []
            details = self.__GetMethodCallCachingDetails(None, serviceOrObjectName, method)
            if details is not None:
                if 'sessionInfo' in details:
                    si = [getattr(session, details['sessionInfo'], None)]
            k = tuple([serviceOrObjectName, method] + si + list(args))
            invalidate.append(k)

        self.InvalidateCachedObjects(invalidate)

    def __ListPartialMatch(self, l, o, pm):
        if len(pm) == len(l) and len(l) == len(o):
            for i in range(len(l)):
                if pm[i]:
                    if i < 2:
                        if type(o[i]) in (types.TupleType, types.ListType):
                            if l[i] not in o[i]:
                                return 0
                    if not l[i] == o[i]:
                        return 0

            return 1
        return 0

    def InvalidateCachedObjects(self, objectIDs, forward = 1):
        deleted = 0
        for each in objectIDs:
            if each in self.cachedMethodCalls:
                del self.cachedMethodCalls[each]
                self.__CacheIsDirty('cachedMethodCalls', each)
            if type(each) in (types.TupleType, types.ListType):
                objectID = each[0]
                version = each[1]
            else:
                objectID = each
                version = None
            if objectID in self.cachedObjects and not isinstance(self.cachedObjects[objectID], uthread.Semaphore):
                if version is None or self.__OlderVersion(self.cachedObjects[objectID].version, version):
                    del self.cachedObjects[objectID]
                    self.__CacheIsDirty('cachedObjects', objectID)

        gpcs = sm.services['machoNet']
        gpcs.GetGPCS()
        if macho.mode == 'client':
            return
        if macho.mode == 'proxy':
            for eachNodeID in sm.services['machoNet'].GetConnectedSolNodes():
                gpcs.RemoteServiceNotify(self.session, MachoAddress(nodeID=eachNodeID, service='objectCaching'), 'objectCaching', 'InvalidateCachedObjects', objectIDs, 0)

        elif forward and sm.services['machoNet'].GetConnectedProxyNodes():
            eachNodeID = random.choice(sm.services['machoNet'].GetConnectedProxyNodes())
            gpcs.RemoteServiceNotify(self.session, MachoAddress(nodeID=eachNodeID, service='objectCaching'), 'objectCaching', 'InvalidateCachedObjects', objectIDs, 0)

    def GetCachedObject(self, objectID):
        if objectID in self.cachedObjects and not isinstance(self.cachedObjects[objectID], uthread.Semaphore):
            return self.cachedObjects[objectID].object

    def GetCachedObjectVersion(self, objectID):
        if objectID in self.cachedObjects and not isinstance(self.cachedObjects[objectID], uthread.Semaphore):
            v = self.cachedObjects[objectID].version
            if v[0] is None:
                return v[1]
            else:
                return v

    def GetCachableObject(self, shared, objectID, objectVersion, nodeID):
        callTimer = basesession.CallTimer('objectCaching::GetCachableObject')
        try:
            if macho.mode == 'client':
                gpcs = sm.services['machoNet']
            else:
                gpcs = sm.services['machoNet']
                gpcs.GetGPCS()
            if objectID in self.cachedObjects and isinstance(self.cachedObjects[objectID], utilCachedObject) and macho.mode == 'proxy':
                if sm.services['machoNet'].GetTransportOfNode(self.cachedObjects[objectID].__nodeID__) is None:
                    del self.cachedObjects[objectID]
            if objectID in self.cachedObjects and isinstance(self.cachedObjects[objectID], uthread.Semaphore) or objectID not in self.cachedObjects or not isinstance(self.cachedObjects[objectID], uthread.Semaphore) and self.__OlderVersion(self.cachedObjects[objectID].version, objectVersion):
                if objectID not in self.cachedObjects or not isinstance(self.cachedObjects[objectID], uthread.Semaphore) and self.__OlderVersion(self.cachedObjects[objectID].version, objectVersion):
                    self.cachedObjects[objectID] = uthread.Semaphore(('objectCaching', objectID))
                while 1:
                    semaphore = self.cachedObjects[objectID]
                    semaphore.acquire()
                    try:
                        if not isinstance(self.cachedObjects[objectID], uthread.Semaphore):
                            self.__UpdateStatisticsGetCachableObject(objectID, objectVersion, self.cachedObjects[objectID])
                            return self.cachedObjects[objectID]
                        if macho.mode == 'client':
                            if shared:
                                if not sm.services['machoNet'].myProxyNodeID:
                                    proxyNodeID = nodeID
                                else:
                                    proxyNodeID = sm.services['machoNet'].myProxyNodeID
                                remoteObject = gpcs.RemoteServiceCall(session, proxyNodeID, 'objectCaching', 'GetCachableObject', shared, objectID, objectVersion, nodeID)
                            else:
                                remoteObject = gpcs.RemoteServiceCall(session, nodeID, 'objectCaching', 'GetCachableObject', shared, objectID, objectVersion, nodeID)
                            self.cachedObjects[objectID] = remoteObject
                            self.__CacheIsDirty('cachedObjects', objectID)
                        elif macho.mode == 'proxy':
                            remoteObject = gpcs.RemoteServiceCall(self.session, nodeID, 'objectCaching', 'GetCachableObject', shared, objectID, objectVersion, nodeID)
                            if not remoteObject.compressed and len(remoteObject.pickle) > 200:
                                try:
                                    t = ClockThis('objectCaching::compress', zlib.compress, remoteObject.pickle, 1)
                                except zlib.error as e:
                                    raise RuntimeError('Compression Failure: ' + strx(e))

                                if len(t) < len(remoteObject.pickle):
                                    remoteObject.compressed = 1
                                    remoteObject.pickle = t
                            if remoteObject.shared:
                                self.cachedObjects[objectID] = remoteObject
                                self.__CacheIsDirty('cachedObjects', objectID)
                            else:
                                del self.cachedObjects[objectID]
                                return remoteObject
                        elif macho.mode == 'server':
                            self.LogError("Some dude asked me for a cached object I just don't have, objectID=", objectID, ', objectVersion=', objectVersion, ', nodeID=', nodeID)
                            del self.cachedObjects[objectID]
                            raise RuntimeError("I don't have %s, which just don't make sense...." % repr(objectID))
                    finally:
                        semaphore.release()

                    if not isinstance(self.cachedObjects[objectID], uthread.Semaphore):
                        self.__UpdateStatisticsGetCachableObject(objectID, objectVersion, self.cachedObjects[objectID])
                        return self.cachedObjects[objectID]

            else:
                if macho.mode == 'server' and not self.cachedObjects[objectID].shared:
                    tmp = self.cachedObjects[objectID]
                    self.__UpdateStatisticsGetCachableObject(objectID, objectVersion, self.cachedObjects[objectID])
                    del self.cachedObjects[objectID]
                    return tmp
                self.__UpdateStatisticsGetCachableObject(objectID, objectVersion, self.cachedObjects[objectID])
                return self.cachedObjects[objectID]
        finally:
            callTimer.Done()

    def CacheObject(self, object):
        shared, objectID, objectVersion, nodeID, cachedObject, thePickle, compressed = object.MachoGetCachedObjectGuts()
        if objectID not in self.cachedObjects or not isinstance(self.cachedObjects[objectID], uthread.Semaphore) and self.__NewerVersion(self.cachedObjects[objectID].version, objectVersion):
            self.LogInfo('CacheObject: inserting or updating ', objectID, ' into cachedObjects')
            if cachedObject is not None or thePickle is not None:
                if objectID in self.cachedObjects and self.cachedObjects[objectID].pickle is not None:
                    self.cachedBytes.Dec(len(self.cachedObjects[objectID].pickle))
                self.cachedObjects[objectID] = CachedObject(shared, objectID, objectVersion, nodeID, cachedObject, thePickle, compressed)
                if thePickle is not None:
                    self.cachedBytes.Add(len(thePickle))
            else:
                log.LogTraceback('Unexpected CacheObject request')
            self.__CacheIsDirty('cachedObjects', objectID)

    def __NewerVersion(self, oldVersion, newVersion):
        if oldVersion[1] != newVersion[1]:
            return newVersion[0] > oldVersion[0]
        return 0

    def __OlderVersion(self, oldVersion, newVersion):
        if oldVersion[1] != newVersion[1]:
            return oldVersion[0] < newVersion[0]
        return 0

    def __GetMethodCallCachingDetails(self, serviceOrObject, serviceOrObjectName, method):
        if serviceOrObject is not None:
            exportedCalls = getattr(serviceOrObject, '__exportedcalls__', None)
            if exportedCalls is not None:
                methodInfo = exportedCalls.get(method, None)
                if methodInfo is not None:
                    if type(methodInfo) == types.DictType and 'caching' in methodInfo:
                        return methodInfo['caching']
            return
        else:
            return self.methodCallCachingDetails.get((serviceOrObjectName, method), None)

    def GetCachedMethodCallVersion(self, serviceOrObject, serviceOrObjectName, method, args):
        details = self.__GetMethodCallCachingDetails(serviceOrObject, serviceOrObjectName, method)
        if details is not None:
            si = []
            if details.get('sessionInfo', None):
                si = [getattr(session, details['sessionInfo'], None)]
            k = tuple([serviceOrObjectName, method] + si + list(args))
            if k in self.cachedMethodCalls:
                if isinstance(self.cachedMethodCalls[k]['rret'].result, utilCachedObject) and macho.mode == 'proxy':
                    if sm.services['machoNet'].GetTransportOfNode(self.cachedMethodCalls[k]['rret'].result.__nodeID__) is None:
                        del self.cachedMethodCalls[k]
                        self.LogInfo('ObjectCaching ', serviceOrObjectName, '::', method, '(', args, ') says cachable, but on dead server so go for it')
                        return 0
                return self.cachedMethodCalls[k]['version'][1]
        return 0

    def __UpdateStatisticsGetCachableObject(self, objectID, objectVersion, object):
        k = objectID
        if len(objectID) == 3 and objectID[0] == 'Method Call':
            if objectID[1] != macho.mode:
                k = '::'.join(objectID[2][:2])
            else:
                k = objectID[1:]
        k = self.__SanitizeCachingKey(k)
        if k not in self.cachedObjectReturnStatistics:
            self.cachedObjectReturnStatistics[k] = [0, 0]
        self.cachedObjectReturnStatistics[k][0] += 1
        if macho.mode != 'client':
            self.cachedObjectReturnStatistics[k][1] += object.GetSize()

    def __SanitizeCachingKey(self, k):
        if type(k) in (types.ListType, types.TupleType):
            ret = []
            for each in k:
                tmp = self.__SanitizeCachingKey(each)
                if tmp:
                    ret.append(tmp)

            if ret and ret[0] == macho.mode:
                ret = ret[1:]
            if len(ret) == 1:
                return ret[0]
            return tuple(ret)
        elif type(k) in (types.IntType, types.LongType, types.FloatType):
            return 0
        else:
            return k

    def ReturnCachedResults(self, cachable, versionCheck, throwOK, cachedResultRecord, cacheKey, cacheDetails):
        CachedMethodCalled(cacheKey, cacheDetails)
        return (cachable,
         versionCheck,
         throwOK,
         cachedResultRecord,
         cacheKey,
         cacheDetails)

    def PerformCachedMethodCall(self, serviceOrObject, serviceOrObjectName, method, args, remoteVersion = None):
        details = self.__GetMethodCallCachingDetails(serviceOrObject, serviceOrObjectName, method)
        if details is not None:
            si = []
            if details.get('sessionInfo', None):
                si = [getattr(session, details['sessionInfo'], None)]
            k = tuple([serviceOrObjectName, method] + si + list(args))
            if k in self.cachedMethodCalls:
                if isinstance(self.cachedMethodCalls[k]['rret'].result, utilCachedObject) and macho.mode == 'proxy':
                    if sm.services['machoNet'].GetTransportOfNode(self.cachedMethodCalls[k]['rret'].result.__nodeID__) is None:
                        del self.cachedMethodCalls[k]
                        self.LogInfo('ObjectCaching ', serviceOrObjectName, '::', method, '(', args, ') says cachable, but on dead server so go for it')
                        return self.ReturnCachedResults(1, 0, 0, None, k, details)
                versionCheck = self.__ShouldVersionCheck(details, self.cachedMethodCalls[k])
                if remoteVersion is None or remoteVersion == 1 or self.__OlderVersion(remoteVersion, self.cachedMethodCalls[k]['version']):
                    throwOK = 0
                else:
                    throwOK = 1
                self.cachedMethodCalls[k]['used'] = blue.os.GetWallclockTime()
                if versionCheck:
                    self.LogInfo('ObjectCaching ', serviceOrObjectName, '::', method, '(', args, ') returning a cached result that requires version checking.')
                else:
                    self.LogInfo('ObjectCaching ', serviceOrObjectName, '::', method, '(', args, ') returning a cached result')
                return self.ReturnCachedResults(1, versionCheck, throwOK, self.cachedMethodCalls[k], k, details)
            elif remoteVersion is not None and remoteVersion != 1 and self.__GetVersionCheckType(details) == 'never':
                self.LogInfo('ObjectCaching ', serviceOrObjectName, '::', method, '(', args, ') the caller seems to know the result, and we can live with that')
                return self.ReturnCachedResult(1, 0, 1, None, k, details)
            else:
                if remoteVersion is not None and remoteVersion != 1:
                    self.LogInfo('ObjectCaching ', serviceOrObjectName, '::', method, '(', args, ') is cachable, but not cached.  remoteVersion=', remoteVersion, ', details=', details, ', vc type=', self.__GetVersionCheckType(details))
                else:
                    self.LogInfo('ObjectCaching ', serviceOrObjectName, '::', method, '(', args, ') is cachable, but not cached.')
                return self.ReturnCachedResults(1, 0, 0, None, k, details)
        else:
            return self.ReturnCachedResults(0, 0, 0, None, None, None)

    if cacheSessionVariables is not None:
        __cachedsessionvariables__ = tuple(list(cacheSessionVariables) + __cachedsessionvariables__)
    else:
        __cachedsessionvariables__ = tuple(__cachedsessionvariables__)

    def CacheMethodCall(self, serviceOrObjectName, method, args, cmcr):
        k = (serviceOrObjectName, method)
        if k not in self.methodCallCachingDetails:
            self.methodCallCachingDetails[k] = cmcr.details
            self.__CacheIsDirty('methodCallCachingDetails', k)
            details = cmcr.details
        else:
            details = self.methodCallCachingDetails[serviceOrObjectName, method]
        CachedMethodCalled(k, cmcr.details)
        if self.__GetVersionCheckType(details) is not None:
            si = []
            if details.get('sessionInfo', None):
                if macho.mode != 'client' and details['sessionInfo'] not in self.__cachedsessionvariables__:
                    self.LogInfo('ObjectCaching cannot cache by sessionInfo ', details['sessionInfo'], ' on ', macho.mode)
                    return
                gsi = getattr(session, details['sessionInfo'], None)
                si = [gsi]
            ret, version = cmcr.GetResult(), cmcr.GetVersion()
            k = tuple([serviceOrObjectName, method] + si + list(args))
            used = self.__CacheIsDirty('cachedMethodCalls', k)
            self.cachedMethodCalls[k] = {'lret': ret,
             'rret': cmcr,
             'version': version,
             'used': used,
             'runid': self.runid}
            self.LogInfo('ObjectCaching ', serviceOrObjectName, '::', method, '(', args, ') cached the method call for future reference.')

    def __GetVersionCheckType(self, details):
        vc = details.get('versionCheck', 'run')
        if type(vc) == types.TupleType:
            if macho.mode == 'server':
                vc = vc[2]
            elif macho.mode == 'proxy':
                vc = vc[1]
            else:
                vc = vc[0]
        return vc

    def IsCachedOnProxy(self, details):
        if details.get('sessionInfo', None) and details.get('sessionInfo', None) not in self.__cachedsessionvariables__:
            return False
        vc = details.get('versionCheck', 'run')
        if type(vc) == types.TupleType:
            return vc[1] is not None
        return vc is not None

    def UpdateVersionCheckPeriod(self, cacheKey):
        try:
            cacheEntry = self.cachedMethodCalls.get(cacheKey, None)
            if cacheEntry is None:
                self.LogWarn('ObjectCaching unable to update validity period for cache key', cacheKey, 'key not valid')
            else:
                self.LogInfo('ObjectCaching resetting validity period for cache key', cacheKey)
                cacheEntry['version'][0] = blue.os.GetWallclockTime()
        except Exception as e:
            log.LogException('ObjectCaching unknown exception while resetting validity period')

    def __ShouldVersionCheck(self, details, info):
        vc = self.__GetVersionCheckType(details)
        now = blue.os.GetWallclockTime()
        if type(vc) in types.StringTypes:
            if vc == 'never':
                return 0
            if vc == 'always':
                return 1
            if vc in ('run', 'utcmidnight', 'utcmidnight_or_3hours'):
                if info.get('runid', 0) == self.runid:
                    if vc != 'run':
                        midnight = (info.get('runid', 0) / const.DAY + 1) * const.DAY
                        if vc == 'utcmidnight':
                            maxAge = midnight - now
                        else:
                            maxAge = min(midnight - now, 3 * const.HOUR)
                    else:
                        return 0
                else:
                    info['runid'] = self.runid
                    return 1
            else:
                maxAge = self.__versionchecktimes__[vc]
        else:
            maxAge = int(vc)
        age = now - info['version'][0]
        if maxAge <= age:
            return 1
        else:
            return 0


class CachedObject():
    __passbyvalue__ = 1

    def __init__(self, s, oid, v, n, o, p, c):
        self.version, self.object, self.nodeID, self.shared, self.pickle, self.compressed, self.objectID = (v,
         o,
         n,
         s,
         p,
         c,
         oid)

    def __getstate__(self):
        if self.pickle is not None:
            o = None
        else:
            o = self.object
        return (self.version,
         o,
         self.nodeID,
         self.shared,
         self.pickle,
         self.compressed,
         self.objectID)

    def __str__(self):
        try:
            return 'objectCaching.CachedObject(objectID=%s, version=%s, nodeID=%s, shared=%s, compressed=%s)' % (self.objectID,
             self.version,
             self.nodeID,
             self.shared,
             self.compressed)
        except:
            sys.exc_clear()
            return 'objectCaching.CachedObject(???)'

    def __setstate__(self, state):
        self.object = None
        self.version, self.object, self.nodeID, self.shared, self.pickle, self.compressed, self.objectID = state

    def GetObject(self):
        if self.object is None:
            if self.pickle is None:
                raise RuntimeError('Getting cached object contents, but both the object and the pickle are none')
            try:
                if self.compressed:
                    try:
                        dasPickle = zlib.decompress(self.pickle)
                    except zlib.error as e:
                        raise RuntimeError('Decompression Failure: ' + strx(e))

                    self.object = blue.marshal.Load(dasPickle)
                else:
                    self.object = blue.marshal.Load(self.pickle)
            except:
                sm.GetService('objectCaching').LogError('Failed to acquire object from objectCaching.CachedObject, self=', self)
                raise

        return self.object

    def CompressedPart(self):
        if not self.compressed or self.pickle is None:
            return 0
        return len(self.pickle)

    def GetSize(self):
        if self.pickle is None:
            self.pickle = blue.marshal.Save(self.object)
        return len(self.pickle)


class CachedMethodCallResult():
    __passbyvalue__ = 1

    def __init__(self, key, details, result):
        self.details = details
        if isinstance(result, utilCachedObject):
            self.result = result
            self.version = None
        elif sm.services['objectCaching'].IsCachedOnProxy(details) and macho.mode != 'client':
            self.result = utilCachedObject(1, ('Method Call', macho.mode, key), result)
            sm.services['objectCaching'].CacheObject(self.result)
            self.version = None
        else:
            self.result = blue.marshal.Save(result)
            self.version = [blue.os.GetWallclockTime(), zlib.adler32(self.result)]

    def __getstate__(self):
        return (self.details, self.result, self.version)

    def __setstate__(self, state):
        self.details, self.result, self.version = state

    def GetVersion(self):
        if isinstance(self.result, utilCachedObject):
            return list(self.result.__objectVersion__)
        return self.version

    def IsSameVersion(self, machoVersion):
        if machoVersion != 1:
            return self.GetVersion()[1] == machoVersion[1]
        return 0

    def GetResult(self):
        if isinstance(self.result, utilCachedObject):
            return self.result.GetCachedObject()
        else:
            return blue.marshal.Load(self.result)

    def __str__(self):
        try:
            if isinstance(self.result, utilCachedObject):
                return 'objectCaching.CachedMethodCallResult(version=%s, result=%s)' % (self.version, self.result)
            return 'objectCaching.CachedMethodCallResult(version=%s)' % (self.version,)
        except:
            sys.exc_clear()
            return 'objectCaching.CachedMethodCallResult(???)'


class CacheOK(StandardError):
    __passbyvalue__ = 1

    def __init__(self, value = 'CacheOK', *args):
        StandardError.__init__(self, value, *args)
