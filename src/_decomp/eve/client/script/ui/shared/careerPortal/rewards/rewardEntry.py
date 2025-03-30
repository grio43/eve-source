#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\rewards\rewardEntry.py
import eveicon
import evetypes
import math
from carbon.common.script.util.format import FmtAmt
from carbonui import ButtonStyle, TextAlign, uiconst
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.section import SubSection
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from carbonui.util.various_unsorted import GetWindowAbove
from careergoals.client.career_goal_svc import get_career_goals_svc
from careergoals.client.const import RewardLabel
from careergoals.client.goal import Goal
from careergoals.client.signal import on_reward_claimed, on_reward_claimed_failed, on_definitions_loaded
from characterdata import careerpath
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveLabelMedium
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.themeColored import LabelThemeColored
from eve.client.script.ui.shared.careerPortal import careerConst
from eve.client.script.ui.shared.careerPortal.rewards.rewardsTooltip import RewardBundleTooltip
from eve.common.lib import appConst
from eveexceptions import ExceptionEater
from inventorycommon.typeHelpers import GetIconFile
from localization import GetByLabel, GetByMessageID
REWARD_ENTRY_HEIGHT = 105
BOTTOM_CONT_HEIGHT = 25
BOTTOM_FRAME_CORNER_SIZE = 9
GRADUATION_REWARD_CORNER_SIZE = 14

