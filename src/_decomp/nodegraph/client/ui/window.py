#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\window.py
import eveicon
from carbonui import AxisAlignment, Density
from carbonui.button.const import ButtonVariant
from carbonui.button.group import ButtonGroup
from carbonui.services.setting import UserSettingBool
from carbonui.uicore import uicore
from collections import OrderedDict
import eveui
from eve.client.script.ui.control.historyBuffer import HistoryBuffer
from threadutils import scheduler
from eveprefs import prefs
from nodegraph.common.nodedata import NodeGraphLoader, get_node_graphs, get_node_graph_data
from nodegraph.client.custom_graph import get_custom_node_graphs, create_new_custom_node_graph, delete_custom_node_graph, delete_all_custom_node_graphs, copy_graph_to_clipboard, get_custom_node_graph_authored_id
import webbrowser
from .drawer import Drawer
from .editor import ActiveNodeGraphViewer, CustomNodeGraphViewer, LogNodeGraphViewer
from .search import NodeGraphSearch
from .list_item import NodeGraphListItem, ListItem
from .util import is_server_graph, is_client_graph, is_qa_graph, GraphColor
from .controllers import get_node_graph_view_controller_storage
from .view import AuthoredNodeGraphView

class NodeGraphEditorWindow(eveui.Window):
    default_name = 'NodeGraphEditorWindow'
    default_windowID = 'NodeGraphEditorWindow'
    default_caption = 'Node Graph Editor'
    default_width = 900
    default_height = 800
    default_clipChildren = True

    @classmethod
    def Open(cls, node_graph_id = None, from_history = False, *args, **kwargs):
        window = super(NodeGraphEditorWindow, cls).Open(*args, **kwargs)
        window._select_node_graph(node_graph_id, from_history=from_history)
        return window

    def ApplyAttributes(self, attributes):
        super(NodeGraphEditorWindow, self).ApplyAttributes(attributes)
        self._storage = get_node_graph_view_controller_storage()
        self._node_graph_id = None
        self._history_buffer = HistoryBuffer()
        self.OnBack = self._handle_go_back
        self.OnForward = self._handle_go_forward
        self._construct_layout()
        NodeGraphLoader.ConnectToOnReload(self._data_reloaded)
        self._should_reload_fsd_data = False
        self._update_sheduler = scheduler.WallTimeScheduler()
        self._update_sheduler.enter_repeated_interval_event(2, 2, 0, self._check_for_data_reload, ())
        self._update_sheduler.start()

    def _check_for_data_reload(self):
        try:
            if self._should_reload_fsd_data:
                self._should_reload_fsd_data = False
                self.Open(node_graph_id=self._node_graph_id)
        finally:
            return True

    def _data_reloaded(self):
        self._should_reload_fsd_data = True

    def _select_node_graph(self, node_graph_id, from_history = False):
        self._node_graph_id = node_graph_id
        self._update_history(from_history)
        self._drawer.close()
        self._editor_container.Flush()
        uicore.registry.SetFocus(self)
        if node_graph_id in sm.GetService('node_graph').get_active_node_graphs():
            ActiveNodeGraphViewer(parent=self._editor_container, controller=ActiveNodeGraphViewer.controller_class(node_graph_id))
        elif sm.GetService('node_graph').log_graphs.get(node_graph_id):
            LogNodeGraphViewer(parent=self._editor_container, controller=LogNodeGraphViewer.controller_class(node_graph_id))
        elif node_graph_id in get_custom_node_graphs():
            CustomNodeGraphViewer(parent=self._editor_container, controller=CustomNodeGraphViewer.controller_class(node_graph_id))
        elif node_graph_id in get_node_graphs():
            graph_controller = self._storage.get_node_graph(node_graph_id)
            graph_controller.node_graph_component_class(parent=self._editor_container, controller=graph_controller)
        else:
            self._constuct_nothing_selected()

    def _constuct_nothing_selected(self):
        selection_container = eveui.GridContainer(parent=self._editor_container, align=eveui.Align.to_all, columns=4, lines=1)
        NodeGraphSearch(parent=selection_container, padding=12, select_node_graph=self._select_node_graph)
        selection = self._construct_fsd_node_graph_selection()
        selection.SetParent(selection_container)
        selection.padding = 12
        selection = self._construct_custom_node_graph_selection()
        selection.SetParent(selection_container)
        selection.padding = 12
        selection = self._construct_active_node_graph_selection()
        selection.SetParent(selection_container)
        selection.padding = 12

    def _handle_home(self, *args, **kwargs):
        self._select_node_graph(None)

    def _handle_open_existing(self, *args, **kwargs):
        self._drawer.open(content=self._construct_active_node_graph_selection())

    def _handle_open_all(self, *args, **kwargs):
        self._drawer.open(content=self._construct_fsd_node_graph_selection())

    def _handle_open_custom(self, *args, **kwargs):
        self._drawer.open(content=self._construct_custom_node_graph_selection())

    def _construct_active_node_graph_selection(self):
        return ActiveNodeGraphSelection(title='Active Node Graphs', select_node_graph=self._select_node_graph)

    def _construct_fsd_node_graph_selection(self):
        return NodeGraphSelection(title='FSD Node Graphs', select_node_graph=self._select_node_graph)

    def _construct_custom_node_graph_selection(self):
        return CustomNodeGraphSelection(title='Custom Node Graphs', select_node_graph=self._select_node_graph)

    def _update_history(self, open_from_history):
        if not open_from_history and (self._history_buffer.IsEmpty() or self._node_graph_id != self._history_buffer.GetCurrent()):
            self._history_buffer.Append(self._node_graph_id)
        self._back_button.enabled = self._history_buffer.IsBackEnabled()
        self._forward_button.enabled = self._history_buffer.IsForwardEnabled()

    def _handle_go_back(self, *args, **kwargs):
        if self._history_buffer.IsBackEnabled():
            node_graph_id = self._history_buffer.GoBack()
            NodeGraphEditorWindow.Open(node_graph_id=node_graph_id, from_history=True)

    def _handle_go_forward(self, *args, **kwargs):
        if self._history_buffer.IsForwardEnabled():
            node_graph_id = self._history_buffer.GoForward()
            NodeGraphEditorWindow.Open(node_graph_id=node_graph_id, from_history=True)

    def _construct_layout(self):
        self._drawer = Drawer(parent=self.GetMainArea(), drawer_size=400)
        container = eveui.Container(parent=self.GetMainArea(), align=eveui.Align.to_all)
        self._construct_top_bar(container)
        self._editor_container = eveui.Container(parent=container, state=eveui.State.normal, align=eveui.Align.to_all, padTop=8)

    def _construct_top_bar(self, parent):
        container = eveui.ContainerAutoSize(parent=parent, align=eveui.Align.to_top, alignMode=eveui.Align.to_top)
        self._construct_history_buttons(container)
        if prefs.clusterMode != 'LIVE':
            eveui.Checkbox(parent=container, align=eveui.Align.to_right, text='Server Logs', checked=sm.GetService('node_graph').log_graphs.subscribed_to_logs, callback=self._toggle_server_logs)
        group = ButtonGroup(parent=container, align=eveui.Align.to_top, button_alignment=AxisAlignment.START, density=Density.COMPACT, padLeft=16)
        eveui.Button(parent=group, label='Home', func=self._handle_home)
        eveui.Button(parent=group, label='FSD Graphs', func=self._handle_open_all)
        eveui.Button(parent=group, label='Custom Graphs', func=self._handle_open_custom)
        eveui.Button(parent=group, label='Active Graphs', func=self._handle_open_existing)
        eveui.Button(parent=group, label='Documentation', func=self._open_documentation, variant=ButtonVariant.GHOST)

    def _open_documentation(self, *args):
        webbrowser.open('https://ccpgames.atlassian.net/wiki/spaces/ET/pages/238092504/Node+Graphs')

    def GetMenuMoreOptions(self):
        menu_data = super(NodeGraphEditorWindow, self).GetMenuMoreOptions()
        menu_data.AddSeparator()
        menu_data.AddEntry(text='Documentation', func=self._open_documentation, texturePath='res:/ui/Texture/Shared/questionMark.png')
        return menu_data

    def _construct_history_buttons(self, parent):
        container = eveui.Container(parent=parent, align=eveui.Align.to_left, width=36)
        self._back_button = eveui.ButtonIcon(parent=container, align=eveui.Align.center_left, texture_path=eveicon.navigate_back, size=16, on_click=self._handle_go_back, enabled=self._history_buffer.IsBackEnabled(), opacity_enabled=0.6, opacity_disabled=0.2)
        self._forward_button = eveui.ButtonIcon(parent=container, align=eveui.Align.center_right, texture_path=eveicon.navigate_forward, size=16, on_click=self._handle_go_forward, enabled=self._history_buffer.IsForwardEnabled(), opacity_enabled=0.6, opacity_disabled=0.2)

    def _toggle_server_logs(self, checkbox, *args):
        if checkbox.GetValue():
            sm.GetService('node_graph').log_graphs.subscribe()
        else:
            sm.GetService('node_graph').log_graphs.unsubscribe()


