#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\forms\formFields.py
import datetime
import time
from datetime import date
import eveui
import uthread2
from carbonui import ButtonVariant, Density, ButtonFrameType, uiconst
from carbonui import TextColor, TextBody, Align, TextDetail
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.forms import formComponent
from carbonui.control.forms.form import Form
from carbonui.control.forms.formsUtil import FormatAsIncompleteInput
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from dateutil import relativedelta
from eve.client.script.ui.control.datepicker import DatePicker
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.infoIcon import InfoIcon
from eveui import ItemTypeField
from eveui.autocomplete import ItemTypeSuggestion, LocationSuggestion, ShipTypeSuggestion
from eveui.autocomplete.npc.suggestion import FactionSuggestion, NpcCorporationSuggestion
from eveui.autocomplete.player.suggestion import OwnerIdentitySuggestion
from localization import GetByLabel
from localization.formatters.timeIntervalFormatters import FormatSpecificDurationWritten

class BaseField(ContainerAutoSize):
    default_align = Align.TOTOP
    default_alignMode = Align.TOTOP
    default_padTop = 8
    default_padBottom = 16

    def ApplyAttributes(self, attributes):
        super(BaseField, self).ApplyAttributes(attributes)
        self.label = None
        self.icon = None
        self.info = None
        self.component = attributes.component
        self.ConstructLayout()
        self.component.init_value(self.get_value())
        self.component.on_label_changed.connect(self.OnLabelChanged)
        self.component.on_icon_changed.connect(self.OnIconChanged)
        self.component.on_hint_changed.connect(self.OnHintChanged)
        self.component.on_validated.connect(self.OnValidated)
        self.component.on_value_set.connect(self.set_value)
        self.component.on_visibility_changed.connect(self.OnVisibilityChanged)
        self.display = self.component.is_visible
        if self.component.indent_level:
            self.padLeft = self.component.indent_level * 24

    def OnLabelChanged(self, component):
        if self.label:
            self.label.text = self._get_label_text()

    def OnIconChanged(self, component):
        if self.icon:
            self.icon.texturePath = component.icon

    def OnHintChanged(self, component):
        self.component.hint = component.hint
        self.ConstructHint(self.header_container)

    def OnVisibilityChanged(self, component):
        self.display = component.is_visible

    def OnValidated(self, component, is_valid):
        if not self.label:
            return
        text = self._get_label_text()
        if not is_valid:
            text = FormatAsIncompleteInput(text)
        self.label.text = text

    def ConstructLayout(self):
        self.ConstructHeader()
        self.ConstructBody()

    def Reconstruct(self):
        self.Flush()
        self.ConstructLayout()

    def ConstructHeader(self):
        self.header_container = ContainerAutoSize(name='header_container', parent=self, align=Align.TOTOP, alignMode=Align.TOTOP, padBottom=4)
        self.ConstructIcon(self.header_container)
        self.ConstructHint(self.header_container)
        self.ConstructLabel(self.header_container)

    def ConstructIcon(self, parent):
        icon = self.component.icon
        if not icon:
            return
        icon_container = Container(name='icon_container', parent=parent, state=uiconst.UI_DISABLED, align=Align.TOLEFT, width=16)
        self.icon = Sprite(parent=icon_container, texturePath=icon, align=Align.CENTER, height=16, width=16, color=TextColor.SECONDARY)

    def ConstructLabel(self, parent):
        self.label = TextDetail(parent=parent, align=Align.TOTOP, text=self._get_label_text(), color=TextColor.SECONDARY, padLeft=4)

    def ConstructHint(self, parent = None):
        if self.component.hint:
            self.info = InfoIcon(parent=parent or self, align=Align.TOPRIGHT, hint=self.component.hint)
        elif self.info:
            self.info.Close()
            self.info = None

    def ConstructBody(self):
        pass

    def get_value(self):
        raise NotImplementedError

    def _OnValueChanged(self, *args):
        self.component.on_field_value_changed(self.get_value())

    def set_value(self, value):
        raise NotImplementedError

    def _get_label_text(self):
        return self.component.label


