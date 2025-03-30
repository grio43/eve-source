#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\reinforce.py
from carbon.common.lib.const import SEC
from carbon.common.script.util.format import FmtTimeInterval, FmtDate, FmtYesNo
from carbonui.control.contextMenu.menuData import MenuData
from datetimeutils import any_to_datetime
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from spacecomponents.client.display import EntryData, TIMER_ICON
from spacecomponents.common.components.component import Component
from spacecomponents.client.messages import MSG_ON_ADDED_TO_SPACE
from spacecomponents.client.messages import MSG_ON_SLIM_ITEM_UPDATED
from spacecomponents.client.messages import MSG_ON_REINFORCE_TIMER_UPDATED

class Reinforce(Component):

    def __init__(self, *args):
        Component.__init__(self, *args)
        self.isReinforced = False
        self.reinforceTimestamp = None
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnSlimItemUpdated)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)

    def OnSlimItemUpdated(self, slimItem):
        if slimItem.component_reinforce is not None:
            isReinforced, reinforceTimestamp = slimItem.component_reinforce
            self.isReinforced = isReinforced
            self.reinforceTimestamp = reinforceTimestamp
            self.SendMessage(MSG_ON_REINFORCE_TIMER_UPDATED, self, slimItem)

    def IsReinforced(self):
        return self.isReinforced

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/Reinforce/InfoAttributesHeader')), EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Reinforce/DurationLabel'), FmtTimeInterval(long(attributes.durationSeconds * SEC), breakAt='sec'), iconID=TIMER_ICON)]
        if attributes.jitterSeconds is not None:
            attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Reinforce/JitterLabel'), FmtTimeInterval(long(attributes.jitterSeconds * SEC), breakAt='sec'), iconID=TIMER_ICON))
        if instance:
            attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Reinforce/ReinforcedLabel'), FmtYesNo(instance.isReinforced)))
            if instance.isReinforced and instance.reinforceTimestamp > instance.GetWallclockTime():
                attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Reinforce/ExitReinforcementLabel'), FmtDate(instance.reinforceTimestamp, 'ss'), iconID=TIMER_ICON))
        return attributeEntries

    def GetDebugText(self):
        if self.isReinforced:
            timeText = any_to_datetime(self.reinforceTimestamp).strftime('%Y-%m-%d %H:%M:%S')
            return '<color=red>Reinforced</color> until %s' % timeText
        else:
            return '<color=green>Not reinforced</color>'

    def GetGMMenu(self):
        menu_data = MenuData()
        menu_data.AddLabel(text=self.GetDebugText())
        menu_data.AddSeparator()
        if self.isReinforced:
            menu_data.AddEntry(text='Turn OFF reinforcement', func=lambda *args: self.GMSetReinforcement(isReinforced=False))
        else:
            menu_data.AddEntry(text='Turn ON reinforcement', func=lambda *args: self.GMSetReinforcement(isReinforced=True))
        return menu_data

    def GMSetReinforcement(self, isReinforced):
        value = 'on' if isReinforced else 'off'
        sm.GetService('slash').SlashCmd(u'/spacecomponent reinforce {itemID} {value}'.format(itemID=self.itemID, value=value))
