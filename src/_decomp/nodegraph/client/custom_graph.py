#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\custom_graph.py
import datetime
import yaml
from copy import deepcopy
import uuid
import blue
from carbonui import uiconst
from carbonui.uicore import uicore
from utillib import KeyVal
import logging
from nodegraph.common.atomdata import get_atom_data, get_atom_input_parameter_dict, get_event_atoms, get_action_atoms, get_condition_atoms, get_getter_atoms
from nodegraph.common.nodedata import get_node_type, get_node_input_parameter_dict, get_node_types, get_node_graph_data
try:
    import nodegraph.tools as tools
except ImportError:
    tools = None

logger = logging.getLogger(__name__)

def get_custom_node_graphs():
    return settings.user.ui.Get('custom_node_graphs', {})


def get_custom_node_graph(node_graph_id, as_object = False):
    nodes_data = deepcopy(get_custom_node_graphs().get(node_graph_id, None))
    if as_object and nodes_data:
        for node_id in nodes_data:
            nodes_data[node_id] = KeyVal(nodes_data[node_id])
            for parameter_id in nodes_data[node_id].nodeParameters:
                value = nodes_data[node_id].nodeParameters[parameter_id].get('value', None)
                connection = nodes_data[node_id].nodeParameters[parameter_id].get('connection', None)
                if connection:
                    connection = KeyVal(connection)
                nodes_data[node_id].nodeParameters[parameter_id] = KeyVal(value=value, connection=connection)

            if 'atom_id' in nodes_data[node_id].nodeParameters:
                if 'atomParameters' not in nodes_data[node_id]:
                    nodes_data[node_id]['atomParameters'] = {}
                for parameter_id in nodes_data[node_id].atomParameters:
                    value = nodes_data[node_id].atomParameters[parameter_id].get('value', None)
                    connection = nodes_data[node_id].atomParameters[parameter_id].get('connection', None)
                    if connection:
                        connection = KeyVal(connection)
                    nodes_data[node_id].atomParameters[parameter_id] = KeyVal(value=value, connection=connection)

    return nodes_data


def get_custom_node_graph_authored_id(node_graph_id):
    try:
        return int(node_graph_id.split('_')[1])
    except:
        return None


def save_custom_node_graphs(data):
    settings.user.ui.Set('custom_node_graphs', data)
    sm.GetService('settings').SaveSettings(async=False)


def create_new_custom_node_graph(node_graph_id = None, nodes_data = None):
    new_node_graph_id = 'custom_{}'.format(node_graph_id or datetime.datetime.now().isoformat())
    custom_node_graphs = get_custom_node_graphs()
    if new_node_graph_id in custom_node_graphs:
        return new_node_graph_id
    custom_node_graphs[new_node_graph_id] = nodes_data or {}
    save_custom_node_graphs(custom_node_graphs)
    return new_node_graph_id


def delete_all_custom_node_graphs():
    save_custom_node_graphs({})


def delete_custom_node_graph(node_graph_id, show_prompt = True):
    if show_prompt:
        response = uicore.Message('CustomQuestion', {'header': 'Delete',
         'question': 'Are you sure you want to delete the node graph?'}, buttons=uiconst.YESNO)
        if response != uiconst.ID_YES:
            return
    custom_node_graphs = get_custom_node_graphs()
    if node_graph_id not in custom_node_graphs:
        print "Custom node graph doesn't exists", node_graph_id
        return
    custom_node_graphs.pop(node_graph_id, None)
    save_custom_node_graphs(custom_node_graphs)


def copy_graph_to_clipboard(node_graph_id, node_ids = None):
    data = get_custom_node_graph(node_graph_id)
    if node_ids:
        data = {node_id:node_data for node_id, node_data in data.iteritems() if node_id in node_ids}
    blue.pyos.SetClipboardData(yaml.safe_dump(convert_to_fsd_nodes(data), default_flow_style=False, allow_unicode=True, indent=4))


