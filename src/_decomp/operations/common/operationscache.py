#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\operationscache.py
from eve.common.lib import appConst
from fsdBuiltData.common.achievementEvents import AchievementEvents
from operations.common.const import OPERATION_CATEGORY_CAPSULE_DEATH
from operations.common.const import OPERATION_CATEGORY_SHIP_DEATH
from operations.common.const import TASK_DELAY_BEFORE_DEFAULT
from operations.common.exceptions import NoTasksAvailableInOperation
from operations.common.fsdloaders import OperationsLoader
from operations.common.fsdloaders import OperationTasksLoader
from operations.common.fsdloaders import OperationCategoriesLoader
from operations.common.fsdloaders import OperationTreeStructuresLoader
from operations.common.fsdloaders import get_all_operation_categories
from operations.common.operationObjects import Task, Operation, OperationCategory
import logging
from signals import Signal
logger = logging.getLogger(__name__)

class OperationCache(object):

    def __init__(self):
        self.death_operations = None
        self.operations = {}
        self.operation_tasks = {}
        self.operation_categories = {}
        OperationsLoader.ConnectToOnReload(self._on_fsd_reload)
        OperationTasksLoader.ConnectToOnReload(self._on_fsd_reload)
        OperationCategoriesLoader.ConnectToOnReload(self._on_fsd_reload)
        self.on_fsd_reload = Signal()

    def _on_fsd_reload(self):
        self.operations.clear()
        self.operation_tasks.clear()
        self.operation_categories.clear()
        self.on_fsd_reload()

    def load_task_by_id(self, id):
        task = OperationTasksLoader.GetByID(id)
        if task is None:
            self.operation_tasks[id] = None
            return
        taskHint = task.taskHint
        isOptional = task.isOptional
        isSupreme = task.isSupreme
        isCheckpoint = task.isCheckpoint
        isSiteRelevant = task.isSiteRelevant
        serverSkipConditions = task.serverSkipConditions
        clientSkipConditions = task.clientSkipConditions
        completionRewards = task.onCompletionRewards
        delayBefore = task.delayBefore if task.delayBefore is None else TASK_DELAY_BEFORE_DEFAULT
        dungeonBlackboardMessages = task.dungeonBlackboardMessages
        return Task(id, task.name, task.title, task.description, taskHint, AchievementEvents.GetName(task.achievementEventType), task.targetValue, task.eventConditions, serverSkipConditions, clientSkipConditions, isOptional, isSupreme, isCheckpoint, isSiteRelevant, completionRewards, delayBefore, dungeonBlackboardMessages=dungeonBlackboardMessages)

    def get_task_by_id(self, taskID):
        try:
            task = self.operation_tasks[taskID]
        except KeyError:
            task = self.load_task_by_id(taskID)
            self.operation_tasks[taskID] = task

        return task

    def _read_module_requirements_in_operation(self, operation):
        return {appConst.raceAmarr: operation.amarrModuleRequirements or [],
         appConst.raceCaldari: operation.caldariModuleRequirements or [],
         appConst.raceGallente: operation.gallenteModuleRequirements or [],
         appConst.raceMinmatar: operation.minmatarModuleRequirements or []}

    def load_operation_by_id(self, id):
        operation = OperationsLoader.GetByID(id)
        if operation is None:
            return
        task_list = self._load_sorted_task_list(operation.tasksInOperation)
        item_activation_rewards = operation.onActivationRewards
        item_completion_rewards = operation.onCompletionRewards
        skill_rewards = operation.skillRewards
        module_requirements = self._read_module_requirements_in_operation(operation)
        site_id = operation.siteConnection
        operation_prerequisites = operation.operationPrerequisites
        function_description = operation.functionDescription
        notificationTitle = operation.notificationTitle
        notificationDescription = operation.notificationDescription
        musicTrigger = operation.musicTrigger
        return Operation(operation.title, operation.description, operation.iskReward, item_activation_rewards, item_completion_rewards, skill_rewards, module_requirements, notificationTitle, notificationDescription, task_list, operationID=id, isReplayable=operation.isReplayable, siteID=site_id, operationPrerequisites=operation_prerequisites, functionDescription=function_description, name=operation.name, musicTrigger=musicTrigger)

    def _read_tasks_in_operation(self, operation):
        tasks_in_operation_data = operation.tasksInOperation
        if len(tasks_in_operation_data) < 1:
            return {}
        return tasks_in_operation_data[0]

    def _load_sorted_task_list(self, task_id_list):
        task_list = []
        for task_id in task_id_list:
            task = self.load_task_by_id(task_id)
            if task is not None:
                task_list.append(task)

        return task_list

    def get_operation_by_id(self, id):
        try:
            operation = self.operations[id]
        except KeyError:
            operation = self.load_operation_by_id(id)
            self.operations[id] = operation

        return operation

    def _load_operation_tree(self, tree_id):
        tree = OperationTreeStructuresLoader.GetByID(tree_id)
        if tree is None:
            logger.error('Tree with id %s does not exist.' % tree_id)
            return {}
        return (tree_id, tree.connections)

    def load_operation_category_by_id(self, category_id):
        operation_category = OperationCategoriesLoader.GetByID(category_id)
        if operation_category is None:
            return
        operation_tree_data = [ self._load_operation_tree(tree_id) for tree_id in operation_category.operationTrees ]
        return OperationCategory(operation_category.title, operation_category.description, operation_category.iconPath, operation_category.iskReward, operation_category.notificationTitle, operation_category.notificationDescription, operation_tree_data, categoryID=category_id)

    def get_operation_category_by_id(self, id):
        try:
            category = self.operation_categories[id]
        except KeyError:
            category = self.load_operation_category_by_id(id)
            self.operation_categories[id] = category

        return category

    def get_operations_for_category(self, category):
        return {index:self.get_operation_by_id(operation_id) for index, operation_id in enumerate(category.iter_operation_ids(), 1)}

    def get_tasks_in_operation(self, operation_id):
        op = self.get_operation_by_id(operation_id)
        return op.taskList

    def get_tasks_in_category(self, category_id):
        category = self.get_operation_category_by_id(category_id)
        operations = self.get_operations_for_category(category)
        task_ids = []
        for operation in operations.values():
            task_ids.extend([ task.id for task in self.get_tasks_in_operation(operation.operationID) ])

        return task_ids

    def is_operation_in_category(self, category_id, operation_id):
        category = self.get_operation_category_by_id(category_id)
        operations = self.get_operations_for_category(category)
        for operation in operations.values():
            if operation.operationID == operation_id:
                return True

        return False

    def get_all_categories(self):
        categories_list = []
        for category_id in get_all_operation_categories():
            categories_list.append(self.get_operation_category_by_id(category_id))

        return categories_list

    def get_all_operations(self):
        operations = []
        for operation_id in OperationsLoader.GetData():
            operations.append(self.get_operation_by_id(operation_id))

        return operations

    def get_all_tasks(self):
        task_list = []
        for task_id in OperationTasksLoader.GetData():
            task_list.append(self.get_task_by_id(task_id))

        return task_list

    def get_first_task_in_operation(self, operation_id):
        task_list = self.get_tasks_in_operation(operation_id)
        if not task_list:
            raise NoTasksAvailableInOperation('No tasks found, failed to get first task in operation', operation_id)
        return task_list[0]

    def get_category_id_by_site(self, site_id):
        all_categories = self.get_all_categories()
        for category in all_categories:
            operations = self.get_operations_for_category(category)
            for operation in operations.values():
                if operation.siteID == site_id:
                    return category.categoryID

    def get_operation_id_by_site(self, site_id):
        operations = self.get_all_operations()
        for operation in operations:
            if operation.siteID == site_id:
                return operation.operationID

    def get_category_id_for_ship_death(self):
        return OPERATION_CATEGORY_SHIP_DEATH

    def get_category_id_for_capsule_death(self):
        return OPERATION_CATEGORY_CAPSULE_DEATH

    def get_operation_index(self, category_id, operation_id):
        category = self.get_operation_category_by_id(category_id)
        operations = self.get_operations_for_category(category)
        for operation_index, operation in operations.items():
            if operation_id == operation.operationID:
                return operation_index

    def get_task_index(self, operation_id, task_id):
        tasks = self.get_tasks_in_operation(operation_id)
        for task_index, task in enumerate(tasks):
            if task_id == task.id:
                return task_index

    def _filter_values_by_race(self, dictToFilter, raceID):
        return [ v for v in dictToFilter if v.raceID in [None, raceID] ]

    def get_rewards_info(self, raceID):
        rewards_info = {}
        categories = self.get_all_categories()
        for category in categories:
            category_id = category.categoryID
            category_title = category.title
            operations = self.get_operations_for_category(category)
            rewards_info[category_id] = {}
            for operation_index, operation in operations.items():
                operation_id = operation.operationID
                operation_title = operation.title
                isk_reward = operation.iskReward
                activation_rewards = self.get_activation_rewards(operation, raceID)
                completion_rewards = self.get_completion_rewards(operation, raceID)
                rewards_info[category_id][operation_index] = {'category_title': category_title,
                 'operation_id': operation_id,
                 'operation_title': operation_title,
                 'isk_reward': isk_reward,
                 'activation_rewards': activation_rewards,
                 'completion_rewards': completion_rewards}

        return rewards_info

    def get_skill_rewards_info(self, raceID):
        skill_rewards_info = {}
        categories = self.get_all_categories()
        for category in categories:
            category_id = category.categoryID
            operations = self.get_operations_for_category(category)
            for operation_index, operation in operations.items():
                skill_rewards = self.get_skill_rewards(operation, raceID)
                if skill_rewards:
                    if category_id not in skill_rewards_info:
                        skill_rewards_info[category_id] = {}
                    skill_rewards_info[category_id][operation_index] = {'category_title': category.title,
                     'operation_id': operation.operationID,
                     'operation_title': operation.title,
                     'skill_rewards': skill_rewards}

        return skill_rewards_info

    def get_activation_rewards(self, operation, raceID):
        return self._filter_values_by_race(operation.itemActivationRewards, raceID)

    def get_completion_rewards(self, operation, raceID):
        return self._filter_values_by_race(operation.itemCompletionRewards, raceID)

    def get_skill_rewards(self, operation, raceID):
        return self._filter_values_by_race(operation.skillRewards, raceID)
