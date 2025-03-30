#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\parameter_field.py
import eveui
import log
from .union_type import get_union_type_class
import blue

class ParameterField(eveui.ContainerAutoSize):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_padTop = 12

    def __init__(self, parameter, value, on_change, can_edit = True, **kwargs):
        hint_list = []
        if parameter.description:
            hint_list.append(parameter.description)
        if parameter.defaultValue:
            hint_list.append('Default value: {}'.format(parameter.defaultValue))
        hint = '\n\n'.join(hint_list)
        kwargs['hint'] = hint
        super(ParameterField, self).__init__(**kwargs)
        self._on_change = on_change
        self._parameter = parameter
        eveui.EveLabelMedium(parent=self, align=eveui.Align.to_top, text='{} ({}) {}'.format(parameter.parameterKey, parameter.parameterType, required_text(parameter.isRequired)), padBottom=2)
        input_field_container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top, alignMode=eveui.Align.to_top)
        self.open_fsd_editor_button = None
        union_type_class = get_union_type_class(parameter.parameterType)
        if union_type_class and union_type_class.has_fsd_editor_url():
            self.open_fsd_editor_button = eveui.ButtonIcon(parent=input_field_container, align=eveui.Align.to_right, on_click=self._open_fsd_page, texture_path='res:/UI/Texture/classes/agency/iconExternalContent.png', size=26, padLeft=2)
            if not value:
                self.open_fsd_editor_button.state = eveui.State.hidden
        self._input_field = self.get_parameter_input_field(parameter.parameterType, value)
        self._input_field.align = eveui.Align.to_top
        self._input_field.SetParent(input_field_container)
        self._input_field.SetHint(hint=hint)
        if not can_edit:
            self._input_field.state = eveui.State.disabled

    def get_value(self):
        return self._input_field.__get_parameter_value__()

    def _handle_change(self, *args, **kwargs):
        value = self.get_value()
        self._on_change(self._parameter.parameterKey, value)
        if self.open_fsd_editor_button:
            if value:
                self.open_fsd_editor_button.state = eveui.State.normal
            else:
                self.open_fsd_editor_button.state = eveui.State.hidden

    def _open_fsd_page(self):
        union_type_class = get_union_type_class(self._parameter.parameterType)
        if union_type_class:
            union_type_class.open_fsd_editor_url(self.get_value())

    def get_parameter_input_field(self, param_type, value):
        union_type_class = get_union_type_class(param_type)
        if union_type_class:
            return union_type_class.get_input_field(value=value, handle_change=self._handle_change)
        log.LogError('Missing input field for union type ', param_type, '. Please add me.')
        render_type = 'objectType'
        if value is not None:
            if isinstance(value, int):
                render_type = 'integerType'
            elif isinstance(value, float):
                render_type = 'floatType'
            elif isinstance(value, bool):
                render_type = 'boolType'
            elif isinstance(value, str):
                render_type = 'stringType'
        return self.get_parameter_input_field(render_type, value)

    def GetMenu(self):
        parameterKey = self._parameter.parameterKey
        parameterType = self._parameter.parameterType
        value = self.get_value()
        m = [['Copy parameterKey: %s' % parameterKey, lambda *args: self._copy_value(parameterKey)], ['Copy parameterType: %s' % parameterType, lambda *args: self._copy_value(parameterType)], ['Copy value: %s' % value, lambda *args: self._copy_value(value)]]
        return m

    def _copy_value(self, copyValue, *args):
        return blue.pyos.SetClipboardData(unicode(copyValue))


def required_text(is_required):
    if is_required:
        return '(Required)'
    else:
        return ''
