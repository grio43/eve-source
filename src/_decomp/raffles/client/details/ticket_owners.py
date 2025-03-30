#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\ticket_owners.py
from collections import defaultdict
import eveformat.client
import eveui
import itertoolsext
from carbonui import TextColor
from raffles.client import texture, sound
from raffles.client.localization import Text
from raffles.client.util import character_name
from raffles.client.widget.sweep_effect import SweepEffect

class TicketOwners(eveui.Container):
    default_align = eveui.Align.to_left
    default_width = 190
    default_padRight = 8
    max_shown = 9

    def __init__(self, raffle, **kwargs):
        super(TicketOwners, self).__init__(**kwargs)
        self._raffle = raffle
        self._last_owners = defaultdict(int)
        self._list_items = []
        self._layout()
        self._update_data()
        self._raffle.on_tickets_sold.connect(self._update_data)

    def Close(self):
        self._raffle.on_tickets_sold.disconnect(self._update_data)

    def _update_data(self, *args, **kwargs):
        owners = defaultdict(int)
        for ticket in self._raffle.sold_tickets:
            owners[ticket.owner_id] += 1

        data = sorted(owners.items(), key=lambda owner: owner[1], reverse=True)[:self.max_shown]
        if len(owners) > len(data):
            owned_amount = owners[session.charid]
            if owned_amount and not itertoolsext.first_or_default(data, lambda x: x[0] == session.charid, None):
                data[-2] = (None, 0)
                data[-1] = (session.charid, owned_amount)
        for i in xrange(self.max_shown):
            if i >= len(data):
                self._list_items[i].Hide()
                continue
            owner_id, amount = data[i]
            last_amount = self._last_owners[owner_id]
            purchased_amount = amount - last_amount
            self._list_items[i].update(owner_id, amount, purchased_amount)

        self._title_label.text = eveformat.center(Text.ticket_owners(owners_count=len(owners)))
        self._last_owners = owners

    def _layout(self):
        self._content = container = eveui.Container(parent=self, padding=12, clipChildren=True)
        self._title_label = eveui.EveLabelMediumBold(parent=container, align=eveui.Align.to_top, padTop=10, padBottom=10)
        owner_container = eveui.Container(parent=container)
        for _ in range(self.max_shown):
            owner = TicketOwner(parent=owner_container)
            self._list_items.append(owner)

        eveui.StretchSpriteVertical(parent=self, align=eveui.Align.to_all, topEdgeSize=20, bottomEdgeSize=20, texturePath=texture.owned_tickets_frame)

    def _render_ticket_owner(self):
        return TicketOwner()


class TicketOwner(eveui.Container):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_height = 40
    default_padBottom = 4
    isDragObject = True

    def __init__(self, **kwargs):
        super(TicketOwner, self).__init__(**kwargs)
        self._layout()
        self._owner_id = None
        self.GetDragData = self._portrait.GetDragData
        self.OnClick = self._portrait.OnClick
        self.GetMenu = self._portrait.GetMenu

    def update(self, owner_id, amount, purchased_amount):
        self._sweep_effect.stop()
        if not owner_id:
            self._more_container.state = eveui.State.disabled
            self._active_container.state = eveui.State.hidden
            self.state = eveui.State.disabled
        else:
            self._more_container.state = eveui.State.hidden
            self._active_container.state = eveui.State.disabled
            self.state = eveui.State.normal
            self._portrait.character_id = owner_id
            self._character_name.text = character_name(owner_id)
            self._ticket_label.text = Text.ticket_count(ticket_count=amount)
            if owner_id == session.charid:
                self._owner_fill.opacity = 0.8
            else:
                self._owner_fill.opacity = 0
            if self._owner_id:
                if self._owner_id != owner_id:
                    eveui.fade(self, start_value=0, end_value=1, duration=0.5)
                if purchased_amount:
                    self._sweep_effect.sweep(loop=False)
        self._owner_id = owner_id

    def OnMouseEnter(self, *args):
        eveui.play_sound(sound.card_hover)
        eveui.fade(self._hover_fill, end_value=0.1, duration=0.1)

    def OnMouseExit(self, *args):
        eveui.fade_out(self._hover_fill, duration=0.3)

    def _layout(self):
        self._sweep_effect = SweepEffect(parent=self, align=eveui.Align.to_all, opacity=0.4)
        self._more_container = eveui.Container(parent=self)
        eveui.EveCaptionLarge(parent=self._more_container, align=eveui.Align.center_top, top=-2, text='...', opacity=0.75)
        self._active_container = eveui.Container(parent=self)
        self._hover_fill = eveui.Frame(bgParent=self._active_container, opacity=0, cornerSize=9, texturePath=texture.panel_1_corner)
        self._owner_fill = eveui.Frame(bgParent=self._active_container, color=(0.0, 0.31, 0.4, 0.8), opacity=0, cornerSize=9, texturePath=texture.panel_1_corner)
        container = eveui.Container(parent=self._active_container, padding=4)
        self._portrait = eveui.CharacterPortrait(parent=container, state=eveui.State.disabled, align=eveui.Align.to_left, size=32, padRight=6)
        self._character_name = eveui.EveLabelMedium(parent=container, align=eveui.Align.to_top, maxLines=1)
        self._ticket_label = eveui.EveLabelMedium(parent=container, align=eveui.Align.to_top, maxLines=1, color=TextColor.SECONDARY)
        self._ticket_label.SetRightAlphaFade(114, 40)
