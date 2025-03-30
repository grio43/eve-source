#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\editor_drawer.py
import yaml
from carbonui.uicore import uicore
import eveui
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from nodegraph.common.atomdata import get_atom_data, get_action_atoms, get_condition_atoms, get_event_atoms, get_getter_atoms
from nodegraph.common.nodedata import get_node_type, get_node_types
from nodegraph.common.nodes.action import ActionNode
from nodegraph.common.nodes.event import EventNode
from nodegraph.common.nodes.getter import GetterNode
from nodegraph.common.nodes.validation import ValidationNode
from .parameter_field import ParameterField
from .drawer import Drawer
import blue

class EditorDrawer(Drawer):

    def __init__(self, controller, **kwargs):
        super(EditorDrawer, self).__init__(drawer_alignment=eveui.Align.to_right, drawer_size=400, **kwargs)
        self._controller = controller

    def edit_graph_data(self, *args, **kwargs):
        content = EditGraphData(controller=self._controller, close_drawer=self.close)
        self.set_content(content)
        self._open()

    def edit_node(self, node_id):
        content = EditNode(node_id=node_id, controller=self._controller, close_drawer=self.close)
        self.set_content(content)
        self._open()

    def create_node(self, position, connection = None):
        content = AddNode(add_node=self._add_node, position=position, controller=self._controller)
        self.set_content(content)
        self._open()

    def _add_node(self, node_type_id, position, atom_type_id):
        node_id = self._controller.add_node(node_type_id, position, atom_type_id)
        self.edit_node(node_id)


class EditGraphData(eveui.Container):
    default_align = eveui.Align.to_all

    def __init__(self, controller, close_drawer, **kwargs):
        super(EditGraphData, self).__init__(**kwargs)
        self._controller = controller
        self._close_drawer = close_drawer
        self._layout()

    def _layout(self):
        self._edit_field = EditPlainText(parent=self, state=eveui.State.disabled, align=eveui.Align.to_all, setvalue=yaml.safe_dump(self._controller.nodes_data, indent=2, default_flow_style=False, allow_unicode=True))
        if not self._controller.can_edit:
            self._edit_field.state = eveui.State.disabled


