#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\paintToolSignals.py
from signals import Signal
SELECTION_MODIFIER_ADDED = 1
SELECTION_MODIFIER_REMOVED = 2
SELECTION_MODIFIER_CLEAR_ALL = 3
on_paintwork_selection_changed = Signal()
on_structure_selection_changed = Signal()
on_duration_selection_changed = Signal()
on_close_window_requested = Signal()
on_structure_filters_changed = Signal()
on_structure_state_loaded = Signal()
on_structure_select_all_toggle = Signal()
on_application_list_loaded = Signal()