def save_all_custom_fsd_graphs():
    graphs = get_custom_node_graphs()
    for graph_id, nodes_data in graphs.iteritems():
        authored_id = get_custom_node_graph_authored_id(graph_id)
        if not authored_id:
            continue
        save_fsd_node_graph(authored_id, nodes_data)


def save_fsd_node_graph(node_graph_id, nodes_data):
    data = tools.load_node_graph_yaml(node_graph_id)
    data['nodes'] = convert_to_fsd_nodes(nodes_data)
    tools.save_node_graph_yaml(node_graph_id, data)


def convert_to_fsd_nodes(dict_nodes):
    fsd_nodes = {}
    for node_id in dict_nodes:
        fsd_nodes[node_id] = dict_nodes[node_id]
        if 'comment' in fsd_nodes[node_id] and not fsd_nodes[node_id]['comment']:
            del fsd_nodes[node_id]['comment']
        if 'atom_id' in fsd_nodes[node_id]['nodeParameters'] and 'atomParameters' in fsd_nodes[node_id]:
            atom_type_parameters = get_atom_input_parameter_dict(fsd_nodes[node_id]['nodeParameters']['atom_id']['value'])
            for parameter_id in fsd_nodes[node_id]['atomParameters'].keys():
                if parameter_id not in atom_type_parameters:
                    logger.error('Invalid atom parameter %s in node %s - removing', parameter_id, node_id)
                    del fsd_nodes[node_id]['atomParameters'][parameter_id]
                    continue
                parameter = atom_type_parameters[parameter_id]
                parameter_data = fsd_nodes[node_id]['atomParameters'][parameter_id]
                if 'connection' in parameter_data:
                    value = {'connection': parameter_data['connection']}
                else:
                    value = parameter_data['value']
                    if parameter.parameterType == 'boolType':
                        value = bool(value)
                    elif parameter.parameterType == 'boolListType':
                        value = [ bool(i) for i in value ]
                    value = {'value': {'unionType': parameter.parameterType,
                               'unionValue': value}}
                fsd_nodes[node_id]['atomParameters'][parameter_id] = value

            if not fsd_nodes[node_id]['atomParameters']:
                del fsd_nodes[node_id]['atomParameters']
        node_type_parameters = get_node_input_parameter_dict(fsd_nodes[node_id]['nodeType'])
        for parameter_id in fsd_nodes[node_id]['nodeParameters'].keys():
            if parameter_id not in node_type_parameters:
                logger.error('Invalid node parameter %s in node %s - removing', parameter_id, node_id)
                del fsd_nodes[node_id]['nodeParameters'][parameter_id]
                continue
            parameter = node_type_parameters[parameter_id]
            parameter_data = fsd_nodes[node_id]['nodeParameters'][parameter_id]
            if 'connection' in parameter_data:
                value = {'connection': parameter_data['connection']}
            else:
                value = parameter_data['value']
                if parameter.parameterType == 'boolType':
                    value = bool(value)
                elif parameter.parameterType == 'boolListType':
                    value = [ bool(i) for i in value ]
                value = {'value': {'unionType': parameter.parameterType,
                           'unionValue': value}}
            fsd_nodes[node_id]['nodeParameters'][parameter_id] = value

    return fsd_nodes


