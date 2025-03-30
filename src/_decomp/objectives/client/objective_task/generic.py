#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\generic.py
import eveformat
from objectives.client.ui.objective_task_widget import ProgressBarTaskWidget, ObjectiveTaskWidget, ButtonTaskWidget
from objectives.client.objective_task.base import ObjectiveTask

class ProgressTask(ObjectiveTask):
    objective_task_content_id = 9
    WIDGET = ProgressBarTaskWidget

    def __init__(self, current_value = None, goal_value = None, display_percentage = None, **kwargs):
        super(ProgressTask, self).__init__(**kwargs)
        self._current_value = current_value or 0
        self._goal_value = goal_value
        self._display_percentage = display_percentage or False

    def get_values(self):
        result = super(ProgressTask, self).get_values()
        result['current_value'] = self.current_value
        result['goal_value'] = self.goal_value
        result['progress'] = self.progress
        return result

    @property
    def current_value(self):
        return self._current_value

    @current_value.setter
    def current_value(self, value):
        value = min(value, self._goal_value)
        if self._current_value == value:
            return
        self._current_value = value or 0
        self.update()

    @property
    def goal_value(self):
        return self._goal_value

    @goal_value.setter
    def goal_value(self, value):
        if self._goal_value == value:
            return
        self._goal_value = value
        self.update()

    @property
    def display_percentage(self):
        return self._display_percentage or self._goal_value >= 1000000

    @display_percentage.setter
    def display_percentage(self, value):
        if self._display_percentage == value:
            return
        self._display_percentage = value
        self.update()

    @property
    def tooltip(self):
        tooltip = super(ProgressTask, self).tooltip
        if not tooltip:
            if self.display_percentage and self.goal_value <= 1:
                return ''
            return self._get_value(not self.display_percentage)
        return tooltip

    def _update(self):
        self.on_update(objective_task=self)
        self.hidden = not bool(self._goal_value)
        self.completed = self._goal_value and self._current_value >= self._goal_value

    @property
    def value(self):
        return self._get_value(self.display_percentage)

    @property
    def progress(self):
        if self._current_value is None or self._goal_value is None:
            return 0
        return min(self._current_value / float(self._goal_value), 1.0)

    def _get_value(self, as_percentage):
        if self._current_value is None or self._goal_value is None:
            return ''
        elif as_percentage:
            percentage = self._current_value / float(self._goal_value)
            return u'{value}%'.format(value=int(percentage * 100))
        else:
            return u'{}/{}'.format(eveformat.number(self._current_value, 0), eveformat.number(self._goal_value, 0))


class GenericValueTask(ObjectiveTask):
    objective_task_content_id = 35
    WIDGET = ObjectiveTaskWidget

    def __init__(self, value = None, **kwargs):
        super(GenericValueTask, self).__init__(**kwargs)
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._value == value:
            return
        self._value = value
        self.update()


class GenericButtonTask(ObjectiveTask):
    objective_task_content_id = 38
    WIDGET = None
    BUTTON_WIDGET = ButtonTaskWidget

    def button_click(self):
        self.completed = True


class ValueRangeTask(ObjectiveTask):
    objective_task_content_id = 42
    WIDGET = ProgressBarTaskWidget

    def __init__(self, current_value = None, max_value = None, min_goal_value = None, max_goal_value = None, display_percentage = None, **kwargs):
        super(ValueRangeTask, self).__init__(**kwargs)
        self._current_value = current_value or 0
        self._max_value = max_value or 1
        self._min_goal_value = min_goal_value or 0
        self._max_goal_value = max_goal_value or 1
        self._display_percentage = display_percentage or False

    def get_values(self):
        result = super(ValueRangeTask, self).get_values()
        result['current_value'] = self.current_value
        result['max_value'] = self.max_value
        result['min_goal_value'] = self.min_goal_value
        result['max_goal_value'] = self.max_goal_value
        result['progress'] = self.progress
        return result

    @property
    def current_value(self):
        return self._current_value

    @current_value.setter
    def current_value(self, value):
        value = min(value, self._max_value)
        if self._current_value == value:
            return
        self._current_value = value
        self.update()

    @property
    def max_value(self):
        return self._max_value

    @max_value.setter
    def max_value(self, value):
        if self._max_value == value:
            return
        self._max_value = value
        if self._current_value > self._max_value:
            self._current_value = self._max_value
        self.update()

    @property
    def min_goal_value(self):
        return self._min_goal_value

    @min_goal_value.setter
    def min_goal_value(self, value):
        if self._min_goal_value == value:
            return
        self._min_goal_value = value
        self.update()

    @property
    def max_goal_value(self):
        return self._max_goal_value

    @max_goal_value.setter
    def max_goal_value(self, value):
        if self._max_goal_value == value:
            return
        self._max_goal_value = value
        self.update()

    @property
    def display_percentage(self):
        return self._display_percentage or self._max_value >= 1000000

    @display_percentage.setter
    def display_percentage(self, value):
        if self._display_percentage == value:
            return
        self._display_percentage = value
        self.update()

    @property
    def tooltip(self):
        tooltip = super(ValueRangeTask, self).tooltip
        if not tooltip:
            return self._get_value(not self.display_percentage)
        return tooltip

    def _update(self):
        self.on_update(objective_task=self)
        self.completed = self._min_goal_value <= self._current_value <= self._max_goal_value

    @property
    def value(self):
        return self._get_value(self.display_percentage)

    @property
    def progress(self):
        return min(self._current_value / float(self._max_value), 1.0)

    def _get_value(self, as_percentage):
        if as_percentage:
            percentage = self._current_value / float(self._max_value)
            return u'{value}%'.format(value=int(percentage * 100))
        else:
            return u'{}/{}'.format(eveformat.number(self._current_value, 0), eveformat.number(self._max_value, 0))
