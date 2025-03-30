#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\forms\form.py
from carbonui.control.forms.formComponentInterface import FormComponentInterface
from carbonui.control.forms.formsUtil import FormatAsIncompleteInput
from localization import GetByLabel
from signals import Signal

class BaseFormAction(object):

    def __init__(self, label, func = None, hint = None):
        self.label = label
        self.func = func
        self.hint = hint

    def execute(self, form):
        raise NotImplementedError


class FormActionSubmit(BaseFormAction):

    def execute(self, form):
        if form.is_valid():
            self.func(form)
            form.on_submitted(self)
        else:
            form.on_submit_failed(self)


class FormActionCancel(BaseFormAction):

    def __init__(self, label = GetByLabel('UI/Common/Buttons/Cancel'), func = None, hint = None):
        super(FormActionCancel, self).__init__(label, func, hint)

    def execute(self, form):
        if self.func:
            self.func(form)
        form.on_canceled(self)


class Form(FormComponentInterface):

    def __init__(self, components = None, actions = None, name = None, label = None, description = None, icon = None, hint = None, field_cls = None, cancel_dialog = None):
        super(Form, self).__init__()
        self.components = components or []
        self.actions = actions or []
        self.name = name
        self.label = label
        self.description = description
        self.icon = icon
        self.hint = hint
        self.field_cls = field_cls
        self.cancel_dialog = cancel_dialog
        self.on_submitted = Signal('on_submitted')
        self.on_submit_failed = Signal('on_submit_failed')
        self.on_canceled = Signal('on_canceled')
        self.on_components_changed = Signal('on_components_changed')
        for component in self.get_components():
            component.on_value_set_by_user.connect(self.on_value_set_by_user)

    def get_label(self):
        return self.label

    def set_label(self, value):
        self.label = value
        self.on_label_changed(self)

    def get_name(self):
        return self.name

    def get_form_data(self):
        return {c.name:c.get_value() for c in self.get_components()}

    def get_components(self):
        return self.components

    def set_components(self, components):
        self.components = components
        self.on_components_changed()

    def add_component(self, component):
        self.components.append(component)
        self.on_components_changed()

    def get_component(self, name):
        for component in self.get_components():
            if component.name == name:
                return component
            if isinstance(component, Form):
                c = component.get_component(name)
                if c:
                    return c

    def has_component(self, name):
        for component in self.get_components():
            if component.name == name:
                return True
            if isinstance(component, Form):
                c = component.get_component(name)
                if c:
                    return True

        return False

    def get_value(self):
        return self.get_form_data()

    def set_value(self, value):
        pass

    def init_value(self, value):
        pass

    def is_valid(self):
        is_valid = all([ c.is_valid() for c in self.get_components() ])
        self.on_validated(self, is_valid)
        return is_valid

    def get_invalid_reasons(self):
        return [ c.get_invalid_reason() for c in self.get_components() if not c.is_valid() ]

    def get_invalid_reasons_text(self):
        return '\n'.join(self.get_invalid_reasons())

    def get_submit_failed_reasons_text(self):
        reasons = [ FormatAsIncompleteInput(reason) for reason in self.get_invalid_reasons() ]
        return '\n'.join(reasons)

    def get_invalid_reason(self):
        return '\n'.join(self.get_invalid_reasons())
