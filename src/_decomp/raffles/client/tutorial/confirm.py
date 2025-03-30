#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\tutorial\confirm.py
from carbon.common.script.sys.serviceManager import ServiceManager
import uihighlighting
from raffles.client.localization import Text
CONFIRM_BUTTON_LEARNED_KEY = 'hyper_net_confirm_button_learned'

def have_learned_to_confirm():
    return settings.char.ui.Get(CONFIRM_BUTTON_LEARNED_KEY, False)


def set_confirm_button_learned(learned = True):
    settings.char.ui.Set(CONFIRM_BUTTON_LEARNED_KEY, learned)


def show_confirm_button_hint(ui_element_name):
    sm = ServiceManager.Instance()
    ui_highlighting_service = sm.GetService('uiHighlightingService')
    if not ui_highlighting_service.are_any_ui_highlights_active():
        ui_highlighting_service.highlight_ui_element_by_name(ui_element_name=ui_element_name, title=Text.tutorial_confirm_hint_title(), message=Text.tutorial_confirm_hint_text(), fadeout_seconds=8, default_direction=uihighlighting.UiHighlightDirections.UP)


def hide_confirm_button_hint(ui_element_name):
    sm = ServiceManager.Instance()
    sm.GetService('uiHighlightingService').remove_highlight_from_ui_element_by_name(ui_element_name)
