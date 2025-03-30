#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\locks\__init__.py
import blue
import sys
import stackless
import traceback2 as traceback
import re
import weakref
import contextlib
import heapq
import logmodule as log
import functools
import copy
from itertools import chain
from collections import defaultdict, deque
from ccpProfile import TimedFunction
FORMAT = traceback.FORMAT_LOGSRV | traceback.FORMAT_SINGLE

def Startup(new):
    StartEventQueue(new)


def ChannelTasklets(channel):
    result = []
    t = first = channel.queue
    while t:
        result.append(t)
        t = t.next
        if t is first:
            break

    return result


class LockInheritanceMap(object):

    def __init__(self):
        self.inherits = {}

    def AddInheritance(self, parent, child):
        if child in self.inherits:
            raise ValueError('%r already inherits locks' % child)
        parents = (parent,)
        try:
            parents += self.inherits[parent]
        except KeyError:
            pass

        self.inherits[child] = parents

    def RemoveInheritance(self, child):
        del self.inherits[child]

    def Inherits(self, parent, child = None):
        if child is None:
            child = stackless.getcurrent()
        try:
            return child is parent or parent in self.inherits[child]
        except KeyError:
            return False

    def GetInheritances(self):
        return [ (c, p[0]) for c, p in self.inherits.iteritems() ]

    @contextlib.contextmanager
    def Inheritance(self, parent):
        child = stackless.getcurrent()
        self.AddInheritance(parent, child)
        try:
            yield
        finally:
            self.RemoveInheritance(child)


_inheritance = LockInheritanceMap()
Inheritance = _inheritance.Inheritance
Inherits = _inheritance.Inherits

class EventQueue(object):

    def __init__(self):
        self.queue = []
        self.fuzz = 0.001

    @staticmethod
    def clock():
        return blue.os.GetWallclockTimeNow() * 1e-07

    def push(self, when, what):
        heapq.heappush(self.queue, (when, what))
        if self.queue[0][0] == when:
            delta = max(0.0, when - self.clock())
            blue.pyos.NextScheduledEvent(int(delta * 1000.0))

    def pump(self):
        if not self.queue:
            return
        now = self.clock() + self.fuzz
        batch = []
        while self.queue and self.queue[0][0] <= now:
            batch.append(heapq.heappop(self.queue))

        for when, what in batch:
            what()

    def next_time(self):
        if self.queue:
            return self.queue[0][0]

    def next_delay(self):
        if self.queue:
            return max(0.0, self.queue[0][0] - self.clock())


eventQueue = EventQueue()

def StartEventQueue(new):

    def Loop():
        while True:
            try:
                eventQueue.pump()
                t = eventQueue.next_delay()
                if t is not None:
                    blue.pyos.NextScheduledEvent(int(t * 1000))
            except StandardError:
                log.LogException()
                sys.exc_clear()

            blue.pyos.synchro.Yield()

    new(Loop).context = 'EventQueueLoop'


class LockTimeout(StopIteration):
    pass


def WaitWithTimeout(channel, timeout):
    waiting = True
    me = stackless.getcurrent()

    def wakeup():
        if waiting:
            me.raise_exception(LockTimeout)

    eventQueue.push(eventQueue.clock() + timeout, wakeup)
    try:
        channel.receive()
    except LockTimeout:
        return True
    finally:
        waiting = False

    return False


class ContextMixin(object):

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc, val, tb):
        try:
            self.release()
        except StandardError:
            if exc:
                log.LogException('supressed error in ContextMixin.__exit__')
            else:
                raise


class LockMixin(ContextMixin):

    def LockedFor(self):
        if self.lockedWhen:
            return (blue.os.GetWallclockTime() - self.lockedWhen) * 1e-07
        return -1.0

    def __repr__(self):
        return '<%s %r, t=%f at %#x>' % (self.__class__.__name__,
         self.name,
         self.LockedFor(),
         id(self))


