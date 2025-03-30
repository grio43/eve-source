#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\multi_buy.py
import eveformat
import eveui
from carbonui import TextColor, uiconst
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.uicore import uicore
from raffles.client.localization import Text
from raffles.client.widget.confirm_button import ConfirmButton

class MultiBuy(object):

    def __init__(self, on_buy, raffle = None):
        self._on_buy = on_buy
        self._tooltip = None
        self._open = False
        self.set_raffle(raffle)

    def set_raffle(self, raffle):
        if self._open:
            self.close()
        self._raffle = raffle
        self._ticket_amount = 0

    def open(self, owner):
        if self._open:
            return
        self._open = True
        self._tooltip = eveui.show_persistent_tooltip(owner, load_function=self._load_tooltip)
        self._global_click = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnGlobalMouseDown)
        self._raffle.on_tickets_sold.connect(self._on_tickets_sold)

    def close(self):
        if not self._open:
            return
        self._open = False
        self._raffle.on_tickets_sold.disconnect(self._on_tickets_sold)
        self._tooltip.Close()

    def OnGlobalMouseDown(self, object, *args, **kwargs):
        if object == self._tooltip or object.IsUnder(self._tooltip):
            return True
        self.close()

    def _load_tooltip(self, tooltip_panel, *args):
        tooltip_panel.LoadGeneric2ColumnTemplate()
        tooltip_panel.SetState(eveui.State.normal)
        tooltip_panel.margin = 12
        tooltip_panel.cellSpacing = (12, 4)
        tooltip_panel.AddLabelMedium(text=Text.number_of_tickets(), align=eveui.Align.center_left)
        self.ticket_amount_field = SingleLineEditInteger(OnChange=self._handle_ticket_amount, OnInsert=self._handle_ticket_amount_insert, maxValue=self._raffle.tickets_remaining_count, align=eveui.Align.to_top, setvalue=self._ticket_amount)
        self.ticket_amount_field.SetFocus()
        tooltip_panel.AddCell(self.ticket_amount_field, colSpan=2)
        tooltip_panel.AddSpacer(colSpan=2, width=225, height=10)
        tooltip_panel.AddLabelMedium(text=Text.total_price())
        self.total_price_label = tooltip_panel.AddLabelMedium(align=eveui.Align.top_right, bold=True)
        self.total_price_readable_label = tooltip_panel.AddLabelMedium(align=eveui.Align.top_right, colSpan=2, color=TextColor.SECONDARY)
        self._update_price_label()
        self.buy_button = ConfirmButton(align=eveui.Align.top_right, iconAlign=eveui.Align.to_right_no_push, label=Text.buy_button_label(), on_click=self._handle_buy)
        if self._ticket_amount == 0:
            self.buy_button.Disable()
        tooltip_panel.AddSpacer(colSpan=2, height=10)
        tooltip_panel.AddCell(self.buy_button, colSpan=2)

    def _handle_ticket_amount(self, *args):
        if not self.ticket_amount_field.text:
            self._ticket_amount = 0
        else:
            self._ticket_amount = self.ticket_amount_field.GetValue()
        if self._ticket_amount == 0:
            self.buy_button.Disable()
        else:
            self.buy_button.Enable()
        self._update_price_label()

    def _handle_ticket_amount_insert(self, *args):
        if not self.ticket_amount_field.text:
            return
        if self.ticket_amount_field.GetValue() > self._ticket_amount:
            self.ticket_amount_field.SetValue(self._ticket_amount)

    def _update_price_label(self):
        amount = self._raffle.ticket_price * self._ticket_amount
        self.total_price_label.text = eveformat.isk(amount)
        self.total_price_readable_label.text = eveformat.isk_readable(amount)

    def _on_tickets_sold(self, *args, **kwargs):
        if not self._open:
            return
        self.ticket_amount_field.SetMinValue(1)
        self.ticket_amount_field.SetMaxValue(self._raffle.tickets_remaining_count)
        self.ticket_amount_field.ClampMinMaxValue()

    def _handle_buy(self, *args):
        self.close()
        if self._ticket_amount > 0:
            self._on_buy(self._ticket_amount)