def get_yaml_nodes_as_dict(node_graph_id):
    nodes_data = tools.load_node_graph_yaml(node_graph_id)['nodes']
    if not nodes_data:
        return {}
    result = nodes_data
    for node_id, node in nodes_data.iteritems():
        result[node_id] = {'nodeType': node['nodeType'],
         'nodeParameters': node['nodeParameters'],
         'atomParameters': node.get('atomParameters', {}),
         'connections': node['connections'],
         'position': node['position'],
         'comment': node.get('comment', None)}
        node_type = get_node_type(node['nodeType'])
        for parameter in node_type.parameters.inputs:
            if parameter.parameterKey not in result[node_id]['nodeParameters']:
                continue
            param = result[node_id]['nodeParameters'][parameter.parameterKey]
            if 'connection' in param:
                result[node_id]['nodeParameters'][parameter.parameterKey]['connection'] = param['connection']
            elif 'value' in param:
                result[node_id]['nodeParameters'][parameter.parameterKey]['value'] = param['value']['unionValue']
            else:
                result[node_id]['nodeParameters'][parameter.parameterKey]['value'] = param

        if 'atom_id' in result[node_id]['nodeParameters']:
            atom_id = result[node_id]['nodeParameters']['atom_id']
            if not isinstance(atom_id, int):
                atom_id = atom_id['value']
            atom_type = get_atom_data(atom_id)
            for parameter in atom_type.parameters.inputs:
                if parameter.parameterKey not in result[node_id]['atomParameters']:
                    continue
                param = result[node_id]['atomParameters'][parameter.parameterKey]
                if 'connection' in param:
                    result[node_id]['atomParameters'][parameter.parameterKey]['connection'] = param['connection']
                elif 'value' in param:
                    result[node_id]['atomParameters'][parameter.parameterKey]['value'] = param['value']['unionValue']
                else:
                    result[node_id]['atomParameters'][parameter.parameterKey]['value'] = param

    return result


def get_built_nodes_as_dict(node_graph_id):
    nodes_data = get_node_graph_data(node_graph_id).nodes
    if not nodes_data:
        return {}
    result = {}
    for node_id, node in nodes_data.iteritems():
        result[node_id] = KeyVal(nodeType=node.nodeType, nodeParameters=dict(node.nodeParameters), connections={}, position=list(node.position), comment=node.comment)
        node_type = get_node_type(node.nodeType)
        for parameter in node_type.parameters.inputs:
            if parameter.parameterKey not in result[node_id]['nodeParameters']:
                continue
            param = result[node_id]['nodeParameters'][parameter.parameterKey]
            if getattr(param, 'connection', None):
                connection = getattr(param, 'connection')
                update_parameter_connection(result[node_id], parameter.parameterKey, connection.node, connection.parameter)
            elif getattr(param, 'value', None) is not None:
                update_parameter(result[node_id], parameter.parameterKey, getattr(param, 'value'))
            else:
                update_parameter(result[node_id], parameter.parameterKey, param)

        if 'atom_id' in result[node_id]['nodeParameters']:
            result[node_id]['atomParameters'] = dict(node.atomParameters or {})
            atom_id = result[node_id]['nodeParameters']['atom_id']
            if not isinstance(atom_id, int):
                atom_id = atom_id['value']
            atom_type = get_atom_data(atom_id)
            for parameter in atom_type.parameters.inputs:
                if parameter.parameterKey not in result[node_id]['atomParameters']:
                    continue
                param = result[node_id]['atomParameters'][parameter.parameterKey]
                if getattr(param, 'connection', None):
                    connection = getattr(param, 'connection')
                    update_parameter_connection(result[node_id], parameter.parameterKey, connection.node, connection.parameter)
                elif getattr(param, 'value', None) is not None:
                    update_parameter(result[node_id], parameter.parameterKey, getattr(param, 'value'))
                else:
                    update_parameter(result[node_id], parameter.parameterKey, param)

        for connection_id in node.connections:
            result[node_id]['connections'][connection_id] = list(node.connections[connection_id])

    result = convert_to_dict_nodes(result)
    return result


def convert_to_dict_nodes(nodes_data):
    result = {}
    for node_id in nodes_data:
        result[node_id] = nodes_data[node_id].__dict__
        for parameter_id, parameter in nodes_data[node_id]['nodeParameters'].items():
            data = {}
            if parameter.connection:
                data['connection'] = parameter.connection.__dict__
            else:
                data['value'] = parameter.value
            result[node_id]['nodeParameters'][parameter_id] = data

        for parameter_id, parameter in nodes_data[node_id].get('atomParameters', {}).items():
            data = {}
            if parameter.connection:
                data['connection'] = parameter.connection.__dict__
            else:
                data['value'] = parameter.value
            result[node_id]['atomParameters'][parameter_id] = data

    return result


