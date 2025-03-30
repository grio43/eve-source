#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\editor.py
from __future__ import absolute_import
import math
import geo2
import uthread2
import eveui
import threadutils
import utillib
from carbonui.uicore import uicore
from eve.client.script.ui.control.marqueeCont import MarqueeCont
from eve.client.script.ui.control.panContainer import PanContainer
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.util.various_unsorted import GetClipboardData
from nodegraph.common.nodedata import InPort
from .active_graph_hierarchy import ActiveGraphHierarchy
from .active_instances import ActiveInstances
from .blackboard_info import BlackboardInfo
from .controller import ActiveNodeGraphController, AuthoredNodeGraphController, CustomNodeGraphController, LogNodeGraphController
from .editor_drawer import EditorDrawer
from .logs import LogHistory
from .node import Node
from .node_connection import NodeConnectionLine
from .sub_graphs import SubGraphs, AuthoredHierarchy
from .util import position_to_ui, ui_to_position, get_connection_color

class NodeGraphEditor(eveui.Container):
    node_graph_color = (0, 0, 0)
    controller_class = None
    default_align = eveui.Align.to_all

    def __init__(self, controller, **kwargs):
        super(NodeGraphEditor, self).__init__(**kwargs)
        self._nodes = {}
        self._grid_highlight = None
        self._active_instances = None
        self._sub_graphs = None
        self._hierarchy = None
        self._controller = controller
        self._controller.on_update.connect(self._on_graph_updated)
        self._controller.on_focus_node.connect(self._pan_to_node)
        self._controller.on_highlight_node.connect(self._highlight_node)
        uthread2.start_tasklet(self._layout)

    def Close(self):
        if self._controller:
            if self._pan_container:
                self._controller.pan_left = self._pan_container.panLeft
                self._controller.pan_top = self._pan_container.panTop
            self._controller.close()
        super(NodeGraphEditor, self).Close()

    def _on_graph_updated(self):
        self._node_container.Flush()
        self._left_top_container.Flush()
        self._left_bot_container.Flush()
        self._construct_nodes()
        self._construct_left_top_content()
        self._construct_left_bot_content()

    def _handle_node_click(self, node_id):
        self._drawer.edit_node(node_id)

    def _pan_to_node(self, node_id):
        node_position = self._nodes[node_id].GetPosition()
        max_position = self._node_container.GetSize()
        pan_left = node_position[0] / float(max_position[0]) * self._controller.zoom_level
        pan_top = node_position[1] / float(max_position[1]) * self._controller.zoom_level
        self._pan_container.PanTo(pan_left, pan_top)

    def _highlight_node(self, node_id, highlight):
        self._nodes[node_id].toggle_highlight(highlight)

    def GetMenu(self):
        return None

    def OnClick(self, *args):
        if self._controller.selected_nodes and eveui.Key.control.is_down and not eveui.Key.shift.is_down:
            self._controller.clear_selection()

    def OnDblClick(self, *args):
        pass

    @eveui.skip_if_destroyed
    def _layout(self):
        self._drawer = EditorDrawer(parent=self, controller=self._controller)
        self._construct_left()
        self._construct_top()
        self._construct_node_container()
        self._construct_nodes()

    def _construct_left(self):
        parent = DragResizeCont(parent=self, align=eveui.Align.to_left, settingsID='node_graph_editor_left_side', minSize=150, maxSize=600, defaultSize=250, padRight=12)
        eveui.GradientSprite(bgParent=parent.mainCont, rgbData=((1.0, self.node_graph_color),), alphaData=((0.0, 0.5), (0.2, 0.0)), rotation=-math.pi * 0.5)
        container = eveui.Container(parent=parent.mainCont, align=eveui.Align.to_all, padding=8)
        header_container = eveui.ContainerAutoSize(parent=container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top)
        icon_container = eveui.Container(parent=header_container, align=eveui.Align.to_right, width=26)
        self.open_fsd_editor_button = eveui.ButtonIcon(parent=icon_container, align=eveui.Align.to_top, on_click=self._controller.open_fsd_page, texture_path='res:/UI/Texture/classes/agency/iconExternalContent.png', size=26)
        eveui.EveLabelLarge(parent=header_container, align=eveui.Align.to_top, text=u'{} ({})'.format(self._controller.name, self._controller.node_graph_id))
        eveui.EveLabelMedium(parent=header_container, align=eveui.Align.to_top, text=u'tags: {}'.format(', '.join(self._controller.tags)), opacity=0.8)
        self._left_top_container = eveui.ContainerAutoSize(parent=container, align=eveui.Align.to_top)
        self._construct_left_top_content()
        self._left_bot_container = eveui.ScrollContainer(parent=container, align=eveui.Align.to_all, padTop=12)
        self._left_bot_container.mainCont.padRight = 4
        self._construct_left_bot_content()

    def _construct_left_bot_content(self):
        pass

    def _construct_left_top_content(self):
        pass

    def _construct_top(self):
        parent = eveui.Container(parent=self, align=eveui.Align.to_top, height=50)
        self._coords = eveui.EveLabelMedium(parent=parent, align=eveui.Align.top_left, text='Coords:')
        uthread2.start_tasklet(self._update_coords_routine)
        NodeSearch(parent=parent, align=eveui.Align.bottom_left, controller=self._controller, get_nodes=lambda : self._nodes)

    def _construct_node_container(self):
        self._pan_container = parent = PanContainerWithMarqueeSelection(parent=self, align=eveui.Align.to_all, apply_selection_func=self.apply_marquee_selection, panLeft=self._controller.pan_left, panTop=self._controller.pan_top)
        self._pan_container.scale = self._controller.zoom_level
        parent.OnMouseWheel = self._on_mouse_wheel
        parent.GetMenu = self.GetMenu
        parent.OnClick = self.OnClick
        parent.OnDblClick = self.OnDblClick
        parent.OnDropData = self.OnDropData
        parent.OnDragEnter = self.OnDragEnter
        parent.OnDragExit = self.OnDragExit
        parent.OnDragMove = self.OnDragMove
        self._node_container = eveui.Transform(parent=parent.mainCont, align=eveui.Align.top_left)
        eveui.Frame(bgParent=self._node_container, color=(1, 1, 1, 0.25))

    def _construct_nodes(self):
        self._grid_highlight = eveui.Frame(parent=self._node_container, state=eveui.State.hidden, align=eveui.Align.top_left, color=(1, 0, 1, 0.25), width=225, height=80)
        max_x = 0
        max_y = 0
        for node_id, node_data in self._controller.nodes_data.iteritems():
            x, y = position_to_ui(*node_data.position)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
            node = Node(parent=self._node_container, align=eveui.Align.top_left, node_id=node_id, node_data=node_data, on_click=self._handle_node_click, controller=self._controller, top=y, left=x)
            self._nodes[node_id] = node

        self._node_container.SetSize(max_x + 800, max_y + 400)
        for node_id, node_data in self._controller.nodes_data.iteritems():
            for connection_id, to_node_ids in node_data.connections.iteritems():
                for to_node_id in to_node_ids:
                    self._add_connection(from_node_id=node_id, from_connection_type='output', from_connection_id=connection_id, to_node_id=to_node_id, to_connection_type='input', to_connection_id=InPort.input, connection_color=get_connection_color(connection_id))

            for parameter_id, parameter in node_data.nodeParameters.iteritems():
                if parameter.connection:
                    self._add_connection(from_node_id=parameter.connection.node, from_connection_type='output_variables', from_connection_id=parameter.connection.parameter, to_node_id=node_id, to_connection_type='input_variables', to_connection_id=parameter_id, connection_color=get_connection_color('variables'))

            if getattr(node_data, 'atomParameters', None):
                for parameter_id, parameter in node_data.atomParameters.iteritems():
                    if parameter.connection:
                        self._add_connection(from_node_id=parameter.connection.node, from_connection_type='output_variables', from_connection_id=parameter.connection.parameter, to_node_id=node_id, to_connection_type='input_variables', to_connection_id=parameter_id, connection_color=get_connection_color('variables'))

    def _add_connection(self, from_node_id, from_connection_type, from_connection_id, to_node_id, to_connection_type, to_connection_id, connection_color):
        point_a = self._nodes[from_node_id].get_connection_point_object(from_connection_type, from_connection_id)
        point_b = self._nodes[to_node_id].get_connection_point_object(to_connection_type, to_connection_id)
        connection_line = NodeConnectionLine(parent=self._node_container, point_a=point_a, point_b=point_b, color=connection_color)
        self._nodes[from_node_id].add_connection_line(connection_line)
        self._nodes[to_node_id].add_connection_line(connection_line)
        point_a.add_connection_line(connection_line)
        point_b.add_connection_line(connection_line)

    def _on_mouse_wheel(self, delta, *args):
        scale = self._pan_container.scale
        if delta > 0:
            scale += 0.1
        else:
            scale -= 0.1
        scale = min(1.0, max(scale, 0.5))
        self._controller.zoom_level = scale
        self._pan_container.scale = scale

    def _update_coords_routine(self):
        while not self.destroyed:
            position = self._get_relative_position()
            self._coords.text = 'Position: ({}, {})'.format(*position)
            uthread2.sleep(0.2)

    def _get_relative_position(self):
        position = (geo2.Vector(eveui.Mouse.position()) - geo2.Vector(self._node_container.GetAbsolutePosition())) / self._controller.zoom_level
        return ui_to_position(*position)

    def apply_marquee_selection(self, bL, bT, bW, bH):
        bX0 = bL
        bX1 = bL + bW
        bY0 = bT
        bY1 = bT + bH
        selected = []
        for node_id, node in self._nodes.iteritems():
            if self.is_marquee_selected(node, bX0, bX1, bY0, bY1):
                selected.append(node_id)

        if selected:
            self._controller.add_selection(selected)

    def is_marquee_selected(self, node, bX0, bX1, bY0, bY1):
        nL, nT, nW, nH = node.GetAbsolute()
        nX0 = nL
        nX1 = nL + nW
        nY0 = nT
        nY1 = nT + nH
        if nX0 > bX1:
            return False
        if nX1 < bX0:
            return False
        if nY0 > bY1:
            return False
        if nY1 < bY0:
            return False
        return True