class RewardEntry(SubSection):
    default_name = 'RewardEntry'
    default_height = REWARD_ENTRY_HEIGHT
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOTOP
    default_stroked = False
    default_inside_padding = 0
    default_opacity = 0

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        budgetLeft, budgetTop, budgetWidth, budgetHeight, sizeChange = super(RewardEntry, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        self._UpdateTextContainerOpacity()
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight,
         sizeChange)

    def _UpdateTextContainerOpacity(self):
        if self.textContainer.displayWidth < 40:
            self.textContainer.opacity = 0
        else:
            self.textContainer.opacity = 1

    def ApplyAttributes(self, attributes):
        self.goal = attributes.goal
        self.reward_label = attributes.reward_label
        super(RewardEntry, self).ApplyAttributes(attributes)
        self.ConstructLayout()
        self.LoadGoal()
        on_reward_claimed.connect(self.OnRewardClaimed)
        on_reward_claimed_failed.connect(self.OnRewardClaimedFailed)
        on_definitions_loaded.connect(self.LoadGoal)
        wnd = GetWindowAbove(self)
        if wnd:
            wnd.on_end_scale.connect(self.OnWindowEndScale)
        self.AnimEntry()

    def OnWindowEndScale(self, wnd):
        self._UpdateTextContainerOpacity()

    def AnimEntry(self):
        order = self.GetOrder()
        timeOffset = order * 0.2 if order else 0
        animations.FadeIn(self, duration=0.25, timeOffset=timeOffset / 2)
        if self.reward_label not in self.goal.get_unclaimed_reward_labels():
            self.SetClaimedState()

    def Close(self):
        with ExceptionEater('disconnectSignals'):
            on_reward_claimed.disconnect(self.OnRewardClaimed)
            on_reward_claimed_failed.disconnect(self.OnRewardClaimedFailed)
            on_definitions_loaded.disconnect(self.LoadGoal)
        super(RewardEntry, self).Close()

    def _ConstructConts(self):
        self.topCont = Container(name='topCont', parent=self, align=uiconst.TOTOP, height=self.height - BOTTOM_CONT_HEIGHT)
        self.topUiCont = Container(name='topUiCont', parent=self.topCont, align=uiconst.TOALL, left=8)
        self.bottomCont = Container(name='bottomCont', parent=self)

    def _ConstructFrame(self):
        self._ConstructConts()
        self.bottomFrame = Frame(bgParent=self.bottomCont, name='bottomFrame', texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=BOTTOM_FRAME_CORNER_SIZE, color=self.bottom_frame_color, opacity=self.bottom_frame_opacity)
        self.topFillContainer = Container(name='topFillContainer', parent=self.topCont)
        self.construct_top_fill()

    def construct_top_fill(self):
        self.topFill = Fill(bgParent=self.topFillContainer, name='topFill', color=self.top_fill_color, opacity=self.top_fill_opacity)

    def ConstructLayout(self):
        self.loadingWheel = LoadingWheel(parent=self, name='loadingWheel', align=uiconst.CENTER)
        self.loadingFill = Fill(parent=self, name='loadingFill', color=Color.GRAY1, opacity=0.75)
        self.rewardIconCont = Container(parent=self.topUiCont, name='iconCont', align=uiconst.TOLEFT, width=64)
        self.rewardIcon = Sprite(parent=self.rewardIconCont, name='rewardIcon', align=uiconst.CENTER, width=64, height=64, state=uiconst.UI_NORMAL)
        self.claimBtn = Button(parent=ContainerAutoSize(parent=self.topUiCont, align=uiconst.TORIGHT, left=16), name='claimBtn', label=GetByLabel('UI/CareerPortal/ClaimReward'), align=uiconst.CENTERRIGHT, func=self.ClickClaim, style=self.claim_button_style)
        self.textContainer = ScrollContainer(parent=self.topUiCont, name='textCont', align=uiconst.TOALL, padding=(8, 8, 0, 8))
        self.nameLabel = EveCaptionSmall(parent=self.textContainer, name='nameLabel', align=uiconst.TOTOP, textAlign=TextAlign.LEFT, autoFadeSides=True)
        pathCont = Container(parent=self.textContainer, name='pathCont', align=uiconst.TOTOP, top=4, height=16)
        Sprite(parent=pathCont, name='careerIcon', align=uiconst.TOLEFT, width=16, texturePath=careerConst.CAREERS_32_SIZES.get(self.goal.definition.career, ''), hint=careerConst.GetCareerPathName(self.goal.definition.career))
        self.pathLabel = EveLabelMedium(parent=pathCont, name='pathLabel', align=uiconst.TOTOP, left=4)
        self.amountInBundleLabel = LabelThemeColored(parent=self.textContainer, name='amountInBundleLabel', align=uiconst.TOTOP, textAlign=TextAlign.LEFT, top=4)
        EveLabelMedium(parent=self.bottomCont, name='goalName', align=uiconst.CENTERLEFT, text=self.goal.definition.name, left=8)

    def update(self):
        pass

    def LoadGoal(self):
        if not self.goal or not self.reward_label:
            return
        rewards = [ x for x in self.goal.get_unclaimed_rewards() if x.reward_label == self.reward_label ]
        if len(rewards) == 1:
            reward = rewards[0]
            self.rewardIcon.texturePath = GetIconFile(reward.type_id)
            if reward.quantity > 1:
                self.nameLabel.text = '%s %s' % (FmtAmt(reward.quantity), self.GetName(reward.type_id))
            else:
                self.nameLabel.text = self.GetName(reward.type_id)
        else:
            self.rewardIcon.tooltipPanelClassInfo = RewardBundleTooltip(rewards)
            self.rewardIcon.texturePath = careerConst.CRATE_64_SIZES.get(self.goal.definition.career, '')
            self.nameLabel.text = self.GetBundleRewardName()
            self.amountInBundleLabel.text = GetByLabel('UI/CareerPortal/ItemsInRewardBundle', quantity=len(rewards))
        if self.goal.definition.career:
            self.pathLabel.text = self.GetPathLabelText()
        self.update()
        self.loadingFill.Hide()
        self.loadingWheel.Hide()

    def GetName(self, typeID):
        if typeID == appConst.typeKredits:
            return GetByLabel('UI/Common/ISK')
        else:
            return evetypes.GetName(typeID)

    def GetBundleRewardName(self):
        return GetByLabel('UI/CareerPortal/RewardBundle')

    def GetPathLabelText(self):
        return self.goal.definition.career_points_text

    def SetLoadingState(self):
        self.claimBtn.Disable()
        self.loadingFill.Show()
        self.loadingWheel.Show()

    def SetNormalState(self):
        self.claimBtn.Enable()
        self.loadingFill.Hide()
        self.loadingWheel.Hide()

    def SetClaimedState(self):
        self.loadingFill.Show()
        self.loadingWheel.Hide()
        self.claimBtn.SetLabel(GetByLabel('UI/CareerPortal/RewardClaimed'))
        self.claimBtn.Disable()
        self.SetHint(GetByLabel('UI/CareerPortal/CheckRedeemingQueue'))

    def ClickClaim(self, *args):
        if self.reward_label not in self.goal.get_unclaimed_reward_labels() or not self.claimBtn.IsEnabled():
            return
        self.SetLoadingState()
        get_career_goals_svc().claim_reward(self.goal.goal_id, self.reward_label)

    def OnRewardClaimed(self, goal_id, reward_label):
        if goal_id != self.goal.goal_id or self.reward_label != reward_label:
            return
        self.SetClaimedState()

    def OnRewardClaimedFailed(self, goal_id, reward_label):
        if goal_id != self.goal.goal_id or self.reward_label != reward_label:
            return
        self.SetNormalState()

    def OnTimeout(self):
        self.SetNormalState()

    @property
    def top_fill_color(self):
        return eveColor.WHITE

    @property
    def top_fill_opacity(self):
        return 0.05

    @property
    def bottom_frame_color(self):
        return eveColor.WHITE

    @property
    def bottom_frame_opacity(self):
        return 0.1

    @property
    def claim_button_style(self):
        return ButtonStyle.NORMAL


