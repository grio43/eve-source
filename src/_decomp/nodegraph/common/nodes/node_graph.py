#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\nodes\node_graph.py
import logging
from nodegraph.common.nodes.base import Node
from nodegraph.common.nodedata import get_node_graph_data, OutPort
logger = logging.getLogger('node_graph')

class SubGraphNode(Node):
    node_type_id = 13

    def __init__(self, **kwargs):
        super(SubGraphNode, self).__init__(**kwargs)
        self.node_graph_id = self.get_node_parameter_value(self.node_parameters, 'node_graph_id')
        self.exclusive_key = self.get_node_parameter_value(self.node_parameters, 'exclusive_key')
        self.sub_graph = None
        self._blackboard_parameters = {}

    def update_variable(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)

    def start(self, is_stopping = False, **kwargs):
        if self.is_active:
            return
        super(SubGraphNode, self).start(**kwargs)
        if is_stopping:
            self._start_standalone_graph()
            return
        self.mark_active()
        self.sub_graph = self.graph.start_sub_graph(node_graph_id=self.node_graph_id, blackboard_parameters=self._blackboard_parameters, exclusive_key=self.exclusive_key)
        if self.sub_graph:
            self.sub_graph.on_stop.connect(self._on_stop)
            self._start_connection(OutPort.on_start, **kwargs)
        else:
            self.mark_inactive()

    def stop(self, **kwargs):
        if not self.is_active:
            return
        super(SubGraphNode, self).stop(**kwargs)
        if self.sub_graph:
            sm.GetService('node_graph').stop_node_graph(self.sub_graph.instance_id)

    def _on_stop(self):
        self.mark_inactive()
        self.sub_graph = None
        if self.graph.is_active:
            self._start_connection(OutPort.on_stop)

    def _start_standalone_graph(self):
        logger.debug('Starting a standalone graph from a SubGraphNode. node_graph_id: %s - parent_graph_id: %s (%s)', self.node_graph_id, self.graph.graph_id, self.graph.instance_id)
        sm.GetService('node_graph').start_node_graph(self.node_graph_id, blackboard_parameters=self.graph.context.values.copy())

    @classmethod
    def get_subtitle(cls, node_data):
        node_graph = get_node_graph_data(cls.get_node_parameter_value(node_data.nodeParameters, 'node_graph_id'))
        if node_graph:
            return node_graph.name
        return ''


class StopNodeGraph(Node):
    node_type_id = 12

    def start(self, **kwargs):
        super(StopNodeGraph, self).start(**kwargs)
        sm.GetService('node_graph').stop_node_graph(self.graph.instance_id)


class StopSubGraph(Node):
    node_type_id = 56

    def __init__(self, **kwargs):
        super(StopSubGraph, self).__init__(**kwargs)
        self.exclusive_key = self.get_node_parameter_value(self.node_parameters, 'exclusive_key')

    def start(self, **kwargs):
        super(StopSubGraph, self).start(**kwargs)
        self.graph.stop_sub_graph_by_exclusive_key(self.exclusive_key)
        self._start_connection(OutPort.output, **kwargs)


class StopActiveNodes(Node):
    node_type_id = 14

    def start(self, **kwargs):
        super(StopActiveNodes, self).start(**kwargs)
        self.graph.stop_active_nodes()
        self._start_connection(OutPort.output, **kwargs)


class NodeGraphStopped(Node):
    node_type_id = 20

    def __init__(self, **kwargs):
        super(NodeGraphStopped, self).__init__(**kwargs)
        self.graph.start_active_node_ids.append(self.node_id)

    def start(self, **kwargs):
        super(NodeGraphStopped, self).start(**kwargs)
        self.graph.on_stop.connect(self._on_stop)

    def _on_stop(self):
        self._start_connection(OutPort.output, is_stopping=True)


