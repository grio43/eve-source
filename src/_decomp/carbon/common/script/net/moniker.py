#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\moniker.py
import weakref
import cPickle
import sys
import log
import uthread
from carbon.common.script.net import machoNet
from carbon.common.script.net.machoNetExceptions import UnMachoDestination
from carbon.common.script.sys import basesession
from carbon.common.script.sys.service import ROLE_SERVICE
from eveexceptions import UserError
allMonikers = weakref.WeakSet()

class Moniker():
    __guid__ = 'util.Moniker'
    __passbyvalue__ = 1
    __persistvar__ = ['__serviceName',
     '__nodeID',
     '__bindParams',
     '__sessionCheck']

    def __init__(self, serviceName = None, bindParams = None, nodeID = None):
        global allMonikers
        self.__serviceName = serviceName
        self.__bindParams = bindParams
        self.__nodeID = nodeID
        self.__sessionCheck = None
        self.boundObject = None
        allMonikers.add(self)

    def __del__(self):
        self.__ClearBoundObject()

    def __str__(self):
        if self.__class__ == Moniker:
            name = 'Generic'
        else:
            name = self.__class__.__name__
        args = (name,
         self.__serviceName,
         self.__nodeID,
         self.__bindParams)
        return '%s moniker on service %s, node %s, params %s' % args

    def SetSessionCheck(self, sessionCheck):
        self.__sessionCheck = sessionCheck

    def __PerformSessionCheck(self):
        if self.__sessionCheck:
            for attribute, expected in self.__sessionCheck.iteritems():
                if session:
                    current = getattr(session, attribute, None)
                else:
                    current = None
                if current != expected or not expected and current:
                    log.LogTraceback('__PerformSessionCheck:  Monikers session has changed. Traceback=', toAlertSvc=0, severity=log.LGWARN)
                    raise RuntimeError('MonikerSessionCheckFailure', {'attribute': attribute,
                     'expected': expected,
                     'current': current,
                     'serviceName': self.__serviceName,
                     'bindParams': self.__bindParams})

    def ToURLString(self):
        import binascii
        return binascii.b2a_hex(cPickle.dumps((self.__serviceName, self.__bindParams), 1))

    def FromURLString(self, s):
        import binascii
        b = binascii.a2b_hex(s)
        self.__serviceName, self.__bindParams = cPickle.loads(b)

    def __getstate__(self):
        ret = []
        for each in self.__persistvar__:
            ret.append(self.__dict__['_Moniker' + each])

        return tuple(ret)

    def __setstate__(self, state):
        for i in xrange(len(self.__persistvar__)):
            self.__dict__['_Moniker' + self.__persistvar__[i]] = state[i]

        if self.__nodeID is not None:
            sm.services['machoNet'].SetNodeOfAddress(self.__serviceName, self.__bindParams, self.__nodeID)
        self.boundObject = None
        allMonikers.add(self)

    __remobsuppmeth__ = ('RegisterObjectChangeHandler', 'UnRegisterObjectChangeHandler')

    def __getattr__(self, key):
        if key in self.__remobsuppmeth__:
            self.Bind()
            return getattr(self.boundObject, key)
        elif not key[0].isupper():
            if key.startswith('__'):
                raise AttributeError(key)
            self.Bind()
            return getattr(self.boundObject, key)
        else:
            return MonikerCallWrap(self, key)

    def __ClearBoundObject(self, disconnectDelay = 30):
        if self.boundObject is not None and isinstance(self.boundObject, basesession.ObjectConnection):
            try:
                self.boundObject.DisconnectObject(disconnectDelay)
            except AttributeError:
                pass

        self.boundObject = None

    def Bind(self, sess = None, call = None):
        localKeywords = ('machoTimeout', 'noCallThrottling')
        done = set()
        while 1:
            try:
                if self.__bindParams is None:
                    raise RuntimeError("Thou shall not use None as a Moniker's __bindParams")
                if '__semaphoreB__' not in self.__dict__:
                    self.__semaphoreB__ = uthread.Semaphore(('moniker::Bind', self.__serviceName, self.__bindParams))
                self.__semaphoreB__.acquire()
                try:
                    if not self.boundObject:
                        if self.__nodeID is None:
                            self.__ResolveImpl(sess)
                        if sess is None:
                            if session and basesession.IsInClientContext():
                                sess = session
                            elif session and session.role == ROLE_SERVICE:
                                sess = session.GetActualSession()
                            else:
                                sess = basesession.GetServiceSession('util.Moniker')
                        else:
                            sess = sess.GetActualSession()
                        if self.__nodeID == sm.GetService('machoNet').GetNodeID():
                            service = sess.ConnectToService(self.__serviceName)
                            self.boundObject = service.MachoGetObjectBoundToSession(self.__bindParams, sess)
                        else:
                            remotesvc = sess.ConnectToRemoteService(self.__serviceName, self.__nodeID)
                            self.__PerformSessionCheck()
                            if call is not None and call[2]:
                                c2 = {k:v for k, v in call[2].iteritems() if k not in localKeywords}
                                call = (call[0], call[1], c2)
                            self.boundObject, retval = remotesvc.MachoBindObject(self.__bindParams, call)
                            self.boundObject.persistantObjectID = (self.__serviceName, self.__bindParams)
                            return retval
                finally:
                    done.add((self.__serviceName, self.__bindParams))
                    self.__semaphoreB__.release()

                if call is not None:
                    return self.MonikeredCall(call, sess)
                return
            except UpdateMoniker as e:
                if (e.serviceName, e.bindParams) in done:
                    log.LogException()
                    raise RuntimeError('UpdateMoniker referred us to the same location twice', (e.serviceName, e.bindParams))
                else:
                    self.__bindParams = e.bindParams
                    self.__serviceName = e.serviceName
                    self.__nodeID = e.nodeID
                    self.Unbind()
                    sys.exc_clear()

    def MonikeredCall(self, call, sess):
        retry = 0
        while 1:
            try:
                self.__PerformSessionCheck()
                if self.boundObject is None:
                    return self.Bind(sess, call)
                try:
                    return apply(getattr(self.boundObject, call[0]), call[1], call[2])
                except UpdateMoniker as e:
                    self.__bindParams = e.bindParams
                    self.__serviceName = e.serviceName
                    self.__nodeID = e.nodeID
                    self.Unbind()
                    sys.exc_clear()

            except UserError as e:
                if e.msg == 'UnMachoDestination' and not retry:
                    retry = 1
                    self.Unresolve()
                    sys.exc_clear()
                    continue
                raise
            except UnMachoDestination:
                if not retry:
                    retry = 1
                    self.Unresolve()
                    sys.exc_clear()
                    continue
                raise

    def QuickResolve(self):
        if self.__nodeID is None and self.__serviceName in sm.services:
            self.__nodeID = self.__ResolveImpl()

    def Resolve(self, sess = None):
        return self.__ResolveImpl(sess)

    def __ResolveImpl(self, sess = None):
        if '__semaphoreR__' not in self.__dict__:
            self.__semaphoreR__ = uthread.Semaphore(('moniker::Resolve', self.__serviceName, self.__bindParams))
        self.__semaphoreR__.acquire()
        try:
            if self.__nodeID is not None:
                return self.__nodeID
            if machoNet.mode == 'client' or basesession.IsInClientContext():
                self.__nodeID = sm.services['machoNet'].GuessNodeIDFromAddress(self.__serviceName, self.__bindParams)
                if self.__nodeID is not None:
                    return self.__nodeID
                if not self.__nodeID:
                    self.__nodeID = sm.GetService('machoNet').LookupAddressCache(self.__serviceName, self.__bindParams)
                    if self.__nodeID is not None:
                        return self.__nodeID
            if sess is None:
                if session and session.role == ROLE_SERVICE:
                    sess = session.GetActualSession()
                else:
                    sess = basesession.GetServiceSession('util.Moniker')
            else:
                sess = sess.GetActualSession()
            if machoNet.mode == 'client' or basesession.IsInClientContext():
                service = sess.ConnectToRemoteService(self.__serviceName)
            else:
                service = sess.ConnectToAnyService(self.__serviceName)
            self.__nodeID = service.MachoResolveObject(self.__bindParams)
            if self.__nodeID is None:
                raise RuntimeError('Resolution failure:  ResolveObject returned None')
            if machoNet.mode == 'client' or basesession.IsInClientContext():
                sm.services['machoNet'].SetNodeOfAddress(self.__serviceName, self.__bindParams, self.__nodeID)
            return self.__nodeID
        finally:
            self.__semaphoreR__.release()

    def Unresolve(self):
        while 1:
            self.Unbind()
            if '__semaphoreR__' not in self.__dict__:
                self.__semaphoreR__ = uthread.Semaphore(('moniker::Resolve', self.__serviceName, self.__bindParams))
            self.__semaphoreR__.acquire()
            try:
                if self.boundObject is None:
                    self.__nodeID = None
                    sm.services['machoNet'].SetNodeOfAddress(self.__serviceName, self.__bindParams, None)
                    return
            finally:
                self.__semaphoreR__.release()

    def Unbind(self, disconnectDelay = 30):
        if '__semaphoreB__' not in self.__dict__:
            self.__semaphoreB__ = uthread.Semaphore(('moniker::Bind', self.__serviceName, self.__bindParams))
        self.__semaphoreB__.acquire()
        try:
            self.__ClearBoundObject(disconnectDelay)
        finally:
            self.__semaphoreB__.release()

    def GetNodeID(self):
        if self.__nodeID is None:
            self.__ResolveImpl()
        return self.__nodeID

    def GetSelfLocal(self):
        if self.GetNodeID() == sm.services['machoNet'].GetNodeID():
            self.Bind()
            return self.boundObject.__object__
        raise RuntimeError('You are not local %d != %d' % (self.GetNodeID(), sm.services['machoNet'].GetNodeID()))


class MonikerCallWrap():

    def __init__(self, moniker, key):
        self.moniker = moniker
        self.key = key
        if key[0] != key[0].upper():
            raise RuntimeError("This moniker has no attribute '%s'. Moniker: %s" % (key, moniker))

    def __call__(self, *args, **kw):
        try:
            return self.moniker.MonikeredCall((self.key, args, kw), None)
        finally:
            self.__dict__.clear()


class UpdateMoniker(StandardError):
    __passbyvalue__ = 1

    def __init__(self, serviceName = None, bindParams = None, nodeID = None):
        Exception.__init__(self, 'Update')
        self.serviceName = serviceName
        self.nodeID = nodeID
        self.bindParams = bindParams