class NodeGraphSelection(eveui.Container):

    def __init__(self, title, select_node_graph, **kwargs):
        super(NodeGraphSelection, self).__init__(**kwargs)
        self._title = title
        self._node_graphs = self._get_node_graphs()
        self._select_node_graph = select_node_graph
        self._layout()

    def _get_node_graphs(self):
        sorted_graphs = [ (key, value) for key, value in sorted(get_node_graphs().items(), key=lambda x: x[1].name) ]
        return OrderedDict(sorted_graphs)

    def _handle_right_click(self, node_graph_id):
        pass

    def _layout(self):
        eveui.EveLabelLarge(parent=self, align=eveui.Align.to_top, text=self._title, padBottom=12)
        filter_container = eveui.Container(name='FilterNodeGraphsContainer', parent=self, align=eveui.Align.to_top, clipChildren=True, padBottom=10)
        self._add_server_filter(parent=filter_container)
        self._add_client_filter(parent=filter_container)
        self._add_qa_filter(parent=filter_container)
        filter_container.height = self.client_cb.height
        self.textfield = eveui.TextField(parent=self, align=eveui.Align.to_top, padBottom=12, placeholder='Filter...')
        self.textfield.controller.bind(text=self._on_text_changed)
        uicore.registry.SetFocus(self.textfield)
        self._list_container = eveui.ScrollContainer(parent=self, align=eveui.Align.to_all)
        self.load_list_items()

    def _get_setting_prefix_filter(self):
        return 'nodegraph_cb_%s' % self.__class__.__name__

    def _add_server_filter(self, parent):
        setting_prefix = self._get_setting_prefix_filter()
        server_cb_setting = UserSettingBool('%s_%s' % (setting_prefix, 'server'), True)
        self.server_cb = eveui.Checkbox(parent=parent, align=eveui.Align.to_left, text='Server', left=10, checked=True, callback=self.reload_list, setting=server_cb_setting)
        eveui.Fill(parent=self.server_cb, align=eveui.Align.top_left, color=GraphColor.server, pos=(-2,
         self.server_cb.checkboxCont.top,
         2,
         self.server_cb.checkboxCont.height))

    def _add_client_filter(self, parent):
        setting_prefix = self._get_setting_prefix_filter()
        client_cb_setting = UserSettingBool('%s_%s' % (setting_prefix, 'client'), True)
        self.client_cb = eveui.Checkbox(parent=parent, align=eveui.Align.to_left, text='Client', left=10, checked=True, callback=self.reload_list, setting=client_cb_setting)
        eveui.Fill(parent=self.client_cb, align=eveui.Align.top_left, color=GraphColor.client, pos=(-2,
         self.server_cb.checkboxCont.top,
         2,
         self.server_cb.checkboxCont.height))

    def _add_qa_filter(self, parent):
        setting_prefix = self._get_setting_prefix_filter()
        qa_cb_setting = UserSettingBool('%s_%s' % (setting_prefix, 'qa'), True)
        self.qa_cb = eveui.Checkbox(parent=parent, align=eveui.Align.to_left, text='QA', left=10, checked=True, callback=self.reload_list, setting=qa_cb_setting)
        eveui.Fill(parent=self.qa_cb, align=eveui.Align.top_left, color=GraphColor.qa, pos=(-2,
         self.server_cb.checkboxCont.top,
         2,
         self.server_cb.checkboxCont.height))

    def reload_list(self, *args):
        self.load_list_items()

    def load_list_items(self):
        self._list_container.Flush()
        for node_graph_id in self._node_graphs:
            if self.is_item_filtered_out(node_graph_id):
                continue
            self._add_list_item(node_graph_id)

        self.filter_items(self.textfield.text)

    def _add_list_item(self, node_graph_id):
        NodeGraphListItem(parent=self._list_container, node_graph_id=node_graph_id, on_click=self._select_node_graph, on_right_click=self._handle_right_click)

    def _get_node_graph_tags(self, node_graph_id):
        return self._node_graphs[node_graph_id].tags

    def is_item_filtered_out(self, node_graph_id):
        tags = self._get_node_graph_tags(node_graph_id)
        _is_server_graph = is_server_graph(tags)
        _is_client_graph = is_client_graph(tags)
        _is_qa_graph = is_qa_graph(tags)
        if _is_qa_graph:
            return not self.qa_cb.checked
        if _is_server_graph and _is_client_graph:
            return False
        if _is_server_graph and not self.server_cb.checked:
            return True
        if _is_client_graph and not self.client_cb.checked:
            return True
        return False

    def _on_text_changed(self, controller, text):
        self.filter_items(text)

    def filter_items(self, text):
        text = text.lower()
        for item in self._list_container.mainCont.children:
            item.filter_item(text)


