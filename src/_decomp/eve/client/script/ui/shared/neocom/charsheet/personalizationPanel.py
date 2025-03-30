#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\personalizationPanel.py
from carbonui.primitives.container import Container
from carbonui.control.tabGroup import TabGroup, GetTabData
import carbonui.const as uiconst
from eve.client.script.ui.shared.neocom.charsheet import GetPanelName, GetPanelDescription, PANEL_SHIPSKINS, PANEL_SHIPEMBLEMS, GetPanelUniqueName
from eve.client.script.ui.shared.neocom.charsheet.emblemsPanel import EmblemsPanel
from eve.client.script.ui.shared.neocom.charsheet.skinsPanel import SkinsPanel

class PersonalizationPanel(Container):
    default_name = 'PersonalizationPanel'
    default_padTop = 6

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self._emblemsErrorScreenPadding = attributes.emblemsErrorScreenPadding
        self.isConstructed = False

    def ConstructLayout(self):
        if self.isConstructed:
            return
        self.isConstructed = True
        self.panelCont = Container(name='panelCont', parent=self, align=uiconst.TOALL)
        self.skinsPanel = SkinsPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.emblemsPanel = EmblemsPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN, errorScreenPadding=self._emblemsErrorScreenPadding)
        self.tabs = TabGroup(parent=self, align=uiconst.TOTOP, padding=0, groupID='PersonalizationPanelTabs', idx=0, autoselecttab=False, tabs=self.GetTabs())

    def GetTabs(self):
        return (self.GetTabEntry(self.skinsPanel, PANEL_SHIPSKINS), self.GetTabEntry(self.emblemsPanel, PANEL_SHIPEMBLEMS))

    def GetTabEntry(self, panel, panelID):
        return GetTabData(label=GetPanelName(panelID), panel=panel, code=self, tabID=panelID, hint=GetPanelDescription(panelID), uniqueName=GetPanelUniqueName(panelID))

    def LoadPanel(self):
        self.ConstructLayout()
        self.tabs.AutoSelect()

    def LoadSubPanel(self, panelID):
        if self.isConstructed and self.tabs.GetSelectedID() == panelID:
            return
        self.ConstructLayout()
        self.tabs.SelectByID(panelID)

    def GetActivePanelID(self):
        return self.tabs.GetSelectedID()
