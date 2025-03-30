#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\atoms\conditions\class_registry.py
_class_map = {}

def get_class_map():
    return _class_map


from nodegraph.common.atomdata import get_atom_data
from .compare import *
from .evetype import *
from .primitive import *
from .string import *
from .base import ConditionAtom

def _map_classes(local_scope):
    for name, value in local_scope.items():
        if '__' in name:
            continue
        if isinstance(value, type) and issubclass(value, ConditionAtom) and value.atom_id is not None and get_atom_data(value.atom_id):
            _class_map[value.atom_id] = value


_map_classes(locals())
