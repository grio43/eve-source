#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\__init__.py
from behaviors import status
from behaviors.tasks import Task

class ToggleAction(Task):

    def OnEnter(self):
        self.SetStatusToSuccessIfTrueElseToFailed(self.attributes.trueOrFalse)


class WaitAction(Task):

    def OnEnter(self):
        self.status = status.TaskSuspendedStatus


class AutoFailAction(Task):

    def OnEnter(self):
        self.status = status.TaskFailureStatus
