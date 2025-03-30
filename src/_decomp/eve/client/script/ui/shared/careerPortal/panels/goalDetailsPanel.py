#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\panels\goalDetailsPanel.py
import evetypes
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util import logUtil as log
from carbon.common.script.util.format import FmtAmt
from carbonui import Axis, ButtonFrameType, ButtonVariant, uiconst
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from careergoals.client.goal import Goal
from careergoals.client.signal import on_goal_completed, on_definitions_loaded
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveLabelMedium, EveCaptionLarge, EveLabelLarge
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupHome
from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
from eve.client.script.ui.shared.careerPortal import careerConst, cpSignals
from eve.client.script.ui.shared.careerPortal.careerConst import AGENCY_SECTION_NAMES_TO_IDS
from eve.client.script.ui.shared.careerPortal.careerControllerUI import get_career_portal_controller_svc
from eve.client.script.ui.shared.careerPortal.panels.basePanel import BasePanel
from eve.client.script.ui.shared.careerPortal.panels.detailsEntry import OmegaRewardDetailsEntry, AlphaRewardDetailsEntry, CareerPointsDetailsEntry, GoalInfoDetailsEntry
from fsdBuiltData.client.agency.helpVideoFSDLoader import AgencyHelpVideosFSDLoader
from fsdBuiltData.common.iconIDs import GetIconFile
from localization import GetByLabel, GetByMessageID
MAX_LABEL_WIDTH = 250
BOTTOM_CONT_HEIGHT = 32
COMPLETION_FADE_IN_DURATION = 0.1

class AuraGoalPanel(BasePanel):
    default_state = uiconst.UI_NORMAL
    default_name = 'AuraGoalAssistanceSection'

    def ApplyAttributes(self, attributes):
        super(AuraGoalPanel, self).ApplyAttributes(attributes)
        self.ConstructHeader()
        self.ConstructEmptyBody()

    def LoadGoal(self, goal):
        if self.mainCont.destroyed:
            return
        self.bodyCont.Flush()
        PlaySound('career_portal_aura_assistance_play')
        EveLabelLarge(parent=self.bodyCont, state=uiconst.UI_NORMAL, align=uiconst.TOTOP, text=GetByMessageID(int(goal.definition.aura_text_id)), padBottom=16)
        buttonCont = ButtonGroup(parent=self.bodyCont, align=uiconst.TOTOP, orientation=Axis.VERTICAL, button_size_mode=ButtonSizeMode.STRETCH)
        if goal.definition.has_video_id():
            video = AgencyHelpVideosFSDLoader.GetByID(int(goal.definition.video_id))
            if video:
                self.videoButton = Button(name='videoButton', parent=buttonCont, label=GetByMessageID(video.nameID), texturePath='res:/UI/Texture/classes/careerPortal/playVideo.png', func=lambda x: get_career_portal_controller_svc().play_video(video.path), variant=ButtonVariant.GHOST)
        agencyLinkIdString = goal.definition.agency_link_text_id
        if agencyLinkIdString and agencyLinkIdString != u'null':
            if goal.definition.agency_screen_id in AGENCY_SECTION_NAMES_TO_IDS:
                agencyContentGroup = AGENCY_SECTION_NAMES_TO_IDS[goal.definition.agency_screen_id]
            else:
                agencyContentGroup = contentGroupHome
                log.LogWarn('Failed to find %s in AGENCY_SECTION_NAMES_TO_IDS - Defaulting to agency homepage' % goal.definition.agency_screen_id)

            def open_career_agents_in_agency():
                PlaySound('career_portal_career_agents_play')
                AgencyWndNew.OpenAndShowContentGroup(agencyContentGroup)

            self.showInAgencyBtn = Button(parent=buttonCont, label=GetByMessageID(int(agencyLinkIdString)), texturePath='res:/UI/Texture/classes/careerPortal/aura_icon_agency.png', func=open_career_agents_in_agency, args=(), variant=ButtonVariant.GHOST)

    def ConstructEmptyBody(self):
        self.bodyCont = ContainerAutoSize(padLeft=5, parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)

    def ConstructHeader(self):
        self.headerCont = Container(parent=self, align=uiconst.TOTOP, height=32, padBottom=5)
        Sprite(parent=self.headerCont, align=uiconst.TOLEFT, useSizeFromTexture=True, texturePath='res:/UI/Texture/classes/careerPortal/aura/aura_icon_32x32.png', width=32)
        EveCaptionLarge(parent=self.headerCont, align=uiconst.TOLEFT, text=GetByLabel('UI/CareerPortal/AuraAssistancePanelTitle'), padLeft=8, color=eveColor.AURA_PURPLE, bold=True)


