#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_goals\forms\goalFormFields.py
import math
import eveicon
import uthread
from carbonui import Align, uiconst, TextDetail
from carbonui import TextColor, TextBody
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.combo import Combo
from carbonui.control.forms.formFields import BaseField, IntegerEditField
from carbonui.primitives.container import Sprite, Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from eveformat import currency, number
from eveformat.client import solar_system_with_security
from eveui import LocationField, fade, fade_in, ItemField, NpcCorporationField, ShipField, PlayerOrPlayerOrganizationField, fade_out
from eveui.audio import Sound
from eveui.autocomplete import LocationSuggestion, ItemTypeSuggestion, ItemGroupSuggestion, ItemCategorySuggestion, ShipTypeSuggestion, ShipClassSuggestion, OwnerIdentitySuggestion, NpcCorporationSuggestion
from localization import GetByLabel

class MultiValueFormField(BaseField):

    def ApplyAttributes(self, attributes):
        self.edit = None
        self._result = list()
        self._results_entry = {}
        super(MultiValueFormField, self).ApplyAttributes(attributes)

    def ConstructBody(self):
        self.ConstructSearchField()
        self._results_container = ContainerAutoSize(name='multivalue_results_container', parent=self, align=Align.TOTOP)
        for entry in self.component.get_value() or []:
            self._initialize_entry(entry)

    def ConstructSearchField(self):
        pass

    def _initialize_entry(self, entry):
        self._add_new_entry(entry)

    def _add_entry_chip(self, entry):
        self._result.append(entry)
        self._sort_results()
        chip = MultiValueListItem(idx=self._result.index(entry), parent=self._results_container, entry=entry, get_text=self._get_text, render_icon=self._render_icon, get_menu=self._get_menu, get_drag_data=self._get_drag_data, on_click_remove=self._on_remove_chip)
        self._results_entry[entry] = chip

    def _get_label_text(self):
        return u'{} <color={}>{}/{}</color>'.format(self.component.label, TextColor.DISABLED, len(self._result), self.component.max_entries)

    def _get_text(self, entry):
        return str(entry)

    def _get_subtext(self, entry):
        return ''

    def _render_icon(self, entry, size):
        return None

    def _get_menu(self, entry):
        return None

    def _get_drag_data(self, entry):
        return None

    def _on_remove_chip(self, entry):
        self._result.remove(entry)
        chip = self._results_entry[entry]
        chip.Close()
        del self._results_entry[entry]
        self._values_changed()

    def _cant_add_new_entry(self, entry):
        return self._result is None or entry in self._result or self._at_max_entries()

    def _add_new_entry(self, entry):
        if self._cant_add_new_entry(entry):
            self._clear_edit()
            return
        self._add_entry_chip(entry)
        self._values_changed()
        self._clear_edit()

    def _at_max_entries(self):
        return len(self._result) >= self.component.max_entries

    def _values_changed(self):
        self.component.on_field_value_changed(self.get_value())
        self.label.text = self._get_label_text()
        self._update_input_field()

    def _update_input_field(self):
        pass

    def _clear_edit(self):
        return NotImplementedError()

    def get_value(self):
        return self._result

    def set_value(self, value):
        pass

    def _sort_results(self):
        pass


class _AutoCompleteMultiField(MultiValueFormField):

    def get_value(self):
        return [ self._get_suggestion_value(suggestion) for suggestion in self._result ]

    def _get_suggestion_value(self, suggestion):
        return suggestion

    def _value_changed(self, *args):
        new_value = self.edit.completed_suggestion
        if new_value is None:
            return
        self._add_new_entry(new_value)

    def _get_text(self, entry):
        return entry.text

    def _get_menu(self, entry):
        return entry.get_menu()

    def _get_drag_data(self, entry):
        return entry.get_drag_data()

    def _update_input_field(self):
        if self._at_max_entries():
            self.edit.placeholder = GetByLabel('UI/Corporations/Goals/MultiValueLimitReached')
        else:
            self.edit.placeholder = self.component.placeholder

    def _clear_edit(self):
        uthread.pool('_AutoCompleteMultiField::_clear_edit', self.edit.clear)

    def _sort_results(self):
        self._result.sort(key=lambda entry: self._sort_key(entry))

    def _sort_key(self, entry):
        return entry.text.lower()