class EditNode(eveui.ScrollContainer):
    default_align = eveui.Align.to_all

    def __init__(self, node_id, controller, close_drawer, **kwargs):
        super(EditNode, self).__init__(**kwargs)
        self._graph_controller = controller
        self._node_controller = controller.get_node_controller(node_id)
        self._node_id = node_id
        self._close_drawer = close_drawer
        self._param_fields = {}
        self._layout()

    def _layout(self):
        node_data = self._node_controller.node_data
        eveui.EveLabelLarge(parent=self, align=eveui.Align.to_top, text=self._node_controller.title)
        eveui.EveLabelMedium(parent=self, align=eveui.Align.to_top, text=u'ID: {}\nPosition: ({}, {})'.format(self._node_id, *node_data.position), padBottom=12)
        description = self._node_controller.description
        if description:
            eveui.EveLabelMedium(parent=self, align=eveui.Align.to_top, text=description, padBottom=12)
        tags = self._node_controller.tags
        if tags:
            eveui.EveLabelMedium(parent=self, align=eveui.Align.to_top, text='Tags: {}'.format(', '.join(tags)), padBottom=6)
        output_description = self._node_controller.output_description
        if output_description:
            eveui.EveLabelMedium(parent=self, align=eveui.Align.to_top, text='Outputs:\n{}'.format(output_description), color=(0, 1, 0, 0.6), padBottom=12)
        self._construct_parameters(node_data)
        self._construct_comment(node_data)

    def _construct_parameters(self, node_data):
        node_type = get_node_type(node_data.nodeType)
        container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top)
        for parameter in node_type.parameters.inputs:
            if parameter.parameterKey == 'atom_id':
                continue
            can_edit = self._graph_controller.can_edit
            if parameter.parameterKey in node_data.nodeParameters:
                if node_data.nodeParameters[parameter.parameterKey].connection:
                    value = parameter.defaultValue
                    can_edit = False
                else:
                    value = node_data.nodeParameters[parameter.parameterKey].value
            else:
                value = parameter.defaultValue
            param_field = ParameterField(parent=container, align=eveui.Align.to_top, parameter=parameter, value=value, on_change=self._parameter_changed, can_edit=can_edit)
            self._param_fields[parameter.parameterKey] = param_field

        if 'atom_id' in node_data.nodeParameters:
            atom_type = get_atom_data(node_data.nodeParameters['atom_id'].value)
            for parameter in atom_type.parameters.inputs:
                can_edit = self._graph_controller.can_edit
                if node_data.atomParameters and parameter.parameterKey in node_data.atomParameters:
                    if node_data.atomParameters[parameter.parameterKey].connection:
                        value = parameter.defaultValue
                        can_edit = False
                    else:
                        value = node_data.atomParameters[parameter.parameterKey].value
                else:
                    value = parameter.defaultValue
                param_field = ParameterField(parent=container, align=eveui.Align.to_top, parameter=parameter, value=value, on_change=self._parameter_changed, can_edit=can_edit)
                self._param_fields[parameter.parameterKey] = param_field

        if self._param_fields:
            eveui.EveLabelLarge(parent=container, align=eveui.Align.to_top, idx=0, text='Parameters', padTop=12)

    def _parameter_changed(self, parameter_id, value):
        self._graph_controller.update_node_parameter(self._node_id, parameter_id, value)

    def _construct_comment(self, node_data):
        eveui.EveLabelLarge(parent=self, align=eveui.Align.to_top, text='Comment', padTop=24, padBottom=6)
        self._comment_field = EditPlainText(parent=self, state=eveui.State.normal if self._graph_controller.can_edit else eveui.State.disabled, align=eveui.Align.to_top, setvalue=node_data.comment or '', padTop=6)
        self._comment_field.OnChange = self._comment_changed
        self._comment_field.EnableAutoSize()

    def _comment_changed(self):
        self._graph_controller.update_node_comment(self._node_id, self._comment_field.GetValue())


DATA_ALL = -1
DATA_OTHER = -2
DATA_GROUPS = 3
GROUP_OTHER = 'Other'
GROUP_ACTION = 'Action'
GROUP_EVENT = 'Event'
GROUP_VALIDATION = 'Condition'
GROUP_GETTER = 'Getter'

