#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_goals\forms\goalFormComponents.py
import signals
from carbonui.control.forms import formComponent
from eve.client.script.ui.shared.neocom.corporation.corp_goals.forms.goalFormFields import MultiValueLocationFormField, MultiValueItemFormField, MultiValuePlayerCorpOrOrgFormField, MultiValueShipAndShipTreeFormField, MultiValueEnum, MultiValueNPCCorpFormField, MaxRewardPerContributorField, ParticipationLimitField

class MultiValueFormComponentBase(formComponent._BaseComponent):
    field_cls = None

    def __init__(self, name, label, placeholder = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None, max_entries = 1):
        super(MultiValueFormComponentBase, self).__init__(name, label, value, validators, hint, self.field_cls if field_cls is None else field_cls, is_visible, icon, indent_level, form)
        self.max_entries = max_entries
        self.placeholder = placeholder


class MultiValueLocationFormComponent(MultiValueFormComponentBase):
    field_cls = MultiValueLocationFormField


class MultiValueItemFormComponent(MultiValueFormComponentBase):
    field_cls = MultiValueItemFormField

    def __init__(self, name, label, placeholder = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None, max_entries = 1, type_filter = None, group_filter = None, category_filter = None, include_type = True, include_group = True, include_category = True):
        super(MultiValueItemFormComponent, self).__init__(name, label, placeholder, value, validators, hint, self.field_cls if field_cls is None else field_cls, is_visible, icon, indent_level, form, max_entries)
        self.type_filter = type_filter
        self.group_filter = group_filter
        self.category_filter = category_filter
        self.include_type = include_type
        self.include_group = include_group
        self.include_category = include_category


class MultiValueNpcCorpFormComponent(MultiValueFormComponentBase):
    field_cls = MultiValueNPCCorpFormField

    def __init__(self, name, label, placeholder = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None, max_entries = 1, filter = None):
        super(MultiValueNpcCorpFormComponent, self).__init__(name, label, placeholder, value, validators, hint, self.field_cls if field_cls is None else field_cls, is_visible, icon, indent_level, form, max_entries)
        self.filter = filter


class MultiValuePlayerCorpOrOrgFormComponent(MultiValueFormComponentBase):
    field_cls = MultiValuePlayerCorpOrOrgFormField


class MultiValueShipAndShipTreeFormComponent(MultiValueFormComponentBase):
    field_cls = MultiValueShipAndShipTreeFormField


class MultiValueEnumComponent(MultiValueFormComponentBase):
    field_cls = MultiValueEnum

    def __init__(self, name, label, placeholder = None, value = None, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, indent_level = 0, form = None, max_entries = 1, options = None):
        super(MultiValueEnumComponent, self).__init__(name, label, placeholder, value, validators, hint, self.field_cls if field_cls is None else field_cls, is_visible, icon, indent_level, form, max_entries)
        self.options = options


class ParticipationLimitComponent(formComponent.Integer):
    field_cls = ParticipationLimitField

    def __init__(self, name, label, is_included = False, value = None, min_value = 0, max_value = 1, validators = None, hint = None, field_cls = None, is_visible = True, icon = None, placeholder = None, indent_level = 0, form = None):
        super(ParticipationLimitComponent, self).__init__(name, label, value, min_value, max_value, validators, hint, self.field_cls if field_cls is None else field_cls, is_visible, icon, placeholder, indent_level, form)


class MaxRewardPerContributorComponent(formComponent._BaseComponent):
    field_cls = MaxRewardPerContributorField

    def __init__(self, name, label = None, hint = None, is_visible = False, indent_level = 0, limit = 0, reward = 0, field_cls = None, form = None):
        self._limit = limit
        self._reward = reward
        super(MaxRewardPerContributorComponent, self).__init__(name=name, label=label, hint=hint, is_visible=is_visible, indent_level=indent_level, field_cls=self.field_cls if field_cls is None else field_cls, form=form)
        self.on_limit_changed_signal = signals.Signal('max_reward_limit_changed')
        self.on_reward_changed_signal = signals.Signal('max_reward_reward_changed')

    def set_is_included(self, component):
        value = component.get_value()
        if value:
            self.set_visible()
        else:
            self.set_hidden()

    def get_limit(self):
        return self._limit

    def get_reward(self):
        return self._reward

    def limit_changed(self, component):
        self._limit = component.get_value()
        self.on_limit_changed_signal(self._limit)

    def set_reward(self, value):
        self._reward = value
        self.on_reward_changed_signal(self._reward)

    def reward_changed(self, component):
        self._reward = component.get_value()
        self.on_reward_changed_signal(self._reward)
