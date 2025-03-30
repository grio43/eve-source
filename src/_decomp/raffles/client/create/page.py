#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\create\page.py
from carbonui import TextColor
from eve.client.script.ui.control.moreIcon import DescriptionIcon
import eveformat.client
import eveui
import localization
from raffles.common.const import RAFFLE_TAX_PERCENTAGE, RAFFLE_DURATION, MAX_TOTAL_PRICE, MIN_TOTAL_PRICE
from raffles.client.localization import Text
from raffles.client.widget.checkbox import Checkbox
from raffles.client.widget.confirm_button import ConfirmButton
from raffles.client import texture
from raffles.client.util import get_item_name, get_market_estimate_text
from .drag_drop_area import DragDropArea
from .tokens import Tokens
from .statistics import Statistics
from .label_value import LabelValue
from .result import CreateResult
from .controller import CreationStatus

class CreatePage(eveui.Container):
    default_name = 'RafflesCreatePage'

    def __init__(self, window_controller, background_layer, **kwargs):
        self._background_layer = background_layer
        self._navigation = window_controller.navigation_controller
        self._controller = window_controller.create_page_controller
        self.create_button = None
        super(CreatePage, self).__init__(**kwargs)
        if self._controller.status in (CreationStatus.success, CreationStatus.failure):
            self._controller.clear()
        self._layout()
        if self._controller.item:
            self._on_item_changed()
        self._navigation.current_page_title = Text.page_title_create()
        self._controller.on_item_changed.connect(self._on_item_changed)
        self._controller.on_price_changed.connect(self._on_price_changed)
        self._controller.on_token_changed.connect(self._on_token_changed)

    def Close(self):
        super(CreatePage, self).Close()
        self._controller.on_item_changed.disconnect(self._on_item_changed)
        self._controller.on_price_changed.disconnect(self._on_price_changed)
        self._controller.on_token_changed.disconnect(self._on_token_changed)

    def _on_item_changed(self):
        self.content_container.Flush()
        if not self._controller.item:
            self.no_item_label.opacity = 1
            return
        self.no_item_label.opacity = 0
        self._fade(self.content_container)
        if self._controller.status == CreationStatus.none:
            self._construct_item_info()
            self._construct_form()
            self._on_price_changed()
            self._on_token_changed()
        else:
            self._construct_item_info()
            self._construct_create()

    def _on_price_changed(self):
        self.ticket_count_label.text = self._controller.ticket_count
        self.ticket_price_label.text = eveformat.isk(self._controller.ticket_price, fraction=True)
        self.ticket_price_label.hint = eveformat.isk_readable(self._controller.ticket_price)
        self.total_price_label.text = eveformat.isk(self._controller.total_price, fraction=True)
        self.total_price_label.hint = eveformat.isk_readable(self._controller.total_price)
        self.sales_tax_label.text = eveformat.isk(self._controller.sales_tax, fraction=True)
        self.sales_tax_label.hint = eveformat.isk_readable(self._controller.sales_tax)
        self.earnings_label.text = eveformat.isk(self._controller.earnings, fraction=True)
        self.earnings_label.hint = eveformat.isk_readable(self._controller.earnings)
        self._update_low_price_warning()

    def _update_low_price_warning(self):
        if self._controller.is_low_price:
            state = eveui.State.normal
        else:
            state = eveui.State.hidden
        self._low_price_icon.state = state

    def _on_token_changed(self):
        if not self.create_button:
            return
        if self._controller.enable_create_button:
            self.create_button.Enable()
        else:
            self.create_button.Disable()

    def _handle_ticket_count(self, combo, key, value):
        self._controller.ticket_count = value
        self.total_price_field.SetValue(self._controller.total_price, docallback=False)

    def _handle_is_private(self, checkbox):
        self._controller.is_private = checkbox.checked

    def _handle_total_price(self, *args):
        if not self.total_price_field.text:
            return
        self._controller.total_price = self.total_price_field.GetValue()

    def _handle_total_price_scroll(self, val):
        if val > 0:
            self._controller.ticket_price += 1
        else:
            self._controller.ticket_price -= 1
        self._update_total_price_field()

    def _focus_lost_total_price(self, *args):
        self._update_total_price_field()

    def _update_total_price_field(self, *args):
        if self.total_price_field.GetValue() != self._controller.total_price:
            self.total_price_field.SetValue(self._controller.total_price)

    def _handle_create(self, *args):
        if not self._controller.enable_create_button:
            return
        self.form_container.Disable()
        eveui.fade_out(self.form_container, duration=0.3)
        self._construct_create()
        self._controller.create()

    def _handle_clear(self, *args):
        self._controller.clear()

    def _layout(self):
        drag_drop_cont = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top)
        self.drag_drop_area = DragDropArea(parent=drag_drop_cont, align=eveui.Align.center, controller=self._controller)
        self.no_item_label = eveui.EveCaptionMedium(name='noItem', parent=self, align=eveui.Align.center, text=Text.missing_item())
        self.content_container = eveui.Container(parent=self, name='content_container')
        eveui.Sprite(parent=self._background_layer, align=eveui.Align.center_top, texturePath=texture.background_triangles, width=1024, height=716, opacity=0.2)

    def _construct_item_info(self):
        container = eveui.Container(name='item_info_container', parent=self.content_container, align=eveui.Align.to_top, height=89, padBottom=24, padTop=24)
        eveui.EveCaptionMedium(parent=container, align=eveui.Align.to_top, text=eveformat.center(get_item_name(self._controller.type_id, item_id=self._controller.item_id)))
        eveui.EveLabelMedium(parent=container, align=eveui.Align.to_top, text=eveformat.center(get_market_estimate_text(self._controller.type_id, self._controller.item_id)), padBottom=16)
        eveui.EveLabelMedium(parent=container, align=eveui.Align.to_top, text=eveformat.center(eveformat.solar_system_with_security_and_jumps(self._controller.solar_system_id)))
        eveui.EveLabelMedium(parent=container, align=eveui.Align.to_top, text=eveformat.center(cfg.evelocations.Get(self._controller.location_id).locationName))

    def _construct_form(self):
        self.form_container = eveui.Container(name='form_container', parent=self.content_container)
        button_container = eveui.Container(name='ButtonContainer', parent=self.form_container, align=eveui.Align.to_bottom, height=28, padTop=12)
        self.create_button = ConfirmButton(parent=button_container, align=eveui.Align.center_right, iconAlign=eveui.Align.to_right_no_push, label=Text.create_button(), on_click=self._handle_create)
        eveui.Button(parent=button_container, align=eveui.Align.center_left, label=Text.clear_button(), func=self._handle_clear)
        container = eveui.Container(parent=self.form_container, padding=12)
        eveui.Frame(bgParent=container, padding=-12, texturePath=texture.panel_1_corner, color=(0, 0, 0, 0.25))
        self._construct_input(container)
        self._construct_details(container)
        Statistics(controller=self._controller, parent=container, align=eveui.Align.center_right, height=176, width=300)

    def _construct_input(self, parent):
        container = eveui.Container(parent=parent, align=eveui.Align.center_left, height=210, width=300)
        self.total_price_field = TotalPriceField(parent=container, align=eveui.Align.to_top, label=Text.total_price(), on_scroll=self._handle_total_price_scroll, OnChange=self._handle_total_price, OnFocusLost=self._focus_lost_total_price, inputType='ISK', minValue=MIN_TOTAL_PRICE, maxValue=MAX_TOTAL_PRICE, padTop=16, padBottom=24)
        self.total_price_field.SetValue(self._controller.total_price, docallback=False)
        self._low_price_icon = eveui.Sprite(parent=self.total_price_field, align=eveui.Align.center_right, state=eveui.State.hidden, pos=(24, 0, 16, 16), texturePath=texture.exclamation_icon, color=TextColor.WARNING, hint=Text.low_price_warning())
        eveui.Combo(parent=container, align=eveui.Align.to_top, label=Text.number_of_tickets(), options=self._controller.ticket_options, callback=self._handle_ticket_count, select=self._controller.ticket_count)
        Tokens(controller=self._controller, parent=container, align=eveui.Align.to_top, padTop=16)
        DescriptionIcon(parent=container, align=eveui.Align.bottom_right, hint=Text.private_raffle_tooltip())
        Checkbox(parent=container, align=eveui.Align.to_bottom, height=27, text=Text.private_raffle(), checked=self._controller.is_private, callback=self._handle_is_private)

    def _construct_details(self, parent):
        center_cont = eveui.Container(name='CenterContainer', parent=parent, align=eveui.Align.center, height=194, width=300, top=8)
        LabelValue(parent=center_cont, align=eveui.Align.to_top, label=Text.duration(), value=localization.formatters.FormatTimeIntervalWritten(RAFFLE_DURATION, showFrom='day', showTo='hour'), padBottom=14)
        ticket_count = LabelValue(parent=center_cont, align=eveui.Align.to_top, label=Text.number_of_tickets())
        self.ticket_count_label = ticket_count.value
        ticket_price = LabelValue(parent=center_cont, align=eveui.Align.to_top, label=Text.ticket_price(), padBottom=14)
        self.ticket_price_label = ticket_price.value
        self.ticket_price_label.state = eveui.State.normal
        total_price = LabelValue(parent=center_cont, align=eveui.Align.to_top, label=Text.total_price())
        self.total_price_label = total_price.value
        self.total_price_label.state = eveui.State.normal
        sales_tax = LabelValue(parent=center_cont, align=eveui.Align.to_top, label=Text.sales_tax(percentage=u'{:.0%}'.format(RAFFLE_TAX_PERCENTAGE)))
        self.sales_tax_label = sales_tax.value
        self.sales_tax_label.state = eveui.State.normal
        earnings = LabelValue(parent=center_cont, align=eveui.Align.to_top, label=Text.earnings())
        self.earnings_label = earnings.value
        self.earnings_label.state = eveui.State.normal
        self.earnings_label.SetTextColor(TextColor.SUCCESS)
        icon_container = eveui.Container(parent=center_cont, align=eveui.Align.to_bottom, height=27, padTop=12)
        DescriptionIcon(parent=icon_container, align=eveui.Align.bottom_right, hint=Text.create_information_tooltip())

    def _construct_create(self):
        CreateResult(parent=self.content_container, controller=self._controller, navigation=self._navigation)

    def _fade(self, container):
        eveui.fade(container, start_value=0, end_value=1, duration=1)


class TotalPriceField(eveui.SingleLineEditInteger):
    default_dataType = long

    def __init__(self, on_scroll, **kwargs):
        super(TotalPriceField, self).__init__(**kwargs)
        self._on_scroll = on_scroll

    def ChangeNumericValue(self, val):
        super(TotalPriceField, self).ChangeNumericValue(val)
        self._on_scroll(val)
