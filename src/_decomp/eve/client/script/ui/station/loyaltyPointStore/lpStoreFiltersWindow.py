#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\loyaltyPointStore\lpStoreFiltersWindow.py
import weakref
import evetypes
import localization
from carbon.client.script.util.misc import TryDel
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.station.loyaltyPointStore.lpLabels import LPStoreHeaderLabel, LPStoreLabel
from eve.client.script.ui.util import utilWindows

class LPStoreFiltersWindow(Window):
    __guid__ = 'form.LPStoreFilters'
    __notifyevents__ = ['OnLPStoreCurrentPresetChange', 'OnLPStorePresetsChange']
    comboParentHeight = 50
    editParentHeight = 50
    checkboxParentHeight = 20
    comboSeparatorHeight = 16
    editSeparatorHeight = 18
    labelSeparatorHeight = 2
    labelParentHeight = 15
    scrollSeparatorHeight = 6
    comboWidth = 150
    default_windowID = 'lpfilter'
    default_captionLabelPath = 'UI/LPStore/Filters'
    default_scope = uiconst.SCOPE_STATION
    default_minSize = (380, 260)

    def ApplyAttributes(self, attributes):
        super(LPStoreFiltersWindow, self).ApplyAttributes(attributes)
        self.corpID = attributes.corpID
        self.lpSvc = sm.GetService('lpstore')
        try:
            self.ConstructContent()
        except Exception as e:
            import log
            log.LogException(e)
            raise

        self.filters = {}
        self.resetters = []
        self.OnEdited = self.OnEdited_Inactive
        self.HookCombos()
        self.resetters.append(self.ResetCheckboxes)
        self.ConstructButtonGroup()
        self.InitPresetsScroll()
        self.RefreshCurrentPresetLabel()
        self.OnEdited = self.OnEdited_Active
        self.SyncInputs()

    def ConstructContent(self):
        main = Container(parent=self.sr.main, name='TabPanelGroupParent', align=uiconst.TOALL)
        tabGroup = TabGroup(parent=main, name='tabs')
        panelParent = Container(parent=main, align=uiconst.TOALL, name='panelParent', state=uiconst.UI_PICKCHILDREN, padding=[uiconst.defaultPadding] * 4)
        tabs = []
        self._MakeRewardTab(tabs, panelParent)
        self._MakeRequiredItemsTab(tabs, panelParent)
        self._MakeFilterPresetsTab(tabs, panelParent)
        tabGroup.Startup(tabs)

    def _MakeTab(self, tabs, panelParent, caption):

        def MakeOnTabSelect(panelWr):

            def OnTabSelect(*args):
                panel = panelWr()
                panel.state = uiconst.UI_PICKCHILDREN
                for sibling in panel.parent.children:
                    if sibling is not panelWr():
                        sibling.state = uiconst.UI_HIDDEN

            return OnTabSelect

        panel = Container(parent=panelParent, name=caption, align=uiconst.TOALL)
        panel.OnTabSelect = MakeOnTabSelect(weakref.ref(panel))
        tabs.append((caption,
         panel,
         None,
         (caption + '_args',)))
        return panel

    def _MakeRewardTab(self, tabs, panelParent):
        tab = self._MakeTab(tabs, panelParent, localization.GetByLabel('UI/LPStore/Reward'))
        Container(parent=tab, name='rewardComboSeparator', height=self.comboSeparatorHeight, align=uiconst.TOTOP, state=uiconst.UI_DISABLED)
        rewardCategoryComboParent = Container(parent=tab, name='rewardCategoryComboParent', height=self.comboParentHeight, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        self.sr.rewardCategoryCombo = Combo(parent=rewardCategoryComboParent, name='rewardCategoryCombo', label=localization.GetByLabel('UI/Common/Category'), width=self.comboWidth, align=uiconst.RELATIVE)
        rewardGroupComboParent = Container(parent=tab, name='rewardGroupComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.rewardGroupCombo = Combo(parent=rewardGroupComboParent, name='rewardGroupCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Group'))
        rewardTypeComboParent = Container(parent=tab, name='rewardTypeComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.rewardTypeCombo = Combo(parent=rewardTypeComboParent, name='rewardTypeCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Type'))

    def _MakeRequiredItemsTab(self, tabs, panelParent):
        tab = self._MakeTab(tabs, panelParent, localization.GetByLabel('UI/LPStore/RequiredItems'))
        reqItemsHeaderParent = Container(parent=tab, name='reqItemsHeaderParent', height=18, align=uiconst.TOTOP)
        LPStoreHeaderLabel(parent=reqItemsHeaderParent, text=localization.GetByLabel('UI/LPStore/FilterRequiredItemsHeader'))
        reqIllegalCbParent = Container(parent=tab, name='reqIllegalCbParent', height=self.checkboxParentHeight, align=uiconst.TOTOP)
        self.sr.reqIllegalCb = Checkbox(parent=reqIllegalCbParent, name='reqIllegalCb', text=localization.GetByLabel('UI/LPStore/FilterRequiredItemsAreIllegal'), align=uiconst.TOTOP, callback=self.OnReqIllegalCheckboxChange)
        reqNotInHangarCbParent = Container(parent=tab, name='reqNotInHangarCbParent', height=self.checkboxParentHeight, align=uiconst.TOTOP)
        self.sr.reqNotInHangarCb = Checkbox(parent=reqNotInHangarCbParent, name='reqNotInHangarCb', text=localization.GetByLabel('UI/LPStore/FilterRequiredItemsNotInHangar'), align=uiconst.TOTOP, callback=self.OnReqNotInHangarCheckboxChange)
        Container(parent=tab, name='reqItemsOrMatchTypeLabelSeparator', height=10, align=uiconst.TOTOP)
        reqItemsOrMatchTypeLabelParent = Container(parent=tab, name='reqItemsOrMatchTypeLabelParent', height=16, align=uiconst.TOTOP)
        LPStoreHeaderLabel(parent=reqItemsOrMatchTypeLabelParent, text=localization.GetByLabel('UI/LPStore/FilterRequiredItemsType'), height=16)
        Container(parent=tab, name='reqComboSeparator', height=self.comboSeparatorHeight, align=uiconst.TOTOP)
        reqCategoryComboParent = Container(parent=tab, name='reqCategoryComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.reqCategoryCombo = Combo(parent=reqCategoryComboParent, name='reqCategoryCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Category'))
        reqGroupComboParent = Container(parent=tab, name='reqGroupComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.reqGroupCombo = Combo(parent=reqGroupComboParent, name='reqGroupCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Group'))
        reqTypeComboParent = Container(parent=tab, name='reqTypeComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.reqTypeCombo = Combo(parent=reqTypeComboParent, name='reqTypeCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Type'))

    def _MakeFilterPresetsTab(self, tabs, panelParent):
        tab = self._MakeTab(tabs, panelParent, localization.GetByLabel('UI/LPStore/FilterPresets'))
        Container(parent=tab, name='presetsHeaderSeparator', height=self.labelSeparatorHeight, align=uiconst.TOTOP)
        currentPresetHeaderParent = Container(parent=tab, name='currentPresetHeaderParent', height=16, align=uiconst.TOTOP)
        LPStoreHeaderLabel(name='currentPresetHeader', parent=currentPresetHeaderParent, text=localization.GetByLabel('UI/LPStore/ActivePresetName'))
        currentPresetLabelParent = Container(parent=tab, name='currentPresetLabelParent', height=16, align=uiconst.TOTOP)
        self.sr.currentPresetLabel = LPStoreLabel(name='currentPresetLabel', parent=currentPresetLabelParent, text=localization.GetByLabel('UI/LPStore/PresetAll'))
        btnsGrandParent = Container(parent=tab, name='btnsGrandParent', height=15, align=uiconst.TOBOTTOM)
        self.sr.btnsParent = Container(parent=btnsGrandParent, name='btnsParent', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        Container(parent=tab, name='presetsScrollSeparator', height=self.scrollSeparatorHeight, align=uiconst.TOTOP)
        Container(parent=tab, name='presetsScrollSeparator', height=self.scrollSeparatorHeight, align=uiconst.TOBOTTOM)
        self.sr.presetsScroll = eveScroll.Scroll(name='presetsScroll', parent=tab, align=uiconst.TOALL)

    def HookCombos(self):
        all = [(localization.GetByLabel('UI/Common/All'), 'all')]

        def MakeOnTypeComboChange(filterKey):

            def OnTypeComboChange(blah, bleh, id):
                if id == 'all':
                    TryDel(self.filters, filterKey)
                else:
                    self.filters[filterKey] = id
                self.OnEdited()

            return OnTypeComboChange

        def GetGroupChoices(categoryID):
            ret = []
            for groupID in evetypes.GetGroupIDsByCategory(categoryID):
                if evetypes.IsGroupPublishedByGroup(groupID):
                    ret.append((evetypes.GetGroupNameByGroup(groupID), groupID))

            ret.sort()
            return ret

        def GetTypeChoices(groupID):
            ret = []
            for typeID in evetypes.GetTypeIDsByGroup(groupID):
                if evetypes.IsPublished(typeID):
                    ret.append((evetypes.GetName(typeID), typeID))

            ret.sort()
            return ret

        def MakeOnCategoryComboChange(filterKey, dependant):

            def OnCategoryComboChange(blah, bleh, id):
                if id == 'all':
                    TryDel(self.filters, filterKey)
                else:
                    self.filters[filterKey] = id
                if dependant is not None:
                    if id == 'all':
                        dependant.state = uiconst.UI_HIDDEN
                    else:
                        dependant.state = uiconst.UI_NORMAL
                        dependant.LoadOptions(all + GetGroupChoices(id))
                    dependant.OnChange(None, None, 'all')
                self.OnEdited()

            return OnCategoryComboChange

        def MakeOnGroupComboChange(filterKey, dependant):

            def OnCategoryComboChange(blah, bleh, id):
                if id == 'all':
                    TryDel(self.filters, filterKey)
                else:
                    self.filters[filterKey] = id
                if dependant is not None:
                    if id == 'all':
                        dependant.state = uiconst.UI_HIDDEN
                    else:
                        dependant.state = uiconst.UI_NORMAL
                        dependant.LoadOptions(all + GetTypeChoices(id))
                    dependant.OnChange(None, None, 'all')
                self.OnEdited()

            return OnCategoryComboChange

        categories = []
        for categoryID in evetypes.GetAllCategoryIDs():
            if evetypes.IsCategoryPublishedByCategory(categoryID):
                categories.append((evetypes.GetCategoryNameByCategory(categoryID), categoryID))

        categories.sort()
        typeSuites = ('reward', 'req')
        for typeSuite in typeSuites:
            typeCombo = self.sr.Get('%sTypeCombo' % typeSuite)
            groupCombo = self.sr.Get('%sGroupCombo' % typeSuite)
            categCombo = self.sr.Get('%sCategoryCombo' % typeSuite)
            typeCombo.OnChange = MakeOnTypeComboChange(typeSuite + 'Type')
            groupCombo.OnChange = MakeOnGroupComboChange(typeSuite + 'Group', typeCombo)
            categCombo.OnChange = MakeOnCategoryComboChange(typeSuite + 'Category', groupCombo)
            categCombo.LoadOptions(all + categories)
            categCombo.OnChange(None, None, 'all')

        def ResetCombos():
            for typeSuite in typeSuites:
                for metaType in ('Type', 'Group', 'Category'):
                    combo = self.sr.Get('%s%sCombo' % (typeSuite, metaType))
                    setting = self.filters.get(typeSuite + metaType, 'all')
                    combo.SelectItemByValue(setting)
                    combo.OnChange(None, None, setting)

        self.resetters.append(ResetCombos)

    def OnReqIllegalCheckboxChange(self, cb):
        key = 'reqNotInHangar'
        if cb.checked:
            self.filters[key] = True
        else:
            TryDel(self.filters, key)
        self.OnEdited()

    def OnReqNotInHangarCheckboxChange(self, cb):
        key = 'reqIllegal'
        if cb.checked:
            self.filters[key] = True
        else:
            TryDel(self.filters, key)
        self.OnEdited()

    def ResetCheckboxes(self):
        self.sr.reqIllegalCb.SetChecked(self.filters.get('reqIllegal', False))
        self.sr.reqNotInHangarCb.SetChecked(self.filters.get('reqNotInHangar', False))

    def ConstructButtonGroup(self):
        self.buttonGroup = ButtonGroup(name='presetsActionButtonGroup', parent=self.sr.btnsParent, align=uiconst.CENTER, top=-2)
        self.buttonGroup.AddButton(label=localization.GetByLabel('UI/Common/Buttons/New'), func=self.OnClickNew, hint=localization.GetByLabel('UI/LPStore/HintNewPreset'))
        self.sr.loadBtn = self.buttonGroup.AddButton(label=localization.GetByLabel('UI/Common/Buttons/Load'), func=self.OnClickLoad, hint=localization.GetByLabel('UI/LPStore/HintLoadPreset'))
        self.sr.overwriteBtn = self.buttonGroup.AddButton(label=localization.GetByLabel('UI/Common/Buttons/Overwrite'), func=self.OnClickOverwrite, hint=localization.GetByLabel('UI/LPStore/HintOverwritePreset'))
        self.sr.delBtn = self.buttonGroup.AddButton(label=localization.GetByLabel('UI/Common/Buttons/Delete'), func=self.OnClickDelete, hint=localization.GetByLabel('UI/LPStore/HintDeletePreset'))
        self.RefreshVisibleButtons()

    def InitPresetsScroll(self):
        self.sr.presetsScroll.multiSelect = False
        self.sr.presetsScroll.OnSelectionChange = self.OnPresetsScrollSelectionChange
        self.RefreshPresetsScroll()

    def OnLPStorePresetsChange(self):
        self.RefreshPresetsScroll()

    def RefreshPresetsScroll(self):
        self.sr.presetsScroll.Load(contentList=[ GetFromClass(Generic, preset) for preset in self.lpSvc.GetPresets() if preset.label != localization.GetByLabel('UI/LPStore/PresetNone') ])

    def OnPresetsScrollSelectionChange(self, *etc):
        self.RefreshVisibleButtons()

    def RefreshVisibleButtons(self):
        sel = self.sr.presetsScroll.GetSelected()
        if not sel:
            self.sr.loadBtn.state = uiconst.UI_HIDDEN
            self.sr.overwriteBtn.state = uiconst.UI_HIDDEN
            self.sr.delBtn.state = uiconst.UI_HIDDEN
        elif not sel[0].editable:
            self.sr.loadBtn.state = uiconst.UI_NORMAL
            self.sr.overwriteBtn.state = uiconst.UI_HIDDEN
            self.sr.overwriteBtn.state = uiconst.UI_HIDDEN
            self.sr.delBtn.state = uiconst.UI_HIDDEN
        else:
            self.sr.loadBtn.state = uiconst.UI_NORMAL
            self.sr.overwriteBtn.state = uiconst.UI_NORMAL
            self.sr.delBtn.state = uiconst.UI_NORMAL
        self.buttonGroup.ResetLayout()

    def OnClickNew(self, *blah):

        def Validate(data):
            name = data
            if not name:
                return localization.GetByLabel('UI/LPStore/ErrorNoName', cancelLabel=localization.GetByLabel('UI/Common/Buttons/Cancel'))
            if name in [ preset.label for preset in self.lpSvc.GetPresets() ]:
                return localization.GetByLabel('UI/LPStore/ErrorExistingName', overwriteLabel=localization.GetByLabel('UI/Common/Buttons/Overwrite'))

        result = utilWindows.NamePopup(maxLength=50, validator=Validate)
        if result:
            self.lpSvc.AddPreset(result, self.filters.copy())

    def SelectedPreset(self):
        return self.sr.presetsScroll.GetSelected()[0]

    def OnClickLoad(self, *blah):
        self.LoadPreset(self.SelectedPreset())

    def LoadPreset(self, preset):
        self.lpSvc.ChangeCurrentPreset(preset.label)

    def OnLPStoreCurrentPresetChange(self):
        self.RefreshCurrentPresetLabel()
        if self.lpSvc.GetCurrentPresetLabel() != localization.GetByLabel('UI/LPStore/PresetNone'):
            self.SyncInputs()

    def SyncInputs(self):
        self.OnEdited = self.OnEdited_Inactive
        try:
            self.filters = self.lpSvc.GetCurrentFilters()
            for Reset in self.resetters:
                Reset()

        finally:
            self.OnEdited = self.OnEdited_Active

    def RefreshCurrentPresetLabel(self):
        self.sr.currentPresetLabel.text = self.lpSvc.GetCurrentPresetLabel()

    def OnClickOverwrite(self, *blah):
        self.OverwritePreset(self.SelectedPreset())

    def OverwritePreset(self, preset):
        if eve.Message('ConfirmOverwriteLPStoreFilterPreset', {}, uiconst.OKCANCEL, uiconst.ID_OK) == uiconst.ID_OK:
            self.lpSvc.OverwritePreset(preset.label, self.filters)

    def OnClickDelete(self, *blah):
        self.DeletePreset(self.SelectedPreset())
        self.RefreshVisibleButtons()

    def DeletePreset(self, preset):
        if eve.Message('ConfirmDeleteLPStoreFilterPreset', {}, uiconst.OKCANCEL, uiconst.ID_OK) == uiconst.ID_OK:
            self.lpSvc.DeletePreset(preset.label)
            self.RefreshPresetsScroll()

    def OnEdited_Active(self):
        self.lpSvc.ChangeFilters(self.filters)

    def OnEdited_Inactive(self):
        pass