class FifoLock(LockMixin):
    __guid__ = 'locks.FifoLock'

    def __init__(self, name = 'noname'):
        self.name = name
        self.waiting = stackless.channel()
        self.waiting.preference = 1
        self.owning = None
        self.lockedWhen = None
        lockManager.Register(self)

    def acquire(self, blocking = True):
        if self.owning:
            if not blocking:
                return False
            try:
                self.waiting.receive()
            except:
                self._except_release()
                raise

        else:
            self.owning = stackless.getcurrent()
            self.lockedWhen = blue.os.GetTime()
        return True

    def _except_release(self):
        try:
            if self.owning is stackless.getcurrent():
                self.release()
        except StandardError:
            pass

    def release(self):
        self.owning = None
        self.lockedWhen = None
        if self.waiting.balance < 0:
            self.owning = self.waiting.queue
            self.lockedWhen = blue.os.GetTime()
            self.waiting.send(None)

    def IsCool(self):
        return self.owning is None

    def HoldingTasklets(self):
        if self.owning:
            return [self.owning]
        return []

    def WaitingTasklets(self):
        return ChannelTasklets(self.waiting)

    def LockedAt(self):
        return self.lockedWhen

    def Unblock(self):
        self.release()


class Lock(LockMixin):

    def __init__(self, name = 'noname'):
        self.name = name
        self.waiting = stackless.channel()
        self.waiting.preference = 1
        self.nWaiting = 0
        self.owning = []
        self.lockedWhen = None
        lockManager.Register(self)

    def acquire(self, blocking = 1):
        if not blocking:
            return self.try_acquire()
        while not self.try_acquire():
            try:
                self.nWaiting += 1
                try:
                    self.waiting.receive()
                finally:
                    self.nWaiting -= 1

            except:
                self._safe_pump()
                raise

        return True

    def try_acquire(self):
        if not self.owning:
            self.lockedWhen = blue.os.GetWallclockTime()
            self.owning.append(stackless.getcurrent())
            return True
        return False

    def release(self):
        if not self.owning:
            raise RuntimeError, 'invalid unlock'
        self.owning.pop()
        if not self.owning:
            self.lockedWhen = None
        self._pump()

    def _release_save(self):
        r = self.owning
        self.owning = []
        self.lockedWhen = None
        self._pump()
        return r

    def _acquire_restore(self, state):
        self.acquire()
        self.owning = state

    def _pump(self):
        if not self.owning and self.waiting.balance:
            self.waiting.send(None)

    def _safe_pump(self):
        try:
            self._pump()
        except StandardError:
            pass

    def _is_owned(self):
        return self.owning and self.owning[0] is stackless.getcurrent()

    def IsCool(self):
        return not (self.owning or self.nWaiting)

    def LockedAt(self):
        return self.lockedWhen

    def HoldingTasklets(self):
        return self.owning[:]

    def WaitingTasklets(self):
        return ChannelTasklets(self.waiting)

    def Unblock(self):
        self._release_save()


class RLock(Lock):

    def try_acquire(self):
        current = stackless.getcurrent()
        if not self.owning or Inherits(self.owning[0], current):
            if not self.owning:
                self.lockedWhen = blue.os.GetWallclockTime()
            self.owning.append(current)
            return True
        return False

    def _is_owned(self):
        return self.owning and Inherits(self.owning[0], stackless.getcurrent())


