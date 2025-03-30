#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\activate.py
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from spacecomponents.client.display import EntryData, TIMER_ICON
from spacecomponents.common.componentConst import ACTIVATE_CLASS
from spacecomponents.common.components.component import Component
from carbon.common.lib.const import SEC
from gametime import GetSecondsSinceWallclockTime
from spacecomponents.client.messages import MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_ADDED_TO_SPACE
from spacecomponents.client.messages import MSG_ON_ACTIVATE_TIMER_UPDATED, MSG_ON_LOAD_OBJECT

class Activate(Component):

    def __init__(self, *args):
        Component.__init__(self, *args)
        self.isActive = False
        self.activeTimestamp = None
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)
        self.SubscribeToMessage(MSG_ON_LOAD_OBJECT, self.OnLoadObject)

    def OnAddedToSpace(self, slimItem):
        self.OnSlimItemUpdated(slimItem)

    def OnLoadObject(self, ball):
        self._UpdateModel(ball)

    def OnSlimItemUpdated(self, slimItem):
        if slimItem.component_activate is not None:
            isActive, activeTimestamp = slimItem.component_activate
            self.isActive = isActive
            self.activeTimestamp = activeTimestamp
            self.SendMessage(MSG_ON_ACTIVATE_TIMER_UPDATED, self, slimItem)
        ball = sm.GetService('michelle').GetBall(self.itemID)
        if ball is not None:
            self._UpdateModel(ball)

    def _UpdateModel(self, ball):
        try:
            model = ball.GetModel()
        except AttributeError:
            return

        if model is not None:
            durationSeconds = self.GetDurationSeconds()
            totalDuration = float(durationSeconds or 0)
            remainingDuration = totalDuration
            if self.activeTimestamp is not None:
                remainingDuration = -GetSecondsSinceWallclockTime(self.activeTimestamp)
            model.SetControllerVariable('Activate_IsActive', float(self.isActive or 0))
            model.SetControllerVariable('Activate_TotalDuration', totalDuration)
            model.SetControllerVariable('Activate_RemainingDuration', remainingDuration)

    def IsActive(self):
        return self.isActive

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/Activate/InfoAttributesHeader')), EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Activate/DurationLabel'), localization.GetByLabel('UI/Inflight/SpaceComponents/Activate/DurationValue', duration=long(attributes.durationSeconds * SEC)), iconID=TIMER_ICON)]
        if instance and instance.activeTimestamp:
            attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Activate/TimestampLabel'), localization.GetByLabel('UI/Journal/JournalWindow/Contracts/TimeRemaining', time=instance.activeTimestamp - instance.GetSimTime()), iconID=TIMER_ICON))
        return attributeEntries

    def GetDurationSeconds(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        return GetActivationDurationForItem(ballpark, self.itemID)


def GetActivationDurationForItem(ballpark, itemID):
    slimItem = ballpark.GetInvItem(itemID)
    if slimItem and slimItem.activate_comp_durationSeconds:
        return slimItem.activate_comp_durationSeconds
    component = ballpark.componentRegistry.GetComponentForItem(itemID, ACTIVATE_CLASS)
    return component.attributes.durationSeconds
