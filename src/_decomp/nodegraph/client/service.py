#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\service.py
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_SERVICE
from nodegraph.client.graph import ClientNodeGraph
from nodegraph.client.log_graph import LogsNodeGraphs
from nodegraph.common.nodedata import is_client_graph

class NodeGraphService(Service):
    __guid__ = 'svc.node_graph'
    __displayname__ = 'Node Graph Service'
    __notifyevents__ = ['ProcessSessionReset',
     'OnStartClientNodeGraph',
     'OnStopClientNodeGraph',
     'OnStopClientNodeGraphById',
     'OnStopAllClientNodeGraphs',
     'OnClientNodeGraphUpdate',
     'OnClientNodeGraphMessage']
    __dependencies__ = []
    __exportedcalls__ = {'StartClientNodeGraph': [ROLE_SERVICE],
     'StopClientNodeGraphById': [ROLE_SERVICE]}

    def __init__(self):
        super(NodeGraphService, self).__init__()
        _map_nodes_and_atoms()
        self._active_graphs = {}
        self.log_graphs = LogsNodeGraphs()

    def ProcessSessionReset(self):
        for node_graph_instance_id in self.get_active_root_graph_ids():
            self.stop_node_graph(node_graph_instance_id)

    def OnStartClientNodeGraph(self, node_graph_id, node_graph_instance_id, blackboard_parameters):
        self.start_node_graph(node_graph_id, node_graph_instance_id=node_graph_instance_id, blackboard_parameters=blackboard_parameters)

    def OnStopClientNodeGraph(self, node_graph_instance_id):
        self.stop_node_graph(node_graph_instance_id)

    def OnStopClientNodeGraphById(self, node_graph_id):
        self.stop_node_graph_by_id(node_graph_id)

    def OnStopAllClientNodeGraphs(self):
        self.stop_all_node_graphs()

    def OnClientNodeGraphUpdate(self, node_graph_instance_id, blackboard_parameters):
        node_graph = self.get_active_node_graph(node_graph_instance_id)
        if node_graph and blackboard_parameters:
            for key, value in blackboard_parameters.iteritems():
                node_graph.context.update_value(key, value)

    def OnClientNodeGraphMessage(self, node_graph_instance_id, key, value):
        node_graph = self.get_active_node_graph(node_graph_instance_id)
        if node_graph:
            node_graph.context.send_message(key, value)

    def StartClientNodeGraph(self, node_graph_id, blackboard_parameters):
        graph = self.start_node_graph(node_graph_id, blackboard_parameters=blackboard_parameters, wait_while_nodes_start=False)
        return graph.instance_id

    def StopClientNodeGraphById(self, node_graph_id):
        instance_ids = self.stop_node_graph_by_id(node_graph_id)
        return instance_ids

    def start_node_graph(self, node_graph_id, node_graph_instance_id = None, node_graph_parent_id = None, context = None, blackboard_parameters = None, message_handlers = None, exclusive_key = None, wait_while_nodes_start = False):
        if not is_client_graph(node_graph_id):
            raise ValueError('%s is not a client graph' % node_graph_id)
        parent_graph = None
        if node_graph_parent_id:
            if node_graph_parent_id not in self._active_graphs:
                self.LogError('Parent graph', node_graph_parent_id, 'is not in active graphs, when starting', node_graph_id)
                return
            parent_graph = self._active_graphs[node_graph_parent_id]
        node_graph = ClientNodeGraph(node_graph_id, instance_id=node_graph_instance_id, parent_graph=parent_graph, context=context, blackboard_parameters=blackboard_parameters, message_handlers=message_handlers, exclusive_key=exclusive_key)
        self._active_graphs[node_graph.instance_id] = node_graph
        node_graph.start_node_graph(wait_while_nodes_start=wait_while_nodes_start)
        return node_graph

    def stop_node_graph(self, node_graph_instance_id, clear_context = False):
        graph = self._active_graphs.pop(node_graph_instance_id, None)
        if graph:
            graph.stop_node_graph(clear_context=clear_context)

    def stop_node_graph_by_id(self, node_graph_id, clear_context = False):
        instance_ids = self.get_active_instances_by_id(node_graph_id)
        for instance_id in instance_ids:
            self.stop_node_graph(instance_id, clear_context=clear_context)

        return instance_ids

    def stop_all_node_graphs(self):
        for instance_id in self.get_active_root_graph_ids():
            self.stop_node_graph(instance_id, clear_context=True)

    def get_active_node_graphs(self):
        return self._active_graphs

    def get_active_root_graph_ids(self):
        return [ node_graph_instance_id for node_graph_instance_id, graph in self._active_graphs.iteritems() if graph.parent_instance_id is None ]

    def get_active_node_graph(self, node_graph_instance_id):
        return self._active_graphs.get(node_graph_instance_id, None)

    def get_active_node_graph_by_id(self, node_graph_id):
        if node_graph_id:
            for node_graph in self._active_graphs.values():
                if node_graph.graph_id == node_graph_id:
                    return node_graph

    def get_active_instances_by_id(self, node_graph_id):
        result = []
        for instance_id, node_graph in self._active_graphs.iteritems():
            if node_graph.graph_id == node_graph_id:
                result.append(instance_id)

        return result

    def qa_start_node_graph(self, node_graph_id, blackboard_parameters = None):
        self._manager.qa_start_node_graph(node_graph_id, blackboard_parameters)

    @property
    def _manager(self):
        return sm.RemoteSvc('node_graph')

    def get_root_instance_id(self, instance_id):
        graph = self.get_active_node_graph(instance_id)
        if graph.parent_instance_id is None:
            return instance_id
        else:
            return self.get_root_instance_id(graph.parent_instance_id)


def _map_nodes_and_atoms():
    from nodegraph.client.nodes import get_all_node_classes
    from nodegraph.client.actions import get_all_atom_action_classes
    from nodegraph.client.conditions import get_all_atom_condition_classes
    from nodegraph.client.events import get_all_atom_event_classes
    from nodegraph.client.getters import get_all_atom_getter_classes
    _ = get_all_node_classes()
    _ = get_all_atom_action_classes()
    _ = get_all_atom_condition_classes()
    _ = get_all_atom_event_classes()
    _ = get_all_atom_getter_classes()