class GraduationRewardEntry(RewardEntry):
    default_name = 'GraduationRewardEntry'

    def __init__(self, *args, **kwargs):
        self.career_color = careerConst.COLOR_BY_CAREER_ID.get(kwargs.get('goal').definition.career)
        super(GraduationRewardEntry, self).__init__(*args, **kwargs)

    def GetBundleRewardName(self):
        return GetByLabel('UI/CareerPortal/GraduationReward')

    def GetPathLabelText(self):
        careerInfo = careerpath.get_career_path(self.goal.definition.career)
        return GetByMessageID(careerInfo.nameID)

    @property
    def top_fill_color(self):
        return self.career_color

    @property
    def top_fill_opacity(self):
        return 0.1

    @property
    def bottom_frame_color(self):
        return self.career_color

    @property
    def bottom_frame_opacity(self):
        return 0.15


class OmegaRewardEntry(RewardEntry):
    __notifyevents__ = ['OnSubscriptionChanged']

    def construct_top_fill(self):
        self.topFillContainer.Flush()
        if not self.has_omega:
            self.construct_top_fill_pattern()
        GradientSprite(name='topFill', bgParent=self.topCont, rgbData=((0.0, eveColor.BLACK[:3]), (1.0, self.top_fill_color[:3])), alphaData=((0.0, 0.0), (self.top_fill_opacity, self.top_fill_opacity)), rotation=math.pi * 0.5)

    def construct_top_fill_pattern(self):
        Sprite(name='topFillPattern', bgParent=self.topFillContainer, texturePath='res:/UI/Texture/Classes/Industry/Output/hatchPattern.png', tileX=True, tileY=True, color=self.top_fill_color, opacity=0.1)

    def update(self):
        self.construct_top_fill()
        if self.has_omega:
            self.textContainer.mainCont.opacity = 1.0
            self.rewardIconCont.opacity = 1.0
            self.claimBtn.label = GetByLabel('UI/CareerPortal/ClaimReward')
            self.claimBtn.texturePath = None
        else:
            self.textContainer.mainCont.opacity = 0.5
            self.rewardIconCont.opacity = 0.5
            self.claimBtn.label = GetByLabel('UI/CloneState/UpgradeToOmega')
            self.claimBtn.texturePath = eveicon.omega

    def ClickClaim(self, *args):
        if not self.has_omega:
            return
        super(OmegaRewardEntry, self).ClickClaim(*args)

    def OnSubscriptionChanged(self):
        self.update()

    @property
    def top_fill_color(self):
        return eveColor.OMEGA_YELLOW

    @property
    def bottom_frame_color(self):
        return eveColor.OMEGA_YELLOW

    @property
    def claim_button_style(self):
        return ButtonStyle.MONETIZATION

    @property
    def has_omega(self):
        return sm.GetService('cloneGradeSvc').IsOmega()