class AddNode(eveui.Container):
    default_align = eveui.Align.to_all

    def __init__(self, position, add_node, controller, connection = None, **kwargs):
        super(AddNode, self).__init__(**kwargs)
        self._add_node = add_node
        self._position = position
        self._atom_type = None
        self._data_loaded = None
        self._view_mode = 'server' if controller.is_server_graph else 'client'
        self._connection = connection
        self.create_mapping()
        self._layout()

    def create_mapping(self):
        self._node_type_by_group_id = {GROUP_ACTION: ActionNode.node_type_id,
         GROUP_EVENT: EventNode.node_type_id,
         GROUP_VALIDATION: ValidationNode.node_type_id,
         GROUP_GETTER: GetterNode.node_type_id}
        self._atom_getters_by_group_id = {GROUP_ACTION: get_action_atoms,
         GROUP_EVENT: get_event_atoms,
         GROUP_VALIDATION: get_condition_atoms,
         GROUP_GETTER: get_getter_atoms}

    def _handle_select_group(self, group_id):
        self._back_button.state = eveui.State.normal
        if group_id == GROUP_OTHER:
            self._construct_node_selection()
        else:
            getter_func = self._atom_getters_by_group_id.get(group_id, None)
            if getter_func:
                node_type = self._node_type_by_group_id.get(group_id, None)
                atoms = getter_func()
                self._construct_atom_selection(atoms, node_type)

    def _handle_select_node(self, node_type_id, *args):
        self._add_node(node_type_id, self._position, self._atom_type)

    def _handle_select_atom(self, atom_id, node_type):
        self._atom_type = atom_id
        self._add_node(node_type, self._position, self._atom_type)

    def _handle_go_back(self):
        self._back_button.state = eveui.State.hidden
        self._construct_group_selection()

    def _layout(self):
        eveui.EveLabelLarge(parent=self, align=eveui.Align.to_top, text='Add node', padBottom=12)
        filter_container = eveui.Container(parent=self, align=eveui.Align.to_top, height=26, padBottom=12)
        self._back_button = eveui.Container(parent=filter_container, state=eveui.State.hidden, align=eveui.Align.to_left, width=26)
        eveui.ButtonIcon(parent=self._back_button, align=eveui.Align.center_left, texture_path='res:/UI/Texture/Shared/DarkStyle/backward.png', size=16, on_click=self._handle_go_back)
        self._filter = eveui.TextField(parent=filter_container, align=eveui.Align.to_top, placeholder='Filter...')
        self._filter.controller.bind(text=self._on_text_changed)
        self._list_container = eveui.ScrollContainer(parent=self, align=eveui.Align.to_all)
        self._construct_group_selection()

    def _construct_group_selection(self):
        uicore.registry.SetFocus(self._filter)
        self._filter.text = ''
        self.load_group_selection()

    def load_group_selection(self):
        self._data_loaded = DATA_GROUPS
        self._list_container.Flush()
        node_groups = [GROUP_ACTION,
         GROUP_EVENT,
         GROUP_VALIDATION,
         GROUP_GETTER,
         GROUP_OTHER]
        for node_group_id in node_groups:
            node_type_id = self._node_type_by_group_id.get(node_group_id, None)
            NodeGroupListItem(parent=self._list_container, node_group_id=node_group_id, on_click=self._handle_select_group, node_type_id=node_type_id)

    def _construct_node_selection(self):
        data = self._get_node_selection_data()
        self._construct_items_list(data, self._handle_select_node, None, DATA_OTHER)

    def _get_node_selection_data(self):
        data = {key:value for key, value in get_node_types().iteritems() if key not in self._node_type_by_group_id.values()}
        return data

    def _construct_atom_selection(self, atoms, node_type):
        self._construct_items_list(atoms, self._handle_select_atom, node_type, node_type)

    def _construct_items_list(self, data, on_click, node_type_id, data_type):
        uicore.registry.SetFocus(self._filter)
        self._filter.text = ''
        self._list_container.Flush()
        sorted_data_and_click = self.prepare_sorted_data(data, on_click, node_type_id)
        self._construct_items(sorted_data_and_click, data_type)

    def prepare_sorted_data(self, data, on_click, node_type_id):
        sorted_data_and_click = [ (key,
         value,
         on_click,
         node_type_id) for key, value in sorted(data.items(), key=lambda x: x[1].name) ]
        return sorted_data_and_click

    def _construct_items(self, sorted_data_and_click, data_type):
        self._data_loaded = data_type
        for item_id, item_data, on_click, node_type_id in sorted_data_and_click:
            NodeClassListItem(parent=self._list_container, item_id=item_id, item_data=item_data, on_click=on_click, node_type_id=node_type_id)

        self.filter_items()

    def _on_text_changed(self, controller, text):
        if text:
            if self._data_loaded == DATA_GROUPS:
                self.load_all_data()
        elif self._data_loaded == DATA_ALL:
            self.load_group_selection()
        self.filter_items()

    def filter_items(self):
        for item in self._list_container.mainCont.children:
            item.filter_item(self._filter.text, tag=self._view_mode)

    def load_all_data(self):
        self._list_container.Flush()
        all_data_and_click = self.get_all_data()
        self._construct_items(all_data_and_click, DATA_ALL)

    def get_all_data(self):
        all_data = self.prepare_sorted_data(self._get_node_selection_data(), self._handle_select_node, None)
        for group_id in [GROUP_ACTION,
         GROUP_EVENT,
         GROUP_VALIDATION,
         GROUP_GETTER]:
            node_type_id = self._node_type_by_group_id.get(group_id, None)
            getter_func = self._atom_getters_by_group_id.get(group_id)
            atoms = getter_func()
            group_data = self.prepare_sorted_data(atoms, self._handle_select_atom, node_type_id)
            all_data.extend(group_data)

        all_data.sort(key=lambda x: x[1].name)
        return all_data


