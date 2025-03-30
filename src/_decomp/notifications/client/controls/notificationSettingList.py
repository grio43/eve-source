#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\controls\notificationSettingList.py
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMediumBold
from carbonui.primitives.container import Container
from globalConfig.getFunctions import IsPlayerBountyHidden
from notifications.client.controls.notificationSettingEntityDeco import NotificationSettingEntityDeco
from notifications.client.notificationSettings.notificationSettingHandler import NotificationSettingHandler
import localization
import carbonui.const as uiconst
from carbonui.primitives.line import Line
import eve.common.script.util.notificationconst as notificationConst
from notifications.client.controls.treeViewSettingsItem import TreeViewSettingsItem
from notifications.common.formatting.notificationFormatMapping import GetFormatterForType
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER

class NotificationSettingList(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.lastVerticalBarEnabledStatus = False
        self.notificationSettingHandler = NotificationSettingHandler()
        self.notificationSettingData = self.notificationSettingHandler.LoadSettings()
        self.isDeveloperMode = attributes.get('developerMode', False)
        self._SetupUI()

    def _SetupUI(self):
        self.settingsDescriptionRowContainer = ContainerAutoSize(name='Settings', parent=self, align=uiconst.TOTOP, alignMode=uiconst.CENTERLEFT, minHeight=16, padding=(0, 0, 24, 8))
        EveLabelLarge(name='Settings', parent=self.settingsDescriptionRowContainer, align=uiconst.CENTERLEFT, text=localization.GetByLabel('Notifications/NotificationSettings/CategorySubscriptions'))
        Sprite(name='popupIcon', parent=ContainerAutoSize(parent=self.settingsDescriptionRowContainer, align=uiconst.TORIGHT), align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/Notifications/settingsPopupIcon.png', width=16, height=16, hint=localization.GetByLabel('Notifications/NotificationSettings/PopupVisibilityTooltip'))
        Sprite(name='visibilityIcon', parent=ContainerAutoSize(parent=self.settingsDescriptionRowContainer, align=uiconst.TORIGHT, left=8), align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/Notifications/settingsVisibleIcon.png', width=16, height=16, hint=localization.GetByLabel('Notifications/NotificationSettings/HistoryVisibilityTooltip'))
        self.scrollList = ScrollContainer(name='scrollContainer', parent=self, align=uiconst.TOALL, padding=0)
        self.scrollList.OnScrolledVertical = self.VerticalScrollInject

    def VerticalScrollInject(self, scrollTo):
        self.AdjustCategoryHeaderForScrollBar()

    def AdjustCategoryHeaderForScrollBar(self):
        if self.lastVerticalBarEnabledStatus == self.scrollList._scrollbar_vertical.display:
            return
        if self.scrollList._scrollbar_vertical.display:
            self.settingsDescriptionRowContainer.padRight = 24
        else:
            self.settingsDescriptionRowContainer.padRight = 8
        self.lastVerticalBarEnabledStatus = self.scrollList._scrollbar_vertical.display

    def _GetGroupScrollEntries(self):
        entries = []
        for group, list in notificationConst.groupTypes.iteritems():
            if group == notificationConst.groupBounties and IsPlayerBountyHidden(sm.GetService('machoNet')):
                continue
            groupName = localization.GetByLabel(notificationConst.groupNamePathsNewNotifications[group])
            entries.append(self.GetGroupEntry(fakeID=group, groupName=groupName))

        return entries

    def PopulateScroll(self):
        entries = self._GetGroupScrollEntries()
        entries.sort(key=lambda entr: entr.data.GetLabel().lower())
        for entry in entries:
            self.scrollList.children.append(entry)

    def ReloadScroll(self):
        self.notificationSettingHandler = NotificationSettingHandler()
        self.notificationSettingData = self.notificationSettingHandler.LoadSettings()
        self.scrollList.Flush()
        self.PopulateScroll()

    def GetGroupEntry(self, fakeID, groupName):
        from eve.client.script.ui.control.treeData import TreeData
        rawNotificationList = notificationConst.groupTypes[fakeID]
        groupSettings = {}
        self.AppendEntryData(data=groupSettings, visibilityChecked=self.notificationSettingHandler.GetVisibilityStatusForGroup(fakeID, self.notificationSettingData), showPopupChecked=self.notificationSettingHandler.GetShowPopupStatusForGroup(fakeID, self.notificationSettingData), isGroup=True, id=fakeID)
        childrenData = []
        for notification in rawNotificationList:
            settingLabel = notificationConst.notificationToSettingDescription.get(notification, None)
            settingName = localization.GetByLabel(settingLabel)
            params = {}
            setting = self.notificationSettingData[notification]
            self.AppendEntryData(data=params, visibilityChecked=setting.showAtAll, showPopupChecked=setting.showPopup, isGroup=False, id=notification)
            notificationData = TreeData(label=settingName, parent=None, isRemovable=False, settings=params, settingsID=notification)
            childrenData.append(notificationData)

        childrenData.sort(key=lambda childData: childData.GetLabel().lower())
        data = TreeData(label=groupName, parent=None, children=childrenData, icon=None, isRemovable=False, settings=groupSettings)
        entry = TreeViewSettingsItem(level=0, eventListener=self, data=data, settingsID=fakeID, defaultExpanded=False)
        return entry

    def OnTreeViewClick(self, selected, *args):
        if selected.data.HasChildren():
            selected.ToggleChildren()

    def AppendEntryData(self, data, visibilityChecked, showPopupChecked, isGroup, id):
        data.update({NotificationSettingEntityDeco.VISIBILITY_CHECKED_KEY: visibilityChecked,
         NotificationSettingEntityDeco.POPUP_CHECKED_KEY: showPopupChecked,
         NotificationSettingEntityDeco.VISIBILITY_CHANGED_CALLBACK_KEY: self.OnVisibilityEntryChangedNew,
         NotificationSettingEntityDeco.POPUP_CHANGED_CALLBACK_KEY: self.OnShowPopupEntryChangedNew,
         NotificationSettingEntityDeco.GETMENU_CALLBACK: self.GetMenuForEntry,
         'isGroup': isGroup,
         'id': id})

    def OnVisibilityEntryChangedNew(self, isGroup, id, checked):
        if not isGroup:
            self._setVisibilitySettingForNotification(id, checked)

    def OnShowPopupEntryChangedNew(self, isGroup, id, checked):
        if not isGroup:
            self._setPopupSettingForNotification(id, checked)

    def _setVisibilitySettingForNotification(self, id, on):
        notificationData = self.notificationSettingData[id]
        notificationData.showAtAll = on
        self.SaveAllData()

    def _setPopupSettingForNotification(self, id, on):
        notificationData = self.notificationSettingData[id]
        notificationData.showPopup = on
        self.SaveAllData()

    def SaveAllData(self):
        self.notificationSettingHandler.SaveSettings(self.notificationSettingData)

    def GetMenuForEntry(self, isGroup, nodeID):
        if session.role & ROLE_PROGRAMMER and not isGroup:
            return [('GM: spawnNotification %s' % nodeID, self.OnSpawnNotificationClick, [nodeID])]
        else:
            return [('spawnNotification %s' % nodeID, self.OnSpawnNotificationClick, [nodeID])]

    def OnSpawnNotificationClick(self, notificationID):
        newFormatter = GetFormatterForType(notificationID)
        if newFormatter:
            import blue
            data = newFormatter.MakeSampleData()
            sender = newFormatter.GetSampleSender()
            sm.ScatterEvent('OnNotificationReceived', 123, notificationID, sender, blue.os.GetWallclockTime(), data=data)
        else:
            from notifications.client.development.notificationDevUI import FakeNotificationMaker
            maker = FakeNotificationMaker()
            counter = 1
            agentStartID = 3008416
            someAgentID = agentStartID + counter
            senderID = 98000001
            corpStartID = 1000089
            someCorp = corpStartID + counter
            maker.ScatterSingleNotification(counter, notificationID, senderID, someAgentID, someCorp)
