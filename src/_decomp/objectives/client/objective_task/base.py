#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\base.py
from collections import OrderedDict
import signals
import uthread2
import threadutils
import eveicon
import localization
import carbonui
from objectives.client.ui.objective_task_widget import ObjectiveTaskWidget, ObjectiveTaskGroupWidget
from objectives.common.objectives_data import get_objective_task_type_data

class ObjectiveTask(object):
    objective_task_content_id = None
    WIDGET = ObjectiveTaskWidget
    BUTTON_WIDGET = None
    USE_TYPE_ICON = False
    __notifyevents__ = []

    def __init__(self, task_id, title = '', icon = '', tooltip = '', show_completed = False, objective_task_content_id = None, hidden = False, **kwargs):
        self.task_id = task_id
        data = get_objective_task_type_data(objective_task_content_id or self.objective_task_content_id)
        self._input_parameters = {p.parameterKey:p for p in data.inputParameters}
        self._title = title
        if not title and data.title:
            self._title = localization.GetByLabel(data.title)
        if isinstance(icon, eveicon.IconData):
            self._icon = icon
        else:
            self._icon = eveicon.get(icon or data.icon or '')
        self._tooltip = tooltip or ''
        self.show_completed = show_completed
        self._completed = False
        self._is_active = False
        self._hidden = hidden
        self._highlight = None
        self._is_highlighting = False
        self._highlight_reasons = set()
        self._is_button_hidden = False
        self.on_state_changed = signals.Signal('on_task_state_changed')
        self.on_update = signals.Signal('on_task_updated')
        self.on_button_state_changed = signals.Signal('on_button_state_changed')

    def start(self):
        if self._is_active:
            return
        self.is_active = True
        self._start()
        self._register()
        self.update()
        self._update_highlight_state()

    def stop(self):
        if not self._is_active:
            return
        self.is_active = False
        self._stop()
        self._unregister()
        self._update_highlight_state()

    def show_button(self):
        self._is_button_hidden = False
        self.on_button_state_changed()

    def hide_button(self):
        self._is_button_hidden = True
        self.on_button_state_changed()

    def update(self):
        if self.is_active:
            self._update()

    def update_value(self, key, value):
        if key in self._input_parameters and hasattr(self, key):
            setattr(self, key, value)

    def get_values(self):
        result = {}
        for key in self._input_parameters:
            result[key] = getattr(self, key, None)

        return result

    def get_status_values(self):
        return {'hidden': self.hidden,
         'completed': self.completed,
         'is_active': self.is_active}

    def construct_widget(self, *args, **kwargs):
        if self.WIDGET:
            return self.WIDGET(objective_task=self, *args, **kwargs)
        else:
            return None

    def construct_button_widget(self, *args, **kwargs):
        if self.BUTTON_WIDGET:
            return self.BUTTON_WIDGET(objective_task=self, *args, **kwargs)
        else:
            return None

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
        self.on_state_changed(objective_task=self, reason='on_hide' if value else 'on_show')

    @property
    def completed(self):
        return self._completed

    @completed.setter
    def completed(self, value):
        if self._completed == value:
            return
        self._completed = bool(value)
        self._update_highlight_state()
        self.on_state_changed(objective_task=self, reason='on_complete' if value else 'on_incomplete')

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        if self._is_active == value:
            return
        self._is_active = value
        self._update_highlight_state()
        self.on_state_changed(objective_task=self, reason='on_start' if value else 'on_stop')

    @property
    def title(self):
        return self._title

    @property
    def icon(self):
        return self._icon

    @property
    def icon_color(self):
        return carbonui.TextColor.NORMAL

    @property
    def value(self):
        return ''

    @property
    def tooltip(self):
        return self._tooltip

    @property
    def highlight(self):
        return self._highlight

    @highlight.setter
    def highlight(self, value):
        if value == self._highlight:
            return
        if self._highlight and self._is_highlighting:
            self._highlight.stop()
            self._is_highlighting = False
        self._highlight = value
        self._update_highlight_state()

    @property
    def button_label(self):
        return self.title

    @property
    def button_icon(self):
        return self.icon

    @property
    def button_tooltip(self):
        return self.tooltip

    @property
    def is_button_hidden(self):
        return self._is_button_hidden

    def mouse_down(self, ui_widget):
        pass

    def click(self):
        pass

    def double_click(self):
        pass

    def button_click(self):
        self.double_click()

    def get_context_menu(self):
        return []

    def enable_highlight(self, reason = 'on_hover'):
        self._highlight_reasons.add(reason)
        self._update_highlight_state()

    def disable_highlight(self, reason = 'on_hover'):
        if not self._highlight_reasons:
            return
        self._highlight_reasons.discard(reason)
        self._update_highlight_state()

    @threadutils.threaded
    def _update_highlight_state(self):
        if not self.highlight:
            return
        should_highlight = bool(self._highlight_reasons) and self.is_active and (not self.completed or 'on_hover' in self._highlight_reasons) and not settings.char.ui.Get('guidance_highlighting_disabled', False)
        if should_highlight:
            if not self._is_highlighting:
                self.highlight.start()
                self._is_highlighting = True
        elif self._is_highlighting:
            self.highlight.stop()
            self._is_highlighting = False

    def _register(self):
        sm.RegisterNotify(self)

    def _unregister(self):
        sm.UnregisterNotify(self)

    def _update(self):
        self.on_update(objective_task=self)

    def _start(self):
        pass

    def _stop(self):
        pass

    @property
    def destroyed(self):
        return False


