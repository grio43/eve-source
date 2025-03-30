#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\live_data\current_skin_design.py
import uthread2
from eve.client.script.ui.control.historyBuffer import HistoryBuffer
from cosmetics.common.ships.skins.static_data.slot_name import PATTERN_RELATED_SLOT_IDS, PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID
from characterdata.races import get_ship_type_id
from cosmetics.client.shipSkinDataSvc import get_ship_skin_data_svc
from cosmetics.client.shipSkinDesignSvc import get_ship_skin_design_svc
from cosmetics.client.ships.skins.live_data import current_skin_design_signals
from cosmetics.client.ships.skins.live_data.skin_design import SkinDesign
from cosmetics.common.ships.skins.static_data.slot_configuration import is_skinnable_ship
from eve.client.script.ui.control.message import ShowQuickMessage
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException
_current_design = SkinDesign()
_current_design.on_name_changed.connect(current_skin_design_signals.on_name_changed)
_current_design.on_line_name_changed.connect(current_skin_design_signals.on_line_name_changed)
_current_design.on_slot_fitting_changed.connect(current_skin_design_signals.on_slot_fitting_changed)
_current_design.on_ship_type_id_changed.connect(current_skin_design_signals.on_ship_type_id_changed)
_current_design.on_tier_level_changed.connect(current_skin_design_signals.on_tier_level_changed)
_current_design.on_component_instance_license_to_use_changed.connect(current_skin_design_signals.on_component_instance_license_to_use_changed)
_current_design.on_pattern_blend_mode_changed.connect(current_skin_design_signals.on_pattern_blend_mode_changed)
_current_design.on_component_attribute_changed.connect(current_skin_design_signals.on_component_attribute_changed)
_snapshot_design = SkinDesign()
_selected_slot_id = None
_undo_history_buffer = HistoryBuffer(maxLen=50)
_undo_batch_thread = None

def take_snapshot():
    _snapshot_design.update_from_other(_current_design)
    current_skin_design_signals.on_snapshot_changed()


def has_changes_from_snapshot():
    return _current_design != _snapshot_design


def get():
    return _current_design


def get_default_ship_type_id(type_id = None):
    if not type_id:
        type_id = get_active_ship_type_id()
    if not is_skinnable_ship(type_id):
        type_id = get_ship_type_id(session.raceID)
    return type_id


def get_active_ship_type_id():
    return sm.GetService('godma').GetItem(session.shipid).typeID


def get_selected_slot_id():
    global _selected_slot_id
    return _selected_slot_id


def get_selected_pattern_component_instance():
    slot_id = get_selected_slot_id()
    if slot_id not in PATTERN_RELATED_SLOT_IDS:
        return
    slot_id = PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID.get(slot_id, slot_id)
    return get().get_fitted_component_instance(slot_id)


def set_selected_slot_id(value):
    global _selected_slot_id
    _selected_slot_id = value
    current_skin_design_signals.on_slot_selected(value)


def create_blank_design(ship_type_id = None):
    ship_type_id = get_default_ship_type_id(ship_type_id)
    _current_design.clear()
    _current_design.creator_character_id = session.charid
    _current_design.ship_type_id = ship_type_id
    take_snapshot()
    reset_undo_history()
    current_skin_design_signals.on_design_reset(_current_design, None)


def reset_design(ship_type_id = None):
    if not ship_type_id:
        ship_type_id = get_default_ship_type_id()
    if _current_design.has_fitted_components() or ship_type_id != _current_design.ship_type_id:
        create_blank_design(ship_type_id)
        reset_undo_history()


def open_existing_saved_design(saved_skin_design_id):
    try:
        existing_saved_design = get_ship_skin_design_svc().get_saved_design(saved_skin_design_id)
    except (GenericException, TimeoutException):
        ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
        existing_saved_design = None

    if existing_saved_design is not None:
        update_from_other(existing_saved_design, saved_skin_design_id)
        reset_undo_history()


def update_from_other(skin_design, saved_skin_design_id = None, animate = True):
    _current_design.update_from_other(skin_design, saved_skin_design_id=saved_skin_design_id)
    take_snapshot()
    current_skin_design_signals.on_existing_design_loaded(_current_design, animate)


def open_existing_design(skin_hex, animate = True):
    try:
        existing_design = get_ship_skin_data_svc().get_skin_data(skin_hex)
    except (GenericException, TimeoutException):
        ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
        return

    if existing_design is not None:
        _current_design.update_from_other(existing_design)
        take_snapshot()
        current_skin_design_signals.on_existing_design_loaded(_current_design, animate)


def reset_undo_history():
    _undo_history_buffer.Reset()
    add_to_undo_history()


def add_to_undo_history():
    skin_design = _add_to_undo_history()
    current_skin_design_signals.on_undo_history_change()
    return skin_design


def add_to_undo_history_batch_up(batch_up_delay = 3.0):
    global _undo_batch_thread
    if _undo_batch_thread:
        skin_design, _ = _undo_history_buffer.GetCurrent()
        skin_design.update_from_other(_current_design)
    else:
        _add_to_undo_history()
        _undo_batch_thread = uthread2.start_tasklet(_add_to_undo_history_thread, batch_up_delay)


def _add_to_undo_history_thread(batch_up_delay = None):
    global _undo_batch_thread
    uthread2.Sleep(batch_up_delay)
    _undo_batch_thread = None


def _add_to_undo_history():
    _kill_undo_batch_thread()
    skin_design = SkinDesign()
    skin_design.update_from_other(_current_design)
    _undo_history_buffer.Append((skin_design, _selected_slot_id))
    return skin_design


def _kill_undo_batch_thread():
    global _undo_batch_thread
    if _undo_batch_thread:
        _undo_batch_thread.kill()
        _undo_batch_thread = None


def _undo_redo(skin_design, selected_slot_id):
    if not skin_design:
        return
    _current_design.update_from_other(skin_design)
    set_selected_slot_id(selected_slot_id)
    current_skin_design_signals.on_existing_design_loaded(_current_design, False)
    current_skin_design_signals.on_undo_history_change()


def undo():
    if _undo_batch_thread:
        _add_to_undo_history()
    _undo_redo(*_undo_history_buffer.GoBack())


def redo():
    if _undo_batch_thread:
        _add_to_undo_history()
    _undo_redo(*_undo_history_buffer.GoForward())


def is_undo_enabled():
    return _undo_history_buffer.IsBackEnabled()


def is_redo_enabled():
    return _undo_history_buffer.IsForwardEnabled()
