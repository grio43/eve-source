#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\towGameOperator.py
import logging
from spacecomponents import Component
from spacecomponents.client import MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE, MSG_ON_SLIM_ITEM_UPDATED
logger = logging.getLogger(__name__)

class TowGameOperator(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)

    def OnAddedToSpace(self, slimItem):
        self.OnSlimItemUpdated(slimItem)
        scoreByFactionID = slimItem.component_TowGameOperator_scoreByFactionID
        sm.GetService('towGameSvc').AddTowGame(self.itemID, self.attributes.winThreshold, scoreByFactionID)

    def OnRemovedFromSpace(self):
        sm.GetService('towGameSvc').RemoveTowGame()

    def OnSlimItemUpdated(self, slimItem):
        if slimItem.component_TowGameOperator_scoreByFactionID:
            scoreByFactionID = slimItem.component_TowGameOperator_scoreByFactionID
            sm.GetService('towGameSvc').UpdateTowGame(scoreByFactionID)
            logger.warn('TowGameOperator.OnSlimItemUpdated scoreByFactionID: %s', scoreByFactionID)
