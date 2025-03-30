#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\debugging\behaviortreemonitor.py
from behaviors import behaviortree
import logging
from behaviors.blackboards import scopes, BlackboardDeletedError
from behaviors.composites import Composite
from behaviors.debugging.tools import DepthFirstTaskIterator
from cluster import SERVICE_BEYONCE
import gametime
logger = logging.getLogger(__name__)

class BehaviorTreeMonitor(object):
    __machoresolve__ = None

    def __init__(self, serviceManager, clientID, itemID):
        self.serviceManager = serviceManager
        self.clientID = clientID
        self.itemID = itemID
        self.behaviorTree = None
        self.events = []
        self.machoNet = serviceManager.GetService('machoNet')
        self.taskSeen = []

    def SendToClient(self, *args, **kwargs):
        self.machoNet.SinglecastByClientID(self.clientID, 'OnBehaviorDebugUpdate', self.itemID, *args, **kwargs)

    def AttachToBehaviorTree(self, behaviorTree):
        self.behaviorTree = behaviorTree
        messenger = self.behaviorTree.GetMessenger()
        messenger.SubscribeToMessage(behaviortree.MESSAGE_STEP, self.OnTreeStep)
        messenger.SubscribeToMessage(behaviortree.MESSAGE_RESET, self.OnTreeReset)
        messenger.SubscribeToMessage(behaviortree.MESSAGE_REQUEST_RESET, self.OnTreeResetRequest)
        messenger.SubscribeToMessage(behaviortree.MESSAGE_TICK_DONE, self.OnTickDone)
        messenger.SubscribeToMessage(behaviortree.MESSAGE_BLOCK_RESET, self.OnTreeSetBlockReset)
        self.serviceManager.RegisterForNotifyEvent(self, 'OnSessionDetach')
        self.serviceManager.RegisterForNotifyEvent(self, 'OnSessionChanged')

    def DetachFromBehaviorTree(self):
        if self.behaviorTree is None:
            return
        try:
            messenger = self.behaviorTree.GetMessenger()
            messenger.UnsubscribeFromMessage(behaviortree.MESSAGE_STEP, self.OnTreeStep)
            messenger.UnsubscribeFromMessage(behaviortree.MESSAGE_RESET, self.OnTreeReset)
            messenger.UnsubscribeFromMessage(behaviortree.MESSAGE_REQUEST_RESET, self.OnTreeResetRequest)
            messenger.UnsubscribeFromMessage(behaviortree.MESSAGE_TICK_DONE, self.OnTickDone)
            messenger.UnsubscribeFromMessage(behaviortree.MESSAGE_BLOCK_RESET, self.OnTreeSetBlockReset)
            self.serviceManager.UnregisterForNotifyEvent(self, 'OnSessionDetach')
            self.serviceManager.UnregisterForNotifyEvent(self, 'OnSessionChanged')
        except:
            logger.exception('Problem detaching debugger from the behavior for entity')
        finally:
            self.behaviorTree = None

    def OnSessionDetach(self):
        logger.warn('OnSessionDetach %s', session)
        if getattr(session, 'clientID', None) == self.clientID:
            self.DetachFromBehaviorTree()

    def OnSessionChanged(self, isRemote, sess, change):
        logger.warn('OnSessionChanged %s %s %s', isRemote, sess, change)
        if getattr(sess, 'clientID', None) == self.clientID and 'solarsystemid' in change:
            self.DetachFromBehaviorTree()

    def OnTreeReset(self):
        logger.debug('OnTreeReset')
        self.events.append((self.GetSimTime(), 'Reset', None))

    def OnTreeResetRequest(self, requestedBy):
        logger.debug('OnTreeResetRequest requestedBy=%s', requestedBy)
        self.events.append((self.GetSimTime(), 'RequestReset', id(requestedBy)))

    def OnTreeSetBlockReset(self, value, task):
        logger.debug('OnTreeSetBlockReset task=%s is %sblocking', task, '' if value else 'un-')
        self.events.append((self.GetSimTime(), 'SetBlockReset', (id(task), value)))

    def OnTreeStep(self, task):
        if task is not None:
            self.taskSeen.append(task)
        self.events.append((self.GetSimTime(), 'Step', id(task)))

    def OnTickDone(self, context):
        if self.behaviorTree is None:
            return
        events = self.events
        self.events = []
        taskStatuses = {id(t):t.status.__name__ for t in DepthFirstTaskIterator(self.behaviorTree.GetRootTask())}
        tasksSeen = [ id(t) for t in self.taskSeen ]
        del self.taskSeen[:]
        blackboards = GetBlackboards(context)
        self.SendToClient(events, taskStatuses, tasksSeen, blackboards)

    def GetTreeDump(self):
        return DumpTree(self.behaviorTree)

    def GetSimTime(self):
        return gametime.GetSimTime()

    def MachoResolve(self, session):
        result = None
        solarsystemid2 = session.GetSessionVariable('solarsystemid2')
        if solarsystemid2:
            result = self.machoNet.GetNodeFromAddress(SERVICE_BEYONCE, session.solarsystemid2)
        return result


def DumpTree(behaviorTree):
    taskList = []
    rootTask = behaviorTree.GetRootTask()
    RecursiveDumpTask(taskList, rootTask, 0)
    return taskList


def RecursiveDumpTask(taskList, task, depth):
    taskDict = DumpTask(task, depth)
    taskList.append(taskDict)
    if issubclass(task.__class__, Composite):
        subTasks = []
        for subTask in task.GetSubTasks():
            subTasks.append(id(subTask))
            RecursiveDumpTask(taskList, subTask, depth + 1)

        taskDict['subtasks'] = subTasks


def DumpTask(task, depth):
    return dict(type=task.__class__.__name__, id=id(task), attributes=get_attribute_dict(task), status=task.status.__name__, depth=depth)


def get_attribute_dict(task):
    if isinstance(task.attributes, dict):
        if task.attributes:
            return dict(task.attributes)
        return {}
    else:
        return dict(task.attributes._asdict())


def GetBlackboards(context):
    bbm = context.blackboardManager
    blackboards = {}
    for scopeType in scopes.ScopeTypes.values():
        if scopeType not in scopes.CONTEXT_ID_BY_SCOPE:
            continue
        scopeID = context.get(scopes.CONTEXT_ID_BY_SCOPE[scopeType])
        if scopeID is not None:
            scope = scopes.Scope(scopeType, scopeID)
            try:
                bb = bbm.GetBlackboard(scope)
            except BlackboardDeletedError:
                continue

            channels = []
            for channel in bb.GetMessageChannelList():
                message = channel.GetLastMessage()
                if message is None:
                    channels.append((channel.name, None, None))
                else:
                    channels.append((channel.name, message.time, message.value))

            blackboards[scope.scopeType, scope.id] = channels

    return blackboards