class NodeGraphMessageListener(Node):
    node_type_id = 31

    def __init__(self, **kwargs):
        super(NodeGraphMessageListener, self).__init__(**kwargs)
        self.message_key = self.get_node_parameter_value(self.node_parameters, 'message_key')
        self.keep_listening = self.get_node_parameter_value(self.node_parameters, 'keep_listening')
        self._cached_values = {}

    def get_values(self):
        return self._cached_values

    def start(self, **kwargs):
        if self.is_active:
            return
        super(NodeGraphMessageListener, self).start(**kwargs)
        self.mark_active()
        self.graph.context.subscribe_to_message(self.message_key, self._message_received)

    def stop(self, **kwargs):
        if not self.is_active:
            return
        super(NodeGraphMessageListener, self).stop(**kwargs)
        self.graph.context.unsubscribe_from_message(self.message_key, self._message_received)
        self.mark_inactive()

    def _message_received(self, key, value, *args, **kwargs):
        valid = True
        kwargs['from_node_id'] = self.node_id
        kwargs[key] = value
        kwargs['value'] = value
        self._cached_values['key'] = key
        self._cached_values['value'] = value
        self._cached_values[key] = value
        for node_id in self.connections.get(OutPort.validation, []):
            valid_node = self.graph.start_node(node_id, **kwargs)
            if valid_node is False:
                valid = False
                break

        if not valid:
            return
        if not self.keep_listening:
            self.stop()
        self._start_connection(OutPort.output, **kwargs)

    @classmethod
    def get_subtitle(cls, node_data):
        result = [cls.get_node_parameter_value(node_data.nodeParameters, 'message_key', '')]
        if cls.get_node_parameter_value(node_data.nodeParameters, 'keep_listening'):
            result.append('KeepListening')
        return ' - '.join(result)


class SendMessageToNodeGraphNode(Node):
    node_type_id = 42

    def __init__(self, **kwargs):
        super(SendMessageToNodeGraphNode, self).__init__(**kwargs)
        self.message_key = self.get_node_parameter_value(self.node_parameters, 'message_key')
        self.message_value = self.get_node_parameter_value(self.node_parameters, 'message_value')

    def start(self, **kwargs):
        super(SendMessageToNodeGraphNode, self).start(**kwargs)
        self.graph.context.send_message(self.message_key, self.message_value)
        self._start_connection(OutPort.output, **kwargs)

    @classmethod
    def get_subtitle(cls, node_data):
        return u'{}:{}'.format(cls.get_node_parameter_value(node_data.nodeParameters, 'message_key', ''), cls.get_node_parameter_value(node_data.nodeParameters, 'message_value', ''))


class BlackboardTriggeredSubgraphNode(SubGraphNode):
    node_type_id = 41

    def __init__(self, **kwargs):
        super(BlackboardTriggeredSubgraphNode, self).__init__(**kwargs)
        self.blackboard_key = self.get_node_parameter_value(self.node_parameters, 'blackboard_key')
        self.blackboard_value = self.get_node_parameter_value(self.node_parameters, 'blackboard_value')

    def start(self, **kwargs):
        super(BlackboardTriggeredSubgraphNode, self).start(start_active=True, **kwargs)
        if self.is_active:
            return
        self.mark_active()
        self.graph.context.subscribe_to_value(self.blackboard_key, self._blackboard_value_changed)
        blackboard_value = self.graph.context.get_value(self.blackboard_key)
        if blackboard_value:
            self._blackboard_value_changed(blackboard_value)

    def stop(self, **kwargs):
        super(BlackboardTriggeredSubgraphNode, self).start(**kwargs)
        if not self.is_active:
            return
        self.mark_inactive()
        self.graph.context.unsubscribe_from_value(self.blackboard_key, self._blackboard_value_changed)

    def _blackboard_value_changed(self, value, **kwargs):
        if value == self.blackboard_value:
            super(BlackboardTriggeredSubgraphNode, self).start()
        else:
            super(BlackboardTriggeredSubgraphNode, self).stop()

    @classmethod
    def get_subtitle(cls, node_data):
        key = cls.get_node_parameter_value(node_data.nodeParameters, 'blackboard_key')
        value = cls.get_node_parameter_value(node_data.nodeParameters, 'blackboard_value')
        node_graph_id = cls.get_node_parameter_value(node_data.nodeParameters, 'node_graph_id')
        node_graph = get_node_graph_data(node_graph_id)
        return '{key}:{value} {graph_name}({graph_id})'.format(key=key, value=value, graph_name=node_graph.name if node_graph else '<Not found>', graph_id=node_graph_id)
