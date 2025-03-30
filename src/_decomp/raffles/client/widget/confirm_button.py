#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\confirm_button.py
import uuid
import eveui
import threadutils
import uthread2
from eve.client.script.ui import eveColor
from raffles.client import sound, texture
from raffles.client.localization import Text
from raffles.client.tutorial import have_learned_to_confirm, hide_confirm_button_hint, set_confirm_button_learned, show_confirm_button_hint

class ConfirmButton(eveui.Container):
    default_state = eveui.State.normal
    default_width = 70
    default_height = 28
    default_clipChildren = True
    fill_default_color = eveColor.PRIMARY_BLUE
    fill_hover_color = eveColor.CRYO_BLUE
    fill_down_color = eveColor.PRIMARY_BLUE
    default_text_color = (1.0, 1.0, 1.0)

    def __init__(self, label = '', on_click = None, text_color = None, **kwargs):
        super(ConfirmButton, self).__init__(**kwargs)
        self.name = 'confirm_button_{}'.format(uuid.uuid4())
        self._label = label
        self.on_click = on_click
        self._hovered = False
        self._in_confirm_state = False
        self._confirm_state_ready = False
        self._confirm_thread = None
        self._text_color = text_color or self.default_text_color
        self._layout()

    @property
    def text_color(self):
        return self._text_color

    @text_color.setter
    def text_color(self, color):
        self._text_color = color
        self.text_label.SetRGBA(*self.text_color)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        if label == self._label:
            return
        self._label = label
        self.text_label.text = label

    def OnClick(self, *args):
        if not self._in_confirm_state:
            self._confirm_thread = uthread2.start_tasklet(self._enter_confirm_state)
        elif self._confirm_state_ready:
            self._exit_confirm_state(True)
            self.on_click(self)

    def OnMouseEnter(self, *args):
        eveui.play_sound(sound.button_hover)
        self._hovered = True
        self.background_frame.color = self.fill_hover_color

    def OnMouseExit(self, *args):
        self._hovered = False
        self.background_frame.color = self.fill_default_color

    def OnMouseDown(self, *args):
        self.background_frame.color = self.fill_down_color

    def OnMouseUp(self, *args):
        if self._hovered:
            self.background_frame.color = self.fill_hover_color
        else:
            self.background_frame.color = self.fill_default_color

    def Enable(self, *args):
        super(ConfirmButton, self).Enable(*args)
        self.opacity = 1

    def Disable(self, *args):
        super(ConfirmButton, self).Disable(*args)
        self.opacity = 0.5

    def _enter_confirm_state(self):
        eveui.play_sound(sound.confirm_button_on)
        self._in_confirm_state = True
        self._confirm_state_ready = False
        self.confirm_container.align = eveui.Align.to_left_prop
        duration = 0.4
        eveui.fade_in(self.confirm_label, duration=duration, time_offset=0.1)
        eveui.animate(self.confirm_container, 'width', start_value=0.0, end_value=1.0, duration=duration, sleep=True)
        self._confirm_state_ready = True
        uthread2.sleep(1.5)
        if not have_learned_to_confirm():
            show_confirm_button_hint(self.name)
            uthread2.sleep(8.0)
        else:
            uthread2.sleep(1.0)
        self._confirm_thread = None
        self._exit_confirm_state(confirmed=False)

    @threadutils.threaded
    def _exit_confirm_state(self, confirmed):
        if self._confirm_thread:
            self._confirm_thread.kill()
            self._confirm_thread = None
        if confirmed:
            eveui.play_sound(sound.confirm_button_confirmed)
            hide_confirm_button_hint(self.name)
            set_confirm_button_learned()
            self.confirm_container.align = eveui.Align.to_right_prop
        else:
            eveui.play_sound(sound.confirm_button_off)
            self.confirm_container.align = eveui.Align.to_left_prop
        self._in_confirm_state = False
        self._confirm_state_ready = False
        eveui.fade_out(self.confirm_label, duration=0.1)
        eveui.animate(self.confirm_container, 'width', end_value=0.0, duration=0.3, sleep=True)
        self._on_exit_confirm_state()

    def _on_exit_confirm_state(self):
        pass

    def _layout(self):
        self._construct_confirm()
        self.label_container = eveui.Container(parent=self)
        self.text_label = eveui.EveLabelMedium(parent=self.label_container, align=eveui.Align.center, color=self.text_color, text=self.label)
        self.background_frame = eveui.Frame(parent=self, texturePath=texture.button_gradient, cornerSize=9, color=self.fill_default_color)

    def _construct_confirm(self):
        self.confirm_container = eveui.Container(parent=self, align=eveui.Align.to_left_prop, width=0)
        self.confirm_label = eveui.EveHeaderMedium(parent=self.confirm_container, align=eveui.Align.center, text=Text.confirm_purchase(), maxWidth=self.default_width - 8, maxLines=1, opacity=0.0, color=(0, 0, 0))
        eveui.Frame(parent=self.confirm_container, texturePath=texture.button_gradient, cornerSize=9, color=(0.9, 0.9, 0.9))
