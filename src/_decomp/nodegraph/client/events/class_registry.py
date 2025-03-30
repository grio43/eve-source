#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\class_registry.py
_class_map = {}

def get_class_map():
    return _class_map


from nodegraph.common.atomdata import get_atom_data
from .acp import *
from .agency import *
from .agent import *
from .blinks import *
from .camera import *
from .chat import *
from .conversation import *
from .cosmetic import *
from .crimewatch import *
from .dungeon import *
from .fitting import *
from .industry import *
from .inventory import *
from .language import *
from .location import *
from .market import *
from .mission import *
from .module import *
from .navigation import *
from .new_eden_store import *
from .node_graph import *
from .opportunity import *
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
from .base import Event

def _map_classes(local_scope):
    for name, value in local_scope.items():
        if '__' in name:
            continue
        if isinstance(value, type) and issubclass(value, Event) and value.atom_id is not None and get_atom_data(value.atom_id):
            _class_map[value.atom_id] = value


_map_classes(locals())
