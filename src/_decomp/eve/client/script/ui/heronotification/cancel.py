#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\heronotification\cancel.py
import datetimeutils
from stacklesslib.locks import NLCondition

class CancellationToken(object):

    def __init__(self):
        self._cancelled = False
        self._cancelled_condition = NLCondition()

    @property
    def cancelled(self):
        return self._cancelled

    def cancel(self):
        self._cancelled = True
        self._cancelled_condition.notify_all()

    def check_cancelled(self):
        if self._cancelled:
            raise Cancelled()

    def sleep(self, duration):
        self._cancelled_condition.wait(timeout=datetimeutils.timedelta_to_filetime_delta(duration))
        self.check_cancelled()


class Cancelled(Exception):
    pass
