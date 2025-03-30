#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\class_registry.py
_class_map = {}

def get_class_map():
    return _class_map


from nodegraph.common.atomdata import get_atom_data
from .acp import *
from .agency import *
from .agent import *
from .attribute import *
from .camera import *
from .character import *
from .corporations import *
from .corporation_projects import *
from .cosmetic import *
from .crimewatch import *
from .fitting import *
from .industry import *
from .inrange import *
from .inventory import *
from .language import *
from .launch_darkly import *
from .location import *
from .market import *
from .mission import *
from .module import *
from .navigation import *
from .new_eden_store import *
from .node_graph import *
from .parameters import *
from .redeem import *
from .session import *
from .ship import *
from .skill import *
from .target import *
from .travel import *
from .tutorial import *
from .ui import *
from .wallet import *
from .window import *
from .base import Condition

def _map_classes(local_scope):
    for name, value in local_scope.items():
        if '__' in name:
            continue
        if isinstance(value, type) and issubclass(value, Condition) and value.atom_id is not None and get_atom_data(value.atom_id):
            _class_map[value.atom_id] = value

    from nodegraph.common.atoms.conditions.class_registry import get_class_map as get_common_class_map
    _class_map.update(get_common_class_map())


_map_classes(locals())
