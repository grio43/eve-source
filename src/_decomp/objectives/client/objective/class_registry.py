#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective\class_registry.py
_class_map = {}

def get_class_map():
    return _class_map


from objectives.common.objectives_data import get_objective_type_data
from .agent import *
from .scanning import *
from .base import Objective

def _map_classes(local_scope):
    for name, value in local_scope.items():
        if '__' in name:
            continue
        if isinstance(value, type) and issubclass(value, Objective) and value.objective_content_id is not None and get_objective_type_data(value.objective_content_id):
            _class_map[value.objective_content_id] = value


_map_classes(locals())
