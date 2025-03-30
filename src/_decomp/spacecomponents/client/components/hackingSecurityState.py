#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\hackingSecurityState.py
import logging
from spacecomponents import Component
from spacecomponents.client import MSG_ON_SLIM_ITEM_UPDATED
logger = logging.getLogger(__name__)

class HackingSecurityState(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)

    def OnSlimItemUpdated(self, slimItem):
        ball = sm.GetService('michelle').GetBall(self.itemID)
        if ball is not None:
            ball.SetControllerVariable('SecurityState', slimItem.hackingSecurityState or 0.0)
