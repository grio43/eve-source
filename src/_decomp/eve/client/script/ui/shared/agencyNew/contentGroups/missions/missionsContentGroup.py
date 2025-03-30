#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\missions\missionsContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.missions.agents.agentFinder import AgentFinderContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.missions.agents.careerAgents import CareerAgentsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.missions.agents.heraldryContentGroup import HeraldryContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.missions.agents.missionAgentsContentGroup import MissionAgentsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.missions.epicArcs import EpicArcsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.missions.agents.storylineAgentsContentGroup import StorylineAgentsContentGroup

class MissionsContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupMissions
    childrenGroups = [(contentGroupConst.contentGroupMissionAgentsHeraldry, HeraldryContentGroup),
     (contentGroupConst.contentGroupMissionAgents, MissionAgentsContentGroup),
     (contentGroupConst.contentGroupCareerAgents, CareerAgentsContentGroup),
     (contentGroupConst.contentGroupEpicArcs, EpicArcsContentGroup),
     (contentGroupConst.contentGroupStorylineAgents, StorylineAgentsContentGroup),
     (contentGroupConst.contentGroupAgentFinder, AgentFinderContentGroup)]

    @staticmethod
    def IsTabGroup():
        return True
