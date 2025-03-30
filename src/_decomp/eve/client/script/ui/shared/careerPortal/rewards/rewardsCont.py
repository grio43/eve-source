#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\rewards\rewardsCont.py
import carbonui.const as uiconst
import logging
import trinity
import uthread2
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.section import Section
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from carbonui.uianimations import animations
from careergoals.client.career_goal_svc import get_career_goals_svc
from careergoals.client.const import RewardLabel
from careergoals.client.signal import on_goal_completed, on_reward_claimed, on_reward_claimed_failed
from eve.client.script.ui import eveThemeColor, eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.shared.careerPortal.cpSignals import on_clicked_outside
from eve.client.script.ui.shared.careerPortal.rewards.rewardEntry import GraduationRewardEntry, OmegaRewardEntry, RewardEntry
from eve.client.script.ui.util.uix import GetTextWidth, GetTextHeight
from eveexceptions import ExceptionEater
from localization import GetByLabel
from eve.client.script.ui.shared.pointerTool import pointerToolConst as pConst
logger = logging.getLogger(__name__)
EXPANDED_WIDTH = 444
REWARD_HEADER_PADDING = 24
REWARD_HEADER_HEIGHT = 30
REWARD_ENTRY_PADDING = 8
SCROLL_CONTAINER_PADDING = 24
DOT_SIZE_SMALL = 16
DOT_SIZE_BIG = 32
NO_CONTENT_HEIGHT = 150
MAX_HEIGHT = 754

