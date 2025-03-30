#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\fanfare\slot_options.py
import eveui
import threadutils
import uthread2
import random
from raffles.client import sound
from .picker import Picker

class SlotOptions(eveui.Container):
    default_state = eveui.State.normal
    default_width = 243
    default_height = 32
    bg_color_off = (0, 0, 0, 0.5)
    bg_color_on = (0.12, 0.34, 0.8, 0.2)

    def __init__(self, controller, **kwargs):
        super(SlotOptions, self).__init__(**kwargs)
        self._controller = controller
        self._selected_slot = None
        self.slots = []
        self.random_move_count = [0,
         1,
         2,
         2]
        random.shuffle(self.random_move_count)
        self._layout()

    def close(self):
        eveui.fade_out(self, duration=0.5)

    def unselect(self):
        eveui.animate(self.slots[self._selected_slot].fill, 'color', end_value=self.bg_color_off, duration=0.2)
        eveui.fade_out(self.slots[self._selected_slot].label_container, duration=0.2)
        self.slots[self._selected_slot].label.opacity = 1
        self.picker.unlock()

    def show_options(self, hash_index):
        options, highlighted_indexes = self._controller.get_slot_options(hash_index)
        eveui.play_sound(sound.fanfare_show_options, time_offset=0.5)
        eveui.fade_in(self.picker, duration=0.5, time_offset=0.5)
        self.picker.move_to(self.slots[-1].left, 0.3)
        for index, slot in enumerate(self.slots):
            slot.label.text = options[index]
            if index in highlighted_indexes:
                slot.label.SetTextColor((1, 1, 1, 1.0))
            else:
                slot.label.SetTextColor((0.4, 0.6, 0.8, 1.0))
            self._turn_on_slot(index)

        self.picker.move_to(self.slots[0].left, 0.6)
        self._highlight_characters()
        uthread2.sleep(0.2)
        winning_character = self._controller.winning_hash[hash_index]
        for index, option in enumerate(options):
            if option == winning_character:
                self._selected_slot = index
                break

        self._random_movement(hash_index)
        self._move_to_slot(self._selected_slot)
        eveui.play_sound(sound.fanfare_lock_in_slot)
        eveui.fade(self.slots[self._selected_slot].fill, start_value=0.2, end_value=0.7, duration=0.1, loops=3, curve_type=eveui.CurveType.wave)
        self.slots[self._selected_slot].label.opacity = 3
        self.picker.lock_in()
        for index in range(len(self.slots)):
            if index == self._selected_slot:
                continue
            self._turn_off_slot(index)

    def _random_movement(self, hash_index):
        if self._controller.highlighted_ticket_count == 0:
            return
        indexes = range(len(self.slots))
        indexes.remove(self._selected_slot)
        random.shuffle(indexes)
        for index in range(self.random_move_count[hash_index]):
            self._move_to_slot(indexes[index])

    def _move_to_slot(self, index):
        eveui.play_sound(sound.fanfare_move_to_slot)
        self.picker.move_to(self.slots[index].left, duration=0.35)
        uthread2.sleep(0.3)

    @threadutils.threaded
    def _highlight_characters(self):
        for index, slot in enumerate(self.slots):
            eveui.fade(slot.label_container, start_value=3, end_value=1, duration=0.35)
            uthread2.sleep(0.07)

    def _turn_on_slot(self, index):
        offset = abs(index - len(self.slots)) * 0.075
        slot = self.slots[index]
        eveui.animate(slot.fill, 'color', self.bg_color_on, duration=0.1, time_offset=offset)
        eveui.fade(slot.label_container, duration=0.2, time_offset=offset)

    def _turn_off_slot(self, index):
        offset = abs(index - self._selected_slot) * 0.1
        slot = self.slots[index]
        eveui.animate(slot.fill, 'color', end_value=self.bg_color_off, duration=0.3, time_offset=offset)
        eveui.fade_out(slot.label_container, duration=0.3, time_offset=offset)

    def _layout(self):
        self.picker = Picker(parent=self, align=eveui.Align.center_left, height=34, width=26, opacity=0)
        left = 0
        for i in range(9):
            slot = eveui.Container(parent=self, align=eveui.Align.center_left, width=26, height=32, left=left)
            slot.fill = eveui.Fill(bgParent=slot, opacity=0)
            slot.label_container = eveui.Container(parent=slot, opacity=0)
            slot.label = eveui.Label(parent=slot.label_container, align=eveui.Align.center, fontsize=18, opacity=1, fontStyle=eveui.FontStyle.condensed)
            self.slots.append(slot)
            left += slot.width + 1
