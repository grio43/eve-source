#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\ticket.py
import uuid
from carbonui.uiconst import TIME_EXIT, TIME_ENTRY
import eveformat.client
import eveui
import signals
import threadutils
import uthread2
from raffles.client import sound, texture
from raffles.client.localization import Text
from raffles.client.tutorial import have_learned_to_confirm, hide_confirm_button_hint, set_confirm_button_learned, show_confirm_button_hint
from raffles.client.widget.dotted_progress import DottedProgress
from raffles.client.widget.error_tooltip import show_error_tooltip
from raffles.client.widget.sweep_effect import SweepEffect

class TicketController(object):

    def __init__(self, raffle, ticket_number):
        self.raffle = raffle
        self.number = ticket_number
        self._owner_id = raffle.get_ticket_owner_id(ticket_number)
        self._is_buying = None
        self._error = None
        self.on_update = signals.Signal(signalName='on_update')

    @property
    def raffle_id(self):
        return self.raffle.raffle_id

    @property
    def display_hash(self):
        return self.raffle.get_ticket_display_hash(self.number)

    @property
    def price(self):
        return self.raffle.ticket_price

    @property
    def owner_id(self):
        return self._owner_id

    @owner_id.setter
    def owner_id(self, owner_id):
        if owner_id == self._owner_id:
            return
        self._owner_id = owner_id
        self.on_update()

    @property
    def is_available(self):
        return self.owner_id is None and not self.is_buying

    @property
    def is_buying(self):
        return self._is_buying

    @is_buying.setter
    def is_buying(self, is_buying):
        if is_buying == self._is_buying:
            return
        self._is_buying = is_buying
        self.on_update()

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, error):
        self._error = error
        self.on_update()

    @threadutils.threaded
    def buy(self):
        if not self.is_available:
            return
        self.is_buying = True
        try:
            self.raffle.buy_ticket(self.number)
        except Exception as error:
            self.error = error
        finally:
            self.is_buying = False


BG_FILL_COLOR_BUYING = (0.7,
 0.7,
 0.7,
 0.8)
BG_FILL_COLOR_AVAILABLE = (0.2,
 0.2,
 0.2,
 0.8)
BG_FILL_COLOR_UNAVAILABLE = (0.08,
 0.08,
 0.08,
 0.8)
BG_FILL_COLOR_OWNED = (0.0,
 0.31,
 0.4,
 0.8)
BG_FILL_COLOR_ERROR = (0.2,
 0.149,
 0.098,
 0.8)
PORTRAIT_FRAME_COLOR_NORMAL = (0.0, 0.0, 0.0)
PORTRAIT_FRAME_COLOR_ERROR = (0.506, 0.341, 0.173)