class GoalPanel(BasePanel):
    default_name = 'GoalPanel'

    def ApplyAttributes(self, attributes):
        super(GoalPanel, self).ApplyAttributes(attributes)
        self.goal = None
        self.ConstructHeaderSubsection()
        self.ConstructRewardsSubsection()
        self.ConstructInformationSubsection()
        self.ConstructBottomSubsection()
        self._ConnectSignals()

    def Close(self):
        self._DisconnectSignals()
        super(GoalPanel, self).Close()

    def _ConnectSignals(self):
        cpSignals.on_cp_goal_tracking_added.connect(self.OnGoalTrackingAdded)
        cpSignals.on_cp_goal_tracking_removed.connect(self.OnGoalTrackingRemoved)
        on_goal_completed.connect(self.OnGoalCompleted)
        on_definitions_loaded.connect(self._LoadRewards)

    def _DisconnectSignals(self):
        cpSignals.on_cp_goal_tracking_added.disconnect(self.OnGoalTrackingAdded)
        cpSignals.on_cp_goal_tracking_removed.disconnect(self.OnGoalTrackingRemoved)
        on_goal_completed.disconnect(self.OnGoalCompleted)
        on_definitions_loaded.disconnect(self._LoadRewards)

    def LoadGoal(self, goal):
        if self.mainCont.destroyed:
            return
        self.goal = goal
        self.rewardsSubsection.Flush()
        self.informationSubsection.Flush()
        self.goalName.text = goal.definition.name
        self.goalDescription.text = goal.definition.description
        self._LoadRewards()
        GoalInfoDetailsEntry(parent=self.informationSubsection, texture_path='res:/UI/Texture/Shared/warning_16.png', text=GetByLabel('UI/CareerPortal/Threat'), value=careerConst.get_threat_name(goal.definition.threat))
        GoalInfoDetailsEntry(parent=self.informationSubsection, texture_path='res:/UI/Texture/classes/careerPortal/clock_16.png', text=GetByLabel('UI/CareerPortal/GoalDuration'), value=goal.definition.duration_text)
        if goal.is_completed():
            self._HideTrackedButton(animate=False)
            self._ShowCompletedState(animate=False)
        else:
            self._ShowTrackedButton()
            self._HideCompletedState()
            self.trackButton.SetFunc(lambda x: self.OnTrackButtonPressed(goal.goal_id, x))
            isTracked = get_career_portal_controller_svc().is_goal_tracked(goal.goal_id)
            if isTracked:
                self._SetButtonToTrackedState()
            else:
                self._SetButtonToUntrackedState()

    def _LoadRewards(self):
        if self.rewardsSubsection.children:
            return
        if not self.goal:
            return
        for reward in self.goal.definition.omega_rewards:
            self.create_omega_reward_entry(reward)

        for reward in self.goal.definition.alpha_rewards:
            self.create_alpha_reward_entry(reward)

        self.create_career_points_entry()
        self.rewardsLoadingWheel.Hide()

    def create_omega_reward_entry(self, reward):
        OmegaRewardDetailsEntry(parent=self.rewardsSubsection, texture_path=GetIconFile(evetypes.GetIconID(reward.type_id)), text='%sx %s' % (FmtAmt(reward.quantity), evetypes.GetName(reward.type_id)), type_id=reward.type_id)

    def create_alpha_reward_entry(self, reward):
        AlphaRewardDetailsEntry(parent=self.rewardsSubsection, texture_path=GetIconFile(evetypes.GetIconID(reward.type_id)), text='%sx %s' % (FmtAmt(reward.quantity), evetypes.GetName(reward.type_id)), type_id=reward.type_id)

    def create_career_points_entry(self):
        CareerPointsDetailsEntry(parent=self.rewardsSubsection, texture_path=careerConst.CAREERS_32_SIZES[self.goal.definition.career], text=self.goal.definition.career_points_text)

    def ConstructHeaderSubsection(self):
        self.goalName = EveCaptionLarge(parent=self.mainCont, align=uiconst.TOTOP, bold=True)
        self.goalDescription = EveLabelMedium(parent=self.mainCont, align=uiconst.TOTOP)

    def ConstructRewardsSubsection(self):
        Line(parent=self.mainCont, align=uiconst.TOTOP, padding=(0, 8, 0, 8))
        EveCaptionSmall(parent=self.mainCont, align=uiconst.TOTOP, text=GetByLabel('UI/CareerPortal/RewardsHeader'))
        self.rewardsSubsection = ContainerAutoSize(name='RewardsSubsection', parent=self.mainCont, align=uiconst.TOTOP)
        self.rewardsLoadingWheel = LoadingWheel(name='LoadingWheel', parent=ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP), align=uiconst.CENTERTOP, width=32, height=32)

    def ConstructInformationSubsection(self):
        Line(parent=self.mainCont, align=uiconst.TOTOP, padding=(0, 8, 0, 8))
        EveCaptionSmall(parent=self.mainCont, align=uiconst.TOTOP, text=GetByLabel('UI/Common/Information'))
        self.informationSubsection = ContainerAutoSize(name='InformationSubsection', parent=self.mainCont, align=uiconst.TOTOP)

    def ConstructBottomSubsection(self):
        bottomCont = Container(parent=self.mainCont, name='bottomCont', align=uiconst.TOTOP, top=16, height=BOTTOM_CONT_HEIGHT)
        self.trackButton = Button(parent=bottomCont, name='trackButton', align=uiconst.TOTOP, iconSize=20, frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT)
        self.completedCont = ContainerAutoSize(parent=bottomCont, name='completedCont', align=uiconst.CENTER, height=BOTTOM_CONT_HEIGHT)
        GlowSprite(parent=self.completedCont, name='completedSprite', align=uiconst.TOLEFT, texturePath='res:/UI/Texture/classes/careerPortal/rewardBar_completedCrate.png', width=32)
        textContainer = ContainerAutoSize(parent=self.completedCont, name='textCont', align=uiconst.TOLEFT)
        EveLabelMedium(parent=textContainer, name='completedLabel', align=uiconst.CENTERLEFT, text=GetByLabel('UI/CareerPortal/GoalCompleted'), color=eveColor.LEAFY_GREEN, bold=True)

    def OnTrackButtonPressed(self, goalID, button):
        isTracked = get_career_portal_controller_svc().is_goal_tracked(goalID)
        if isTracked:
            get_career_portal_controller_svc().untrack_goal(goalID)
        else:
            PlaySound('career_portal_mission_view_play')
            get_career_portal_controller_svc().track_goal(goalID)

    def OnGoalTrackingAdded(self, goalID):
        if not self.goal:
            return
        if goalID == self.goal.goal_id:
            self._SetButtonToTrackedState()

    def OnGoalTrackingRemoved(self, goalID):
        if not self.goal:
            return
        if goalID == self.goal.goal_id:
            self._SetButtonToUntrackedState()

    def OnGoalCompleted(self, goalID):
        if not self.goal:
            return
        if goalID == self.goal.goal_id:
            self._HideTrackedButton(animate=True)
            self._ShowCompletedState(animate=True)

    def _HideTrackedButton(self, animate = False):
        if animate:
            animations.FadeOut(self.trackButton, duration=COMPLETION_FADE_IN_DURATION)
        else:
            self.trackButton.opacity = 0.0

    def _ShowTrackedButton(self):
        self.trackButton.opacity = 1.0

    def _HideCompletedState(self):
        self.completedCont.Hide()

    def _ShowCompletedState(self, animate = False):
        self.completedCont.Show()
        if animate:
            animations.FadeIn(self.completedCont, duration=COMPLETION_FADE_IN_DURATION)
        else:
            self.completedCont.opacity = 1.0

    def _SetButtonToTrackedState(self):
        self.trackButton.variant = ButtonVariant.NORMAL
        self.trackButton.SetLabel(GetByLabel('UI/CareerPortal/UntrackGoal'))
        self.trackButton.texturePath = 'res:/UI/Texture/classes/careerPortal/circleView/eye_closed_32.png'

    def _SetButtonToUntrackedState(self):
        self.trackButton.variant = ButtonVariant.PRIMARY
        self.trackButton.SetLabel(GetByLabel('UI/CareerPortal/TrackGoal'))
        self.trackButton.texturePath = 'res:/UI/Texture/classes/careerPortal/circleView/eye_open_32.png'
