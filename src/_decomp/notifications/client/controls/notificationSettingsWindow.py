#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\controls\notificationSettingsWindow.py
import localization
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.slider import Slider
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelSmall
from notifications.client.controls.notificationSettingList import NotificationSettingList
from notifications.client.notificationSettings.notificationSettingConst import ExpandAlignmentConst
from notifications.client.notificationSettings.notificationSettingHandler import NotificationSettingHandler

class NotificationSettingsWindow(Window):
    default_windowID = 'NotificationSettings'
    default_iconNum = 'res:/UI/Texture/WindowIcons/settings.png'
    default_captionLabelPath = 'Notifications/NotificationSettings/NotificationSettingsWindowCaption'
    default_width = 660
    default_height = 400
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        developerMode = sm.GetService('notificationUIService').IsDeveloperMode()
        self.mainContainer = NotificationSettingsMainContainer(name='mainContainer', align=uiconst.TOALL, parent=self.content, developerMode=developerMode)

    def ReloadSettings(self):
        self.mainContainer.ReloadSettings()


class NotificationSettingsMainContainer(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes=attributes)
        self.isDeveloperMode = attributes.get('developerMode', True)
        self.basePadLeft = 5
        self.dev_exportNotificationHistoryEnabled = False
        self.dev_clearNotificationHistoryEnabled = False
        self.lastVerticalBarEnabledStatus = False
        self.entryCache = {}
        self.leftContainerDragResizeCont = DragResizeCont(name='leftContainerDragResizeCont', parent=self, align=uiconst.TOLEFT_PROP, settingsID='notification_leftContainerDragResizeCont', minSize=0.4, maxSize=0.6)
        self.leftContainer = NotificationSettingList(name='LeftContainer', align=uiconst.TOALL, parent=self.leftContainerDragResizeCont.mainCont, padding=(0, 0, 8, 0), developerMode=self.isDeveloperMode)
        self.rightContainer = ScrollContainer(name='RightContainer', align=uiconst.TOALL, parent=self, padding=(8, 0, 0, 0))
        self.notificationSettingHandler = NotificationSettingHandler()
        self.notificationSettingData = self.notificationSettingHandler.LoadSettings()
        self._SetupRightSide()
        self.leftContainer.PopulateScroll()

    def ReloadSettings(self):
        self.leftContainer.ReloadScroll()

    def _SetupRightSide(self):
        self._SetupPopupArea()
        self._SetupUIArea()
        self._SetupHistoryArea()

    def _SetupPopupArea(self):
        self.popupSettingsContainer = ContainerAutoSize(name='PopupSettings', align=uiconst.TOTOP, parent=self.rightContainer, padding=(0, 0, 0, 8))
        EveLabelLarge(name='PopupHeader', align=uiconst.TOTOP, parent=self.popupSettingsContainer, text=localization.GetByLabel('Notifications/NotificationSettings/PopupsHeader'))
        Checkbox(name='UsepopupNotifications', text=localization.GetByLabel('Notifications/NotificationSettings/UsePopupNotifications'), parent=self.popupSettingsContainer, align=uiconst.TOTOP, top=8, checked=self.notificationSettingHandler.GetPopupsEnabled(), callback=self.OnShowPopupNotificationToggle)
        Checkbox(name='Play sound checkbox', text=localization.GetByLabel('Notifications/NotificationSettings/PlaySound'), parent=self.popupSettingsContainer, align=uiconst.TOTOP, checked=self.notificationSettingHandler.GetNotificationSoundEnabled(), callback=self.OnPlaySoundToggle)
        self.MakeSliderTextRow(label=localization.GetByLabel('Notifications/NotificationSettings/FadeDelay'), minValue=0, maxValue=10.0, startValue=self.notificationSettingHandler.GetFadeTime(), stepping=0.5, callback=self.OnFadeDelaySet)
        self.MakeSliderTextRow(label=localization.GetByLabel('Notifications/NotificationSettings/StackSize'), minValue=1, maxValue=10, startValue=self.notificationSettingHandler.GetStackSize(), stepping=1, callback=self.OnStackSizeSet)

    def OnFadeDelaySet(self, slider):
        self.notificationSettingHandler.SaveFadeTime(slider.GetValue())
        sm.ScatterEvent('OnNotificationFadeTimeChanged', slider.GetValue())

    def OnStackSizeSet(self, slider):
        self.notificationSettingHandler.SaveStackSize(slider.GetValue())
        sm.ScatterEvent('OnNotificationStackSizeChanged', slider.GetValue())

    def OnShowPopupNotificationToggle(self, checkbox):
        self.notificationSettingHandler.TogglePopupsEnabled()

    def OnPlaySoundToggle(self, *args):
        self.notificationSettingHandler.ToggleSoundEnabled()

    def _SetupHistoryArea(self):
        self.historySettingsContainer = ContainerAutoSize(name='HistorySettings', align=uiconst.TOTOP, parent=self.rightContainer, alignMode=uiconst.TOTOP, padding=(0, 8, 0, 0))
        EveLabelLarge(name='History', parent=self.historySettingsContainer, align=uiconst.TOTOP, top=8, text=localization.GetByLabel('Notifications/NotificationSettings/HistoryHeader'))
        Button(name='Restore Notification History Button', align=uiconst.CENTERTOP, label=localization.GetByLabel('Notifications/NotificationSettings/RestoreNotificationHistory'), func=self.OnExportHistoryClick, parent=ContainerAutoSize(parent=self.historySettingsContainer, align=uiconst.TOTOP, padTop=8))
        Button(name='clearNotificationHistoryBtn', align=uiconst.CENTERTOP, label=localization.GetByLabel('Notifications/NotificationSettings/ClearNotificationHistory'), func=self.OnClearHistoryClick, parent=ContainerAutoSize(parent=self.historySettingsContainer, align=uiconst.TOTOP, padTop=8))

    def _SetupUIArea(self):
        self.UISettingsContainer = ContainerAutoSize(name='HistorySettings', align=uiconst.TOTOP, parent=self.rightContainer, alignMode=uiconst.TOTOP)
        hComboRowContainer = ContainerAutoSize(name='ComboBoxRow', parent=self.UISettingsContainer, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        Combo(name='H-ExpandCombo', parent=hComboRowContainer, labelleft=120, label=localization.GetByLabel('Notifications/NotificationSettings/DefaultHExpand'), hint=localization.GetByLabel('Notifications/NotificationSettings/DefaultHExpandToolTip'), options=self.GetHorizontalComboOptions(), align=uiconst.TOTOP, width=self.rightContainer.width, callback=self.OnHorizontalComboSelect, select=self.notificationSettingHandler.GetHorizontalExpandAlignment())
        Combo(name='V-ExpandCombo', parent=hComboRowContainer, top=8, labelleft=120, label=localization.GetByLabel('Notifications/NotificationSettings/DefaultVExpand'), hint=localization.GetByLabel('Notifications/NotificationSettings/DefaultVExpandToolTip'), align=uiconst.TOTOP, options=self.GetVerticalComboOptions(), width=self.rightContainer.width, callback=self.OnVerticalComboSelect, select=self.notificationSettingHandler.GetVerticalExpandAlignment())

    def OnVerticalComboSelect(self, box, key, value):
        self.notificationSettingHandler.SetVerticalExpandAlignment(value)

    def OnHorizontalComboSelect(self, box, key, value):
        self.notificationSettingHandler.SetHorizontalExpandAlignment(value)

    def GetHorizontalComboOptions(self):
        return ((localization.GetByLabel('Notifications/NotificationSettings/ExpandDirectionLeft'), ExpandAlignmentConst.EXPAND_ALIGNMENT_HORIZONTAL_LEFT), (localization.GetByLabel('Notifications/NotificationSettings/ExpandDirectionRight'), ExpandAlignmentConst.EXPAND_ALIGNMENT_HORIZONTAL_RIGHT))

    def GetVerticalComboOptions(self):
        return ((localization.GetByLabel('Notifications/NotificationSettings/ExpandDirectionUp'), ExpandAlignmentConst.EXPAND_ALIGNMENT_VERTICAL_UP), (localization.GetByLabel('Notifications/NotificationSettings/ExpandDirectionDown'), ExpandAlignmentConst.EXPAND_ALIGNMENT_VERTICAL_DOWN))

    def OnExportHistoryClick(self, *args):
        sm.GetService('notificationUIService').UnClearHistory()

    def OnClearHistoryClick(self, *args):
        sm.GetService('notificationUIService').ClearHistory()

    def MakeSliderTextRow(self, label, minValue, maxValue, startValue, stepping, setValueFunc = None, callback = None):
        sliderWidth = 100
        sliderValueWidth = 30
        sliderLabelWidth = 120
        size = EveLabelSmall.MeasureTextSize(label, width=sliderLabelWidth)
        rowHeight = size[1]
        rowContainer = ContainerAutoSize(name='TextRowContainer', parent=self.rightContainer, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT, height=rowHeight, minHeight=24)
        EveLabelSmall(name='sliderlabel', align=uiconst.TOPLEFT, parent=rowContainer, text=label, width=sliderLabelWidth)
        increments = []
        currentValue = minValue
        while currentValue <= maxValue:
            increments.append(currentValue)
            currentValue = currentValue + stepping

        valueLabel = EveLabelSmall(name='sliderValuelabel', left=sliderLabelWidth, align=uiconst.TOPLEFT, text=str(startValue), width=sliderValueWidth)

        def UpdateLabel(slider):
            valueLabel.text = str(slider.GetValue())

        valueLabel._update_label_func = UpdateLabel
        Slider(name='niceSlider', parent=rowContainer, align=uiconst.TOTOP, minValue=minValue, maxValue=maxValue, width=sliderWidth, padLeft=sliderLabelWidth + sliderValueWidth, value=startValue, increments=increments, on_dragging=UpdateLabel, callback=callback)
        rowContainer.children.append(valueLabel)
        return rowContainer
