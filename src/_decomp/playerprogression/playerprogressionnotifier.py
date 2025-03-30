#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\playerprogression\playerprogressionnotifier.py
from carbon.common.script.util.observerNotifier import ObserverNotifier
from gametime import GetWallclockTime
import uthread2

class PlayerProgressionNotifier(ObserverNotifier):
    NOTIFIER_ID = None

    def __init__(self):
        self.calculation_thread = None
        super(PlayerProgressionNotifier, self).__init__()

    def get_value(self):
        return settings.char.ui.Get('%s_value' % self.NOTIFIER_ID, None)

    def set_value(self, value):
        settings.char.ui.Set('%s_value' % self.NOTIFIER_ID, value)

    def get_last_update_date(self):
        return settings.char.ui.Get('%s_last_update' % self.NOTIFIER_ID, None)

    def set_last_update_date(self, last_update):
        settings.char.ui.Set('%s_last_update' % self.NOTIFIER_ID, last_update)

    def calculate_progression(self):
        raise NotImplementedError('Must implement player progression calculation.')

    def start_updates(self):
        if self.calculation_thread is None:
            self.calculation_thread = uthread2.StartTasklet(self._get_calculation)

    def stop_updates(self):
        self.calculation_thread = None

    def _get_calculation(self):
        try:
            if self.should_update_calculation():
                last_update_date = GetWallclockTime()
                self.set_last_update_date(last_update_date)
                self.calculate_progression()
            progression = self.get_value()
            self._notify_subscribers(progression)
        finally:
            self.stop_updates()

    def should_update_calculation(self):
        raise NotImplementedError('Must implement player progression update rules.')
