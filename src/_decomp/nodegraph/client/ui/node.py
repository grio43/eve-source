#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\node.py
from __future__ import absolute_import
from logging import getLogger
import eveui
import uthread2
import utillib
from nodegraph.common.nodedata import get_node_type, InPort
from .util import get_connection_color
from .node_connection import ConnectionPoint, InputVariableConnectionPoint, OutputVariableConnectionPoint
logger = getLogger(__name__)

class BaseNode(eveui.ContainerAutoSize):
    default_state = eveui.State.normal
    default_align = eveui.Align.top_left
    default_alignMode = eveui.Align.to_top
    default_width = 225

    def __init__(self, graph_controller, node_controller, edit_node, **kwargs):
        super(BaseNode, self).__init__(callback=self._update_connection_lines, **kwargs)
        self._graph_controller = graph_controller
        self._node_controller = node_controller
        self._edit_node = edit_node
        self._node_id = self._node_controller.node_id
        self._node_data = self._node_controller.node_data
        self._connection_points = {'input': {},
         'output': {},
         'input_variables': {},
         'output_variables': {}}
        self._connection_lines = set()
        self._graph_controller.on_selected_nodes.connect(self._on_selection_changed)
        self._layout()

    def Close(self):
        super(BaseNode, self).Close()
        self._node_controller.on_selection_changed.disconnect(self._on_selection_changed)

    def _on_selection_changed(self, *args, **kwargs):
        self._selection_highlight.opacity = 1 if self._node_controller.is_selected else 0

    def get_connection_point_object(self, connection_type, connection_id):
        return self._connection_points[connection_type][connection_id]

    def add_connection_line(self, connection_line):
        self._connection_lines.add(connection_line)

    def toggle_highlight(self, on):
        if on:
            self._bg.color = (0.3, 0.3, 0.3)
        else:
            self._bg.color = (0, 0, 0)

    def OnClick(self, *args):
        if eveui.Key.control.is_down:
            self._graph_controller.toggle_selection(self._node_id)
        elif eveui.Key.shift.is_down:
            self._graph_controller.add_to_selection(self._node_id)
        else:
            self._graph_controller.clear_selection()
            self._edit_node(self._node_id)

    def GetMenu(self, *args):
        return self._node_controller.get_context_menu()

    def GetHint(self):
        comment = self._node_controller.comment
        if comment:
            return u'Comment:\n{}'.format(comment)

    def OnMouseEnter(self, *args):
        self.SetOrder(0)
        eveui.fade(self._bg, end_value=1, duration=0.1)
        self._show_variables()

    def OnMouseExit(self, *args):
        eveui.fade(self._bg, end_value=0.5, duration=0.2)
        self._hide_variables()

    def _show_variables(self):
        if eveui.Key.control.is_down or eveui.Key.shift.is_down:
            return
        for variable_connection_point in self._connection_points['input_variables'].itervalues():
            variable_connection_point.node_hover_enter()

        for variable_connection_point in self._connection_points['output_variables'].itervalues():
            variable_connection_point.node_hover_enter()

        self._update_connections_height()

    def _hide_variables(self):
        for variable_connection_point in self._connection_points['input_variables'].itervalues():
            variable_connection_point.node_hover_exit()

        for variable_connection_point in self._connection_points['output_variables'].itervalues():
            variable_connection_point.node_hover_exit()

        self._update_connections_height()

    def _update_connection_lines(self):
        for connection_line in self._connection_lines:
            connection_line.update_position()

    def _layout(self):
        self._frame = eveui.Frame(bgParent=self, color=(0, 1, 0), opacity=0)
        self._selection_highlight = eveui.Frame(bgParent=self, color=(1, 1, 1), padding=-2, opacity=0)
        self._bg = eveui.Fill(bgParent=self, color=(0, 0, 0), opacity=0.5)
        self._construct_icons()
        self._construct_header()
        eveui.Line(parent=self, padBottom=2)
        self._construct_connection_points()

    def _construct_header(self):
        container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top, padding=6)
        eveui.Container(parent=container, align=eveui.Align.to_top, height=1)
        self._title = eveui.EveLabelMedium(parent=container, align=eveui.Align.to_top, text=self._node_controller.title, maxLines=1)
        eveui.EveLabelMedium(parent=container, align=eveui.Align.to_top, text=self._node_controller.subtitle or ' ', maxLines=1)
        eveui.GradientSprite(bgParent=container, rgbData=((1.0, self._node_controller.color),), alphaData=((0.0, 0.75), (1.0, 0.25)), padding=-6)

    def _construct_icons(self):
        container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.top_right, top=-14, height=24)
        eveui.EveLabelSmall(parent=container, align=eveui.Align.to_right, text=u'{}...'.format(self._node_id[:3]), padding=1, bgColor=(0, 0, 0, 0.7))
        if self._node_controller.comment:
            eveui.Sprite(parent=container, align=eveui.Align.to_right, width=24, texturePath='res:/UI/Texture/WindowIcons/chatchannel.png', color=(1, 1, 1, 1))
        if self._node_controller.get_parameter_value('delay'):
            eveui.Sprite(parent=container, align=eveui.Align.to_right, width=24, texturePath='res:/UI/Texture/WindowIcons/trainingqueue.png', color=(1, 1, 1, 1))

    def _construct_connection_points(self):
        self._connection_points_container = container = eveui.Container(parent=self, align=eveui.Align.to_top, padBottom=2)
        right = eveui.Container(parent=container, align=eveui.Align.to_right_prop, width=0.5)
        for connection_id in self._node_controller.output_ports:
            point = ConnectionPoint(parent=right, node_id=self._node_id, node_object=self, connection_id=connection_id, connection_type='output', controller=self._graph_controller, child_align=eveui.Align.to_right)
            self._connection_points['output'][connection_id] = point

        for parameter in self._node_controller.output_parameters:
            parameter_key = parameter.parameterKey
            point = OutputVariableConnectionPoint(parent=right, node_id=self._node_id, node_object=self, connection_id=parameter_key, parameter=parameter, controller=self._graph_controller, child_align=eveui.Align.to_right)
            self._connection_points['output_variables'][parameter_key] = point

        self._left_connections_container = left = eveui.ContainerAutoSize(parent=container, align=eveui.Align.to_all)
        for connection_id in self._node_controller.input_ports:
            point = ConnectionPoint(parent=left, node_id=self._node_id, node_object=self, connection_id=connection_id, connection_type='input', controller=self._graph_controller, child_align=eveui.Align.to_left)
            self._connection_points['input'][connection_id] = point

        for parameter in self._node_controller.input_parameters:
            if parameter.parameterKey == 'atom_id':
                continue
            point = InputVariableConnectionPoint(parent=left, node_id=self._node_id, node_object=self, connection_id=parameter.parameterKey, parameter=parameter, controller=self._graph_controller, child_align=eveui.Align.to_left)
            self._connection_points['input_variables'][parameter.parameterKey] = point

        uthread2.start_tasklet(self._update_connections_height)

    def _update_connections_height(self):
        visible_left = 0
        visible_right = 0
        connection_points = self._connection_points_container.children
        left_children = connection_points[0].children if len(connection_points) > 0 else []
        right_children = connection_points[1].children if len(connection_points) > 1 else []
        for child in left_children:
            if not child.IsHidden():
                visible_left += 1

        for child in right_children:
            if not child.IsHidden():
                visible_right += 1

        self._connection_points_container.height = max(visible_left, visible_right) * 24


