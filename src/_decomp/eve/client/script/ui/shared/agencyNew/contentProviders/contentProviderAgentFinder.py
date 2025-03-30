#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderAgentFinder.py
from eve.client.script.ui.shared.agencyNew import agencyFilters, agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentProviders.contentProviderAgents import ContentProviderAgents
from eve.common.lib import appConst

class ContentProviderAgentFinder(ContentProviderAgents):
    contentGroup = contentGroupConst.contentGroupAgentFinder

    def CheckDivisionFilterCriteria(self, agent):
        if agent.agentTypeID == appConst.agentTypeAura:
            return False
        filterValue = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_AGENTDIVISION)
        if filterValue == agencyConst.FILTERVALUE_ANY:
            return True
        elif filterValue == appConst.agentTypeCareerAgent:
            return agent.agentTypeID == appConst.agentTypeCareerAgent
        elif filterValue == appConst.agentTypeStorylineMissionAgent:
            return agent.agentTypeID in (appConst.agentTypeStorylineMissionAgent, appConst.agentTypeGenericStorylineMissionAgent)
        elif filterValue == appConst.agentTypeEpicArcAgent:
            return agent.agentTypeID == appConst.agentTypeEpicArcAgent
        elif filterValue == appConst.agentTypeFactionalWarfareAgent:
            return agent.agentTypeID == appConst.agentTypeFactionalWarfareAgent
        elif filterValue == appConst.agentTypeHeraldry:
            return agent.agentTypeID == appConst.agentTypeHeraldry
        else:
            return agent.divisionID == filterValue

    def CheckDivisionValidCriteria(self, agent):
        if agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_AGENTISLOCATOR):
            return agent.isLocatorAgent
        else:
            divisionID = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_AGENTDIVISION)
            if divisionID in (appConst.agentTypeCareerAgent, appConst.agentTypeFactionalWarfareAgent):
                return True
            return super(ContentProviderAgentFinder, self).CheckDivisionValidCriteria(agent)
