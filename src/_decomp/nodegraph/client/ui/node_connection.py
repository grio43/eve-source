#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\node_connection.py
import eveui
import uthread2
import geo2
from .util import get_connection_color, get_connection_name
from .union_type import get_union_type_name

class NodeConnectionLine(eveui.VectorLine):

    def __init__(self, point_a, point_b, color = (1, 1, 1), *args, **kwargs):
        self.point_a = point_a
        self.point_b = point_b
        kwargs['colorFrom'] = color
        kwargs['colorTo'] = color
        super(NodeConnectionLine, self).__init__(*args, **kwargs)
        self.update_position()

    def update_position(self):
        self.translationFrom = self.point_a.get_position_for_line()
        self.translationTo = self.point_b.get_position_for_line()


class ConnectionPoint(eveui.Container):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_height = 20
    default_padBottom = 2
    default_padTop = 2

    def __init__(self, node_id = None, node_object = None, connection_id = None, controller = None, child_align = None, connection_type = None, **kwargs):
        super(ConnectionPoint, self).__init__(**kwargs)
        self.node_id = node_id
        self.node_object = node_object
        self.connection_id = connection_id
        self.connection_type = connection_type
        self._controller = controller
        self.connection_lines = []
        fill_container = eveui.Container(parent=self, align=child_align, width=14)
        self.fill = eveui.Fill(parent=fill_container, align=eveui.Align.center, height=14, width=14, name=connection_id, color=self.get_connection_color())
        self.label = eveui.EveLabelMedium(parent=self, align=child_align, text=get_connection_name(connection_id), padLeft=6, padRight=6)
        if not self._controller.can_edit:
            self.state = eveui.State.disabled

    def get_position_for_line(self):
        point_size = self.fill.GetCurrentAbsoluteSize()
        offset = [point_size[0], point_size[1] * 0.5]
        if self.label.align == eveui.Align.to_left:
            offset[0] = 0
        return (geo2.Vector(self.fill.GetCurrentAbsolutePosition()) - geo2.Vector(self.node_object.parent.GetCurrentAbsolutePosition())) / self._controller.zoom_level + geo2.Vector(offset)

    def get_connection_color(self):
        return get_connection_color(self.connection_id)

    def add_connection_line(self, connection_line):
        self.connection_lines.append(connection_line)

    def highlight_ping(self):
        eveui.animate(self.label, 'color', start_value=self.fill.color.GetRGB(), end_value=(1, 1, 1, 0.6), duration=1)

    @property
    def is_selected_point(self):
        if hasattr(self._controller, 'selected_connection_point'):
            return self._controller.selected_connection_point == self
        return False

    def OnClick(self, *args):
        if eveui.Key.control.is_down or eveui.Key.shift.is_down:
            self.node_object.OnClick(*args)
        elif eveui.Key.menu.is_down:
            self._controller.clear_selected_connection_point()
            self._controller.remove_all_connection_lines(self.connection_lines)
        else:
            self._controller.node_connection_clicked(self)

    def _remove_all_connections(self):
        self._controller.remove_all_connection_lines(self.connection_lines)

    def GetMenu(self, *args):
        if not self._controller.can_edit or not self.connection_lines:
            return
        result = []
        for connection_line in self.connection_lines:
            connecion_point = connection_line.point_a if connection_line.point_b == self else connection_line.point_b

            def remove_conn(line):

                def func():
                    self._controller.remove_connection_line(line)

                return func

            func = remove_conn(connection_line)
            result.append(('{} - {} - id:{}'.format(self._controller.get_node_class_title(connecion_point.node_id), connecion_point.connection_id, connecion_point.node_id), func))

        data = [('Remove connection: {}'.format(self.connection_id), None)]
        if len(result) > 1:
            data.append(('All', self._remove_all_connections))
        data.extend(result)
        return data

    def OnMouseEnter(self, *args):
        if eveui.Key.control.is_down or eveui.Key.shift.is_down:
            return
        eveui.fade(self, end_value=2, duration=0.1)

    def OnMouseExit(self, *args):
        eveui.fade(self, end_value=1, duration=0.2)


class VariableConnectionPoint(ConnectionPoint):

    def __init__(self, parameter = None, *args, **kwargs):
        super(VariableConnectionPoint, self).__init__(*args, **kwargs)
        self.parameter = parameter
        self._node_hovered = False
        uthread2.start_tasklet(self.update_state)

    def get_connection_color(self):
        return get_connection_color('variables')

    def add_connection_line(self, connection_line):
        super(VariableConnectionPoint, self).add_connection_line(connection_line)
        self.update_state()

    def node_hover_enter(self):
        self._node_hovered = True
        self.update_state()

    def node_hover_exit(self):
        self._node_hovered = False
        self.update_state()

    def update_state(self):
        if self.connection_lines or self.is_selected_point or self._node_hovered:
            self.state = eveui.State.normal
        else:
            self.state = eveui.State.hidden


class OutputVariableConnectionPoint(VariableConnectionPoint):

    def __init__(self, *args, **kwargs):
        kwargs['connection_type'] = 'output_variable'
        super(OutputVariableConnectionPoint, self).__init__(*args, **kwargs)

    def GetHint(self):
        hint_list = []
        hint_list.append('<color=#FFFFFFED>{}</color> ({})'.format(self.parameter.parameterKey, self.parameter.parameterType))
        if self.parameter.description:
            hint_list.append(self.parameter.description)
        hint = '\n\n'.join(hint_list)
        return hint


class InputVariableConnectionPoint(VariableConnectionPoint):

    def __init__(self, *args, **kwargs):
        kwargs['connection_type'] = 'input_variable'
        super(InputVariableConnectionPoint, self).__init__(*args, **kwargs)

    def GetHint(self):
        parameter_key = self.parameter.parameterKey
        hint_list = []
        if self.connection_lines:
            connection_point = self.connection_lines[0].point_a
            from_node_id = connection_point.node_id
            from_connection_id = connection_point.connection_id
            value_name = '{}.{}'.format(self._controller.get_node_class_title(from_node_id), from_connection_id)
        else:
            node_data = self._controller.nodes_data[self.node_id]
            is_default = False
            if parameter_key in node_data.nodeParameters:
                value = node_data.nodeParameters[parameter_key].value
            elif parameter_key in (getattr(node_data, 'atomParameters', {}) or {}):
                value = node_data.atomParameters[parameter_key].value
            else:
                is_default = True
                value = self.parameter.defaultValue
            value_name = get_union_type_name(self.parameter.parameterType, value)
            if is_default:
                value_name = '{} (default)'.format(value_name)
        hint_list.append('<color=#FFFFFFED>{} = {}</color>'.format(parameter_key, value_name))
        hint_list.append('{} ({})'.format('Required' if self.parameter.isRequired else 'Optional', self.parameter.parameterType))
        if self.parameter.description:
            hint_list.append('')
            hint_list.append(self.parameter.description)
        hint = '\n'.join(hint_list)
        return hint
