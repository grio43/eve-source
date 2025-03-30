#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelRecommendations.py
import carbonui.const as uiconst
import logging
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import ButtonStyle
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
from eve.client.script.ui.shared.infoPanels.infoPanelMissions import InfoPanelMissions
from eve.client.script.ui.shared.infoPanels.infoPanelOperations import InfoPanelOperationRecommendationsData
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_RECOMMENDATIONS_INFO_PANEL
from eve.client.script.ui.shared.recommendation.const import Sounds
from eve.client.script.ui.shared.recommendation.recommendationWnd import RecommendationWnd
from eve.client.script.ui.shared.recommendation.uiConst import HAS_INTERACTED_WITH, INFO_PANEL_ICON, TREATMENT_ACTIVE_COLORS_BTN, TREATMENT_COMPLETED_COLORS_BTN, TREATMENT_NORMAL_COLORS_BTN
from localization import GetByLabel
from eve.client.script.ui.shared.infoPanels.const.infoPanelUIConst import PANELWIDTH, LEFTPAD
from operations.client.operationscontroller import GetOperationsController
from operations.common.const import OPERATION_CATEGORY_RECOMMENDATIONS
from uihider import UiHiderMixin
logger = logging.getLogger(__name__)
HEADER_WIDTH = PANELWIDTH - LEFTPAD
HEADER_HEIGHT = 29
HEADER_ICON_SIZE = 20
PADDING_HEADER_TO_OBJECTIVE_HEADER = 4
PADDING_ICON_TO_TITLE = 4
PADDING_EDGE_TO_TITLE = 8
POINT_RIGHT_HEADER_FRAME_TEXTURE_PATH = 'res:/UI/Texture/classes/Achievements/pointRightHeaderFrame.png'
POINT_RIGHT_HEADER_FRAME_CORNER_SIZE = 16
POINT_RIGHT_HEADER_FRAME_OFFSET = -14
POINT_RIGHT_HEADER_COLOR = (1, 1, 1, 0.25)

