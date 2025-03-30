#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\tabPresetsPanel.py
from collections import defaultdict
import evetypes
import overviewPresets.overviewSettingsConst as osConst
from carbonui import ButtonVariant, Density, TextColor, uiconst
from carbonui.control.button import Button
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.parklife.overview import overviewSignals
from eve.client.script.parklife.state import GetNPCGroups
from eve.client.script.parklife.tacticalConst import get_groups
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control import eveLabel
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.listgroup import ListGroup
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.inflight.overview.overviewUtil import GetFilterComboOptions
from eve.client.script.ui.inflight.overviewSettings.overviewSettingEntries import OverviewTabPresetEntry
from eve.client.script.ui.inflight.overviewSettings.statesPanel import StatesPanel
from eve.client.script.ui.quickFilter import QuickFilterEdit
from localization import GetByLabel
from overviewPresets import overviewSettingsConst
from utillib import KeyVal
FILTER_STATES = 'filterstates'
FILTER_TYPES = 'filtertypes'

class TabPresetPanel(Container):
    default_name = 'tabPresetPanel'
    default_state = uiconst.UI_HIDDEN
    __notifyevents__ = ['OnOverviewPresetsChanged']

    def ApplyAttributes(self, attributes):
        super(TabPresetPanel, self).ApplyAttributes(attributes)
        self.specialGroups = GetNPCGroups()
        self.bracketTexturesForGroupID = defaultdict(set)
        self.presetSvc = sm.GetService('overviewPresetSvc')
        eveLabel.EveLabelLarge(parent=self, text=GetByLabel('UI/Overview/FilterToEdit'), align=uiconst.TOTOP, padTop=8)
        topCont = Container(parent=self, align=uiconst.TOTOP, padding=(0, 4, 0, 8), height=HEIGHT_NORMAL)
        self.presetCombo = Combo(name='presetCombo', parent=topCont, align=uiconst.TOLEFT, callback=self.OnPresetCombo)
        self.deleteButton = Button(parent=topCont, align=uiconst.TOLEFT, padLeft=4, label=GetByLabel('UI/Common/Delete'), func=self.OnDeleteButton, variant=ButtonVariant.GHOST)
        overviewSignals.on_preset_saved.connect(self.OnOverviewPresetsChanged)
        overviewSignals.on_preset_saved_as.connect(self.OnOveriewPresetSavedAs)
        overviewSignals.on_preset_created.connect(self.OnOverviewPresetsChanged)
        overviewSignals.on_preset_deleted.connect(self.OnOverviewPresetsChanged)
        overviewSignals.on_preset_restored.connect(self.OnOverviewPresetsChanged)
        self.tabGroup = TabGroup(name='overviewstatesTab', height=18, align=uiconst.TOTOP, parent=self, groupID='overviewfilterTab', autoselecttab=0, padTop=8, padBottom=0)
        self.statesPanel = StatesPanel(parent=self)
        self.tabGroup.AddTab(GetByLabel('UI/Overview/TypesShown'), None, self, FILTER_TYPES)
        self.tabGroup.AddTab(GetByLabel('UI/Overview/Exceptions'), None, self, FILTER_STATES)
        self.ConstructFilterCont()
        self.scroll = Scroll(name='presetScroll', parent=self)
        self.scroll.multiSelect = 0
        self.scroll.SelectAll = self.SelectAll
        self.buttonGroup = ButtonGroup(parent=self, idx=0, padTop=8)
        self.revertButton = self.buttonGroup.AddButton(GetByLabel('UI/Common/Buttons/Revert'), self.OnRevertButton)
        self.saveButton = self.buttonGroup.AddButton(GetByLabel('UI/Common/Buttons/Save'), self.OnSaveButton)
        self.saveAsButton = self.buttonGroup.AddButton(GetByLabel('UI/Common/Buttons/SaveAs'), self.OnSaveAsButton)
        self.PopulatePresetsCombo()
        self.UpdateButtonVisibility()

    def OnOveriewPresetSavedAs(self, presetName, newPresetName):
        self.OnOverviewPresetsChanged()
        if presetName == self.GetSelectedPresetName():
            self.presetCombo.SelectItemByValue(newPresetName)

    def OnDeleteButton(self, *args):
        self.presetSvc.DeletePreset(self.GetSelectedPresetName())

    def OnRevertButton(self, *args):
        if uicore.Message('RevertOverviewPresetChanges', {}, uiconst.YESNO) == uiconst.ID_YES:
            self.presetSvc.RevertUnsaved(self.GetSelectedPresetName())

    def OnSaveButton(self, *args):
        self.presetSvc.SavePreset(self.GetSelectedPresetName())

    def OnSaveAsButton(self, *args):
        self.presetSvc.SavePresetAs(self.GetSelectedPresetName())

    def OnOverviewPresetsChanged(self, *args):
        self.PopulatePresetsCombo()
        self.UpdateButtonVisibility()
        self.tabGroup.ReloadVisible()

    def PopulatePresetsCombo(self):
        presetID = self.presetCombo.GetValue()
        self.presetCombo.LoadOptions(GetFilterComboOptions())
        self.presetCombo.SelectItemByValue(presetID or self.presetSvc.GetActiveOverviewPresetName())

    def OnPresetCombo(self, combo, presetDisplayName, presetName):
        self._LoadPreset(presetName)

    def ConstructFilterCont(self):
        self.filterCont = Container(name='filterCont', parent=self, align=uiconst.TOTOP, height=32, padding=(0, 16, 0, 8))
        Button(parent=self.filterCont, label=GetByLabel('UI/Common/SelectAll'), func=self.SelectAll, align=uiconst.TOLEFT, density=Density.COMPACT, variant=ButtonVariant.GHOST)
        Button(parent=self.filterCont, label=GetByLabel('UI/Common/DeselectAll'), func=self.DeselectAll, align=uiconst.TOLEFT, density=Density.COMPACT, variant=ButtonVariant.GHOST, padLeft=4)
        self.groupQuickFilter = QuickFilterEdit(name='search', parent=self.filterCont, pos=(5, 0, 150, 0), align=uiconst.TOPRIGHT)
        self.groupQuickFilter.ReloadFunction = self.LoadFilteredTypes

    def Load(self, key):
        if key == FILTER_TYPES:
            self.scroll.display = True
            self.statesPanel.display = False
            self.filterCont.display = True
            self.LoadTypes()
        elif key == FILTER_STATES:
            self.scroll.display = False
            self.statesPanel.display = True
            self.filterCont.display = False
            self.statesPanel.Load()

    def CheckBoxChange(self, checkbox, node):
        changeList = [(checkbox.GetSettingsKey(), node.retval, checkbox.checked)]
        self.presetSvc.ChangeSettings(changeList=changeList, presetName=self.GetSelectedPresetName())

    def LoadPanel(self):
        self.tabGroup.AutoSelect()
        self.PopulatePresetsCombo()

    def LoadFilteredTypes(self, *args):
        self.LoadTypes()

    def LoadPreset(self, presetName):
        self.presetCombo.SelectItemByValue(presetName, triggerCallback=True)

    def _LoadPreset(self, presetName):
        self.presetCombo.SelectItemByValue(presetName)
        self.UpdateButtonVisibility()
        self.statesPanel.SetPresetName(presetName)
        if self.tabGroup.IsVisible() and self.tabGroup.GetSelectedArgs() in (FILTER_TYPES, FILTER_STATES):
            self.tabGroup.ReloadVisible()

    def UpdateButtonVisibility(self):
        presetName = self.GetSelectedPresetName()
        isUnsaved = self.presetSvc.IsUnsavedPreset(presetName)
        isDefaultName = self.presetSvc.IsDefaultPresetName(presetName)
        if isUnsaved:
            self.revertButton.Enable()
        else:
            self.revertButton.Disable()
        if isUnsaved and not isDefaultName:
            self.saveButton.Enable()
        else:
            self.saveButton.Disable()
        if not isDefaultName:
            self.deleteButton.Show()
        else:
            self.deleteButton.Hide()

    def LoadTypes(self):
        filterText = self.groupQuickFilter.GetValue()
        categoryList = self.GetListOfCategories(filterText=filterText.lower())
        sortCat = categoryList.keys()
        sortCat.sort()
        scrolllist = []
        userSettings = self.presetSvc.GetPresetGroupsFromKey(self.GetSelectedPresetName())
        for catName in sortCat:
            checkedCounter = 0
            groupItems = categoryList[catName]
            for groupID, name in groupItems:
                if isinstance(groupID, list):
                    for each in groupID:
                        if each in userSettings:
                            checkedCounter += 1
                            break

                else:
                    checkedCounter += int(groupID in userSettings)

            color = self._GetListGroupLabelColor(checkedCounter, groupItems)
            posttext = '<color=%s>%s / %s</color>' % (color, checkedCounter, len(groupItems))
            label = '<color=%s>%s</color>' % (color, catName)
            data = {'GetSubContent': self.GetCatSubContent,
             'label': label,
             'MenuFunction': self.GetSubFolderMenu,
             'id': ('GroupSel', catName),
             'groupItems': groupItems,
             'showlen': 0,
             'sublevel': 0,
             'state': 'locked',
             'presetName': self.GetSelectedPresetName(),
             'showicon': 'hide',
             'posttext': posttext}
            scrolllist.append(GetFromClass(ListGroup, data))

        self.scroll.Load(contentList=scrolllist)

    def _GetListGroupLabelColor(self, checkedCounter, groupItems):
        if checkedCounter >= len(groupItems):
            return eveThemeColor.THEME_ACCENT.hex_argb
        elif checkedCounter > 0:
            return TextColor.HIGHLIGHT.hex_argb
        else:
            return TextColor.SECONDARY.hex_argb

    def GetSelectedPresetName(self):
        return self.presetCombo.GetValue()

    def GetSubFolderMenu(self, node):
        m = [None, (GetByLabel('UI/Common/SelectAll'), self.SelectGroup, (node, True)), (GetByLabel('UI/Common/DeselectAll'), self.SelectGroup, (node, False))]
        return m

    def SelectGroup(self, node, isSelect):
        groups = []
        for entry in node.groupItems:
            if type(entry[0]) == list:
                for entry1 in entry[0]:
                    groups.append(entry1)

            else:
                groups.append(entry[0])

        changeList = [(overviewSettingsConst.PRESET_SETTINGS_GROUPS, groups, isSelect)]
        self.presetSvc.ChangeSettings(changeList=changeList, presetName=self.GetSelectedPresetName())

    def GetCatSubContent(self, nodedata, newitems = 0):
        presetName = nodedata.presetName
        userSettings = self.presetSvc.GetPresetGroupsFromKey(presetName)
        scrolllist = []
        for groupID, name in nodedata.groupItems:
            texturePaths = set()
            if type(groupID) == list:
                for each in groupID:
                    if each in userSettings:
                        checked = 1
                        break
                else:
                    checked = 0

            else:
                texturePaths = self.GetBracketTextureForGroupID(groupID)
                name = evetypes.GetGroupNameByGroup(groupID)
                checked = groupID in userSettings
            data = KeyVal()
            data.label = name
            data.sublevel = 1
            data.checked = checked
            data.cfgname = osConst.CONFIG_GROUPS
            data.retval = groupID
            data.OnChange = self.CheckBoxChange
            data.texturePaths = texturePaths
            entry = GetFromClass(OverviewTabPresetEntry, data)
            scrolllist.append((name, entry))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def GetBracketTextureForGroupID(self, groupID):
        if isinstance(groupID, list):
            return set()
        if groupID not in self.bracketTexturesForGroupID:
            texturePaths = self.FindBracketsForTypesInGroup(groupID)
            if texturePaths is None:
                bracketData = sm.GetService('bracket').GetBracketDataByGroupID(groupID)
                texturePaths = {bracketData.texturePath} if bracketData else set()
            self.bracketTexturesForGroupID[groupID] = texturePaths
        return self.bracketTexturesForGroupID[groupID]

    def FindBracketsForTypesInGroup(self, groupID):
        bracketSvc = sm.GetService('bracket')
        texturePaths = set()
        for eachTypeID in evetypes.GetTypeIDsByGroup(groupID):
            bracketData = bracketSvc.GetBracketDataByTypeID(eachTypeID)
            if not bracketData:
                continue
            texturePaths.add(bracketData.texturePath)

        return texturePaths

    def GetListOfCategories(self, filterText = ''):
        categoryList = {}
        for _, groupid_name_tuple in get_groups():
            groupID, name = groupid_name_tuple
            if filterText and name.lower().find(filterText) < 0:
                continue
            for cat, groupdict in self.specialGroups.iteritems():
                for group, groupIDs in groupdict.iteritems():
                    if groupID in groupIDs:
                        catName = cat
                        groupID = groupIDs
                        name = group
                        break
                else:
                    continue

                break
            else:
                catName = evetypes.GetCategoryNameByGroup(groupID)

            if catName not in categoryList:
                categoryList[catName] = [(groupID, name)]
            elif (groupID, name) not in categoryList[catName]:
                categoryList[catName].append((groupID, name))

        return categoryList

    def SelectAll(self, *args):
        presetName = self.GetSelectedPresetName()
        groups = set(self.presetSvc.GetSettingForGroups(presetName))
        for entry in self.scroll.GetNodes():
            if entry.__guid__ == 'listentry.Checkbox':
                entry.checked = 1
                if entry.panel:
                    entry.panel.Load(entry)
            if entry.__guid__ == 'listentry.Group':
                for item in entry.groupItems:
                    if type(item[0]) == list:
                        groups.update(item[0])
                    else:
                        groups.add(item[0])

        if groups:
            self.presetSvc.SavePresetGroupFilters(list(groups), presetName=presetName)

    def DeselectAll(self, *args):
        toRemove = set()
        for entry in self.scroll.GetNodes():
            if entry.__guid__ == 'listentry.Checkbox':
                entry.checked = 0
                if entry.panel:
                    entry.panel.Load(entry)
            if entry.__guid__ == 'listentry.Group':
                for item in entry.groupItems:
                    if type(item[0]) == list:
                        toRemove.update(item[0])
                    else:
                        toRemove.add(item[0])

        presetName = self.GetSelectedPresetName()
        currentGroups = set(self.presetSvc.GetSettingForGroups(presetName))
        newGroups = currentGroups - toRemove
        self.presetSvc.SavePresetGroupFilters(list(newGroups), presetName)

    def GetBtnWidth(self):
        btnWdith = 0
        for btn in self.buttonGroup.buttons:
            btnWdith += btn.width

        return btnWdith