class ActiveNodeGraphSelection(NodeGraphSelection):

    def __init__(self, **kwargs):
        super(ActiveNodeGraphSelection, self).__init__(**kwargs)
        if self._node_graphs:
            ListItem(parent=self._list_container, name='STOP ALL GRAPHS', on_click=self._stop_all_graphs, idx=0)

    def _get_node_graphs(self):
        graphs = {}
        for graph_id, graph in sm.GetService('node_graph').get_active_node_graphs().iteritems():
            graphs[graph_id] = graph

        for graph_id, graph in sm.GetService('node_graph').log_graphs.get_all().iteritems():
            graphs[graph_id] = graph

        return graphs

    def _add_list_item(self, instance_id):
        node_graph_id = self._node_graphs[instance_id].graph_id
        if isinstance(node_graph_id, int):
            NodeGraphListItem(parent=self._list_container, node_graph_id=node_graph_id, instance_id=instance_id, on_click=self._select_node_graph, on_right_click=self._handle_right_click)
        else:
            ListItem(parent=self._list_container, list_item_id=node_graph_id, name=node_graph_id, on_click=self._select_node_graph, on_right_click=self._handle_right_click)

    def _stop_all_graphs(self, *args, **kwargs):
        service = sm.GetService('node_graph')
        all_graphs = service._active_graphs.keys()
        for graph_id in all_graphs:
            service.stop_node_graph(graph_id)

        service.log_graphs.stop_all()
        self._select_node_graph(None)