class ObjectiveTaskGroup(ObjectiveTask):
    objective_task_content_id = None
    WIDGET = ObjectiveTaskGroupWidget
    TASK = None

    def __init__(self, *args, **kwargs):
        super(ObjectiveTaskGroup, self).__init__(*args, **kwargs)
        self.tasks = OrderedDict()
        self.on_group_changed = signals.Signal('on_task_group_changed')

    def get_values(self):
        result = super(ObjectiveTaskGroup, self).get_values()
        tasks = {}
        for task in self.tasks.itervalues():
            tasks[task.task_id] = task.get_values()

        result['tasks'] = tasks
        return result

    def get_task_ids(self):
        return self.tasks.keys()

    def add_task(self, task_id = None, start_task = False, **kwargs):
        task = self.TASK(task_id=(task_id or self.task_id), objective_task_content_id=self.objective_task_content_id, show_completed=self.show_completed, title=self.title, icon=self.icon, **kwargs)
        self.tasks[task_id] = task
        if start_task and self.is_active:
            self._start_task(task)
            self._signal_update()
            self._on_task_state_changed()

    def remove_task(self, task_id):
        if task_id in self.tasks:
            task = self.tasks.pop(task_id)
            self._stop_task(task)
            self._signal_update()
            self._on_task_state_changed()

    def all_tasks_added(self):
        if self.is_active and self.tasks:
            for task in self.tasks.itervalues():
                self._start_task(task)

            self._on_task_state_changed()
        self._signal_update()

    def clear_tasks(self):
        for task in self.tasks.itervalues():
            self._stop_task(task)

        self.tasks.clear()

    def construct_widget(self, *args, **kwargs):
        return self.WIDGET(objective_task=self, *args, **kwargs)

    def construct_task_widget(self, task_id, *args, **kwargs):
        return self.TASK.WIDGET(objective_task=self.tasks[task_id], *args, **kwargs)

    @uthread2.debounce(wait=0.3)
    def _signal_update(self):
        self._signal()

    def _signal(self):
        self.on_group_changed()
        self.on_update(objective_task=self)

    def _start(self):
        for task in self.tasks.itervalues():
            self._start_task(task)

        if self.tasks:
            self._on_task_state_changed()

    def _stop(self):
        for task in self.tasks.itervalues():
            self._stop_task(task)

        self._on_task_state_changed()

    def _update(self):
        for task in self.tasks.itervalues():
            task.update()

    def _start_task(self, task):
        task.start()
        task.on_state_changed.connect(self._on_task_state_changed)

    def _stop_task(self, task):
        task.on_state_changed.disconnect(self._on_task_state_changed)
        task.stop()

    def _on_task_state_changed(self, **kwargs):
        self._update_completed_state()

    @uthread2.debounce(wait=0.5)
    def _update_completed_state(self):
        for task in self.tasks.itervalues():
            if not task.completed:
                self.completed = False
                return

        self.completed = True