class FormField(BaseField):
    default_padTop = 0
    default_padBottom = 0

    def ConstructLayout(self):
        self.ConstructHint()
        ConstructFields(self, self.component)
        self.component.on_components_changed.connect(self.OnComponentsChanged)

    def OnComponentsChanged(self, *args):
        self.Reconstruct()

    def get_value(self):
        return self.component.get_value()

    def set_value(self, value):
        pass


class EditField(BaseField):

    def ConstructBody(self):
        max_chars = self.component.get_max_characters()
        self.textEdit = SingleLineEditText(name=self.component.get_id(), parent=self, setvalue=self.component.get_value(), hintText=self.component.placeholder, align=Align.TOTOP, OnChange=self._OnValueChanged, showLetterCounter=bool(max_chars), maxLength=max_chars)

    def get_value(self):
        return self.textEdit.GetText().strip()

    def set_value(self, value):
        self.textEdit.SetText(value)


class EditFieldMultiLine(BaseField):

    def ConstructBody(self):
        max_chars = self.component.get_max_characters()
        self.textEdit = EditPlainText(name=self.component.get_id(), parent=self, setvalue=self.component.get_value(), hintText=self.component.placeholder, height=32 + self.component.num_lines * 16, align=Align.TOTOP, countWithTags=bool(max_chars), counterMax=max_chars, showattributepanel=self.component.show_formatting_panel)
        self.textEdit.OnChange = self._OnValueChanged

    def get_value(self):
        return self.textEdit.GetValue().strip()

    def set_value(self, value):
        self.textEdit.SetText(value)


class Label(BaseField):

    def ConstructLayout(self):
        self.ConstructLabel(self)

    def get_value(self):
        return None

    def set_value(self, value):
        pass


class IntegerEditField(BaseField):

    def ApplyAttributes(self, attributes):
        super(IntegerEditField, self).ApplyAttributes(attributes)
        self.component.max_value_changed_signal.connect(self.set_max_value)

    def Close(self):
        super(IntegerEditField, self).Close()
        self.component.max_value_changed_signal.disconnect(self.set_max_value)

    def ConstructBody(self):
        self.edit = SingleLineEditInteger(name=self.component.get_id(), parent=self, setvalue=self.component.get_value(), minValue=self.component.min_value, maxValue=self.component.max_value, align=Align.TOTOP, hintText=self.component.placeholder, OnChange=self._OnValueChanged)

    def get_value(self):
        if not self.edit.text:
            return None
        return self.edit.GetValue()

    def set_value(self, value):
        self.edit.SetValue(value)

    def get_max_value(self):
        return self.edit.maxValue

    def set_max_value(self, value):
        self.edit.SetMaxValue(value)
        if self.get_value() > value:
            self.set_value(value)


class FloatEditField(BaseField):

    def ConstructBody(self):
        self.edit = SingleLineEditFloat(name=self.component.get_id(), parent=self, setvalue=self.component.get_value(), minValue=self.component.min_value, align=Align.TOTOP, OnChange=self._OnValueChanged, decimalPlaces=2)

    def get_value(self):
        return self.edit.GetValue()

    def set_value(self, value):
        self.edit.SetValue(value)


class CheckboxField(BaseField):

    def ConstructLayout(self):
        self.ConstructHint()
        self.checkbox = Checkbox(name=self.component.get_id(), parent=self, checked=self.component.get_value(), text=self.component.get_label(), callback=self._OnValueChanged)

    def get_value(self):
        return self.checkbox.GetValue()

    def set_value(self, value):
        self.checkbox.checked = value

    def ConstructHint(self, parent = None):
        if self.component.hint:
            InfoIcon(parent=self, align=Align.CENTERRIGHT, hint=self.component.hint)


class ComboField(BaseField):

    def ConstructBody(self):
        self.combo = Combo(name=self.component.get_id(), parent=self, align=Align.TOTOP, callback=self._OnValueChanged, options=self.component.options, select=self.component.get_value(), nothingSelectedText=self.component.placeholder)

    def get_value(self):
        return self.combo.GetValue()

    def set_value(self, value):
        self.combo.SelectItemByValue(value)