def convert_from_clipboard(nodes_data, position):
    import sys
    result = {}
    new_id_map = {}
    min_x = sys.maxint
    min_y = sys.maxint
    for node_id, node_data in nodes_data.iteritems():
        new_node_id = str(uuid.uuid4())
        new_id_map[node_id] = new_node_id
        result[new_node_id] = KeyVal(node_data)
        min_x = min(min_x, result[new_node_id]['position'][0])
        min_y = min(min_y, result[new_node_id]['position'][1])

    for node_id, node_data in result.iteritems():
        if 'comment' not in node_data:
            node_data['comment'] = ''
        node_data['position'] = (result[node_id]['position'][0] - min_x + position[0], result[node_id]['position'][1] - min_y + position[1])
        new_connections = {}
        for connection_id in node_data['connections']:
            new_connections[connection_id] = []
            for connected_node_id in node_data['connections'][connection_id]:
                if connected_node_id not in nodes_data:
                    continue
                new_connections[connection_id].append(new_id_map[connected_node_id])

        node_data['connections'] = new_connections
        for parameter_id, parameter in node_data['nodeParameters'].items():
            if 'value' in parameter:
                node_data['nodeParameters'][parameter_id] = KeyVal(value=parameter['value']['unionValue'], connection=None)
            elif parameter['connection']['node'] in nodes_data:
                node_data['nodeParameters'][parameter_id] = KeyVal(value=None, connection=KeyVal(node=new_id_map[parameter['connection']['node']], parameter=parameter['connection']['parameter']))
            else:
                node_data['nodeParameters'].pop(parameter_id, None)

        for parameter_id, parameter in node_data.get('atomParameters', {}).items():
            if 'value' in parameter:
                node_data['atomParameters'][parameter_id] = KeyVal(value=parameter['value']['unionValue'], connection=None)
            elif parameter['connection']['node'] in nodes_data:
                node_data['atomParameters'][parameter_id] = KeyVal(value=None, connection=KeyVal(node=new_id_map[parameter['connection']['node']], parameter=parameter['connection']['parameter']))
            else:
                node_data['atomParameters'].pop(parameter_id, None)

    return result


def customize_all_fsd_graphs(fix = False):
    from nodegraph.common.nodedata import get_node_graphs
    custom_graphs = get_custom_node_graphs()
    fsd_graphs = get_node_graphs()
    for node_graph_id in fsd_graphs:
        custom_id = 'custom_{}'.format(node_graph_id)
        if custom_id in custom_graphs:
            continue
        nodes_data = get_yaml_nodes_as_dict(node_graph_id)
        if fix:
            nodes_data = fix_custom_graph(node_graph_id, nodes_data)
        create_new_custom_node_graph(node_graph_id, nodes_data)


def customize_fsd_graph(node_graph_id, fix = False):
    nodes_data = get_yaml_nodes_as_dict(node_graph_id)
    if fix:
        nodes_data = fix_custom_graph(node_graph_id, nodes_data)
    return create_new_custom_node_graph(node_graph_id, nodes_data)


def fix_custom_graphs():
    graphs = get_custom_node_graphs()
    for graph_id in graphs:
        graphs[graph_id] = fix_custom_graph(graph_id, graphs[graph_id])


