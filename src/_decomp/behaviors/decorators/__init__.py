#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\decorators\__init__.py
from behaviors import status
from behaviors.composites import Composite, NoSubTasksError
from ccpProfile import TimedFunction

class Decorator(Composite):

    @TimedFunction('behaviors::decorators::Decorator::OnEnter')
    def OnEnter(self):
        if not self._subTasks:
            raise NoSubTasksError()
        if len(self._subTasks) > 1:
            raise TooManySubTasksError()
        self.SetStatusToSuspended()
        self.behaviorTree.StartTask(self.GetDecoratedTask())

    def DoSubTaskCompleted(self, task):
        self.status = task.status

    def GetDecoratedTask(self):
        return self._subTasks[0]


class TooManySubTasksError(Exception):
    pass
