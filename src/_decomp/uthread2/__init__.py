#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uthread2\__init__.py
from uthread2_plugins import get_implementation
import uthread2_lib
try:
    from . import bluepyimpl
except ImportError:
    pass

impl = get_implementation()
map = impl.map
Map = map
sleep = impl.sleep
Sleep = sleep
sleep_sim = impl.sleep_sim
SleepSim = sleep_sim
start_tasklet = impl.start_tasklet
StartTasklet = start_tasklet
yield_ = impl.yield_
Yield = yield_
get_current = impl.get_current
wait = impl.wait
Event = impl.Event
Semaphore = impl.Semaphore

def blocking_channel():
    return impl.BlockingChannel()


def pump_channel():
    return impl.PumpChannel()


def queue_channel():
    return impl.QueueChannel()


from .delayedcalls import call_after_simtime_delay, call_after_wallclocktime_delay
from .callthrottlers import CallCombiner, BufferedCall
from .debounce import debounce
using_stackless = False
try:
    import stackless
    using_stackless = True
except ImportError:
    using_stackless = False

def decorate_if(condition, decorator):
    if condition:
        return decorator
    return lambda x: x
