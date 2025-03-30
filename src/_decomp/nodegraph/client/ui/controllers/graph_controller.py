#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\controllers\graph_controller.py
import signals
from nodegraph.common.nodedata import get_node_graph_data, get_node_type, reload_node_graph_data
from nodegraph.client.custom_graph import get_yaml_nodes_as_dict, get_built_nodes_as_dict
from nodegraph.client.ui.controllers.node_controller import NodeViewController, AuthoredNodeViewController
from nodegraph.client.ui.view import BaseNodeGraphView, AuthoredNodeGraphView

class NodeGraphViewController(object):
    node_graph_component_class = BaseNodeGraphView
    _node_view_controller_class = NodeViewController

    def __init__(self, node_graph_id):
        from nodegraph.client.ui.controllers import get_node_graph_settings
        self.node_graph_id = node_graph_id
        self.selected_nodes = set()
        self._settings = get_node_graph_settings(self.node_graph_id)
        self._node_controllers = {}
        self.on_update = signals.Signal('on_update')
        self.on_selected_nodes = signals.Signal('on_selected_nodes')
        self.on_focus_node = signals.Signal('on_focus_node')
        self.on_highlight_node = signals.Signal('on_highlight_node')
        self._graph_data = get_node_graph_data(self.node_graph_id)

    def initialize(self):
        pass

    def get_node_controller(self, node_id):
        if node_id not in self._node_controllers:
            self._node_controllers[node_id] = self._node_view_controller_class(node_id=node_id, graph_controller=self)
        return self._node_controllers[node_id]

    def start_node_graph(self, *args, **kwargs):
        if self.is_server_graph:
            self.service.qa_start_node_graph(self.node_graph_id)
        else:
            node_graph = self.service.start_node_graph(self.node_graph_id)
            open_node_graph(node_graph.instance_id)

    def add_to_selection(self, node_id):
        self.add_selection([node_id])

    def add_selection(self, node_ids):
        for node_id in node_ids:
            if node_id in self.selected_nodes:
                continue
            self.selected_nodes.add(node_id)

        self.on_selected_nodes(self.selected_nodes)

    def toggle_selection(self, node_id):
        if node_id in self.selected_nodes:
            self.selected_nodes.remove(node_id)
        else:
            self.selected_nodes.add(node_id)
        self.on_selected_nodes(self.selected_nodes)

    def remove_selection(self, node_ids):
        for node_id in node_ids.copy():
            self.selected_nodes.remove(node_id)

        self.on_selected_nodes(self.selected_nodes)

    def select_all(self):
        self.selected_nodes = set(self.nodes_data.keys())
        self.on_selected_nodes(self.selected_nodes)

    def clear_selection(self):
        self.remove_selection(self.selected_nodes)

    def focus_node(self, node_id):
        self.on_focus_node(node_id)

    def highlight_node(self, node_id):
        pass

    def unhighlight_node(self, node_id):
        pass

    def get_node_context_menu(self, node_id):
        if len(self.selected_nodes) > 1:
            return [('MULTIPLE NODES SELECTED', None), ('Copy nodes to clipboard', lambda : self.copy_nodes_to_clipboard(self.selected_nodes))]
        else:
            return self.get_node_controller(node_id).get_context_menu()

    def open_fsd_page(self):
        import webbrowser
        webbrowser.open_new('http://localhost:8000/nodegraphs/{}/'.format(self.node_graph_id))

    def copy_nodes_to_clipboard(self, node_ids = None):
        from nodegraph.tools import copy_nodes_to_clipboard
        copy_nodes_to_clipboard(self.node_graph_id, node_ids)

    def get_node_data(self, node_id):
        return self.nodes_data[node_id]

    @property
    def service(self):
        return sm.GetService('node_graph')

    @property
    def nodes_data(self):
        return self._graph_data.nodes

    @property
    def name(self):
        return self._graph_data.name

    @property
    def description(self):
        return self._graph_data.description

    @property
    def parent_graph_id(self):
        return self._graph_data.parentGraph

    @property
    def tags(self):
        return self._graph_data.tags

    @property
    def is_server_graph(self):
        return 'server' in self.tags

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


