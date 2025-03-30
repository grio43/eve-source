#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uthread2_lib\__init__.py
import contextlib
import os
import logging
logger = logging.getLogger('uthread2_lib')
ENV_ALLOW_TASKLESS = 'ENV_ALLOW_TASKLESS'
__all__ = ['map',
 'get_implementation',
 'start_tasklet',
 'sleep',
 'sleep_sim',
 'yield_',
 'Event']
from uthread2_plugins import get_implementation
logger = logging.getLogger('uthread2_lib')

@contextlib.contextmanager
def _catch():
    try:
        yield
    except ImportError as e:
        logger.debug('Failed to import: %s', e)


def _prime_plugins():
    with _catch():
        from uthread2_plugins import stacklessimpl
        logger.debug('uthread2 registered stackless')
    with _catch():
        from uthread2_plugins import geventimpl
        logger.debug('uthread2 registered gevent')
    if os.environ.get(ENV_ALLOW_TASKLESS):
        from uthread2_plugins import taskless
        logger.debug('uthread2 registered taskless')


_prime_plugins()
impl = get_implementation()
map = impl.map
sleep = impl.sleep
sleep_sim = impl.sleep_sim
start_tasklet = impl.start_tasklet
yield_ = impl.yield_
get_current = impl.get_current
Event = impl.Event
Semaphore = impl.Semaphore
