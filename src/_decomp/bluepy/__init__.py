#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\bluepy\__init__.py
import atexit
import blue
import contextlib
import re
import stackless
import sys
import traceback
import weakref
import utillib as util
import ccpProfile
import datetime
STACKLESS_TRACING_ENABLED_KEY = 'stackless_tracing_enabled'
tasklet_id = 0

class TaskletExt(stackless.tasklet):
    __slots__ = ['context',
     'localStorage',
     'storedContext',
     'startTime',
     'endTime',
     'runTime',
     'tasklet_id',
     'origin_traceback',
     'highlighted',
     'method_name',
     'module_name',
     'file_name',
     'line_number',
     'parent_callsite',
     'tracer',
     'trace_id',
     'parent_id',
     'sampled',
     'ingress_id',
     'sample_rate',
     'creation_datetime']

    @staticmethod
    def GetWrapper(method):
        if not callable(method):
            raise TypeError('TaskletExt::__new__ argument "method" must be callable.')

        def CallWrapper(*args, **kwds):
            current = stackless.getcurrent()
            current.startTime = blue.os.GetWallclockTimeNow()
            oldtimer = PushTimer(current.context)
            exc = None
            with tasklet_trace(current):
                try:
                    try:
                        return method(*args, **kwds)
                    except TaskletExit as e:
                        pass
                    except SystemExit as e:
                        import logmodule as log
                        log.general.Log('system %s exiting with %r' % (stackless.getcurrent(), e), log.LGINFO)
                    except Exception:
                        import logmodule as log
                        log.LogException('Unhandled exception in %r' % stackless.getcurrent())

                    return
                except:
                    traceback.print_exc()
                    if exc:
                        traceback.print_exception(exc[0], exc[1], exc[2])
                finally:
                    exc = None
                    PopTimer(oldtimer)
                    current.endTime = blue.os.GetWallclockTimeNow()

        return CallWrapper

    def __new__(cls, ctx, method = None, stackless_tracing_enabled = True):
        global tasklet_id
        tid = tasklet_id
        tasklet_id += 1
        if method:
            t = stackless.tasklet.__new__(cls, cls.GetWrapper(method))
        else:
            t = stackless.tasklet.__new__(cls)
        t.creation_datetime = datetime.datetime.utcnow()
        c = stackless.getcurrent()
        ls = getattr(c, 'localStorage', None)
        if ls is None:
            t.localStorage = {}
        else:
            t.localStorage = dict(ls)
        t.storedContext = t.context = ctx
        t.method_name = getattr(method, '__name__', 'unknown_method')
        t.module_name = getattr(method, '__module__', 'unknown_module')
        try:
            t.file_name = method.__code__.co_filename
            t.line_number = method.__code__.co_firstlineno
        except AttributeError:
            t.file_name = 'unknown_file'
            t.line_number = 0

        parent_module_name = getattr(c, 'module_name', 'unknown_parent_module')
        parent_method_name = getattr(c, 'method_name', 'unknown_parent_method')
        t.parent_callsite = ('{}.{}'.format(parent_module_name, parent_method_name),)
        if stackless_tracing_enabled:
            cls.copy_tracer_and_state(c, t)
        t.runTime = 0.0
        t.tasklet_id = tid
        t.highlighted = False
        tasklets[t] = True
        return t

    @staticmethod
    def copy_tracer_and_state(old, new):
        trace_context_slots = ['trace_id',
         'parent_id',
         'sampled',
         'ingress_id',
         'sample_rate']
        for trace_slot in trace_context_slots:
            setattr(new, trace_slot, getattr(old, trace_slot, None))

        tracer = getattr(old, 'tracer', None)
        if tracer is not None:
            setattr(new, 'tracer', tracer.clone())

    def bind(self, callableObject):
        return stackless.tasklet.bind(self, self.CallWrapper(callableObject))

    def __repr__(self):
        abps = [ getattr(self, attr) for attr in ['alive',
         'blocked',
         'paused',
         'scheduled'] ]
        abps = ''.join((str(int(flag)) for flag in abps))
        return '<TaskletExt object at 0x%x, abps=%s, ctxt=%r>' % (id(self), abps, getattr(self, 'storedContext', None))

    def __reduce__(self):
        return (str, ("__reduce__()'d " + repr(self),))

    def PushTimer(self, ctxt):
        blue.pyos.taskletTimer.EnterTasklet(ctxt)

    def PopTimer(self, ctxt):
        blue.pyos.taskletTimer.ReturnFromTasklet(ctxt)

    def GetCurrent(self):
        blue.pyos.taskletTimer.GetCurrent()

    def GetWallclockTime(self):
        return (blue.os.GetWallclockTimeNow() - self.startTime) * 1e-07

    def GetRunTime(self):
        return self.runTime + blue.pyos.GetTimeSinceSwitch()


