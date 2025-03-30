#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\character_sheet\browse\controller.py
import signals
from expertSystems import get_expert_systems
from expertSystems.client.service import ExpertSystemService

class PageController(object):

    def __init__(self, expert_system_service = None):
        if expert_system_service is None:
            expert_system_service = ExpertSystemService.instance()
        self._expert_system_service = expert_system_service
        self._expert_systems = None
        self._selected_expert_system_id = None
        self.on_back = signals.Signal()
        self.on_selected_expert_system_changed = signals.Signal()

    @property
    def expert_systems(self):
        if self._expert_systems is None:
            self._expert_systems = {expert_system.type_id:expert_system for expert_system in get_expert_systems()}
        return self._expert_systems.values()

    @property
    def selected_expert_system(self):
        if self._selected_expert_system_id:
            return self._expert_systems[self._selected_expert_system_id]

    @selected_expert_system.setter
    def selected_expert_system(self, expert_system):
        if expert_system.type_id not in self._expert_systems:
            raise ValueError()
        if expert_system.type_id != self._selected_expert_system_id:
            self._selected_expert_system_id = expert_system.type_id
            self.on_selected_expert_system_changed()

    def go_back(self):
        self.on_back()
