#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\entities.py
import logging
import evetypes
from behaviors.tasks import Task
from behaviors.utility.inventory import is_my_cargo_full
from behaviors.utility.roles import is_commander
from ccpProfile import TimedFunction
from inventorycommon.const import ownerUnknown
from inventorycommon.util import IsNPC
logger = logging.getLogger(__name__)

class HasAnyOfTypesInEntityAdditionalLoot(Task):

    @TimedFunction('behaviors::condition::entities::HasAnyOfTypesInEntityAdditionalLoot::OnEnter')
    def OnEnter(self):
        for typeId in self.attributes.typeIds:
            if self.context.myBall.HasTypeInAdditionalLoot(typeId):
                self.SetStatusToSuccess()
                break
        else:
            self.SetStatusToFailed()


class OwnerIsNpcCondition(Task):

    @TimedFunction('behaviors::condition::entities::OwnerIsNpcCondition::OnEnter')
    def OnEnter(self):
        ownerId = self.GetLastBlackboardValue(self.attributes.ownerIdAddress)
        if ownerId and (IsNPC(ownerId) or ownerId == ownerUnknown):
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()


class HasEnoughCargoForType(Task):

    @TimedFunction('behaviors::condition::entities::HasEnoughCargoForType::OnEnter')
    def OnEnter(self):
        typeId = self.GetLastBlackboardValue(self.attributes.typeIdAddress)
        if typeId and self.HasEnoughCargoForType(typeId):
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def HasEnoughCargoForType(self, typeId):
        return self.context.myBall.HasEnoughAdditionalCargoCapacityForType(typeId)


class IsCargoAboveCapacityThreshold(Task):

    @TimedFunction('behaviors::actions::entities::IsCargoAboveCapacityThreshold::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        totalCapacity = evetypes.GetAttributeForType(self.context.mySlimItem.typeID, 'capacity')
        if not totalCapacity:
            logger.error('Entity: %s - failed checking cargo due to having no cargo.', self.context.myItemId)
            return
        usedCapacity = totalCapacity - self.context.myBall.GetAvailableAdditionalCargoCapacity()
        if usedCapacity / totalCapacity >= self.attributes.cargoCapacityThreshold:
            self.SetStatusToSuccess()


class AmITheCommander(Task):

    @TimedFunction('behaviors::actions::entities::AmITheCommander::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        if is_commander(self, self.context.myItemId):
            self.SetStatusToSuccess()


class IsMyCargoFull(Task):

    @TimedFunction('behaviors::actions::entities::IsMyInventoryFull::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        if is_my_cargo_full(self):
            self.SetStatusToSuccess()
