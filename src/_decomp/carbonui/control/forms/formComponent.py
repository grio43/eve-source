#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\forms\formComponent.py
import signals
from carbonui.control.forms import formValidators
from carbonui.control.forms.form import FormComponentInterface

class _BaseComponent(FormComponentInterface):

    def __init__(self, name, label, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None):
        super(_BaseComponent, self).__init__()
        self.name = name
        self.label = label
        self.icon = icon
        self._value = value
        self.get_value_func = None
        self.validators = validators or []
        self.hint = hint
        self.field_cls = field_cls
        self.is_visible = is_visible
        self.indent_level = indent_level
        if form:
            form.add_component(self)

    def get_value(self):
        return self._value

    def init_value(self, value):
        self._value = value

    def set_value(self, value):
        self._value = value
        self.on_value_set(value)

    def get_id(self):
        return self.name

    def get_label(self):
        return self.label

    def set_label(self, value):
        self.label = value
        self.on_label_changed(self)

    def set_icon(self, value):
        self.icon = value
        self.on_icon_changed(self)

    def set_hint(self, value):
        self.hint = value
        self.on_hint_changed(self)

    def get_name(self):
        return self.name

    def get_invalid_reason(self):
        reasons = self.get_invalid_reasons()
        if not reasons:
            return
        reason = ', '.join(reasons)
        if self.label:
            reason = u'{}: {}'.format(self.label, reason)
        return reason

    def get_invalid_reasons(self):
        reasons = [ validator.get_invalid_reason(self.get_value()) for validator in self.validators ]
        return [ r for r in reasons if r ]

    def is_valid(self):
        is_valid = self.get_invalid_reason() is None
        self.on_validated(self, is_valid)
        return is_valid

    def on_field_value_changed(self, value):
        self._value = value
        self.on_value_set_by_user(self)

    def set_visible(self):
        if not self.is_visible:
            self.is_visible = True
            self.on_visibility_changed(self)

    def set_hidden(self):
        if self.is_visible:
            self.is_visible = False
            self.on_visibility_changed(self)


class Text(_BaseComponent):

    def __init__(self, name, label, value = None, placeholder = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = None, form = None):
        super(Text, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.placeholder = placeholder

    def get_max_characters(self):
        for validator in self.validators:
            if isinstance(validator, formValidators.Length):
                return validator.max_length


class Label(_BaseComponent):

    def __init__(self, name, label, hint = None):
        super(Label, self).__init__(name, label, hint=hint)


class TextMultiLine(_BaseComponent):

    def __init__(self, name, label, value = None, placeholder = None, num_lines = 4, show_formatting_panel = False, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = None, form = None):
        super(TextMultiLine, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.placeholder = placeholder
        self.num_lines = num_lines
        self.show_formatting_panel = show_formatting_panel

    def get_max_characters(self):
        for validator in self.validators:
            if isinstance(validator, formValidators.Length):
                return validator.max_length


class Integer(_BaseComponent):

    def __init__(self, name, label, value = None, min_value = 0, max_value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, placeholder = None, indent_level = None, form = None):
        super(Integer, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.min_value = min_value
        self.max_value = max_value
        self.placeholder = placeholder
        self._value = _clamp_with_none_checks(value, min_value, max_value)
        self.max_value_changed_signal = signals.Signal('component_max_value_changed')

    def max_values_changed(self, value):
        self.max_value = value
        self.max_value_changed_signal(self.max_value)


class Float(_BaseComponent):

    def __init__(self, name, label, value = 0.0, min_value = 0.0, max_value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = None, form = None):
        super(Float, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.min_value = min_value
        self.max_value = max_value
        self._value = _clamp_with_none_checks(value, min_value, max_value)


class Enum(_BaseComponent):

    def __init__(self, name, label, options, placeholder = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = None, form = None):
        super(Enum, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.placeholder = placeholder
        self.options = options


class Boolean(_BaseComponent):
    pass


class EveType(_BaseComponent):

    def __init__(self, name, label, placeholder = None, type_filter = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None):
        super(EveType, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.placeholder = placeholder
        self.type_filter = type_filter


class EveGroup(_BaseComponent):

    def __init__(self, name, label, placeholder = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None):
        super(EveGroup, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.placeholder = placeholder


class EveCategory(_BaseComponent):

    def __init__(self, name, label, placeholder = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None):
        super(EveCategory, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.placeholder = placeholder


class SolarSystem(_BaseComponent):

    def __init__(self, name, label, placeholder = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None):
        super(SolarSystem, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.placeholder = placeholder


class NPCFaction(_BaseComponent):

    def __init__(self, name, label, placeholder = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None):
        super(NPCFaction, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.placeholder = placeholder


class PlayerCorporation(_BaseComponent):

    def __init__(self, name, label, placeholder = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None):
        super(PlayerCorporation, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.placeholder = placeholder


class NPCCorporation(_BaseComponent):

    def __init__(self, name, label, filter = None, placeholder = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0):
        super(NPCCorporation, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level)
        self.placeholder = placeholder
        self.filter = filter


class Organization(_BaseComponent):

    def __init__(self, name, label, placeholder = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None):
        super(Organization, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.placeholder = placeholder


class PlayerOrPlayerOrganization(_BaseComponent):

    def __init__(self, name, label, placeholder = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None):
        super(PlayerOrPlayerOrganization, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.placeholder = placeholder


class DateTime(_BaseComponent):

    def __init__(self, name, label = None, value = None, duration_datetime = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None, time_options = None, year_range = None, timeparts = 4, time_padding = 0):
        super(DateTime, self).__init__(name, label, value, validators, hint, field_cls, is_visible, icon, indent_level, form)
        self.time_options = time_options
        self.year_range = year_range
        self.timeparts = timeparts
        self.time_padding = time_padding
        self.duration_datetime = duration_datetime


class Divider(_BaseComponent):

    def __init__(self, name):
        super(Divider, self).__init__(name, label='')


def _clamp_with_none_checks(value, min_value, max_value):
    if value is None:
        return value
    if min_value is not None:
        value = max(min_value, value)
    if max_value is not None:
        value = min(max_value, value)
    return value
