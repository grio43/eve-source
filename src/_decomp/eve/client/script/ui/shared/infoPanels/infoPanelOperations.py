#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelOperations.py
import carbonui.const as uiconst
from achievements.common.achievementConst import AchievementEventConst
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.shared.infoPanels.const.infoPanelConst import PANEL_OPERATIONS, MODE_HIDDEN
from eve.client.script.ui.shared.infoPanels.infoPanelMissions import InfoPanelMissions, InfoPanelMissionData
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_TUTORIAL_INFO_PANEL
from localization import GetByLabel, GetByMessageID
from operations.client.UI import taskObjectiveData
from operations.client.operationscontroller import GetOperationsController
from operations.client.tutorialOperationsController import GetTutorialOperationsController
from operations.client.util import are_operations_active
from storylines.client.airnpe import skip_air_npe
from uihider import UiHiderMixin
import logging
logger = logging.getLogger(__name__)
CLOSE_ICON_SIZE = 12
MINIMIZE_ICON_TEXTURE = 'res:/UI/Texture/icons/38_16_221.png'
CLOSE_ICON_TEXTURE = 'res:/UI/Texture/classes/InfoPanels/quitOperation_Icon.png'
MINIMIZE_LABEL = 'UI/Common/Collapse'
SKIP_TUTORIAL_LABEL = 'UI/Operations/InfoPanel/SkipTutorialOption'
SKIP_TUTORIAL_HINT_LABEL = 'UI/Operations/InfoPanel/SkipTutorialOptionHint'
SKIP_TUTORIAL_WARNING_DIALOG_ID = 'SkipTutorialWarning'
QUIT_OPERATION_LABEL = 'UI/Operations/InfoPanel/QuitOperationOption'
QUIT_OPERATION_HINT_LABEL = 'UI/Operations/InfoPanel/QuitOperationOptionHint'
CATEGORIES_THAT_SHOW_PAST_OBJECTIVES = []

def GetOperationsTitle():
    tutorialOperationsController = GetTutorialOperationsController()
    if tutorialOperationsController.is_tutorial_active():
        return GetByLabel('UI/Agents/AuraAgentName')
    return GetByLabel('UI/Operations/InfoPanel/InfoPanelTitle')


class InfoPanelOperationData(InfoPanelMissionData):

    def __init__(self, categoryID = None, operation = None, activeTasks = None):
        self.categoryID = categoryID or GetOperationsController().get_active_category_id()
        self.operation = operation or GetOperationsController().get_active_operation()
        self.activeTasks = activeTasks or GetOperationsController().get_active_task_tuples()
        operationTitle = GetByMessageID(self.operation.title)
        super(InfoPanelOperationData, self).__init__(title=operationTitle)

    def _InitializeObjectives(self):
        self.objectives = []
        objectives = []
        isCurrentObjective = False
        for task in self.operation.taskList:
            objective = self._GetObjective(task)
            isCurrentObjective = self._IsActiveTask(task.id)
            if isCurrentObjective or self._ShouldShowPastObjectives():
                objectives.append(objective)
            if isCurrentObjective:
                objective.SetActive()
                break

        if not isCurrentObjective:
            return
        self.objectives.extend(objectives)

    def _GetObjective(self, task):
        category = GetOperationsController().get_category_by_id(self.categoryID)
        objectiveClass = self._GetObjectiveClass(task)
        objective = objectiveClass(category, self.operation, task)
        return objective

    def _GetObjectiveClass(self, task):
        if task.achievementEventType == AchievementEventConst.TRAVEL_SET_DESTINATION_TO_CAREER_AGENTS:
            objectiveClass = taskObjectiveData.TaskTravelToCareerAgent
        elif self.operation.siteID and task.is_site_relevant:
            objectiveClass = taskObjectiveData.TaskWithSiteObjective
        else:
            objectiveClass = taskObjectiveData.TaskObjective
        return objectiveClass

    def _ShouldShowPastObjectives(self):
        return self.categoryID in CATEGORIES_THAT_SHOW_PAST_OBJECTIVES

    def _IsActiveTask(self, taskID):
        return taskID in [ activeTaskID for activeTaskID, _, _ in self.activeTasks ]


class InfoPanelOperationRecommendationsData(InfoPanelOperationData):

    def __init__(self, categoryID = None, operation = None, activeTasks = None, includePrveviousTask = False):
        self.includePrveviousTask = includePrveviousTask
        super(InfoPanelOperationRecommendationsData, self).__init__(categoryID, operation, activeTasks)

    def _ShouldShowPastObjectives(self):
        return self.includePrveviousTask

    def _InitializeObjectives(self):
        self.objectives = []
        currentObjective = None
        previousObjective = None
        for task in self.operation.taskList:
            objective = self._GetObjective(task)
            isCurrentObjective = self._IsActiveTask(task.id)
            if isCurrentObjective:
                currentObjective = objective
                objective.SetActive()
                break
            previousObjective = objective

        if not currentObjective:
            return
        objectives = [currentObjective]
        if self._ShouldShowPastObjectives() and previousObjective:
            objectives.insert(0, previousObjective)
        self.objectives.extend(objectives)


class InfoPanelOperations(UiHiderMixin, InfoPanelMissions):
    default_name = 'InfoPanelOperations'
    uniqueUiName = UNIQUE_NAME_TUTORIAL_INFO_PANEL
    panelTypeID = PANEL_OPERATIONS
    label = ''
    default_iconTexturePath = 'res:/UI/Texture/Classes/InfoPanels/operationsIcon_Main.png'
    default_are_objectives_collapsable = False

    def ApplyAttributes(self, attributes):
        super(InfoPanelOperations, self).ApplyAttributes(attributes)
        self.closeButton = ButtonIcon(name='closeButton_InfoPanelOperations', parent=self.topCont, align=uiconst.CENTERRIGHT, width=CLOSE_ICON_SIZE, height=CLOSE_ICON_SIZE, iconSize=CLOSE_ICON_SIZE, texturePath=CLOSE_ICON_TEXTURE, left=5, state=uiconst.UI_NORMAL)
        self.UpdateCloseButton()

    def UpdateCloseButton(self):
        self.closeButton.hint = GetByLabel(SKIP_TUTORIAL_LABEL)
        self.closeButton.func = self.SkipTutorial

    def GetTitle(self):
        return GetOperationsTitle()

    @classmethod
    def GetClassHint(cls):
        if cls.mode != MODE_HIDDEN:
            return GetOperationsTitle()

    @staticmethod
    def IsAvailable():
        if are_operations_active() and GetOperationsController().is_any_operation_active():
            if not GetOperationsController().is_active_operation_a_recommendation():
                return True
        return False

    def Update(self, oldMode = None):
        if self.header:
            self.header.text = self.GetTitle()
        super(InfoPanelOperations, self).Update(oldMode)

    def ConstructNormal(self):
        super(InfoPanelOperations, self).ConstructNormal()
        self.UpdateCloseButton()

    def _AnimFadeInSelf(self, duration):
        if self._is_hidden:
            return
        super(InfoPanelOperations, self)._AnimFadeInSelf(duration)

    def GetMissions(self):
        missions = []
        if GetOperationsController().is_any_operation_active():
            activeOperationData = InfoPanelOperationData()
            missions.append(activeOperationData)
        return missions

    def GetFirstActiveObjective(self):
        for mission in self.missions:
            for objective in mission.GetObjectives():
                if objective.IsActive():
                    return objective

    def SkipTutorial(self):
        skip_air_npe('SkipTutorialOffer')


class DummyInfoPanelMissionData(InfoPanelMissionData):

    def _InitializeObjectives(self):
        pass