def fix_custom_graph(node_graph_id, nodes_data):
    fixed_graph_nodes = {}
    with_output_variables = set()
    node_id_map = {}

    def get_new_node_id(node_id):
        if node_id not in node_id_map:
            if not isinstance(node_id, str):
                node_id_map[node_id] = str(uuid.uuid4())
            else:
                node_id_map[node_id] = node_id
        return node_id_map[node_id]

    for node_id in nodes_data:
        node = nodes_data[node_id]
        if node['nodeType'] == 29:
            continue
        fixed_node = {'nodeType': node['nodeType'],
         'position': node['position'],
         'connections': {},
         'nodeParameters': node['nodeParameters'],
         'comment': node.get('comment', '')}
        if 'atomParameters' in node:
            fixed_node['atomParameters'] = node['atomParameters']
        comment = node.get('notes', node.get('comment', ''))
        if comment:
            fixed_node['comment'] = comment
        for parameter_id in fixed_node['nodeParameters']:
            try:
                if not isinstance(fixed_node['nodeParameters'][parameter_id], basestring) and ('value' in fixed_node['nodeParameters'][parameter_id] or 'connection' in fixed_node['nodeParameters'][parameter_id]):
                    continue
            except:
                pass

            fixed_node['nodeParameters'][parameter_id] = {'value': fixed_node['nodeParameters'][parameter_id]}

        if 'atomParameters' in fixed_node:
            for parameter_id in fixed_node['atomParameters']:
                try:
                    if not isinstance(fixed_node['atomParameters'][parameter_id], basestring) and ('value' in fixed_node['atomParameters'][parameter_id] or 'connection' in fixed_node['atomParameters'][parameter_id]):
                        continue
                except:
                    pass

                fixed_node['atomParameters'][parameter_id] = {'value': fixed_node['atomParameters'][parameter_id]}

        for connection_id in node['connections']:
            if connection_id == 'variables':
                if node['connections'].get(connection_id, []):
                    with_output_variables.add(node_id)
            else:
                fixed_node['connections'][connection_id] = [ get_new_node_id(connected_node_id) for connected_node_id in node['connections'].get(connection_id, []) ]

        fixed_graph_nodes[get_new_node_id(node_id)] = fixed_node

    for node_id in with_output_variables:
        node = nodes_data[node_id]
        new_node_id = get_new_node_id(node_id)
        for connected_node_id in node['connections']['variables']:
            connected_node = nodes_data[connected_node_id]
            if connected_node['nodeType'] == 29:
                for map_id in connected_node['connections']['variables']:
                    map_node = fixed_graph_nodes[get_new_node_id(map_id)]
                    parameter_id = connected_node['nodeParameters']['output_key']
                    connection_parameter_id = connected_node['nodeParameters']['input_key']
                    if map_node['nodeType'] == 19:
                        parameter_id = 'blackboard_value'
                    if node['nodeType'] == 18:
                        connection_parameter_id = 'blackboard_value'
                    update_parameter_connection(map_node, parameter_id, new_node_id, connection_parameter_id)

            elif connected_node['nodeType'] == 19:
                if connected_node['nodeParameters'].get('input_key', ''):
                    map_node = fixed_graph_nodes[get_new_node_id(connected_node_id)]
                    update_parameter_connection(map_node, 'blackboard_value', new_node_id, connected_node['nodeParameters']['input_key']['value'])
                    connected_node['nodeParameters'].pop('input_key', None)
            elif node['nodeType'] != 18:
                print '*********** warning', node_graph_id, node_id, connected_node_id
            if node['nodeType'] == 18:
                output_key = node['nodeParameters'].get('output_key', None)
                if not output_key:
                    continue
                for connected_node_id in node['connections']['variables']:
                    if nodes_data[connected_node_id]['nodeType'] == 29:
                        continue
                    try:
                        map_node = fixed_graph_nodes[get_new_node_id(connected_node_id)]
                        update_parameter_connection(map_node, output_key['value'], new_node_id, 'blackboard_value')
                    except:
                        print 'NOT FIXED???', node_graph_id, node_id, connected_node_id

        if node['nodeType'] == 18:
            node['nodeParameters'].pop('output_key', None)

    for node_id in fixed_graph_nodes:
        if fixed_graph_nodes[node_id]['nodeType'] == 19:
            fixed_graph_nodes[node_id]['nodeParameters'].pop('input_key', None)
        elif fixed_graph_nodes[node_id]['nodeType'] == 18:
            fixed_graph_nodes[node_id]['nodeParameters'].pop('output_key', None)

    return fixed_graph_nodes