class EveTypeField(BaseField):

    def ConstructBody(self):
        type_id = self.component.get_value()
        completed_suggestion = ItemTypeSuggestion(type_id=type_id) if type_id else None
        self.edit = ItemTypeField(parent=self, align=Align.TOTOP, placeholder=self.component.placeholder, show_suggestions_on_focus=True, completed_suggestion=completed_suggestion, type_filter=self.component.type_filter)
        self.edit.bind(completed_suggestion=self._OnValueChanged)

    def get_value(self):
        selected = self.edit.completed_suggestion
        if selected:
            return selected.type_id

    def set_value(self, value):
        pass


class SolarSystemField(BaseField):

    def ConstructBody(self):
        location_id = self.component.get_value()
        completed_suggestion = LocationSuggestion(location_id=location_id) if location_id else None
        self.edit = eveui.SolarSystemField(parent=self, align=Align.TOTOP, placeholder=self.component.placeholder, show_suggestions_on_focus=True, completed_suggestion=completed_suggestion, location_id=location_id)
        self.edit.bind(completed_suggestion=self._OnValueChanged)

    def get_value(self):
        selected = self.edit.completed_suggestion
        if selected:
            return selected.location_id

    def set_value(self, value):
        pass


class NPCFactionField(BaseField):

    def ConstructBody(self):
        faction_id = self.component.get_value()
        completed_suggestion = FactionSuggestion(faction_id=faction_id) if faction_id else None
        self.edit = eveui.FactionField(parent=self, align=Align.TOTOP, placeholder=self.component.placeholder, show_suggestions_on_focus=True, completed_suggestion=completed_suggestion)
        self.edit.bind(completed_suggestion=self._OnValueChanged)

    def get_value(self):
        selected = self.edit.completed_suggestion
        if selected:
            return selected.faction_id

    def set_value(self, value):
        pass


class PlayerCorporationField(BaseField):

    def ConstructBody(self):
        corp_id = self.component.get_value()
        completed_suggestion = OwnerIdentitySuggestion(owner_id=corp_id) if corp_id else None
        self.edit = eveui.PlayerCorporationField(parent=self, align=Align.TOTOP, placeholder=self.component.placeholder, show_suggestions_on_focus=True, completed_suggestion=completed_suggestion)
        self.edit.bind(completed_suggestion=self._OnValueChanged)

    def get_value(self):
        selected = self.edit.completed_suggestion
        if selected:
            return selected.corp_id

    def set_value(self, value):
        pass


class NPCCorporationField(BaseField):

    def ConstructBody(self):
        corporation_id = self.component.get_value()
        completed_suggestion = NpcCorporationSuggestion(corporation_id=corporation_id) if corporation_id else None
        self.edit = eveui.NpcCorporationField(parent=self, align=Align.TOTOP, placeholder=self.component.placeholder, show_suggestions_on_focus=True, completed_suggestion=completed_suggestion, filter=self.component.filter)
        self.edit.bind(completed_suggestion=self._OnValueChanged)

    def get_value(self):
        selected = self.edit.completed_suggestion
        if selected:
            return selected.corporation_id

    def set_value(self, value):
        pass


class OrganizationField(BaseField):

    def ConstructBody(self):
        owner_id = self.component.get_value()
        completed_suggestion = OwnerIdentitySuggestion(owner_id=owner_id) if owner_id else None
        self.edit = eveui.OrganizationField(parent=self, align=Align.TOTOP, placeholder=self.component.placeholder, show_suggestions_on_focus=True, completed_suggestion=completed_suggestion)
        self.edit.bind(completed_suggestion=self._OnValueChanged)

    def get_value(self):
        selected = self.edit.completed_suggestion
        if selected:
            return selected.owner_id

    def set_value(self, value):
        pass


class PlayerOrPlayerOrganizationField(BaseField):

    def ConstructBody(self):
        owner_id = self.component.get_value()
        completed_suggestion = OwnerIdentitySuggestion(owner_id=owner_id) if owner_id else None
        self.edit = eveui.PlayerOrPlayerOrganizationField(parent=self, align=Align.TOTOP, placeholder=self.component.placeholder, show_suggestions_on_focus=True, completed_suggestion=completed_suggestion)
        self.edit.bind(completed_suggestion=self._OnValueChanged)

    def get_value(self):
        selected = self.edit.completed_suggestion
        if selected:
            return selected.owner_id

    def set_value(self, value):
        pass