class MultiValueLocationFormField(_AutoCompleteMultiField):

    def ConstructSearchField(self):
        self.edit = LocationField(parent=self, align=Align.TOTOP, placeholder=self.component.placeholder, show_suggestions_on_focus=True, location_id=None, include_station=False)
        self.edit.bind(completed_suggestion=self._value_changed)

    def _initialize_entry(self, entry):
        self._add_new_entry(LocationSuggestion(entry))

    def _get_suggestion_value(self, suggestion):
        return suggestion.location_id

    def _get_text(self, entry):
        if entry.is_solar_system:
            return solar_system_with_security(entry.location_id)
        subtext = None
        if entry.is_constellation:
            subtext = GetByLabel('UI/Common/LocationTypes/Constellation')
        elif entry.is_region:
            subtext = GetByLabel('UI/Common/LocationTypes/Region')
        return _get_text_with_subtext(entry.text, subtext)

    def _render_icon(self, entry, size):
        if entry.is_solar_system:
            icon = eveicon.solar_system
        elif entry.is_constellation:
            icon = eveicon.constellation
        elif entry.is_region:
            icon = eveicon.region
        else:
            return None
        return _render_basic_icon(icon, size)

    def _get_menu(self, entry):
        return entry.get_menu()

    def _sort_key(self, entry):
        if entry.is_solar_system:
            priority = 1
        elif entry.is_constellation:
            priority = 2
        elif entry.is_region:
            priority = 3
        else:
            priority = 4
        return (priority, entry.text.lower())


class MultiValueItemFormField(_AutoCompleteMultiField):

    def ConstructSearchField(self):
        self.edit = ItemField(parent=self, align=Align.TOTOP, placeholder=self.component.placeholder, show_suggestions_on_focus=True, type_filter=self.component.type_filter, group_filter=self.component.group_filter, category_filter=self.component.category_filter, include_type=self.component.include_type, include_group=self.component.include_group, include_category=self.component.include_category)
        self.edit.bind(completed_suggestion=self._value_changed)

    def _initialize_entry(self, entry):
        entry_type, entry_id = entry
        suggestion = None
        if entry_type == 'item_type':
            suggestion = ItemTypeSuggestion(entry_id)
        elif entry_type == 'item_group':
            suggestion = ItemGroupSuggestion(entry_id)
        elif entry_type == 'item_category':
            suggestion = ItemCategorySuggestion(entry_id)
        if suggestion:
            self._add_new_entry(suggestion)

    def _get_suggestion_value(self, suggestion):
        if isinstance(suggestion, ItemTypeSuggestion):
            return ('item_type', suggestion.type_id)
        if isinstance(suggestion, ItemGroupSuggestion):
            return ('item_group', suggestion.group_id)
        if isinstance(suggestion, ItemCategorySuggestion):
            return ('item_category', suggestion.category_id)

    def _render_icon(self, entry, size):
        if isinstance(entry, ItemTypeSuggestion):
            size = max(size, 24)
        return entry.render_icon(size)

    def _get_text(self, entry):
        if isinstance(entry, ItemTypeSuggestion):
            return entry.text
        return _get_text_with_subtext(entry.text, entry.subtext)

    def _sort_key(self, entry):
        if isinstance(entry, ItemTypeSuggestion):
            priority = 1
        elif isinstance(entry, ItemGroupSuggestion):
            priority = 2
        elif isinstance(entry, ItemCategorySuggestion):
            priority = 3
        else:
            priority = 4
        return (priority, entry.text.lower())


class MultiValueNPCCorpFormField(_AutoCompleteMultiField):

    def ConstructSearchField(self):
        self.edit = NpcCorporationField(parent=self, align=Align.TOTOP, placeholder=self.component.placeholder, show_suggestions_on_focus=True, filter=self.component.filter)
        self.edit.bind(completed_suggestion=self._value_changed)

    def _initialize_entry(self, entry):
        self._add_new_entry(NpcCorporationSuggestion(entry))

    def _get_suggestion_value(self, suggestion):
        return suggestion.corporation_id

    def _render_icon(self, entry, size):
        size = max(size, 24)
        return entry.render_icon(size)