class ActiveNodeGraphViewer(NodeGraphEditor):
    default_bgColor = (0, 0.2, 0, 0.1)
    node_graph_color = (0, 0.2, 0)
    controller_class = ActiveNodeGraphController

    def _layout(self):
        super(ActiveNodeGraphViewer, self)._layout()
        self._controller.node_graph.log.on_log.connect(self._on_graph_log)
        for active_node_id in self._controller.node_graph.active_node_ids:
            self._nodes[active_node_id].set_active()

    def Close(self):
        self._graph_hierarchy.close()
        self._blackboard_info.close()
        self._log_history.close()
        super(ActiveNodeGraphViewer, self).Close()

    def _on_graph_log(self, log):
        node_id = log['info'].get('node_id', None)
        if node_id and node_id in self._nodes:
            self._nodes[node_id].on_log(log)

    def _construct_left_top_content(self):
        container = self._left_top_container
        eveui.EveLabelMedium(parent=container, align=eveui.Align.to_top, text=u'Instance ID: {}'.format(self._controller.node_graph.instance_id))
        eveui.Button(parent=container, align=eveui.Align.to_top, label='Go to Graph', func=lambda *args: self._controller.go_to_graph(), padTop=8)
        if self._controller.node_graph.is_active:
            eveui.Button(parent=container, align=eveui.Align.to_top, label='Stop', func=self._controller.stop_node_graph, padTop=8)
            eveui.Button(parent=container, align=eveui.Align.to_top, label='Stop active nodes', func=self._controller.stop_active_nodes, padTop=8)
        else:
            eveui.EveLabelLarge(parent=container, align=eveui.Align.to_top, padTop=10, text='This instance is INACTIVE', color=(1, 0, 0))

    def _construct_left_bot_content(self):
        container = self._left_bot_container
        self._graph_hierarchy = ActiveGraphHierarchy(parent=container, align=eveui.Align.to_top, controller=self._controller)
        self._blackboard_info = BlackboardInfo(parent=container, align=eveui.Align.to_top, padTop=12, node_graph_context=self._controller.node_graph.context)
        self._log_history = LogHistory(parent=container, align=eveui.Align.to_top, padTop=12, controller=self._controller)