class ShipAndTreeGroupField(BaseField):

    def ConstructBody(self):
        type_id = self.component.get_value()
        completed_suggestion = ShipTypeSuggestion(type_id=type_id) if type_id else None
        self.edit = eveui.ShipField(parent=self, align=Align.TOTOP, placeholder=self.component.placeholder, show_suggestions_on_focus=True, completed_suggestion=completed_suggestion)
        self.edit.bind(completed_suggestion=self._OnValueChanged)

    def get_value(self):
        selected = self.edit.completed_suggestion
        if selected:
            return selected.owner_id

    def set_value(self, value):
        pass


class DateTimeField(BaseField):
    default_clipChildren = True
    default_padTop = -8

    def _get_default_value(self):
        if self.component.duration_datetime:
            duration_in_seconds = self.component.duration_datetime.total_seconds()
            time_to_advance = relativedelta.relativedelta(seconds=duration_in_seconds)
        else:
            time_to_advance = relativedelta.relativedelta(weeks=1)
        now = datetime.datetime.utcnow()
        target_time = now + time_to_advance
        target_time_tuple = target_time.timetuple()
        return target_time_tuple

    def ConstructBody(self):
        if self.component.time_options is not None:
            self._buttons = []
            self._button_data = {}
            _flow = FlowContainer(parent=self, align=Align.TOTOP, height=24, contentSpacing=(8, 8))
            self._construct_buttons_from_options(_flow)
        date_container = ContainerAutoSize(name='date_container', parent=self, align=Align.TOTOP, alignMode=Align.TOTOP, top=32)
        set_picker_value = self._get_default_value()
        self.date_picker = DatePicker(name='datepicker', parent=date_container, align=Align.TOTOP, width=256, height=18)
        now = time.gmtime()
        self.date_picker.Startup(now=now, withTime=True, timeparts=self.component.timeparts, startYear=now[0], yearRange=self.component.year_range, set_value=set_picker_value)
        self.date_picker.OnDateChange = self._OnValueChanged
        self.duration_label = TextBody(name='duration_label', parent=self, align=Align.TOTOP, top=8)
        self._update_duration_label()
        uthread2.start_tasklet(self._time_remaining_routine)

    def _time_remaining_routine(self):
        while not self.destroyed:
            self._update_duration_label()
            uthread2.sleep(1)

    def _pre_set_from_timedelta(self):
        self.date_picker.SetValueFromNow(seconds=self.component.duration_datetime.total_seconds())
        self.component.on_field_value_changed(self.get_value())

    def _construct_buttons_from_options(self, parent):
        options = self.component.time_options
        for idx, option in enumerate(options):
            period, label, duration = self._parse_option(option)
            is_first = idx == 0
            is_last = idx == len(options) - 1
            self._add_button(parent, period, label, duration, is_first=is_first, is_last=is_last)

    def _parse_option(self, option):
        digits = ''
        period = ''
        for char in option:
            if char.isdigit():
                digits = digits + char
            else:
                char = char.lower()
                if char not in ('h', 'd', 'w', 'm') or len(digits) == 0:
                    raise ValueError('Invalid time option %s', option)
                period = char
                break

        if len(digits) == 0 or len(period) == 0:
            raise ValueError('Invalid time option %s', option)
        duration = int(digits)
        label = ''
        if period == 'h':
            label = FormatSpecificDurationWritten(duration, type='hour')
        elif period == 'd':
            label = FormatSpecificDurationWritten(duration, type='day')
        elif period == 'w':
            label = FormatSpecificDurationWritten(duration, type='week')
        elif period == 'm':
            label = FormatSpecificDurationWritten(duration, type='month')
        return (period, label, duration)

    def _add_button(self, parent, period, label, duration, is_first, is_last):
        if is_first:
            frame_type = ButtonFrameType.CUT_BOTTOM_LEFT
        elif is_last:
            frame_type = ButtonFrameType.CUT_BOTTOM_RIGHT
        else:
            frame_type = ButtonFrameType.RECTANGLE
        button = Button(parent=parent, label=label, func=self._button_clicked, variant=ButtonVariant.GHOST, density=Density.COMPACT, frame_type=frame_type)
        self._buttons.append(button)
        self._button_data[button] = (period, duration)

    def _deselect_buttons(self):
        for button in self._buttons:
            if button.variant == ButtonVariant.PRIMARY:
                button.variant = ButtonVariant.GHOST

    def _button_clicked(self, component):
        if component is None:
            return
        for button in self._buttons:
            if component == button:
                button.variant = ButtonVariant.PRIMARY
            elif button.variant == ButtonVariant.PRIMARY:
                button.variant = ButtonVariant.GHOST

        period, duration = self._button_data[component]
        if period == 'h':
            self.date_picker.SetValueFromNow(hours=duration)
        elif period == 'd':
            self.date_picker.SetValueFromNow(days=duration)
        elif period == 'w':
            self.date_picker.SetValueFromNow(weeks=duration)
        elif period == 'm':
            self.date_picker.SetValueFromNow(months=duration)
        self._update_duration_label()
        self.component.on_field_value_changed(self.get_value())

    def _is_valid_duration(self):
        if self.date_picker.HasDatePassed():
            return False
        delta = self.date_picker.GetDurationFromNow()
        if delta.months is 0 and delta.days is 0 and delta.hours is 0 and delta.minutes < 15:
            return False
        if delta.years is 0:
            return True
        if delta.years is 1 and delta.days is 0:
            date_now = date.today()
            date_in_picker = self.date_picker.GetValueAsDateTime()
            if date_now.day is date_in_picker.day and date_now.month is date_in_picker.month:
                return True
        return False

    def _update_duration_label(self):
        written_form = self.date_picker.GetDurationFromNowString(show_from='day')
        if written_form:
            label = u'{} {}'.format(GetByLabel('UI/Corporations/Goals/ChosenDuration'), written_form)
        else:
            label = GetByLabel('UI/Corporations/Goals/DurationInPast')
        self.duration_label.text = label
        if self._is_valid_duration() and self.duration_label.color is not TextColor.NORMAL:
            self.duration_label.color = TextColor.NORMAL
        elif self.duration_label.color is not TextColor.DANGER:
            self.duration_label.color = TextColor.DANGER

    def _OnValueChanged(self, *args):
        super(DateTimeField, self)._OnValueChanged(*args)
        self._deselect_buttons()
        self._update_duration_label()

    def get_value(self):
        return self.date_picker.GetValue()

    def set_value(self, value):
        self.date_picker.SetValue(value)