class MultiValuePlayerCorpOrOrgFormField(_AutoCompleteMultiField):

    def ConstructSearchField(self):
        self.edit = PlayerOrPlayerOrganizationField(parent=self, align=Align.TOTOP, placeholder=self.component.placeholder, show_suggestions_on_focus=True)
        self.edit.bind(completed_suggestion=self._value_changed)

    def _initialize_entry(self, entry):
        self._add_new_entry(OwnerIdentitySuggestion(entry))

    def _get_suggestion_value(self, suggestion):
        return suggestion.owner_id

    def _render_icon(self, entry, size):
        size = max(size, 24)
        return entry.render_icon(size)

    def _get_text(self, entry):
        return _get_text_with_subtext(entry.text, entry.subtext)

    def _sort_key(self, entry):
        if entry.is_character:
            priority = 1
        elif entry.is_corporation:
            priority = 2
        elif entry.is_alliance:
            priority = 3
        elif entry.is_faction:
            priority = 4
        else:
            priority = 5
        return (priority, entry.text.lower())


class MultiValueShipAndShipTreeFormField(_AutoCompleteMultiField):

    def ConstructSearchField(self):
        self.edit = ShipField(parent=self, align=Align.TOTOP, placeholder=self.component.placeholder, show_suggestions_on_focus=True)
        self.edit.bind(completed_suggestion=self._value_changed)

    def _initialize_entry(self, entry):
        entry_type, entry_id = entry
        suggestion = None
        if entry_type == 'ship_type':
            suggestion = ShipTypeSuggestion(entry_id)
        elif entry_type == 'ship_class':
            suggestion = ShipClassSuggestion(entry_id)
        if suggestion:
            self._add_new_entry(suggestion)

    def _get_suggestion_value(self, suggestion):
        if isinstance(suggestion, ShipTypeSuggestion):
            return ('ship_type', suggestion.type_id)
        if isinstance(suggestion, ShipClassSuggestion):
            return ('ship_class', suggestion.ship_class_id)

    def _render_icon(self, entry, size):
        if isinstance(entry, ShipTypeSuggestion):
            size = max(size, 24)
        return entry.render_icon(size)

    def _sort_key(self, entry):
        if isinstance(entry, ShipTypeSuggestion):
            priority = 1
        elif isinstance(entry, ShipClassSuggestion):
            priority = 2
        else:
            priority = 3
        return (priority, entry.text.lower())


class MultiValueEnum(MultiValueFormField):

    def ConstructSearchField(self):
        self.edit = Combo(name=self.component.get_id(), parent=self, align=Align.TOTOP, callback=self._value_changed, options=self.component.options, nothingSelectedText=GetByLabel('UI/Common/PleaseSelect'))

    def _value_changed(self, *args):
        entry = self.edit.GetSelectedEntry()
        if entry is None:
            return
        self._add_new_entry(entry)

    def _get_text(self, entry):
        return entry.label

    def _render_icon(self, entry, size):
        return _render_basic_icon(entry.icon, size)

    def _clear_edit(self):
        self.edit.SetNothingSelected()

    def _update_input_field(self):
        if self._at_max_entries():
            self.edit.nothingSelectedText = GetByLabel('UI/Corporations/Goals/MultiValueLimitReached')
        else:
            self.edit.placeholder = GetByLabel('UI/Common/PleaseSelect')