class LogNodeGraphViewer(ActiveNodeGraphViewer):
    default_bgColor = (0, 0.2, 0, 0.1)
    node_graph_color = (0, 0.2, 0)
    controller_class = LogNodeGraphController

    def _construct_left_top_content(self):
        container = self._left_top_container
        eveui.EveLabelMedium(parent=container, align=eveui.Align.to_top, text=u'Instance ID: {}'.format(self._controller.node_graph.instance_id))
        eveui.Button(parent=container, align=eveui.Align.to_top, label='Go to Graph', func=lambda *args: self._controller.go_to_graph(), padTop=8)
        if self._controller.node_graph.is_active:
            eveui.Button(parent=container, align=eveui.Align.to_top, label='Stop', func=self._controller.stop_node_graph, padTop=8)
            eveui.Button(parent=container, align=eveui.Align.to_top, label='Stop active nodes', func=self._controller.stop_active_nodes, padTop=8)
        else:
            eveui.EveLabelLarge(parent=container, align=eveui.Align.to_top, padTop=10, text='This instance is INACTIVE', color=(1, 0, 0))

    def _construct_left_bot_content(self):
        container = self._left_bot_container
        self._graph_hierarchy = ActiveGraphHierarchy(parent=container, align=eveui.Align.to_top, controller=self._controller)
        self._blackboard_info = BlackboardInfo(parent=container, align=eveui.Align.to_top, padTop=12, node_graph_context=self._controller.node_graph.context, can_edit=False)
        self._log_history = LogHistory(parent=container, align=eveui.Align.to_top, padTop=12, controller=self._controller)


