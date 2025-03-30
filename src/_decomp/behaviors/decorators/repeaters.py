#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\decorators\repeaters.py
from behaviors import status
from behaviors.decorators import Decorator
from ccpProfile import TimedFunction

class RepeatWhileFailing(Decorator):

    @TimedFunction('behaviors::decorators::repeaters::RepeatWhileFailing::OnEnter')
    def OnEnter(self):
        super(RepeatWhileFailing, self).OnEnter()
        self.repetitions = self.attributes.maxRepetitions

    @TimedFunction('behaviors::decorators::repeaters::RepeatWhileFailing::DoSubTaskCompleted')
    def DoSubTaskCompleted(self, task):
        if task.status is status.TaskSuccessStatus:
            self.SetStatusToSuccess()
        else:
            self.repetitions -= 1
            if self.repetitions > 0:
                task.CleanUp()
                self.behaviorTree.StartTaskNextTick(task)
            else:
                self.SetStatusToFailed()
