#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\agentContentPiece.py
from carbonui.util.bunch import Bunch
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.agencyConst import AGENT_STANDARDDIVISIONIDS
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.comtool.constants import CHANNEL_MISSIONS
from eve.client.script.ui.station.agents import agentUtil
from eve.client.script.ui.station.agents.agentUtil import GetAgentStandingThreshold, GetAgentDerivedStanding
from eve.common.lib import appConst
from localization import GetByLabel
from npcs.divisions import get_division_name

class AgentContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_AGENTS

    def __init__(self, agent = None, *args, **kwargs):
        BaseContentPiece.__init__(self, *args, **kwargs)
        self.agent = agent

    def GetTitle(self):
        activeMission = self.GetActiveMissionForAgent()
        if activeMission:
            return '%s: %s' % (self.GetAgentTypeName(), activeMission.GetMissionTypeText())
        else:
            return self.GetAgentTypeName()

    def GetExpandedTitle(self):
        return self.GetAgentNameAndLevel()

    def GetAgentID(self):
        return self.agent.agentID

    def GetDivisionName(self):
        return get_division_name(self.GetDivisionID())

    def GetDivisionID(self):
        return self.agent.divisionID

    def GetAgentTypeName(self):
        return GetByLabel('UI/Agency/AgentTypeName', divisionName=self.GetDivisionName())

    def GetActiveMissionForAgent(self):
        return sm.GetService('journal').GetActiveMissionForAgent(self.agent.agentID)

    def IsActiveAndAcceptedMission(self):
        activeMission = self.GetActiveMissionForAgent()
        if activeMission:
            return activeMission.IsMissionAccepted()
        else:
            return False

    def GetSubtitle(self):
        return self.GetAgentNameAndLevel()

    def GetAgentName(self):
        return cfg.eveowners.Get(self.GetAgentID()).ownerName

    def GetAgentCorpName(self):
        return cfg.eveowners.Get(self.GetCorpID()).ownerName

    def GetAgentNameAndLevel(self):
        return GetByLabel('UI/Agents/AgentNameAndLevel', charid=self.GetAgentID(), level=self.GetAgentLevel())

    def GetAgentLevel(self):
        return self.agent.level

    def GetAgentDivisionAndLevel(self):
        return '%s - %s' % (self.GetDivisionName(), GetByLabel('UI/Agents/AgentEntry/Level', level=self.GetAgentLevel()))

    def GetExpandedSubtitle(self):
        return self.GetAgentTypeName()

    def GetExpiryTimeText(self):
        activeMission = self.GetActiveMissionForAgent()
        if activeMission:
            return '%s %s' % (activeMission.GetMissionStateTextColored(), activeMission.GetExpiryTimeText(short=True))

    def IsActiveMissionExpired(self):
        activeMission = self.GetActiveMissionForAgent()
        if activeMission:
            return activeMission.IsExpired()

    def GetTimeRemaining(self):
        activeMission = self.GetActiveMissionForAgent()
        if activeMission:
            return activeMission.GetTimeRemaining()

    def GetCardSortValue(self):
        systemSec = self.GetSystemSecurityStatus()
        return (self._GetActiveMissionSortKey(),
         self._GetDivisionSortKey(),
         self.GetJumpsToSelfFromCurrentLocation(),
         -systemSec)

    def _GetDivisionSortKey(self):
        if self.IsStorylineAgent():
            return -1
        return AGENT_STANDARDDIVISIONIDS.index(self.GetDivisionID())

    def IsStorylineAgent(self):
        return self.agent.agentTypeID in (appConst.agentTypeStorylineMissionAgent, appConst.agentTypeGenericStorylineMissionAgent)

    def IsCareerAgent(self):
        return False

    def IsLocatorAgent(self):
        return self.agent.isLocatorAgent

    def _GetActiveMissionSortKey(self):
        activeMission = self.GetActiveMissionForAgent()
        if activeMission:
            return activeMission.GetActiveMissionSortKey()
        else:
            return 10000000000.0

    def _GetButtonState(self):
        if self.IsInCurrentStation() or not self.IsAvailable():
            return agencyUIConst.ACTION_STARTCONVERSATION
        else:
            return super(AgentContentPiece, self)._GetButtonState()

    def _ExecutePrimaryFunction(self, actionID):
        if actionID == agencyUIConst.ACTION_STARTCONVERSATION:
            self.ExecuteStartConversation()
        else:
            BaseContentPiece._ExecutePrimaryFunction(self, actionID)

    def ExecuteStartConversation(self):
        sm.GetService('agents').OpenDialogueWindow(self.itemID)

    def _GetButtonLabel(self, buttonState):
        if buttonState == agencyUIConst.ACTION_STARTCONVERSATION:
            return GetByLabel('UI/Chat/StartConversationAgent')
        else:
            return BaseContentPiece._GetButtonLabel(self, buttonState)

    def GetMenu(self):
        agentID = self.GetDestinationAgentID()
        return sm.GetService('menu').CharacterMenu(agentID)

    def GetBlurbText(self):
        if self.IsStorylineAgent():
            return GetByLabel('UI/Agency/Blurbs/StorylineAgent')
        if self.agent.divisionID == appConst.corpDivisionSecurity:
            return GetByLabel('UI/Agency/Blurbs/SecurityAgent')
        if self.agent.divisionID == appConst.corpDivisionMining:
            return GetByLabel('UI/Agency/Blurbs/MiningAgent')
        if self.agent.divisionID == appConst.a:
            return GetByLabel('UI/Agency/Blurbs/DistributionAgent')

    def GetActivityBadgeTexturePath(self):
        if self.IsStorylineAgent():
            return 'res:/UI/Texture/classes/agency/ActivityBadges/badge_storylineMissions.png'
        if self.IsCareerAgent():
            return 'res:/UI/Texture/classes/agency/ActivityBadges/badge_careerAgents.png'
        if self.agent.agentTypeID == appConst.agentTypeResearchAgent:
            return 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsResearch.png'
        if self.agent.divisionID == appConst.corpDivisionSecurity:
            return 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsSecurity.png'
        if self.agent.divisionID == appConst.corpDivisionMining:
            return 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsMining.png'
        if self.agent.divisionID == appConst.corpDivisionDistribution:
            return 'res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsDistribution.png'

    def GetEnemyOwnerID(self):
        activeMission = self.GetActiveMissionForAgent()
        if not activeMission:
            return None
        return activeMission.GetEnemyFactionID()

    def GetRewardTypes(self):
        agentType = self.agent.agentTypeID
        iskReward = self._GetIskRewardType()
        if agentType == appConst.corpDivisionSecurity:
            return [iskReward, agencyConst.REWARDTYPE_LP1, agencyConst.REWARDTYPE_LOOT]
        else:
            return [iskReward, agencyConst.REWARDTYPE_LP1]

    def _GetIskRewardType(self):
        level = self.GetAgentLevel()
        if level < 2:
            return agencyConst.REWARDTYPE_ISK1
        elif level < 4:
            return agencyConst.REWARDTYPE_ISK2
        else:
            return agencyConst.REWARDTYPE_ISK3

    def IsAvailable(self):
        return agentUtil.IsAgentAvailable(self.GetAgentID())

    def GetStanding(self):
        return GetAgentDerivedStanding(self.GetAgentID())[0]

    def GetRequiredStanding(self):
        return GetAgentStandingThreshold(self.GetAgentLevel())

    def GetBGVideoPath(self):
        if self.IsStorylineAgent():
            return 'res:/Video/Agency/agentStoryline.webm'
        if self.agent.divisionID == appConst.corpDivisionSecurity:
            return 'res:/Video/Agency/agentSecurity.webm'
        if self.agent.divisionID == appConst.corpDivisionMining:
            return 'res:/Video/Agency/agentMining.webm'
        if self.agent.divisionID == appConst.corpDivisionDistribution:
            return 'res:/Video/Agency/agentDistribution.webm'

    def GetAllowedShipTypeIDs(self):
        activeMission = self.GetActiveMissionForAgent()
        if activeMission:
            return activeMission.GetAllowedShipTypeIDs()

    def IsShipRestrictionShown(self):
        activeMission = self.GetActiveMissionForAgent()
        if activeMission:
            if not activeMission.IsShipRestrictionInteresting():
                return False
        return BaseContentPiece.IsShipRestrictionShown(self)

    def GetContentSubTypeID(self):
        return self.GetDivisionID()

    def GetDragData(self):
        agentID = self.GetAgentID()
        dragData = Bunch()
        dragData.__guid__ = 'listentry.User'
        dragData.itemID = agentID
        dragData.charID = agentID
        dragData.info = Bunch(typeID=appConst.typeCharacter, name=cfg.eveowners.Get(agentID).name)
        return [dragData]

    def GetDestinationAgentID(self):
        mission = self.GetActiveMissionForAgent()
        if mission:
            return mission.GetDestinationAgentID()
        else:
            return self.GetAgentID()

    def GetDestinationSolarSystemID(self):
        destAgent = self.GetDestinationAgent()
        return destAgent.solarsystemID

    def GetDestinationAgent(self):
        destAgentID = self.GetDestinationAgentID()
        destinationAgent = sm.GetService('agents').GetAgentByID(destAgentID)
        return destinationAgent

    def GetStationID(self):
        destAgent = self.GetDestinationAgent()
        if destAgent:
            return destAgent.stationID

    def IsInCurrentSolarSystem(self):
        destAgent = self.GetDestinationAgent()
        return destAgent.solarsystemID == session.solarsystemid2

    def _ExecuteWarpTo(self):
        stationID = self.GetStationID()
        if stationID:
            WarpToItem(stationID)
        else:
            sm.GetService('agents').GetAgentMoniker(self.GetDestinationAgentID()).WarpToAgentInSpace()

    def GetChatChannelID(self):
        return CHANNEL_MISSIONS