class AuthoredNodeGraphViewer(NodeGraphEditor):
    default_bgColor = (0, 0, 0.2, 0.1)
    node_graph_color = (0, 0, 0.2)
    controller_class = AuthoredNodeGraphController

    def Close(self):
        if self._active_instances:
            self._active_instances.close()
        if self._sub_graphs:
            self._sub_graphs.close()
        if self._hierarchy:
            self._hierarchy.close()
        super(AuthoredNodeGraphViewer, self).Close()

    def _construct_left_top_content(self):
        container = self._left_top_container
        label = 'Continue Customizing' if self._controller.has_custom_graph else 'Customize'
        eveui.Button(parent=container, align=eveui.Align.to_top, label=label, func=self._controller.customize_graph, padTop=8)
        eveui.Button(parent=container, align=eveui.Align.to_top, label='Start', func=self._controller.start_node_graph, padTop=8)
        eveui.Button(parent=container, align=eveui.Align.to_top, label='Reload from FSD', func=self._controller.reload_from_fsd, padTop=8)

    def _construct_left_bot_content(self):
        container = self._left_bot_container
        self._active_instances = ActiveInstances(parent=container, align=eveui.Align.to_top, controller=self._controller)
        self._sub_graphs = SubGraphs(parent=container, align=eveui.Align.to_top, controller=self._controller, padTop=12)
        self._hierarchy = AuthoredHierarchy(parent=container, align=eveui.Align.to_top, controller=self._controller, padTop=12)