class Condition(ContextMixin):

    def __init__(self, lock = None, name = 'noname'):
        if not lock:
            lock = RLock(name)
        self.lock = lock
        self.name = name
        self.waiting = stackless.channel()
        self.waiting.preference = 1
        self.acquire = lock.acquire
        self.try_acquire = lock.try_acquire
        self.release = lock.release
        try:
            self._release_save = lock._release_save
            self._acquire_restore = lock._acquire_restore
        except AttributeError:
            pass

        try:
            self._is_owned = lock._is_owned
        except AttributeError:
            pass

    def __repr__(self):
        return '<Condition %r, %r, %d at %#x)>' % (self.name,
         self.lock,
         -self.waiting.balance,
         id(self))

    def _release_save(self):
        self.lock.release()

    def _acquire_restore(self, x):
        self.lock.acquire()

    def _is_owned(self):
        if self.lock.acquire(0):
            self.lock.release()
            return False
        else:
            return True

    def wait(self, timeout = None):
        if not self._is_owned():
            raise RuntimeError, 'must have lock when waiting'
        saved = self._release_save()
        try:
            if timeout is None:
                self.waiting.receive()
            else:
                WaitWithTimeout(self.waiting, timeout)
        finally:
            self._acquire_restore(saved)

    def notify(self):
        if not self._is_owned():
            raise RuntimeError, 'must have lock when waiting'
        if self.waiting.balance:
            self.waiting.send(None)

    def notify_all(self):
        if not self._is_owned():
            raise RuntimeError, 'must have lock when waiting'
        for i in xrange(-self.waiting.balance):
            self.waiting.send(None)

    notifyAll = notify_all

    def Unblock(self):
        for i in xrange(-self.waiting.balance):
            self.waiting.send(None)


class Event(object):

    def __init__(self, name = 'none'):
        self.waiting = stackless.channel()
        self.waiting.preference = 1
        self.name = name
        self.state = False

    def is_set(self):
        return self.state

    isSet = is_set

    def set(self):
        self.state = True
        for i in xrange(-self.waiting.balance):
            self.waiting.send(None)

    def clear(self):
        self.state = False

    def wait(self, timeout = None):
        if not self.state:
            if timeout is None:
                self.waiting.receive()
            else:
                WaitWithTimeout(self.waiting, timeout)


class RWLock(LockMixin):

    def __init__(self, lockName = 'noname'):
        self.name = lockName
        self.rchan = stackless.channel()
        self.wchan = stackless.channel()
        self.rchan.preference = self.wchan.preference = 1
        self.nWaiting = [0, 0]
        self.state = 0
        self.owning = []
        self.lockedWhen = None
        lockManager.Register(self)

    def __repr__(self):
        return '<RWLock %r held by %r, state:%d, rdwait:%d, wrwait:%d, t:%f at %#x>' % (self.name,
         self.owning,
         self.state,
         -self.rchan.balance,
         -self.wchan.balance,
         self.LockedFor(),
         id(self))

    def try_acquire(self):
        current = stackless.getcurrent()
        if self.state == 0 or self.state < 0 and Inherits(self.owning[0], current):
            self.state -= 1
            self.owning.append(current)
            if not self.lockedWhen:
                self.lockedWhen = blue.os.GetWallclockTime()
            return True
        return False

    def try_acquire_read(self):
        if self.state < 0:
            return self.try_acquire()
        current = stackless.getcurrent()
        if not self.nWaiting[1]:
            ok = True
        else:
            for owning in self.owning:
                if Inherits(owning, current):
                    ok = True
                    break
            else:
                ok = False

        if ok:
            self.state += 1
            self.owning.append(current)
            if not self.lockedWhen:
                self.lockedWhen = blue.os.GetWallclockTime()
            return True
        return False

    def acquire(self, blocking = True):
        while not self.try_acquire():
            if not blocking:
                return False
            self._wait(self.wchan, 1)

        return True

    def acquire_read(self, blocking = True):
        while not self.try_acquire_read():
            if not blocking:
                return False
            self._wait(self.rchan, 0)

    def _wait(self, channel, i):
        try:
            self.nWaiting[i] += 1
            try:
                channel.receive()
            finally:
                self.nWaiting[i] -= 1

        except:
            self._safe_pump()
            raise

    def _safe_pump(self):
        try:
            self._pump()
        except StandardError:
            pass

    def release(self):
        try:
            self.owning.remove(stackless.getcurrent())
        except ValueError:
            raise RuntimeError('Trying to release a rwlock without a matching lock!')

        if self.state > 0:
            self.state -= 1
        else:
            self.state += 1
        if self.state == 0:
            self.lockedWhen = None
        self._pump()

    def _pump(self):
        while True:
            if self.nWaiting[1]:
                if self.state == 0 and -self.wchan.balance == self.nWaiting[1]:
                    self.wchan.send(None)
            elif self.state >= 0 and self.rchan.balance:
                self.rchan.send(None)
                continue
            break

    class LockContext(object):

        def __init__(self, lock):
            self.lock = lock

        def __enter__(self):
            self.lock.acquire_read()

        def __exit__(self, e, v, tb):
            self.lock.release()

    def acquired_read(self):
        return self.LockContext(self)

    def acquired(self):
        return self

    def _is_owned(self):
        return self.state < 0 and Inherits(self.owning[0])

    def _release_save(self):
        r = self.owning
        self.owning = []
        self.state = 0
        self.lockedWhen = None
        self._pump()
        return r

    def _acquire_restore(self, x):
        self.acquire()
        self.owning = x
        self.state = -len(x)

    def IsCool(self):
        return self.state == 0 and self.nWaiting[0] == 0 and self.nWaiting[1] == 0

    def WaitingTasklets(self):
        return ChannelTasklets(self.rchan) + ChannelTasklets(self.wchan)

    def HoldingTasklets(self):
        return self.owning[:]

    def LockedAt(self):
        return self.lockedWhen

    def Unblock(self):
        self._release_save()


