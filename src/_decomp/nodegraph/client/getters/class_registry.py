#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\class_registry.py
_class_map = {}

def get_class_map():
    return _class_map


from nodegraph.common.atomdata import get_atom_data
from .agent import *
from .blackboard import *
from .character import *
from .cosmetic import *
from .dungeon import *
from .fitting import *
from .inventory import *
from .language import *
from .location import *
from .module import *
from .npc import *
from .object import *
from .other import *
from .skill import *
from .target import *
from .ui import *
from .wallet import *
from .player import *
from .base import GetterAtom

def _map_classes(local_scope):
    for name, value in local_scope.items():
        if '__' in name:
            continue
        if isinstance(value, type) and issubclass(value, GetterAtom) and value.atom_id is not None and get_atom_data(value.atom_id):
            _class_map[value.atom_id] = value

    from nodegraph.common.atoms.getters.class_registry import get_class_map as get_common_class_map
    _class_map.update(get_common_class_map())


_map_classes(locals())
