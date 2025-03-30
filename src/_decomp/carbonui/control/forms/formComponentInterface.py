#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\forms\formComponentInterface.py
from signals import Signal

class FormComponentInterface(object):
    name = None
    description = None
    hint = None
    is_visible = True
    indent_level = 0

    def __init__(self):
        self.on_value_set_by_user = Signal('on_value_changed')
        self.on_value_set = Signal('on_value_set')
        self.on_label_changed = Signal('on_label_changed')
        self.on_validated = Signal('on_validated')
        self.on_visibility_changed = Signal('on_visibility_changed')
        self.on_icon_changed = Signal('on_icon_changed')
        self.on_hint_changed = Signal('on_hint_changed')

    def get_name(self):
        raise NotImplementedError

    def get_label(self):
        raise NotImplementedError

    def is_valid(self):
        raise NotImplementedError

    def get_invalid_reason(self):
        raise NotImplementedError

    def get_invalid_reasons(self):
        raise NotImplementedError

    def get_form_data(self):
        raise NotImplementedError
