#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uthread2\delayedcalls\__init__.py
from .. import start_tasklet, sleep_sim, sleep
MAX_SINGLE_SLEEP = 86400
MAX_TOTAL_DELAY = 1209600

def call_after_simtime_delay(tasklet_func, delay, *args, **kwargs):
    return _call_after_delay(delay, sleep_sim, tasklet_func, *args, **kwargs)


def call_after_wallclocktime_delay(tasklet_func, delay, *args, **kwargs):
    return _call_after_delay(delay, sleep, tasklet_func, *args, **kwargs)


def _call_after_delay(delay, sleep_func, tasklet_func, *args, **kwargs):
    if delay > MAX_TOTAL_DELAY:
        raise RuntimeError('Cannot delay a tasklet for more than MAX_TOTAL_DELAY seconds')

    def _worker(_delay):
        while _delay > MAX_SINGLE_SLEEP:
            sleep_func(MAX_SINGLE_SLEEP)
            _delay -= MAX_SINGLE_SLEEP

        sleep_func(_delay)
        tasklet_func(*args, **kwargs)

    return start_tasklet(_worker, delay)