tasklets = weakref.WeakKeyDictionary()
ctxtfilter = re.compile('at 0x[0-9A-F]+')

def tasklet_trace(t):
    tracer = getattr(t, 'tracer', None)
    if tracer is None:
        return no_tasklet_tracer()
    return tracer.get_tasklet_tracer(t)


@contextlib.contextmanager
def no_tasklet_tracer():
    yield


def tracing_enabled(**kwargs):
    if STACKLESS_TRACING_ENABLED_KEY not in kwargs.keys():
        return (True, kwargs)
    stackless_tracing_enabled = kwargs[STACKLESS_TRACING_ENABLED_KEY]
    del kwargs[STACKLESS_TRACING_ENABLED_KEY]
    return (stackless_tracing_enabled, kwargs)


def CreateTaskletExt(func, *args, **kw):
    ctx = ctxtfilter.sub('', repr(func))
    ctx = blue.pyos.taskletTimer.GetCurrent().split('^')[-1] + '^' + ctx
    stackless_tracing_enabled, kw = tracing_enabled(**kw)
    t = TaskletExt(ctx, func, stackless_tracing_enabled=stackless_tracing_enabled)
    t(*args, **kw)
    return t


def Shutdown(exitprocs):

    def RunAll():
        stackless.getcurrent().block_trap = True
        for proc in exitprocs:
            try:
                proc()
            except Exception:
                import logmodule as log
                log.LogException('exitproc ' + repr(proc), toAlertSvc=False)
                sys.exc_clear()

    if exitprocs:
        TaskletExt('Shutdown', RunAll)()
        intr = stackless.run(1000000)
        if intr:
            log.general.Log('ExitProcs interrupted at tasklet ' + repr(intr), log.LGERR)
    GetTaskletDump(True)
    if len(tasklets):
        KillTasklets()
        GetTaskletDump(True)


def GetTaskletDump(logIt = True):
    import logmodule as log
    lines = []
    lines.append('GetTaskletDump:  %s TaskletExt objects alive' % len(tasklets))
    lines.append('[context] - [code] - [stack depth] - [creation context]')
    for t in tasklets.keys():
        try:
            if t.frame:
                stack = traceback.extract_stack(t.frame, 1)
                depth = len(stack)
                f = stack[-1]
                code = '%s(%s)' % (f[0], f[1])
            else:
                code, depth = ('<no frame>', 0)
        except Exception as e:
            code, depth = repr(e), 0

        ctx = (getattr(t, 'context', '(unknown)'),)
        sctx = getattr(t, 'storedContext', '(unknown)')
        l = '%s - %s - %s - %s' % (sctx,
         code,
         depth,
         ctx)
        lines.append(l)

    lines.append('End TaskletDump')
    if logIt:
        for l in lines:
            log.general.Log(l, log.LGINFO)

    return '\n'.join(lines) + '\n'


def KillTasklets():
    t = TaskletExt('KillTasklets', KillTasklets_)
    t()
    t.run()


