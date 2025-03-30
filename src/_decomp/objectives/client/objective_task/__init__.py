#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\__init__.py
from objectives.client.objective_task.class_registry import get_class_map
_class_map = None

def get_all_objective_task_classes():
    global _class_map
    if not _class_map:
        _class_map = get_class_map()
    return _class_map


def get_objective_task_class(task_id):
    return get_all_objective_task_classes().get(task_id, None)
