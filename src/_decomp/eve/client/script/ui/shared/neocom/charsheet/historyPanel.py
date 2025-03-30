#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\historyPanel.py
from carbonui.primitives.container import Container
from carbonui.control.tabGroup import TabGroup
import carbonui.const as uiconst
from eve.client.script.ui.shared.neocom.charsheet import GetPanelName, PANEL_EMPLOYMENT, PANEL_SKILLS_HISTORY
from eve.client.script.ui.shared.neocom.charsheet.employmentHistoryPanel import EmploymentHistoryPanel
from eve.client.script.ui.shared.neocom.charsheet.skillHistoryPanel import SkillHistoryPanel

class HistoryPanel(Container):
    default_name = 'HistoryPanel'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isConstructed = False

    def ConstructLayout(self):
        if self.isConstructed:
            return
        self.isConstructed = True
        self.panelCont = Container(name='panelCont', parent=self, align=uiconst.TOALL, padTop=8)
        self.employmentHistoryPanel = EmploymentHistoryPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.skillHistoryPanel = SkillHistoryPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.tabs = TabGroup(parent=self, align=uiconst.TOTOP, padding=0, groupID='HistoryPanelTabs', autoselecttab=False, idx=0, tabs=((GetPanelName(PANEL_EMPLOYMENT),
          self.employmentHistoryPanel,
          self,
          PANEL_EMPLOYMENT), (GetPanelName(PANEL_SKILLS_HISTORY),
          self.skillHistoryPanel,
          self,
          PANEL_SKILLS_HISTORY)))

    def LoadPanel(self, panelID = None):
        self.ConstructLayout()
        if panelID:
            self.tabs.SelectByID(panelID)
        else:
            self.tabs.AutoSelect()

    def LoadSubPanel(self, panelID):
        self.ConstructLayout()
        self.tabs.SelectByID(panelID)

    def GetActivePanelID(self):
        return self.tabs.GetSelectedID()
