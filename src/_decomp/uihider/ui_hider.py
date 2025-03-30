#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihider\ui_hider.py
import logging
import signals
from copy import deepcopy
from uihider.template_data import get_ui_elements_in_template
logger = logging.getLogger(__name__)
UI_HIDER_ID_ALL_HIDDEN = 1

class UiHider(object):

    def __init__(self):
        self.initialize()

    def initialize(self):
        self._active_data = None
        self._active_template_id = None
        self._on_change = signals.Signal()

    def subscribe(self, callback):
        self._on_change.connect(callback)

    def unsubscribe(self, callback):
        self._on_change.disconnect(callback)

    def set_active_template(self, template_id = None):
        if self._active_template_id == template_id:
            return
        self._active_data = get_ui_elements_in_template(template_id) if template_id else None
        self._active_template_id = template_id
        self._on_change()

    def is_ui_element_hidden(self, unique_ui_name):
        if not self._active_data:
            return False
        return self._active_data.get(unique_ui_name, False)

    def reveal_ui(self, template_id):
        if self._active_template_id == template_id:
            return
        all_hidden_data = deepcopy(get_ui_elements_in_template(UI_HIDER_ID_ALL_HIDDEN))
        template_data = get_ui_elements_in_template(template_id)
        all_hidden_data.update(template_data)
        self._active_data = all_hidden_data
        self._active_template_id = template_id
        self._on_change()

    def reveal_everything(self):
        self.set_active_template(template_id=None)

    def hide_everything(self):
        self.set_active_template(template_id=UI_HIDER_ID_ALL_HIDDEN)
