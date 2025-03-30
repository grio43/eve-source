#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\fanfare\ticket.py
import trinity
import eveui
import threadutils
import uthread2
import math
from raffles.client.widget.sweep_effect import SweepEffect
from raffles.client import texture
from .picker import Picker

class Ticket(eveui.Container):
    default_width = 176
    default_height = 32
    position_offset = [-54,
     -18,
     18,
     54]

    def __init__(self, controller, **kwargs):
        super(Ticket, self).__init__(**kwargs)
        self._controller = controller
        self._slots = []
        self._layout()

    @threadutils.threaded
    def reveal(self):
        uthread2.sleep(1)
        eveui.fade_in(self.picker, duration=0.5, time_offset=0.2)
        offset = 0
        for slot in self._slots:
            offset += 0.1
            eveui.fade_in(slot, duration=0.1, time_offset=offset)

    @threadutils.threaded
    def highlight(self, index):
        self.picker.move_to(self.position_offset[index], 0.3)
        self.picker.lock_in()
        self._slots[index].highlight()

    def decrypt(self, index):
        self._slots[index].decrypt()

    def show_all(self):
        for slot in self._slots:
            slot.decrypt()

    def close(self):
        eveui.fade_out(self, duration=0.5)

    def _layout(self):
        self.picker = Picker(parent=self, align=eveui.Align.center, width=34, height=44, left=self.position_offset[0], opacity=0)
        winning_hash = self._controller.winning_hash
        for i in range(4):
            character = TicketSlot(parent=self, left=self.position_offset[i], opacity=0, character=winning_hash[i])
            self._slots.append(character)


class TicketSlot(eveui.Container):
    default_width = 34
    default_height = 42
    default_align = eveui.Align.center

    def __init__(self, character, **kwargs):
        super(TicketSlot, self).__init__(**kwargs)
        self._character = character
        self._thread = None
        self._layout()

    def highlight(self):
        self._thread = uthread2.start_tasklet(self._highlight_anim)

    def _highlight_anim(self):
        eveui.fade(self.bg, start_value=0.2, end_value=0.7, duration=0.1, loops=4, curve_type=eveui.CurveType.wave, sleep=True)
        eveui.fade(self.bg, start_value=0.2, end_value=0.4, duration=1, loops=-1, curve_type=eveui.CurveType.wave)

    def decrypt(self):
        if self.bg.opacity == 0.5:
            return
        if self._thread:
            self._thread.kill()
        self._thread = uthread2.start_tasklet(self._decrypt_anim)

    def _decrypt_anim(self):
        eveui.stop_animation(self.bg, 'opacity')
        eveui.fade(self.effect, start_value=1.5, end_value=0, duration=1.5)
        eveui.fade(self.label, start_value=0, end_value=2, duration=0.3, time_offset=0.2)
        eveui.fade(self.bg, start_value=0.2, end_value=0.7, duration=0.1, loops=3, curve_type=eveui.CurveType.wave, sleep=True)
        self.effect.opacity = 0
        self.bg.opacity = 0.5
        SweepEffect(parent=self, idx=0, align=eveui.Align.to_all, duration=0.5, rotation=-math.pi * 0.75, opacity=0.5).sweep()

    def _layout(self):
        self.label = eveui.Label(parent=self, align=eveui.Align.center, fontsize=30, fontStyle=eveui.FontStyle.condensed, text=self._character, opacity=0)
        self.bg = eveui.Fill(parent=self, align=eveui.Align.to_all, color=(0.12, 0.34, 0.8, 0.2))
        self.effect = eveui.GradientSprite(parent=self, align=eveui.Align.to_all, alphaData=[(0, 0), (0.5, 0.5), (1, 0)], rgbData=[(0, (0.12, 0.34, 0.8))], rotation=-math.pi * 0.5, padTop=-40, padBottom=-40, opacity=0)
