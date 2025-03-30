#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\audio.py
from carbon.client.script.environment.AudioUtil import PlaySound
import carbonui.uiconst
import enum
import uthread2

def play_sound(sound_path, time_offset = None):
    if time_offset is not None:

        def sleeper():
            uthread2.sleep(time_offset)
            PlaySound(sound_path)

        uthread2.start_tasklet(sleeper)
    else:
        PlaySound(sound_path)


class Sound(str, enum.Enum):

    def play(self):
        play_sound(self.value)

    button_hover = carbonui.uiconst.SOUND_BUTTON_HOVER
    button_click = carbonui.uiconst.SOUND_BUTTON_CLICK
    entry_hover = carbonui.uiconst.SOUND_ENTRY_HOVER
    entry_select = carbonui.uiconst.SOUND_ENTRY_SELECT
    text_field_hover = carbonui.uiconst.SOUND_TEXTEDIT_HOVER
    value_change_tick = carbonui.uiconst.SOUND_VALUECHANGE_TICK
    expand = carbonui.uiconst.SOUND_EXPAND
    collapse = carbonui.uiconst.SOUND_COLLAPSE
    close = carbonui.uiconst.SOUND_CLOSE
    add_or_use = carbonui.uiconst.SOUND_ADD_OR_USE
    remove = carbonui.uiconst.SOUND_REMOVE
    set_selected = carbonui.uiconst.SOUND_SETSELECTED
    set_deselected = carbonui.uiconst.SOUND_SETDESELECTED
    drag_drop_loop = carbonui.uiconst.SOUND_DRAGDROPLOOP
    isk_received = carbonui.uiconst.SOUND_ISK_RECEIVED
    isk_paid = carbonui.uiconst.SOUND_ISK_PAID
