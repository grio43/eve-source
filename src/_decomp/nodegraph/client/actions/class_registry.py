#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\class_registry.py
_class_map = {}

def get_class_map():
    return _class_map


from nodegraph.common.atomdata import get_atom_data
from .agent import *
from .audio import *
from .blinks import *
from .button import *
from .camera import *
from .character import *
from .commands import *
from .conversation import *
from .corporation_projects import *
from .crimewatch import *
from .dungeon import *
from .effects import *
from .highlights import *
from .input import *
from .inventory import *
from .language import *
from .launch_darkly import *
from .market import *
from .module import *
from .navigation import *
from .new_eden_store import *
from .objectives import *
from .opportunity import *
from .other import *
from .overview import *
from .qa import *
from .scene import *
from .skill import *
from .target import *
from .tutorial import *
from .ui import *
from .base import Action

def _map_classes(local_scope):
    for name, value in local_scope.items():
        if '__' in name:
            continue
        if isinstance(value, type) and issubclass(value, Action) and value.atom_id is not None and get_atom_data(value.atom_id):
            _class_map[value.atom_id] = value


_map_classes(locals())
