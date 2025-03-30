#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\reinforcements.py
from ballpark.entities.reinforcementmanager import REINFORCEMENTS_AUTHORIZED, REINFORCEMENT_COOLDOWN, ReinforcedEntityGroupNotFoundError
from behaviors import status
from behaviors.behaviortree import UnrecoverableBehaviorError
from behaviors.blackboards import scopes, BlackboardDeletedError
from behaviors.tasks import Task
from ccpProfile import TimedFunction
REINFORCEMENTS_AUTHORIZED_ADDRESS = (scopes.ScopeTypes.EntityGroup, REINFORCEMENTS_AUTHORIZED)
REINFORCEMENT_COOLDOWN_ADDRESS = (scopes.ScopeTypes.EntityGroup, REINFORCEMENT_COOLDOWN)

class AreReinforcementsAuthorizedMonitor(Task):

    @TimedFunction('behaviors::monitors::reinforcements::AreReinforcementsAuthorizedMonitor::OnEnter')
    def OnEnter(self):
        reinforcementManager = self.context.entityLocation.GetReinforcementManager()
        try:
            if reinforcementManager.IsReinforcementAuthorized(self.context.myEntityGroupId):
                self.status = status.TaskSuccessStatus
            else:
                self.SubscribeToBlackboard(REINFORCEMENTS_AUTHORIZED_ADDRESS, self.OnReinforcementAuthorizationChanged)
                self.status = status.TaskFailureStatus
        except (ReinforcedEntityGroupNotFoundError, BlackboardDeletedError):
            raise UnrecoverableBehaviorError('Unable to find reinforced entity group.  All the members are likely dead.')

    @TimedFunction('behaviors::monitors::reinforcements::AreReinforcementsAuthorizedMonitor::OnReinforcementAuthorizationChanged')
    def OnReinforcementAuthorizationChanged(self, messageName, message):
        if self.IsInvalid():
            return
        isAuthorized = message.value
        if not isAuthorized:
            return
        self.behaviorTree.RequestReset(requestedBy=self)

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeToBlackboard(REINFORCEMENTS_AUTHORIZED_ADDRESS, self.OnReinforcementAuthorizationChanged)
            self.SetStatusToInvalid()


class AreReinforcementAvailableMonitor(Task):

    @TimedFunction('behaviors::monitors::reinforcements::AreReinforcementAvailableMonitor::OnEnter')
    def OnEnter(self):
        myEntityGroupId = self.context.myEntityGroupId
        reinforcementManager = self.context.entityLocation.GetReinforcementManager()
        if reinforcementManager.AreReinforcementsAvailable(myEntityGroupId):
            self.SetStatusToSuccess()
        else:
            self.SubscribeToBlackboard(REINFORCEMENT_COOLDOWN_ADDRESS, self.OnCooldownDone)
            self.SetStatusToFailed()

    @TimedFunction('behaviors::monitors::reinforcements::AreReinforcementAvailableMonitor::OnCooldownDone')
    def OnCooldownDone(self, messageName, message):
        if self.status is status.TaskInvalidStatus:
            return
        isCoolingDown = message.value is not None
        if isCoolingDown:
            return
        self.behaviorTree.RequestReset(requestedBy=self)

    def CleanUp(self):
        self.status = status.TaskInvalidStatus
        self.UnsubscribeToBlackboard(REINFORCEMENT_COOLDOWN_ADDRESS, self.OnCooldownDone)
