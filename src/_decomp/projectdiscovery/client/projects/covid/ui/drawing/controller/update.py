#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\controller\update.py
import signals

class UpdateController(object):

    def __init__(self):
        self._last_reported_tick = 0
        self._tick_count = 0
        self._update_signal = signals.Signal(signalName='_update_signal')

    @property
    def tick_count(self):
        return self._tick_count

    def tick(self):
        self._tick_count += 1

    def report_update(self):
        if self._tick_count != self._last_reported_tick:
            self._update_signal()
            self._last_reported_tick = self.tick_count
            return True
        return False

    def register_update_callback(self, method):
        self._update_signal.connect(method)

    def unregister_update_callback(self, method):
        self._update_signal.disconnect(method)

    def clear(self):
        self._update_signal.clear()