class Ticket(eveui.Container):
    default_state = eveui.State.hidden
    default_height = 30
    default_width = 138
    default_align = eveui.Align.no_align
    default_opacity = 0

    def __init__(self, **kwargs):
        self.name = 'raffle_ticket_{}'.format(uuid.uuid4())
        super(Ticket, self).__init__(**kwargs)
        self._changing_controller = False
        self._in_confirm_state = False
        self._confirm_state_ready = False
        self._showing_error = False
        self._confirm_thread = None
        self.controller = None
        self._layout_constructed = False
        eveui.fade_in(self, duration=0.5)

    def set_ticket_controller(self, controller):
        self._changing_controller = True
        if self.controller:
            self.controller.on_update.disconnect(self._update)
        self.controller = controller
        if self.controller:
            if not self._layout_constructed:
                self._layout_constructed = True
                self._layout()
            self.controller.on_update.connect(self._update)
            self._on_update_controller()
            self.state = eveui.State.normal
        else:
            self.state = eveui.State.hidden
        self._changing_controller = False

    def _on_update_controller(self):
        self._ticket_hash.set_controller(self.controller)
        if self._showing_error:
            self._error_indicator.opacity = 0
            self._showing_error = False
        if self._in_confirm_state:
            self._exit_confirm_state()
        self._sweep_effect.stop()
        self._hide_portrait()
        self._update()

    @property
    def hint(self):
        if self.controller.error:
            return None
        if self.controller.owner_id == session.charid:
            return Text.ticket_owned_by_me_hint()
        if self.controller.owner_id:
            return Text.ticket_owner_hint(owner_id=self.controller.owner_id)
        if not self.controller.is_available:
            return None
        return Text.purchase_ticket_hint(price=self.controller.price)

    def anim_show(self):
        self.Show()

    def anim_hide(self):
        self.Hide()

    def _update(self, *args):
        self._ticket_hash.update()
        if self.controller.error:
            self._show_error()
        elif self.controller.is_buying:
            self._on_buying()
        elif self.controller.owner_id:
            self._on_owned()
        else:
            self._on_available()

    def _on_available(self):
        self._buying_indicator.Hide()
        self._hide_portrait()

    def _on_buying(self):
        self._buying_indicator.Show()
        self._show_portrait(character_id=session.charid)

    def _on_owned(self):
        self._buying_indicator.Hide()
        if not self._changing_controller:
            self._sweep_effect.sweep(loop=False)
        if self.controller.owner_id == session.charid:
            self._show_portrait()
        else:
            if self._in_confirm_state:
                self._exit_confirm_state()
            self._show_portrait()

    def _get_enabled(self):
        if self.controller.error:
            return False
        if not self.controller.is_available:
            return False
        return True

    def _show_portrait(self, character_id = None):
        if character_id is None:
            character_id = self.controller.owner_id
        if self._changing_controller:
            duration = 0.0
        else:
            duration = 0.25
        self._portrait.state = eveui.State.normal
        self._portrait.character_id = character_id
        eveui.fade_in(self._portrait, duration=duration)

    def _hide_portrait(self):
        if self._portrait.state == eveui.State.disabled:
            return
        if self._changing_controller:
            duration = 0.0
        else:
            duration = 0.25
        self._portrait.state = eveui.State.disabled
        eveui.fade_out(self._portrait, duration=duration)

    def _layout(self):
        self._sweep_effect = SweepEffect(parent=self, align=eveui.Align.to_all, idx=0, opacity=0.4)
        self._main_cont = eveui.Container(parent=self, align=eveui.Align.top_left, width=self.default_width, height=self.default_height)
        self._portrait_container = eveui.Container(parent=self._main_cont, align=eveui.Align.to_left, width=self.default_height)
        eveui.Fill(bgParent=self._portrait_container, color=PORTRAIT_FRAME_COLOR_NORMAL)
        self._buy_icon = eveui.Sprite(parent=self._portrait_container, align=eveui.Align.center, texturePath=texture.isk_16, width=16, height=16, opacity=0.0)
        self._number_container = eveui.Container(parent=self._main_cont, align=eveui.Align.to_all)
        self._hover_fill = eveui.Frame(name='bgHover', parent=self._number_container, texturePath=texture.panel_2_corner, opacity=0.0, cornerSize=9)
        self._corner_sprite = eveui.Sprite(parent=self._portrait_container, texturePath=texture.corner_triangle_small, align=eveui.Align.top_right, pos=(-6, 0, 6, 6), color=PORTRAIT_FRAME_COLOR_NORMAL)
        self._ticket_hash = TicketHash(parent=self._number_container, align=eveui.Align.top_left)

    @eveui.lazy
    def _portrait(self):
        return eveui.CharacterPortrait(parent=self._portrait_container, align=eveui.Align.top_left, size=28, character_id=self.controller.owner_id, left=1, top=1, opacity=0.0)

    @eveui.lazy
    def _buying_indicator(self):
        progress = DottedProgress(parent=self._number_container, align=eveui.Align.center, dot_size=4, wait_time=0.1, idx=0)
        return progress

    @eveui.lazy
    def _error_indicator(self):
        container = eveui.Container(parent=self._portrait_container, align=eveui.Align.to_all, opacity=0.0, idx=0)
        eveui.Fill(bgParent=container, color=PORTRAIT_FRAME_COLOR_ERROR)
        eveui.Sprite(parent=container, align=eveui.Align.center, texturePath=texture.exclamation_icon, width=20, height=20, color=(1.0, 0.651, 0.302), opacity=0.8)
        eveui.Sprite(parent=container, texturePath=texture.corner_triangle_small, align=eveui.Align.top_right, pos=(-6, 0, 6, 6), color=PORTRAIT_FRAME_COLOR_ERROR)
        return container

    @threadutils.threaded
    def _show_error(self):
        if self._showing_error:
            return
        self._showing_error = True
        sound.play(sound.ticket_error)
        show_error_tooltip(self, self.controller.error)
        self._buying_indicator.Hide()
        eveui.fade_in(self._error_indicator, duration=0.2)
        eveui.animate(self._main_cont, 'left', start_value=2, end_value=0, curve_type=eveui.CurveType.bounce, loops=5, duration=0.1)
        uthread2.sleep(2.5)
        if self.destroyed:
            return
        eveui.fade_out(self._error_indicator, duration=0.2, on_complete=self._error_indicator.Close)
        self._showing_error = False
        self.controller.error = None

    @eveui.lazy
    def _confirm_icon(self):
        return eveui.Sprite(parent=self._portrait_container, align=eveui.Align.center, texturePath=texture.checkmark, width=15, height=15, opacity=0.0)

    @eveui.lazy
    def _confirm_overlay(self):
        container = eveui.Container(parent=self._number_container, align=eveui.Align.to_all, idx=1)
        overlay = eveui.Container(parent=container, align=eveui.Align.to_left_prop, opacity=0.0)
        eveui.Frame(bgParent=overlay, texturePath=texture.panel_1_corner, color=BG_FILL_COLOR_BUYING, opacity=1.0, cornerSize=9)
        return overlay

    @eveui.lazy
    def _confirm_label(self):
        text = Text.confirm_purchase()
        width, height = eveui.EveHeaderLarge.MeasureTextSize(text)
        if width > 90 or height > self.default_height:
            label_class = eveui.EveHeaderSmall
        else:
            label_class = eveui.EveHeaderLarge
        return label_class(parent=self._confirm_overlay, align=eveui.Align.center, width=90, text=eveformat.center(text), color=(0, 0, 0), opacity=0.0)

    def _enter_confirm_state(self):
        if self._in_confirm_state:
            return
        self._in_confirm_state = True
        sound.play(sound.ticket_enter_confirm)
        duration = 0.4
        eveui.fade_out(self._buy_icon, duration=TIME_EXIT)
        eveui.fade(self._confirm_icon, end_value=0.8, duration=TIME_ENTRY, time_offset=duration)
        eveui.fade_in(self._confirm_label, duration=duration, time_offset=0.1)
        eveui.fade_in(self._confirm_overlay, duration=0.2)
        eveui.animate(self._confirm_overlay, 'width', start_value=0.0, end_value=1.0, duration=duration)
        uthread2.sleep(duration)
        self._confirm_state_ready = True
        uthread2.sleep(1.5)
        if not have_learned_to_confirm():
            show_confirm_button_hint(self.name)
            uthread2.sleep(8.0)
        else:
            uthread2.sleep(1.0)
        self._confirm_thread = None
        self._exit_confirm_state()

    def _exit_confirm_state(self, is_buying = False):
        if self._confirm_thread:
            self._confirm_thread.kill()
            self._confirm_thread = None
        self._in_confirm_state = False
        self._confirm_state_ready = False
        eveui.fade_out(self._confirm_icon, duration=0.3, on_complete=self._confirm_icon.Close)
        if is_buying:
            sound.play(sound.ticket_confirmed)
            hide_confirm_button_hint(self.name)
            set_confirm_button_learned(True)
            eveui.fade_out(self._confirm_overlay, duration=0.3, time_offset=0.1, on_complete=self._confirm_overlay.Close)
        else:
            sound.play(sound.ticket_exit_confirm)
            eveui.fade_out(self._confirm_label, duration=0.1)
            eveui.fade_out(self._confirm_overlay, duration=0.1, time_offset=0.1, on_complete=self._confirm_overlay.Close)
            eveui.animate(self._confirm_overlay, 'width', end_value=0.0, duration=0.25)

    def OnClick(self, *args):
        if not self._get_enabled():
            return
        if self._in_confirm_state and self._confirm_state_ready:
            self._exit_confirm_state(is_buying=True)
            self.controller.buy()
        else:
            self._confirm_thread = uthread2.StartTasklet(self._enter_confirm_state)

    def OnMouseEnter(self, *args):
        if not self._get_enabled():
            return
        sound.play(sound.ticket_hover)
        eveui.fade(self._hover_fill, end_value=0.1, duration=TIME_ENTRY)
        if self._in_confirm_state:
            eveui.fade(self._confirm_icon, end_value=0.8, duration=TIME_ENTRY)
        else:
            eveui.fade(self._buy_icon, end_value=0.8, duration=TIME_ENTRY)

    def OnMouseExit(self, *args):
        eveui.fade_out(self._hover_fill, duration=TIME_EXIT)
        if self._in_confirm_state:
            eveui.fade_out(self._confirm_icon, duration=TIME_EXIT)
        else:
            eveui.fade_out(self._buy_icon, duration=TIME_EXIT)


