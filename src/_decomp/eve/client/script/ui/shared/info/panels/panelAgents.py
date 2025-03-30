#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelAgents.py
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.station.agents.agentUtil import AGENTS_IN_CORP_SHOW_INFO
from eve.common.lib import appConst as const
from eve.common.script.sys.rowset import Rowset

class PanelAgents(Container):
    default_name = 'PanelAgents'

    def ApplyAttributes(self, attributes):
        super(PanelAgents, self).ApplyAttributes(attributes)
        self.ownerID = attributes.ownerID
        self.typeID = attributes.typeID
        self.selectedLevel = attributes.get('selectedLevel', 1)
        self.isInitialized = False

    def Load(self):
        if self.isInitialized:
            return
        self.ConstructPanel()
        self.isInitialized = True

    def ConstructPanel(self):
        self.Flush()
        toggleButtonCont = Container(name='btnGroupCont', parent=self, align=uiconst.TOTOP, height=35)
        btnGroup = ToggleButtonGroup(parent=toggleButtonCont, align=uiconst.CENTER, height=toggleButtonCont.height, width=300, padding=(10, 4, 10, 3), callback=self.LoadAgentsOfLevel)
        for level in xrange(1, 6):
            isDisabled = not self.FilterAgents(self.GetAgentsOfLevel(level))
            hint = localization.GetByLabel('UI/Agents/NoAgentAvailableHint', level=level) if isDisabled else localization.GetByLabel('UI/Agents/AgentFilterButtonHint', level=level)
            btnGroup.AddButton(btnID=level, label=level, hint=hint, isDisabled=isDisabled)

        self.scroll = Scroll(name='scroll', parent=self, padding=const.defaultPadding)
        if self.FilterAgents(self.GetAgentsOfLevel(self.selectedLevel)):
            btnGroup.SelectByID(self.selectedLevel)
        else:
            btnGroup.SelectFirst()

    def LoadAgentsOfLevel(self, level, *args):
        scrollList = []
        filteredAgents = self.FilterAgents(self.GetAgentsOfLevel(level))
        sm.GetService('info').GetAgentScrollGroups(filteredAgents, scrollList)
        self.scroll.Load(contentList=scrollList)

    def GetAgentsOfLevel(self, level):
        self.agentsInCorp = sm.GetService('agents').GetAgentsByCorpID(self.ownerID).Clone()
        return self.agentsInCorp.Filter('level')[level]

    def FilterAgents(self, agents):
        agentCopy = agents[:]
        filteredAgents = Rowset(agentCopy.header)
        for agent in agentCopy:
            if agent.agentTypeID in AGENTS_IN_CORP_SHOW_INFO:
                filteredAgents.append(agent)

        return filteredAgents
