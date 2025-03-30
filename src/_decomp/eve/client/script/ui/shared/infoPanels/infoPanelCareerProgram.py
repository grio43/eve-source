#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelCareerProgram.py
from carbonui import TextColor
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from careergoals.client.career_goal_svc import get_career_goals_svc
from careergoals.client.signal import on_goal_progress_changed, on_goal_completed, on_reward_claimed
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from carbonui.primitives.line import Line
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.shared.careerPortal.careerControllerUI import get_career_portal_controller_svc
from eve.client.script.ui.shared.careerPortal.cpSignals import on_cp_goal_tracking_added, on_cp_goal_tracking_removed
from eve.client.script.ui.shared.careerPortal.panels.goalDetailsPanel import AuraGoalPanel
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel
from uihider import UiHiderMixin
import carbonui.const as uiconst
from uihighlighting.uniqueNameConst import UNIQUE_NAME_CAREER_INFO_PANEL
from carbonui import Density, ButtonFrameType
from careergoals.client.goal import Goal

class InfoPanelCareerProgram(UiHiderMixin, InfoPanelBase):
    __guid__ = 'uicls.InfoPanelCareerProgram'
    default_name = 'InfoPanelCareerProgram'
    uniqueUiName = UNIQUE_NAME_CAREER_INFO_PANEL
    panelTypeID = infoPanelConst.PANEL_CAREER_PROGRAM
    label = 'UI/CareerPortal/CareerPortalWnd'
    default_iconTexturePath = 'res:/ui/Texture/Classes/InfoPanels/careerProgram.png'
    default_mode = infoPanelConst.MODE_NORMAL
    default_are_objectives_collapsable = False

    def ApplyAttributes(self, attributes):
        self.sectionHeader = None
        super(InfoPanelCareerProgram, self).ApplyAttributes(attributes)
        self.currentGoals = {}
        titleText = GetByLabel(self.label)
        self.titleLabel = self.headerCls(name='title', text=titleText, parent=self.headerCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        self.UpdatePanel()
        self.ConnectSignals()

    def ConnectSignals(self):
        on_cp_goal_tracking_added.connect(self.UpdateTrackedGoal)
        on_cp_goal_tracking_removed.connect(self.UpdateTrackedGoal)
        on_goal_progress_changed.connect(self.OnGoalProgress)
        on_goal_completed.connect(self.OnGoalCompleted)
        on_reward_claimed.connect(self.OnRewardClaimed)

    def DisconnectSignals(self):
        on_cp_goal_tracking_added.disconnect(self.UpdateTrackedGoal)
        on_cp_goal_tracking_removed.disconnect(self.UpdateTrackedGoal)
        on_goal_progress_changed.disconnect(self.OnGoalProgress)
        on_goal_completed.disconnect(self.OnGoalCompleted)
        on_reward_claimed.disconnect(self.OnRewardClaimed)

    @staticmethod
    def IsAvailable():
        return bool(get_career_portal_controller_svc().get_tracked_goals())

    def UpdatePanel(self):
        trackedGoalIDs = get_career_portal_controller_svc().get_tracked_goals()
        for goalID in trackedGoalIDs:
            goalCont = self.currentGoals.get(goalID, None)
            if not goalCont or goalCont.destroyed:
                goal = get_career_goals_svc().get_goal_data_controller().get_goal(goalID)
                if not goal:
                    continue
                self.currentGoals[goalID] = TrackedGoal(parent=self.mainCont, goal=goal)

        for goalID in self.currentGoals.keys():
            if goalID in trackedGoalIDs:
                continue
            cont = self.currentGoals.pop(goalID, None)
            if cont:
                cont.Close()

    def UpdateTrackedGoal(self, *args):
        if set(self.currentGoals.keys()) != get_career_portal_controller_svc().get_tracked_goals():
            self.UpdatePanel()

    def ConstructHeaderButton(self):
        btn = self.ConstructSimpleHeaderButton()
        btn.OnClick = OpenCareerPortal

    def OnGoalProgress(self, goalID, progress):
        self.UpdateGoal(goalID)

    def OnGoalCompleted(self, goalID):
        self.UpdateGoal(goalID)

    def OnRewardClaimed(self, goalID, _):
        if goalID in self.currentGoals:
            isTracked = get_career_portal_controller_svc().is_goal_tracked(goalID)
            if isTracked:
                goal = get_career_goals_svc().get_goal_data_controller().get_goal(goalID)
                if goal and not goal.has_unclaimed_rewards():
                    get_career_portal_controller_svc().untrack_goal(goalID)

    def UpdateGoal(self, goalID):
        cont = self.currentGoals.get(goalID)
        if not cont:
            return
        cont.UpdateGoalInfo()

    def Close(self):
        self.DisconnectSignals()
        super(InfoPanelCareerProgram, self).Close()


def OpenCareerPortal(*args):
    from eve.client.script.ui.shared.careerPortal.careerPortalWnd import CareerPortalDockablePanel
    wnd = CareerPortalDockablePanel.GetIfOpen()
    if wnd and not wnd.destroyed:
        wnd.Maximize()
    else:
        CareerPortalDockablePanel.Open()


class TrackedGoal(ContainerAutoSize):
    default_align = uiconst.TOTOP
    default_alignMode = uiconst.TOTOP
    default_padBottom = 8

    def ApplyAttributes(self, attributes):
        super(TrackedGoal, self).ApplyAttributes(attributes)
        self.goal = attributes.goal
        SectionHeader(parent=self, title=self.goal.definition.name, goal=self.goal)
        self._collapsed = False
        mainContainer = ContainerAutoSize(parent=self, bgColor=(0, 0, 0, 0.25), align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padTop=4)
        wrapper = ContainerAutoSize(parent=mainContainer, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=8)
        progressCont = ContainerAutoSize(name='progressCont', parent=wrapper, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.completeLine = Line(parent=progressCont, state=uiconst.UI_HIDDEN, align=uiconst.TOLEFT_NOPUSH, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, color=TextColor.SUCCESS, opacity=0.75, left=-8)
        progressCont.OnClick = self._OnProgressContClicked
        self.progressLabel = EveLabelLarge(parent=progressCont, name='progressLabel', align=uiconst.TOTOP)
        contentContainer = ContainerAutoSize(name='contentContainer', parent=wrapper, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, clipChildren=True)
        self.bottomCont = ContainerAutoSize(name='bottomCont', parent=contentContainer, align=uiconst.TOTOP)
        self.descLabel = EveLabelMedium(parent=self.bottomCont, name='descLabel', align=uiconst.TOTOP, text=self.goal.definition.description, padding=4)
        self.claimButton = Button(name='claimButton', align=uiconst.TOTOP, parent=self.bottomCont, density=Density.COMPACT, frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT, label=GetByLabel('UI/CareerPortal/ClaimRewards'), func=OpenCareerPortal)
        self.UpdateGoalInfo()

    def UpdateGoalInfo(self):
        self.progressLabel.text = GetByLabel('UI/CareerPortal/GoalProgressCompleted', progressValue=self.goal.progress, targetValue=self.goal.definition.target_value)
        if self.goal.has_unclaimed_rewards():
            self.completeLine.Show()
            self.claimButton.Show()
        else:
            self.completeLine.Hide()
            self.claimButton.Hide()
        self.descLabel.text = self.goal.definition.description

    def _OnProgressContClicked(self):
        self._collapsed = not self._collapsed
        if self._collapsed:
            self.bottomCont.CollapseHeight(callback=self.bottomCont.Hide)
        else:
            self.bottomCont.Show()
            self.bottomCont.ExpandHeight()


class SectionHeader(ContainerAutoSize):
    default_name = 'SectionHeader'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOTOP
    default_alignMode = uiconst.TOTOP
    default_bgColor = (0, 0, 0, 0.35)

    def ApplyAttributes(self, attributes):
        super(SectionHeader, self).ApplyAttributes(attributes)
        title = attributes.title
        goal = attributes.goal
        mainContainer = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=8)
        auraIconContainer = Container(name='auraIconContainer', parent=mainContainer, align=uiconst.TORIGHT, width=16, padLeft=4)
        auraSprite = Sprite(parent=auraIconContainer, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/careerPortal/aura/aura_icon_16x16.png', width=16, height=16)
        auraSprite.tooltipPanelClassInfo = AuraAssistanceTooltip(goal)
        titleContainer = ContainerAutoSize(name='titleContainer', parent=mainContainer, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, clipChildren=True)
        EveLabelLarge(name='titleLabel', parent=titleContainer, align=uiconst.TOTOP, maxLines=1, showEllipsis=True, color=TextColor.HIGHLIGHT, text=title)
        self.hint = title


class AuraAssistanceTooltip(TooltipBaseWrapper):

    def __init__(self, goal, *args, **kwargs):
        super(AuraAssistanceTooltip, self).__init__(*args, **kwargs)
        self.goal = goal

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.AddCaptionMedium(text=GetByLabel('UI/CareerPortal/AuraAssistancePanelTitle'), left=16)
        self.tooltipPanel.AddDivider()
        auraAssistanceSection = AuraGoalPanel(width=400, align=uiconst.CENTER, insidePadding=(8, 8, 8, 8))
        auraAssistanceSection.headerCont.Hide()
        auraAssistanceSection.LoadGoal(self.goal)
        auraAssistanceSection.opacity = 1
        self.tooltipPanel.AddCell(auraAssistanceSection)
        return self.tooltipPanel