class MultiValueListItem(Container):
    default_align = Align.TOTOP
    default_state = uiconst.UI_NORMAL
    default_alignMode = Align.TOLEFT
    default_height = 28
    default_padTop = 8
    isDragObject = True

    def __init__(self, entry, get_text, render_icon, get_menu, get_drag_data, on_click_remove, *args, **kwargs):
        super(MultiValueListItem, self).__init__(*args, **kwargs)
        self._entry = entry
        self._get_menu = get_menu
        self._get_drag_data = get_drag_data
        self._on_click_remove = on_click_remove
        contents_container = Container(parent=self, align=Align.TOALL, padLeft=8, padRight=8)
        self._close_container = Container(parent=contents_container, align=Align.TORIGHT, width=16, padLeft=8, opacity=0)
        ButtonIcon(parent=self._close_container, texturePath=eveicon.close, align=Align.CENTER, height=16, width=16, color=TextColor.SECONDARY, func=self._close_icon_clicked)
        icon = render_icon(entry, size=16)
        if icon:
            icon_container = Container(parent=contents_container, state=uiconst.UI_DISABLED, align=Align.TOLEFT, width=16, padRight=8)
            icon.align = Align.CENTER
            icon.SetParent(icon_container)
        label_container = Container(parent=contents_container, align=Align.TOALL)
        self._label = TextBody(parent=label_container, align=Align.CENTERLEFT, text=get_text(entry))
        self._bg_frame = Frame(bgParent=self, cornerSize=9, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', color=(1, 1, 1, 0.05))

    def _close_icon_clicked(self, *args, **kwargs):
        self._on_click_remove(self._entry)

    def GetMenu(self):
        return self._get_menu(self._entry)

    def GetDragData(self):
        drag_data = self._get_drag_data(self._entry)
        if drag_data:
            return [drag_data]

    def OnMouseEnter(self, *args):
        super(MultiValueListItem, self).OnMouseEnter(*args)
        Sound.button_hover.play()
        fade(self._bg_frame, end_value=0.1, duration=0.2)
        fade_in(self._close_container, duration=0.2)

    def OnMouseExit(self, *args):
        super(MultiValueListItem, self).OnMouseExit(*args)
        fade(self._bg_frame, end_value=0.05, duration=0.2)
        fade_out(self._close_container, duration=0.2)


def _render_basic_icon(icon, size):
    return Sprite(texturePath=icon, align=Align.CENTER, height=size, width=size, color=TextColor.NORMAL)


def _get_text_with_subtext(text, subtext):
    if subtext:
        return u'<color={}>[{}]</color> {}'.format(TextColor.SECONDARY, subtext, text)
    return text


class ParticipationLimitField(IntegerEditField):
    default_padTop = 0

    def ApplyAttributes(self, attributes):
        super(ParticipationLimitField, self).ApplyAttributes(attributes)
        self.component.max_value_changed_signal.connect(self.set_max_value)
        self.recalculate_required_contributors()

    def Close(self):
        super(ParticipationLimitField, self).Close()
        self.component.max_value_changed_signal.disconnect(self.set_max_value)

    def ConstructLayout(self):
        self.ConstructHeader()
        self.ConstructHint(self)
        self.ConstructBody()
        self.required_contributors_label = TextDetail(parent=self, align=Align.TOTOP, color=TextColor.SECONDARY, padTop=6, padLeft=2)

    def _OnValueChanged(self, *args):
        super(ParticipationLimitField, self)._OnValueChanged(*args)
        self.recalculate_required_contributors()

    def get_max_value(self):
        return self.edit.maxValue

    def set_max_value(self, value):
        self.edit.SetMaxValue(value)
        if self.get_value() > value:
            self.set_value(value)
        self.recalculate_required_contributors()

    def recalculate_required_contributors(self):
        value = self.get_value()
        if not value:
            self.required_contributors_label.display = False
            return
        max_value = self.get_max_value()
        required_contributors = int(math.ceil(float(max_value) / value))
        label = GetByLabel('UI/Corporations/Goals/RequiredContributors', color=TextColor.NORMAL, num=number(required_contributors, decimal_places=0))
        self.required_contributors_label.display = True
        self.required_contributors_label.SetText(label)


class MaxRewardPerContributorField(BaseField):
    default_padTop = 0

    def ApplyAttributes(self, attributes):
        super(MaxRewardPerContributorField, self).ApplyAttributes(attributes)
        self.component.on_reward_changed_signal.connect(self.on_reward_changed)
        self.component.on_limit_changed_signal.connect(self.on_limit_changed)

    def ConstructLayout(self):
        self.ConstructHint(self)
        self.text = TextDetail(parent=self, align=Align.TOTOP, text=self.component.label, color=TextColor.NORMAL, padding=(8, 0, 0, 4))
        self.recalculate_reward_per_contributor()

    def get_value(self):
        return None

    def on_reward_changed(self, value):
        if value is not None:
            self.recalculate_reward_per_contributor()

    def on_limit_changed(self, value):
        if value is not None:
            self.recalculate_reward_per_contributor()

    def recalculate_reward_per_contributor(self):
        if self.component.get_limit() is None:
            return
        reward = self.component.get_limit() * self.component.get_reward()
        text = GetByLabel('UI/Corporations/Goals/RewardLimitPerContributor', rewardAmount=currency.isk(reward), secondaryColor=TextColor.SECONDARY)
        self.text.SetText(text)
