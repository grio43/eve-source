#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\fanfare\owned_tickets.py
import eveformat.client
import eveui
import uthread2
import threadutils
from raffles.client import sound, texture
from raffles.client.localization import Text

class OwnedTickets(eveui.Container):
    default_width = 180
    default_opacity = 0

    def __init__(self, controller, **kwargs):
        super(OwnedTickets, self).__init__(**kwargs)
        self._controller = controller
        self._closed = False
        self._tickets = []
        self._layout()
        self._open()

    @threadutils.threaded
    def _open(self):
        uthread2.sleep(1)
        eveui.fade_in(self, duration=0.3)
        self._adjust_height(duration=0.8)
        eveui.fade_in(self._content, duration=0.5)

    def decrypt(self, index):
        if self._closed:
            return
        self._update_ticket_count_label()
        character = self._controller.winning_hash[index]
        for ticket in self._tickets:
            ticket.check_character(index, character)

        if self._controller.highlighted_ticket_count == 0:
            self.close()
        else:
            self._adjust_height(duration=0.5, offset=0.5)

    def _adjust_height(self, duration, offset = 0.0):
        height = min(10, self._controller.highlighted_ticket_count) * (Ticket.default_height + Ticket.default_padBottom) + self._ticket_count_label.height + self._ticket_count_label.padBottom + self._content.padTop + self._content.padBottom
        if self.height == height:
            return
        if height > self.height:
            eveui.play_sound(sound.fanfare_tickets_open)
        else:
            eveui.play_sound(sound.fanfare_tickets_shrink)
        eveui.animate(self, 'height', end_value=height, duration=duration, time_offset=offset)

    def close(self):
        self._closed = True
        eveui.animate(self, 'height', end_value=44, duration=0.3)
        eveui.fade_out(self, duration=0.3)

    def _layout(self):
        self._content = container = eveui.Container(parent=self, padding=(20, 10, 20, 20), clipChildren=True, opacity=0)
        self._ticket_count_label = eveui.EveLabelLarge(parent=container, align=eveui.Align.to_top, padBottom=10, text=self._get_ticket_count_text())
        for ticket_hash in threadutils.be_nice_every(10, self._controller.owned_hashes):
            ticket = Ticket(parent=container, ticket_hash=ticket_hash)
            self._tickets.append(ticket)

        eveui.StretchSpriteVertical(parent=self, align=eveui.Align.to_all, topEdgeSize=20, bottomEdgeSize=20, texturePath=texture.owned_tickets_frame)

    def _get_ticket_count_text(self):
        return eveformat.center(Text.my_tickets(active=self._controller.active_owned_count, owned=self._controller.total_owned_count, total=self._controller.total_ticket_count))

    def _update_ticket_count_label(self):
        self._ticket_count_label.SetText(self._get_ticket_count_text())


class Ticket(eveui.Container):
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_height = 30
    default_padBottom = 6

    def __init__(self, ticket_hash, **kwargs):
        super(Ticket, self).__init__(**kwargs)
        self._highlighted = True
        self._ticket_hash = ticket_hash
        self._characters = []
        self._layout()

    def check_character(self, index, character):
        if not self._highlighted:
            return
        if self._ticket_hash[index] == character:
            self._characters[index].highlight()
        else:
            self._close()

    @threadutils.threaded
    def _close(self):
        self._highlighted = False
        eveui.fade(self, end_value=0.3, duration=0.5, sleep=True)
        eveui.animate(self, 'height', end_value=0, duration=0.5)
        eveui.animate(self, 'padBottom', end_value=0, duration=0.5)
        eveui.fade_out(self, duration=0.3)

    def _layout(self):
        container = eveui.Container(parent=self, align=eveui.Align.center, height=30, width=108)
        eveui.Frame(name='bg', bgParent=container, texturePath=texture.panel_2_corner, cornerSize=9, color=(0.2, 0.2, 0.2, 0.8))
        hash_container = eveui.Container(parent=container, align=eveui.Align.to_all, padding=(2, 3, 2, 3))
        for character in self._ticket_hash:
            ticket_character = TicketCharacter(parent=hash_container, character=character)
            self._characters.append(ticket_character)


class TicketCharacter(eveui.Container):
    default_align = eveui.Align.to_left
    default_width = 24
    default_padLeft = 1
    default_padRight = 1

    def __init__(self, character, **kwargs):
        super(TicketCharacter, self).__init__(**kwargs)
        self._frame = eveui.Frame(bgParent=self, texturePath=texture.panel_2_corner, cornerSize=9, opacity=0.05)
        eveui.Label(parent=self, align=eveui.Align.center, text=character, fontsize=16, fontStyle=eveui.FontStyle.condensed)

    def highlight(self):
        eveui.animate(self._frame, 'color', end_value=(0.12, 0.34, 0.8, 0.5), duration=0.3)
