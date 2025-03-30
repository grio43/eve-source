#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\cargo.py
from appConst import maxCargoContainerTransferDistance
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import Align, TextBody, TextColor, PickState, uiconst
from carbonui.control.button import Button
from carbonui.control.forms import formComponent, formFields
from carbonui.control.forms.form import Form, FormActionSubmit
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.warningContainer import WarningContainer
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.control.message import ShowQuickMessage
from evelink.client import type_link
from evetypes import GetVolume
from localization import GetByLabel
from logging import getLogger
from sovereignty.mercenaryden.client.ui.containers.cargo_item import CargoItem
from uthread2 import StartTasklet
logger = getLogger('mercenary_den')

class CargoContainer(ContainerAutoSize):
    LABEL_PATH_CARGO_NAME = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/CargoName'
    LABEL_PATH_CARGO_CAPACITY = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/CargoCapacity'
    LABEL_PATH_BUTTON_SELECTED = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/TakeButtonNameForSelectedCargo'
    LABEL_PATH_BUTTON_TOOLTIP_SELECTED = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/TakeButtonTooltipForSelectedCargo'
    LABEL_PATH_BUTTON_ALL = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/TakeButtonNameForAllCargo'
    LABEL_PATH_BUTTON_TOOLTIP_ALL = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/TakeButtonTooltipForAllCargo'
    LABEL_PATH_BUTTON_TOOLTIP_DISABLED = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/TakeButtonTooltipForDisabled'
    LABEL_PATH_TAKE_CARGO_SUCCESS = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/TakeCargoSuccess'
    LABEL_PATH_CARGO_VOLUME = 'UI/Inventory/ContainerQuantityAndCapacity'
    LABEL_PATH_CARGO_ITEM = 'UI/Inventory/QuantityAndName'
    LABEL_PATH_GAUGE_TOOLTIP = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/TimerTooltip'
    LABEL_PATH_WARNING_SKILLS_MISSING = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/TakeCargoDisabledMissingSkills'
    WIDTH_INPUT_FIELD = 104
    HEIGHT_CARGO_CAPACITY_BAR = 24
    PADDING_BOTTOM_CARGO_NAME = 8
    PADDING_BOTTOM_CARGO_CAPACITY_BAR = 16
    PADDING_CARGO_ITEMS_TO_BUTTON = 8
    PADDING_BUTTON_TO_WARNING_SKILLS_MISSING = 16
    PADDING_AROUND_CARGO_ITEM = 8
    COLOR_CARGO_NAME_LABEL = TextColor.SECONDARY
    COLOR_CARGO_CAPACITY_BAR = eveThemeColor.THEME_FOCUSDARK
    COLOR_CARGO_CAPACITY_BAR_BACKGROUND = eveColor.COAL_BLACK
    COLOR_CARGO_CAPACITY_LABEL = TextColor.SECONDARY
    COLOR_WARNING_SKILLS_MISSING = eveColor.DANGER_RED
    COLOR_WARNING_BACKGROUND_SKILLS_MISSING = eveColor.CHERRY_RED
    OPACITY_ENABLED = 1.0
    OPACITY_DISABLED = 0.6
    OPACITY_WARNING_SKILLS_MISSING = 0.6
    FORM_NAME_INFOMORPHS_AMOUNT = 'infomorphs_amount'
    DIALOG_EXTRACTION_CONFIRMATION = 'MercenaryDenConfirmCargoExtraction'
    UI_POINTER_INVENTORY = 2479

    def __init__(self, controller, should_show_name, *args, **kwargs):
        self._controller = controller
        self.should_show_name = should_show_name
        super(CargoContainer, self).__init__(*args, **kwargs)
        self._construct_content()

    def _construct_content(self):
        self._construct_form()
        self._construct_cargo_name()
        self._construct_cargo_capacity_bar()
        self._construct_cargo_items()
        self._construct_button()
        self._construct_warnings()

    def _construct_form(self):
        self._form_submit_action = FormActionSubmit(label=GetByLabel(self.LABEL_PATH_BUTTON_ALL), hint=GetByLabel(self.LABEL_PATH_BUTTON_TOOLTIP_ALL), func=self._on_form_submit)
        self._form = Form(name='take_cargo_form', actions=[self._form_submit_action])
        self._infomorphs_amount_component = None
        self._infomorphs_amount_input = None

    def _construct_cargo_name(self):
        if self.should_show_name:
            self._name_text = TextBody(name='name_label', parent=self, align=Align.TOTOP, color=self.COLOR_CARGO_NAME_LABEL, maxLines=1, padBottom=self.PADDING_BOTTOM_CARGO_NAME)

    def _construct_cargo_capacity_bar(self):
        capacity_bar_container = Container(name='capacity_bar_container', parent=self, align=Align.TOTOP, height=self.HEIGHT_CARGO_CAPACITY_BAR, padBottom=self.PADDING_BOTTOM_CARGO_CAPACITY_BAR)
        self._capacity_label = TextBody(name='capacity_label', parent=capacity_bar_container, align=Align.CENTER, color=self.COLOR_CARGO_CAPACITY_LABEL)
        self._capacity_bar = Gauge(name='capacity_bar', parent=capacity_bar_container, align=Align.TOTOP, gaugeHeight=self.HEIGHT_CARGO_CAPACITY_BAR, backgroundColor=self.COLOR_CARGO_CAPACITY_BAR_BACKGROUND, color=self.COLOR_CARGO_CAPACITY_BAR)

    def _construct_cargo_items(self):
        self._infomorphs = CargoItem(name='infomorphs_cargo_item', parent=self, align=Align.TOTOP, controller=self._controller, form=self._form, padding=self.PADDING_AROUND_CARGO_ITEM)

    def _construct_button(self):
        self._button_container = ContainerAutoSize(name='button_container', parent=self, align=Align.TOTOP, padTop=self.PADDING_CARGO_ITEMS_TO_BUTTON)
        self._button = Button(name='take_cargo_items_button', parent=self._button_container, align=Align.TOPRIGHT, func=self._on_button_clicked)

    def _construct_warnings(self):
        self._warnings_container = WarningContainer(name='warnings_container', parent=self, align=Align.TOTOP, warningColor=self.COLOR_WARNING_SKILLS_MISSING, warningBackgroundColor=self.COLOR_WARNING_BACKGROUND_SKILLS_MISSING, warningOpacity=self.OPACITY_WARNING_SKILLS_MISSING, textAlignment=Align.TOTOP, pickState=PickState.OFF, display=False, padTop=self.PADDING_BUTTON_TO_WARNING_SKILLS_MISSING)

    def _update_cargo_name(self):
        if self.should_show_name:
            self._name_text.text = GetByLabel(self.LABEL_PATH_CARGO_NAME, typeID=self._controller.type_id)

    def _update_cargo_capacity_bar(self):
        infomorphs_capacity = self._controller.get_infomorph_capacity()
        if infomorphs_capacity <= 0 or self.infomorphs_available <= 0:
            progress = 0.0
        else:
            progress = float(self.infomorphs_available) / infomorphs_capacity
        infomorph_volume = GetVolume(self.infomorphs_type_id)
        current = self.infomorphs_available * infomorph_volume
        capacity = infomorphs_capacity * infomorph_volume
        self._capacity_bar.SetValue(progress)
        volume_info = GetByLabel(self.LABEL_PATH_CARGO_VOLUME, quantity=current, capacity=capacity)
        self._capacity_label.text = GetByLabel(self.LABEL_PATH_CARGO_CAPACITY, capacity=volume_info)

    def _update_cargo_items(self):
        self._infomorphs.load(amount=self.infomorphs_available)

    def _update_form(self):
        self._infomorphs_amount_component = formComponent.Integer(name=self.FORM_NAME_INFOMORPHS_AMOUNT, label='', value=self.infomorphs_available, min_value=0, max_value=self.infomorphs_available)
        self._form.set_components([self._infomorphs_amount_component])
        self._infomorphs_amount_component.on_value_set_by_user.connect(self._on_form_input_changed_by_user)
        if self._infomorphs_amount_input and not self._infomorphs_amount_input.destroyed:
            self._infomorphs_amount_input.Close()
        self._infomorphs_amount_input = formFields.ConstructField(parent=self._infomorphs.input_container, component=self._infomorphs_amount_component, align=Align.CENTERRIGHT, width=self.WIDTH_INPUT_FIELD, padTop=0, padBottom=0)
        if self.is_infomorph_extraction_enabled:
            self._infomorphs_amount_input.edit.state = uiconst.UI_NORMAL
            self._infomorphs_amount_input.edit.opacity = self.OPACITY_ENABLED
        else:
            self._infomorphs_amount_input.edit.state = uiconst.UI_DISABLED
            self._infomorphs_amount_input.edit.opacity = self.OPACITY_DISABLED

    def _update_warnings(self):
        if self.is_warning_enabled:
            self._warnings_container.display = True
            self._warnings_container.text = GetByLabel(self.LABEL_PATH_WARNING_SKILLS_MISSING, typeID=self.infomorphs_type_id)
        else:
            self._warnings_container.display = False
        self._warnings_container.SetSizeAutomatically()

    def _update_button(self):
        self._button.enabled = self.is_infomorph_extraction_enabled and self._controller.is_within_range_for_extraction
        self._button_container.SetSizeAutomatically()

    def _update_button_text(self):
        hint_args = {}
        if self._infomorphs_amount_component.get_value() < self.infomorphs_available:
            label = self.LABEL_PATH_BUTTON_SELECTED
            hint = self.LABEL_PATH_BUTTON_TOOLTIP_SELECTED
        else:
            label = self.LABEL_PATH_BUTTON_ALL
            hint = self.LABEL_PATH_BUTTON_TOOLTIP_ALL
        if not self._button.enabled:
            hint = self.LABEL_PATH_BUTTON_TOOLTIP_DISABLED
            hint_args['distance'] = maxCargoContainerTransferDistance
            hint_args['typeID'] = self.infomorphs_type_id
        self._form_submit_action.label = GetByLabel(label)
        self._form_submit_action.hint = GetByLabel(hint, **hint_args)
        self._button.label = self._form_submit_action.label
        self._button.hint = self._form_submit_action.hint

    def _is_extraction_confirmed(self, quantity_to_extract):
        contents = GetByLabel(self.LABEL_PATH_CARGO_ITEM, quantity=quantity_to_extract, name=type_link(self.infomorphs_type_id))
        return eve.Message(self.DIALOG_EXTRACTION_CONFIRMATION, {'contents': contents}, uiconst.YESNO) == uiconst.ID_YES

    def _on_button_clicked(self, *args, **kwargs):
        self._button.Disable()
        self._button.busy = True
        try:
            self._form_submit_action.execute(self._form)
        finally:
            self._button.Enable()
            self._button.busy = False

    def _on_form_submit(self, *args, **kwargs):
        form_data = self._form.get_value()
        quantity_to_extract = form_data[self.FORM_NAME_INFOMORPHS_AMOUNT]
        if self._is_extraction_confirmed(quantity_to_extract):
            quantity_extracted = self._controller.extract_infomorphs(quantity_to_extract)
            self._on_infomorphs_extracted(quantity_extracted)

    def _show_inventory_pointer(self):
        should_show_inventory_pointer = self._get_show_inventory_pointer_setting()
        if should_show_inventory_pointer:
            sm = ServiceManager.Instance()
            StartTasklet(sm.GetService('uiHighlightingService').highlight_ui_element, self.UI_POINTER_INVENTORY)
            StartTasklet(sm.GetService('neocom').Blink, 'inventory')
            self._set_show_inventory_pointer_setting(False)

    def _get_show_inventory_pointer_setting(self):
        return settings.user.ui.Get('show_inventory_pointer_on_extraction_from_mercenary_den', True)

    def _set_show_inventory_pointer_setting(self, value):
        settings.user.ui.Set('show_inventory_pointer_on_extraction_from_mercenary_den', value)

    def _on_infomorphs_extracted(self, quantity_extracted):
        self.infomorphs_available -= quantity_extracted
        self._show_inventory_pointer()
        self._update_content()
        ShowQuickMessage(GetByLabel(self.LABEL_PATH_TAKE_CARGO_SUCCESS, quantity=quantity_extracted))

    def _update_content(self):
        self._update_cargo_name()
        self._update_cargo_capacity_bar()
        self._update_cargo_items()
        self._update_form()
        self._update_button()
        self._update_button_text()
        self._update_warnings()
        self.SetSizeAutomatically()
        logger.info('UI: Cargo Content: Updated')

    def load_controller(self, controller):
        self._controller = controller
        self.is_warning_enabled = not self._controller.is_cargo_extraction_enabled()
        self.is_infomorph_extraction_enabled = self._controller.is_cargo_extraction_enabled()
        self.infomorphs_available = self._controller.get_infomorphs_collected()
        self.infomorphs_type_id = self._controller.get_infomorph_type_id()
        self._update_content()

    def _on_form_input_changed_by_user(self, *args, **kwargs):
        self._update_button_text()