def KillTasklets_():
    import logmodule as log
    log.general.Log('killing all %s TaskletExt objects' % len(tasklets), log.LGINFO)
    for i in range(3):
        for t in tasklets.keys():
            if t is stackless.getcurrent():
                continue
            try:
                if t.frame:
                    log.general.Log('killing %s' % t, log.LGINFO)
                    t.kill()
                else:
                    log.general.Log('ignoring %r, no frame.' % t, log.LGINFO)
            except RuntimeError as e:
                log.general.Log("couldn't kill %r: %r" % (t, e), log.LGWARN)

    log.general.Log('killing done', log.LGINFO)


class PyResFile(object):
    __slots__ = ['rf',
     'name',
     'mode',
     'softspace']

    def __init__(self, path, mode = 'r', bufsize = -1):
        self.rf = blue.ResFile()
        self.mode = mode
        self.name = path
        if 'w' in mode:
            try:
                self.rf.Create(path)
            except:
                raise IOError, 'could not create ' + path

        else:
            readonly = 'a' not in mode and '+' not in mode
            try:
                self.rf.OpenAlways(path, readonly, mode)
            except:
                raise IOError, 'could not open ' + path

    def read(self, count = 0):
        try:
            return self.rf.read(count)
        except:
            raise IOError, 'could not read %d bytes from %s' % (count, self.rf.filename)

    def write(self, data):
        raise NotImplemented

    def readline(self, size = 0):
        raise NotImplemented

    def readlines(self, sizehint = 0):
        r = []
        while True:
            l = self.readline()
            if not l:
                return r
            r.append(l)

    def writelines(self, iterable):
        for i in iterable:
            self.write(i)

    def seek(self, where, whence = 0):
        if whence == 1:
            where += self.rf.pos
        elif whence == 2:
            where += self.rf.size
        try:
            self.rf.Seek(where)
        except:
            raise IOError, 'could not seek to pos %d in %s' % (where, self.rf.filename)

    def tell(self):
        return self.rf.pos

    def truncate(self, size = None):
        if size is None:
            size = self.rf.pos
        try:
            self.rf.SetSize(size)
        except:
            raise IOError, 'could not trucated file %s to %d bytes' % (self.rf.filename, size)

    def flush():
        pass

    def isatty():
        return False

    def close(self):
        self.rf.close()
        del self.rf

    def next(self):
        l = self.readline()
        if l:
            return l
        raise StopIteration

    def __iter__(self):
        return self


PushTimer = ccpProfile.PushTimer
PopTimer = ccpProfile.PopTimer
CurrentTimer = ccpProfile.CurrentTimer
EnterTasklet = ccpProfile.EnterTasklet
ReturnFromTasklet = ccpProfile.ReturnFromTasklet
Timer = ccpProfile.Timer
TimerPush = ccpProfile.TimerPush
TimedFunction = ccpProfile.TimedFunction
blue.TaskletExt = TaskletExt
blue.tasklets = tasklets
stackless.taskletext = TaskletExt

