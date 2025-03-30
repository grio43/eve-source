#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\tutorial\history.py
from __future__ import division
from carbon.common.script.sys.serviceManager import ServiceManager
import eveui
import threadutils
import uihighlighting
import uthread2
from raffles.client import texture
from raffles.client.localization import Text
from raffles.client.tutorial.effects import do_ding
HISTORY_TAB_LEARNED_KEY = 'hyper_net_history_tab_learned'

def have_learned_history_tab():
    return settings.char.ui.Get(HISTORY_TAB_LEARNED_KEY, False)


def set_history_tab_learned(learned = True):
    settings.char.ui.Set(HISTORY_TAB_LEARNED_KEY, learned)


def show_history_tab_hint():
    if have_learned_history_tab():
        return
    button_hint = find_by_name('RaffleWindow', 'RaffleWindowTabHistory', 'ButtonHint')
    if button_hint:
        return
    history_tab = find_by_name('RaffleWindow', 'RaffleWindowTabHistory')
    if history_tab:
        ButtonHint(history_tab)


class ButtonHint(eveui.compatibility.CarbonEventHandler, eveui.Container):
    default_name = 'ButtonHint'
    default_state = eveui.State.normal
    default_opacity = 0.0

    def __init__(self, button):
        self._button = button
        self._hint_shown = False
        super(ButtonHint, self).__init__(parent=button, align=eveui.Align.to_all, idx=0)
        HintBubble(parent=self, align=eveui.Align.bottom_right, top=4, left=4)
        eveui.fade_in(self, duration=0.4)

    def on_click(self, click_count):
        sm = ServiceManager.Instance()
        ui_highlighting_service = sm.GetService('uiHighlightingService')
        if self._hint_shown:
            ui_highlighting_service.remove_highlight_from_ui_element_by_name(self._button.name)
            set_history_tab_learned()
            self._button.OnClick()
            self.Close()
        else:
            self._hint_shown = True
            ui_highlighting_service.highlight_ui_element_by_name(ui_element_name=self._button.name, title=Text.tutorial_history_tab_hint_title(), message=Text.tutorial_history_tab_hint_text(), fadeout_seconds=8, default_direction=uihighlighting.UiHighlightDirections.DOWN)
            eveui.fade_out(self, duration=0.5)


class HintBubble(eveui.Container):
    default_clipChildren = False
    default_width = 8
    default_height = 8
    default_state = eveui.State.disabled

    def __init__(self, **kwargs):
        super(HintBubble, self).__init__(**kwargs)
        self._bubble = eveui.Sprite(parent=self, align=eveui.Align.center, texturePath=texture.button_hint_bubble, pos=(0, 0, 12, 12), color=(1.0, 0.2, 0.0), opacity=0.9)
        self._animate()

    @threadutils.threaded
    def _animate(self):
        eveui.animate(self._bubble, 'scale', start_value=(1.0, 1.0), end_value=(1.3, 1.3), duration=2.0, curve_type=eveui.CurveType.wave, loops=-1)
        uthread2.sleep(1.0)
        while not self._bubble.destroyed:
            do_ding(parent=self, align=eveui.Align.center, pos=(0, 0, 64, 64), offset=0.0, index=-1, color=(1.0, 0.2, 0.0))
            do_ding(parent=self, align=eveui.Align.center, pos=(0, 0, 64, 64), offset=0.2, index=-1, color=(1.0, 0.2, 0.0))
            uthread2.sleep(2.0)


def find_by_name(*selector):
    from carbonui.uicore import uicore
    return uicore.desktop.FindChild(*selector)
