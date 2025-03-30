#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\missions\agents\missionAgentsContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.missions.agents.distributionAgents import DistributionAgentsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.missions.agents.locatorAgents import LocatorAgentsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.missions.agents.miningAgents import MiningAgentsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.missions.agents.researchAgents import ResearchAgentsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.missions.agents.securityAgents import SecurityAgentsContentGroup

class MissionAgentsContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupMissionAgents
    childrenGroups = [(contentGroupConst.contentGroupMissionAgentsSecurity, SecurityAgentsContentGroup),
     (contentGroupConst.contentGroupMissionAgentsDistribution, DistributionAgentsContentGroup),
     (contentGroupConst.contentGroupMissionAgentsMining, MiningAgentsContentGroup),
     (contentGroupConst.contentGroupMissionAgentsResearch, ResearchAgentsContentGroup),
     (contentGroupConst.contentGroupMissionAgentsLocator, LocatorAgentsContentGroup)]