class CustomNodeGraphViewer(NodeGraphEditor):
    default_bgColor = (0.2, 0, 0.2, 0.1)
    node_graph_color = (0.2, 0, 0.2)
    controller_class = CustomNodeGraphController

    def _layout(self):
        super(CustomNodeGraphViewer, self)._layout()
        self._controller.on_selected_connection_point.connect(self._on_selected_connection_point)

    def _on_selected_connection_point(self, connection_point):
        if connection_point:
            uthread2.start_tasklet(self._connection_line_thread)

    def _connection_line_thread(self):
        connection_line = NodeConnectionLine(parent=self._node_container, point_a=self._controller.selected_connection_point, point_b=utillib.KeyVal(get_position_for_line=self._get_mouse_position), color=self._controller.selected_connection_point.get_connection_color())
        while not self.destroyed and self._controller.selected_connection_point:
            connection_line.update_position()
            eveui.wait_for_next_frame()

        connection_line.Close()

    def _get_mouse_position(self):
        if self._controller.selected_connection_point:
            return (geo2.Vector(eveui.Mouse.position()) - geo2.Vector(self._node_container.GetAbsolutePosition())) / self._controller.zoom_level
        return (0, 0)

    def Close(self):
        if self._active_instances:
            self._active_instances.close()
        if self._sub_graphs:
            self._sub_graphs.close()
        super(CustomNodeGraphViewer, self).Close()

    def _construct_left_top_content(self):
        container = self._left_top_container
        authored_id = self._controller.get_authored_id()
        if authored_id:
            eveui.Button(parent=container, align=eveui.Align.to_top, label='Go to authored graph', func=lambda *args: self._controller.go_to_authored_graph(), padTop=8)
        eveui.Button(parent=container, align=eveui.Align.to_top, label='Start', func=self._controller.start_node_graph, padTop=8)
        eveui.Button(parent=container, align=eveui.Align.to_top, label='Copy to clipboard', func=lambda *args: self._controller.copy_graph_to_clipboard(), padTop=8)
        if authored_id:
            eveui.Button(parent=container, align=eveui.Align.to_top, label='Save to FSD', func=lambda *args: self._controller.save_to_fsd(), padTop=8)
        eveui.Button(parent=container, align=eveui.Align.to_top, label='Delete', func=self._controller.delete_graph, padTop=8)

    def _construct_left_bot_content(self):
        container = self._left_bot_container
        self._active_instances = ActiveInstances(parent=container, align=eveui.Align.to_top, controller=self._controller)
        self._sub_graphs = SubGraphs(parent=container, align=eveui.Align.to_top, controller=self._controller, padTop=12)

    def GetMenu(self):
        self._controller.clear_selected_connection_point()
        position = self._get_relative_position()
        result = [('Create node', lambda : self._drawer.create_node(position))]
        clipboard_data = GetClipboardData()
        if clipboard_data:
            result.append(None)
            result.append(('Paste nodes', lambda : self._controller.paste_from_clipboard(position, clipboard_data)))
        result.append(None)
        result.append(('Select all nodes', lambda : self._controller.select_all_nodes()))
        return result

    def OnClick(self, *args):
        super(CustomNodeGraphViewer, self).OnClick(*args)
        if self._controller.selected_connection_point and self._controller.selected_connection_point.connection_type == 'output' and not eveui.Key.menu.is_down:
            self._drawer.create_node(self._get_relative_position())
        else:
            self._controller.clear_selected_connection_point()

    def OnDblClick(self, *args):
        self._drawer.create_node(self._get_relative_position())

    def OnDropData(self, source, data):
        if data[0].type != 'move_node':
            return
        self._node_container.state = eveui.State.pick_children
        if self._controller.selected_nodes:
            self._controller.move_nodes(self._controller.selected_nodes, data[0].node_id, self._get_relative_position())
        else:
            self._controller.move_node(data[0].node_id, self._get_relative_position())

    def OnDragMove(self, source, data):
        if data[0].type != 'move_node':
            return
        old_pos = self._grid_highlight.GetPosition()
        new_pos = position_to_ui(*self._get_relative_position())
        self._grid_highlight.SetPosition(*new_pos)
        self._pan_container.Pan(*geo2.Subtract(old_pos, new_pos))

    def OnDragEnter(self, source, data):
        if data[0].type != 'move_node':
            return
        self._node_container.state = eveui.State.disabled
        self._grid_highlight.state = eveui.State.disabled
        self._grid_highlight.SetSize(*self._nodes[data[0].node_id].GetAbsoluteSize())
        self._grid_highlight.SetPosition(*position_to_ui(*self._get_relative_position()))

    def OnDragExit(self, source, data):
        if data[0].type != 'move_node':
            return
        self._node_container.state = eveui.State.pick_children
        self._grid_highlight.state = eveui.State.hidden


