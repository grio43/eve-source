#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\interactionsPanel.py
from carbonui.primitives.container import Container
from carbonui.control.tabGroup import TabGroup, GetTabData
import carbonui.const as uiconst
from eve.client.script.ui.shared.neocom.charsheet import GetPanelDescription, GetPanelName, PANEL_COMBATLOG, PANEL_KILLRIGHTS, PANEL_SECURITYSTATUS, PANEL_STANDINGS, GetPanelUniqueName
from eve.client.script.ui.shared.neocom.charsheet.combatLogPanel import CombatLogPanel
from eve.client.script.ui.shared.neocom.charsheet.killRightsPanel import KillRightsPanel
from eve.client.script.ui.shared.neocom.charsheet.securityStatusPanel import SecurityStatusPanel
from eve.client.script.ui.shared.neocom.charsheet.standingsPanel.standingsPanel import StandingsPanel

class InteractionsPanel(Container):
    default_name = 'InteractionsPanel'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isConstructed = False

    def ConstructLayout(self):
        if self.isConstructed:
            return
        self.isConstructed = True
        self.panelCont = Container(name='panelCont', parent=self, align=uiconst.TOALL)
        self.killRightsPanel = KillRightsPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.standingsPanel = StandingsPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN, toID=session.charid, padTop=8)
        self.securityStatusPanel = SecurityStatusPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.combatLogPanel = CombatLogPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.tabs = TabGroup(parent=self, align=uiconst.TOTOP, padding=0, groupID='InteractionsPanelTabs', idx=0, autoselecttab=False, tabs=self.GetTabs())

    def GetTabs(self):
        return (self.GetTabEntry(self.standingsPanel, PANEL_STANDINGS),
         self.GetTabEntry(self.killRightsPanel, PANEL_KILLRIGHTS),
         self.GetTabEntry(self.securityStatusPanel, PANEL_SECURITYSTATUS),
         self.GetTabEntry(self.combatLogPanel, PANEL_COMBATLOG))

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
