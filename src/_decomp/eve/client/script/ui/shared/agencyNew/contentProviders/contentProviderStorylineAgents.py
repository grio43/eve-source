#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderStorylineAgents.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.agentContentPiece import AgentContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider
from eve.common.lib import appConst
from localization import GetByLabel

class ContentProviderStorylineAgents(BaseContentProvider):
    contentType = agencyConst.CONTENTTYPE_STORYLINEAGENTS
    contentGroup = contentGroupConst.contentGroupStorylineAgents
    __notifyevents__ = BaseContentProvider.__notifyevents__ + ['OnAgentMissionChanged']

    def __init__(self):
        super(ContentProviderStorylineAgents, self).__init__()
        sm.RegisterNotify(self)

    def _ConstructContentPieces(self):
        agents = self.GetActiveStorylineAgents()
        contentPieces = [ self.ConstructContentPiece(agent) for agent in agents ]
        self.ExtendContentPieces(contentPieces)

    def GetActiveStorylineAgents(self):
        missions = self.GetAllActiveMissions()
        agentSvc = sm.GetService('agents')
        agents = [ agentSvc.GetAgentByID(mission.agentID) for mission in missions ]
        return [ agent for agent in agents if self.CheckAgentTypeIDCriteria(agent) ]

    def GetAllActiveMissions(self):
        return sm.GetService('journal').GetActiveMissions()

    def CheckAgentTypeIDCriteria(self, agent):
        return agent.agentTypeID in (appConst.agentTypeStorylineMissionAgent, appConst.agentTypeGenericStorylineMissionAgent)

    def ConstructContentPiece(self, agent):
        contentPiece = AgentContentPiece(solarSystemID=agent.solarsystemID, itemID=agent.agentID, locationID=agent.stationID, typeID=agent.agentTypeID, ownerID=agent.corporationID, agent=agent)
        return contentPiece

    def OnAgentMissionChanged(self, missionState, agentID):
        self.InvalidateContentPieces()
        self._CheckBlinkNeocomButton(agentID, missionState)

    def _CheckBlinkNeocomButton(self, agentID, missionState):
        agent = sm.GetService('agents').GetAgentByID(agentID)
        if agent and self.CheckAgentTypeIDCriteria(agent):
            if missionState == appConst.agentMissionOffered:
                sm.GetService('neocom').Blink('agency', GetByLabel('UI/Neocom/Blink/NewStorylineMissionAvailable'))