class TicketHash(eveui.Container):
    default_width = 108
    default_height = 30

    def __init__(self, **kwargs):
        super(TicketHash, self).__init__(**kwargs)
        self.controller = None
        self._characters = []
        self._layout()

    def set_controller(self, controller):
        self.controller = controller
        self._update_hash()

    def update(self):
        self.character_container.opacity = self._get_text_opacity()
        self._bg_fill.color = self._get_background_color()

    def _update_hash(self):
        for i, character in enumerate(self._characters):
            character.text = self.controller.display_hash[i]

    def _get_text_opacity(self):
        if self.controller.error:
            return 0.2
        elif self.controller.is_buying:
            return 0.0
        elif self.controller.is_available:
            return 1.0
        elif self.controller.owner_id == session.charid:
            return 0.8
        else:
            return 0.2

    def _get_character_frame_opacity(self):
        if self.controller.is_available and not self.controller.error:
            return 0.05
        else:
            return 0.0

    def _get_background_color(self):
        if self.controller.is_buying:
            return BG_FILL_COLOR_BUYING
        elif self.controller.error:
            return BG_FILL_COLOR_ERROR
        elif self.controller.is_available:
            return BG_FILL_COLOR_AVAILABLE
        elif self.controller.owner_id == session.charid:
            return BG_FILL_COLOR_OWNED
        else:
            return BG_FILL_COLOR_UNAVAILABLE

    def _layout(self):
        self._bg_fill = eveui.Frame(name='bg', bgParent=self, texturePath=texture.panel_2_corner, cornerSize=9, opacity=0.8)
        self.character_container = eveui.Container(parent=self, opacity=0, padding=(2, 3, 2, 3))
        left = 10
        for _ in xrange(4):
            label = eveui.Label(parent=self.character_container, align=eveui.Align.center_left, fontsize=16, fontStyle=eveui.FontStyle.condensed, left=left)
            self._characters.append(label)
            left += 26
