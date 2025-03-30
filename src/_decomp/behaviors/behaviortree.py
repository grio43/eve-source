#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\behaviortree.py
from collections import deque
import gametime
from ccpProfile import TimedFunction
import logging
import signals
from eveexceptions.exceptionEater import ExceptionEater
logger = logging.getLogger(__name__)
TICK_END_MARKER = None
MESSAGE_REQUEST_RESET = 'OnRequestReset'
MESSAGE_STEP = 'OnStep'
MESSAGE_RESET = 'OnReset'
MESSAGE_TICK_DONE = 'OnTickDone'
MESSAGE_BLOCK_RESET = 'OnBlockReset'

class UnrecoverableBehaviorError(Exception):
    pass


class BehaviorTree(object):

    def __init__(self, behaviorId = None, scopeType = None):
        self.behaviorId = behaviorId
        self.scopeType = scopeType
        self._tasks = deque()
        self._rootTask = None
        self._isResetRequested = False
        self._isResetBlocked = False
        self._messenger = signals.Messenger()

    def Release(self):
        with ExceptionEater('CleanUp behavior tree'):
            if self._rootTask is not None:
                self._rootTask.CleanUp()
                logger.debug('Cleaned up behaviors for behaviortree')
        self._rootTask = None
        self._messenger = None

    def StartRootTask(self, rootTask):
        self._rootTask = rootTask
        rootTask.SetExitObserver(self.OnRootTaskTerminated)
        self.StartTask(rootTask)

    def AddEndMarker(self):
        self._tasks.append(TICK_END_MARKER)

    def StartTask(self, task):
        self._tasks.appendleft(task)

    def StartTaskNextTick(self, task):
        self._tasks.append(task)

    def GetTaskList(self):
        return list(self._tasks)

    def GetRootTask(self):
        return self._rootTask

    @TimedFunction('behaviors::behaviortree::BehaviorTree::Tick')
    def Tick(self, context):
        startTime = gametime.GetWallclockTimeNow()
        self.ProcessResetRequest()
        self.AddEndMarker()
        while self.Step(context):
            pass

        self.SendMessage(MESSAGE_TICK_DONE, context)
        updateTime = gametime.GetWallclockTimeNow() - startTime
        context.statistics.update(updateTime)

    @TimedFunction('behaviors::behaviortree::BehaviorTree::Step')
    def Step(self, context):
        task = self._tasks.popleft()
        moreTasks = True
        if task is TICK_END_MARKER:
            moreTasks = False
        else:
            task.Tick(self, context)
            context.statistics.add_tick()
        self.SendMessage(MESSAGE_STEP, task=task)
        return moreTasks

    def BlockReset(self, blockingTask):
        self._SetBlockReset(True, blockingTask)

    def UnblockReset(self, blockingTask):
        self._SetBlockReset(False, blockingTask)

    def _SetBlockReset(self, isBlocking, blockingTask):
        self.SendMessage(MESSAGE_BLOCK_RESET, isBlocking, blockingTask)
        self._isResetBlocked = isBlocking

    def RequestReset(self, requestedBy = None):
        logger.debug("requested reset for behavior=%s by task=%s name='%s'", self.behaviorId, requestedBy.__class__.__name__, getattr(getattr(requestedBy, 'attributes', None), 'name', None))
        self._isResetRequested = True
        self.SendMessage(MESSAGE_REQUEST_RESET, requestedBy=requestedBy)
        self._UpdateStatistics(requestedBy)

    def _UpdateStatistics(self, requestedBy):
        self.GetRootTask().context.statistics.update_request_reset(requestedBy)

    @TimedFunction('behaviors::behaviortree::BehaviorTree::Reset')
    def Reset(self):
        self._tasks.clear()
        self._rootTask.CleanUp()
        self.StartTask(self._rootTask)
        self.SendMessage(MESSAGE_RESET)

    def ProcessResetRequest(self):
        if self._isResetRequested and not self._isResetBlocked:
            self._isResetRequested = False
            self.Reset()

    def HasResetRequest(self):
        return self._isResetRequested

    def OnRootTaskTerminated(self, rootTask):
        self.RequestReset(requestedBy=rootTask)

    def GetMessenger(self):
        return self._messenger

    def SendMessage(self, messageName, *args, **kwargs):
        self._messenger.SendMessage(messageName, *args, **kwargs)

    def GetBehaviorId(self):
        return self.behaviorId
