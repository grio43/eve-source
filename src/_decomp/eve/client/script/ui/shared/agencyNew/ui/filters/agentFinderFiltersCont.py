#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\filters\agentFinderFiltersCont.py
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters
from eve.client.script.ui.shared.agencyNew.ui.filters.agentsFiltersCont import AgentsFiltersCont
from eve.client.script.ui.shared.agencyNew.ui.controls.filterCombo import FilterCombo
from eve.common.lib import appConst
from localization import GetByLabel
from npcs.divisions import get_division_name

class AgentFinderFiltersCont(AgentsFiltersCont):
    default_name = 'AgentFinderFiltersCont'

    def ConstructFilters(self):
        self.agentDivisionCombo = FilterCombo(name='agentDivisionCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/AgentFinder/AgentType'), options=self.GetAgentDivisionOptions(), callback=self.OnAgentDivisionCombo, select=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTDIVISION))
        super(AgentFinderFiltersCont, self).ConstructFilters()
        checkBoxContainer = Container(name='checkBoxContainer', parent=self.filtersCont, align=uiconst.TOTOP, height=20, padTop=10)
        Checkbox(parent=checkBoxContainer, align=uiconst.CENTERRIGHT, checked=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTISLOCATOR), callback=self.OnLocatorAgentCheckbox)
        EveLabelMedium(parent=checkBoxContainer, align=uiconst.CENTERLEFT, text=GetByLabel('UI/AgentFinder/LocatorAgent'))

    def OnLocatorAgentCheckbox(self, checkbox):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTISLOCATOR, checkbox.GetValue())

    def GetAgentDivisionOptions(self):
        options = [(GetByLabel('UI/Agency/AnyType'), agencyConst.FILTERVALUE_ANY)]
        for divisionID in agencyConst.AGENT_STANDARDDIVISIONIDS:
            if divisionID == appConst.corpDivisionHeraldry:
                if sm.GetService('agents').IsHeraldryAvailable():
                    options.append([GetByLabel('UI/AgentFinder/HeraldryAgent'), appConst.agentTypeHeraldry])
            else:
                divisionName = get_division_name(divisionID).replace('&', '&amp;')
                options.append([divisionName, divisionID])

        options.append([GetByLabel('UI/Agency/ContentGroups/ContentGroupCareerAgents'), appConst.agentTypeCareerAgent])
        options.append([GetByLabel('UI/Agents/FactionalWarfare'), appConst.agentTypeFactionalWarfareAgent])
        options.append([GetByLabel('UI/Agents/MissionTypes/Storyline'), appConst.agentTypeStorylineMissionAgent])
        options.append([GetByLabel('UI/Agents/MissionTypes/EpicArc'), appConst.agentTypeEpicArcAgent])
        return options

    def OnAgentDivisionCombo(self, comboBox, key, value):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTDIVISION, value)
