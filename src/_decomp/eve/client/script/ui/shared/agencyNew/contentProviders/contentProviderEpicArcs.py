#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderEpicArcs.py
from carbon.common.lib import telemetry
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyUtil, agencyFilters
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentPieces.epicArcAgentContentPiece import EpicArcAgentContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider
from eve.client.script.ui.station.agents.agentUtil import IsAgentStandingSufficientToUse

class ContentProviderEpicArcs(BaseContentProvider):
    __notifyevents__ = BaseContentProvider.__notifyevents__ + ['OnAgentMissionChanged', 'OnEpicArcDataChanged']
    contentType = agencyConst.CONTENTTYPE_EPICARCS
    contentGroup = contentGroupConst.contentGroupEpicArcs
    contentTypeFilters = (agencyConst.CONTENTTYPE_SUGGESTED, agencyConst.CONTENTTYPE_COMBAT, agencyConst.CONTENTTYPE_EPICARCS)

    def OnAgentMissionChanged(self, missionState, agentID):
        self.InvalidateContentPieces()

    def OnEpicArcDataChanged(self):
        self.InvalidateContentPieces()

    @telemetry.ZONE_METHOD
    def _ConstructContentPieces(self):
        epicArcs = self.GetAllEpicArcs()
        contentPieces = [ self._ConstructContentPiece(epicArc) for epicArc in epicArcs ]
        self.contentPieces = sorted(contentPieces, key=self._GetSortKey)

    def _ConstructContentPiece(self, epicArc):
        agent = epicArc.GetActiveAgent()
        contentPiece = EpicArcAgentContentPiece(agent=agent, epicArc=epicArc, ownerID=epicArc.GetFactionID(), solarSystemID=agent.solarsystemID, itemID=agent.agentID, locationID=agent.stationID, typeID=agent.agentTypeID)
        return contentPiece

    def _GetSortKey(self, contentPiece):
        return (contentPiece.epicArc.GetState(), contentPiece.GetJumpsToSelfFromCurrentLocation())

    def GetBestEpicArcAgent(self, epicArc):
        missions = epicArc.GetActiveMissions()
        if not missions:
            return self.GetAgent(epicArc.startNodes[0].agentID)
        agents = [ self.GetAgent(mission.agentID) for mission in missions ]
        agents = sorted(agents, key=self._GetAgentSortKey)
        return agents[0]

    def GetAgent(self, agentID):
        return sm.GetService('agents').GetAgentByID(agentID)

    @telemetry.ZONE_METHOD
    def _GetAgentSortKey(self, agent):
        return (-int(IsAgentStandingSufficientToUse(agent)), self.GetNumJumpsToSystem(agent.solarsystemID))

    def GetAllEpicArcs(self):
        return sm.GetService('epicArc').GetEpicArcs()
