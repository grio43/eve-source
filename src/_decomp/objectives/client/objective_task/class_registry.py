#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\class_registry.py
_class_map = {}

def get_class_map():
    return _class_map


from objectives.common.objectives_data import get_objective_task_type_data
from .abyss import *
from .agent import *
from .container import *
from .defend_target import *
from .destroy_counter import *
from .destroy_target import *
from .drone import *
from .dungeon import *
from .fitting import *
from .generic import *
from .inventory import *
from .location import *
from .mining import *
from .module import *
from .scanning import *
from .sovereignty_tasks import *
from .target import *
from .timer import *
from .ui import *
from .base import ObjectiveTask

def _map_classes(local_scope):
    for name, value in local_scope.items():
        if '__' in name:
            continue
        if isinstance(value, type) and issubclass(value, ObjectiveTask) and value.objective_task_content_id is not None and get_objective_task_type_data(value.objective_task_content_id):
            _class_map[value.objective_task_content_id] = value


_map_classes(locals())
