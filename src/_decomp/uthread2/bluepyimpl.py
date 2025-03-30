#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uthread2\bluepyimpl.py
import time
import blue
from stacklesslib import locks, main
from stackless import getcurrent
import weakref
import bluepy
from uthread2_plugins import BaseUthreadImpl, stacklessimpl, set_implementation

class BluepyTasklet(stacklessimpl.StacklessTasklet):

    def __init__(self, func, *args, **kwargs):

        def inner():
            getcurrent().localStorage['uthread2_tasklet'] = weakref.ref(self)
            try:
                func_name = func.func_name
            except AttributeError:
                try:
                    func_name = func.key
                except AttributeError:
                    func_name = 'UnnamedCallable'

            with bluepy.Timer('BluepyTasklet::%s' % func_name):
                func(*args, **kwargs)

        self.tasklet = bluepy.CreateTaskletExt(inner)
        self.tasklet.method_name = getattr(func, '__name__', 'unknown_method')
        self.tasklet.module_name = getattr(func, '__module__', 'unknown_module')
        try:
            self.tasklet.file_name = func.__code__.co_filename
            self.tasklet.line_number = func.__code__.co_firstlineno
        except AttributeError:
            self.tasklet.file_name = 'unknown_file'
            self.tasklet.line_number = 0

    def get(self):
        while self.tasklet.alive:
            blue.synchro.Yield()
            main.mainloop.wakeup_tasklets(None)


class _BluepyAutoTasklet(BluepyTasklet):

    def __init__(self, tasklet):
        self.tasklet = weakref.proxy(tasklet)
        if hasattr(tasklet, 'localStorage'):
            tasklet.localStorage['uthread2_tasklet'] = self


class _BluepyUthread(BaseUthreadImpl):

    def __init__(self):
        BaseUthreadImpl.__init__(self)

    def sleep(self, seconds):
        blue.synchro.Sleep(seconds * 1000)

    def sleep_sim(self, seconds):
        blue.synchro.SleepSim(seconds * 1000)

    def start_tasklet(self, func, *args, **kwargs):
        return BluepyTasklet(func, *args, **kwargs)

    def yield_(self):
        blue.synchro.Yield()
        main.mainloop.wakeup_tasklets(None)

    def get_current(self):
        current = getcurrent()
        result = getattr(current, 'localStorage', {}).get('uthread2_tasklet', None)
        if isinstance(result, _BluepyAutoTasklet):
            return result
        if result:
            tasklet = result()
            if tasklet is not None:
                return tasklet
        return _BluepyAutoTasklet(current)

    def wait(self, tasklets, timeout):
        deadline = time.time() + timeout
        while time.time() < deadline:
            alive = [ tasklet.is_alive() for tasklet in tasklets ]
            if not all(alive):
                return
            self.yield_()

        for tasklet in tasklets:
            try:
                tasklet.kill()
            except Exception as e:
                pass

    def Event(self):
        return locks.Event()

    def Semaphore(self):
        return stacklessimpl.StacklessSemaphore()

    def BlockingChannel(self):
        return stacklessimpl.Channel(-1)

    def PumpChannel(self):
        return stacklessimpl.Channel(1)

    def QueueChannel(self):
        return stacklessimpl.QueueChannel()


BluepyImpl = _BluepyUthread()
set_implementation(BluepyImpl)