def update_parameter(node_data, parameter_id, value):
    parameter, parameter_group = _get_parameter_and_group(node_data, parameter_id)
    if not parameter:
        return
    default_value = parameter.defaultValue
    if value is None:
        if default_value is None:
            node_data[parameter_group].pop(parameter_id, None)
            return
        value = default_value
    if default_value is None and value is not None:
        if parameter.parameterType.endswith('ListType'):
            default_value = []
        else:
            default_value = type(value)()
    if value == default_value:
        node_data[parameter_group].pop(parameter_id, None)
        return
    if parameter.parameterType == 'boolType':
        value = bool(value)
    elif parameter.parameterType == 'boolListType':
        value = [ bool(i) for i in value ]
    elif parameter.parameterType.endswith('ListType') or parameter.parameterType == 'vector3Type':
        value = list(value)
    if parameter_group not in node_data:
        node_data[parameter_group] = {}
    node_data[parameter_group][parameter_id] = KeyVal(value=value, connection=None)


def update_parameter_connection(node_data, parameter_id, connection_node_id, connection_parameter_id):
    parameter, parameter_group = _get_parameter_and_group(node_data, parameter_id)
    if not parameter:
        return
    if connection_node_id and connection_parameter_id:
        if parameter_group not in node_data:
            node_data[parameter_group] = {}
        node_data[parameter_group][parameter_id] = KeyVal(value=None, connection=KeyVal(node=connection_node_id, parameter=connection_parameter_id))
    elif parameter_group in node_data:
        node_data[parameter_group].pop(parameter_id, None)


def _get_parameter_and_group(node_data, parameter_id):
    parameter = None
    parameter_group = None
    node_type_parameters = get_node_input_parameter_dict(node_data['nodeType'])
    if parameter_id in node_type_parameters:
        parameter = node_type_parameters[parameter_id]
        parameter_group = 'nodeParameters'
    else:
        atom_parameter = node_data['nodeParameters'].get('atom_id', None)
        if atom_parameter:
            atom_type_parameters = get_atom_input_parameter_dict(atom_parameter['value'])
            if parameter_id in atom_type_parameters:
                parameter = atom_type_parameters[parameter_id]
                parameter_group = 'atomParameters'
    return (parameter, parameter_group)


def get_new_node_data(node_type_id, position, atom_type_id = None):
    node_data = KeyVal(nodeType=node_type_id, position=position, nodeParameters={}, comment=None)
    node_type = get_node_type(node_type_id)
    node_data['connections'] = {connection_id:[] for connection_id in node_type.ports.outPorts}
    if atom_type_id:
        node_data['nodeParameters']['atom_id'] = KeyVal(value=atom_type_id, connection=None)
        node_data['atomParameters'] = {}
    return node_data


def _get_atom_id_from_old(atom_id):
    from nodegraph.client.actions import get_atom_action_class
    from nodegraph.client.conditions import get_atom_condition_class
    from nodegraph.client.events import get_atom_event_class
    atom_class = get_atom_action_class(atom_id)
    if atom_class:
        return atom_class.atom_id
    atom_class = get_atom_condition_class(atom_id)
    if atom_class:
        return atom_class.atom_id
    atom_class = get_atom_event_class(atom_id)
    if atom_class:
        return atom_class.atom_id
    return atom_id


def multiply_spacing(x = 1, y = 1):
    graphs = get_custom_node_graphs()
    for graph_id, nodes_data in graphs.iteritems():
        for node_id in nodes_data:
            position = nodes_data[node_id]['position']
            nodes_data[node_id]['position'] = [position[0] * x, position[1] * y]

    save_custom_node_graphs(graphs)


