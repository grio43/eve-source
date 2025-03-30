#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\reinforcements.py
import logging
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task
from ccpProfile import TimedFunction
logger = logging.getLogger(__name__)

class AreAnyReinforcementMembersAlive(Task, GroupTaskMixin):

    @TimedFunction('behaviors::conditions::reinforcements::AreAnyReinforcementMembersAlive::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        reinforcedEntityIds = self.context.entityLocation.reinforcementManager.GetActiveReinforcedEntityIds(self.context.myEntityGroupId)
        for entityId in reinforcedEntityIds:
            if self.context.ballpark.HasBall(entityId):
                self.SetStatusToSuccess()
                break
