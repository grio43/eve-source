#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderHeraldryAgents.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.agencyFilters import GetFilterValue
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentProviders.contentProviderAgents import ContentProviderAgents
from eve.common.lib import appConst
import telemetry

class ContentProviderHeraldryAgents(ContentProviderAgents):
    contentType = agencyConst.CONTENTTYPE_HERALDRYAGENTS
    contentGroup = contentGroupConst.contentGroupMissionAgentsHeraldry

    def CheckDivisionValidCriteria(self, agent):
        return agent.divisionID == appConst.corpDivisionHeraldry

    def CheckAgentTypeIDCriteria(self, agent):
        return agent.agentTypeID == appConst.agentTypeHeraldry

    @telemetry.ZONE_METHOD
    def CheckDistanceCriteria(self, solarSystemID):
        if solarSystemID is None:
            return False
        distance = GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_DISTANCE)
        if distance == agencyConst.DISTANCE_ANY:
            return True
        elif distance == agencyConst.DISTANCE_REGION:
            return self.CheckRegionOrConstellationCriteria(solarSystemID)
        elif distance == agencyConst.DISTANCE_CURRSYSTEM:
            return solarSystemID == session.solarsystemid2
        numJumps = self.GetNumJumpsToSystem(solarSystemID)
        if numJumps is None:
            return False
        else:
            return numJumps <= distance

    def _GetAgentsWithinJumpRange(self):
        return sm.GetService('agents').GetAgentsByType(appConst.agentTypeHeraldry)
