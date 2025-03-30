#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\active_panel.py
import math
import eveui
import threadutils
import uthread2
from raffles import RafflesError
from raffles.client import sound, texture
from raffles.client.localization import Text
from raffles.client.details.ticket import Ticket
from raffles.client.widget.checkbox import Checkbox
from raffles.client.widget.multi_buy import MultiBuy
from raffles.client.widget.error_tooltip import show_error_tooltip
from raffles.client.widget.dotted_progress import DottedProgress
from raffles.client.widget.virtual_list import VirtualList
from .info_panel import InfoPanel
from .tickets_list_item import TicketsListItem
from .ticket import TicketController
from .ticket_owners import TicketOwners

class ActivePanel(eveui.Container):
    default_name = 'activePanel'

    def __init__(self, raffle, **kwargs):
        super(ActivePanel, self).__init__(**kwargs)
        self._raffle = raffle
        self._ticket_controllers = [ TicketController(raffle, index) for index in xrange(raffle.ticket_count) ]
        self._only_available = False
        self._multi_buy = MultiBuy(raffle=self._raffle, on_buy=self._handle_buy)
        self._layout()
        self._update_ticket_labels()
        self._update_list()
        self._raffle.on_tickets_sold.connect(self._on_tickets_sold)

    def Close(self):
        super(ActivePanel, self).Close()
        self._multi_buy.close()
        self._raffle.on_tickets_sold.disconnect(self._on_tickets_sold)

    def _on_tickets_sold(self, *args, **kwargs):
        if not self._raffle.sold_tickets:
            return
        self._update_ticket_labels()
        for ticket in self._raffle.sold_tickets:
            if self._ticket_controllers[ticket.number].owner_id == ticket.owner_id:
                continue
            if ticket.owner_id == session.charid:
                sound.play(sound.ticket_sold)
            else:
                sound.play(sound.ticket_sold_to_other)
            self._ticket_controllers[ticket.number].owner_id = ticket.owner_id

    def _update_ticket_labels(self):
        self.tickets_owned_label.text = Text.owned_tickets(owned_ticket_count=self._raffle.tickets_owned_count)
        self.tickets_available_label.text = Text.available_tickets(remaining_ticket_count=self._raffle.tickets_remaining_count)

    def _update_ticket_visible(self, ticket):
        if self._only_available and ticket.controller.owner_id and ticket.controller.owner_id != session.charid and not ticket.controller.error:
            ticket.anim_hide()
        else:
            ticket.anim_show()

    def _toggle_only_available(self, *args):
        self._only_available = not self._only_available
        self._update_list()

    @threadutils.threaded
    def _update_list(self):
        if self._only_available:
            ticket_controllers = [ ticket for ticket in self._ticket_controllers if not ticket.owner_id ]
        else:
            ticket_controllers = self._ticket_controllers
        if self._should_update_list(ticket_controllers):
            for ticket_list_item in self._ticket_list.items:
                ticket_list_item.controllers = ticket_controllers

            self._ticket_list.data = range(int(math.ceil(float(len(ticket_controllers)) / 4)))

    def _should_update_list(self, ticket_controllers):
        if not self._ticket_list.data:
            return True
        if len(ticket_controllers) != len(self._ticket_list.data):
            return True
        return False

    def _handle_buy(self, amount):
        self._multi_buy_button.Disable()
        self._multi_buy_button.sr.label.state = eveui.State.hidden
        self._multi_buy_progress.Show()
        try:
            self._raffle.buy_random_tickets(amount)
        except RafflesError as error:
            show_error_tooltip(self._multi_buy_button, error)
        finally:
            self._multi_buy_progress.Hide()
            self._multi_buy_button.sr.label.state = eveui.State.disabled
            self._multi_buy_button.Enable()

    def _layout(self):
        InfoPanel(parent=self, raffle=self._raffle)
        main_container = eveui.Container(name='mainContainer', parent=self)
        TicketOwners(parent=main_container, raffle=self._raffle)
        if self._raffle.is_expired:
            self._construct_expired(main_container)
        content_container = eveui.Container(name='contentContainer', parent=main_container, padding=16)
        self._construct_frame(main_container)
        self._construct_top(content_container)
        self._construct_tickets(content_container)

    def _construct_expired(self, parent):
        container = eveui.Container(parent=parent)
        eveui.EveCaptionSmall(parent=container, align=eveui.Align.center, text=Text.card_expired().upper())
        eveui.Fill(parent=container, color=(0, 0, 0, 0.5), state=eveui.State.normal)

    def _construct_frame(self, parent):
        eveui.StretchSpriteVertical(parent=parent, state=eveui.State.disabled, align=eveui.Align.to_all, texturePath=texture.banner_frame, topEdgeSize=20, bottomEdgeSize=20, color=(0, 0, 0, 0.5), padding=(0, 4, 0, 4))
        top_container = eveui.Container(parent=parent, state=eveui.State.disabled, align=eveui.Align.to_top_no_push, height=5, opacity=1.5)
        eveui.StretchSpriteHorizontal(parent=top_container, align=eveui.Align.to_all, texturePath=texture.content_frame, rightEdgeSize=50, leftEdgeSize=5)
        eveui.StretchSpriteHorizontal(parent=top_container, align=eveui.Align.center_bottom, texturePath=texture.content_frame_middle, width=252, height=4, rightEdgeSize=5, leftEdgeSize=5)
        bot_container = eveui.Transform(parent=parent, state=eveui.State.disabled, align=eveui.Align.to_bottom_no_push, height=5, rotation=math.pi, opacity=1.5, top=1)
        eveui.StretchSpriteHorizontal(parent=bot_container, align=eveui.Align.to_all, texturePath=texture.content_frame, rightEdgeSize=5, leftEdgeSize=5)
        eveui.StretchSpriteHorizontal(parent=bot_container, align=eveui.Align.center_bottom, texturePath=texture.content_frame_middle, width=252, height=4, rightEdgeSize=5, leftEdgeSize=5)

    def _construct_top(self, parent):
        container = eveui.Container(parent=parent, align=eveui.Align.to_top, height=28, padBottom=12)
        left_container = eveui.Container(parent=container, align=eveui.Align.to_left_prop, width=0.5, padRight=16)
        right_container = eveui.Container(parent=container, padLeft=16)
        self.onlyAvailableCheckbox = Checkbox(parent=left_container, align=eveui.Align.to_left, width=200, checked=self._only_available, callback=self._toggle_only_available, text=Text.show_only_available())
        self._multi_buy_button = eveui.Button(parent=right_container, align=eveui.Align.to_right, label=Text.multi_buy(), func=self._multi_buy.open)
        self._multi_buy_button.sr.label.state = eveui.State.disabled
        self._multi_buy_progress = DottedProgress(parent=self._multi_buy_button, align=eveui.Align.center, dot_size=4)
        eveui.Line(parent=container, align=eveui.Align.center, height=18, width=1)
        self.tickets_available_label = eveui.EveLabelMedium(parent=left_container, align=eveui.Align.center_right)
        eveui.Sprite(parent=right_container, align=eveui.Align.center_left, height=10, width=10, texturePath=texture.tickets_icon)
        self.tickets_owned_label = eveui.EveLabelMedium(parent=right_container, align=eveui.Align.center_left, left=16)

    def _construct_tickets(self, parent):
        self._ticket_list = VirtualList(parent=parent, align=eveui.Align.to_all, pushContent=False, render_item=self._render_list_item)

    def _render_list_item(self):
        return TicketsListItem(ticket_controllers=self._ticket_controllers)
