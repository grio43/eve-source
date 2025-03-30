#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\decorators\modifiers.py
from behaviors import status
from behaviors.decorators import Decorator
from ccpProfile import TimedFunction

class Not(Decorator):

    def DoSubTaskCompleted(self, task):
        if task.status is status.TaskSuccessStatus:
            self.status = status.TaskFailureStatus
        elif task.status is status.TaskFailureStatus:
            self.status = status.TaskSuccessStatus


class ForceFailure(Decorator):

    def DoSubTaskCompleted(self, task):
        self.status = status.TaskFailureStatus


class ForceSuccess(Decorator):

    def DoSubTaskCompleted(self, task):
        self.status = status.TaskSuccessStatus


class Uninterruptible(Decorator):

    @TimedFunction('behaviors::decorators::modifiers::Uninterruptible::OnEnter')
    def OnEnter(self):
        super(Uninterruptible, self).OnEnter()
        self.status = status.TaskBlockingStatus
        self.behaviorTree.BlockReset(self)

    def OnExit(self):
        self.behaviorTree.UnblockReset(self)

    def DoSubTaskCompleted(self, task):
        self.status = task.status


class Invulnerable(Decorator):

    @TimedFunction('behaviors::decorators::modifiers::Invulnerable::OnEnter')
    def OnEnter(self):
        super(Invulnerable, self).OnEnter()
        self.MakeSelfInvulnerable()

    def MakeSelfInvulnerable(self):
        self.context.ballpark.MakeInvulnerablePermanently(self.context.myBall.id, self.attributes.reason)

    def OnExit(self):
        self.CancelInvulnerabilityForSelf()

    def CleanUp(self):
        if not self.IsInvalid():
            self.CancelInvulnerabilityForSelf()
        super(Invulnerable, self).CleanUp()

    def CancelInvulnerabilityForSelf(self):
        self.context.ballpark.CancelCurrentInvulnerability(self.context.myBall.id, self.attributes.reason)


class Cloaked(Decorator):

    @TimedFunction('behaviors::decorators::modifiers::Cloaked::OnEnter')
    def OnEnter(self):
        super(Cloaked, self).OnEnter()
        self.CloakShip()

    def CloakShip(self):
        self.context.ballpark.CloakShip(self.context.myItemId)

    def OnExit(self):
        self.UncloakShip()

    def CleanUp(self):
        if not self.IsInvalid():
            self.UncloakShip()
        super(Cloaked, self).CleanUp()

    def UncloakShip(self):
        self.context.ballpark.UncloakShip(self.context.myItemId)


class OneShot(Decorator):

    def OnEnter(self):
        if self.GetLastBlackboardValue(self.attributes.oneShotTriggeredFlagAddress):
            self.SetStatusToSuccess()
        else:
            self.set_one_shot_triggered()
            super(OneShot, self).OnEnter()

    def set_one_shot_triggered(self):
        if not self.GetLastBlackboardValue(self.attributes.oneShotTriggeredFlagAddress):
            self.SendBlackboardValue(self.attributes.oneShotTriggeredFlagAddress, True)