def create_graph_with_all_client_nodes():
    create_graph_with_all_nodes('client')


def create_graph_with_all_server_nodes():
    create_graph_with_all_nodes('server')


def create_graph_with_all_nodes(filter_tag):
    new_graph = {}
    action_node_type = 4
    event_node_type = 5
    validation_node_type = 9
    getter_atom_node_type = 30
    node_types = {node_type_id for node_type_id in get_node_types() if node_type_id not in (action_node_type,
     event_node_type,
     validation_node_type,
     getter_atom_node_type)}
    node_id = 0
    x = 0
    y = 0
    for node_type_id in node_types:
        new_graph[node_id] = get_new_node_data(node_type_id, [x, y])
        y += 4
        node_id += 1

    x = 4
    y = 0
    for atom_id, atom in get_action_atoms().iteritems():
        if filter_tag not in atom.tags:
            continue
        new_graph[node_id] = get_new_node_data(action_node_type, [x, y], atom_id)
        y += 4
        node_id += 1

    x = 8
    y = 0
    for atom_id, atom in get_event_atoms().iteritems():
        if filter_tag not in atom.tags:
            continue
        new_graph[node_id] = get_new_node_data(event_node_type, [x, y], atom_id)
        y += 4
        node_id += 1

    x = 12
    y = 0
    for atom_id, atom in get_condition_atoms().iteritems():
        if filter_tag not in atom.tags:
            continue
        new_graph[node_id] = get_new_node_data(validation_node_type, [x, y], atom_id)
        y += 4
        node_id += 1

    x = 16
    y = 0
    for atom_id, atom in get_getter_atoms().iteritems():
        if filter_tag not in atom.tags:
            continue
        new_graph[node_id] = get_new_node_data(getter_atom_node_type, [x, y], atom_id)
        y += 4
        node_id += 1

    create_new_custom_node_graph('all_{}_nodes'.format(filter_tag), new_graph)


def start_all_custom_graphs():
    from nodegraph.client.graph import ClientNodeGraph
    from utillib import KeyVal
    graphs = get_custom_node_graphs()
    for node_graph_id in graphs:
        print 'Starting', node_graph_id
        node_graph = ClientNodeGraph(graph_id=node_graph_id, graph_data=KeyVal(name=node_graph_id, description='', nodes=get_custom_node_graph(node_graph_id, as_object=True)))
        sm.GetService('node_graph')._active_graphs[node_graph.instance_id] = node_graph
        node_graph.start_node_graph()


def start_all_fsd_graphs(client_graphs = True, server_graphs = True):
    from nodegraph.common.nodedata import get_node_graphs
    for node_graph_id, node_graph in get_node_graphs().iteritems():
        if 'server' in node_graph.tags:
            if server_graphs:
                print 'Starting server graph', node_graph_id, node_graph.name
                sm.GetService('node_graph').qa_start_node_graph(node_graph_id)
        elif client_graphs:
            print 'Starting client graph', node_graph_id, node_graph.name
            sm.GetService('node_graph').start_node_graph(node_graph_id)


def open_all_custom_graphs(wait_time = 0.5):
    from nodegraph.client.ui.window import NodeGraphEditorWindow
    import uthread2
    for node_graph_id in get_custom_node_graphs():
        print 'Opening', node_graph_id
        NodeGraphEditorWindow.Open(node_graph_id=node_graph_id)
        uthread2.sleep(wait_time)


def open_all_fsd_graphs(wait_time = 0.5):
    from nodegraph.client.ui.window import NodeGraphEditorWindow
    from nodegraph.common.nodedata import get_node_graphs
    import uthread2
    for node_graph_id in get_node_graphs():
        print 'Opening', node_graph_id
        NodeGraphEditorWindow.Open(node_graph_id=node_graph_id)
        uthread2.sleep(wait_time)
