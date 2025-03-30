#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihighlighting\statelogger.py
POINTER_STATE_VISIBLE = 1
POINTER_STATE_HIDDEN = 2
POINTER_STATE_ELEMENT_INVISIBLE = 3
POINTER_STATE_ELEMENT_NOT_FOUND = 4
STATE_TO_LOG_STRING = {POINTER_STATE_ELEMENT_INVISIBLE: "Not displaying UI Pointer because the element with the id/name '{point_to_id}' is invisible",
 POINTER_STATE_ELEMENT_NOT_FOUND: "Not displaying UI Pointer because the element with the id/name '{point_to_id}' can not be found",
 POINTER_STATE_VISIBLE: "Displaying UI Pointer with the id/name '{point_to_id}'",
 POINTER_STATE_HIDDEN: "Hiding UI Pointer with the id/name '{point_to_id}'"}

class StateLogger(object):
    logger = None
    pointer_states_by_point_to_id = {}

    def __init__(self, logger):
        self.logger = logger

    def set_pointer_state(self, point_to_id, new_pointer_state):
        oldPointerState = self.pointer_states_by_point_to_id.get(point_to_id, None)
        if new_pointer_state == oldPointerState:
            return
        self.pointer_states_by_point_to_id[point_to_id] = new_pointer_state
        log_line = STATE_TO_LOG_STRING.get(new_pointer_state, None)
        if log_line is not None:
            self.logger.LogInfo(log_line.format(point_to_id=point_to_id))

    def log_visible(self, point_to_id):
        self.set_pointer_state(point_to_id, POINTER_STATE_VISIBLE)

    def log_hidden(self, point_to_id):
        self.set_pointer_state(point_to_id, POINTER_STATE_HIDDEN)

    def log_element_invisible(self, point_to_id):
        self.set_pointer_state(point_to_id, POINTER_STATE_ELEMENT_INVISIBLE)

    def log_element_not_found(self, point_to_id):
        self.set_pointer_state(point_to_id, POINTER_STATE_ELEMENT_NOT_FOUND)

    def clear_pointer(self, point_to_id):
        self.pointer_states_by_point_to_id.pop(point_to_id, None)