class RewardsCont(Section):
    uniqueUiName = pConst.UNIQUE_NAME_ACP_REWARDS_CONTAINER
    default_state = uiconst.UI_NORMAL
    default_name = 'RewardsContainer'
    default_color = (0, 0, 0, 0.9)

    def ApplyAttributes(self, attributes):
        self._expanded = False
        self._lenRewardsLoading = 0
        super(RewardsCont, self).ApplyAttributes(attributes)
        self._collapsedWidth = 2 * REWARD_HEADER_PADDING + GetTextWidth(self.titleLabel.text, fontsize=self.titleLabel.fontsize, fontStyle=self.titleLabel.fontStyle)
        self._collapsedWidthWithBadge = self._collapsedWidth + 10
        self._collapsedHeight = 2 * REWARD_HEADER_PADDING + GetTextHeight(self.titleLabel.text, fontsize=self.titleLabel.fontsize, fontStyle=self.titleLabel.fontStyle)
        goal_data_controller = get_career_goals_svc().get_goal_data_controller()
        if goal_data_controller.get_claimable_rewards_count() > 0 or len(goal_data_controller.get_local_claimed_rewards()) > 0:
            uthread2.StartTasklet(self.ConstructExpandedView)
        else:
            self.ConstructCollapsedView()
        on_goal_completed.connect(self.AddClaimableGoal)
        on_reward_claimed.connect(self.OnRewardClaimed)
        on_clicked_outside.connect(self.OnClickedOutside)
        on_reward_claimed_failed.connect(self.OnRewardClaimedFailed)

    def _ConstructLine(self):
        Line(parent=self, align=uiconst.TOTOP, outputMode=trinity.Tr2SpriteTarget.COLOR_AND_GLOW, color=eveThemeColor.THEME_ACCENT)

    def Close(self):
        with ExceptionEater('disconnectSignals'):
            on_goal_completed.disconnect(self.AddClaimableGoal)
            on_reward_claimed.disconnect(self.OnRewardClaimed)
            on_clicked_outside.disconnect(self.OnClickedOutside)
            on_reward_claimed_failed.disconnect(self.OnRewardClaimedFailed)
        super(RewardsCont, self).Close()

    def _ConstructHeader(self):
        self._ConstructLine()
        self.headerContainer = FlowContainer(name='headerContainer', parent=self, align=uiconst.TOTOP, padding=(REWARD_HEADER_PADDING,
         REWARD_HEADER_PADDING,
         REWARD_HEADER_PADDING,
         REWARD_HEADER_PADDING), height=REWARD_HEADER_HEIGHT, contentSpacing=(8, 0))
        self.titleLabel = EveCaptionLarge(parent=ContainerAutoSize(parent=self.headerContainer, align=uiconst.NOALIGN), name='headerLabel', align=uiconst.CENTER, state=uiconst.UI_DISABLED, text=GetByLabel('UI/CareerPortal/YourRewards'))
        self.claimAllBtn = Button(parent=self.headerContainer, uniqueUiName=pConst.UNIQUE_NAME_ACP_CLAIM_ALL_BUTTON, label=GetByLabel('UI/CareerPortal/ClaimAllRewards'), align=uiconst.NOALIGN, func=self.ClaimAll)
        self._UpdateButtonState()

    def _ConstructMainContainer(self):
        self.rewardsScroll = ScrollContainer(name='rewardsScroll', parent=self, align=uiconst.TOALL, padding=(SCROLL_CONTAINER_PADDING,
         0,
         SCROLL_CONTAINER_PADDING,
         0))

    def _ConstructFrame(self):
        Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=eveColor.BLACK, opacity=0.9)

    def _GetEntries(self):
        return self.rewardsScroll.mainCont.children

    def ClaimAll(self, *args):
        self.claimAllBtn.Disable()
        entries = self._GetEntries()
        self.lenRewardsLoading = len(entries)
        for entry in entries:
            entry.ClickClaim()

    @property
    def lenRewardsLoading(self):
        return self._lenRewardsLoading

    @lenRewardsLoading.setter
    def lenRewardsLoading(self, newValue):
        if newValue == 0:
            self.claimAllBtn.Enable()
        self._lenRewardsLoading = newValue

    def ConstructCollapsedView(self):
        self._expanded = False
        self.rewardsScroll.Hide()
        self.claimAllBtn.Hide()

    def ConstructExpandedView(self):
        self._expanded = True
        self.width = EXPANDED_WIDTH
        goals_with_claimable_rewards = get_career_goals_svc().get_goal_data_controller().get_goals_with_claimable_rewards()
        for goal in goals_with_claimable_rewards:
            for reward_label in goal.get_unclaimed_reward_labels():
                self._AddRewardEntry(goal, reward_label, False)

        goals_with_local_claimed_rewards = get_career_goals_svc().get_goal_data_controller().get_local_claimed_rewards()
        for goal_id, reward_labels in goals_with_local_claimed_rewards.iteritems():
            goal = get_career_goals_svc().get_goal_data_controller().get_goal(goal_id)
            if not goal:
                logger.exception('failed to construct a reward entry for goal with claimed rewards, goal_id: %s', goal_id)
                continue
            for reward_label in reward_labels:
                self._AddRewardEntry(goal, reward_label, False)

        self._AdjustHeight()

    def AddClaimableGoal(self, goal_id):
        self._Expand()
        goal = get_career_goals_svc().get_goal_data_controller().get_goal(goal_id)
        if not goal:
            return
        if len(goal.get_unclaimed_rewards()) > 0:
            self.rewardsScroll.HideNoContentHint()
        for reward_label in goal.get_unclaimed_reward_labels():
            self._AddRewardEntry(goal, reward_label, False)

        self._UpdateButtonState()

    def _AddRewardEntry(self, goal, reward_label, move_to_top = True):
        if move_to_top:
            if len(self._GetEntries()) > 0:
                self._GetEntries()[0].top = REWARD_ENTRY_PADDING
        entry = self.get_reward_entry_class(goal, reward_label)(parent=self.rewardsScroll, reward_label=reward_label, goal=goal)
        if move_to_top:
            entry.SetOrder(0)
        else:
            isFirst = entry.GetOrder() == 0
            entry.top = 0 if isFirst else REWARD_ENTRY_PADDING
        self._AdjustHeight()

    def get_reward_entry_class(self, goal, reward_label):
        if get_career_goals_svc().get_goal_data_controller().is_career_path_goal(goal.goal_id, None):
            return GraduationRewardEntry
        if reward_label == RewardLabel.OMEGA:
            return OmegaRewardEntry
        return RewardEntry

    def _AdjustHeight(self):
        if self._expanded:
            newHeight = 78
            entries = self._GetEntries()
            for i, each in enumerate(entries):
                padding = 0 if i == 0 else REWARD_ENTRY_PADDING
                newHeight += each.height + padding

            self.height = min(newHeight + SCROLL_CONTAINER_PADDING, MAX_HEIGHT)
            self.rewardsScroll.padBottom = SCROLL_CONTAINER_PADDING if len(entries) >= 5 else 0
        else:
            self.height = self._collapsedHeight

    def OnRewardClaimed(self, *args):
        self._UpdateButtonState()
        if len(self._GetEntries()) <= 0:
            self._Collapse()
        self.lenRewardsLoading -= 1

    def OnRewardClaimedFailed(self, *args):
        self.lenRewardsLoading -= 1

    def OnClickedOutside(self):
        if self._expanded:
            self._Collapse()

    def OnClick(self, *args):
        if not self._expanded and len(self._GetEntries()) > 0:
            self._Expand()

    def _UpdateButtonState(self):
        self.claimAllBtn.enabled = get_career_goals_svc().get_goal_data_controller().get_claimable_rewards_count() > 0

    def _Expand(self):
        if not self._expanded:
            self._expanded = True
            self.align = uiconst.TOTOP
            self.rewardsScroll.Show()
            self.claimAllBtn.Show()
            animations.MorphScalar(self, 'width', startVal=self.width, endVal=EXPANDED_WIDTH, duration=0.2)
            for entry in self._GetEntries():
                animations.FadeTo(entry, entry.opacity, 1.0, duration=0.2, timeOffset=0.2)

            self._AdjustHeight()

    def _Collapse(self):
        if self._expanded:
            self._expanded = False
            self.align = uiconst.TOPLEFT
            self.rewardsScroll.Hide()
            self.claimAllBtn.Hide()
            width = self._collapsedWidth
            animations.MorphScalar(self, 'width', startVal=self.displayWidth, endVal=width, duration=0.2)
            for entry in self._GetEntries():
                animations.FadeTo(entry, entry.opacity, 0.0, duration=0.2)

            self.height = self._collapsedHeight