class InfoPanelRecommendations(UiHiderMixin, InfoPanelMissions):
    __guid__ = 'uicls.InfoPanelRecommendations'
    default_name = 'InfoPanelRecommendations'
    uniqueUiName = UNIQUE_NAME_RECOMMENDATIONS_INFO_PANEL
    panelTypeID = infoPanelConst.PANEL_RECOMMENDATIONS
    label = 'UI/recommendations/InfoPanel/Header'
    default_iconTexturePath = INFO_PANEL_ICON
    default_mode = infoPanelConst.MODE_NORMAL
    default_are_objectives_collapsable = False
    __notifyevents__ = InfoPanelMissions.__notifyevents__ + ['OnRecommendationsChanged', 'OnOperationRecommendationCompleted', 'OnOperationTaskTransition']

    def __init__(self, *args, **kwargs):
        self.recommendationSvc = sm.GetService('recommendationSvc')
        self.includePreviousTask = False
        super(InfoPanelRecommendations, self).__init__(*args, **kwargs)

    def GetTitle(self):
        return GetByLabel('UI/recommendations/InfoPanel/Header')

    @staticmethod
    def IsAvailable():
        if not sm.GetService('recommendationSvc').IsFeatureEnabled():
            return False
        if GetOperationsController().is_non_recommendation_operation_active():
            return False
        return True

    def Update(self, oldMode = None):
        if self.header:
            self.header.text = self.GetTitle()
        super(InfoPanelRecommendations, self).Update(oldMode)

    def OnRecommendationsChanged(self, *args):
        self.Update(self.mode)

    def OnOperationRecommendationCompleted(self, operationID):
        self.UpdateButton()

    def OnOperationTaskTransition(self, categoryID, operationID, taskID, fromState, toState):
        if categoryID != OPERATION_CATEGORY_RECOMMENDATIONS:
            return
        if not GetOperationsController().is_any_operation_active():
            return
        self.includePreviousTask = True
        self.ConstructNormal()
        self.AnimateTransition()
        self.includePreviousTask = False

    def AnimateTransition(self):
        for eachMission in self.missionContainers.itervalues():
            for objCont in eachMission.missionObjectiveContainers.itervalues():
                if objCont.objective.IsActive():
                    animations.MorphScalar(objCont, 'padBottom', startVal=-objCont.height, endVal=objCont.padBottom, duration=0.35)
                    animations.FadeTo(objCont, duration=0.35)
                else:
                    animations.MorphScalar(objCont, 'top', startVal=objCont.top, endVal=-objCont.height, duration=1.0, timeOffset=1.0)

    def ConstructNormal(self):
        self.mainCont.Flush()
        self.state = uiconst.UI_NORMAL
        if GetOperationsController().is_active_operation_a_recommendation() or self.recommendationSvc.ShowLastCompleted():
            super(InfoPanelRecommendations, self).ConstructNormal()
        else:
            self.ConstructHeaderFrame()
            if not self.recommendationSvc.HasEverAcceptedARecommendation():
                textCont = ContainerAutoSize(name='textCont', parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
                Fill(bgParent=textCont, color=(0.2, 0.2, 0.2, 0.4))
                EveLabelMedium(parent=textCont, text=GetByLabel('UI/recommendations/InfoPanel/Description'), align=uiconst.TOTOP, padding=(6, 10, 6, 10))
        buttonCont = Container(name='buttonCont', parent=self.mainCont, align=uiconst.TOTOP, padTop=0)
        if not getattr(self, 'btn', None) or self.btn.destroyed:
            self.btn = Button(parent=buttonCont, align=uiconst.TOTOP, label=GetByLabel('UI/recommendations/InfoPanel/ViewOpportunities'), texturePath='res:/UI/Texture/classes/war/leftArrow.png', func=self.OpenRecommendationsWindow)
        buttonCont.height = self.btn.height
        self.UpdateButton()

    def ConstructHeaderFrame(self):
        missionHeaderPadBottom = PADDING_HEADER_TO_OBJECTIVE_HEADER
        missionHeaderContainer = Container(name='recommendations_containerHeader', parent=self.mainCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=HEADER_HEIGHT + missionHeaderPadBottom, padBottom=missionHeaderPadBottom)
        Frame(name='recommendations_containerHeader_frame', texturePath=POINT_RIGHT_HEADER_FRAME_TEXTURE_PATH, cornerSize=POINT_RIGHT_HEADER_FRAME_CORNER_SIZE, offset=POINT_RIGHT_HEADER_FRAME_OFFSET, parent=missionHeaderContainer, color=POINT_RIGHT_HEADER_COLOR, align=uiconst.TOALL)
        paddingLeft = PADDING_EDGE_TO_TITLE
        paddingRight = PADDING_ICON_TO_TITLE
        titleWidth = HEADER_WIDTH - paddingLeft - paddingRight
        missionTitleContainer = Container(name='recommendations_containerTitle', parent=missionHeaderContainer, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED, width=titleWidth, height=HEADER_HEIGHT, left=PADDING_EDGE_TO_TITLE)
        titleLabel = EveLabelLarge(name='recommendations_title', parent=missionTitleContainer, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, text=GetByLabel('UI/recommendations/InfoPanel/RecommendedForYou'))
        titleLabel.SetRightAlphaFade(fadeEnd=missionTitleContainer.width, maxFadeWidth=3)
        optionsMenuIconContainer = Container(name='recommendations_containerIconOptionsMenu', parent=missionHeaderContainer, align=uiconst.TORIGHT, state=uiconst.UI_PICKCHILDREN, width=HEADER_ICON_SIZE, height=HEADER_HEIGHT)
        self.helpIcon = MoreInfoIcon(parent=optionsMenuIconContainer, align=uiconst.CENTERRIGHT, left=1, hint=GetByLabel('UI/recommendations/InfoPanel/OpportunitiesHint'))

    def UpdateButton(self):
        btn = getattr(self, 'btn', None)
        if not btn or btn.destroyed:
            return
        btn.SetLabel(GetByLabel('UI/recommendations/InfoPanel/ViewOpportunities'))
        shouldBlink = self.recommendationSvc.ShouldInfoPanelBlink()
        if self.recommendationSvc.ShowLastCompleted():
            btn.label = GetByLabel('UI/recommendations/InfoPanel/OpportunityCompleted')
            btn.style = ButtonStyle.SUCCESS
            if shouldBlink:
                btn.Blink(1)
        elif GetOperationsController().is_active_operation_a_recommendation():
            btn.style = ButtonStyle.NORMAL
        else:
            btn.style = ButtonStyle.NORMAL
            if shouldBlink:
                btn.Blink(1)

    def OpenRecommendationsWindow(self, *args):
        btn = getattr(self, 'btn', None)
        if btn:
            btn.Blink(0)
        hasInteractedWith = settings.char.ui.Get(HAS_INTERACTED_WITH, False)
        wnd = RecommendationWnd.Open()
        wnd.ShowDialog(modal=True, state=uiconst.UI_PICKCHILDREN, closeWhenClicked=True)
        PlaySound(Sounds.OPEN)
        settings.char.ui.Set(HAS_INTERACTED_WITH, True)
        if not hasInteractedWith:
            sm.ScatterEvent('OnRecommendationsUpdated')

    def GetMissions(self):
        missions = []
        if GetOperationsController().is_any_operation_active():
            activeOperationData = InfoPanelOperationRecommendationsData(includePrveviousTask=self.includePreviousTask)
            missions.append(activeOperationData)
        elif self.recommendationSvc.ShowLastCompleted():
            lastActiveOperationInfo = self.recommendationSvc.activeRecommendation
            activeOperationData = InfoPanelOperationRecommendationsData(lastActiveOperationInfo.categoryID, lastActiveOperationInfo.operation, lastActiveOperationInfo.taskList)
            missions.append(activeOperationData)
        return missions

    def GetFirstActiveObjective(self):
        for mission in self.missions:
            for objective in mission.GetObjectives():
                if objective.IsActive():
                    return objective

    def GetOptionsMenu(self, menuParent, mission):
        pass
