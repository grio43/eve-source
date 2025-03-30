#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\log_graph.py
from collections import defaultdict
import datetime
from nodegraph.common.nodedata import get_node_graph_data
from nodegraph.common.graph import NodeGraphLog, NodeGraphContext

class LogsNodeGraphs(object):

    def __init__(self):
        self.subscribed_to_logs = False
        self._graphs = {}
        self._sub_graphs = defaultdict(set)
        sm.RegisterForNotifyEvent(self, 'OnNodeGraphLog')

    def __del__(self):
        sm.UnregisterForNotifyEvent(self, 'OnNodeGraphLog')

    def OnNodeGraphLog(self, log):
        instance_id = log['node_graph_instance_id']
        if instance_id not in self._graphs:
            self._add_graph(log['node_graph_id'], instance_id, log['info'].get('parent_instance_id', None))
        self._graphs[instance_id].add_log(log)

    def get(self, instance_id):
        return self._graphs.get(instance_id, None)

    def get_all(self):
        return self._graphs

    def get_all_by_id(self, node_graph_id):
        result = []
        for instance_id, node_graph in self._graphs.iteritems():
            if node_graph.graph_id == node_graph_id:
                result.append(instance_id)

        return result

    def subscribe(self):
        if self.subscribed_to_logs:
            return
        self.subscribed_to_logs = True
        active_logs = sm.RemoteSvc('node_graph').qa_subscribe()
        ordered = []
        for instance_id, logs in active_logs.iteritems():
            parent_id = logs[0]['info'].get('parent_instance_id', None)
            if parent_id:
                if parent_id in ordered:
                    ordered.append(instance_id)
                else:
                    ordered.insert(0, instance_id)
            else:
                graph = self._add_graph(logs[0]['node_graph_id'], instance_id, parent_id)
                for log in logs:
                    graph.add_log(log)

        for instance_id in ordered:
            graph = self._add_graph(active_logs[instance_id][0]['node_graph_id'], instance_id, active_logs[instance_id][0]['info'].get('parent_instance_id', None))
            for log in active_logs[instance_id]:
                graph.add_log(log)

    def unsubscribe(self):
        if not self.subscribed_to_logs:
            return
        self.subscribed_to_logs = False
        self._graphs.clear()
        sm.RemoteSvc('node_graph').qa_unsubscribe()

    def stop_all(self):
        for graph in self._graphs.itervalues():
            graph.stop_node_graph()

        self._graphs.clear()

    def _add_graph(self, graph_id, instance_id, parent_instance_id):
        graph = LogsNodeGraph(graph_id=graph_id, instance_id=instance_id, parent_instance_id=parent_instance_id, get_graph=self.get)
        self._graphs[instance_id] = graph
        return graph


class LogsNodeGraph(object):

    def __init__(self, graph_id, instance_id, parent_instance_id, get_graph):
        self._get_graph = get_graph
        self.graph_id = graph_id
        self.instance_id = instance_id
        self.parent_instance_id = None
        self.active_node_ids = set()
        self.active_sub_graphs = set()
        self.is_active = False
        self.graph_data = get_node_graph_data(self.graph_id)
        self.log = NodeGraphLog(self.graph_id, self.instance_id)
        self.parent_instance_id = parent_instance_id
        if self.parent_instance_id:
            parent_graph = self._get_graph(self.parent_instance_id)
            parent_graph.active_sub_graphs.add(self.instance_id)
            self.context = parent_graph.context
        else:
            self.context = NodeGraphContext()
            self.context.subscribe_to_all_values(self._log_blackboard_value_change)

    def stop_node_graph(self):
        sm.RemoteSvc('node_graph').qa_stop_node_graph(self.instance_id)

    def start_node(self, node_id):
        sm.RemoteSvc('node_graph').qa_start_node(self.instance_id, node_id)

    def stop_node(self, node_id):
        sm.RemoteSvc('node_graph').qa_stop_node(self.instance_id, node_id)

    def stop_active_nodes(self):
        sm.RemoteSvc('node_graph').qa_stop_active_nodes(self.instance_id)

    def add_log(self, log):
        if log['type'] == 'node':
            if log['event'] == 'active':
                self.active_node_ids.add(log['info']['node_id'])
            elif log['event'] == 'inactive':
                self.active_node_ids.discard(log['info']['node_id'])
        elif log['type'] == 'graph':
            if log['event'] == 'started':
                self.is_active = True
                sm.ScatterEvent('OnNodeGraphStarted', instance_id=self.instance_id, node_graph_id=self.graph_id)
            elif log['event'] == 'stopped':
                self.is_active = False
                if self.parent_instance_id:
                    self._get_graph(self.parent_instance_id).active_sub_graphs.discard(self.instance_id)
                sm.ScatterEvent('OnNodeGraphStopped', instance_id=self.instance_id, node_graph_id=self.graph_id)
        elif log['type'] == 'blackboard':
            if log['event'] == 'update':
                self.context.update_value(log['info']['key'], log['info']['value'])
            return
        self.log.history.append(log)
        self.log.on_log(log)

    @property
    def nodes_data(self):
        return self.graph_data.nodes

    @property
    def name(self):
        return self.graph_data.name

    @property
    def description(self):
        return self.graph_data.description

    @property
    def tags(self):
        return self.graph_data.tags

    def _log_blackboard_value_change(self, key = None, value = None, old_value = None):
        self.log.blackboard_update(key=key, value=value, old_value=old_value)