class AuthoredNodeGraphViewController(NodeGraphViewController):
    node_graph_component_class = AuthoredNodeGraphView
    _node_view_controller_class = AuthoredNodeViewController

    def __init__(self, node_graph_id):
        self.selected_connection_point = None
        self.on_selected_connection_point = signals.Signal('on_selected_connection_point')
        self._node_graph_yaml = None
        self._nodes_raw_dict = None
        self._nodes_built_dict = None
        self._nodes_object = None
        self._has_changes = False
        super(AuthoredNodeGraphViewController, self).__init__(node_graph_id)

    def initialize(self):
        from nodegraph.tools import load_node_graph_yaml
        self._node_graph_yaml = load_node_graph_yaml(self.node_graph_id)
        self._nodes_raw_dict = get_yaml_nodes_as_dict(self.node_graph_id)
        self._nodes_built_dict = get_built_nodes_as_dict(self.node_graph_id)
        self._nodes_object = None
        self._has_changes = self._nodes_raw_dict != self._nodes_built_dict

    @property
    def nodes_data(self):
        if self._nodes_object is None:
            self._nodes_object = _get_nodes_as_object(self._nodes_raw_dict)
        return self._nodes_object

    @property
    def can_edit(self):
        return False

    @property
    def has_custom_graph(self):
        from nodegraph.client.custom_graph import get_custom_node_graph
        custom_node_graph_id = 'custom_{}'.format(self.node_graph_id)
        return bool(get_custom_node_graph(custom_node_graph_id))

    def customize_graph(self, *args, **kwargs):
        from nodegraph.client.custom_graph import customize_fsd_graph
        custom_node_graph_id = customize_fsd_graph(self.node_graph_id)
        open_node_graph(custom_node_graph_id)

    def add_node(self, node_type_id, position, atom_type_id):
        print 'add_node', node_type_id, position, atom_type_id

    def duplicate_node(self, node_id):
        print 'duplicate_node', node_id

    def paste_from_clipboard(self, position, clipboard_data):
        print 'paste_from_clipboard', position

    def remove_nodes(self, node_ids):
        print 'remove_node', node_ids

    def add_node_connection(self, from_node_id, to_node_id, connection_id):
        if 'input' not in get_node_type(self.nodes_data[to_node_id].nodeType).ports.inPorts:
            return
        if connection_id not in self.nodes_data[from_node_id]['connections']:
            self.nodes_data[from_node_id]['connections'][connection_id] = []
        connections = self.nodes_data[from_node_id]['connections'][connection_id]
        if to_node_id not in connections:
            connections.append(to_node_id)
            self.save()

    def node_connection_clicked(self, connection_point):
        print 'node_connection_clicked', connection_point

    def clear_selected_connection_point(self):
        pass

    def save(self, *args, **kwargs):
        print 'save'

    def reload_from_fsd(self, *args, **kwargs):
        self._nodes_object = None
        reload_node_graph_data()
        self.on_update()

    def build(self, *args, **kwargs):
        print 'build'


def _get_nodes_as_object(nodes_data):
    from copy import deepcopy
    from utillib import KeyVal
    nodes_data = deepcopy(nodes_data)
    for node_id in nodes_data:
        nodes_data[node_id] = KeyVal(nodes_data[node_id])
        for parameter_id in nodes_data[node_id].nodeParameters:
            value = nodes_data[node_id].nodeParameters[parameter_id].get('value', None)
            connection = nodes_data[node_id].nodeParameters[parameter_id].get('connection', None)
            if connection:
                connection = KeyVal(connection)
            nodes_data[node_id].nodeParameters[parameter_id] = KeyVal(value=value, connection=connection)

        if 'atom_id' in nodes_data[node_id].nodeParameters:
            for parameter_id in nodes_data[node_id].atomParameters:
                value = nodes_data[node_id].atomParameters[parameter_id].get('value', None)
                connection = nodes_data[node_id].atomParameters[parameter_id].get('connection', None)
                if connection:
                    connection = KeyVal(connection)
                nodes_data[node_id].atomParameters[parameter_id] = KeyVal(value=value, connection=connection)

    return nodes_data


def get_new_node_id():
    import uuid
    return str(uuid.uuid4())


def open_node_graph(node_graph_id):
    from nodegraph.client.ui.window import NodeGraphEditorWindow
    NodeGraphEditorWindow.Open(node_graph_id=node_graph_id)
