#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\tasks.py
import weakref
from collections import defaultdict
from behaviors import status
from behaviors.blackboards import scopes, BlackboardDeletedError
from behaviors.blackboards.scopes import ItemScope
from brennivin.itertoolsext import Bundle
from ccpProfile import TimedFunction
import weakness
import logging
logger = logging.getLogger(__name__)

class TaskAttributeMissingError(Exception):
    pass


class Task(object):
    __attributes__ = {}

    def __init__(self, attributes = None):
        self.SetAttributes(attributes or Bundle())
        self.status = None
        self.SetStatusToInvalid()
        self.exitObserver = None
        self.context = None
        self.behaviorTree = None

    def OnEnter(self):
        self.SetStatusToRunning()

    def OnExit(self):
        pass

    def Update(self):
        pass

    def CleanUp(self):
        self.SetStatusToInvalid()

    def Tick(self, behaviorTree, context):
        if self.status is status.TaskInvalidStatus:
            self.SetEnvironment(behaviorTree, context)
            self.OnEnter()
        self.Update()
        self.OnStatusUpdate()

    def NotifyExited(self):
        if self.exitObserver:
            self.exitObserver(self)

    def SetExitObserver(self, exitObserver):
        self.exitObserver = weakness.callable_proxy(exitObserver)

    def Exit(self):
        self.NotifyExited()
        self.OnExit()

    def SetAttributes(self, attributes):
        self.attributes = attributes

    def HasSubTasks(self):
        return False

    def SetEnvironment(self, behaviorTree, context):
        self.behaviorTree = weakref.proxy(behaviorTree)
        self.context = weakref.proxy(context)

    def GetChannelFromAddress(self, address):
        channel_cache = self.context.task_channel_cache[self]
        if address in channel_cache:
            return channel_cache[address]
        else:
            channel = scopes.GetChannelFromAddress(self.context, address)
            channel_cache[address] = channel
            return channel

    @TimedFunction('behaviors::tasks::Task::GetLastBlackboardValue')
    def GetLastBlackboardValue(self, address):
        return self.GetChannelFromAddress(address).GetLastMessageValue()

    def GetLastBlackboardValueWithMaxAge(self, address, maxAge):
        return self.GetChannelFromAddress(address).GetLastMessageValueWithMaxAge(maxAge)

    @TimedFunction('behaviors::tasks::Task::SendBlackboardValue')
    def SendBlackboardValue(self, address, value):
        return self.GetChannelFromAddress(address).SendMessage(value)

    def SubscribeToBlackboard(self, address, handler):
        self.GetChannelFromAddress(address).AddObserver(handler)

    def UnsubscribeToBlackboard(self, address, handler):
        try:
            self.GetChannelFromAddress(address).RemoveObserver(handler)
        except BlackboardDeletedError:
            pass

    def GetEventMessenger(self):
        return self.context.ballpark.eventMessenger

    def SubscribeItem(self, itemID, messageId, handler):
        self.GetEventMessenger().SubscribeItem(itemID, messageId, handler)

    def UnsubscribeItem(self, itemID, messageId, handler):
        try:
            self.GetEventMessenger().UnsubscribeItem(itemID, messageId, handler)
        except ReferenceError:
            logger.debug('Unable to unsubscribe from message as behavior is probably dead and context reference is lost. (itemID=%s, messageId=%, handler=%s)', itemID, messageId, handler)

    def SetStatusToInvalid(self):
        self.status = status.TaskInvalidStatus

    def SetStatusToSuccess(self):
        self.status = status.TaskSuccessStatus

    def SetStatusToFailed(self):
        self.status = status.TaskFailureStatus

    def SetStatusToSuspended(self):
        self.status = status.TaskSuspendedStatus

    def SetStatusToRunning(self):
        self.status = status.TaskRunningStatus

    def SetStatusToBlocked(self):
        self.status = status.TaskBlockingStatus

    def IsInvalid(self):
        return self.status is status.TaskInvalidStatus

    def IsSuspended(self):
        return self.status == status.TaskSuspendedStatus

    def IsRunning(self):
        return self.status == status.TaskRunningStatus

    def IsSuccessful(self):
        return self.status == status.TaskSuccessStatus

    def IsFailed(self):
        return self.status == status.TaskFailureStatus

    def IsBlocked(self):
        return self.status == status.TaskBlockingStatus

    def SetStatusToSuccessIfTrueElseToFailed(self, value):
        if value:
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def GetMessageChannelForItemId(self, itemId, channelAddress):
        scope = ItemScope(itemId)
        return self.context.blackboardManager.GetBlackboard(scope).GetMessageChannel(channelAddress)

    def GetMessageChannelForGroupId(self, groupId, channelAddress):
        scope = scopes.EntityGroupScope(groupId)
        return self.context.blackboardManager.GetBlackboard(scope).GetMessageChannel(channelAddress)

    def HasAttribute(self, attributeName):
        return hasattr(self.attributes, attributeName) and getattr(self.attributes, attributeName) is not None

    def GetTaskName(self):
        return type(self).__name__

    def GetContextValue(self, valueName):
        return self.context.task_cache[self].get(valueName)

    def SetContextValue(self, valueName, value):
        self.context.task_cache[self][valueName] = value

    def HasContextValue(self, valueName):
        return valueName in self.context.task_cache[self]

    def ResetBlackboardAddressCache(self):
        self.context.task_channel_cache = defaultdict(dict)

    def OnStatusUpdate(self):
        self.status.OnUpdated(self)


class BlockingTask(Task):

    def OnEnter(self):
        self.SetStatusToBlocked()
        self.behaviorTree.BlockReset(self)

    def OnExit(self):
        self.behaviorTree.UnblockReset(self)


class MonitorTask(Task):

    @TimedFunction('behaviors::tasks::MonitorTask::OnEnter')
    def OnEnter(self):
        item_id = self._get_item_id()
        if item_id is None:
            self.SetStatusToFailed()
            return
        self.SubscribeItem(self._get_item_id(), self._get_message(), self._self_process_message)
        self.SetStatusToSuccess()

    def _get_item_id(self):
        return self.context.myItemId

    def _get_message(self):
        raise NotImplementedError

    @TimedFunction('behaviors::tasks::MonitorTask::_self_process_message')
    def _self_process_message(self, *args):
        if self._can_process_message(*args):
            self.behaviorTree.RequestReset(requestedBy=self)

    def _can_process_message(self, *args):
        return True

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeItem(self._get_item_id(), self._get_message(), self._self_process_message)
            self.SetStatusToInvalid()