def GetBlueInfo(numMinutes = None, isYield = True):
    if numMinutes:
        trend = blue.pyos.cpuUsage[-numMinutes * 60 / 10:]
    else:
        trend = blue.pyos.cpuUsage[:]
    mega = 1.0 / 1024.0 / 1024.0
    ret = util.KeyVal()
    ret.memData = []
    ret.pymemData = []
    ret.bluememData = []
    ret.othermemData = []
    ret.threadCpuData = []
    ret.procCpuData = []
    ret.threadKerData = []
    ret.procKerData = []
    ret.timeData = []
    ret.latenessData = []
    ret.schedData = []
    latenessBase = 100000000.0
    if len(trend) >= 1:
        ret.actualmin = int((trend[-1].timestamp - trend[0].timestamp) / 10000000.0 / 60.0)
        t1 = trend[0].timestamp
    benice = blue.pyos.BeNice
    mem = 0
    for sample in trend:
        if isYield:
            benice()
        elap = sample.timestamp - t1
        t1 = sample.timestamp
        p_elap = 100.0 / elap if elap else 0.0
        ret.memData.append(sample.virtualMemory * mega)
        ret.pymemData.append(sample.pythonMemoryUsage * mega)
        thread_u, proc_u = sample.userThreadCpuUsage, sample.userProcessCpuUsage
        thread_k, proc_k = sample.kernelThreadCpuUsage, sample.kernelProcessCpuUsage
        thread_cpupct = thread_u * p_elap
        proc_cpupct = proc_u * p_elap
        thread_kerpct = thread_k * p_elap
        proc_kerpct = proc_k * p_elap
        ret.threadCpuData.append(thread_cpupct)
        ret.procCpuData.append(proc_cpupct)
        ret.threadKerData.append(thread_kerpct)
        ret.procKerData.append(proc_kerpct)
        sched = (sample.fps,
         sample.taskletsProcessed,
         sample.taskletsYielding,
         sample.taskletsSleeping,
         sample.taskletsSchedulerDuration,
         sample.taskletsQueued)
        ret.schedData.append(sched)
        ret.timeData.append(sample.timestamp)
        late = 0.0
        if elap:
            late = (elap - latenessBase) / latenessBase * 100
        ret.latenessData.append(late)

    ret.proc_cpupct = proc_cpupct
    ret.mem = mem
    return ret


def get_blue_info_last_tick():
    result = {}
    stats = blue.pyos.cpuUsage[-1:][0]
    result['virtualmemory'] = stats.virtualMemory
    result['pymemory'] = stats.pythonMemoryUsage
    result['workingset'] = stats.workingSetSize
    result['pagefaults'] = stats.pageFaultCount
    user_thread, user_process = stats.userThreadCpuUsage, stats.userProcessCpuUsage
    kernel_thread, kernel_process = stats.kernelThreadCpuUsage, stats.kernelProcessCpuUsage
    result['user_thread_time_micro'] = user_thread * 0.1
    result['user_process_time_micro'] = user_process * 0.1
    result['kernel_thread_time_micro'] = kernel_thread * 0.1
    result['kernel_process_time_micro'] = kernel_process * 0.1
    spf = 1.0 / stats.fps if stats.fps > 0.1 else 0
    result['tasklets_processed'] = stats.taskletsProcessed
    result['tasklets_queued'] = stats.taskletsQueued
    result['tasklet_scheduler_duration'] = stats.taskletsSchedulerDuration
    result['tasklets_sleeping'] = stats.taskletsSleeping
    result['tasklets_yielding'] = stats.taskletsYielding
    result['spf'] = spf
    return result


def Terminate(exit_code, reason = ''):
    if not isinstance(exit_code, (int, long)):
        raise TypeError('exit_code must be an integer value.')
    import logmodule as log
    if exit_code == 0:
        log.general.Log('bluepy.Terminate - Reason: %s' % reason, log.LGNOTICE)
    else:
        log.general.Log('bluepy.Terminate - Reason: %s' % reason, log.LGERR)
    try:
        if 'sm' in __builtins__:
            sm.ChainEvent('ProcessShutdown')
    except:
        log.LogException()

    log.general.Log('Terminate - all ProcessShutdown done', log.LGNOTICE)
    atexit._run_exitfuncs()
    log.general.Log('Terminate - atexit done, about to shut down', log.LGNOTICE)
    blue.os.Terminate(exit_code)


def TerminateSilently(exit_code, reason = ''):
    if not isinstance(exit_code, (int, long)):
        raise TypeError('exit_code must be an integer value.')
    import logmodule as log
    if exit_code == 0:
        log.general.Log('bluepy.Terminate - Reason: %s' % reason, log.LGNOTICE)
    else:
        log.general.Log('bluepy.Terminate - Reason: %s' % reason, log.LGERR)
    atexit._run_exitfuncs()
    blue.os.Terminate(exit_code)
