#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\registry\registrator.py
from behaviors.registry import COMPOSITE, ACTION, CONDITION, DECORATOR, MONITOR
from behaviors.registry.taskregistry import TaskRegistry
REGISTRY = TaskRegistry()
NO_ATTRIBUTES = {}

def register_task(task_type, task_class, attributes = None, short_description = None, detailed_description = None):
    if attributes is None:
        attributes = NO_ATTRIBUTES
    REGISTRY.register_task(task_type, {'task_type': task_type,
     'task_class': task_class,
     'short_description': short_description,
     'detailed_description': detailed_description,
     'attributes': attributes})


def register_composite(task_class, attributes = None, short_description = None, detailed_description = None):
    register_task(COMPOSITE, task_class, attributes, short_description, detailed_description)


def register_action(task_class, attributes = None, short_description = None, detailed_description = None):
    register_task(ACTION, task_class, attributes, short_description, detailed_description)


def register_condition(task_class, attributes = None, short_description = None, detailed_description = None):
    register_task(CONDITION, task_class, attributes, short_description, detailed_description)


def register_decorator(task_class, attributes = None, short_description = None, detailed_description = None):
    register_task(DECORATOR, task_class, attributes, short_description, detailed_description)


def register_monitor(task_class, attributes = None, short_description = None, detailed_description = None):
    register_task(MONITOR, task_class, attributes, short_description, detailed_description)
