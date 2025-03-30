#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderCareerAgents.py
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.careerAgentContentPiece import CareerAgentContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider

class ContentProviderCareerAgents(BaseContentProvider):
    contentType = agencyConst.CONTENTTYPE_CAREERAGENTS
    contentGroup = contentGroupConst.contentGroupCareerAgents

    def _ConstructContentPieces(self):
        allAgents = self.GetSuggestedAgents()
        contentPieces = [ self.ConstructContentPiece(agent) for agent in allAgents ]
        contentPieces = [ contentPiece for contentPiece in contentPieces if self.CheckDistanceCriteria(contentPiece.solarSystemID) ]
        contentPieces = sorted(contentPieces, key=self._GetSortKey)
        self.ExtendContentPieces(contentPieces)

    def _GetSortKey(self, contentPiece):
        return contentPiece.GetCardSortValue()

    def ConstructContentPiece(self, agent):
        contentPiece = CareerAgentContentPiece(solarSystemID=agent.solarsystemID, itemID=agent.agentID, locationID=agent.stationID, typeID=agent.agentTypeID, ownerID=agent.corporationID, agent=agent)
        return contentPiece

    def GetSuggestedAgents(self):
        agents = sm.GetService('agents').GetMySuggestedCareerAgents()
        agents = self.GetAgentsWithAvailableMissions(agents)
        return agents

    def GetAgentsWithAvailableMissions(self, agents):
        self._PrimeCompletedAgents(agents)
        return agents

    def _PrimeCompletedAgents(self, agents):
        agentIDs = [ agent.agentID for agent in agents ]
        sm.GetService('agents').CheckPrimeCompletedCareerAgentIDs(agentIDs)

    def IsAgentCompleted(self, agentID):
        return sm.GetService('agents').IsCareerAgentCompleted(agentID)

    def _GetActiveAgents(self):
        return []

    def ApplyDefaultFilters(self):
        agencyFilters.SetFilterValueWithoutEvent(self.contentGroup, agencyConst.FILTERTYPE_DISTANCE, agencyConst.DISTANCE_ANY)
