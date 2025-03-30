#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective\base.py
from collections import OrderedDict, defaultdict
import logging
import localization
import signals
from objectives.common.objectives_data import get_objective_type_data
from objectives.client.objective_task import get_objective_task_class
logger = logging.getLogger('objectives')

class Objective(object):
    objective_content_id = None

    def __init__(self, objective_id, objective_content_id, objective_values, title = None, description = '', tooltip = '', task_overrides = None, show_completed = False, rendering_order = 5):
        self.objective_id = objective_id
        self.objective_content_id = objective_content_id
        data = get_objective_type_data(self.objective_content_id)
        self._title = title
        if title is None and data.title:
            self._title = localization.GetByLabel(data.title)
        self._description = description or ''
        self._tooltip = tooltip or ''
        self.overrides = task_overrides or {}
        self.show_completed = show_completed
        self.rendering_order = rendering_order
        self._tasks_info = OrderedDict()
        for task_info in data.tasks:
            self._tasks_info[task_info.key] = task_info

        self._objective_values = objective_values
        self._completed = False
        self._is_active = False
        self._hidden = False
        self._subscribed_values = defaultdict(dict)
        self._tasks = OrderedDict()
        self._construct_tasks(self._tasks_info, self._objective_values)
        self._starting = False
        self._triggering = False
        self.on_state_changed = signals.Signal('on_objective_state_changed')
        self.on_tasks_changed = signals.Signal('on_objective_tasks_changed')

    def get_status_values(self):
        return {'hidden': self.hidden,
         'completed': self.completed,
         'is_active': self.is_active}

    @property
    def hidden(self):
        if self._hidden:
            return True
        if not self.is_active:
            return True
        return self.completed and not self.show_completed

    @hidden.setter
    def hidden(self, value):
        if self._hidden == value:
            return
        self._hidden = value
        self.on_state_changed(objective=self, objective_id=self.objective_id, reason='on_hide' if value else 'on_show')

    @property
    def completed(self):
        return self._completed

    @completed.setter
    def completed(self, value):
        if self._completed == value:
            return
        self._completed = value
        self._state_changed(reason='on_complete' if value else 'on_incomplete')

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        if self._is_active == value:
            return
        self._is_active = value
        self._state_changed(reason='on_start' if value else 'on_stop')

    @property
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def tooltip(self):
        return self._tooltip

    def start(self):
        if self._is_active:
            return
        self.is_active = True
        self._starting = True
        self._on_start()
        self._starting = False
        self._check_completed_state()

    def _on_start(self):
        for task_info in self._tasks_info.itervalues():
            if task_info.startActive:
                self.start_task(task_info.key)

    def clear(self):
        for task in self._tasks.itervalues():
            task.on_state_changed.disconnect(self._task_state_changed)

        self.stop()
        self._tasks.clear()
        self._subscribed_values.clear()

    def stop(self):
        if not self._is_active:
            return
        self.is_active = False
        self.stop_all_tasks()

    def start_task(self, task_id):
        self._tasks[task_id].start()

    def stop_task(self, task_id):
        self._tasks[task_id].stop()

    def stop_all_tasks(self):
        for task in self._tasks.itervalues():
            task.stop()

    def show_task_button(self, task_id):
        self._tasks[task_id].show_button()

    def hide_task_button(self, task_id):
        self._tasks[task_id].hide_button()

    def show_highlights(self):
        for task in self._tasks.itervalues():
            task.enable_highlight(reason='objective')

    def hide_highlights(self):
        for task in self._tasks.itervalues():
            task.disable_highlight(reason='objective')

    def update_value(self, key, value):
        if key not in self._subscribed_values:
            return
        for task_id, value_key in self._subscribed_values[key].iteritems():
            self._objective_values[key] = value
            self._tasks[task_id].update_value(value_key, value)

    def get_value(self, key):
        return self._objective_values.get(key, None)

    def get_values(self):
        return self._objective_values

    def get_all_tasks(self):
        return self._tasks.values()

    def get_visible_tasks(self):
        result = []
        for task in self._tasks.itervalues():
            if task.hidden:
                continue
            result.append(task)

        return result

    def task_trigger(self, task_id, trigger_key):
        task_triggers = self._tasks_info[task_id].triggers
        if not task_triggers or trigger_key not in task_triggers:
            return
        self._triggering = True
        for trigger in task_triggers[trigger_key]:
            if trigger.action == 'start_task':
                self.start_task(trigger.taskKey)
            elif trigger.action == 'stop_task':
                self.stop_task(trigger.taskKey)
            elif trigger.action == 'show_task_button':
                self.show_task_button(trigger.taskKey)
            elif trigger.action == 'hide_task_button':
                self.hide_task_button(trigger.taskKey)
            else:
                logger.error('Objective trigger action %s is not supported', trigger.action)

        self._triggering = False
        self._check_completed_state()

    def _state_changed(self, reason):
        self.on_state_changed(objective=self, objective_id=self.objective_id, reason=reason)

    def _task_state_changed(self, objective_task, reason):
        self.task_trigger(objective_task.task_id, reason)
        self.on_tasks_changed(objective=self, objective_id=self.objective_id, task_id=objective_task.task_id, reason=reason)
        self._check_completed_state()

    def _check_completed_state(self):
        if self._starting or self._triggering or not self._is_active or not self._tasks:
            return
        completed = True
        for task in self._tasks.itervalues():
            if task.is_active and not task.completed:
                completed = False
                break

        self.completed = completed

    def _construct_tasks(self, tasks_info, values):
        for task_info in tasks_info.itervalues():
            task_class = get_objective_task_class(task_info.taskType)
            task_values = {}
            for task_value_key, objective_value_key in task_info.inputParameters.iteritems():
                if objective_value_key in values:
                    task_values[task_value_key] = values.get(objective_value_key)
                self._subscribe_to_value(task_info.key, task_value_key, objective_value_key)

            overrides = self.overrides.get(task_info.key)
            title = getattr(overrides, 'title', task_info.title) or ''
            if title:
                title = localization.GetByLabel(title)
            icon = getattr(overrides, 'icon', task_info.icon)
            task = task_class(task_id=task_info.key, show_completed=bool(task_info.showCompleted), title=title, icon=icon, **task_values)
            self._tasks[task_info.key] = task
            task.on_state_changed.connect(self._task_state_changed)

    def _subscribe_to_value(self, task_id, task_value_key, objective_value_key):
        self._subscribed_values[objective_value_key][task_id] = task_value_key
