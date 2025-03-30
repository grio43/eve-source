#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\combat.py
from behaviors import status
from behaviors.tasks import Task
from behaviors.utility.ballparks import is_ball_in_range, is_ball_cloaked, is_target_valid
from ccpProfile import TimedFunction
from dogma.const import attributeMaxLockedTargets

class HasValidTarget(Task):

    @TimedFunction('behaviors::conditions::combat::HasValidTarget::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        selected_target = self.GetLastBlackboardValue(self.attributes.selectedTargetAddress)
        if is_target_valid(self, selected_target):
            self.SetStatusToSuccess()


class HasAvailableTargetCapacity(Task):

    @TimedFunction('behaviors::conditions::combat::HasAvailableTargetCapacity::OnEnter')
    def OnEnter(self):
        if self.GetTargetCount() >= self.GetMaxLockedTargets():
            self.status = status.TaskFailureStatus
        else:
            self.status = status.TaskSuccessStatus

    def GetMaxLockedTargets(self):
        return self.context.dogmaLM.GetAttributeValue(self.context.myItemId, attributeMaxLockedTargets)

    def GetTargetCount(self):
        return len(self.context.dogmaLM.GetTargetsEx(self.context.myItemId))


class HasItemsFromCollectionWithinRange(Task):

    @TimedFunction('behaviors::conditions::combat::HasItemsFromCollectionWithinRange::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        item_collection = self.GetLastBlackboardValue(self.attributes.itemIdCollectionAddress)
        if not item_collection:
            return
        detection_range = self.GetLastBlackboardValue(self.attributes.detectionRangeAddress)
        reference_item_id = self.context.myItemId
        if self.FindAnyValidItemInRange(item_collection, detection_range, reference_item_id):
            self.SetStatusToSuccess()

    @TimedFunction('behaviors::conditions::combat::HasItemsFromCollectionWithinRange::FindAnyValidItemInRange')
    def FindAnyValidItemInRange(self, item_collection, detection_range, reference_item_id):
        include_clocked_items = self.attributes.includeCloakedItems
        for item_id in item_collection:
            if not is_ball_in_range(self, reference_item_id, item_id, detection_range):
                continue
            if not include_clocked_items and is_ball_cloaked(self, item_id):
                continue
            return True

        return False
