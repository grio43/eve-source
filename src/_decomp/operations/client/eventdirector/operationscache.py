#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\client\eventdirector\operationscache.py
from fsdBuiltData.common.achievementEvents import AchievementEvents
from operations.common.const import TASK_DELAY_BEFORE_DEFAULT
from operations.common.fsdloaders import OperationTasksLoader, OperationsLoader
from operations.common.operationscache import OperationCache
from operations.common.operationObjects import Task, Operation

class EventDirectorTask(Task):

    def __init__(self, conversationOnTaskStarted, conversationOnTaskEnded, *args, **kwargs):
        Task.__init__(self, *args, **kwargs)
        self.conversationOnTaskStarted = conversationOnTaskStarted
        self.conversationOnTaskEnded = conversationOnTaskEnded


class EventDirectorOperationCache(OperationCache):

    def load_task_by_id(self, task_id):
        task = OperationTasksLoader.GetByID(task_id)
        if task is None:
            self.operation_tasks[task_id] = None
            return
        return EventDirectorTask(conversationOnTaskStarted=task.conversationOnTaskStarted, conversationOnTaskEnded=task.conversationOnTaskEnded, id=task_id, name=task.name, title=task.title, description=task.description, taskHint=task.taskHint, achievementEventType=AchievementEvents.GetName(task.achievementEventType), targetValue=task.targetValue, eventConditions=task.eventConditions, serverSkipConditions=task.serverSkipConditions, clientSkipConditions=task.clientSkipConditions, isOptional=task.isOptional, isSupreme=task.isSupreme, isCheckpoint=task.isCheckpoint, isSiteRelevant=task.isSiteRelevant, completionRewards=task.onCompletionRewards, delayBefore=task.delayBefore if task.delayBefore is None else TASK_DELAY_BEFORE_DEFAULT)

    def load_operation_by_id(self, operation_id):
        operation = OperationsLoader.GetByID(operation_id)
        if operation is None:
            return
        task_list = self._load_sorted_task_list(operation.tasksInOperation)
        item_activation_rewards = operation.onActivationRewards
        item_completion_rewards = operation.onCompletionRewards
        skill_rewards = operation.skillRewards
        module_requirements = self._read_module_requirements_in_operation(operation)
        site_id = operation.siteConnection
        return Operation(title=operation.title, description=operation.description, iskReward=operation.iskReward, itemActivationRewards=item_activation_rewards, itemCompletionRewards=item_completion_rewards, skillRewards=skill_rewards, moduleRequirements=module_requirements, notificationTitle=operation.notificationTitle, notificationDescription=operation.notificationDescription, taskList=task_list, operationID=operation_id, isReplayable=operation.isReplayable, siteID=site_id, operationPrerequisites=operation.operationPrerequisites, functionDescription=operation.functionDescription, musicTrigger=operation.musicTrigger)

    def get_conversation_on_task_start(self, task_id):
        task = self.get_task_by_id(task_id)
        return task.conversationOnTaskStarted

    def get_conversation_on_task_end(self, task_id):
        task = self.get_task_by_id(task_id)
        return task.conversationOnTaskEnded
