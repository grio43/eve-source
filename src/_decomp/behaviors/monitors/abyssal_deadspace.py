#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\abyssal_deadspace.py
from ballpark.messenger.const import MESSAGE_ON_CLOSE_TO_ABYSSAL_DANGER_ZONE
from behaviors.tasks import Task

class ResetOnCloseToAbyssalDangerZone(Task):

    def OnEnter(self):
        self.context.ballpark.eventMessenger.SubscribeItem(self.context.myItemId, MESSAGE_ON_CLOSE_TO_ABYSSAL_DANGER_ZONE, self._on_close_to_abyssal_danger_zone)
        self.SetStatusToSuccess()

    def CleanUp(self):
        if not self.IsInvalid():
            self.SetStatusToInvalid()
            self.context.ballpark.eventMessenger.UnsubscribeItem(self.context.myItemId, MESSAGE_ON_CLOSE_TO_ABYSSAL_DANGER_ZONE, self._on_close_to_abyssal_danger_zone)

    def _on_close_to_abyssal_danger_zone(self):
        if self.IsInvalid():
            return
        self.behaviorTree.RequestReset(requestedBy=self)
