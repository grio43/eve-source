#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\character_sheet\home\controller.py
import datetime
import logging
import datetimeutils
import gametime
import signals
import threadutils
from expertSystems import get_expert_system, MAX_INSTALLED_DURATION_TO_ALLOW_TOP_UP
from expertSystems.client.prompt import prompt_remove_expert_system
from expertSystems.client.service import ExpertSystemService
from expertSystems.client.ui.character_sheet.home.slot import SlotController
from expertSystems.client.util import browse_expert_systems, train_expert_system_skills
import skills.client.util as skillsUtil
log = logging.getLogger(__name__)

class State(object):
    initial = 0
    loading = 1
    ready = 2
    error = 3


class PageController(object):

    def __init__(self, expert_system_service = None):
        if expert_system_service is None:
            expert_system_service = ExpertSystemService.instance()
        self.on_state_changed = signals.Signal()
        self.on_selected_expert_system_changed = signals.Signal()
        self.on_browse = signals.Signal()
        self.slots = [ SlotController() for _ in range(3) ]
        self._expert_system_service = expert_system_service
        self._my_expert_systems = None
        self._selected_expert_system_id = None
        self._state = State.initial
        self._expert_system_service.on_expert_systems_updated.connect(self._handle_expert_systems_updated)

    @property
    def selected_expert_system_id(self):
        return self._selected_expert_system_id

    @selected_expert_system_id.setter
    def selected_expert_system_id(self, expert_system_id):
        if self._selected_expert_system_id != expert_system_id:
            self._selected_expert_system_id = expert_system_id
            for slot in self.slots:
                slot.is_selected = slot.expert_system is not None and slot.expert_system.type_id == expert_system_id

            self.on_selected_expert_system_changed()

    @property
    def selected_expert_system(self):
        if self._selected_expert_system_id is not None:
            return self._my_expert_systems[self._selected_expert_system_id]

    @property
    def state(self):
        return self._state

    def close(self):
        self._expert_system_service.on_expert_systems_updated.disconnect(self._handle_expert_systems_updated)
        for slot in self.slots:
            slot.on_add.disconnect(self._on_add_from_slot)
            slot.on_selected_changed.disconnect(self._on_slot_selected_changed)

    @threadutils.highlander_threaded
    def load(self):
        self._set_state(State.loading)
        try:
            self._load_my_expert_systems()
            my_expert_systems = sorted(self._my_expert_systems.values(), key=lambda expert_system: expert_system.installed_at)
            for i, slot in enumerate(self.slots):
                if len(my_expert_systems) > i:
                    expert_system = my_expert_systems[i]
                    slot.expert_system = expert_system
                    if expert_system.type_id == self.selected_expert_system_id:
                        slot.is_selected = True
                else:
                    slot.expert_system = None
                slot.on_add.connect(self._on_add_from_slot)
                slot.on_selected_changed.connect(self._on_slot_selected_changed)

            previously_selected = self.selected_expert_system_id
            self.selected_expert_system_id = None
            if previously_selected not in self._my_expert_systems:
                if self.slots[0].expert_system is not None:
                    self.selected_expert_system_id = self.slots[0].expert_system.type_id
            else:
                self.selected_expert_system_id = previously_selected
            self._set_state(State.ready)
        except Exception:
            log.exception('Failed to load Expert Systems panel')
            self._set_state(State.error)

    def browse(self):
        self.on_browse()

    def extend_selected_duration(self):
        browse_expert_systems(self.selected_expert_system_id)

    def remove_selected(self):
        if self.selected_expert_system_id:
            if not prompt_remove_expert_system(self.selected_expert_system_id):
                return
            self._expert_system_service.RemoveExpertSystem(self.selected_expert_system_id)

    def train_selected_skills(self):
        if self.selected_expert_system_id:
            train_expert_system_skills(self.selected_expert_system_id)

    def _load_my_expert_systems(self):
        my_expert_systems_data = self._expert_system_service.GetMyExpertSystems()
        self._my_expert_systems = {type_id:ExpertSystem(type_id=type_id, installed_at=datetimeutils.filetime_to_datetime(installed_blue_time), expires_at=datetimeutils.filetime_to_datetime(expires_blue_time)) for type_id, (installed_blue_time, expires_blue_time) in my_expert_systems_data.iteritems()}

    def _set_state(self, state):
        if state != self._state:
            old_state = self._state
            self._state = state
            self.on_state_changed(state, old_state)

    def _on_slot_selected_changed(self, slot):
        if slot.is_selected:
            self.selected_expert_system_id = slot.expert_system.type_id

    def _on_add_from_slot(self, slot):
        self.browse()

    def _handle_expert_systems_updated(self):
        self.load()


class ExpertSystem(object):

    def __init__(self, type_id, installed_at, expires_at):
        self._type_id = type_id
        self._installed_at = installed_at
        self._expires_at = expires_at
        self._static_data = get_expert_system(type_id)

    @property
    def type_id(self):
        return self._type_id

    @property
    def name(self):
        return self._static_data.name

    @property
    def description(self):
        return self._static_data.description

    @property
    def skills(self):
        return self._static_data.skills

    @property
    def skills_to_train(self):
        return skillsUtil.get_skills_to_train(self.skills)

    @property
    def can_train_skills(self):
        return len(self.validate_train_skills()) == 0

    @property
    def can_extend(self):
        return len(self.validate_extend()) == 0

    @property
    def expires_at(self):
        return self._expires_at

    @property
    def expires_in(self):
        return self._expires_at - gametime.now()

    @property
    def installed_at(self):
        return self._installed_at

    @property
    def expires_soon(self):
        return self.expires_at - gametime.now() < datetime.timedelta(days=1)

    @property
    def remaining_time_proportion(self):
        remaining_seconds = (self.expires_at - gametime.now()).total_seconds()
        total_seconds = (self.expires_at - self.installed_at).total_seconds()
        return max(0.0, remaining_seconds) / total_seconds

    def validate_extend(self):
        errors = []
        top_up_duration_limit = datetimeutils.filetime_delta_to_timedelta(MAX_INSTALLED_DURATION_TO_ALLOW_TOP_UP)
        if self._static_data.hidden:
            errors.append(ExtendValidationError.hidden)
        elif self._static_data.retired:
            errors.append(ExtendValidationError.retired)
        elif self.expires_in > top_up_duration_limit:
            errors.append(ExtendValidationError.duration_limit_reached)
        return errors

    def validate_train_skills(self):
        errors = []
        if len(self.skills_to_train) == 0:
            errors.append(TrainSkillsValidationError.no_skills_to_train)
        return errors

    def __eq__(self, other):
        return isinstance(other, ExpertSystem) and self._type_id == other.type_id and self._expires_at == other.expires_at and self._installed_at == other.installed_at

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.type_id)


class ExtendValidationError(object):
    hidden = 1
    retired = 2
    duration_limit_reached = 3


class TrainSkillsValidationError(object):
    no_skills_to_train = 1
