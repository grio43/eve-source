#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\active_instances.py
import eveui
import threadutils
from .collapse_section import CollapseSection
from .controller import open_node_graph

class ActiveInstances(CollapseSection):
    default_name = 'ActiveInstances'

    def __init__(self, controller, **kwargs):
        self._controller = controller
        self._controller.on_update.connect(self.refresh_content)
        super(ActiveInstances, self).__init__(title='Active Instances', **kwargs)

    def close(self):
        self._controller.on_update.disconnect(self.refresh_content)

    @threadutils.threaded
    def construct_content(self):
        active_instances = sm.GetService('node_graph').get_active_instances_by_id(self._controller.node_graph_id) or sm.GetService('node_graph').log_graphs.get_all_by_id(self._controller.node_graph_id)
        if not active_instances:
            eveui.EveLabelMedium(parent=self.content_container, align=eveui.Align.to_top, text='No active instances')
        else:
            for instance_id in active_instances:
                self._construct_item(instance_id)

    def _construct_item(self, instance_id):
        ActiveInstanceListItem(parent=self.content_container, instance_id=instance_id)


class ActiveInstanceListItem(eveui.ContainerAutoSize):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top

    def __init__(self, instance_id, **kwargs):
        super(ActiveInstanceListItem, self).__init__(**kwargs)
        self._instance_id = instance_id
        self._bg_fill = eveui.Fill(bgParent=self, opacity=0)
        text_container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top, padding=(8, 4, 8, 4))
        eveui.EveLabelMedium(parent=text_container, align=eveui.Align.to_top, text=instance_id)

    def OnClick(self, *args):
        open_node_graph(self._instance_id)

    def GetMenu(self):
        return [('Stop graph', lambda : sm.GetService('node_graph').stop_node_graph(self._instance_id))]

    def OnMouseEnter(self, *args):
        eveui.fade_in(self._bg_fill, end_value=0.05, duration=0.1)

    def OnMouseExit(self, *args):
        eveui.fade_out(self._bg_fill, duration=0.1)
