#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\nodedata.py
from caching import Memoize
from fsdBuiltData.common.base import BuiltDataLoader
from nodegraph.common.const import SUB_GRAPH_NODE
try:
    import nodeGraphsLoader
except ImportError:
    nodeGraphsLoader = None

try:
    import nodeTypesLoader
except ImportError:
    nodeTypesLoader = None

class NodeGraphLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/nodeGraphs.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/nodeGraphs.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/nodeGraphs.fsdbinary'
    __loader__ = nodeGraphsLoader


class NodeTypesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/nodeTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/nodeTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/nodeTypes.fsdbinary'
    __loader__ = nodeTypesLoader


def get_node_graphs():
    return NodeGraphLoader.GetData()


def get_node_graph_data(node_graph_id):
    return get_node_graphs().get(node_graph_id, None)


def iter_node_graphs():
    for node_graph_id, node_graph in get_node_graphs().iteritems():
        yield (node_graph_id, node_graph)


def reload_node_graph_data():
    return NodeGraphLoader.ReloadDataFromDisk()


def get_node_types():
    return NodeTypesLoader.GetData()


def get_node_type(node_type_id):
    return get_node_types().get(node_type_id, None)


def get_node_input_parameter_dict(node_type_id):
    return {p.parameterKey:p for p in get_node_type(node_type_id).parameters.inputs}


def get_node_graph_id_by_name(node_graph_name):
    for node_graph_id, node_graph in iter_node_graphs():
        if node_graph.name == node_graph_name:
            return node_graph_id


def get_root_graph_id(node_graph_id):
    parent_graph_id = get_node_graph_data(node_graph_id).parentGraph
    if not parent_graph_id:
        return node_graph_id
    else:
        return get_root_graph_id(parent_graph_id)


@Memoize
def get_remote_graph_id(node_graph_id):
    node_graph_data = get_node_graph_data(node_graph_id)
    return get_remote_graph_id_from_data(node_graph_data)


def get_remote_graph_id_from_data(node_graph_data):
    remote_info = node_graph_data.remote
    if remote_info:
        return getattr(remote_info, 'remoteGraph', None)


@Memoize
def get_scope(node_graph_id):
    node_graph_data = get_node_graph_data(node_graph_id)
    return get_scope_from_data(node_graph_data)


def get_scope_from_data(node_graph_data):
    remote_info = node_graph_data.remote
    if remote_info:
        return getattr(remote_info, 'scope', None)


def get_sub_graphs(node_graph_id):
    nodes = get_node_graph_data(node_graph_id).nodes
    sub_graphs = set()
    for node in nodes.itervalues():
        if node.nodeType != SUB_GRAPH_NODE:
            continue
        sub_graphs.add(node.nodeParameters['node_graph_id'].value)

    return list(sub_graphs)


def get_node_graph_ids_with_tags(tags):
    result = []
    for node_graph_id, node_graph in iter_node_graphs():
        if all((tag in node_graph.tags for tag in tags)):
            result.append(node_graph_id)

    return result


def is_client_graph(node_graph_id):
    if node_graph_id is None:
        return False
    node_graph_data = get_node_graph_data(node_graph_id)
    if not node_graph_data:
        return False
    if 'client' in node_graph_data.tags or 'Client' in node_graph_data.tags:
        return True
    return False


def is_server_graph(node_graph_id):
    if node_graph_id is None:
        return False
    node_graph_data = get_node_graph_data(node_graph_id)
    if not node_graph_data:
        return False
    if 'server' in node_graph_data.tags or 'Server' in node_graph_data.tags:
        return True
    return False


def _clear_cached_data():
    get_remote_graph_id.clear_memoized()
    get_scope.clear_memoized()


NodeGraphLoader.ConnectToOnReload(_clear_cached_data)

class OutPort(object):
    output = 'output'
    success = 'success'
    failure = 'failure'
    validation = 'validation'
    nodes = 'nodes'
    on_start = 'on_start'
    on_stop = 'on_stop'
    on_success = 'on_success'
    on_failure = 'on_failure'
    group_nodes = 'group_nodes'
    on_end = 'on_end'
    on_next = 'on_next'
    on_complete = 'on_complete'
    on_incomplete = 'on_incomplete'


class InPort(object):
    input = 'input'
