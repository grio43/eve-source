#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\combattargets.py
from ballpark.messenger.const import MESSAGE_TARGET_ADDED, MESSAGE_ON_DOGMA_ATTRIBUTE_VALUE_CHANGED
from behaviors.tasks import Task
from ccpProfile import TimedFunction
from dogma.const import attributeMaxRange, attributeMissileEntityVelocityMultiplier
BEHAVIOR_RANGE_ATTRIBUTES_FOR_RECALCULATION = [attributeMaxRange, attributeMissileEntityVelocityMultiplier]

class MonitorTargetAdded(Task):

    @TimedFunction('behaviors::monitors::combattargets::MonitorTargetLockSuccess::OnEnter')
    def OnEnter(self):
        self.SubscribeItem(self.context.myItemId, MESSAGE_TARGET_ADDED, self._OnTargetAdded)
        self.SetStatusToSuccess()

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeItem(self.context.myItemId, MESSAGE_TARGET_ADDED, self._OnTargetAdded)
        super(MonitorTargetAdded, self).CleanUp()

    @TimedFunction('behaviors::monitors::combattargets::MonitorTargetLockSuccess::_OnMaxLockedTargetsChanged')
    def _OnTargetAdded(self, target_id):
        if not self.IsInvalid() and self._is_my_pending_target(target_id):
            self.behaviorTree.RequestReset(requestedBy=self)

    def _is_my_pending_target(self, target_id):
        return self.GetLastBlackboardValue(self.attributes.targetAddress) == target_id


class CombatRangeMonitor(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        self.SubscribeItem(self.context.myItemId, MESSAGE_ON_DOGMA_ATTRIBUTE_VALUE_CHANGED, self._on_dogma_attribute_value_changed)

    @TimedFunction('behaviors::monitors::combattargets::CombatRangeMonitor::_on_dogma_attribute_value_changed')
    def _on_dogma_attribute_value_changed(self, attribute_id):
        if attribute_id in BEHAVIOR_RANGE_ATTRIBUTES_FOR_RECALCULATION:
            self.SendBlackboardValue(self.attributes.combatRangeRecalculateAddress, None)
            self.behaviorTree.RequestReset(requestedBy=self)

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeItem(self.context.myItemId, MESSAGE_ON_DOGMA_ATTRIBUTE_VALUE_CHANGED, self._on_dogma_attribute_value_changed)
        super(CombatRangeMonitor, self).CleanUp()
