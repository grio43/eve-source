#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\client\operationscontroller.py
from achievements.common.achievementConst import AchievementEventConst
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.const import YESNO, ID_YES
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem
from operations.client.activeOperation import ActiveOperations
from operations.client.error import OperationNotReplayable, ReplayCancelledByUser, FailedToActivateDueToPrerequisites, FailedToActivateByServer, FailedToActivateInUnknownSpace
from operations.client.eventdirector.operationscache import EventDirectorOperationCache
from operations.client.operationstatecache import OperationStateLock
from operations.client.util import can_undock, are_operations_active
from operations.common.const import TaskState, OperationState, OPERATION_CATEGORY_RECOMMENDATIONS
from operations.common import util
from operations.common.progression import TreeKeeper
from operations.common.skipconditions.evaluator import evaluate_client_skip_conditions_for_task
import logging
logger = logging.getLogger(__name__)
REPLAY_WARNING_DIALOG_ID = 'ReplayOperationWarning'

def find_task_index(state_cache, category_id, operation_id, task_id):
    active_tasks = state_cache.tasks_by_category_and_operation_id[category_id][operation_id]
    for task_tuple in active_tasks:
        active_task_id, active_task_state, active_task_progress = task_tuple
        if active_task_id == task_id:
            return active_tasks.index(task_tuple)


def get_next_task_index(state_cache, category_id, operation_id, current_task_index):
    next_task_index = current_task_index + 1
    if next_task_index < len(state_cache.tasks_by_category_and_operation_id[category_id][operation_id]):
        return next_task_index


def get_task_index(state_cache, category_id, operation_id, task_id):
    for task_tuple in state_cache.tasks_by_category_and_operation_id[category_id][operation_id]:
        if task_tuple[0] == task_id:
            return state_cache.tasks_by_category_and_operation_id[category_id][operation_id].index(task_tuple)


def get_task_state(state_cache, category_id, operation_id, task_id):
    task_index = get_task_index(state_cache, category_id, operation_id, task_id)
    if task_index is None:
        return
    _, task_state, _ = state_cache.tasks_by_category_and_operation_id[category_id][operation_id][task_index]
    return task_state


def transition_task(state_cache, category_id, operation_id, task_id, from_state, to_state):
    task_index = get_task_index(state_cache, category_id, operation_id, task_id)
    _, task_state, task_progress = state_cache.tasks_by_category_and_operation_id[category_id][operation_id][task_index]
    if task_state == from_state and from_state != to_state:
        state_cache.tasks_by_category_and_operation_id[category_id][operation_id][task_index] = (task_id, to_state, task_progress)
        scatter_transition(category_id, operation_id, task_id, from_state, to_state)


def transition_task_from_any(state_cache, category_id, operation_id, task_id, to_state, progress = None):
    task_index = get_task_index(state_cache, category_id, operation_id, task_id)
    task_id, from_state, task_progress = state_cache.tasks_by_category_and_operation_id[category_id][operation_id][task_index]
    if progress is not None:
        task_progress = progress
    if from_state != to_state:
        state_cache.tasks_by_category_and_operation_id[category_id][operation_id][task_index] = (task_id, to_state, task_progress)
        scatter_transition_from_any(category_id, operation_id, task_id, from_state, to_state)


def scatter_transition(category_id, operation_id, task_id, from_state, to_state):
    if from_state != to_state:
        scatter_transition_from_any(category_id, operation_id, task_id, from_state, to_state)


def scatter_transition_from_any(category_id, operation_id, task_id, from_state, to_state):
    sm.ScatterEvent('OnOperationTaskTransition', category_id, operation_id, task_id, from_state, to_state)
    if to_state == TaskState.ACTIVE:
        sm.ScatterEvent('OnOperationTaskMadeActive', task_id, None, operation_id)


