#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\sub_graphs.py
import eveui
import threadutils
from .collapse_section import CollapseSection
from .controller import open_node_graph
from nodegraph.common.nodedata import get_node_graph_data, get_sub_graphs, get_root_graph_id
from nodegraph.common.nodes.node_graph import SubGraphNode

class AuthoredHierarchy(CollapseSection):
    default_name = 'AuthoredHierarchy'

    def __init__(self, controller, **kwargs):
        self._controller = controller
        self._controller.on_update.connect(self.refresh_content)
        super(AuthoredHierarchy, self).__init__(title='Graph Hierarchy', default_expanded=False, **kwargs)

    def close(self):
        self._controller.on_update.disconnect(self.refresh_content)

    @threadutils.threaded
    def construct_content(self):
        root_graph_id = get_root_graph_id(self._controller.node_graph_id)
        self._construct_item(root_graph_id, get_node_graph_data(root_graph_id).name)

    def _construct_item(self, node_graph_id, node_graph_name, indent = 0):
        item = SubGraphListItem(parent=self.content_container, node_graph_id=node_graph_id, title=node_graph_name, padLeft=8 * indent)
        if node_graph_id == self._controller.node_graph_id:
            eveui.Frame(bgParent=item, color=(0, 0, 0.75))
        sorted_graphs = sorted([ (get_node_graph_data(node_graph_id).name, node_graph_id) for node_graph_id in get_sub_graphs(node_graph_id) ])
        for graph_name, graph_id in sorted_graphs:
            self._construct_item(graph_id, graph_name, indent + 1)


class SubGraphs(CollapseSection):
    default_name = 'SubGraphs'

    def __init__(self, controller, **kwargs):
        self._controller = controller
        self._controller.on_update.connect(self.refresh_content)
        super(SubGraphs, self).__init__(title='Sub graphs', **kwargs)

    def close(self):
        self._controller.on_update.disconnect(self.refresh_content)

    @threadutils.threaded
    def construct_content(self):
        if self._controller.parent_graph_id:
            SubGraphListItem(parent=self.content_container, node_graph_id=self._controller.parent_graph_id, title=get_node_graph_data(self._controller.parent_graph_id).name, subtitle='PARENT GRAPH')
        sub_graphs = []
        for node_id in sorted(self._controller.nodes_data):
            node_controller = self._controller.get_node_controller(node_id)
            if node_controller.node_type != SubGraphNode.node_type_id:
                continue
            node_graph_id = node_controller.get_parameter_value('node_graph_id')
            if node_graph_id is None:
                sub_graphs.append(('MISSING NODE GRAPH ID', node_id, None))
            elif node_graph_id == 'connection':
                sub_graphs.append(('CONNECTED NODE GRAPH ID', node_id, node_graph_id))
            else:
                sub_graphs.append((get_node_graph_data(node_graph_id).name, node_id, node_graph_id))

        if sub_graphs and self._controller.parent_graph_id:
            eveui.Line(parent=self.content_container, align=eveui.Align.to_top, weight=0.5, padTop=6, padBottom=6)
        sub_graphs.sort()
        for title, node_id, node_graph_id in sub_graphs:
            SubGraphListItem(parent=self.content_container, node_graph_id=node_graph_id, node_id=node_id, controller=self._controller, title=title, subtitle=u'Node ID: {}'.format(node_id))

        if not len(self.content_container.children):
            eveui.EveLabelMedium(parent=self.content_container, align=eveui.Align.to_top, text='No sub graphs in this graph')


class SubGraphListItem(eveui.ContainerAutoSize):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top

    def __init__(self, node_graph_id, title, subtitle = None, node_id = None, controller = None, **kwargs):
        super(SubGraphListItem, self).__init__(**kwargs)
        self._node_graph_id = node_graph_id
        self._node_id = node_id
        self._controller = controller
        self._bg_fill = eveui.Fill(bgParent=self, opacity=0)
        text_container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top, padding=(8, 4, 8, 4))
        eveui.EveLabelMedium(parent=text_container, align=eveui.Align.to_top, maxLines=1, text=title)
        if subtitle:
            eveui.EveLabelSmall(parent=text_container, align=eveui.Align.to_top, maxLines=1, text=subtitle, color=(0.7, 0.7, 0.7, 0.6))

    def OnClick(self, *args):
        open_node_graph(self._node_graph_id)

    def OnMouseEnter(self, *args):
        if self._node_id:
            self._controller.highlight_node(self._node_id)
        eveui.fade_in(self._bg_fill, end_value=0.05, duration=0.1)

    def OnMouseExit(self, *args):
        if self._node_id:
            self._controller.unhighlight_node(self._node_id)
        eveui.fade_out(self._bg_fill, duration=0.1)
