#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\shell_tools.py
import os
ng = sm.GetService('node_graph')

def print_graphs():
    info_lines = _get_active_graphs_info_lines()
    for line in info_lines:
        print line


def get_active_graphs_info():
    info_lines = _get_active_graphs_info_lines()
    return '<br>'.join(info_lines)


def _get_active_graphs_info_lines():
    info_lines = ['***** Active Node Graphs *****']

    def get_info(graphs, parent_instance = None, depth = 0):
        lines = []
        for g in graphs.itervalues():
            if g.parent_instance_id == parent_instance:
                lines.append('-' * depth + ' instance_id: ' + str(g.instance_id))
                lines.append(' ' * depth + ' node_graph_id: ' + str(g.graph_id))
                lines.append(' ' * depth + ' active_node_ids: ' + str(list(g.active_node_ids)))
                lines += get_info(graphs, g.instance_id, depth + 1)

        return lines

    active_graphs = sm.GetService('node_graph').get_active_node_graphs()
    info_lines += get_info(active_graphs)
    info_lines.append('***** End Active Node Graphs *****')
    return info_lines


def print_bb(g):
    print '***** Blackboard (', g.instance_id, ') *****'
    for k, v in g.context.values.items():
        print k, ':', v

    print '***** end ******'


def get_graph(instance_id = None):
    ng = sm.GetService('node_graph')
    if instance_id:
        return ng.get_active_node_graph(instance_id)
    all_keys = ng.get_active_node_graphs().keys()
    if not all_keys:
        return None
    inst_id = all_keys[0]
    inst_id = ng.get_root_instance_id(inst_id)
    return ng.get_active_node_graph(inst_id)


def stop_all():
    ng = sm.GetService('node_graph')
    ng.stop_all_node_graphs()


def reload_graphs():
    import nodegraph.common.nodedata as nd
    nd.NodeGraphLoader.ReloadDataFromDisk()


def node_info():
    machoNet = sm.GetService('machoNet')
    print 'Pid:', os.getpid(), 'Node Index:', machoNet.nodeIndex, 'Node ID:', machoNet.GetNodeID()
