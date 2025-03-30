#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderAgents.py
from collections import defaultdict
import blue
import telemetry
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters
from eve.client.script.ui.shared.agencyNew.agencyConst import AGENT_STANDARDDIVISIONIDS, MAX_CONTENT_PIECES_MAX
from eve.client.script.ui.shared.agencyNew.agencyUtil import GetRoundRobinMix, GetUnlockedAgents
from eve.client.script.ui.shared.agencyNew.contentPieces.agentContentPiece import AgentContentPiece
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider
from eve.client.script.ui.station.agents import agentUtil
from eve.client.script.ui.station.agents.agentUtil import GetAgentDerivedStandingsSortedList
from eve.common.lib.appConst import corpDivisionHeraldry

class ContentProviderAgents(BaseContentProvider):
    __notifyevents__ = BaseContentProvider.__notifyevents__ + ['OnNPCStandingChange', 'OnAgentMissionChanged', 'OnHeraldryAvailabilityChanged']
    contentType = agencyConst.CONTENTTYPE_AGENTS

    def __init__(self):
        super(ContentProviderAgents, self).__init__()
        self.newAgents = []
        self._isHeraldryAvailable = None

    @telemetry.ZONE_METHOD
    def _ConstructContentPieces(self):
        allAgents = self._GetAllAgents()
        contentPieces = [ self.ConstructContentPiece(agent) for agent in allAgents ]
        self.ExtendContentPieces(contentPieces)

    @telemetry.ZONE_METHOD
    def CheckInactiveAgentCriteria(self, agent):
        if not self.CheckInactiveAgentGenericCriteria(agent):
            return False
        return self.CheckAgentsUserSelectedFilterCriteria(agent)

    @telemetry.ZONE_METHOD
    def CheckAgentsUserSelectedFilterCriteria(self, agent):
        return self.CheckFactionAndCorpFilterCriteria(agent) and self.CheckAgentLevelFilterCriteria(agent) and self.CheckShowOnlyAvailableCriteria(agent) and self.CheckDivisionFilterCriteria(agent) and self.CheckSecurityStatusFilterCriteria(agent.solarsystemID)

    def CheckShowOnlyAvailableCriteria(self, agent):
        if not agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_AGENTIGNORESTANDINGSREQUIREMENT):
            return self.CheckIsStandingSufficient(agent)
        return True

    @telemetry.ZONE_METHOD
    def CheckInactiveAgentGenericCriteria(self, agent):
        return self._CheckDivisionEnabled(agent) and self.CheckDivisionValidCriteria(agent) and self.CheckAgentTypeIDCriteria(agent) and self.CheckDistanceCriteria(solarSystemID=agent.solarsystemID)

    def CheckFactionAndCorpFilterCriteria(self, agent):
        factionID = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_AGENTFACTION)
        if factionID == agencyConst.FILTERVALUE_ANY:
            return True
        else:
            return agent.factionID == factionID and self.CheckCorpCriteria(agent)

    def CheckCorpCriteria(self, agent):
        corpID = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_AGENTCORP)
        if corpID == agencyConst.FILTERVALUE_ANY:
            return True
        else:
            return agent.corporationID == corpID

    def _CheckDivisionEnabled(self, agent):
        return agent.divisionID != corpDivisionHeraldry or self.IsHeraldryAvailable()

    def CheckDivisionValidCriteria(self, agent):
        return agent.divisionID in AGENT_STANDARDDIVISIONIDS

    def CheckAgentTypeIDCriteria(self, agent):
        return True

    def CheckDivisionFilterCriteria(self, agent):
        return True

    def IsHeraldryAvailable(self):
        if self._isHeraldryAvailable is None:
            self._isHeraldryAvailable = sm.GetService('agents').IsHeraldryAvailable()
        return self._isHeraldryAvailable

    def OnHeraldryAvailabilityChanged(self):
        self._isHeraldryAvailable = None
        agencyFilters.ResetFilter(self.contentGroup, agencyConst.FILTERTYPE_AGENTDIVISION)

    @telemetry.ZONE_METHOD
    def _GetAllAgents(self):
        agentBuckets = self.GetAgentsByBuckets()
        agentMix = GetRoundRobinMix(agentBuckets, numMax=MAX_CONTENT_PIECES_MAX)
        return list(agentMix)

    @telemetry.ZONE_METHOD
    def GetAgentsByBuckets(self):
        agents = self._GetAgentsWithinJumpRange()
        buckets = defaultdict(list)
        for agent in agents:
            blue.pyos.BeNice()
            if self.CheckInactiveAgentCriteria(agent):
                bucketKey = self._GetBucketKey(agent)
                buckets[bucketKey].append(agent)

        return self._GetAgentsByBucket(buckets)

    def _GetAgentsWithinJumpRange(self):
        solarSystemIDs = self.GetAllSolarSystemIDsWithinJumpRange(shouldIncludeAvoided=True)
        agentsBySolarSystemID = sm.GetService('agents').GetAgentsBySolarSystemID()
        ret = []
        for solarSystemID in solarSystemIDs:
            ret.extend(agentsBySolarSystemID.get(solarSystemID, []))

        return ret

    @telemetry.ZONE_METHOD
    def _GetAgentsByBucket(self, buckets):
        agentsByBuckets = [ iter(sorted(buckets[key], key=self._GetAgentSortKey, reverse=True)) for key in sorted(buckets.keys(), key=self._GetBucketSortKey) ]
        return agentsByBuckets

    def _GetBucketSortKey(self, sortKey):
        divisionID, isHighSec = sortKey
        if divisionID in AGENT_STANDARDDIVISIONIDS:
            divisionIndex = AGENT_STANDARDDIVISIONIDS.index(divisionID)
        else:
            divisionIndex = divisionID
        return (-isHighSec, divisionIndex)

    @telemetry.ZONE_METHOD
    def _GetBucketKey(self, agent):
        isHighSec = self.IsInHighSec(agent.solarsystemID)
        divisionID = agent.divisionID
        key = (divisionID, isHighSec)
        return key

    @telemetry.ZONE_METHOD
    def _GetAgentSortKey(self, agent):
        numJumps = self.GetNumJumpsToSystem(agent.solarsystemID)
        if numJumps is None:
            numJumps = 1000
        return (agent.level, -numJumps, GetAgentDerivedStandingsSortedList(agent.agentID))

    @telemetry.ZONE_METHOD
    def CheckAgentLevelFilterCriteria(self, agent):
        level = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_AGENTLEVEL)
        if level == agencyConst.FILTERVALUE_ANY:
            return True
        elif level == agencyConst.AGENTLEVEL_HIGHESTAVAILABLE:
            return self.CheckIsStandingSufficient(agent)
        else:
            return level == agent.level

    @telemetry.ZONE_METHOD
    def CheckIsStandingSufficient(self, agent):
        return agentUtil.IsAgentStandingSufficientToUse(agent)

    def ConstructContentPiece(self, agent):
        cls = self._GetContentPieceClass()
        isNewAgent = self.IsAgentNew(agent)
        contentPiece = cls(solarSystemID=agent.solarsystemID, itemID=agent.agentID, locationID=agent.stationID, typeID=agent.agentTypeID, ownerID=agent.corporationID, agent=agent, isNew=isNewAgent)
        return contentPiece

    def _GetContentPieceClass(self):
        return AgentContentPiece

    def OnNPCStandingChange(self, fromID, newStandingsValue, oldStandingsValue):
        unlockedAgents = GetUnlockedAgents(fromID, newStandingsValue, oldStandingsValue)
        if unlockedAgents:
            self.newAgents.extend([ agent.agentID for agent in unlockedAgents ])

    def IsAgentNew(self, agent):
        return agent.agentID in self.newAgents

    def ClearNewContent(self, contentPiece):
        agentID = contentPiece.agent.agentID
        if agentID in self.newAgents:
            self.newAgents.remove(agentID)

    def OnAgentMissionChanged(self, missionState, agentID):
        self.InvalidateContentPieces()