def SingletonCall(f):
    mapping = {}

    @functools.wraps(f)
    def helper(*args):
        key = args
        c = mapping.get(key, None)
        if c:
            return c.receive()
        c = stackless.channel()
        c.preference = 0
        mapping[key] = c
        try:
            r = f(*args)
            del mapping[key]
            for i in xrange(-c.balance):
                c.send(r)

            return r
        except:
            del mapping[key]
            e, v = sys.exc_info()[:2]
            for i in xrange(-c.balance):
                c.send_exception(e, v)

            raise

    return helper


class GraphNode(object):

    def __init__(self):
        self.e_in = set()
        self.e_out = set()


class Graph(object):

    def __init__(self):
        self.nodes = defaultdict(GraphNode)

    def __getitem__(self, key):
        node = self.nodes[key]
        node.key = key
        return node

    def __len__(self):
        return len(self.nodes)

    def AddEdge(self, a, b):
        self[a].e_out.add(b)
        self[b].e_in.add(a)

    def PathsFrom(self, node):
        result = []
        stack = []

        def descend(o):
            r = o in stack
            stack.append(o)
            children = self.nodes[o].e_out
            if children and not r:
                for n in children:
                    descend(n)

            else:
                result.append(stack[:])
            stack.pop(-1)

        descend(node)
        descend = None
        return result

    def CyclesFrom(self, node):
        result = []
        stack = []

        def descend(o):
            if o in stack:
                result.append(stack[stack.index(o):])
                return
            neighbours = self.nodes[o].e_out
            if not neighbours:
                return
            stack.append(o)
            for n in neighbours:
                descend(n)

            stack.pop(-1)

        descend(node)
        descend = None
        return result

    def FindRoots(self):
        result = []
        for i, e in self.nodes.iteritems():
            if not e.e_in:
                result.append(i)

        return result

    @TimedFunction('Graph::FindCycles')
    def FindCycles(self):
        cycles = []
        for SCC in self.Tarjan_SCC():
            if len(SCC) <= 1:
                continue
            startnode = min(SCC, key=lambda n: n.index)
            cycles += self.CyclesFrom(startnode.key)

        return cycles

    def Tarjan_SCC(self):

        class idx:
            i = 0

        S = deque()
        result = []

        def strongconnect(node):
            node.index = idx.i
            node.lowlink = idx.i
            idx.i += 1
            S.append(node)
            node.onStack = True
            for nextnode in node.e_out:
                w = self.nodes[nextnode]
                if not hasattr(w, 'index'):
                    strongconnect(w)
                    node.lowlink = min(node.lowlink, w.lowlink)
                elif w.onStack:
                    node.lowlink = min(node.lowlink, w.index)

            if node.lowlink == node.index:
                strongcomponent = []
                while True:
                    successor = S.pop()
                    successor.onStack = False
                    strongcomponent.append(successor)
                    if successor == node:
                        break

                result.append(strongcomponent)

        for k, n in self.nodes.iteritems():
            if not hasattr(n, 'index'):
                strongconnect(n)

        return result


