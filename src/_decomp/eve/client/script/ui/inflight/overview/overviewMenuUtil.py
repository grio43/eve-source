#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overview\overviewMenuUtil.py
import evetypes
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuEntryData import MenuEntryData, MenuEntryDataRadioButton
from carbonui.services.setting import SessionSettingBool
from carbonui.uicore import uicore
from eve.client.script.parklife import bracketConst
from eve.client.script.parklife.bracketSettings import bracket_display_override_setting
from eve.client.script.ui.inflight.overview import overviewConst
from eve.client.script.ui.inflight.overviewSettings.columnConfigurationWnd import ColumnConfigurationWindow
from localization import GetByLabel
from menu import MenuLabel
from overviewPresets import overviewSettingsConst

def GetToggleEntry(groupID):
    presetSvc = sm.GetService('overviewPresetSvc')
    tabIDs = _GetActiveOverviewTabIDs()
    if len(tabIDs) <= 1:
        if presetSvc.IsGroupIDShown(groupID):
            return GetRemoveGroupFromOverviewEntry(groupID)
        else:
            return GetAddGroupToOverviewEntry(groupID)
    else:
        subMenuData = [ _GetToggleSubEntry(tabID, groupID) for tabID in tabIDs ]
        return MenuEntryData(MenuLabel('UI/Overview/ToggleOverviewVisibilty', {'groupName': evetypes.GetGroupNameByGroup(groupID)}), subMenuData=subMenuData)


def _GetToggleSubEntry(tabID, groupID):
    presetSvc = sm.GetService('overviewPresetSvc')
    presetName = presetSvc.GetTabSettings(tabID)[overviewSettingsConst.SETTING_OVERVIEW_PRESET_NAME]
    tabName = presetSvc.GetTabName(tabID)
    if presetSvc.IsGroupIDShown(groupID, presetName):
        label = MenuLabel('UI/Overview/RemoveGroupToTab', {'tabName': tabName})
        return MenuEntryData(label, lambda : sm.GetService('overviewPresetSvc').RemoveGroupIDFromPreset(groupID, presetName))
    else:
        label = MenuLabel('UI/Overview/AddGroupToTab', {'tabName': tabName})
        return MenuEntryData(label, lambda : sm.GetService('overviewPresetSvc').AddGroupIDToPreset(groupID, presetName))


def GetAddGroupToOverviewEntry(groupID):
    label = MenuLabel('UI/Overview/AddGroupToOverview', {'groupName': evetypes.GetGroupNameByGroup(groupID)})
    return MenuEntryData(label, lambda : sm.GetService('overviewPresetSvc').AddGroupIDToPreset(groupID))


def GetRemoveGroupFromOverviewEntry(groupID):
    label = MenuLabel('UI/Overview/RemoveGroupFromOverview', {'groupName': evetypes.GetGroupNameByGroup(groupID)})
    return MenuEntryData(label, lambda : sm.GetService('overviewPresetSvc').RemoveGroupIDFromPreset(groupID))


def _GetEntry(groupID, label, func):
    presetSvc = sm.GetService('overviewPresetSvc')
    tabIDs = _GetActiveOverviewTabIDs()
    if len(tabIDs) > 1:
        subMenuData = MenuData()
        for tabID in tabIDs:
            presetName = presetSvc.GetTabSettings(tabID)[overviewSettingsConst.SETTING_OVERVIEW_PRESET_NAME]
            subMenuData.AddEntry(presetSvc.GetTabName(tabID), lambda : func(groupID, presetName))

        return MenuEntryData(label, subMenuData=subMenuData)
    return MenuEntryData(label, lambda : func(groupID))


def _GetActiveOverviewTabIDs():
    from eve.client.script.ui.inflight.overview.overviewWindow import OverviewWindow
    windows = uicore.registry.GetWindowsByClass(OverviewWindow)
    return [ window.GetSelectedTabID() for window in windows if window.GetSelectedTabID() is not None ]


def GetBracketVisibilitySubMenu():
    return [MenuEntryDataRadioButton(MenuLabel('UI/Overview/UseSelectedTabBracketPreset'), bracketConst.SHOW_DEFAULT, bracket_display_override_setting), MenuEntryDataRadioButton(MenuLabel('UI/Overview/ShowAll'), bracketConst.SHOW_ALL, bracket_display_override_setting), MenuEntryDataRadioButton(MenuLabel('UI/Overview/HideAll'), bracketConst.SHOW_NONE, bracket_display_override_setting)]


def GetColumnVisibilitySubMenu(tabID):
    menuData = MenuData()
    presetSvc = sm.GetService('overviewPresetSvc')
    visibleColumnIDs = presetSvc.GetTabVisibleColumnIDs(tabID)
    for columnID, label in overviewConst.NAME_BY_COLUMN.iteritems():
        columnSetting = ColumnSetting(columnID in visibleColumnIDs, tabID, columnID)
        columnSetting.on_change.connect(_OnColumnCheckbox)
        hint = overviewConst.COLUMN_DESCRIPTIONS.get(columnID, None)
        if hint:
            hint = GetByLabel(hint)
        menuData.AddCheckbox(GetByLabel(label), columnSetting, hint=hint)

    menuData.AddSeparator()
    menuData.AddEntry(GetByLabel('UI/Overview/ChangeOrder'), lambda : ColumnConfigurationWindow.Open(tabID=tabID))
    return menuData


def _OnColumnCheckbox(value, tabID, columnID):
    presetSvc = sm.GetService('overviewPresetSvc')
    return presetSvc.ToggleTabColumnVisibility(tabID, columnID)


class ColumnSetting(SessionSettingBool):

    def __init__(self, default_value, tabID, columnID):
        super(ColumnSetting, self).__init__(default_value)
        self.tabID = tabID
        self.columnID = columnID

    def _trigger_on_change(self, value):
        self.on_change(value, self.tabID, self.columnID)
