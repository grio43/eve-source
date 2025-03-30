#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelAgentMissions.py
from eve.client.script.ui.shared.infoPanels.const.infoPanelConst import PANEL_MISSIONS
from eve.client.script.ui.shared.infoPanels.infoPanelMissions import InfoPanelMissions, InfoPanelMissionData
from functools import partial
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_AGENT_MISSION_INFO_PANEL
from localization import GetByLabel, GetByMessageID
from missions.client.ui.missionObjectiveData import CreateObjective, TalkToAgent, ReadDetails, START_CONVERSATION_LABEL_PATH, START_CONVERSATION_ICON_PATH, READ_DETAILS_LABEL_PATH, READ_DETAILS_ICON_PATH
from jobboard.client import get_job_board_service
from jobboard.client.provider_type import ProviderType
from uthread2 import StartTasklet

class InfoPanelAgentMissionData(InfoPanelMissionData):

    def __init__(self, title, agentID, contentID, bookmarks, objectiveChain):
        self.agentID = agentID
        self.contentID = contentID
        self.bookmarks = bookmarks
        self.missionObjectivesTracker = sm.GetService('missionObjectivesTracker')
        self.objectiveChain = objectiveChain
        super(InfoPanelAgentMissionData, self).__init__(title)

    def _InitializeObjectives(self):
        self.objectives = []
        isCurrentObjective = False
        objectives = []
        currentObjective = self.missionObjectivesTracker.GetCurrentAgentMissionInfo(self.agentID)
        for index, objectiveData in enumerate(self.missionObjectivesTracker.GetAllAgentMissionInfo(self.agentID)):
            objective = CreateObjective(objectiveData, self.agentID, self.bookmarks, self.title)
            isCurrentObjective = self._IsCurrentObjective(objectiveData, currentObjective)
            objectives.append(objective)
            if isCurrentObjective:
                objective.SetActive()
                break

        if not isCurrentObjective:
            return
        self.objectives.extend(objectives)

    def _IsCurrentObjective(self, objective, currentObjective):
        objectiveStringList = [ str(item) for item in objective ] if objective else ['']
        return objectiveStringList == currentObjective

    def GetID(self):
        return self.agentID

    def GetContextMenu(self):
        from evemissions.client.qa_tools import get_agent_mission_context_menu
        result = get_agent_mission_context_menu(self.contentID, self.agentID)
        return result

    def GetStateColor(self):
        activeMission = sm.GetService('missionObjectivesTracker').agentMissions.get(self.agentID)
        if activeMission and activeMission.are_objectives_complete:
            return eveColor.SUCCESS_GREEN


class InfoPanelAgentMissions(InfoPanelMissions):
    default_name = 'InfoPanelAgentMissions'
    uniqueUiName = UNIQUE_NAME_AGENT_MISSION_INFO_PANEL
    panelTypeID = PANEL_MISSIONS
    label = 'UI/PeopleAndPlaces/AgentMissions'
    default_iconTexturePath = 'res:/UI/Texture/Classes/InfoPanels/Missions.png'
    featureID = 'agent_mission'

    def ApplyAttributes(self, attributes):
        InfoPanelMissions.ApplyAttributes(self, attributes)
        self.missionObjectivesTracker = sm.GetService('missionObjectivesTracker')

    @staticmethod
    def IsAvailable():
        service = get_job_board_service()
        if service.is_available:
            provider = service.get_provider(ProviderType.AGENT_MISSIONS)
            if provider.is_enabled:
                return False
        return bool(sm.GetService('missionObjectivesTracker').GetAgentMissions())

    def ConstructNormal(self):
        super(InfoPanelAgentMissions, self).ConstructNormal()

    def GetMissions(self):
        missions = []
        for mission in self.missionObjectivesTracker.GetAgentMissions():
            missionName = self._GetAgentMissionName(mission.missionNameID)
            objectiveChain = self.missionObjectivesTracker.agentMissions[mission.agentID].objective_chain
            missionData = InfoPanelAgentMissionData(missionName, mission.agentID, mission.contentID, mission.bookmarks, objectiveChain)
            missions.append(missionData)

        return missions

    def _GetAgentMissionName(self, missionNameID):
        if isinstance(missionNameID, (int, long)):
            return GetByMessageID(missionNameID)
        return missionNameID

    def HasOptionsMenu(self):
        return True

    def GetOptionsMenu(self, menuParent, mission):
        menuParent.AddIconEntry(icon=READ_DETAILS_ICON_PATH, text=GetByLabel(READ_DETAILS_LABEL_PATH), callback=partial(ReadDetails, mission.agentID), name='utilmenu_MissionReadDetails')
        menuParent.AddIconEntry(icon=START_CONVERSATION_ICON_PATH, text=GetByLabel(START_CONVERSATION_LABEL_PATH), callback=partial(TalkToAgent, mission.agentID), name='utilmenu_MissionStartConversation')

    def UpdateExpandedStateForMissionID(self, agentID):
        expandedMissionIndex = self.GetIndexForMissionID(agentID)
        if self.expandedMissionIndex != expandedMissionIndex:
            self.UpdateExpandedStateForMission(expandedMissionIndex)
            if expandedMissionIndex is not None and self.scrollContainer and not self.scrollContainer.destroyed:
                StartTasklet(self.ScrollToMission, expandedMissionIndex)

    def GetMissionIDForIndex(self, index):
        try:
            return self.missions[index].agentID
        except:
            return -1

    def GetIndexForMissionID(self, agentID):
        if agentID is not None:
            for missionIndex, mission in enumerate(self.missions):
                if mission.agentID == agentID:
                    return missionIndex

    def GetDefaultExpandedMissionIndex(self):
        expandedMissionAgentID = self.missionObjectivesTracker.GetAgentForLastAcceptedMission()
        return self.GetIndexForMissionID(expandedMissionAgentID)