@TimedFunction('Locks::GetDependencyGraph')
def GetDependencyGraph():
    g = Graph()
    for l in lockManager.GetLocks():
        time = l.LockedFor()
        if time >= 0:
            g[l].time = time
        for t in l.HoldingTasklets():
            g.AddEdge(t, l)

        for t in l.WaitingTasklets():
            g.AddEdge(l, t)

    for c, p in _inheritance.GetInheritances():
        g.AddEdge(c, p)

    return g


sem_re = re.compile('Semaphore (.+) has been held up')

def GetDependencyGraphFromConflictLog(text):
    lines = text.splitlines()
    lockCnt = 0
    locks = []
    g = Graph()
    for l in lines:
        l = l.strip()
        if not l:
            continue
        m = sem_re.search(l)
        if m:
            name = m.group(1) + str(lockCnt)
            lockCnt += 1
            currentLock = name
            locks.append(name)
        elif 'waiting thread' in l:
            where = l.index('<')
            name = l[where:]
            g.AddEdge(currentLock, name)
        elif 'holding thread' in l:
            where = l.index('<')
            name = l[where:]
            g.AddEdge(name, currentLock)

    return g


@TimedFunction('Locks::LockCycleReport')
def LockCycleReport(graph = None, out = None, timeLimit = None, pathLimit = 10):
    if not graph:
        g = GetDependencyGraph()
    else:
        g = graph
    if out is None:
        out = sys.stdout
    cycles = g.FindCycles()
    roots = g.FindRoots()

    def PathTime(graphpath):
        return sum((getattr(g[node], 'time', 0) for node in graphpath))

    npaths = 0
    paths = []
    for r in roots:
        p = g.PathsFrom(r)
        npaths += len(p)
        longest = max(p, key=lambda pl: len(pl))
        t = PathTime(longest)
        if timeLimit is None or t is None or t > timeLimit:
            paths.append((longest, t))

    if not cycles and not paths:
        return False
    paths.sort(key=lambda pa: (pa[1], len(pa[0])), reverse=True)
    if pathLimit:
        del paths[pathLimit:]
    players = []
    seen = set()
    nc = 0
    mapping = {}
    for p in chain(cycles, (p[0] for p in paths)):
        for n in p:
            if n not in seen:
                seen.add(n)
                players.append(n)
                mapping[n] = 'N%d' % nc
                nc += 1

    print >> out, 'Found %s cycles' % len(cycles)
    for i, cycle in enumerate(cycles):
        print >> out, '%2d: ' % i,
        for e in cycle:
            print >> out, '%s -> ' % mapping[e],

        print >> out

    print >> out, 'Found %s roots in %s paths (showing longest path for each root)' % (len(paths), npaths)
    for i, pathentry in enumerate(paths):
        path = pathentry[0]
        time = pathentry[1]
        if time is not None:
            print >> out, '%2d, t=%4.0fs: ' % (i, time),
        else:
            print >> out, '%2d,        : ' % (i,),
        for e in path[:-1]:
            print >> out, '%s -> ' % mapping[e],

        print >> out, '%s' % mapping[path[-1]]

    minimum = 0
    if cycles:
        minimum = max(minimum, len(cycles[0]))
    if paths:
        minimum = max(minimum, len(paths[0][0]))
    maximum = max(minimum, 10)
    print >> out, 'where:'
    for v in players[0:maximum]:
        k = mapping[v]
        print >> out, ' %3s = %r' % (k, v),
        if stackless and isinstance(v, stackless.tasklet):
            print >> out, ':'
            try:
                if not v.alive:
                    print >> out, 'dead'
                elif v.frame:
                    for s in traceback.format_list(traceback.extract_stack(v.frame, 40), format=FORMAT):
                        print >> out, '       ' + s,

                else:
                    print >> out, 'no frame'
            except StandardError:
                pass

        elif hasattr(v, 'WaitingTasklets') and hasattr(v, 'HoldingTasklets'):
            print >> out, '( blocks tasklets', [ '0x%x' % id(t) for t in v.WaitingTasklets() ], 'and held by', [ '0x%x' % id(t) for t in v.HoldingTasklets() ], ')'

    return True