class Divider(BaseField):

    def ConstructLayout(self):
        Line(parent=self, align=Align.TOTOP, weight=1, opacity=0.2)

    def get_value(self):
        return None

    def set_value(self, value):
        pass


def ConstructFields(parent, form):
    for component in form.get_components():
        ConstructField(parent, component)


def ConstructField(parent, component, **kwargs):
    field_cls = GetFieldClass(component)
    return field_cls(parent=parent, component=component, **kwargs)


def GetFieldClass(component):
    if component.field_cls:
        return component.field_cls
    if isinstance(component, Form):
        return FormField
    if isinstance(component, formComponent.Boolean):
        return CheckboxField
    if isinstance(component, formComponent.Text):
        return EditField
    if isinstance(component, formComponent.TextMultiLine):
        return EditFieldMultiLine
    if isinstance(component, formComponent.Integer):
        return IntegerEditField
    if isinstance(component, formComponent.Float):
        return FloatEditField
    if isinstance(component, formComponent.Enum):
        return ComboField
    if isinstance(component, formComponent.EveType):
        return EveTypeField
    if isinstance(component, formComponent.SolarSystem):
        return SolarSystemField
    if isinstance(component, formComponent.NPCFaction):
        return NPCFactionField
    if isinstance(component, formComponent.PlayerCorporation):
        return PlayerCorporationField
    if isinstance(component, formComponent.NPCCorporation):
        return NPCCorporationField
    if isinstance(component, formComponent.PlayerOrPlayerOrganization):
        return PlayerOrPlayerOrganizationField
    if isinstance(component, formComponent.Label):
        return Label
    if isinstance(component, formComponent.Divider):
        return Divider
    if isinstance(component, formComponent.DateTime):
        return DateTimeField
    raise ValueError('Unknown component', repr(component))
