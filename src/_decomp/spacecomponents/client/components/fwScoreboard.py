#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\fwScoreboard.py
from spacecomponents import Component
from spacecomponents.client import MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE, MSG_ON_SLIM_ITEM_UPDATED

class FWScoreboard(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)

    def OnAddedToSpace(self, slimItem):
        score = slimItem.component_fwScoreboard_score or 0
        sm.GetService('fwWarzoneSvc').BattleFieldAdded(self.itemID, slimItem.typeID, score)
        self.OnSlimItemUpdated(slimItem)

    def OnRemovedFromSpace(self):
        sm.GetService('fwWarzoneSvc').BattleFieldRemoved(self.itemID)

    def OnSlimItemUpdated(self, slimItem):
        score = slimItem.component_fwScoreboard_score or 0
        sm.ScatterEvent('OnFwScoreboardUpdated', slimItem.itemID, score)
