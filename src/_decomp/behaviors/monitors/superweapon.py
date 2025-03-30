#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\superweapon.py
import logging
from behaviors.tasks import Task
from ccpProfile import TimedFunction
from spacecomponents.common.componentConst import TURBO_SHIELD_CLASS
from spacecomponents.server.messages import MSG_ON_TURBO_SHIELD_STATE_CHANGED
logger = logging.getLogger(__name__)

class WaitForTurboShieldState(Task):

    @TimedFunction('behaviors::monitors::superweapon::WaitForTurboShieldState::OnEnter')
    def OnEnter(self):
        self.component = None
        myItemId = self.context.myItemId
        try:
            self.component = self.GetTurboShieldComponent(myItemId)
        except KeyError:
            self.SetStatusToFailed()
            return

        if self.component.IsShieldState(self.attributes.turboShieldState):
            self.SetStatusToSuccess()
            self.SendMessageStateChanged()
        else:
            self.SetStatusToFailed()
            self.component.SubscribeToMessage(MSG_ON_TURBO_SHIELD_STATE_CHANGED, self.OnTurboShieldStateChanged)

    def CleanUp(self):
        if self.IsInvalid():
            return
        if self.component is not None:
            self.component.UnsubscribeFromMessage(MSG_ON_TURBO_SHIELD_STATE_CHANGED, self.OnTurboShieldStateChanged)
            self.component = None
        self.SetStatusToInvalid()

    @TimedFunction('behaviors::monitors::superweapon::WaitForTurboShieldState::OnTurboShieldStateChanged')
    def OnTurboShieldStateChanged(self, turboShieldState):
        if self.IsInvalid():
            return
        if turboShieldState == self.attributes.turboShieldState:
            self.SendMessageStateChanged()
            self.behaviorTree.RequestReset(self)

    def SendMessageStateChanged(self):
        if getattr(self.attributes, 'messageAddress', None) is None:
            return
        state = self.GetLastBlackboardValue(self.attributes.messageAddress)
        if not state:
            self.SendBlackboardValue(self.attributes.messageAddress, True)

    def GetTurboShieldComponent(self, itemId):
        return self.context.ballpark.componentRegistry.GetComponentForItem(itemId, TURBO_SHIELD_CLASS)