class AuthoredNode(BaseNode):

    def OnClick(self, *args):
        if self._graph_controller.selected_connection_point:
            if self._graph_controller.selected_connection_point.connection_type == 'output' and InPort.input in self._node_controller.input_parameters:
                self._graph_controller.add_node_connection(self._graph_controller.selected_connection_point.node_id, self._node_id, self._graph_controller.selected_connection_point.connection_id)
            self._graph_controller.clear_selected_connection_point()
            return
        super(AuthoredNode, self).OnClick(*args)

    def PrepareDrag(self, dragContainer, dragSource):
        container = eveui.ContainerAutoSize(parent=dragContainer, bgColor=(1, 0, 1, 0.2))
        text_lines = ['Move Node']
        for node in dragContainer.dragData:
            t = '{} - id:{}'.format(self._node_controller.title, node.node_id)
            text_lines.append(t)

        text = '\n'.join(text_lines)
        eveui.EveLabelLarge(parent=container, text=text, padding=4)
        self.Disable()
        return (0, 0)

    def GetDragData(self):
        ret = [utillib.KeyVal(type='move_node', node_id=self._node_id)]
        selected_nodes = self._graph_controller.selected_nodes
        for node_id in selected_nodes:
            ret.append(utillib.KeyVal(type='move_node', node_id=node_id))

        if self._graph_controller.selected_nodes and self._node_id not in self._graph_controller.selected_nodes:
            self._graph_controller.add_to_selection(self._node_id)
        return ret

    def OnEndDrag(self, *args):
        self.Enable()


