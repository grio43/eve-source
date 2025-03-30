#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\skyhookReagentSilo.py
from spacecomponents import Component
from spacecomponents.client import MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE, MSG_ON_DAMAGE_UPDATED, MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_SKYHOOK_REAGENT_SILO_SLIM_ITEM_UPDATED
import logging
from carbon.common.script.util import timerstuff
import mathext
logger = logging.getLogger(__name__)

class SkyhookReagentSilo(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)
        self.skyhookID = None
        self.model = None
        self.planetID = None
        self.itemID = itemID
        self.damageTimer = None
        self.ballpark = None
        self.shieldPercentage = None

    def get_parent_skyhook_id(self):
        return self.skyhookID

    def OnAddedToSpace(self, slimItem):
        self.ballpark = sm.GetService('michelle').GetBallpark()
        self.OnSlimItemUpdated(slimItem)
        self.damageTimer = timerstuff.AutoTimer(1000, self.UpdateDamage)

    def OnRemovedFromSpace(self):
        self.damageTimer = None

    def OnSlimItemUpdated(self, slimItem):
        self.skyhookID = slimItem.component_skyhookReagentSilo_skyhookID
        self.componentRegistry.SendMessageToItem(self.skyhookID, MSG_ON_SKYHOOK_REAGENT_SILO_SLIM_ITEM_UPDATED, slimItem)

    def UpdateDamage(self):
        if self.ballpark is None:
            self.damageTimer = None
            return
        damage = self.ballpark.GetDamageState(self.itemID)
        if damage is not None:
            shield = damage[0]
            rounded = round(shield, 3)
            newShieldPercentage = 100 * mathext.clamp(rounded, 0, 1.0)
            if newShieldPercentage != self.shieldPercentage:
                self.shieldValue = newShieldPercentage
                self.SendMessage(MSG_ON_DAMAGE_UPDATED, self.itemID, newShieldPercentage)
