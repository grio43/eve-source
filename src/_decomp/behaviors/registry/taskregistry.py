#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\registry\taskregistry.py
from . import COMPOSITE, ACTION, CONDITION, DECORATOR, MONITOR
from functoolsext import lru_cache

def get_full_class_name(task_class):
    return task_class['task_class']


def get_class_from_name(full_class_name):
    module_name, class_name = full_class_name.rsplit('.', 1)
    mod = __import__(module_name, fromlist=[class_name])
    return getattr(mod, class_name)


class TaskRegistry(object):

    def __init__(self):
        self._registered_tasks_by_class_name = {}
        self._tasks_by_type = {COMPOSITE: set(),
         ACTION: set(),
         CONDITION: set(),
         DECORATOR: set(),
         MONITOR: set()}

    def register_task(self, task_type, task_class):
        task_name = get_full_class_name(task_class)
        self._registered_tasks_by_class_name[task_name] = task_class
        self._tasks_by_type[task_type].add(task_name)

    def register_action(self, task_class):
        self.register_task(ACTION, task_class)

    def register_condition(self, task_class):
        self.register_task(CONDITION, task_class)

    def register_composite(self, task_class):
        self.register_task(COMPOSITE, task_class)

    def register_decorator(self, task_class):
        self.register_task(DECORATOR, task_class)

    def register_monitor(self, task_class):
        self.register_task(MONITOR, task_class)

    def _get_classes_by_type(self, task_type):
        return [ get_class_from_name(name) for name in self._tasks_by_type[task_type] ]

    def get_tasks_by_type(self, task_type):
        return list(self._tasks_by_type.get(task_type))

    def get_actions(self):
        return self._get_classes_by_type(ACTION)

    def get_conditions(self):
        return self._get_classes_by_type(CONDITION)

    def get_composites(self):
        return self._get_classes_by_type(COMPOSITE)

    def get_decorators(self):
        return self._get_classes_by_type(DECORATOR)

    def get_monitors(self):
        return self._get_classes_by_type(MONITOR)

    def action_list(self):
        return self.get_tasks_by_type(ACTION)

    def condition_list(self):
        return self.get_tasks_by_type(CONDITION)

    def composite_list(self):
        return self.get_tasks_by_type(COMPOSITE)

    def decorator_list(self):
        return self.get_tasks_by_type(DECORATOR)

    def monitor_list(self):
        return self.get_tasks_by_type(MONITOR)

    def is_action(self, task_name):
        return task_name in self._tasks_by_type[ACTION]

    def is_condition(self, task_name):
        return task_name in self._tasks_by_type[CONDITION]

    def is_composite(self, task_name):
        return task_name in self._tasks_by_type[COMPOSITE]

    def is_decorator(self, task_name):
        return task_name in self._tasks_by_type[DECORATOR]

    def is_monitor(self, task_name):
        return task_name in self._tasks_by_type[MONITOR]

    def get_task_type(self, task_name):
        return self._registered_tasks_by_class_name[task_name]['task_type']

    def get_class_attributes(self, task_name):
        return self._registered_tasks_by_class_name[task_name]['attributes']

    def get_class_short_description(self, task_name):
        return self._registered_tasks_by_class_name[task_name]['short_description']

    def get_class_detailed_description(self, task_name):
        return self._registered_tasks_by_class_name[task_name]['detailed_description']

    @lru_cache(maxsize=256)
    def get_class_from_name(self, full_class_name):
        return get_class_from_name(str(full_class_name))

    def get_full_class_name(self, task_class):
        get_full_class_name(task_class)
