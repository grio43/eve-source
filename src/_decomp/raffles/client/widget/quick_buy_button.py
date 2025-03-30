#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\quick_buy_button.py
import eveui
from carbonui import TextColor
from raffles.client import texture
from raffles.client.localization import Text
from raffles.client.widget.confirm_button import ConfirmButton
from raffles.client.widget.error_tooltip import show_error_tooltip
from raffles.client.widget.dotted_progress import DottedProgress

class QuickBuyButton(ConfirmButton):
    default_icon_color = (1.0, 1.0, 1.0)

    def __init__(self, raffle = None, icon_color = None, **kwargs):
        self._raffle = None
        self._card_hovered = False
        self._is_buying = False
        self._icon_color = icon_color or self.default_icon_color
        super(QuickBuyButton, self).__init__(on_click=self._buy, **kwargs)
        self.set_raffle(raffle)

    def set_raffle(self, raffle):
        self._raffle = raffle
        self.update_state()

    def update_state(self):
        if not self._raffle:
            if self._in_confirm_state:
                self._exit_confirm_state(confirmed=False)
            return
        if self._raffle.is_ticket_owner:
            self.text_label.text = self._raffle.tickets_owned_count
            self.button_icon.texturePath = texture.tickets_icon
            self.button_icon.height = 10
            self.button_icon.width = 10
            pad = (self.text_label.GetAbsoluteSize()[0] + 14) / 4 + 2
            self.text_label.left = -pad
            self.button_icon.left = pad
        else:
            self.text_label.text = ''
            self.button_icon.height = 14
            self.button_icon.width = 14
            self.button_icon.left = 0
            self.button_icon.texturePath = texture.isk_16
        self._update()

    def tickets_sold(self):
        self.update_state()

    def card_enter(self):
        self._card_hovered = True
        self._update()

    def card_exit(self):
        self._card_hovered = False
        self._update()

    def OnMouseEnter(self, *args):
        if self._raffle and self._raffle.is_finished:
            return
        super(QuickBuyButton, self).OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        if self._raffle and self._raffle.is_finished:
            return
        super(QuickBuyButton, self).OnMouseExit(*args)

    def OnMouseDown(self, *args):
        if self._is_buying or not self._raffle or self._raffle.is_finished:
            return
        super(QuickBuyButton, self).OnMouseDown(*args)

    def OnMouseUp(self, *args):
        if self._raffle and self._raffle.is_finished:
            return
        super(QuickBuyButton, self).OnMouseUp(*args)

    def OnClick(self, *args):
        if not self._raffle or self._raffle.is_finished or self._raffle.is_sold_out or self._is_buying:
            return
        super(QuickBuyButton, self).OnClick(*args)

    def _buy(self, *args):
        self._is_buying = True
        self.progress.Show()
        self.label_container.opacity = 0
        self._update()
        try:
            self._raffle.buy_random_tickets(1)
        except Exception as error:
            self.SetHint(None)
            self.error_frame.opacity = 0.5
            show_error_tooltip(self, error, on_finished=self._finished_buying)
        else:
            self._finished_buying()

    def _finished_buying(self):
        self._is_buying = False
        self.error_frame.opacity = 0
        eveui.fade_in(self.label_container, duration=0.1)
        self.progress.Hide()
        self._update()

    def _on_exit_confirm_state(self):
        if self._raffle:
            self._update()

    def _update(self):
        if self._raffle is None or self._raffle.winner_id and not self._raffle.is_winner_unseen:
            self.state = eveui.State.hidden
            return
        self._update_hint()
        self.state = eveui.State.normal
        if self._not_hovering_check():
            eveui.fade_out(self.content_container, duration=0.1)
            return
        if self._raffle.is_expired and not self._raffle.is_ticket_owner:
            eveui.fade_out(self.content_container, duration=0.1)
            return
        if self._raffle.is_winner_unseen:
            self.button_icon.color = (0, 0, 0)
            self.text_label.SetTextColor((0, 0, 0))
        else:
            self.button_icon.color = (1, 1, 1)
            self.text_label.SetTextColor((1, 1, 1))
        eveui.fade_in(self.content_container, duration=0.1)
        self._update_background()

    def _update_background(self):
        if self._raffle.is_finished or not self._card_hovered:
            eveui.fade_out(self.background_frame, duration=0.1)
        else:
            eveui.fade_in(self.background_frame, duration=0.1)

    def _update_hint(self):
        if self._raffle.is_finished:
            self.SetHint(Text.owned_tickets(owned_ticket_count=self._raffle.tickets_owned_count))
        elif self._raffle.is_ticket_owner:
            self.SetHint(u'{}\n{}'.format(Text.owned_tickets(owned_ticket_count=self._raffle.tickets_owned_count), Text.quick_buy_button_hint(price=self._raffle.ticket_price)))
        else:
            self.SetHint(Text.quick_buy_button_hint(price=self._raffle.ticket_price))

    def _not_hovering_check(self):
        return not self._card_hovered and not self._raffle.is_ticket_owner and not self._is_buying

    def _layout(self):
        self.error_frame = eveui.Frame(parent=self, texturePath=texture.button_gradient, cornerSize=9, color=TextColor.WARNING, opacity=0)
        self.progress = DottedProgress(parent=self, align=eveui.Align.center, dot_size=4)
        super(QuickBuyButton, self)._layout()
        self.content_container = eveui.Container(name='contentContainer', parent=self, opacity=0)
        self.label_container.SetParent(self.content_container)
        self.background_frame.SetParent(self.content_container)
        self.background_frame.opacity = 0
        self.button_icon = eveui.Sprite(parent=self.label_container, align=eveui.Align.center, texturePath=texture.isk_16, width=14, height=14)
        self.text_label = eveui.EveLabelLargeBold(parent=self.label_container, align=eveui.Align.center, color=self.text_color)
