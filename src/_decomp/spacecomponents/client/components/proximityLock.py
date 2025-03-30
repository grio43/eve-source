#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\proximityLock.py
from carbon.common.lib.const import SEC
from spacecomponents.common.components.component import Component
from spacecomponents.client.messages import MSG_ON_ADDED_TO_SPACE, MSG_ON_PROXIMITY_LOCK_TIMER_UPDATED, MSG_ON_SLIM_ITEM_UPDATED

class ProximityLock(Component):

    def __init__(self, *args):
        super(ProximityLock, self).__init__(*args)
        self.paused_at = None
        self.time_remaining = None
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)

    @property
    def duration(self):
        return self.attributes.durationSeconds * SEC

    def OnAddedToSpace(self, slimItem):
        self.OnSlimItemUpdated(slimItem)

    def OnSlimItemUpdated(self, slimItem):
        if slimItem.component_proximity_lock is not None:
            self.time_remaining, self.paused_at = slimItem.component_proximity_lock
            self.SendMessage(MSG_ON_PROXIMITY_LOCK_TIMER_UPDATED, self, slimItem)
