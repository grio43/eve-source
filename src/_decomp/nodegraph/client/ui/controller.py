#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\controller.py
from copy import deepcopy
import blue
import signals
import threadutils
from utillib import KeyVal
import uthread2
import uuid
import eveformat
from nodegraph.common.nodedata import get_node_graph_data, reload_node_graph_data, get_node_type, get_remote_graph_id_from_data, get_scope_from_data
from nodegraph.common.atomdata import get_atom_data
from nodegraph.client.graph import ClientNodeGraph
from nodegraph.client.nodes import get_node_class
from nodegraph.client.custom_graph import get_custom_node_graph, get_custom_node_graph_authored_id, get_custom_node_graphs, save_custom_node_graphs, delete_custom_node_graph, customize_fsd_graph, save_fsd_node_graph, update_parameter, update_parameter_connection, get_new_node_data, copy_graph_to_clipboard, convert_to_dict_nodes, convert_from_clipboard

def open_node_graph(node_graph_id):
    from nodegraph.client.ui.window import NodeGraphEditorWindow
    NodeGraphEditorWindow.Open(node_graph_id=node_graph_id)


class NodeGraphController(object):

    def __init__(self, node_graph_id):
        self.node_graph_id = node_graph_id
        self.node_graph = None
        self.selected_nodes = set()
        self._settings = None
        self._node_controllers = {}
        self.on_update = signals.Signal('on_update')
        self.on_selected_nodes = signals.Signal('on_selected_nodes')
        self.on_focus_node = signals.Signal('on_focus_node')
        self.on_highlight_node = signals.Signal('on_highlight_node')
        sm.RegisterForNotifyEvent(self, 'OnNodeGraphStarted')
        sm.RegisterForNotifyEvent(self, 'OnNodeGraphStopped')
        self._initialize()

    def _initialize(self):
        from .controllers import get_node_graph_settings
        self._settings = get_node_graph_settings(self.node_graph_id)

    def close(self):
        sm.UnregisterForNotifyEvent(self, 'OnNodeGraphStarted')
        sm.UnregisterForNotifyEvent(self, 'OnNodeGraphStopped')

    def OnNodeGraphStarted(self, instance_id, node_graph_id):
        node_graph = self.service.get_active_node_graph(instance_id) or self.service.log_graphs.get(instance_id)
        if node_graph and node_graph.graph_id == self.node_graph_id:
            if hasattr(self.node_graph, 'instance_id'):
                self.on_update()
            else:
                open_node_graph(instance_id)

    def OnNodeGraphStopped(self, instance_id, node_graph_id):
        if node_graph_id == self.node_graph_id:
            self.on_update()

    @property
    def service(self):
        return sm.GetService('node_graph')

    @property
    def name(self):
        return self.node_graph.name

    @property
    def description(self):
        return self.node_graph.description

    @property
    def nodes_data(self):
        return self.node_graph.nodes_data

    @property
    def parent_graph_id(self):
        return self.node_graph.parent_graph_id

    @property
    def tags(self):
        return self.node_graph.tags

    @property
    def is_server_graph(self):
        return 'server' in self.tags

    def get_node_data(self, node_id):
        return self.nodes_data[node_id]

    def get_node_controller(self, node_id):
        from nodegraph.client.ui.controllers.node_controller import NodeViewController
        if node_id not in self._node_controllers:
            self._node_controllers[node_id] = NodeViewController(node_id=node_id, graph_controller=self)
        return self._node_controllers[node_id]

    def get_node_context_menu(self, node_id):
        node_data = self.nodes_data[node_id]
        nodeTypeID = node_data.nodeType
        node_type_name = get_node_type(nodeTypeID).name
        m = [['Copy nodeID: %s' % node_id, lambda *args: self._copy_value(node_id)], ['Copy nodeTypeID: %s (%s)' % (node_type_name, nodeTypeID), lambda *args: self._copy_value(nodeTypeID)]]
        if 'atom_id' in node_data.nodeParameters:
            atom_id = node_data.nodeParameters['atom_id'].value
            m += [['Copy atomID: %s' % atom_id, lambda *args: self._copy_value(atom_id)]]
        return m

    def _copy_value(self, copyValue, *args):
        return blue.pyos.SetClipboardData(unicode(copyValue))

    def get_node_class_title(self, node_id):
        node_data = self.nodes_data[node_id]
        node_class = get_node_class(node_data.nodeType)
        if node_class:
            return node_class.get_title(node_data)
        return self._get_atom_or_node_type(node_id).name

    def get_node_class_subtitle(self, node_id):
        node_data = self.nodes_data[node_id]
        node_class = get_node_class(node_data.nodeType)
        if node_class:
            return node_class.get_subtitle(node_data)
        return ''

    def get_node_description(self, node_id):
        return self._get_atom_or_node_type(node_id).description or ''

    def get_node_color(self, node_id):
        return get_node_type(self.nodes_data[node_id].nodeType).color[:3]

    def get_node_tags(self, node_id):
        node_data = self.nodes_data[node_id]
        if 'atom_id' in node_data.nodeParameters:
            return get_atom_data(node_data.nodeParameters['atom_id'].value).tags
        return []

    def get_node_output_description(self, node_id):
        ouput_parameters = self.get_node_output_parameters(node_id)
        outputs = []
        for parameter in ouput_parameters:
            outputs.append('{} ({})'.format(parameter.parameterKey, parameter.parameterType))

        return '\n'.join(outputs)

    def get_node_output_parameters(self, node_id):
        return self._get_atom_or_node_type(node_id).parameters.outputs

    def get_node_input_parameters(self, node_id):
        input_parameters = []
        node_type = get_node_type(self.nodes_data[node_id].nodeType)
        input_parameters.extend([ p for p in node_type.parameters.inputs if p.parameterKey != 'atom_id' ])
        if 'atom_id' in self.nodes_data[node_id].nodeParameters:
            atom_data = get_atom_data(self.nodes_data[node_id].nodeParameters['atom_id'].value)
            input_parameters.extend(atom_data.parameters.inputs)
        return input_parameters

    def _get_atom_or_node_type(self, node_id):
        node_data = self.nodes_data[node_id]
        if 'atom_id' in node_data.nodeParameters:
            return get_atom_data(node_data.nodeParameters['atom_id'].value)
        return get_node_type(node_data.nodeType)

    @property
    def can_edit(self):
        return False

    @property
    def zoom_level(self):
        return self._settings.zoom_level

    @zoom_level.setter
    def zoom_level(self, value):
        self._settings.zoom_level = value

    @property
    def pan_left(self):
        return self._settings.pan_left

    @pan_left.setter
    def pan_left(self, value):
        self._settings.pan_left = value

    @property
    def pan_top(self):
        return self._settings.pan_top

    @pan_top.setter
    def pan_top(self, value):
        self._settings.pan_top = value

    def open_graph(self, graph_id):
        open_node_graph(graph_id)

    def open_fsd_page(self, node_graph_id = None):
        import webbrowser
        webbrowser.open_new('http://localhost:8000/nodegraphs/{}/'.format(node_graph_id or self.node_graph_id))

    def toggle_selection(self, node_id):
        if node_id in self.selected_nodes:
            self.selected_nodes.remove(node_id)
        else:
            self.selected_nodes.add(node_id)
        self.on_selected_nodes(self.selected_nodes)

    def add_to_selection(self, node_id):
        self.add_selection([node_id])

    def add_selection(self, node_ids):
        for node_id in node_ids:
            if node_id in self.selected_nodes:
                continue
            self.selected_nodes.add(node_id)

        self.on_selected_nodes(self.selected_nodes)

    def select_nodes(self, node_ids):
        self.selected_nodes = set(node_ids)
        self.on_selected_nodes(self.selected_nodes)

    def select_all_nodes(self):
        self.selected_nodes = set(self.nodes_data.keys())
        self.on_selected_nodes(self.selected_nodes)

    def clear_selection(self):
        self.selected_nodes.clear()
        self.on_selected_nodes(self.selected_nodes)

    def highlight_node(self, node_id):
        self.on_highlight_node(node_id, True)

    def unhighlight_node(self, node_id):
        self.on_highlight_node(node_id, False)

    def focus_node(self, node_id):
        self.on_focus_node(node_id)


