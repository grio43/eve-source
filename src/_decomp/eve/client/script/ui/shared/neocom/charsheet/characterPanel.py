#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\characterPanel.py
import expertSystems.client
import homestation.client
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.control.tabGroup import TabGroup, GetTabData
from eve.client.script.ui.shared.neocom.charsheet import GetPanelName, PANEL_IMPLANTSBOOTERS, PANEL_JUMPCLONES, PANEL_ATTRIBUTES, PANEL_BIO, PANEL_DECORATIONS, GetPanelDescription, PANEL_EXPERTSYSTEMS, PANEL_HOME_STATION, GetPanelUniqueName
from eve.client.script.ui.shared.neocom.charsheet.attributesPanel import AttributesPanel
from eve.client.script.ui.shared.neocom.charsheet.bioPanel import BioPanel
from eve.client.script.ui.shared.neocom.charsheet.decorationsPanel import DecorationsPanel
from eve.client.script.ui.shared.neocom.charsheet.implantsBoostersPanel import ImplantsBoostersPanel
from eve.client.script.ui.shared.neocom.charsheet.jumpClonesPanel import JumpClonesPanel

class CharacterPanel(Container):
    default_name = 'CharacterPanel'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isConstructed = False

    def ConstructLayout(self):
        if self.isConstructed:
            return
        self.isConstructed = True
        self.panelCont = Container(name='panelCont', parent=self, align=uiconst.TOALL, padTop=8)
        self.jumpClonesPanel = JumpClonesPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.attributesPanel = AttributesPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.decorationsPanel = DecorationsPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.bioPanel = BioPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.implantsBoostersPanel = ImplantsBoostersPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.expertSystemsPanel = expertSystems.ExpertSystemsPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.homeStationPanel = homestation.HomeStationPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        tabs = []
        tabs.append(self.GetTabEntry(self.homeStationPanel, PANEL_HOME_STATION))
        tabs.append(self.GetTabEntry(self.implantsBoostersPanel, PANEL_IMPLANTSBOOTERS))
        tabs.append(self.GetTabEntry(self.jumpClonesPanel, PANEL_JUMPCLONES))
        tabs.append(self.GetTabEntry(self.attributesPanel, PANEL_ATTRIBUTES))
        tabs.append(self.GetTabEntry(self.bioPanel, PANEL_BIO))
        tabs.append(self.GetTabEntry(self.decorationsPanel, PANEL_DECORATIONS))
        if expertSystems.is_expert_systems_enabled():
            tabs.append(self.GetTabEntry(self.expertSystemsPanel, PANEL_EXPERTSYSTEMS))
        self.tabs = TabGroup(parent=self, align=uiconst.TOTOP, padding=0, groupID='CharacterPanelTabs', autoselecttab=False, idx=0, tabs=tabs)

    def LoadPanel(self):
        self.ConstructLayout()
        self.tabs.AutoSelect()

    def UnloadPanel(self):
        if not self.isConstructed:
            return
        panel = self.tabs.GetSelectedPanel()
        if hasattr(panel, 'UnloadPanel'):
            panel.UnloadPanel()

    def LoadSubPanel(self, panelID):
        self.ConstructLayout()
        self.tabs.SelectByID(panelID)

    def GetTabEntry(self, panel, panelID):
        return GetTabData(label=GetPanelName(panelID), panel=panel, code=self, tabID=panelID, hint=GetPanelDescription(panelID), uniqueName=GetPanelUniqueName(panelID))

    def GetActivePanelID(self):
        return self.tabs.GetSelectedID()
