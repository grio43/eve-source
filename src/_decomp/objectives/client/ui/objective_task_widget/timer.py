#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\ui\objective_task_widget\timer.py
import uthread2
from .progress import ProgressBarTaskWidget

class TimerTaskWidget(ProgressBarTaskWidget):

    def __init__(self, *args, **kwargs):
        super(TimerTaskWidget, self).__init__(*args, **kwargs)
        self._thread = uthread2.start_tasklet(self._update_thread)

    def close(self):
        super(TimerTaskWidget, self).close()
        if self._thread:
            self._thread.kill()
            self._thread = None

    def _update_thread(self):
        while not self.destroyed:
            self.update()
            uthread2.sleep(1)

        self._thread = None