class ActiveNodeGraphController(NodeGraphController):

    def __init__(self, node_graph_id):
        node_graph = self.service.get_active_node_graph(node_graph_id)
        self.node_graph_id = node_graph.graph_id
        super(ActiveNodeGraphController, self).__init__(self.node_graph_id)
        self.node_graph = node_graph

    def stop_node_graph(self, *args, **kwargs):
        self.service.stop_node_graph(self.node_graph.instance_id)

    def stop_active_nodes(self, *args, **kwargs):
        self.node_graph.stop_active_nodes()

    def get_node_context_menu(self, node_id):
        m = super(ActiveNodeGraphController, self).get_node_context_menu(node_id)
        if not self.node_graph.is_active:
            return m
        return [('Start node', lambda : self.node_graph.start_node(node_id)), ('Stop node', lambda : self.node_graph.stop_node(node_id)), None] + m

    def go_to_graph(self):
        open_node_graph(self.node_graph_id)


class LogNodeGraphController(NodeGraphController):

    def __init__(self, node_graph_id):
        node_graph = self.service.log_graphs.get(node_graph_id)
        self.node_graph_id = node_graph.graph_id
        super(LogNodeGraphController, self).__init__(self.node_graph_id)
        self.node_graph = node_graph

    def stop_node_graph(self, *args, **kwargs):
        self.node_graph.stop_node_graph()

    def stop_active_nodes(self, *args, **kwargs):
        self.node_graph.stop_active_nodes()

    def get_node_context_menu(self, node_id):
        m = super(LogNodeGraphController, self).get_node_context_menu(node_id)
        if not self.node_graph.is_active:
            return m
        return [('Start node', lambda : self.node_graph.start_node(node_id)), ('Stop node', lambda : self.node_graph.stop_node(node_id)), None] + m

    def go_to_graph(self):
        open_node_graph(self.node_graph_id)