def OldLockReport(threshold = None, out = None):
    if out is None:
        out = sys.stdout
    now = blue.os.GetWallclockTime()
    result = False
    for each in lockManager.GetLocks():
        if threshold is None or each.LockedAt() and (now - each.LockedAt()) * 1e-07 >= threshold:
            waiting = each.WaitingTasklets()
            if not waiting:
                continue
            result = True
            holding = each.HoldingTasklets()
            if each.LockedAt():
                dt = (now - each.LockedAt()) * 1e-07
            else:
                dt = -1
            print >> out, 'Semaphore %r has been held up for a long time (%ss).' % (each, dt)
            for t in waiting:
                print >> out, 'waiting thread: %r' % t
                if False:
                    try:
                        for s in traceback.format_list(traceback.extract_stack(t.frame, 40)):
                            print >> out, s,

                    except StandardError:
                        sys.exc_clear()

            for t in holding:
                print >> out, 'holding thread: %r' % t
                try:
                    for s in traceback.format_list(traceback.extract_stack(t.frame, 40)):
                        print >> out, s,

                except StandardError:
                    sys.exc_clear()

                if t.paused:
                    print >> out, "Holding thread is paused, let's restart it!!!  Oh, and tell Kristjan"
                    try:
                        t.insert()
                        print >> out, 'unpaused.'
                    except StandardError:
                        sys.exc_clear()

                elif not t.alive:
                    print >> out, 'Holding thread is dead.  Just release the semaphore and tell Kristjan'
                    if hasattr(each, 'Unblock'):
                        each.Unblock()
                        print >> out, 'semaphore released'
                    else:
                        try:
                            each.release(True)
                            print >> out, 'semaphore released'
                        except StandardError:
                            sys.exc_clear()

    return result


class LockManager(object):

    def __init__(self):
        self.locks = weakref.WeakKeyDictionary()
        self.locksByName = weakref.WeakValueDictionary()

    def Register(self, lock):
        self.locks[lock] = None

    def GetLocks(self):
        return self.locks.keys()

    def TempLock(self, key, lockClass = RLock):
        lock = self.locksByName.get(key, None)
        if lock is None:
            lock = lockClass(str(key))
            self.locksByName[key] = lock
        return lock


lockManager = LockManager()
Register = lockManager.Register
GetLocks = lockManager.GetLocks
TempLock = lockManager.TempLock
exports = {'locks.GetDependencyGraphFromConflictLog': GetDependencyGraphFromConflictLog,
 'locks.GetDependencyGraph': GetDependencyGraph,
 'locks.LockCycleReport': LockCycleReport,
 'locks.OldLockReport': OldLockReport,
 'locks.Register': Register,
 'locks.GetLocks': GetLocks,
 'locks.TempLock': TempLock,
 'locks.Inheritance': Inheritance,
 'locks.Inherits': Inherits,
 'locks.Lock': Lock,
 'locks.RLock': RLock,
 'locks.RWLock': RWLock,
 'locks.Condition': Condition,
 'locks.Event': Event,
 'locks.FifoLock': FifoLock,
 'locks.eventQueue': eventQueue,
 'locks.Startup': Startup,
 'locks.SingletonCall': SingletonCall}