class CustomNodeGraphSelection(NodeGraphSelection):

    def __init__(self, **kwargs):
        super(CustomNodeGraphSelection, self).__init__(**kwargs)
        ListItem(parent=self._list_container, name='CREATE NEW GRAPH', on_click=self._create_new, on_right_click=self._handle_right_click_new_item, idx=0)

    def _get_node_graphs(self):
        sorted_graphs = [ (key, value) for key, value in sorted(get_custom_node_graphs().items(), key=lambda x: self._get_node_graph_name(x[0])) ]
        return OrderedDict(sorted_graphs)

    def _add_list_item(self, custom_node_graph_id):
        authored_id = get_custom_node_graph_authored_id(custom_node_graph_id)
        if authored_id and get_node_graph_data(authored_id):
            NodeGraphListItem(parent=self._list_container, list_item_id=custom_node_graph_id, node_graph_id=authored_id, on_click=self._select_node_graph, on_right_click=self._handle_right_click)
        else:
            ListItem(parent=self._list_container, list_item_id=custom_node_graph_id, name=self._get_node_graph_name(custom_node_graph_id), on_click=self._select_node_graph, on_right_click=self._handle_right_click)

    def _get_node_graph_name(self, node_graph_id):
        authored_id = get_custom_node_graph_authored_id(node_graph_id)
        if authored_id:
            authored_graph = get_node_graph_data(authored_id)
            if authored_graph:
                return u'{} ({})'.format(authored_graph.name, node_graph_id)
            else:
                return 'FSD GRAPH NO LONGER EXIST: {}'.format(node_graph_id)
        else:
            return node_graph_id

    def _get_node_graph_tags(self, node_graph_id):
        authored_id = get_custom_node_graph_authored_id(node_graph_id)
        if authored_id:
            authored_graph = get_node_graph_data(authored_id)
            if authored_graph:
                return get_node_graph_data(authored_id).tags
        return []

    def _handle_right_click(self, node_graph_id):
        return [('Copy to clipboard', lambda : copy_graph_to_clipboard(node_graph_id)), ('Delete', lambda : self._delete_graph(node_graph_id))]

    def _handle_right_click_new_item(self, node_graph_id):
        return [('Delete All', self._delete_all_graphs)]

    def _delete_graph(self, node_graph_id):
        delete_custom_node_graph(node_graph_id)
        self._select_node_graph(None)

    def _delete_all_graphs(self):
        delete_all_custom_node_graphs()
        self._select_node_graph(None)

    def _create_new(self, *args, **kwargs):
        node_graph_id = create_new_custom_node_graph()
        self._select_node_graph(node_graph_id)
