#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\graph.py
import abc
import uuid
import gametime
import logging
import signals
import threadutils
import uthread2
from nodegraph.common.nodedata import get_node_graph_data, get_remote_graph_id_from_data, get_scope_from_data
from nodegraph.common.context import NodeGraphContext
from nodegraph.common.log import NodeGraphLog
logger = logging.getLogger('node_graph')

class BaseNodeGraph(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, graph_id = None, instance_id = None, parent_graph = None, context = None, blackboard_parameters = None, graph_data = None, message_handlers = None, exclusive_key = None):
        self._are_nodes_constructed = False
        self._are_nodes_started = False
        self.graph_id = graph_id
        self.instance_id = instance_id or str(uuid.uuid4())
        self.graph_data = graph_data or get_node_graph_data(self.graph_id)
        self.exclusive_key = exclusive_key
        self.all_nodes = {}
        self.active_node_ids = set()
        self.active_sub_graphs = set()
        self._is_active = False
        self.on_stop = signals.Signal('on_stop')
        self.start_active_node_ids = []
        self.log = NodeGraphLog(self.graph_id, self.instance_id)
        self.parent_instance_id = parent_graph.instance_id if parent_graph else None
        self.start_time = gametime.GetWallclockTime()
        self.log.graph_starting(parent_instance_id=self.parent_instance_id)
        if parent_graph:
            self.context = parent_graph.context
            parent_graph.add_sub_graph(self.instance_id, self.exclusive_key)
        else:
            self.context = context or NodeGraphContext()
            self.context.subscribe_to_all_values(self._log_blackboard_value_change)
            if context:
                for key, value in self.context.values.iteritems():
                    self._log_blackboard_value_change(key=key, value=value)

            self.context.update_value('root_graph_instance_id', self.instance_id)
        if blackboard_parameters:
            self.context.set_values(**blackboard_parameters)
        if message_handlers:
            self.context.add_message_handlers(message_handlers)
        self._create_nodes()

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
    def parent_graph_id(self):
        return self.graph_data.parentGraph

    @property
    def remote_graph_id(self):
        return get_remote_graph_id_from_data(self.graph_data)

    @property
    def scope(self):
        return get_scope_from_data(self.graph_data)

    @property
    def tags(self):
        return self.graph_data.tags

    @property
    def is_active(self):
        return self._is_active

    @property
    def is_root_graph(self):
        return self.context.get_value('root_graph_instance_id') == self.instance_id

    def start_node_graph(self, wait_while_nodes_start = False):
        self._wait_while_nodes_construct()
        self._start_node_graph()
        if wait_while_nodes_start:
            self._wait_while_nodes_start()

    def _wait_while_nodes_construct(self):
        while not self._are_nodes_constructed:
            uthread2.Yield()

    def _wait_while_nodes_start(self):
        while not self._are_nodes_started:
            uthread2.Yield()

    @threadutils.threaded
    def _start_node_graph(self):
        if self._is_active:
            return
        if self.instance_id not in self.service.get_active_node_graphs():
            return
        self._is_active = True
        sm.ScatterEvent('OnNodeGraphStarted', instance_id=self.instance_id, node_graph_id=self.graph_id)
        self.log.graph_started(parent_instance_id=self.parent_instance_id)
        try:
            for node_id in self.start_active_node_ids:
                self.start_node(node_id)

        except Exception as exc:
            logger.exception('Failed to start root nodes in graph %s - %s', self.graph_id, exc)

        self._are_nodes_started = True

    def stop_node_graph(self, clear_context = False):
        if not self._is_active:
            return
        self._is_active = False
        self._stop_node_graph(clear_context=clear_context)

    @threadutils.threaded
    def _stop_node_graph(self, clear_context = False):
        self.stop_active_nodes()
        self.on_stop()
        if self.parent_instance_id:
            parent_graph = self.service.get_active_node_graph(self.parent_instance_id)
            if parent_graph:
                parent_graph.active_sub_graphs.discard(self.instance_id)
        self.log.graph_stopped()
        sm.ScatterEvent('OnNodeGraphStopped', instance_id=self.instance_id, node_graph_id=self.graph_id)
        if clear_context and self.is_root_graph:
            self.context.clear()

    def stop_active_nodes(self):
        for node_id in self.active_node_ids.copy():
            self.stop_node(node_id)

    def stop_sub_graph_by_exclusive_key(self, exclusive_key):
        if not exclusive_key:
            return
        for instance_id in self.active_sub_graphs.copy():
            graph = self.service.get_active_node_graph(instance_id)
            if graph and graph.exclusive_key == exclusive_key:
                self.service.stop_node_graph(instance_id)

    def get_node(self, node_id):
        return self.all_nodes[node_id]

    def start_node(self, node_id, **kwargs):
        return self.all_nodes[node_id].start(**kwargs)

    def stop_node(self, node_id, **kwargs):
        self.all_nodes[node_id].stop(**kwargs)

    def mark_node_active(self, node_id):
        if node_id not in self.active_node_ids:
            self.active_node_ids.add(node_id)
            self.log.node_active(node_id=node_id)

    def mark_node_inactive(self, node_id):
        if node_id in self.active_node_ids:
            self.active_node_ids.remove(node_id)
            self.log.node_inactive(node_id=node_id)

    def start_sub_graph(self, node_graph_id, blackboard_parameters, exclusive_key = None):
        return self.service.start_node_graph(node_graph_id, node_graph_parent_id=self.instance_id, blackboard_parameters=blackboard_parameters, exclusive_key=exclusive_key)

    def add_sub_graph(self, sub_graph_instance_id, exclusive_key):
        if exclusive_key:
            for instance_id in self.active_sub_graphs.copy():
                if instance_id == sub_graph_instance_id:
                    continue
                graph = self.service.get_active_node_graph(instance_id)
                if graph and graph.exclusive_key == exclusive_key:
                    self.service.stop_node_graph(instance_id)

        self.active_sub_graphs.add(sub_graph_instance_id)

    @threadutils.threaded
    def _create_nodes(self):
        for node_id, node_data in self.nodes_data.iteritems():
            self._create_node(node_id, node_data)

        for node_id in self.all_nodes:
            for connected_node_id in self.all_nodes[node_id].get_connected_nodes():
                self.all_nodes[connected_node_id].add_input_connection(node_id)

        self.context.send_message('nodes_initialized')
        self._are_nodes_constructed = True

    def _create_node(self, node_id, node_data):
        try:
            node_class = self._get_node_class(node_data.nodeType)
            node = node_class(graph=self, node_id=node_id, connections=node_data.connections, node_parameters=node_data.nodeParameters, atom_parameters=getattr(node_data, 'atomParameters', None))
            self.all_nodes[node_id] = node
        except Exception as exc:
            logger.exception('Failed to construct node %s in graph %s - %s', node_id, self.graph_id, exc)

    @abc.abstractmethod
    def _get_node_class(self, node_type):
        pass

    @property
    def service(self):
        return sm.GetService('node_graph')

    def _log_blackboard_value_change(self, key = None, value = None, old_value = None):
        self.log.blackboard_update(key=key, value=value, old_value=old_value)
