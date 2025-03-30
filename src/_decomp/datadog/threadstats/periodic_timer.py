#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\threadstats\periodic_timer.py
from threading import Thread, Event

class PeriodicTimer(Thread):

    def __init__(self, interval, function, *args, **kwargs):
        Thread.__init__(self)
        self.daemon = True
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()

    def _is_alive(self):
        return bool(self.finished) and bool(self.interval) and bool(self.function)

    def end(self):
        if self._is_alive():
            self.finished.set()

    def run(self):
        while True:
            if not self._is_alive() or self.finished.isSet():
                break
            self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)
