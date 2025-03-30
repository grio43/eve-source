#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\active_graph_hierarchy.py
import eveui
from .collapse_section import CollapseSection
from .controller import open_node_graph

class ActiveGraphHierarchy(CollapseSection):
    default_name = 'ActiveGraphHierarchy'

    def __init__(self, controller, **kwargs):
        self._controller = controller
        sm.RegisterForNotifyEvent(self, 'OnNodeGraphStarted')
        sm.RegisterForNotifyEvent(self, 'OnNodeGraphStopped')
        super(ActiveGraphHierarchy, self).__init__(title='Graph Hierarchy', **kwargs)

    def close(self):
        sm.UnregisterForNotifyEvent(self, 'OnNodeGraphStarted')
        sm.UnregisterForNotifyEvent(self, 'OnNodeGraphStopped')

    def OnNodeGraphStarted(self, instance_id, node_graph_id):
        self.refresh_content()

    def OnNodeGraphStopped(self, instance_id, node_graph_id):
        self.refresh_content()

    def construct_content(self):
        self._construct_remote_graph_item()
        self._construct_item(self._controller.node_graph.context.get_value('root_graph_instance_id'))

    def _construct_item(self, instance_id, indent = 0):
        node_graph = sm.GetService('node_graph').get_active_node_graph(instance_id) or sm.GetService('node_graph').log_graphs.get(instance_id)
        if not node_graph:
            return
        GraphListItem(parent=self.content_container, node_graph=node_graph, is_selected=self._controller.node_graph.instance_id == instance_id, padLeft=8 * indent)
        for sub_graph_id in node_graph.active_sub_graphs:
            self._construct_item(sub_graph_id, indent + 1)

    def _construct_remote_graph_item(self):
        if self._controller.is_server_graph:
            instance_id = self._controller.node_graph.context.get_value('client_graph_instance_id')
        else:
            instance_id = self._controller.node_graph.context.get_value('server_graph_instance_id')
        if instance_id:
            node_graph = sm.GetService('node_graph').get_active_node_graph(instance_id) or sm.GetService('node_graph').log_graphs.get(instance_id)
            if node_graph:
                GraphListItem(parent=self.content_container, node_graph=node_graph, is_selected=self._controller.node_graph.instance_id == instance_id, padBottom=8, bgColor=(1, 0, 0, 0.2))


class GraphListItem(eveui.ContainerAutoSize):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top

    def __init__(self, node_graph, is_selected, **kwargs):
        super(GraphListItem, self).__init__(**kwargs)
        self._node_graph = node_graph
        self._bg_fill = eveui.Fill(bgParent=self, opacity=0)
        text_container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top, padding=(8, 4, 8, 4))
        if is_selected:
            eveui.Frame(bgParent=self, color=(0, 0, 0.75))
        eveui.EveLabelMedium(parent=text_container, align=eveui.Align.to_top, maxLines=1, text=node_graph.name)
        eveui.EveLabelSmall(parent=text_container, align=eveui.Align.to_top, maxLines=1, text=node_graph.instance_id, color=(0.7, 0.7, 0.7, 0.6))

    def OnClick(self, *args):
        open_node_graph(self._node_graph.instance_id)

    def OnMouseEnter(self, *args):
        eveui.fade_in(self._bg_fill, end_value=0.05, duration=0.1)

    def OnMouseExit(self, *args):
        eveui.fade_out(self._bg_fill, duration=0.1)
