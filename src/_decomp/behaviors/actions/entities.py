#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\entities.py
import logging
import uthread2
from behaviors import status
from behaviors.behaviortree import UnrecoverableBehaviorError
from behaviors.const.combat import FW_ATTACK_NONE
from behaviors.tasks import Task
from behaviors.utility.inventory import remove_all_items
from ccpProfile import TimedFunction
from spacecomponents.common.helper import HasCargoBayComponent
logger = logging.getLogger(__name__)
SELF_UNSPAWN_SLEEP_DELAY_SEC = 0.2

class AddTypeAndAmountToAdditionalLoot(Task):

    @TimedFunction('behaviors::actions::entities::AddTypeAndAmountToAdditionalLoot::OnEnter')
    def OnEnter(self):
        typeId = self.GetLastBlackboardValue(self.attributes.typeIdAddress)
        if typeId is not None:
            self.context.myBall.AddTypeAndAmountToAdditionalLoot(typeId, self.attributes.amount, self.attributes.allowOverload)
        self.SetStatusToSuccess()


class AddBlackboardTypeAndBlackboardAmountToAdditionalLoot(Task):

    @TimedFunction('behaviors::actions::entities::AddTypeAndAmountToAdditionalLoot::OnEnter')
    def OnEnter(self):
        typeId = self.GetLastBlackboardValue(self.attributes.typeIdAddress)
        amount = self.GetLastBlackboardValue(self.attributes.amountAddress)
        if typeId is not None and amount is not None:
            self.context.myBall.AddTypeAndAmountToAdditionalLoot(typeId, amount, self.attributes.allowOverload)
        self.SetStatusToSuccess()


class RemoveTypesFromAdditionalLoot(Task):

    @TimedFunction('behaviors::actions::entities::RemoveTypesFromAdditionalLoot::OnEnter')
    def OnEnter(self):
        typeIds = self.attributes.typeIds
        for typeId in typeIds:
            logger.debug('Removing type: %s loot from Entity: %s' % (typeId, self.context.myItemId))
            self.context.myBall.RemoveTypeFromAdditionalLoot(typeId)

        self.status = status.TaskSuccessStatus


class MoveAdditionalLootBetweenEntities(Task):

    @TimedFunction('behaviors::actions::entities::PopAdditionalLootFromEntity::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        entityId = self.GetLastBlackboardValue(self.attributes.entityIdAddress)
        if not entityId:
            return
        hasBall = self.context.ballpark.HasBall(entityId)
        if not hasBall:
            return
        self._MoveAdditionalLootFromAnotherEntityToMe(entityId)
        self.SetStatusToSuccess()

    def _MoveAdditionalLootFromAnotherEntityToMe(self, entityId):
        targetEntityBall = self.context.ballpark.GetBall(entityId)
        additionalLoot = targetEntityBall.RemoveAdditionalLoot()
        for typeId, amount in additionalLoot.iteritems():
            self.context.myBall.AddTypeAndAmountToAdditionalLoot(typeId, amount)


class SelectGroupLeaderAction(Task):

    @TimedFunction('behaviors::actions::entities::SelectGroupLeaderAction::OnEnter')
    def OnEnter(self):
        try:
            groupManager = self.context.entityLocation.GetGroupManager()
            group = groupManager.GetGroup(self.context.myEntityGroupId)
            groupLeaderId = min(group.GetGroupMembers())
        except (KeyError, ValueError) as e:
            raise UnrecoverableBehaviorError('Unable to get own group members: %s' % e)

        self.SendBlackboardValue(self.attributes.groupLeaderIdAddress, groupLeaderId)
        self.SetStatusToSuccess()


class UnspawnSelf(Task):

    @TimedFunction('behaviors::actions::entities::UnspawnSelf::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuspended()
        self.behaviorTree.BlockReset(self)
        uthread2.StartTasklet(self._UnspawnSelf)

    def _UnspawnSelf(self):
        uthread2.sleep(SELF_UNSPAWN_SLEEP_DELAY_SEC)
        self.clear_inventory()
        self.context.ballpark.UnspawnEntityBall(self.context.myItemId)

    def clear_inventory(self):
        if HasCargoBayComponent(self.context.mySlimItem.typeID):
            remove_all_items(self, self.context.myItemId)


class UpdateTaleContextForPersistedObject(Task):

    @TimedFunction('behaviors::actions::entities::UpdateTaleContextForPersistedObject::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        if self.context.get('myTaleId') is not None:
            return
        taleId = self._GetTaleIdFromTaleManager()
        if not taleId:
            self.SetStatusToFailed()
            logger.debug('Behavior: %s failed getting taleId from the DB', self.context.myItemId)
        self.context.myTaleId = taleId

    def _GetTaleIdFromTaleManager(self):
        taleManager = self._GetTaleManager()
        persistedObject = taleManager.GetTaleForPersistedObject(self.context.myItemId)
        if len(persistedObject):
            return persistedObject[0].taleID

    def _GetTaleManager(self):
        return sm.GetService('taleMgr')


class DestroySelf(Task):

    def OnEnter(self):
        self.SetStatusToSuspended()
        uthread2.start_tasklet(self._destroy_self)

    def _destroy_self(self):
        self.context.ballpark.ExplodeEx(self.context.myItemId)


class UpdateStandingThresholdsForEntity(Task):

    @TimedFunction('behaviors::actions::entities::UpdateStandingThresholdsForEntity::OnEnter')
    def OnEnter(self):
        self.context.ballpark.UpdateSlimItemFieldMulti(self.context.myItemId, hostile_response_threshold=self.attributes.hostileResponseThreshold, friendly_response_threshold=self.attributes.friendlyResponseThreshold)
        self.SetStatusToSuccess()


class UpdateFwAttackMethodForEntity(Task):

    @TimedFunction('behaviors::actions::entities::UpdateFwAttackMethodForEntity::OnEnter')
    def OnEnter(self):
        fwAttackMethod = self.attributes.fwAttackMethod
        if fwAttackMethod == FW_ATTACK_NONE:
            fwAttackMethod = None
        self.context.ballpark.UpdateSlimItemField(self.context.myItemId, 'fwAttackMethod', fwAttackMethod)
        groupStandingsDisabled = self.attributes.groupStandingsDisabled
        if groupStandingsDisabled:
            self.context.ballpark.UpdateSlimItemField(self.context.myItemId, 'group_standings_disabled', groupStandingsDisabled)
        self.SetStatusToSuccess()


class CountBehaviorEntitiesOfTypeInSystem(Task):

    def OnEnter(self):
        ballpark = self.context.ballpark
        solarsystemID = ballpark.solarsystemID
        entityLocation = ballpark.broker.entity.GetEntityLocation(solarsystemID)
        typeIDsToCount = self.attributes.typeIDsToCount
        behaviorTreeManager = entityLocation.GetBehaviorTreeManager()
        count = 0
        behaviorEntriesByKey = behaviorTreeManager.GetAllBehaviorEntriesByKey()
        for entryKey in behaviorEntriesByKey:
            if entryKey in ballpark.slims and ballpark.slims[entryKey].typeID in typeIDsToCount:
                count += 1

        self.SendBlackboardValue(self.attributes.resultAddress, count)
        self.SetStatusToSuccess()
