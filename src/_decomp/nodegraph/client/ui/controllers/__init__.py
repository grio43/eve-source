#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\controllers\__init__.py
import blue
import utillib
from .graph_controller import NodeGraphViewController, AuthoredNodeGraphViewController

class NodeGraphViewControllerStorage(object):

    def __init__(self):
        self._authored_graphs = {}
        self._graph_settings = {}
        if blue.pyos.packaged:
            self._authored_controller_class = NodeGraphViewController
        else:
            self._authored_controller_class = AuthoredNodeGraphViewController

    def get_node_graph(self, node_graph_id):
        if node_graph_id not in self._authored_graphs:
            self._authored_graphs[node_graph_id] = self._authored_controller_class(node_graph_id)
        graph = self._authored_graphs[node_graph_id]
        graph.initialize()
        return graph

    def get_graph_settings(self, node_graph_id):
        if node_graph_id not in self._graph_settings:
            self._graph_settings[node_graph_id] = utillib.KeyVal(zoom_level=1, pan_left=0.0, pan_top=0.0)
        return self._graph_settings[node_graph_id]


_node_graph_controller_storage = None

def get_node_graph_view_controller_storage():
    global _node_graph_controller_storage
    if _node_graph_controller_storage is None:
        _node_graph_controller_storage = NodeGraphViewControllerStorage()
    return _node_graph_controller_storage


def get_node_graph_view_controller(node_graph_id):
    return get_node_graph_view_controller_storage().get_node_graph(node_graph_id)


def get_node_graph_settings(node_graph_id):
    return get_node_graph_view_controller_storage().get_graph_settings(node_graph_id)
