#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\current_page.py
from carbonui import uiconst
from carbonui.uicore import uicore
from cosmetics.client.ships.skins.live_data import current_skin_design
from eve.client.script.ui.control.historyBuffer import HistoryBuffer
from eve.client.script.ui.cosmetics.ship.const import SkinrPage, CHILD_PAGES_BY_PARENT_PAGE
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
import math
_current_page_id = None
_current_page_args = None
_history_buffer = HistoryBuffer()

def get_page_id():
    global _current_page_id
    return _current_page_id


def get_page_args():
    global _current_page_args
    return _current_page_args


def set_sub_page(page_id, page_args, animate = True):
    global _current_page_args
    global _current_page_id
    last_page_id = _current_page_id
    if _current_page_id == page_id and _current_page_args is None:
        _current_page_args = page_args
        _history_buffer.UpdateCurrent((page_id, page_args))
    elif _current_page_args != page_args:
        _current_page_id = page_id
        _current_page_args = page_args
        _history_buffer.Append((page_id, page_args))
    studioSignals.on_page_opened(page_id, page_args, last_page_id, animate=animate)


def set_page_id(page_id, page_args = None, append_history = True, animate = True):
    if not can_leave_current_page(page_id):
        return False
    _set_page_id(page_id, page_args, append_history, animate)
    return True


def _set_page_id(page_id, page_args, append_history, animate = True):
    global _current_page_args
    global _current_page_id
    last_page_id = _current_page_id
    _current_page_id = page_id
    _current_page_args = page_args
    if append_history:
        _history_buffer.Append((page_id, page_args))
    studioSignals.on_page_opened(page_id, page_args, last_page_id, animate=animate)


def can_leave_current_page(next_page_id = None, page_args = None):
    if _current_page_id == SkinrPage.STUDIO_DESIGNER:
        if next_page_id == SkinrPage.STUDIO_SEQUENCING:
            return True
        return _is_ok_to_discard_unsaved_design()
    if _current_page_id == SkinrPage.STUDIO_SEQUENCING:
        if next_page_id == SkinrPage.STUDIO_DESIGNER:
            return True
        return _is_ok_to_discard_unsaved_design()
    return True


def _is_ok_to_discard_unsaved_design():
    if current_skin_design.has_changes_from_snapshot():
        if uicore.Message('SKINRUnsavedDesign', {}, uiconst.YESNO) != uiconst.ID_YES:
            return False
    return True


def is_back_enabled():
    return _history_buffer.IsBackEnabled()


def _can_go_back():
    if not is_back_enabled():
        return False
    if not can_leave_current_page(*_history_buffer.GetPrevious()):
        return False
    return True


def go_back():
    if _can_go_back():
        page_id, page_args = _history_buffer.GoBack()
        _set_page_id(page_id, page_args, append_history=False)


def is_forward_enabled():
    return _history_buffer.IsForwardEnabled()


def _can_go_forward():
    if not is_forward_enabled():
        return False
    if not can_leave_current_page(*_history_buffer.GetNext()):
        return False
    return True


def go_forward():
    if _can_go_forward():
        page_id, page_args = _history_buffer.GoForward()
        _set_page_id(page_id, page_args, append_history=False)


def reset_history():
    _history_buffer.Reset()


def get_content_right_padding():
    return 0


def get_camera_offset():
    page_id = get_page_id()
    if page_id == SkinrPage.STUDIO:
        return 0.5
    elif page_id == SkinrPage.STORE or page_id in CHILD_PAGES_BY_PARENT_PAGE[SkinrPage.STORE]:
        return 0.425
    elif page_id == SkinrPage.COLLECTION or page_id in CHILD_PAGES_BY_PARENT_PAGE[SkinrPage.COLLECTION]:
        return 0.55
    else:
        return 0.0


def get_camera_yaw():
    page_id = get_page_id()
    if page_id == SkinrPage.STUDIO:
        return -18 / 16.0 * math.pi
    elif page_id == SkinrPage.STUDIO_DESIGNER:
        return -19 / 16.0 * math.pi
    elif page_id == SkinrPage.STUDIO_SEQUENCING:
        return -20 / 16.0 * math.pi
    elif page_id == SkinrPage.STORE or page_id in CHILD_PAGES_BY_PARENT_PAGE[SkinrPage.STORE]:
        return -19 / 16.0 * math.pi
    elif page_id == SkinrPage.COLLECTION or page_id in CHILD_PAGES_BY_PARENT_PAGE[SkinrPage.COLLECTION]:
        return -20 / 16.0 * math.pi
    else:
        return -math.pi
