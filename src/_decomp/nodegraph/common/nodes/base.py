#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\nodes\base.py
import caching
import log
from nodegraph.common.nodedata import get_node_type, get_node_input_parameter_dict, InPort
from nodegraph.common.atomdata import get_atom_data

class Node(object):
    node_type_id = None

    def __init__(self, graph = None, node_id = None, connections = None, node_parameters = None, **kwargs):
        self.graph = graph
        self.node_id = node_id
        self.connections = {}
        self.input_connections = set()
        self.node_parameters = {}
        self.variable_connections = {}
        for parameter_id in node_parameters:
            if node_parameters[parameter_id].connection:
                self.variable_connections[parameter_id] = node_parameters[parameter_id].connection
            else:
                self.node_parameters[parameter_id] = node_parameters[parameter_id]

        for key in connections:
            if key not in self.output_ports:
                log.LogError('Trying to construct an invalid node connection', self.node_id, key)
                continue
            self.connections[key] = list(connections[key])

    def update_variables(self, **kwargs):
        if not kwargs:
            return
        for key, value in kwargs.iteritems():
            self.update_variable(key, value)

    def update_variable(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)

    def start(self, **kwargs):
        self.graph.log.node_started(node_id=self.node_id, **kwargs)
        self._update_variables_from_connections()

    def stop(self, **kwargs):
        self.graph.log.node_stopped(node_id=self.node_id, **kwargs)

    def mark_active(self):
        self.graph.mark_node_active(self.node_id)

    def mark_inactive(self):
        self.graph.mark_node_inactive(self.node_id)

    def get_node_values(self, from_node_id):
        self.graph.log.node_get_values(node_id=self.node_id, from_node_id=from_node_id)
        if not self.is_flow_node:
            self._update_variables_from_connections()
        return self.get_values()

    def get_values(self):
        return None

    def get_connected_nodes(self):
        nodes = set()
        for connected_nodes in self.connections.itervalues():
            nodes.update(connected_nodes)

        return nodes

    def add_input_connection(self, node_id):
        self.input_connections.add(node_id)

    @property
    def is_active(self):
        return self.node_id in self.graph.active_node_ids

    def _update_variables_from_connections(self):
        from_node_values = {}
        for variable_connection_id, variable_connection in self.variable_connections.iteritems():
            from_node_id = variable_connection.node
            if from_node_id not in from_node_values:
                node = self.graph.get_node(from_node_id)
                from_node_values[from_node_id] = node.get_node_values(self.node_id) or {}
            self.update_variable(variable_connection_id, from_node_values[variable_connection.node].get(variable_connection.parameter, None))

    def _start_connection(self, connection_id, is_stopping = False, **kwargs):
        if not is_stopping and not self.graph.is_active:
            return
        self.graph.log.node_connection_started(node_id=self.node_id, connection=connection_id, is_stopping=is_stopping, **kwargs)
        connections = self.connections.get(connection_id, None)
        if not connections:
            return
        kwargs['from_node_id'] = self.node_id
        for node_id in connections:
            self.graph.start_node(node_id, is_stopping=is_stopping, **kwargs)

    def _stop_connection(self, connection_id, **kwargs):
        connections = self.connections.get(connection_id, None)
        if not connections:
            return
        self.graph.log.node_connection_stopped(node_id=self.node_id, connection=connection_id)
        kwargs['from_node_id'] = self.node_id
        for node_id in connections:
            self.graph.stop_node(node_id, **kwargs)

    @caching.lazy_property
    def output_ports(self):
        return get_node_type(self.node_type_id).ports.outPorts

    @caching.lazy_property
    def input_ports(self):
        return get_node_type(self.node_type_id).ports.inPorts

    @caching.lazy_property
    def is_flow_node(self):
        return InPort.input in self.input_ports

    @classmethod
    def get_node_parameter_value(cls, node_parameters, parameter_id, default = None):
        if parameter_id in node_parameters:
            return getattr(node_parameters[parameter_id], 'value', default)
        else:
            parameters = get_node_input_parameter_dict(cls.node_type_id)
            if parameter_id in parameters and parameters[parameter_id].defaultValue is not None:
                return parameters[parameter_id].defaultValue
            return default

    @classmethod
    def get_title(cls, node_data):
        return get_node_type(cls.node_type_id).name

    @classmethod
    def get_subtitle(cls, node_data):
        return ''


class AtomNode(Node):
    node_type_id = None

    def __init__(self, atom_parameters = None, **kwargs):
        super(AtomNode, self).__init__(**kwargs)
        self.atom_id = self.node_parameters['atom_id'].value
        self.atom_parameters = {}
        for parameter_id in atom_parameters or {}:
            if atom_parameters[parameter_id].connection:
                self.variable_connections[parameter_id] = atom_parameters[parameter_id].connection
            else:
                self.atom_parameters[parameter_id] = atom_parameters[parameter_id].value

        self.atom = None

    def update_variable(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        elif hasattr(self.atom, key):
            setattr(self.atom, key, value)

    @classmethod
    def get_atom_class(cls, atom_id):
        return None

    @classmethod
    def get_title(cls, node_data):
        return get_atom_data(node_data.nodeParameters['atom_id'].value).name

    @classmethod
    def get_subtitle(cls, node_data):
        try:
            atom_class = cls.get_atom_class(node_data.nodeParameters['atom_id'].value)
            if atom_class:
                return atom_class.get_subtitle(**{parameter_id:node_data.atomParameters[parameter_id].value for parameter_id in node_data.atomParameters or {} if not node_data.atomParameters[parameter_id].connection})
            return ''
        except Exception:
            node_parameters = getattr(node_data, 'nodeParameters', None)
            atom_id = node_parameters.get('atom_id', None) if node_parameters else None
            node_type_id = getattr(node_data, 'nodeType', None)
            position = getattr(node_data, 'position', None)
            log.LogWarn('Cannot display subtitle for node with atom ID: %s, node type ID: %s, position: %s' % (atom_id, node_type_id, position))
            return ''
