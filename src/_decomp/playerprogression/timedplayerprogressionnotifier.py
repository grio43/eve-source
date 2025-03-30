#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\playerprogression\timedplayerprogressionnotifier.py
from carbon.common.lib.const import MIN, MSEC
from carbon.common.script.util.timerstuff import AutoTimer
from gametime import GetWallclockTime
from playerprogression.playerprogressionnotifier import PlayerProgressionNotifier
import uthread2

class TimedPlayerProgressionNotifier(PlayerProgressionNotifier):
    UPDATE_NOT_RECENT_AFTER_MIN = 5 * MIN
    UPDATE_TIMER_DELAY_MSEC = 5 * MIN / MSEC

    def get_update_requirement(self):
        return settings.char.ui.Get('%s_requires_update' % self.NOTIFIER_ID, True)

    def set_update_requirement(self, requires_update):
        settings.char.ui.Set('%s_requires_update' % self.NOTIFIER_ID, requires_update)

    def start_updates(self):
        if self.calculation_thread is None:
            self.calculation_thread = uthread2.StartTasklet(self._get_calculation_timed)

    def _get_calculation_timed(self):
        self._get_calculation()
        self.calculation_thread = AutoTimer(self.UPDATE_TIMER_DELAY_MSEC, self._get_calculation)

    def _get_calculation(self):
        if self.should_update_calculation():
            last_update_date = GetWallclockTime()
            self.set_last_update_date(last_update_date)
            self.calculate_progression()
        progression = self.get_value()
        self._notify_subscribers(progression)

    def is_last_update_recent(self):
        return self.get_last_update_date() + self.UPDATE_NOT_RECENT_AFTER_MIN > GetWallclockTime()
