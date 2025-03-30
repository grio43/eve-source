#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\composites\__init__.py
from behaviors import status
from behaviors.tasks import Task
from ccpProfile import TimedFunction

class Composite(Task):

    def __init__(self, attributes = None):
        super(Composite, self).__init__(attributes)
        self._subTasks = []

    @TimedFunction('behaviors::composites::Composite::OnEnter')
    def OnEnter(self):
        if not self._subTasks:
            raise NoSubTasksError()
        self.SetStatusToSuspended()
        self.behaviorTree.StartTask(self.GetInitialTask())

    def GetInitialTask(self):
        return self._subTasks[0]

    def AddSubTask(self, task):
        task.SetExitObserver(self.OnSubTaskCompleted)
        self._subTasks.append(task)
        return self

    @TimedFunction('behaviors::composites::Composite::OnSubTaskCompleted')
    def OnSubTaskCompleted(self, task):
        self.DoSubTaskCompleted(task)
        self.status.OnUpdated(self)

    def DoSubTaskCompleted(self, task):
        raise NotImplementedError

    def IsLastSubTask(self, task):
        return task is self._subTasks[-1]

    def GetNextSubTask(self, task):
        return self._subTasks[self._subTasks.index(task) + 1]

    def CleanUp(self):
        for subTask in self._subTasks:
            if subTask.status is not status.TaskInvalidStatus:
                subTask.CleanUp()

        self.SetStatusToInvalid()

    def GetSubTasks(self):
        return self._subTasks

    def HasSubTasks(self):
        return True

    def SubTaskCount(self):
        return len(self._subTasks)


class Sequence(Composite):

    def DoSubTaskCompleted(self, task):
        if task.status is status.TaskFailureStatus:
            self.SetStatusToFailed()
        elif self.IsLastSubTask(task):
            self.SetStatusToSuccess()
        else:
            self.behaviorTree.StartTask(self.GetNextSubTask(task))


class PrioritySelector(Composite):

    def DoSubTaskCompleted(self, task):
        if task.status is status.TaskSuccessStatus:
            self.SetStatusToSuccess()
        elif self.IsLastSubTask(task):
            self.SetStatusToFailed()
        else:
            self.behaviorTree.StartTask(self.GetNextSubTask(task))


class NoSubTasksError(Exception):
    pass
