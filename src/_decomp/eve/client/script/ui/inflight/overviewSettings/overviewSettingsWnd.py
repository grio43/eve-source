#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\overviewSettingsWnd.py
import localization
import overviewPresets.overviewSettingsConst as oConst
from carbonui import uiconst
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control.draggableShareContainer import DraggableShareContainer
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.inflight.overviewSettings.appearancePanel import AppearancePanel
from eve.client.script.ui.inflight.overviewSettings.columnsPanel import ColumnsPanel
from eve.client.script.ui.inflight.overviewSettings.historyPanel import HistoryPanel
from eve.client.script.ui.inflight.overviewSettings.miscPanel import MiscPanel
from eve.client.script.ui.inflight.overviewSettings.shipsPanel import ShipsPanel
from eve.client.script.ui.inflight.overviewSettings.tabPresetsPanel import TabPresetPanel
from eve.client.script.ui.inflight.overviewSettings.tabsPanel import TabsPanel
from localization import GetByLabel
from menu import MenuLabel

class OverviewSettingsWnd(Window):
    __guid__ = 'form.OverviewSettings'
    __notifyevents__ = ['OnOverviewPresetLoaded', 'OnOverviewTabsReconstructed', 'OnReloadingOverviewProfile']
    default_windowID = 'overviewsettings'
    default_captionLabelPath = 'UI/Overview/OverviewSettings'
    default_height = 600
    default_width = 520
    default_minSize = (520, 500)
    default_scope = uiconst.SCOPE_INFLIGHT

    def ApplyAttributes(self, attributes):
        super(OverviewSettingsWnd, self).ApplyAttributes(attributes)
        self.overviewPresetSvc = sm.GetService('overviewPresetSvc')
        presetName = attributes.get('presetName', None)
        self.topParent = Container(name='topParent', parent=self.sr.maincontainer, align=uiconst.TOTOP, height=52, clipChildren=True, idx=self.sr.main.GetOrder())
        self.AddDraggableCont()
        self.settingCheckboxes = []
        self.tabsPanel = TabsPanel(parent=self.sr.main)
        self.appearancePanel = AppearancePanel(parent=self.sr.main)
        self.shipsPanel = ShipsPanel(parent=self.sr.main)
        self.miscPanel = MiscPanel(parent=self.sr.main)
        self.tabPresetPanel = TabPresetPanel(parent=self.sr.main)
        self.columnsPanel = ColumnsPanel(parent=self.sr.main)
        self.historyPanel = HistoryPanel(parent=self.sr.main)
        self.Maximize()
        self.state = uiconst.UI_NORMAL
        settingsTabs = [[GetByLabel('UI/Overview/Tabs'),
          self.tabsPanel,
          self,
          oConst.TAB_TABS,
          None],
         [GetByLabel('UI/Overview/Filters'),
          self.tabPresetPanel,
          self,
          oConst.TAB_FILTERS,
          None],
         [GetByLabel('UI/Generic/Appearance'),
          self.appearancePanel,
          self,
          oConst.TAB_APPEARANCE,
          None],
         [GetByLabel('UI/Common/ItemTypes/Ships'),
          self.shipsPanel,
          self,
          oConst.TAB_SHIPS,
          None],
         [GetByLabel('UI/Generic/Misc'),
          self.miscPanel,
          self,
          oConst.TAB_MISC,
          None],
         [GetByLabel('UI/Overview/ProfileHistory'),
          self.historyPanel,
          self,
          oConst.TAB_HISTORY,
          None]]
        self.tabGroup = TabGroup(name='overviewsettingsTab', height=18, align=uiconst.TOTOP, parent=self.sr.main, idx=0, tabs=settingsTabs, groupID='overviewsettingsTab', UIIDPrefix='overviewSettingsTab', autoSelect=False)
        if presetName:
            self.EditPreset(presetName)
        else:
            self.tabGroup.AutoSelect()

    def EditPreset(self, presetName):
        self.tabGroup.SelectByID(oConst.TAB_FILTERS)
        self.tabPresetPanel.LoadPreset(presetName)

    def AddDraggableCont(self):
        currentText = self.overviewPresetSvc.GetOverviewName()
        defaultText = localization.GetByLabel('UI/Overview/DefaultOverviewName', charID=session.charid)
        configName = 'overviewProfileName'
        shareContainer = DraggableShareContainer(parent=self.topParent, currentText=currentText, defaultText=defaultText, configName=configName, getDragDataFunc=self.overviewPresetSvc.GetShareData, hintText=localization.GetByLabel('UI/Overview/SharableOverviewIconHint'))
        self.overviewNameEdit = shareContainer.sharedNameLabel
        self.topParent.height = self.overviewNameEdit.height + 10

    def RefreshOverviewName(self):
        currentText = self.overviewPresetSvc.GetOverviewName()
        self.overviewNameEdit.SetValue(currentText)
        self.overviewNameEdit.OnEditFieldChanged()

    def OnOverviewPresetLoaded(self, label, preset):
        self.tabsPanel.RefreshOverviewTab()

    def ExportSettings(self, *args):
        pass

    def GetMenuMoreOptions(self):
        menuData = super(OverviewSettingsWnd, self).GetMenuMoreOptions()
        menuData += self.GetPresetsMenu()
        return menuData

    def GetPresetsMenu(self):
        p = self.overviewPresetSvc.GetAllPresets().keys()
        p.sort()
        for name in self.overviewPresetSvc.GetDefaultOverviewPresetNames():
            if name in p:
                p.remove(name)

        m = []
        m += [None, (MenuLabel('UI/Commands/ExportOverviewSettings'), sm.GetService('tactical').ExportOverviewSettings), (MenuLabel('UI/Overview/ImportOverviewSettings'), sm.GetService('tactical').ImportOverviewSettings)]
        dm = []
        for label in p:
            if self.overviewPresetSvc.IsUnsavedPreset(label):
                continue
            dm.append((label.lower(), (label, self.overviewPresetSvc.DeletePreset, (label,))))

        if dm:
            m.append(None)
            dm = SortListOfTuples(dm)
            m.append((MenuLabel('UI/Common/Delete'), dm))
        return m

    def Load(self, key):
        if key == oConst.TAB_COLUMNS:
            self.columnsPanel.LoadColumns()
        elif key == oConst.TAB_APPEARANCE:
            self.appearancePanel.AutoSelectTab()
        elif key == oConst.TAB_SHIPS:
            self.shipsPanel.LoadShips()
        elif key in (oConst.TAB_MISC, oConst.TAB_TABS):
            pass
        elif key == oConst.TAB_HISTORY:
            self.historyPanel.LoadHistory()

    def OnOverviewTabsReconstructed(self):
        sm.GetService('bracket').UpdateLabels()
        self.tabsPanel.RefreshOverviewTab()

    def OnReloadingOverviewProfile(self):
        self.RefreshOverviewName()
        self.historyPanel.LoadHistory()
        self.tabGroup.AutoSelect()
