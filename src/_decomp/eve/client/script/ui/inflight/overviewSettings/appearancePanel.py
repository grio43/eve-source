#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\appearancePanel.py
from carbonui.primitives.container import Container
from carbonui import uiconst
from eve.client.script.parklife import stateSetting
from carbonui.button.group import ButtonGroup
from carbonui.control.checkbox import Checkbox
import overviewPresets.overviewSettingsConst as osConst
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.inflight.overviewSettings.overviewSettingEntries import GetLastEntryToAdd, FlagEntry
from eve.client.script.ui.inflight.overviewSettings.panelUtils import OnContentDragEnter, OnContentDragExit, ResetCbOnReloadingOverviewProfile
from globalConfig import IsPlayerBountyHidden
from localization import GetByLabel
from utillib import KeyVal
from eve.client.script.parklife import states as stateFlagcConst

class AppearancePanel(Container):
    default_name = 'appearancePanel'
    __notifyevents__ = ['OnReloadingOverviewProfile']
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.cachedScrollPos = 0.0
        self.overviewPresetSvc = sm.GetService('overviewPresetSvc')
        self.ConstructCheckboxes()
        statebtns = ButtonGroup(parent=self, idx=0)
        statebtns.AddButton(GetByLabel('UI/Commands/ResetAll'), self.ResetStateSettings)
        self.statetabs = TabGroup(name='overviewstatesTab', align=uiconst.TOTOP, parent=self, groupID='overviewstatesTab', autoselecttab=0, padTop=8)
        self.statetabs.AddTab(GetByLabel('UI/Overview/Colortag'), code=self, tabID='flag', hint=GetByLabel('UI/Overview/HintToggleDisplayState'))
        self.statetabs.AddTab(GetByLabel('UI/Overview/Background'), code=self, tabID='background', hint=GetByLabel('UI/Overview/HintToggleDisplayState'))
        self.scroll = Scroll(name='appearanceScroll', parent=self)
        self.scroll.multiSelect = 0
        self.scroll.sr.content.OnDropData = self.MoveStuff
        self.scroll.sr.content.OnDragEnter = lambda *args: OnContentDragEnter(self.scroll, *args)
        self.scroll.sr.content.OnDragExit = lambda *args: OnContentDragExit(self.scroll, *args)
        sm.RegisterNotify(self)

    def ConstructCheckboxes(self):
        self.settingCheckboxes = []
        cb = Checkbox(text=GetByLabel('UI/Overview/UseSmallColortags'), parent=self, settingsKey=osConst.SETTING_NAME_SMALL_TAGS, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName(osConst.SETTING_NAME_SMALL_TAGS, False), callback=self.CheckBoxChange, settingsPath=('user', 'overview'), align=uiconst.TOTOP)
        self.settingCheckboxes.append(cb)
        self.useSmallColorTags = cb
        self.useSmallText = Checkbox(text=GetByLabel('UI/Overview/UseSmallFont'), parent=self, settingsKey=osConst.SETTING_NAME_SMALL_TEXT, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName(osConst.SETTING_NAME_SMALL_TEXT, False), callback=self.CheckBoxChange, settingsPath=('user', 'overview'), align=uiconst.TOTOP)
        self.settingCheckboxes.append(self.useSmallText)
        EveLabelMedium(text=GetByLabel('UI/Overview/ApplyToShipsAndDronesByDefault'), parent=self, align=uiconst.TOTOP, padding=(0, 16, 0, 0), state=uiconst.UI_NORMAL)
        applyToStructures = self.overviewPresetSvc.GetSettingValueOrDefaultFromName(osConst.SETTING_NAME_APPLY_STRUCTURE, True)
        cb = Checkbox(text=GetByLabel('UI/Overview/ApplyToStructures'), parent=self, settingsKey=osConst.SETTING_NAME_APPLY_STRUCTURE, checked=applyToStructures, callback=self.CheckBoxChange, settingsPath=('user', 'overview'), align=uiconst.TOTOP, padTop=4)
        self.settingCheckboxes.append(cb)
        self.applyToStructures = cb
        applyToOtherObjects = self.overviewPresetSvc.GetSettingValueOrDefaultFromName(osConst.SETTING_NAME_APPLY_OTHER_OBJ, False)
        cb = Checkbox(text=GetByLabel('UI/Overview/ApplyToOtherObjects'), parent=self, settingsKey=osConst.SETTING_NAME_APPLY_OTHER_OBJ, checked=applyToOtherObjects, callback=self.CheckBoxChange, settingsPath=('user', 'overview'), align=uiconst.TOTOP)
        self.settingCheckboxes.append(cb)
        self.applyToOtherObjects = cb

    def ResetStateSettings(self, *args):
        settings.user.overview.Set(stateSetting.SETTING_FLAG_ORDER_CONFIG_NAME, None)
        settings.user.overview.Set(osConst.SETTING_ICON_ORDER, None)
        settings.user.overview.Set(stateSetting.SETTING_BACKGROUND_ORDER_CONFIG_NAME, None)
        settings.user.overview.Set(stateSetting.SETTING_FLAG_STATES_CONFIG_NAME, None)
        settings.user.overview.Set(osConst.SETTING_ICON_STATES, None)
        settings.user.overview.Set(stateSetting.SETTING_BACKGROUND_STATES_CONFIG_NAME, None)
        settings.user.overview.Set(osConst.SETTING_STATE_COLORS, {})
        sm.GetService('stateSvc').InitColors(1)
        settings.user.overview.Set(osConst.SETTING_STATE_BLINKS, {})
        defaultUseSmallColorTags = self.overviewPresetSvc.GetDefaultSettingValueFromName(osConst.SETTING_NAME_SMALL_TAGS, False)
        settings.user.overview.Set(osConst.SETTING_NAME_SMALL_TAGS, defaultUseSmallColorTags)
        self.useSmallColorTags.SetChecked(defaultUseSmallColorTags, 0)
        defaultApplyToStructures = self.overviewPresetSvc.GetDefaultSettingValueFromName(osConst.SETTING_NAME_APPLY_STRUCTURE, True)
        settings.user.overview.Set(osConst.SETTING_NAME_APPLY_STRUCTURE, defaultApplyToStructures)
        self.applyToStructures.SetChecked(defaultApplyToStructures, 0)
        defaultApplyToOtherObjects = self.overviewPresetSvc.GetDefaultSettingValueFromName(osConst.SETTING_NAME_APPLY_OTHER_OBJ, False)
        settings.user.overview.Set(osConst.SETTING_NAME_APPLY_OTHER_OBJ, defaultApplyToOtherObjects)
        self.applyToOtherObjects.SetChecked(defaultApplyToOtherObjects, 0)
        self.LoadFlags()
        sm.GetService('stateSvc').NotifyOnStateSetupChange('reset')

    def AutoSelectTab(self):
        self.statetabs.AutoSelect()

    def GetSelectedTab(self):
        return self.statetabs.GetSelectedArgs()

    def Load(self, key):
        self.LoadFlags()

    def LoadFlags(self, selected = None):
        where = self.GetSelectedTab()
        flagOrder = sm.GetService('stateSvc').GetStateOrder(where)
        scrolllist = []
        i = 0
        playerBountyHidden = IsPlayerBountyHidden(sm.GetService('machoNet'))
        for flag in flagOrder:
            if flag == stateFlagcConst.flagIsWanted and playerBountyHidden:
                continue
            props = sm.GetService('stateSvc').GetStateProps(flag)
            data = KeyVal()
            data.label = props.text
            data.props = props
            data.checked = sm.GetService('stateSvc').GetStateState(where, flag)
            data.cfgname = where
            data.retval = flag
            data.flag = flag
            data.canDrag = True
            data.hint = props.hint
            data.OnChange = self.CheckBoxChange
            data.isSelected = selected == i
            scrolllist.append(GetFromClass(FlagEntry, data=data))
            i += 1

        scrolllist += GetLastEntryToAdd(scrolllist)
        self.scroll.Load(contentList=scrolllist, scrollTo=self.cachedScrollPos)

    def CheckBoxChange(self, checkbox, node = None):
        settingsKey = checkbox.GetSettingsKey()
        if settingsKey:
            if settingsKey == osConst.SETTING_NAME_SMALL_TAGS:
                sm.GetService('stateSvc').NotifyOnStateSetupChange('filter')
            elif settingsKey == osConst.SETTING_NAME_SMALL_TEXT:
                if checkbox.checked:
                    settings.user.overview.Set(osConst.SETTING_NAME_SMALL_TEXT, 1)
                else:
                    settings.user.overview.Set(osConst.SETTING_NAME_SMALL_TEXT, 0)
                self.DoFullOverviewReload()
            elif settingsKey in (osConst.SETTING_NAME_APPLY_STRUCTURE, osConst.SETTING_NAME_APPLY_OTHER_OBJ):
                sm.GetService('overviewPresetSvc').SetNPCGroups()
                sm.GetService('stateSvc').InitFilter()
                sm.GetService('stateSvc').NotifyOnStateSetupChange('filter')
                self.DoFullOverviewReload()
                sm.GetService('bracket').Reload()
        key = checkbox.GetSettingsKey()
        if key:
            selectedTabConfigName = self.GetSelectedTab()
            if key == selectedTabConfigName:
                if node:
                    flag = node.flag
                else:
                    raise ValueError('No flag value passed in')
                sm.GetService('stateSvc').ChangeStateState(selectedTabConfigName, flag, checkbox.checked)

    def DoFullOverviewReload(self):
        sm.ScatterEvent('OnFullOverviewReload')

    def MoveStuff(self, dragObj, entries, idx = -1, *args):
        self.Move(idx)

    def Move(self, idx = None, *args):
        self.cachedScrollPos = self.scroll.GetScrollProportion()
        selected = self.scroll.GetSelected()
        if selected:
            selected = selected[0]
            if idx is not None:
                if idx != selected.idx:
                    if selected.idx < idx:
                        newIdx = idx - 1
                    else:
                        newIdx = idx
                else:
                    return
            else:
                newIdx = max(0, selected.idx - 1)
            where = self.GetSelectedTab()
            sm.GetService('stateSvc').ChangeStateOrder(where, selected.flag, newIdx)
            self.LoadFlags(newIdx)

    def OnReloadingOverviewProfile(self):
        ResetCbOnReloadingOverviewProfile(self.overviewPresetSvc, self.settingCheckboxes)
