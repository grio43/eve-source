#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\timer.py
from carbonui import TextColor
from gametime import GetSimTime
from localization.formatters import FormatTimeIntervalShortWritten
from objectives.client.ui.objective_task_widget import TimerTaskWidget
from objectives.client.objective_task.base import ObjectiveTask

class TimerTask(ObjectiveTask):
    objective_task_content_id = 30
    WIDGET = TimerTaskWidget
    progress_bar_color = TextColor.NORMAL

    def __init__(self, timer = None, **kwargs):
        super(TimerTask, self).__init__(**kwargs)
        self._timer = {}
        self._duration = 0
        if timer:
            self.timer = timer

    def get_values(self):
        result = super(TimerTask, self).get_values()
        result['start_time'] = self.start_time
        result['end_time'] = self.end_time
        result['duration'] = self._duration
        result['progress'] = self.progress
        result['time_remaining'] = self.time_remaining
        return result

    @property
    def timer(self):
        return self._timer

    @timer.setter
    def timer(self, value):
        if self._timer == value:
            return
        self._timer = value or {}
        self._duration = self.end_time - self.start_time
        self.update()

    @property
    def start_time(self):
        return self._timer.get('start_time', 0)

    @property
    def end_time(self):
        return self._timer.get('end_time', 0)

    @property
    def time_remaining(self):
        return max(0, self.end_time - GetSimTime())

    @property
    def progress(self):
        if not self._duration:
            return 0
        return 1 - (self._duration - self.time_remaining) / float(self._duration)

    @property
    def value(self):
        return FormatTimeIntervalShortWritten(self.time_remaining)

    def _update(self):
        self.on_update(objective_task=self)
        if not self._timer:
            self.completed = True
        else:
            self.completed = self.time_remaining == 0 if self._duration else False