class NodeGroupListItem(eveui.Container):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_height = 30

    def __init__(self, node_group_id, on_click, **kwargs):
        super(NodeGroupListItem, self).__init__(**kwargs)
        node_type_id = kwargs.get('node_type_id')
        self._on_click = on_click
        self._node_group_id = node_group_id
        self._filter_string = node_group_id.lower()
        content_container = eveui.Container(parent=self, align=eveui.Align.to_all, padding=6)
        eveui.EveLabelMedium(parent=content_container, text=self._node_group_id, left=8)
        self._bg = eveui.Fill(parent=self, opacity=0.05)
        node_type = get_node_type(node_type_id)
        if node_type:
            color = node_type.color[:3] + (0.5,)
            eveui.Fill(parent=self, color=color, pos=(0, 0, 8, 8), align=eveui.Align.center_left)

    def OnClick(self, *args):
        self._on_click(self._node_group_id)

    def OnMouseEnter(self, *args):
        eveui.fade(self._bg, end_value=0.2, duration=0.1)

    def OnMouseExit(self, *args):
        eveui.fade(self._bg, end_value=0.05, duration=0.1)

    def filter_item(self, filter, tag = None):
        filter = filter.lower()
        if filter in self._filter_string:
            self.state = eveui.State.normal
        else:
            self.state = eveui.State.hidden


class NodeClassListItem(eveui.Container):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_height = 30

    def __init__(self, item_id, item_data, on_click, node_type_id, **kwargs):
        hint = item_data.description or ''
        self._tags = getattr(item_data, 'tags', [])
        if self._tags:
            if hint:
                hint += '\n\n'
            hint += 'Tags:\n{}'.format(', '.join(self._tags))
            hint += '\n\nnode_type_id: {}\nitem_id: {}'.format(node_type_id, item_id)
        kwargs.setdefault('hint', hint)
        super(NodeClassListItem, self).__init__(**kwargs)
        self._on_click = on_click
        self._item_id = item_id
        self._item_data = item_data
        self._node_type_id = node_type_id
        self._filter_string = '{} {}'.format(self._item_data.name.lower(), ' '.join(('"{}"'.format(tag) for tag in self._tags)))
        content_container = eveui.Container(parent=self, align=eveui.Align.to_all, padding=6)
        eveui.EveLabelMedium(parent=content_container, text=self._item_data.name, left=6)
        self._bg = eveui.Fill(parent=self, opacity=0.05)
        node_type = get_node_type(node_type_id or item_id)
        if node_type:
            color = node_type.color[:3] + (0.5,)
            eveui.Fill(parent=self, color=color, pos=(0, 0, 8, 8), align=eveui.Align.center_left)

    def OnClick(self, *args):
        self._on_click(self._item_id, self._node_type_id)

    def OnMouseEnter(self, *args):
        eveui.fade(self._bg, end_value=0.2, duration=0.1)

    def OnMouseExit(self, *args):
        eveui.fade(self._bg, end_value=0.05, duration=0.1)

    def filter_item(self, filter, tag = None):
        valid = True
        if filter:
            filter = filter.lower()
            if filter not in self._filter_string:
                valid = False
        if tag and self._tags and tag not in self._tags:
            valid = False
        if valid:
            self.state = eveui.State.normal
        else:
            self.state = eveui.State.hidden

    def GetMenu(self):
        m = [['Copy nodeTypeID: %s' % self._node_type_id, lambda *args: self._copy_value(self._node_type_id)], ['Copy itemID: %s' % self._item_id, lambda *args: self._copy_value(self._item_id)]]
        return m

    def _copy_value(self, copyValue, *args):
        return blue.pyos.SetClipboardData(unicode(copyValue))
