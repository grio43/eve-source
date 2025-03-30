#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\countdownTimer.py
from carbon.common.script.util.observerNotifier import ObserverNotifier
from carbon.common.script.util.timerstuff import AutoTimer
from gametime import GetWallclockTimeNow, MSEC, SEC
from uthread2 import StartTasklet

class CountdownTimer(ObserverNotifier):

    def __init__(self, expiration_date, seconds_between_updates = 1.0):
        self.milliseconds_between_updates = seconds_between_updates * SEC / MSEC
        self.expiration_date = expiration_date
        self.timer = None
        super(CountdownTimer, self).__init__()

    def get_value(self):
        return self.expiration_date - GetWallclockTimeNow()

    def set_expiration_date(self, expiration_date):
        self.expiration_date = expiration_date

    def start_updates(self):
        if not self.timer:
            self.timer = StartTasklet(self._do_timed_updates)

    def stop_updates(self):
        if self.timer:
            self.timer.KillTimer()
            self.timer = None

    def _do_timed_updates(self):
        self._notify_of_update()
        self.timer = AutoTimer(self.milliseconds_between_updates, self._notify_of_update)

    def _notify_of_update(self):
        update = self.get_value()
        self._notify_subscribers(update)