class NodeSearch(eveui.ContainerAutoSize):
    default_height = 26

    def __init__(self, controller, get_nodes, *args, **kwargs):
        super(NodeSearch, self).__init__(*args, **kwargs)
        self._controller = controller
        self._get_nodes = get_nodes
        self._index = -1
        self._available_nodes = []
        self._layout()
        self._update_buttons()

    @uthread2.debounce(wait=0.3)
    def _update(self):
        text = self._search_field.text.lower()
        self._available_nodes = []
        self._index = -1
        self._update_buttons()
        if text:
            for node_id, node_element in self._get_nodes().iteritems():
                if text in node_id.lower() or text in node_element.get_title().lower():
                    self._available_nodes.append(node_id)

        self._handle_next()

    def _on_text_changed(self, controller, text):
        self._update()

    def _handle_previous(self):
        if self._index > 0:
            self._index -= 1
            self._update_buttons()
            self._focus_node()

    def _handle_next(self):
        if self._index < len(self._available_nodes) - 1:
            self._index += 1
            self._update_buttons()
            self._focus_node()

    def _update_buttons(self):
        self._previous.enabled = self._index > 0
        self._next.enabled = self._index < len(self._available_nodes) - 1
        if len(self._available_nodes) > 0:
            self._info.text = '{}/{}'.format(self._index + 1, len(self._available_nodes))
        elif self._search_field.text:
            self._info.text = '0/0'
        else:
            self._info.text = ''

    @threadutils.threaded
    def _focus_node(self):
        node_id = self._available_nodes[self._index]
        self._controller.focus_node(node_id)
        self._controller.highlight_node(node_id)
        uthread2.sleep(1)
        if not self.destroyed:
            self._controller.unhighlight_node(node_id)

    def _layout(self):
        self._search_field = eveui.TextField(parent=self, align=eveui.Align.to_left, width=200, placeholder='Search for node...')
        self._search_field.controller.bind(text=self._on_text_changed)
        icon_container = eveui.Container(parent=self, align=eveui.Align.to_left, width=40, padLeft=8)
        self._previous = eveui.ButtonIcon(parent=icon_container, align=eveui.Align.center_left, texture_path='res:/UI/Texture/Shared/DarkStyle/backward.png', size=16, on_click=self._handle_previous)
        self._next = eveui.ButtonIcon(parent=icon_container, align=eveui.Align.center_right, texture_path='res:/UI/Texture/Shared/DarkStyle/forward.png', size=16, on_click=self._handle_next)
        self._info = eveui.EveLabelMedium(parent=self, align=eveui.Align.to_left, padTop=4, padLeft=8, width=100)


class PanContainerWithMarqueeSelection(PanContainer):
    default_name = 'PanContainerWithMarqueeSelection'

    def ApplyAttributes(self, attributes):
        self._is_marquee_selecting = False
        self.marqueeCont = None
        self.apply_selection_func = attributes.apply_selection_func
        super(PanContainerWithMarqueeSelection, self).ApplyAttributes(attributes)

    def OnMouseDown(self, *args):
        if not eveui.Key.shift.is_down:
            return super(PanContainerWithMarqueeSelection, self).OnMouseDown(*args)
        uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
        if eveui.Mouse.right.is_down:
            self.stop_marquee_selection()
        elif eveui.Mouse.left.is_down:
            self.start_marquee_selection()

    def OnMouseMove(self, *args):
        if self._is_marquee_selecting:
            return
        super(PanContainerWithMarqueeSelection, self).OnMouseMove(*args)

    def OnMouseUp(self, btnID):
        if self._is_marquee_selecting:
            self.apply_marquee_selection()
        self.stop_marquee_selection()

    def start_marquee_selection(self):
        self.stop_marquee_selection()
        self._is_marquee_selecting = True
        self.marqueeCont = MarqueeCont(parent=self.transform, parentScale=self.scale)

    def stop_marquee_selection(self):
        self._is_marquee_selecting = False
        if self.marqueeCont:
            self.marqueeCont.Close()
            self.marqueeCont = None
        uicore.uilib.UnclipCursor()

    def apply_marquee_selection(self):
        self.apply_selection_func(*self.marqueeCont.GetAbsolute())