class AuthoredNodeGraphController(NodeGraphController):

    def __init__(self, node_graph_id):
        super(AuthoredNodeGraphController, self).__init__(node_graph_id)
        self._load_from_fsd()
        self._is_building = False

    def _load_from_fsd(self):
        fsd_data = get_node_graph_data(self.node_graph_id)
        self.node_graph = KeyVal(name=fsd_data.name, description=fsd_data.description, nodes_data=fsd_data.nodes, tags=fsd_data.tags, parent_graph_id=fsd_data.parentGraph, remote_graph_id=get_remote_graph_id_from_data(fsd_data), scope=get_scope_from_data(fsd_data))

    def start_node_graph(self, *args, **kwargs):
        if self.is_server_graph:
            self.service.qa_start_node_graph(self.node_graph_id)
        else:
            self.service.start_node_graph(self.node_graph_id)

    def reload_from_fsd(self, *args, **kwargs):
        reload_node_graph_data()
        self._load_from_fsd()
        self.on_update()

    @property
    def is_building(self):
        return self._is_building

    @property
    def has_custom_graph(self):
        custom_node_graph_id = 'custom_{}'.format(self.node_graph_id)
        return bool(get_custom_node_graph(custom_node_graph_id))

    def customize_graph(self, *args, **kwargs):
        custom_node_graph_id = customize_fsd_graph(self.node_graph_id)
        open_node_graph(custom_node_graph_id)


