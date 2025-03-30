#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\reinforcements.py
import logging
from ballpark.entities.reinforcementmanager import CreateReinforcedGroup, ReinforcementWave
from behaviors import status
from behaviors.const.blackboardchannels import UNSPAWN_ENTITY
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task
from behaviors.utility import security
from behaviors.utility.blackboards import get_response_thresholds
from ccpProfile import TimedFunction
logger = logging.getLogger(__name__)

class CallInReinforcementsAction(Task):

    @TimedFunction('behaviors::actions::reinforcements::CallInReinforcementsAction::OnEnter')
    def OnEnter(self):
        self.status = status.TaskFailureStatus
        groupId = self.context.myEntityGroupId
        reinforcementManager = self.context.entityLocation.GetReinforcementManager()
        if not reinforcementManager.IsReinforcementAuthorized(groupId):
            return
        if not reinforcementManager.AreReinforcementsAvailable(groupId):
            return
        reinforcementManager.CallInReinforcements(self.context.myEntityGroupId, get_response_thresholds(self))
        self.status = status.TaskSuccessStatus


class AddReinforcementsByOwnerId(Task, GroupTaskMixin):

    @TimedFunction('behaviors::actions::group::AddReinforcementsByOwnerId::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        if self._IsAlreadyReinforced():
            return
        spawnlistId = security.get_spawnlist_by_group_owner_and_security_level(self)
        if not spawnlistId:
            logger.error('Unable to add reinforcements: Owner %s of group %s has no reinforcements defined.', self.GetGroupOwnerId(), self.context.myEntityGroupId)
            return
        reinforcedGroup = self._CreateReinforcedGroup(spawnlistId)
        reinforcedGroup.SetEntityGroupID(self.context.myEntityGroupId)
        self.context.entityLocation.reinforcementManager.AddEntityGroupReinforcement(reinforcedGroup)
        self.SetStatusToSuccess()

    def _IsAlreadyReinforced(self):
        reinforcement_manager = self.context.entityLocation.GetReinforcementManager()
        return reinforcement_manager.GetReinforcedGroup(self.context.myEntityGroupId) is not None

    def _CreateReinforcedGroup(self, spawnlistId):
        reinforcementWave = ReinforcementWave(reinforcementWaveId=spawnlistId, reinforcementWaveCooldownSeconds=self.attributes.reinforcementWaveCooldownSeconds, reinforcementThreshold=self.attributes.reinforcementThreshold, behaviorOverrideId=self._GetBehaviorOverrideId())
        return CreateReinforcedGroup(self._GetEntityCountForOriginalGroup(), self.GetGroupOwnerId(), reinforcementWave, None)

    def _GetEntityCountForOriginalGroup(self):
        return len(self.GetMemberIdList())

    def _GetBehaviorOverrideId(self):
        if self.HasAttribute('behaviorOverrideId'):
            return self.attributes.behaviorOverrideId


class CallForUnspawningReinforcements(Task, GroupTaskMixin):

    @TimedFunction('behaviors::actions::group::UnspawnReinforcements::OnEnter')
    def OnEnter(self):
        reinforcedEntityIds = self.context.entityLocation.reinforcementManager.GetActiveReinforcedEntityIds(self.context.myEntityGroupId)
        for entityId in reinforcedEntityIds:
            self._CallForUnspawningEntity(entityId)

        self.context.entityLocation.reinforcementManager.RemoveActiveReinforcedEntityIds(self.context.myEntityGroupId)
        self.SetStatusToSuccess()

    def _CallForUnspawningEntity(self, entityId):
        try:
            _, channelAddressName = UNSPAWN_ENTITY
            channel = self.GetMessageChannelForItemId(entityId, channelAddressName)
            channel.SendMessage(True)
        except:
            pass
