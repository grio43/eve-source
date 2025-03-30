#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\list_item.py
import eveui
from nodegraph.common.nodedata import get_node_graph_data
from .util import is_client_graph, is_server_graph, is_qa_graph, GraphColor

class ListItem(eveui.Container):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_height = 30

    def __init__(self, list_item_id = None, name = None, on_click = None, on_right_click = None, *args, **kwargs):
        super(ListItem, self).__init__(*args, **kwargs)
        self._on_click = on_click
        self._on_right_click = on_right_click
        self._name_lower = self.name.lower()
        self._list_item_id = list_item_id
        self.content_container = eveui.Container(parent=self, align=eveui.Align.to_all, padding=6)
        self.name_label = eveui.EveLabelMedium(parent=self.content_container, text=name)
        self._bg = eveui.Fill(parent=self, opacity=0.05)

    def OnMouseEnter(self, *args):
        eveui.fade(self._bg, end_value=0.2, duration=0.1)

    def OnMouseExit(self, *args):
        eveui.fade(self._bg, end_value=0.05, duration=0.1)

    def OnClick(self, *args):
        if self._on_click:
            self._on_click(self._list_item_id)

    def GetMenu(self):
        if self._on_right_click:
            return self._on_right_click(self._list_item_id)

    def filter_item(self, filter):
        if filter in self._name_lower:
            self.state = eveui.State.normal
        else:
            self.state = eveui.State.hidden


class NodeGraphListItem(ListItem):

    def __init__(self, node_graph_id, instance_id = None, *args, **kwargs):
        self._node_graph_id = node_graph_id
        self._instance_id = instance_id
        kwargs['name'] = self.name
        kwargs.setdefault('list_item_id', self._instance_id or self._node_graph_id)
        super(NodeGraphListItem, self).__init__(*args, **kwargs)
        self._update_hint()
        if self.tags:
            self.name_label.left = 6
            self._construct_tag_color()

    def _construct_tag_color(self):
        server_graph = is_server_graph(self.tags)
        client_graph = is_client_graph(self.tags)
        qa_graph = is_qa_graph(self.tags)
        if qa_graph:
            color = GraphColor.qa
            hint = 'QA graph'
        elif server_graph and client_graph:
            color = GraphColor.warning
            hint = '!! Both client and server tags !!'
        elif server_graph:
            color = GraphColor.server
            hint = 'Server Graph'
        elif client_graph:
            color = GraphColor.client
            hint = 'Client Graph'
        else:
            color = GraphColor.warning
            hint = '!! Neither client nor server tag !!'
        cont = eveui.Container(parent=self.content_container, align=eveui.Align.to_left_no_push, width=6, state=eveui.State.normal)
        eveui.Line(parent=cont, color=color + (1.0,), align=eveui.Align.to_left, idx=0, weight=2)
        cont.hint = hint
        cont.OnClick = self.OnClick

    def _update_hint(self):
        hint = self.description
        tags = self.tags
        if tags:
            hint = u'{}\n\n'.format(hint) if hint else ''
            hint += u'Tags:\n{}'.format(', '.join(tags))
        self.hint = hint

    @property
    def data(self):
        return get_node_graph_data(self._node_graph_id)

    @property
    def name(self):
        if self._instance_id:
            return u'{} ({} - {})'.format(self.data.name, self._node_graph_id, self._instance_id)
        return u'{} ({})'.format(self.data.name, self._node_graph_id)

    @property
    def tags(self):
        return self.data.tags or []

    @property
    def description(self):
        return self.data.description or ''