class CustomNodeGraphController(NodeGraphController):

    def __init__(self, node_graph_id):
        super(CustomNodeGraphController, self).__init__(node_graph_id)
        authored_id = get_custom_node_graph_authored_id(node_graph_id)
        if authored_id:
            fsd_data = get_node_graph_data(authored_id)
            name = fsd_data.name
            description = fsd_data.description
            tags = fsd_data.tags
            parent_graph_id = fsd_data.parentGraph
            remote_graph_id = get_remote_graph_id_from_data(fsd_data)
            scope = get_scope_from_data(fsd_data)
        else:
            name = node_graph_id
            description = ''
            tags = []
            parent_graph_id = None
            remote_graph_id = None
            scope = None
        self.node_graph = KeyVal(name=name, description=description, nodes_data=get_custom_node_graph(node_graph_id, as_object=True), tags=tags, parent_graph_id=parent_graph_id, remote_graph_id=remote_graph_id, scope=scope)
        self.selected_connection_point = None
        self.on_selected_connection_point = signals.Signal('on_selected_connection_point')

    def _initialize(self):
        from .controllers import get_node_graph_settings
        self._settings = get_node_graph_settings(self.get_authored_id() or self.node_graph_id)

    @property
    def can_edit(self):
        return True

    def open_fsd_page(self, node_graph_id = None):
        node_graph_id = self.get_authored_id()
        if node_graph_id:
            super(CustomNodeGraphController, self).open_fsd_page(node_graph_id)

    def start_node_graph(self, *args, **kwargs):
        if self.is_server_graph:
            return
        node_graph = ClientNodeGraph(graph_id=self.node_graph_id, graph_data=KeyVal(name=self.name, description=self.description, nodes=self.nodes_data, tags=self.tags))
        self.service._active_graphs[node_graph.instance_id] = node_graph
        open_node_graph(node_graph.instance_id)
        node_graph.start_node_graph()

    def get_authored_id(self):
        return get_custom_node_graph_authored_id(self.node_graph_id)

    def copy_graph_to_clipboard(self):
        copy_graph_to_clipboard(self.node_graph_id)

    def copy_nodes_to_clipboard(self, node_ids):
        copy_graph_to_clipboard(self.node_graph_id, node_ids=node_ids)

    def clear_selected_connection_point(self):
        if self.selected_connection_point:
            self.selected_connection_point = None
            self.on_selected_connection_point(self.selected_connection_point)

    def node_connection_clicked(self, connection_point):
        self.clear_selection()
        if not self.selected_connection_point:
            self.selected_connection_point = connection_point
            self.on_selected_connection_point(self.selected_connection_point)
            return
        input_point = None
        output_point = None
        if 'input' in connection_point.connection_type:
            input_point = connection_point
        else:
            output_point = connection_point
        if 'input' in self.selected_connection_point.connection_type:
            input_point = self.selected_connection_point
        else:
            output_point = self.selected_connection_point
        if not input_point or not output_point:
            print 'cannot connect of same group - input->input or output->output'
            self.clear_selected_connection_point()
            return
        if output_point.node_id == input_point.node_id:
            print 'cannot connect the same node - input->output or output->input'
            self.clear_selected_connection_point()
            return
        if 'variable' in output_point.connection_type and 'variable' in input_point.connection_type:
            self._add_variable_connection(output_point.node_id, output_point.connection_id, input_point.node_id, input_point.connection_id)
        elif 'variable' not in output_point.connection_type and 'variable' not in input_point.connection_type:
            self.add_node_connection(output_point.node_id, input_point.node_id, output_point.connection_id)
        else:
            print 'cannot connect variable to non-variable port'
        self.clear_selected_connection_point()

    def get_node_context_menu(self, node_id):
        m = super(CustomNodeGraphController, self).get_node_context_menu(node_id)
        if self.selected_nodes:
            result = [('MULTIPLE NODES SELECTED', None),
             ('Copy to clipboard', lambda : self.copy_nodes_to_clipboard(self.selected_nodes)),
             (eveformat.color('! Remove nodes', (1, 0, 0)), lambda : self.remove_nodes(self.selected_nodes)),
             None] + m
        else:
            result = [('Duplicate node', lambda : self.duplicate_node(node_id)),
             ('Copy to clipboard', lambda : self.copy_nodes_to_clipboard([node_id])),
             None,
             (eveformat.color('! Remove node', (1, 0, 0)), lambda : self.remove_nodes([node_id])),
             None]
        return result + m

    def add_node(self, node_type_id, position, atom_type_id):
        node_id = self._get_new_node_id()
        self.nodes_data[node_id] = get_new_node_data(node_type_id, position, atom_type_id)
        if self.selected_connection_point:
            if self.selected_connection_point.connection_type == 'output':
                self.add_node_connection(self.selected_connection_point.node_id, node_id, self.selected_connection_point.connection_id)
            self.clear_selected_connection_point()
        self.save_graph()
        return node_id

    def duplicate_node(self, node_id):
        node_data = KeyVal(deepcopy(self.nodes_data[node_id].__dict__))
        node_data['connections'] = {connection_id:[] for connection_id in node_data['connections']}
        for parameter_id, parameter in node_data['nodeParameters'].items():
            if parameter.connection:
                del node_data['nodeParameters'][parameter_id]

        for parameter_id, parameter in node_data.get('atomParameters', {}).items():
            if parameter.connection:
                del node_data['atomParameters'][parameter_id]

        node_data['position'] = [node_data['position'][0] + 3, node_data['position'][1] + 1]
        new_node_id = self._get_new_node_id()
        self.nodes_data[new_node_id] = node_data
        self.save_graph()

    def remove_nodes(self, node_ids):
        for node_id in node_ids:
            for from_node_id in self.nodes_data:
                if from_node_id == node_id:
                    continue
                connections = self.nodes_data[from_node_id]['connections']
                for connection_id in connections:
                    try:
                        connections[connection_id].remove(node_id)
                    except Exception:
                        pass

                for parameter_id, parameter in self.nodes_data[from_node_id]['nodeParameters'].items():
                    if parameter.connection and parameter.connection.node == node_id:
                        del self.nodes_data[from_node_id]['nodeParameters'][parameter_id]

                for parameter_id, parameter in self.nodes_data[from_node_id].get('atomParameters', {}).items():
                    if parameter.connection and parameter.connection.node == node_id:
                        del self.nodes_data[from_node_id]['atomParameters'][parameter_id]

            self.nodes_data.pop(node_id, None)

        self.save_graph()

    def add_node_connection(self, from_node_id, to_node_id, connection_id):
        if 'input' not in get_node_type(self.nodes_data[to_node_id].nodeType).ports.inPorts:
            return
        if connection_id not in self.nodes_data[from_node_id]['connections']:
            self.nodes_data[from_node_id]['connections'][connection_id] = []
        connections = self.nodes_data[from_node_id]['connections'][connection_id]
        if to_node_id not in connections:
            connections.append(to_node_id)
            self.save_graph()

    def remove_all_connection_lines(self, connection_lines):
        for connection_line in connection_lines:
            self.remove_connection_line(connection_line)

    def remove_connection_line(self, connection_line):
        if connection_line.point_b.connection_type == 'input_variable':
            self.remove_variable_connection(connection_line.point_b.node_id, connection_line.point_b.connection_id)
        else:
            self.remove_node_connection(connection_line.point_a.node_id, connection_line.point_b.node_id, connection_line.point_a.connection_id)

    def remove_all_node_connections(self, node_id, connection_id):
        self.nodes_data[node_id]['connections'][connection_id] = []
        self.save_graph()

    def remove_node_connection(self, from_node_id, to_node_id, connection_id):
        connections = self.nodes_data[from_node_id]['connections'][connection_id]
        if to_node_id in connections:
            connections.remove(to_node_id)
            self.save_graph()

    def remove_variable_connection(self, node_id, parameter_id):
        update_parameter_connection(self.nodes_data[node_id], parameter_id, None, None)
        self.save_graph()

    def paste_from_clipboard(self, position, clipboard_data):
        import yaml
        nodes_data = convert_from_clipboard(yaml.safe_load(clipboard_data or '{}'), position)
        if nodes_data:
            self.nodes_data.update(nodes_data)
            self.save_graph()

    def move_node(self, node_id, position):
        self.nodes_data[node_id]['position'] = position
        self.save_graph()

    def move_nodes(self, node_ids, main_node_id, new_position):
        current_position = self.nodes_data[main_node_id]['position']
        pos_diff_x = new_position[0] - current_position[0]
        pos_diff_y = new_position[1] - current_position[1]
        adjust_x = 0
        adjust_y = 0
        for node_id in node_ids:
            position = self.nodes_data[node_id]['position']
            new_pos_x = position[0] + pos_diff_x
            new_pos_y = position[1] + pos_diff_y
            if new_pos_x < 0:
                adjust_x = min(adjust_x, new_pos_x)
            if new_pos_y < 0:
                adjust_y = min(adjust_y, new_pos_y)

        pos_diff_x -= adjust_x
        pos_diff_y -= adjust_y
        for node_id in node_ids:
            position = self.nodes_data[node_id]['position']
            new_pos_x = position[0] + pos_diff_x
            new_pos_y = position[1] + pos_diff_y
            self.nodes_data[node_id]['position'] = (new_pos_x, new_pos_y)

        self.save_graph()

    def edit_nodes_data(self, data):
        self.node_graph.nodes_data = data
        self.save_graph()

    def update_node_parameter(self, node_id, parameter_id, value):
        update_parameter(self.nodes_data[node_id], parameter_id, value)
        self.save_graph()

    def update_node_comment(self, node_id, comment):
        if not comment:
            comment = None
        if self.nodes_data[node_id].comment != comment:
            self.nodes_data[node_id].comment = comment
            self.save_graph()

    @uthread2.debounce(wait=0.1)
    def save_graph(self):
        self.clear_selection()
        custom_node_graphs = get_custom_node_graphs()
        data = convert_to_dict_nodes(self.nodes_data)
        custom_node_graphs[self.node_graph_id] = data
        save_custom_node_graphs(custom_node_graphs)
        self.node_graph.nodes_data = get_custom_node_graph(self.node_graph_id, as_object=True)
        self.on_update()

    @threadutils.threaded
    def save_to_fsd(self):
        authored_id = self.get_authored_id()
        if not authored_id:
            return
        open_node_graph(authored_id)
        save_fsd_node_graph(authored_id, get_custom_node_graph(self.node_graph_id))

    def delete_graph(self, *args, **kwargs):
        authored_id = self.get_authored_id()
        delete_custom_node_graph(self.node_graph_id)
        open_node_graph(authored_id)

    def go_to_authored_graph(self):
        authored_id = self.get_authored_id()
        if authored_id:
            open_node_graph(authored_id)

    def _get_new_node_id(self):
        return str(uuid.uuid4())

    def _add_variable_connection(self, from_node_id, from_key, to_node_id, to_key):
        update_parameter_connection(self.nodes_data[to_node_id], to_key, from_node_id, from_key)
        self.save_graph()
