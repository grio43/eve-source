#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\tutorial\__init__.py
from .confirm import have_learned_to_confirm, hide_confirm_button_hint, set_confirm_button_learned, show_confirm_button_hint
from .history import have_learned_history_tab, set_history_tab_learned, show_history_tab_hint
from .intro import have_seen_introduction, show_introduction, set_introduction_seen

def reset_tutorials():
    set_introduction_seen(False)
    set_confirm_button_learned(False)
    set_history_tab_learned(False)