class OperationsController(object):
    __notifyevents__ = ['OnSessionChanged',
     'OnOperationTaskCompleted',
     'OnOperationTaskSkipped',
     'OnOperationSkipped',
     'OnOperationsProgressReset',
     'OnOperationCategoryChanged',
     'OnOperationCategoryCompleted',
     'OnOperationDeactivated',
     'OnOperationsServerFSDReload']

    def __init__(self, operation_cache, *args, **kwargs):
        sm.RegisterNotify(self)
        self.operation_cache = operation_cache
        self.character_id = None
        self.manager = sm.RemoteSvc('operationsManager')
        self.mission_avoidance_systems = None
        self.operation_cache.on_fsd_reload.connect(self.on_fsd_reload)
        self._reset_state_cache()
        self.active_operations = None

    def release(self):
        if self.active_operations:
            self.active_operations.stop()
            self.active_operations = None

    def OnSessionChanged(self, isremote, session, change):
        if 'charid' in change and not self.character_id:
            self._initialize_state_for_character(session.charid)

    def on_fsd_reload(self):
        if not session.charid:
            return
        self._initialize_state_for_character(session.charid)
        ShowQuickMessage('Operations FSD data reloaded')

    def _reset_state_cache(self):
        self.state_cache = OperationStateLock()
        self.operations_completed_at_least_once = {}

    def initialize(self, character_id):
        if character_id:
            self._initialize_state_for_character(character_id)

    def _initialize_progress(self, state_cache):
        progress_dict = self.manager.get_character_progress() or {}
        unlocked_categories = set()
        operation_states = {}
        for category_id in progress_dict:
            state_cache.tasks_by_category_and_operation_id[category_id] = {}
            unlocked_categories.add(category_id)
            operation_states[category_id] = {}
            for operation_id, operation_state, task_states in progress_dict[category_id]:
                operation_states[category_id][operation_id] = operation_state
                state_cache.tasks_by_category_and_operation_id[category_id][operation_id] = task_states

        if state_cache.tree_keeper is None:

            def has_operation_ever_been_completed_by_character(character_id, category_id, operation_id):
                return self.has_operation_ever_been_completed(category_id, operation_id)

            state_cache.tree_keeper = TreeKeeper(self.character_id, self.operation_cache, unlocked_categories, operation_states, has_operation_ever_been_completed_by_character)
            logger.debug('New progress tree keeper initialized for character %s', self.character_id)
        else:
            state_cache.tree_keeper.operation_states = operation_states
            logger.debug('Progress updated for existing progress tree keeper for character %s', self.character_id)

    def _initialize_category_and_operation(self):
        with self.state_cache.Lock() as state_cache:
            self._initialize_active_category(state_cache)
            self._initialize_active_operation(state_cache)
            self.unblock_first_task_in_active_operation(state_cache)

    def _initialize_active_category(self, state_cache):
        state_cache.active_category_id = self.manager.get_active_category_id()

    def _initialize_active_operation(self, state_cache):
        if state_cache.tree_keeper is None:
            logger.warn('Failed to initialize active operation, tree keeper is not available.')
            return
        active_category_id = state_cache.active_category_id
        _, active_category_tree = state_cache.tree_keeper.get_active_progress_tree_for_category(active_category_id)
        if active_category_tree is None:
            return
        operation_node = active_category_tree.get_active_node()
        if operation_node is None:
            logger.warn('Tree for category %s has no active node.' % (active_category_id,))
            return
        self.set_active_operation(state_cache, operation_node.category_id, operation_node.operation_id)
        self.manager.start_site(operation_node.category_id, operation_node.operation_id)

    def _initialize_state_for_character(self, character_id):
        logger.debug('initialize_state_for_character %s', character_id)
        self.character_id = character_id
        self._reset_state_cache()
        if self.active_operations:
            self.active_operations.stop()
        self.active_operations = ActiveOperations(get_active_task_id=self.get_active_task_id)
        with self.state_cache.Lock() as state_cache:
            self._initialize_progress(state_cache)
        self._initialize_category_and_operation()

    def is_death_category_active(self):
        ship_death_category_id = self.operation_cache.get_category_id_for_ship_death()
        capsule_death_category_id = self.operation_cache.get_category_id_for_capsule_death()
        death_categories = filter(None, [ship_death_category_id, capsule_death_category_id])
        return self.get_active_category_id() in death_categories

    def complete_category(self, category_id):
        self.manager.complete_category_for_character(self.character_id, category_id)

    def get_operation_state(self, category_id, operation_id):
        with self.state_cache.Lock() as state_cache:
            return self._get_operation_state(state_cache, category_id, operation_id)

    def _get_operation_state(self, state_cache, category_id, operation_id):
        if state_cache.tree_keeper is None:
            return
        trees = state_cache.tree_keeper.get_progress_trees_for_category(category_id)
        for tree in trees:
            operation_node = tree.get_node_by_operation_id(operation_id)
            if operation_node is not None:
                return operation_node.state

    def set_operation_state(self, state_cache, category_id, operation_id, state):
        if state_cache.tree_keeper is None:
            logger.warn('Failed to set operation state (categoryID: %s, operationID: %s, state: %s), tree keeper is not available.' % (category_id, operation_id, state))
            return
        trees = state_cache.tree_keeper.get_progress_trees_for_category(category_id)
        for tree in trees:
            operation_node = tree.get_node_by_operation_id(operation_id)
            if operation_node is not None:
                operation_node.state = state

        if state == OperationState.COMPLETE:
            self.set_cached_operation_completed(category_id, operation_id)

    def get_task_state(self, category_id, operation_id, task_id):
        with self.state_cache.Lock() as state_cache:
            return get_task_state(state_cache, category_id, operation_id, task_id)

    def is_task_active(self, category_id, operation_id, task_id):
        return self.get_task_state(category_id, operation_id, task_id) == TaskState.ACTIVE

    def is_operation_complete(self, category_id, operation_id):
        return self.get_operation_state(category_id, operation_id) == OperationState.COMPLETE

    def is_operation_offered(self, category_id, operation_id):
        state = self.get_operation_state(category_id, operation_id)
        return state != OperationState.COMPLETE and self.are_operation_prerequisites_met(category_id, operation_id)

    def get_active_category_id(self):
        return self.state_cache.get_active_category_id()

    def get_active_operation_id(self):
        return self.state_cache.get_active_operation_id()

    def is_active_operation_a_recommendation(self):
        return self.get_active_category_id() == OPERATION_CATEGORY_RECOMMENDATIONS and self.get_active_operation()

    def is_non_recommendation_operation_active(self):
        if self.is_any_operation_active():
            if GetOperationsController().is_active_operation_a_recommendation():
                return False
            return True
        return False

    def get_next_operation_id(self, category_id):
        category = self.get_category_by_id(category_id)
        for operation_id in category.iter_operation_ids():
            if self.is_operation_offered(category_id, operation_id):
                return operation_id

    def get_active_operation(self):
        operation_id = self.get_active_operation_id()
        if operation_id:
            return self.get_operation_by_id(operation_id)

    def is_any_operation_active(self):
        return all([self.get_active_category_id(), self.get_active_operation_id()])

    def get_active_site_id(self):
        operationID = self.get_active_operation_id()
        if operationID is None:
            return
        operation = self.get_operation_by_id(operationID)
        return getattr(operation, 'siteID', None)

    def get_operations_for_category(self, category):
        return self.operation_cache.get_operations_for_category(category)

    def get_first_task_in_operation(self, operation_id):
        return self.operation_cache.get_first_task_in_operation(operation_id)

    def get_tasks_in_category(self, category_id):
        return self.operation_cache.get_tasks_in_category(category_id)

    def set_active_operation(self, state_cache, category_id, operation_id, is_silent = False):
        old_active_category_id = state_cache.active_category_id
        old_active_operation_id = state_cache.active_operation_id
        if old_active_category_id is not None and old_active_operation_id is not None:
            old_state = self._get_operation_state(state_cache, old_active_category_id, old_active_operation_id)
            if util.is_operation_active(old_state):
                has_been_completed = self.has_operation_ever_been_completed(old_active_category_id, old_active_operation_id)
                state = OperationState.COMPLETE if has_been_completed else OperationState.LOCKED
                self.set_operation_state(state_cache, old_active_category_id, old_active_operation_id, state)
        state_cache.active_category_id = category_id
        state_cache.active_operation_id = operation_id
        if category_id is not None and operation_id is not None:
            is_reactivation = self.has_operation_ever_been_completed(category_id, operation_id)
            state = OperationState.REACTIVATED if is_reactivation else OperationState.ACTIVE
            self.set_operation_state(state_cache, category_id, operation_id, state)
            sm.ScatterEvent('OnOperationMadeActive', category_id, operation_id, old_active_category_id, old_active_operation_id, is_silent)
        else:
            sm.ScatterEvent('OnOperationQuit', old_active_category_id, old_active_operation_id)

    def get_active_operation_module_requirements(self):
        operation = self.get_active_operation()
        if operation is not None:
            raceID = session.raceID
            if raceID in operation.moduleRequirements:
                return operation.moduleRequirements[raceID]
        return []

    def is_client_event_interesting(self, event_type):
        return event_type in self.get_interesting_events()

    def get_category_by_id(self, category_id):
        return self.operation_cache.get_operation_category_by_id(category_id)

    def get_operation_by_id(self, operation_id):
        return self.operation_cache.get_operation_by_id(operation_id)

    def get_active_task_tuples_for_operation(self, category_id, operation_id):
        with self.state_cache.Lock() as state_cache:
            task_list = []
            for task_tuple in state_cache.tasks_by_category_and_operation_id[category_id][operation_id]:
                task_id, task_state, task_progress = task_tuple
                if util.is_task_completable(task_state):
                    task_list.append(task_tuple)

            return task_list

    def get_first_unfinished_task_in_operation(self, category_id, operation_id):
        operation = self.operation_cache.load_operation_by_id(operation_id)
        if operation is None:
            return
        with self.state_cache.Lock() as state_cache:
            for task_id in operation.iter_task_ids():
                task_state = get_task_state(state_cache, category_id, operation_id, task_id)
                if not util.is_task_finished(task_state):
                    return task_id

    def get_active_task_tuples(self):
        category_id = self.get_active_category_id()
        operation_id = self.get_active_operation_id()
        if category_id is None or operation_id is None:
            return []
        return self.get_active_task_tuples_for_operation(category_id, operation_id)

    def get_interesting_events(self):
        event_list = []
        last_task_was_interesting = False
        last_task_was_optional = False
        category_id = self.get_active_category_id()
        operation_id = self.get_active_operation_id()
        try:
            with self.state_cache.Lock() as state_cache:
                tasks = state_cache.tasks_by_category_and_operation_id[category_id][operation_id]
                for task_tuple in tasks:
                    task_id, task_state, task_progress = task_tuple
                    task = self.operation_cache.get_task_by_id(task_id)
                    if util.is_task_completable(task_state) or task.is_optional and last_task_was_interesting:
                        last_task_was_interesting = True
                        event_list.append(task.achievementEventType)
                    else:
                        if task.is_supreme or last_task_was_interesting and last_task_was_optional:
                            event_list.append(task.achievementEventType)
                        last_task_was_interesting = False
                    last_task_was_optional = task.is_optional

        except KeyError:
            pass

        return event_list

    def _skip_client_task_if_appropriate(self, category_id, operation_id, task_id):
        if evaluate_client_skip_conditions_for_task(self.character_id, self.operation_cache, task_id):
            return self.manager.skip_task(category_id, operation_id, task_id)
        return False

    def _advance_to_next_operation_task(self, state_cache, category_id, operation_id, task_id, task_index):
        next_task_index = get_next_task_index(state_cache, category_id, operation_id, task_index)
        while next_task_index is not None:
            next_task_id, next_task_state, next_task_progress = state_cache.tasks_by_category_and_operation_id[category_id][operation_id][next_task_index]
            if util.is_task_finished(next_task_state):
                next_task_index = get_next_task_index(state_cache, category_id, operation_id, next_task_index)
                continue
            state_cache.tasks_by_category_and_operation_id[category_id][operation_id][next_task_index] = (next_task_id, TaskState.ACTIVE, next_task_progress)
            if not self._skip_client_task_if_appropriate(category_id, operation_id, next_task_id):
                sm.ScatterEvent('OnOperationTaskMadeActive', next_task_id, task_id, operation_id)
            return True

        return False

    def _unlock_task(self, state_cache, category_id, operation_id, task_id):
        skipped = self._skip_client_task_if_appropriate(category_id, operation_id, task_id)
        new_state = TaskState.SKIPPED if skipped else TaskState.ACTIVE
        transition_task_from_any(state_cache, category_id, operation_id, task_id, new_state)

    def block_task(self, category_id, operation_id, task_id):
        with self.state_cache.Lock() as state_cache:
            task_state = get_task_state(state_cache, category_id, operation_id, task_id)
            if not util.is_task_finished(task_state):
                transition_task_from_any(state_cache, category_id, operation_id, task_id, TaskState.BLOCKED)
            self.manager.block_task(category_id, operation_id, task_id)

    def unblock_tasks_in_active_operation(self):
        with self.state_cache.Lock() as state_cache:
            active_category_id = state_cache.active_category_id
            active_operation_id = state_cache.active_operation_id
            if active_category_id is None or active_operation_id is None:
                return
            tasks = state_cache.tasks_by_category_and_operation_id[active_category_id][active_operation_id]
            for task_id, task_state, _ in tasks:
                if task_state == TaskState.BLOCKED:
                    self._unblock_task(state_cache, active_category_id, active_operation_id, task_id)

    def unblock_task(self, category_id, operation_id, task_id):
        with self.state_cache.Lock() as state_cache:
            self._unblock_task(state_cache, category_id, operation_id, task_id)

    def _unblock_task(self, state_cache, category_id, operation_id, task_id):
        self.manager.unblock_task(category_id, operation_id, task_id)
        skipped = self._skip_client_task_if_appropriate(category_id, operation_id, task_id)
        old_state = TaskState.BLOCKED
        new_state = TaskState.SKIPPED if skipped else TaskState.ACTIVE
        transition_task(state_cache, category_id, operation_id, task_id, old_state, new_state)

    def _unlock_first_task_in_operation(self, state_cache, category_id, operation_id):
        tasks = state_cache.tasks_by_category_and_operation_id[category_id][operation_id]
        if not tasks:
            return
        for task_id, from_state, task_progress in state_cache.tasks_by_category_and_operation_id[category_id][operation_id]:
            if not util.is_task_finished(from_state):
                self._unlock_task(state_cache, category_id, operation_id, task_id)
                return

    def unblock_first_task_in_active_operation(self, state_cache):
        category_id = state_cache.active_category_id
        operation_id = state_cache.active_operation_id
        if category_id is None or operation_id is None:
            return
        tasks = state_cache.tasks_by_category_and_operation_id[category_id][operation_id]
        if not tasks:
            return
        for task_id, from_state, task_progress in state_cache.tasks_by_category_and_operation_id[category_id][operation_id]:
            if not util.is_task_finished(from_state):
                task_index = get_task_index(state_cache, category_id, operation_id, task_id)
                state_cache.tasks_by_category_and_operation_id[category_id][operation_id][task_index] = (task_id, TaskState.ACTIVE, task_progress)
                self.manager.unblock_task(category_id, operation_id, task_id)
                scatter_transition(category_id, operation_id, task_id, from_state, TaskState.ACTIVE)
                return

    def _complete_operation(self, state_cache, operation_node):
        operation_node.complete()
        is_activating_next = False
        next_nodes = operation_node.get_nodes_to_activate_on_completion()
        if next_nodes:
            interested, not_interested = next_nodes[0], next_nodes[1:]
            if interested.category_id is not None and interested.operation_id is not None:
                is_activating_next = True
            self.set_active_operation(state_cache, interested.category_id, interested.operation_id)
            for node in not_interested:
                self.set_operation_state(state_cache, node.category_id, node.operation_id, OperationState.LOCKED)

        if not is_activating_next:
            state_cache.active_operation_id = None
            sm.ScatterEvent('OnOperationCompleted', operation_node.category_id, operation_node.operation_id)
        self.set_cached_operation_completed(operation_node.category_id, operation_node.operation_id)

    def unlock_active_operation(self):
        with self.state_cache.Lock() as state_cache:
            active_category_id = state_cache.active_category_id
            active_operation_id = state_cache.active_operation_id
            if active_operation_id is not None:
                self._unlock_first_task_in_operation(state_cache, active_category_id, active_operation_id)

    def _advance_operation_task_for_node(self, state_cache, operation_node, task_id):
        category_id = operation_node.category_id
        operation_id = operation_node.operation_id
        task_index = find_task_index(state_cache, category_id, operation_id, task_id)
        if task_index is None:
            return
        if not self._advance_to_next_operation_task(state_cache, category_id, operation_id, task_id, task_index):
            self._complete_operation(state_cache, operation_node)

    def OnOperationTaskCompleted(self, category_id, operation_id, task_id):
        with self.state_cache.Lock() as state_cache:
            if state_cache.tree_keeper is None:
                return
            PlaySound(uiconst.SOUND_ADD_OR_USE)
            trees = state_cache.tree_keeper.get_progress_trees_for_category(category_id)
            for tree in trees:
                operation_node = tree.get_node_by_operation_id(operation_id)
                if operation_node is not None and operation_node.state != OperationState.LOCKED:
                    transition_task_from_any(state_cache, category_id, operation_id, task_id, TaskState.COMPLETE)
                    self._advance_operation_task_for_node(state_cache, operation_node, task_id)

    def _force_hide_active_conversation(self):
        sm.GetService('operationsEventDirector').force_hide_active_conversation()

    def OnOperationSkipped(self, category_id, operation_id):
        self._force_hide_active_conversation()
        with self.state_cache.Lock() as state_cache:
            if state_cache.tree_keeper is None:
                return
            trees = state_cache.tree_keeper.get_progress_trees_for_category(category_id)
            for tree in trees:
                operation_node = tree.get_node_by_operation_id(operation_id)
                if operation_node is not None:
                    self._complete_operation(state_cache, operation_node)

    def OnOperationCategoryChanged(self, new_category_id, new_operation_id):
        with self.state_cache.Lock() as state_cache:
            if state_cache.tree_keeper is None:
                return
            if new_category_id == state_cache.active_category_id:
                return
            self._force_hide_active_conversation()
            self.set_active_operation(state_cache, new_category_id, new_operation_id)
            sm.ScatterEvent('OnOperationCategoryUpdated', new_category_id)

    def OnOperationTaskSkipped(self, task_list, includes_current):
        with self.state_cache.Lock() as state_cache:
            if state_cache.tree_keeper is None:
                return
            operation_node = None
            task_id = None
            for skipped_task in task_list:
                category_id, operation_id, task_id, _ = skipped_task
                trees = state_cache.tree_keeper.get_progress_trees_for_category(category_id)
                for tree in trees:
                    operation_node = tree.get_node_by_operation_id(operation_id)
                    if operation_node is not None:
                        transition_task_from_any(state_cache, category_id, operation_id, task_id, TaskState.SKIPPED)
                        break

            if operation_node is not None and task_id is not None and includes_current:
                self._advance_operation_task_for_node(state_cache, operation_node, task_id)

    def can_undock(self):
        operation_module_requirements = self.get_active_operation_module_requirements()
        if not operation_module_requirements:
            return True
        return can_undock(operation_module_requirements)

    def OnOperationsProgressReset(self, items_to_lock, items_to_skip, task_to_activate):
        self._force_hide_active_conversation()
        category_to_activate_id, operation_to_activate_id, task_to_activate_id = task_to_activate
        with self.state_cache.Lock() as state_cache:
            if state_cache.tree_keeper is None:
                return
            should_activate_task = all([category_to_activate_id, operation_to_activate_id, task_to_activate_id])
            if should_activate_task:
                transition_task_from_any(state_cache, category_to_activate_id, operation_to_activate_id, task_to_activate_id, TaskState.LOCKED)
            func_store_operation = None
            func_store_task = lambda character_id, category_id, operation_id, task_id, task_state, task_progress: transition_task_from_any(state_cache, category_id, operation_id, task_id, task_state)
            state_cache.tree_keeper.lock_items(self.character_id, items_to_lock, func_store_operation, func_store_task)
            state_cache.tree_keeper.skip_items(self.character_id, items_to_skip, func_store_operation, func_store_task)
            if should_activate_task:
                state_cache.tree_keeper.activate_items(self.character_id, task_to_activate, self.operation_cache)
                active_operation = self.operation_cache.get_operation_by_id(operation_to_activate_id)
                is_silent = task_to_activate_id != active_operation.get_first_task_id()
                self.set_active_operation(state_cache, category_to_activate_id, operation_to_activate_id, is_silent=is_silent)
                transition_task_from_any(state_cache, category_to_activate_id, operation_to_activate_id, task_to_activate_id, TaskState.ACTIVE)
            else:
                self.set_active_operation(state_cache, None, None)

    def has_progressed_in_category(self, category_id):
        category = self.operation_cache.get_operation_category_by_id(category_id)
        first_operation_ids = category.get_head_operation_ids()
        with self.state_cache.Lock() as state_cache:
            for operation_id in first_operation_ids:
                task_id, task_state, task_progress = state_cache.tasks_by_category_and_operation_id[category_id][operation_id][0]
                if util.is_task_finished(task_state):
                    return True

        return False

    def activate_operation(self, category_id, operation_id):
        if not IsKnownSpaceSystem(session.solarsystemid2):
            raise FailedToActivateInUnknownSpace()
        operation = self.operation_cache.get_operation_by_id(operation_id)
        has_been_completed = self.has_operation_ever_been_completed(category_id, operation_id)
        if not operation.isReplayable and has_been_completed:
            raise OperationNotReplayable('Operation is not replayable')
        if not self.are_operation_prerequisites_met(category_id, operation_id):
            raise FailedToActivateDueToPrerequisites('Prerequisites for operation not met')
        operation_state = self.get_operation_state(category_id, operation_id)
        if util.is_operation_active(operation_state) and not self.should_reset_operation():
            raise ReplayCancelledByUser('User cancelled replaying the operation')
        success = self.manager.activate_operation_in_solar_system(category_id, operation_id)
        if not success:
            raise FailedToActivateByServer('Server failed to activate operation')

    def should_reset_operation(self):
        return eve.Message(REPLAY_WARNING_DIALOG_ID, buttons=YESNO, suppress=ID_YES) == ID_YES

    def has_operation_ever_been_completed(self, category_id, operation_id):
        self.prime_operations_completed_at_least_once_cache(category_id)
        return operation_id in self.operations_completed_at_least_once[category_id]

    def set_cached_operation_completed(self, category_id, operation_id):
        self.prime_operations_completed_at_least_once_cache(category_id)
        self.operations_completed_at_least_once[category_id].add(operation_id)

    def prime_operations_completed_at_least_once_cache(self, category_id):
        if category_id not in self.operations_completed_at_least_once:
            operations = self.manager.get_operations_completed_at_least_once(category_id)
            self.operations_completed_at_least_once[category_id] = set(operations)

    def is_category_complete(self, category_id):
        return self.manager.is_category_complete(category_id)

    def get_category_state(self, category_id):
        return self.manager.get_category_state(category_id)

    def get_active_inventory_manipulation_tasks(self):
        task_tuples = self.get_active_task_tuples()
        tasks = []
        for task_id, task_state, task_progress in task_tuples:
            task = self.operation_cache.get_task_by_id(task_id)
            if task.achievementEventType == AchievementEventConst.CLIENT_ITEM_IN_MOVED_TO:
                tasks.append(task)

        return tasks

    def get_active_tasks(self):
        tasks = []
        for task_id, task_state, task_progress in self.get_active_task_tuples():
            tasks.append(self.operation_cache.get_task_by_id(task_id))

        return tasks

    def are_operation_prerequisites_met(self, category_id, operation_id):
        return util.are_operation_prerequisites_met(category_id, operation_id, self.operation_cache, self.has_operation_ever_been_completed)

    def is_mission_avoidance_system(self, solar_system_id):
        if self.mission_avoidance_systems is None:
            self.mission_avoidance_systems = self.manager.get_mission_avoidance_systems()
        return solar_system_id in self.mission_avoidance_systems

    def get_conversation_on_task_start(self, taskID):
        return self.operation_cache.get_conversation_on_task_start(taskID)

    def get_conversation_on_task_end(self, taskID):
        return self.operation_cache.get_conversation_on_task_end(taskID)

    def get_skill_rewards(self, operation, race_id):
        return self.operation_cache.get_skill_rewards(operation, race_id)

    def get_active_task_id(self):
        tasks = self.get_active_task_tuples()
        if tasks:
            task_id, _, _ = tasks[0]
            return task_id

    def get_task_by_id(self, task_id):
        return self.operation_cache.get_task_by_id(task_id)

    def get_tasks_in_operation(self, operation_id):
        return self.operation_cache.get_tasks_in_operation(operation_id)

    def get_completion_rewards(self, operation, race_id):
        return self.operation_cache.get_completion_rewards(operation, race_id)

    def OnOperationCategoryCompleted(self, categoryID):
        sm.ScatterEvent('OnOperationCategoryUpdated', categoryID)

    def OnOperationDeactivated(self):
        self._initialize_state_for_character(session.charid)
        sm.ScatterEvent('OnOperationDeactivatedUpdate')

    def OnOperationsServerFSDReload(self):
        self.on_fsd_reload()


operationsController = None

def GetOperationsController():
    global operationsController
    if operationsController is None:
        operationsController = OperationsController(EventDirectorOperationCache())
        operationsController.initialize(session.charid)
    return operationsController


def ReleaseOperationsController():
    global operationsController
    if operationsController is not None:
        operationsController.release()
        del operationsController
        operationsController = None
