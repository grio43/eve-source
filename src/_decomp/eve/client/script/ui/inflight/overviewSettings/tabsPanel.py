#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\tabsPanel.py
import operator
import eveicon
from bannedwords.client.bannedwords import check_words_allowed
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.combo import Combo
from carbonui.control.comboEntryData import ComboEntryData
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui import uiconst
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.inflight.overview import overviewUtil
from eve.client.script.ui.inflight.overviewSettings.overviewColorPicker import OverviewColorPickerCont
from eveexceptions import UserError
from localization import GetByLabel, util
from overviewPresets import overviewSettingsConst
from overviewPresets.overviewSettingsConst import BRACKET_FILTER_SHOWALL, MAX_TAB_NUM

class TabsPanel(Container):
    default_name = 'tabsPanel'
    default_state = uiconst.UI_HIDDEN
    __notifyevents__ = ['OnOverviewPresetSaved']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.overviewPresetSvc = sm.GetService('overviewPresetSvc')
        self.AddTabForOverviewProfile()
        sm.RegisterNotify(self)

    def AddTabForOverviewProfile(self):
        scrollCont = ScrollContainer(name='scrollCont', parent=self, align=uiconst.TOALL, pos=(4, 0, 4, 4))
        numColumns = 5
        parentGrid = LayoutGrid(name='overviewTabsLayoutGrid', parent=scrollCont, columns=numColumns, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOPLEFT, left=10, top=0, cellSpacing=(15, 8))
        overviewOptions = self.GetFilterOptions()
        bracketOptions = self.GetBracketFilterOptions()
        Container(parent=parentGrid, pos=(0, 0, 0, 0))
        numColToSkip = 1
        for i in xrange(parentGrid.columns - numColToSkip):
            container = Container(pos=(0, 0, 115, 0), name='spacer', align=uiconst.TOPLEFT)
            parentGrid.AddCell(cellObject=container)

        parentGrid.FillRow()
        Container(parent=parentGrid)
        EveLabelMedium(parent=parentGrid, text=GetByLabel('UI/Overview/TabName'), state=uiconst.UI_DISABLED, color=(1, 1, 1, 0.75), width=120)
        EveLabelMedium(parent=parentGrid, text=GetByLabel('UI/Overview/Filter'), state=uiconst.UI_DISABLED, color=(1, 1, 1, 0.75), width=120)
        EveLabelMedium(parent=parentGrid, text=GetByLabel('UI/Overview/BracketFilter'), state=uiconst.UI_DISABLED, color=(1, 1, 1, 0.75), width=120)
        parentGrid.FillRow()
        self.tabedit = {}
        self.comboTabOverview = {}
        self.comboTabBracket = {}
        self.tabColorPickers = {}
        tabsettings = self.overviewPresetSvc.GetSettingsByTabID()
        for i in range(MAX_TAB_NUM):
            comboTabBracketVal, comboTabOverviewVal, newOverviewOptions, tabeditVal, colorVal = self.GetTabInfoForCombos(i, overviewOptions, tabsettings)
            colorPicker = OverviewColorPickerCont(callback=self.SetColorForTab, currentColor=colorVal)
            colorPicker.tabNum = i
            self.tabColorPickers[i] = colorPicker
            parentGrid.AddCell(cellObject=colorPicker, cellSpacing=(0, 0))
            tabedit = SingleLineEditText(name='edit' + str(i), align=uiconst.TOPLEFT, pos=(0, 0, 120, 0), setvalue=tabeditVal, OnFocusLost=self.ChangeTabText, OnReturn=self.OnTabEditReturn, sendSelfAsArgument=True, maxLength=overviewSettingsConst.MAX_TAB_NAME_LENGTH)
            tabedit.originalValue = tabeditVal
            parentGrid.AddCell(cellObject=tabedit)
            self.tabedit[i] = tabedit
            filterCombo = Combo(label='', options=newOverviewOptions or overviewOptions, name='filterCombo', align=uiconst.TOPLEFT, width=120, callback=self.OnProfileInTabChanged, hint=GetByLabel('UI/Overview/ChooseOverviewPreset'))
            if not comboTabOverviewVal:
                comboTabOverviewVal = self.overviewPresetSvc.GetDefaultPreset()
            filterCombo.SelectItemByValue(comboTabOverviewVal)
            self.comboTabOverview[i] = filterCombo
            parentGrid.AddCell(cellObject=filterCombo)
            bracketFilterCombo = Combo(label='', options=bracketOptions, name='bracketFilterCombo', width=120, align=uiconst.TOPLEFT, callback=self.OnProfileInTabChanged, hint=GetByLabel('UI/Overview/ChooseBracketPreset'))
            if comboTabBracketVal:
                bracketFilterCombo.SelectItemByValue(comboTabBracketVal or BRACKET_FILTER_SHOWALL)
            self.comboTabBracket[i] = bracketFilterCombo
            parentGrid.AddCell(cellObject=bracketFilterCombo)
            removeBtn = ButtonIcon(align=uiconst.CENTERLEFT, width=24, height=24, iconSize=16, texturePath=eveicon.close, func=lambda tabID = i: self.overviewPresetSvc.DeleteTab(tabID=tabID), hint=GetByLabel('UI/Overview/DeleteTab'))
            parentGrid.AddCell(cellObject=removeBtn)

        return scrollCont

    def GetFilterOptions(self):
        return overviewUtil.GetFilterComboOptions()

    def GetBracketFilterOptions(self):
        bracketOptions = overviewUtil.GetFilterComboOptions()
        bracketOptions.insert(0, ComboEntryData(GetByLabel('UI/Overview/ShowAllBrackets'), BRACKET_FILTER_SHOWALL))
        return bracketOptions

    def UpdateOverviewTab(self, *args):
        tabSettings = {}
        for key in self.tabedit.keys():
            editContainer = self.tabedit.get(key, None)
            comboTabBracketContainer = self.comboTabBracket.get(key, None)
            comboTabOverviewContainer = self.comboTabOverview.get(key, None)
            colorPicker = self.tabColorPickers.get(key, None)
            if not (editContainer and comboTabOverviewContainer and comboTabBracketContainer):
                continue
            tabColor = None
            if colorPicker:
                tabColor = colorPicker.currentColor
            tabName = editContainer.text
            if not tabName:
                continue
            presetName = comboTabOverviewContainer.selectedValue
            bracketPresetName = comboTabBracketContainer.selectedValue
            if self.overviewPresetSvc.GetTabSettings(key):
                self.overviewPresetSvc.UpdateTab(key, tabName, presetName, bracketPresetName, tabColor)
            else:
                wndInstID = self.overviewPresetSvc.GetDefaultWindowInstanceID()
                self.overviewPresetSvc.AddTab(tabName, presetName, bracketPresetName, wndInstID, tabColor)

    def OnProfileInTabChanged(self, *args):
        self.UpdateOverviewTab()

    def ChangeTabText(self, editField):
        self.CheckEditFieldBannedWord(editField)
        currentValue = editField.GetValue()
        if currentValue != editField.originalValue:
            self.UpdateOverviewTab()

    def OnTabEditReturn(self, edit):
        self.CheckEditFieldBannedWord(edit)
        return self.UpdateOverviewTab()

    def SetColorForTab(self, *args):
        self.UpdateOverviewTab()

    def CheckEditFieldBannedWord(self, editField):
        try:
            check_words_allowed(editField.GetValue())
        except UserError:
            editField.SetValue('')
            raise

    def RefreshOverviewTab(self):
        tabSettings = self.overviewPresetSvc.GetSettingsByTabID()
        for key, editContainer in self.tabedit.iteritems():
            tSetting = tabSettings.get(key, {})
            if tSetting is None:
                continue
            filterCombo = self.comboTabOverview.get(key, None)
            bracketFilterCombo = self.comboTabBracket.get(key, None)
            tabColorPicker = self.tabColorPickers.get(key, None)
            editField = self.tabedit.get(key, None)
            if None in (filterCombo, bracketFilterCombo, editField):
                continue
            overviewSetting = tSetting.get('overview', None)
            bracketSetting = tSetting.get('bracket', None)
            tabName = tSetting.get('name', '')
            tabColor = tSetting.get('color', None)
            overviewOptions = self.GetFilterOptions()
            newOverviewOptions = None
            if self.overviewPresetSvc.IsUnsavedPreset(overviewSetting):
                currBracket, currOverview, newOverviewOptions, tabName, colorVal = self.GetTabInfoForCombos(key, overviewOptions, tabSettings)
            filterCombo.LoadOptions(newOverviewOptions or overviewOptions)
            if not overviewSetting:
                overviewSetting = self.overviewPresetSvc.GetDefaultPreset()
            filterCombo.SelectItemByValue(overviewSetting)
            if bracketSetting:
                bracketFilterCombo.SelectItemByValue(bracketSetting or BRACKET_FILTER_SHOWALL)
            editField.SetText(tabName)
            editField.originalValue = tabName
            if tabColorPicker:
                tabColorPicker.SetCurrentFill(tabColor)

    def GetBracketAndOverviewOptions(self, includeEmpty = True):
        overviewOptions = []
        bracketOptions = []
        if includeEmpty:
            bracketOptions = [[GetByLabel('UI/Overview/ShowAllBrackets'), None]]
        presets = self.overviewPresetSvc.GetAllPresets()
        bothOptions = []
        defaults = []
        for label in presets.keys():
            if self.overviewPresetSvc.IsUnsavedPreset(label):
                continue
            elif label == 'ccp_notsaved':
                bothOptions.append(('   ', [GetByLabel('UI/Overview/NotSaved'), label]))
            else:
                overviewName = self.overviewPresetSvc.GetDefaultOverviewDisplayName(label)
                optionID = label.lower()
                if overviewName is None:
                    bothOptions.append((optionID, [label, label]))

        for name in sm.GetService('overviewPresetSvc').GetDefaultOverviewPresetNames():
            presetName = sm.GetService('overviewPresetSvc').GetPresetDisplayName(name)
            if presetName is not None:
                defaults.append([presetName, name])

        bothOptions = [ x[1] for x in util.Sort(bothOptions, key=operator.itemgetter(0)) ]
        overviewOptions += bothOptions
        overviewOptions += defaults
        bracketOptions += bothOptions
        bracketOptions += defaults
        return (bracketOptions, overviewOptions)

    def GetTabInfoForCombos(self, i, overviewOptions, tabsettings):
        tabeditVal = ''
        presetName = None
        comboTabBracketVal = None
        newOverviewOptions = None
        colorVal = None
        if i in tabsettings:
            tabeditVal = tabsettings[i].get('name', None)
            comboTabBracketVal = tabsettings[i].get('bracket', None) or None
            presetName = tabsettings[i].get('overview', None)
            colorVal = tabsettings[i].get('color', None)
        return (comboTabBracketVal,
         presetName,
         newOverviewOptions,
         tabeditVal,
         colorVal)

    def OnOverviewPresetSaved(self):
        overviewOptions = self.GetFilterOptions()
        bracketOptions = self.GetBracketFilterOptions()
        tabsettings = self.overviewPresetSvc.GetSettingsByTabID()
        for i in range(MAX_TAB_NUM):
            comboTabOverviewVal = None
            comboTabBracketVal = None
            editFieldText = None
            if tabsettings.has_key(i):
                comboTabOverviewVal = tabsettings[i].get('overview', None)
                comboTabBracketVal = tabsettings[i].get('bracket', None)
                editFieldText = tabsettings[i].get('name', None)
            self.comboTabOverview[i].LoadOptions(overviewOptions, comboTabOverviewVal)
            self.comboTabBracket[i].LoadOptions(bracketOptions, comboTabBracketVal)
            if editFieldText:
                self.tabedit[i].SetText(editFieldText)
                self.tabedit[i].originalValue = editFieldText

    def _GetFilterOptions(self):
        overviewOptions = []
        bracketOptions = [(' ', [GetByLabel('UI/Overview/ShowAllBrackets'), None])]
        presets = self.overviewPresetSvc.GetAllPresets()
        for label in presets.keys():
            if label == 'ccp_notsaved':
                overviewOptions.append(('  ', [GetByLabel('UI/Overview/NotSaved'), label]))
                bracketOptions.append(('  ', [GetByLabel('UI/Overview/NotSaved'), label]))
            else:
                presetName = self.overviewPresetSvc.GetDefaultOverviewDisplayName(label)
                optionID = label.lower()
                if 'DefaultPreset_' in label:
                    optionID = presetName
                if presetName is not None:
                    overviewOptions.append((optionID, [presetName, label]))
                    bracketOptions.append((optionID, [presetName, label]))
                else:
                    overviewOptions.append((optionID, [label, label]))
                    bracketOptions.append((optionID, [label, label]))

        overviewOptions = [ x[1] for x in util.Sort(overviewOptions, key=lambda x: x[0]) ]
        bracketOptions = [ x[1] for x in util.Sort(bracketOptions, key=lambda x: x[0]) ]
        return (bracketOptions, overviewOptions)
