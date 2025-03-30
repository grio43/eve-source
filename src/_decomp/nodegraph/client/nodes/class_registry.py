#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\nodes\class_registry.py
_class_map = {}

def get_class_map():
    return _class_map


from nodegraph.common.nodedata import get_node_type
from nodegraph.common.nodes import *
from .atom import ClientActionNode, ClientEventNode, ClientGetterNode, ClientValidationNode
from .metrics import ReportContext
from .mission import MissionObjectiveNode
from .node_graph import SendMessageToServerGraph
from .other import WaitForSession
from nodegraph.common.nodes.base import Node

def _map_classes(local_scope):
    for name, value in local_scope.items():
        if '__' in name:
            continue
        if isinstance(value, type) and issubclass(value, Node) and value.node_type_id is not None and get_node_type(value.node_type_id):
            _class_map[value.node_type_id] = value


_map_classes(locals())