class Node(eveui.ContainerAutoSize):
    default_state = eveui.State.normal
    default_align = eveui.Align.top_left
    default_alignMode = eveui.Align.to_top
    default_width = 225
    isDragObject = True

    def __init__(self, node_id, node_data, on_click, controller, **kwargs):
        super(Node, self).__init__(callback=self._update_connection_lines, **kwargs)
        self._node_id = node_id
        self._node_data = node_data
        self._connection_points = {'input': {},
         'output': {},
         'input_variables': {},
         'output_variables': {}}
        self._connection_lines = set()
        self._on_click = on_click
        self._controller = controller
        self._controller.on_selected_nodes.connect(self._on_selected_nodes)
        try:
            self._input_parameters = self._controller.get_node_input_parameters(self._node_id)
            self._layout()
        except Exception as exc:
            logger.exception('Failed to represent node %s: %s', node_id or '-', exc)
            raise exc

    def Close(self):
        super(Node, self).Close()
        self._controller.on_selected_nodes.disconnect(self._on_selected_nodes)

    def _on_selected_nodes(self, selected_nodes):
        if self._node_id in selected_nodes:
            self._selection_highlight.opacity = 1
        else:
            self._selection_highlight.opacity = 0

    def get_title(self):
        return self._title.text

    def get_connection_point_object(self, connection_type, connection_id):
        return self._connection_points[connection_type][connection_id]

    def add_connection_line(self, connection_line):
        self._connection_lines.add(connection_line)

    def set_active(self):
        self._frame.color = (0, 1, 0)
        eveui.fade(self._frame, start_value=0, end_value=1, duration=0.2)

    def toggle_highlight(self, on):
        if on:
            self._bg.color = (0.3, 0.3, 0.3)
        else:
            self._bg.color = (0, 0, 0)

    def on_log(self, log):
        if log['node_graph_id'] != self._controller.node_graph_id:
            return
        start_value = None
        if self._node_id in self._controller.node_graph.active_node_ids:
            end_value = (0, 1, 0, 1)
        else:
            end_value = (1, 1, 1, 0)
        if log['event'] == 'started':
            start_value = (0, 1, 0, 1)
        elif log['event'] == 'connection_started':
            connection_id = log['info']['connection']
            self._connection_points['output'][connection_id].highlight_ping()
            start_value = get_connection_color(connection_id)
        eveui.animate(self._frame, 'color', start_value=start_value, end_value=end_value, duration=1)

    def OnClick(self, *args):
        if self._controller.can_edit and self._controller.selected_connection_point:
            if self._controller.selected_connection_point.connection_type == 'output' and InPort.input in self._connection_points['input']:
                self._controller.add_node_connection(self._controller.selected_connection_point.node_id, self._node_id, self._controller.selected_connection_point.connection_id)
            self._controller.clear_selected_connection_point()
            return
        if eveui.Key.control.is_down:
            self._controller.toggle_selection(self._node_id)
        elif eveui.Key.shift.is_down:
            self._controller.add_to_selection(self._node_id)
        else:
            self._on_click(self._node_id)
            self._controller.clear_selection()

    def GetMenu(self, *args):
        return self._controller.get_node_context_menu(self._node_id)

    def GetHint(self):
        if self._node_data.comment:
            return u'Comment:\n{}'.format(self._node_data.comment)

    def OnMouseEnter(self, *args):
        self.SetOrder(0)
        eveui.fade(self._bg, end_value=1, duration=0.1)
        self._show_variables()

    def OnMouseExit(self, *args):
        eveui.fade(self._bg, end_value=0.5, duration=0.2)
        self._hide_variables()

    def _show_variables(self):
        if eveui.Key.control.is_down or eveui.Key.shift.is_down:
            return
        for variable_connection_point in self._connection_points['input_variables'].itervalues():
            variable_connection_point.node_hover_enter()

        for variable_connection_point in self._connection_points['output_variables'].itervalues():
            variable_connection_point.node_hover_enter()

        self._update_connections_height()

    def _hide_variables(self):
        for variable_connection_point in self._connection_points['input_variables'].itervalues():
            variable_connection_point.node_hover_exit()

        for variable_connection_point in self._connection_points['output_variables'].itervalues():
            variable_connection_point.node_hover_exit()

        self._update_connections_height()

    def _update_connection_lines(self):
        for connection_line in self._connection_lines:
            connection_line.update_position()

    def _layout(self):
        self._frame = eveui.Frame(bgParent=self, color=(0, 1, 0), opacity=0)
        self._selection_highlight = eveui.Frame(bgParent=self, color=(1, 1, 1), padding=-2, opacity=0)
        self._bg = eveui.Fill(bgParent=self, color=(0, 0, 0), opacity=0.5)
        self._construct_icons()
        self._construct_header()
        eveui.Line(parent=self, padBottom=2)
        self._construct_connection_points()

    def _construct_header(self):
        container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top, padding=6)
        eveui.Container(parent=container, align=eveui.Align.to_top, height=1)
        self._title = eveui.EveLabelMedium(parent=container, align=eveui.Align.to_top, text=self._controller.get_node_class_title(self._node_id), maxLines=1)
        eveui.EveLabelMedium(parent=container, align=eveui.Align.to_top, text=self._controller.get_node_class_subtitle(self._node_id) or ' ', maxLines=1)
        eveui.GradientSprite(bgParent=container, rgbData=((1.0, self._controller.get_node_color(self._node_id)),), alphaData=((0.0, 0.75), (1.0, 0.25)), padding=-6)

    def _construct_icons(self):
        container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.top_right, top=-14, height=24)
        eveui.EveLabelSmall(parent=container, align=eveui.Align.to_right, text=u'{}...'.format(self._node_id[:3]), padding=1, bgColor=(0, 0, 0, 0.7))
        if self._node_data.comment:
            eveui.Sprite(parent=container, align=eveui.Align.to_right, width=24, texturePath='res:/UI/Texture/WindowIcons/chatchannel.png', color=(1, 1, 1, 1))
        delay = self._node_data.nodeParameters.get('delay', None)
        if delay and delay.value:
            eveui.Sprite(parent=container, align=eveui.Align.to_right, width=24, texturePath='res:/UI/Texture/WindowIcons/trainingqueue.png', color=(1, 1, 1, 1))

    def _construct_connection_points(self):
        node_type = get_node_type(self._node_data.nodeType)
        input_ports = node_type.ports.inPorts
        output_ports = node_type.ports.outPorts
        self._connection_points_container = container = eveui.Container(parent=self, align=eveui.Align.to_top, padBottom=2)
        right = eveui.Container(parent=container, align=eveui.Align.to_right_prop, width=0.5)
        for connection_id in output_ports:
            point = ConnectionPoint(parent=right, node_id=self._node_id, node_object=self, connection_id=connection_id, connection_type='output', controller=self._controller, child_align=eveui.Align.to_right)
            self._connection_points['output'][connection_id] = point

        for parameter in self._controller.get_node_output_parameters(self._node_id):
            parameter_key = parameter.parameterKey
            point = OutputVariableConnectionPoint(parent=right, node_id=self._node_id, node_object=self, connection_id=parameter_key, parameter=parameter, controller=self._controller, child_align=eveui.Align.to_right)
            self._connection_points['output_variables'][parameter_key] = point

        self._left_connections_container = left = eveui.ContainerAutoSize(parent=container, align=eveui.Align.to_all)
        for connection_id in input_ports:
            point = ConnectionPoint(parent=left, node_id=self._node_id, node_object=self, connection_id=connection_id, connection_type='input', controller=self._controller, child_align=eveui.Align.to_left)
            self._connection_points['input'][connection_id] = point

        for parameter in self._input_parameters:
            point = InputVariableConnectionPoint(parent=left, node_id=self._node_id, node_object=self, connection_id=parameter.parameterKey, parameter=parameter, controller=self._controller, child_align=eveui.Align.to_left)
            self._connection_points['input_variables'][parameter.parameterKey] = point

        uthread2.start_tasklet(self._update_connections_height)

    def _update_connections_height(self):
        visible_left = 0
        visible_right = 0
        connection_points = self._connection_points_container.children
        left_children = connection_points[0].children if len(connection_points) > 0 else []
        right_children = connection_points[1].children if len(connection_points) > 1 else []
        for child in left_children:
            if not child.IsHidden():
                visible_left += 1

        for child in right_children:
            if not child.IsHidden():
                visible_right += 1

        self._connection_points_container.height = max(visible_left, visible_right) * 24

    def PrepareDrag(self, dragContainer, dragSource):
        container = eveui.ContainerAutoSize(parent=dragContainer, bgColor=(1, 0, 1, 0.2))
        text_lines = ['Move Node']
        for node in dragContainer.dragData:
            t = '{} - id:{}'.format(self._controller.get_node_class_title(node.node_id), node.node_id)
            text_lines.append(t)

        text = '\n'.join(text_lines)
        eveui.EveLabelLarge(parent=container, text=text, padding=4)
        self.Disable()
        return (0, 0)

    def GetDragData(self):
        if self._controller.can_edit:
            ret = [utillib.KeyVal(type='move_node', node_id=self._node_id)]
            selected_nodes = self._controller.selected_nodes
            for node_id in selected_nodes:
                ret.append(utillib.KeyVal(type='move_node', node_id=node_id))

            if self._controller.selected_nodes and self._node_id not in self._controller.selected_nodes:
                self._controller.add_to_selection(self._node_id)
            return ret

    def OnEndDrag(self, *args):
        self.Enable()
