#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\button\icon.py
import proper
from eveui import Container, GlowSprite
from eveui.animation import animate
from eveui.audio import Sound
from eveui.compatibility import CarbonEventHandler
from eveui.constants import Align, State
from eveui.mouse import Mouse
from eveui.primitive.sprite import Sprite

def optional(value, default):
    if value is not None:
        return value
    return default


class ButtonIcon(proper.Observable, CarbonEventHandler, Container):

    def __init__(self, texture_path = None, size = 16, on_click = None, color = None, glow_amount_idle = None, glow_amount_hover = None, glow_amount_click = None, glow_amount_disabled = None, opacity_disabled = None, opacity_enabled = None, **kwargs):
        self._texture_path = texture_path
        self._on_click = on_click
        self._color = optional(color, (1.0, 1.0, 1.0))
        self._glow_amount_idle = optional(glow_amount_idle, 0.0)
        self._glow_amount_hover = optional(glow_amount_hover, 0.5)
        self._glow_amount_click = optional(glow_amount_click, 1.0)
        self._glow_amount_disabled = optional(glow_amount_disabled, 0.0)
        self._opacity_disabled = optional(opacity_disabled, 0.4)
        self._opacity_enabled = optional(opacity_enabled, 1.0)
        kwargs.setdefault('state', State.normal)
        kwargs['width'] = size
        kwargs['height'] = size
        super(ButtonIcon, self).__init__(**kwargs)
        self.__layout()

    @proper.ty(default=True)
    def enabled(self):
        pass

    @proper.ty(default=False)
    def hovered(self):
        pass

    @property
    def size(self):
        return max(self.width, self.height)

    @size.setter
    def size(self, size):
        self.width = size
        self.height = size

    @property
    def texture_path(self):
        return self._texture_path

    @texture_path.setter
    def texture_path(self, texture_path):
        if texture_path != self._texture_path:
            self._texture_path = texture_path
            self._icon.texturePath = texture_path

    def on_enabled(self, is_enabled):
        self._update_icon_state()
        self._update_opacity()

    def on_hovered(self, is_hovered):
        self._update_icon_state()

    def on_click(self, click_count):
        if not self.enabled:
            return
        Sound.button_click.play()
        if callable(self._on_click):
            self._on_click()

    def on_mouse_enter(self):
        self.hovered = True
        if self.enabled:
            Sound.button_hover.play()

    def on_mouse_exit(self):
        self.hovered = False

    def on_mouse_down(self, button):
        self._update_icon_state()

    def on_mouse_up(self, button):
        self._update_icon_state()

    def _update_icon_state(self):
        if not self.enabled:
            glow_amount = self._glow_amount_disabled
        elif self.hovered:
            if Mouse.left.is_down:
                glow_amount = self._glow_amount_click
            else:
                glow_amount = self._glow_amount_hover
        else:
            glow_amount = self._glow_amount_idle
        animate(self._icon, 'glowAmount', end_value=glow_amount, duration=0.2)

    def _update_opacity(self):
        self._icon.opacity = self._opacity_enabled if self.enabled else self._opacity_disabled

    def __layout(self):
        self._icon = GlowSprite(parent=self, align=Align.to_all, state=State.disabled, texturePath=self.texture_path, iconClass=Sprite, color=self._color)
        self._update_opacity()
