#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\nodes\event.py
from nodegraph.common.nodes.base import Node, AtomNode
from nodegraph.common.nodedata import OutPort

class EventNode(AtomNode):
    node_type_id = 5

    def __init__(self, **kwargs):
        super(EventNode, self).__init__(**kwargs)
        self.keep_listening = self.get_node_parameter_value(self.node_parameters, 'keep_listening')
        self.validate_on_start = self.get_node_parameter_value(self.node_parameters, 'validate_on_start')
        self.atom = self.get_atom_class(self.atom_id)(callback=self.invoke, **self.atom_parameters)
        self._cached_output = {}

    def get_values(self):
        return self._cached_output

    def start(self, **kwargs):
        if self.is_active:
            return
        super(EventNode, self).start(**kwargs)
        self.mark_active()
        self.atom.start()
        if self.validate_on_start:
            self.invoke()

    def stop(self, **kwargs):
        if not self.is_active:
            return
        super(EventNode, self).stop(**kwargs)
        self.mark_inactive()
        self.atom.stop()

    def invoke(self, **kwargs):
        valid = True
        kwargs.pop('node_id', None)
        kwargs['from_node_id'] = self.node_id
        self._cached_output = kwargs
        validators = self.connections.get(OutPort.validation, [])
        for node_id in validators:
            valid_node = self.graph.start_node(node_id, **kwargs)
            if valid_node is False:
                valid = False
                break

        if not valid:
            self.atom.start()
            return
        if not self.keep_listening:
            self.stop()
        else:
            self.atom.start()
        self._start_connection(OutPort.output, **kwargs)

    @classmethod
    def get_subtitle(cls, node_data):
        result = []
        if cls.get_node_parameter_value(node_data.nodeParameters, 'keep_listening'):
            result.append('KeepListening')
        if cls.get_node_parameter_value(node_data.nodeParameters, 'validate_on_start'):
            result.append('ValidateOnStart')
        base_subtitle = super(EventNode, cls).get_subtitle(node_data)
        if base_subtitle:
            result.append(base_subtitle)
        return ' - '.join(result)


class EventGroupNode(Node):
    node_type_id = 8

    def __init__(self, **kwargs):
        super(EventGroupNode, self).__init__(**kwargs)
        require_all = self.get_node_parameter_value(self.node_parameters, 'require_all')
        self.keep_listening = self.get_node_parameter_value(self.node_parameters, 'keep_listening')
        self.wait_seconds = self.get_node_parameter_value(self.node_parameters, 'wait_seconds')
        if require_all:
            self.goal_value = len(self.connections.get(OutPort.group_nodes, []))
        else:
            self.goal_value = 1
        self.triggered_nodes = set()
        self.wait_thread = None
        self.should_we_wait = self._should_we_wait()

    def _should_we_wait(self):
        from carbon.common.script.util.mathCommon import FloatCloseEnough
        if self.wait_seconds is None or self.wait_seconds < 0 or FloatCloseEnough(self.wait_seconds, 0):
            return False
        return True

    def start(self, from_node_id = None, **kwargs):
        import blue
        from uthread2 import call_after_wallclocktime_delay
        if from_node_id not in self.connections.get(OutPort.group_nodes, []):
            self._start_group_nodes(kwargs)
            return
        if from_node_id in self.triggered_nodes:
            return
        self.triggered_nodes.add(from_node_id)
        if len(self.triggered_nodes) == self.goal_value:
            self.triggered_nodes.clear()
            if self.should_we_wait:
                if not self.wait_thread:
                    self.wait_thread = call_after_wallclocktime_delay(self._stop_and_output, self.wait_seconds, **kwargs)
                blue.pyos.synchro.Yield()
            else:
                self._stop_and_output(**kwargs)

    def _are_we_waiting(self):
        return bool(self.wait_thread)

    def _stop_and_output(self, **kwargs):
        if not self.is_active:
            return
        if not self.keep_listening:
            self._stop_connection(OutPort.group_nodes)
        self._start_connection(OutPort.output, **kwargs)
        self.triggered_nodes.clear()
        if not self.keep_listening:
            self.stop()
        self.wait_thread = None

    def stop(self, **kwargs):
        if not self.is_active:
            return
        self.mark_inactive()
        if self.wait_thread:
            self.wait_thread.kill()
            self.wait_thread = None

    def _start_group_nodes(self, kwargs):
        if self.is_active:
            return
        self.mark_active()
        for node_id in self.connections.get(OutPort.group_nodes, []):
            node = self.graph.get_node(node_id)
            if node_id not in node.connections.get(OutPort.output, []):
                if OutPort.output not in node.connections:
                    node.connections[OutPort.output] = []
                node.connections[OutPort.output].append(self.node_id)
            self.graph.start_node(node_id, **kwargs)

    @classmethod
    def get_subtitle(cls, node_data):
        result = []
        if cls.get_node_parameter_value(node_data.nodeParameters, 'keep_listening'):
            result.append('KeepListening')
        if cls.get_node_parameter_value(node_data.nodeParameters, 'require_all'):
            result.append('RequireAll')
        else:
            result.append('RequireAny')
        return ' - '.join(result)
