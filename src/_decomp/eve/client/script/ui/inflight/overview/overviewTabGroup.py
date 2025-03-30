#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overview\overviewTabGroup.py
import eveicon
import localization
from carbon.common.script.util.commonutils import StripTags
from carbonui import TextColor
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from eve.client.script.parklife.overview.default import categories
from eve.client.script.ui import menuUtil
from carbonui.control.tab import Tab
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.inflight.overview import overviewSettings
from eve.client.script.ui.inflight.overview.overviewMenuUtil import GetColumnVisibilitySubMenu
from eve.client.script.ui.inflight.overview.overviewUtil import GetCustomFiltersSorted, GetDefaultFiltersByCategory
from eve.client.script.ui.inflight.overviewSettings.overviewSettingsWnd import OverviewSettingsWnd
from eve.client.script.ui.util.utilWindows import NamePopup
from localization import GetByLabel
from overviewPresets import overviewSettingsConst
from overviewPresets.overviewSettingsConst import SETTING_OVERVIEW_PRESET_NAME, SETTING_BRACKET_PRESET_NAME, SETTING_TAB_NAME, BRACKET_FILTER_SHOWALL
FILTERS_GROUPING_THRESHOLD = 10

class OverviewTab(Tab):

    def ApplyAttributes(self, attributes):
        self.presetSvc = sm.GetService('overviewPresetSvc')
        return super(OverviewTab, self).ApplyAttributes(attributes)

    def LoadTooltipPanel(self, tooltipPanel, tab):
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 2
        wrapWidth = 150
        tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Overview/Filter'), wrapWidth=wrapWidth)
        tooltipPanel.AddLabelMedium(text=self._GetFilterLabel(), wrapWidth=wrapWidth, color=TextColor.HIGHLIGHT)
        description = self._GetFilterDescription()
        if description:
            tooltipPanel.AddLabelMedium(text=description, wrapWidth=2 * wrapWidth, colSpan=2, color=TextColor.SECONDARY, cellPadding=(8, 0, 8, 8))
        if self.presetSvc.IsBracketFilterDictatingTab(self.tabID):
            tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Overview/BracketFilter'), wrapWidth=wrapWidth)
            tooltipPanel.AddLabelMedium(text=self._GetBracketFilterLabel(), wrapWidth=wrapWidth, color=TextColor.HIGHLIGHT)
        if overviewSettings.show_debug_info.is_enabled():
            tooltipPanel.AddLabelMedium(text='tabID=%s' % self.tabID)

    def _GetBracketFilterLabel(self):
        tabSettings = self.presetSvc.GetTabSettings(self.tabID)
        bracketPresetName = tabSettings.get(SETTING_BRACKET_PRESET_NAME, None)
        if bracketPresetName:
            bracketLabel = self.presetSvc.GetPresetDisplayName(bracketPresetName)
        else:
            bracketLabel = localization.GetByLabel('UI/Overview/ShowAllBrackets')
        if overviewSettings.show_debug_info.is_enabled():
            bracketLabel += ' (presetName=%s)' % repr(bracketPresetName)
        return bracketLabel

    def _GetFilterLabel(self):
        presetName = self._GetPresetName()
        overviewLabel = self.presetSvc.GetPresetDisplayName(presetName)
        if overviewSettings.show_debug_info.is_enabled():
            overviewLabel += ' (presetName=%s)' % repr(presetName)
        return overviewLabel

    def _GetPresetName(self):
        tabSettings = self.presetSvc.GetTabSettings(self.tabID)
        presetName = tabSettings.get(SETTING_OVERVIEW_PRESET_NAME, None)
        return presetName

    def _GetFilterDescription(self):
        return self.presetSvc.GetDefaultOverviewDescription(self._GetPresetName())

    def GetMenu(self, *args):
        if self.presetSvc.IsReadOnly():
            return []
        ret = [MenuEntryData(GetByLabel('UI/Overview/Filter'), subMenuData=self.GetFiltersSubMenu)]
        if self.presetSvc.IsBracketFilterDictatingTab(self.tabID):
            ret.append(MenuEntryData(GetByLabel('UI/Overview/BracketFilter'), subMenuData=self.GetBracketFiltersSubMenu))
        ret.extend([None, MenuEntryData(GetByLabel('UI/Commands/ChangeName'), self.ChangeTabName), MenuEntryData(GetByLabel('UI/Generic/Columns'), subMenuData=lambda : GetColumnVisibilitySubMenu(self.tabID))])
        if len(self.presetSvc.GetSettingsByTabID()) > 1:
            ret.append(MenuEntryData(GetByLabel('UI/Overview/DeleteTab'), self.DeleteTab, menuGroupID=menuUtil.DESTRUCTIVEGROUP))
        ret.append(MenuEntryData(GetByLabel('UI/Overview/MoveTabTo'), subMenuData=self.GetMoveTabSubMenu()))
        return ret

    def GetMoveTabSubMenu(self):
        menuData = MenuData()
        menuData.AddEntry(GetByLabel('UI/Overview/NewWindow'), lambda : self.presetSvc.MoveTab(self.tabID))
        wndInstIDs = self.presetSvc.GetWindowInstanceIDs()
        if wndInstIDs:
            menuData.AddSeparator()
        for wndInstID in wndInstIDs:
            if wndInstID == self.presetSvc.GetWindowInstanceID(self.tabID):
                continue
            menuData.AddEntry(self.GetWindowName(wndInstID), lambda iid = wndInstID: self.presetSvc.MoveTab(self.tabID, iid))

        return menuData

    def GetWindowName(self, windowInstanceID):
        tabIDs = self.presetSvc.GetTabIDs(windowInstanceID)
        name = ''
        for i, tabID in enumerate(tabIDs):
            if i == 3:
                return name[:-3] + ' ...'
            tabName = self.presetSvc.GetTabSettings(tabID).get(SETTING_TAB_NAME)
            name += tabName + ' - '

        return name[:-3]

    def GetFiltersSubMenu(self):
        m = MenuData()
        self._AddCustomFilterEntries(m, self._AddFilterEntry)
        self._AddDefaultFilterEntries(m, self._AddFilterEntry)
        m.AddSeparator()
        m.AddEntry(GetByLabel('UI/Overview/EditCurrentFilter'), self.EditCurrentFilter, texturePath=eveicon.settings)
        return m

    def EditCurrentFilter(self):
        presetName = self.presetSvc.GetTabPreset(self.tabID)
        self._EditCurrentFilter(presetName)

    def EditCurrentBracketFilter(self):
        presetName = self.presetSvc.GetTabBracketPreset(self.tabID)
        self._EditCurrentFilter(presetName)

    def _EditCurrentFilter(self, presetName):
        wnd = OverviewSettingsWnd.GetIfOpen()
        if wnd:
            wnd.EditPreset(presetName)
        else:
            OverviewSettingsWnd.Open(presetName=presetName)

    def GetBracketFiltersSubMenu(self):
        m = MenuData()
        activePresetName = self.presetSvc.GetTabBracketPreset(self.tabID)
        m.AddEntry(GetByLabel('UI/Overview/ShowAllBrackets'), lambda : self.__ApplyFilter(BRACKET_FILTER_SHOWALL, overviewSettingsConst.SETTING_BRACKET_PRESET_NAME), texturePath=self._GetCheckmarkTexturePath(BRACKET_FILTER_SHOWALL, activePresetName))
        self._AddCustomFilterEntries(m, self._AddBracketFilterEntry)
        self._AddDefaultFilterEntries(m, self._AddBracketFilterEntry)
        m.AddSeparator()
        m.AddEntry(GetByLabel('UI/Overview/EditCurrentFilter'), self.EditCurrentBracketFilter, texturePath=eveicon.settings)
        return m

    def _AddCustomFilterEntries(self, m, addEntryFunc):
        presetNames = GetCustomFiltersSorted()
        menu = self._CheckAddAsSubgroup(m, len(presetNames), GetByLabel('UI/Overview/CustomFilters'))
        for presetName in presetNames:
            addEntryFunc(menu, presetName)

    def _CheckAddAsSubgroup(self, menuData, numPresets, groupName):
        if numPresets > FILTERS_GROUPING_THRESHOLD:
            subMenuData = MenuData()
            menuData.AddSeparator()
            menuData.AddEntry(groupName, subMenuData=subMenuData, texturePath=eveicon.filter)
            return subMenuData
        else:
            if numPresets:
                menuData.AddCaption(groupName)
            return menuData

    def _AddDefaultFilterEntries(self, m, addEntryFunc):
        m.AddCaption(GetByLabel('UI/Overview/DefaultFilters'))
        presetNamesByCategoryID = GetDefaultFiltersByCategory()
        for presetName in presetNamesByCategoryID.get(categories.CATEGORY_NONE, []):
            addEntryFunc(m, presetName)

        for categoryID, presetNames in presetNamesByCategoryID.iteritems():
            self._AddDefaultCategorySubMenu(m, categoryID, presetNames, addEntryFunc)

    def _AddDefaultCategorySubMenu(self, menuData, categoryID, presetNames, addEntryFunc):
        if categoryID == categories.CATEGORY_NONE:
            return
        m = MenuData()
        for presetName in presetNames:
            addEntryFunc(m, presetName)

        menuData.AddEntry(categories.get_name(categoryID), subMenuData=m, texturePath=categories.get_icon(categoryID))

    def _AddFilterEntry(self, menu, presetName):
        activePresetName = self.presetSvc.GetTabPreset(self.tabID)
        menu.AddEntry(self.presetSvc.GetPresetDisplayName(presetName, showCategory=False), lambda p = presetName: self._ApplyFilter(p), texturePath=self._GetCheckmarkTexturePath(presetName, activePresetName), hint=self.presetSvc.GetDefaultOverviewDescription(presetName))

    def _AddBracketFilterEntry(self, menu, presetName):
        activePresetName = self.presetSvc.GetTabBracketPreset(self.tabID)
        menu.AddEntry(self.presetSvc.GetPresetDisplayName(presetName, showCategory=False), lambda p = presetName: self._ApplyBracketFilter(p), texturePath=self._GetCheckmarkTexturePath(presetName, activePresetName), hint=self.presetSvc.GetDefaultOverviewDescription(presetName))

    def _GetCheckmarkTexturePathIfSelected(self, presetName, settingsID):
        if settingsID == SETTING_OVERVIEW_PRESET_NAME:
            activePreset = self.presetSvc.GetTabPreset(self.tabID)
        elif settingsID == SETTING_BRACKET_PRESET_NAME:
            activePreset = self.presetSvc.GetTabBracketPreset(self.tabID)
        return self._GetCheckmarkTexturePath(presetName, activePreset)

    def _GetCheckmarkTexturePath(self, presetName, activePreset):
        if presetName == activePreset:
            return eveicon.checkmark

    def __ApplyFilter(self, presetName, settingsID):
        if settingsID == overviewSettingsConst.SETTING_OVERVIEW_PRESET_NAME:
            self._ApplyFilter(presetName)
        elif settingsID == overviewSettingsConst.SETTING_BRACKET_PRESET_NAME:
            self._ApplyBracketFilter(presetName)

    def _ApplyBracketFilter(self, presetName):
        self.presetSvc.SetTabBracketPreset(self.tabID, presetName)
        if self.IsSelected():
            self.presetSvc.LoadBracketPreset(presetName, False)

    def _ApplyFilter(self, presetName):
        self.presetSvc.SetTabPreset(self.tabID, presetName)
        if self.IsSelected():
            self.presetSvc.LoadPreset(presetName, False)

    def ChangeTabName(self):
        tabName = self.presetSvc.GetTabSettings(self.tabID)[SETTING_TAB_NAME]
        tabName = StripTags(tabName)
        tabName = NamePopup(localization.GetByLabel('UI/Commands/ChangeName'), localization.GetByLabel('/Carbon/UI/Controls/ScrollEntries/TypeInNewName'), tabName, maxLength=30)
        if tabName:
            self.presetSvc.SetTabName(self.tabID, tabName)

    def DeleteTab(self):
        self.presetSvc.DeleteTab(self.tabID)


class OverviewTabGroup(TabGroup):
    default_name = 'OverviewTabGroup'
    default_tabClass = OverviewTab

    def GetUIID(self, name, tabID = None):
        tabsettings = sm.GetService('overviewPresetSvc').GetSettingsByTabID().get(tabID, {})
        presetName = tabsettings.get(SETTING_OVERVIEW_PRESET_NAME, None)
        if presetName:
            return super(OverviewTabGroup, self).GetUIID(name, presetName)
        return super(OverviewTabGroup, self).GetUIID(name, tabID)
