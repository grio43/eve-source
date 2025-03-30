#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\controllers\node_controller.py
import signals
import eveformat
from nodegraph.common.nodedata import get_node_type, InPort
from nodegraph.common.atomdata import get_atom_data
from nodegraph.client.nodes import get_node_class
from nodegraph.client.ui.node import BaseNode, AuthoredNode

class NodeViewController(object):
    node_component_class = BaseNode

    def __init__(self, node_id, graph_controller):
        self.node_id = node_id
        self._graph_controller = graph_controller
        self.on_selection_changed = signals.Signal('on_selection_changed')

    def on_log(self, log):
        pass

    def get_context_menu(self):
        if self._is_multiple_selected():
            return []
        result = [('Copy nodeID: %s' % self.node_id, lambda *args: _copy_value(self.node_id)), ('Copy nodeTypeID: %s (%s)' % (self.node_info.name, self.node_type), lambda *args: _copy_value(self.node_type))]
        if self.atom_info:
            atom_id = self.node_data.nodeParameters['atom_id'].value
            result += [('Copy atomID: %s (%s)' % (self.atom_info.name, atom_id), lambda *args: _copy_value(atom_id))]
        return result

    def get_parameter_value(self, parameter_id):
        node_parameters = self.node_data.nodeParameters or {}
        if not node_parameters:
            return None
        if parameter_id in node_parameters:
            return _get_value_from_parameters(node_parameters, parameter_id)
        atom_parameters = self.node_data.atomParameters or {}
        if not atom_parameters:
            return None
        if parameter_id in atom_parameters:
            return _get_value_from_parameters(atom_parameters, parameter_id)

    @property
    def is_selected(self):
        return self.node_id in self._graph_controller.selected_nodes

    @property
    def node_data(self):
        return self._graph_controller.get_node_data(self.node_id)

    @property
    def node_info(self):
        return get_node_type(self.node_type)

    @property
    def atom_info(self):
        node_data = self.node_data
        if 'atom_id' in node_data.nodeParameters:
            return get_atom_data(node_data.nodeParameters['atom_id'].value)

    @property
    def node_type(self):
        return self.node_data.nodeType

    @property
    def node_class(self):
        return get_node_class(self.node_type)

    @property
    def title(self):
        node_class = self.node_class
        if node_class:
            return node_class.get_title(self.node_data)
        return self._get_atom_or_node_info().name

    @property
    def subtitle(self):
        node_class = self.node_class
        if node_class:
            return node_class.get_subtitle(self.node_data)
        return ''

    @property
    def description(self):
        return self._get_atom_or_node_info().description or ''

    @property
    def tags(self):
        return self._get_atom_or_node_info().tags

    @property
    def comment(self):
        return self.node_data.comment

    @property
    def output_description(self):
        outputs = []
        for parameter in self.output_parameters:
            outputs.append('{} ({})'.format(parameter.parameterKey, parameter.parameterType))

        return '\n'.join(outputs)

    @property
    def color(self):
        return self.node_info.color[:3]

    @property
    def input_ports(self):
        return self.node_info.ports.inPorts

    @property
    def output_ports(self):
        return self.node_info.ports.outPorts

    @property
    def node_input_parameters(self):
        return self.node_info.parameters.inputs

    @property
    def node_output_parameters(self):
        return self.node_info.parameters.outputs

    @property
    def atom_input_parameters(self):
        atom_info = self.atom_info
        if atom_info:
            return atom_info.parameters.inputs
        return []

    @property
    def atom_output_parameters(self):
        atom_info = self.atom_info
        if atom_info:
            return atom_info.parameters.outputs
        return []

    @property
    def input_parameters(self):
        return list(self.node_input_parameters) + list(self.atom_input_parameters)

    @property
    def output_parameters(self):
        return list(self.node_output_parameters) + list(self.atom_output_parameters)

    def _get_atom_or_node_info(self):
        return self.atom_info or self.node_info

    def _is_multiple_selected(self):
        if not self._graph_controller.selected_nodes:
            return False
        return len(self._graph_controller.selected_nodes) > 1 and self.node_id in self._graph_controller.selected_nodes


class AuthoredNodeViewController(NodeViewController):
    node_component_class = AuthoredNode

    def get_context_menu(self):
        m = super(AuthoredNodeViewController, self).get_context_menu()
        if self._is_multiple_selected():
            result = [('MULTIPLE NODES SELECTED', None), ('Copy to clipboard', lambda : self._graph_controller.copy_nodes_to_clipboard(self._graph_controller.selected_nodes))]
            return m + result
        else:
            result = [('Copy node data', lambda : self._graph_controller.copy_nodes_to_clipboard([self.node_id])), None]
            return result + m

    def update_parameter(self, parameter_id, value):
        pass

    def update_parameter_connection(self, parameter_id, connection_node_id, connection_parameter_id):
        pass

    def move(self, position):
        pass


def _get_value_from_parameters(parameters, parameter_id):
    if parameter_id not in parameters:
        return None
    if parameters[parameter_id].connection:
        return 'connection'
    return parameters[parameter_id].value


def _copy_value(value):
    import blue
    return blue.pyos.SetClipboardData(unicode(value))
