#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\util\sessiontools.py
from gametime import GetSimTime
from logging import getLogger
from uthread2 import Sleep
logger = getLogger(__name__)

def wait_for_session_ready(attempts_before_timeout = 20):
    for i in xrange(attempts_before_timeout):
        if _is_session_change_finished() and session.IsItSafe():
            break
        Sleep(1.0)
        logger.info('Waiting for session to be ready (attempt {}/{})'.format(i, attempts_before_timeout))
    else:
        raise TimedOutWaitingForSession(attempts_before_timeout)


def _is_session_change_finished():
    return not session.nextSessionChange or session.nextSessionChange - GetSimTime() < 0


class TimedOutWaitingForSession(RuntimeError):

    def __init__(self, attempts_before_timeout):
        self.message = 'Timed out waiting for session to be ready after {} attempts'.format(attempts_before_timeout)
        super(TimedOutWaitingForSession, self).__init__(self.message)

    def __str__(self):
        return self.message
