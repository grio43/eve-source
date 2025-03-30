#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\loginrewards\client\rewardclaimfanfare.py
import evetypes
import trinity
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.uicore import uicore
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from clonegrade import COLOR_OMEGA_ORANGE
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelSmall, Label, EveLabelMedium
from eve.client.script.ui.shared.cloneGrade import ORIGIN_SEASONALREWARDS
from eve.client.script.ui.shared.cloneGrade.omegaCloneOverlayIcon import OmegaCloneOverlayIcon
from localization import GetByLabel
from redeem import get_redeem_data
from uthread2 import call_after_wallclocktime_delay
REWARD_CONTAINER_WIDTH = 160
REWARD_CONTAINER_HEIGHT = 200
COLOR_OMEGA_SELECTED = (0.49, 0.35, 0.12)
CLOSE_TIMER_SECONDS = 4
MAIN_CONT_PADDING = 2
REWARD_HEADER_HEIGHT = 25
REWARD_FOOTER_HEIGHT = 40
CENTER_HEXAGON_PATH = 'res:/UI/Texture/classes/LoginCampaign/centerHexagon.png'
CENTER_CIRCLE_PATH = 'res:/UI/Texture/classes/LoginCampaign/centerCircle.png'
ALPHA_FRAME_PATH = 'res:/UI/Texture/classes/LoginCampaign/alphaFrame.png'
ALPHA_MILESTONE_FRAME_PATH = 'res:/UI/Texture/classes/LoginCampaign/alphaMilestone_frame.png'
OMEGA_FRAME_PATH = 'res:/UI/Texture/classes/LoginCampaign/omegaFrame.png'
OMEGA_MILESTONE_FRAME_PATH = 'res:/UI/Texture/classes/LoginCampaign/omegaMilestone_frame.png'

class RewardFanfare(Container):
    default_bgColor = (0.05, 0.05, 0.05, 0.85)
    default_frameColor = (0.0, 0.0, 0.0)
    default_clipChildren = True
    default_name = 'RewardFanfare'
    default_windowID = 'RewardFanfare'
    default_width = 920
    default_height = 610
    default_minSize = (920, 610)
    default_maxSize = (920, 610)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.mouseCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp)
        call_after_wallclocktime_delay(self.AnimateClose, CLOSE_TIMER_SECONDS)
        self.rewards = attributes.rewards
        self.reward_count = len(self.rewards)
        is_login_reward = attributes.isLoginReward
        self.mainCont = Container(name='mainCont', align=uiconst.CENTER, parent=self, height=self.height, width=self.width, padding=(MAIN_CONT_PADDING,
         0,
         MAIN_CONT_PADDING,
         MAIN_CONT_PADDING), padTop=-20, padBottom=20, clipChildren=True)
        if is_login_reward:
            self.todaysRewardLabel = EveLabelMedium(parent=self, text=GetByLabel('UI/LoginRewards/TodaysRewards'), align=uiconst.CENTER, padTop=-110, padBottom=110, idx=0, color=(1, 1, 1, 0.85))
        self.rewardContainer = ContainerAutoSize(parent=self.mainCont, width=self.reward_count * REWARD_CONTAINER_WIDTH, height=REWARD_CONTAINER_HEIGHT, align=uiconst.CENTER)
        for reward in self.rewards:
            if reward.isOmegaOnly:
                frameResPath = OMEGA_FRAME_PATH if reward.tier < 2 else OMEGA_MILESTONE_FRAME_PATH
            else:
                frameResPath = ALPHA_FRAME_PATH if reward.tier < 2 else ALPHA_MILESTONE_FRAME_PATH
            RewardItem(parent=self.rewardContainer, width=160, state=uiconst.UI_DISABLED, align=uiconst.TOLEFT, padding=8, reward=reward, frame=frameResPath, showOmegaFrame=reward.isOmegaOnly)

        self.splashLoop = StreamingVideoSprite(parent=self, videoPath='res:/UI/Texture/classes/ItemPacks/SplashBGLoop.webm', width=1250, height=450, align=uiconst.CENTER, state=uiconst.UI_DISABLED, spriteEffect=trinity.TR2_SFX_COPY, blendMode=trinity.TR2_SBM_ADDX2, disableAudio=True, videoLoop=True, padTop=15, padBottom=-15)
        additionalRewards = attributes.Get('additionalRewards', [])
        additionalRewardCount = len(additionalRewards)
        if additionalRewardCount == 0:
            rows = 0
            columns = 0
            width = 0
            height = 0
        elif additionalRewardCount <= 5:
            rows = 1
            columns = additionalRewardCount
            height = rows * 64
            width = columns * 64 + 5 * (columns - 1)
        else:
            rows = 2
            columns = (min(10, additionalRewardCount) + 1) / 2
            height = rows * 64 + 5
            width = columns * 64 + 5 * (columns - 1)
        self.retroContainer = GridContainer(parent=self, align=uiconst.CENTER, width=width, height=height, padTop=100, padBottom=-100, columns=columns, rows=rows)
        rewardsToDisplay = additionalRewards[:10]
        for reward in rewardsToDisplay:
            additionalRewardContainer = Container(parent=self.retroContainer, bgColor=(0, 0, 0, 0.4), align=uiconst.TOALL, padding=5)
            icon = Sprite(parent=additionalRewardContainer, name='reward_icon', width=38, height=38, align=uiconst.CENTER)
            sm.GetService('photo').GetIconByType(icon, reward.typeID)
            Frame(frameConst=uiconst.FRAME_BORDER1_SHADOW_CORNER0, parent=additionalRewardContainer, color=COLOR_OMEGA_SELECTED, state=uiconst.UI_DISABLED, idx=0, cornerSize=50)
            fadedOmegaColor = (COLOR_OMEGA_ORANGE[0],
             COLOR_OMEGA_ORANGE[1],
             COLOR_OMEGA_ORANGE[2],
             0.2)
            lessFadedOmegaColor = (COLOR_OMEGA_ORANGE[0],
             COLOR_OMEGA_ORANGE[1],
             COLOR_OMEGA_ORANGE[2],
             0.8)
            yellowCrossContainer = Container(parent=additionalRewardContainer, align=uiconst.TOPLEFT, width=16, height=16, bgColor=fadedOmegaColor, idx=1)
            Sprite(parent=yellowCrossContainer, texturePath='res:/UI/Texture/Icons/Plus.png', align=uiconst.CENTER, width=8, height=8, state=uiconst.UI_DISABLED, color=lessFadedOmegaColor, idx=0)

        self.retroLabel = None
        retroLabelHeight = 0
        if len(additionalRewards) > 0:
            if len(additionalRewards) > 5:
                pushDown = 20
            else:
                pushDown = 52
            self.retroLabel = EveLabelMedium(parent=self, text=GetByLabel('UI/LoginRewards/OmegaUpgradeRewards'), align=uiconst.CENTER, padTop=pushDown, padBottom=-pushDown, idx=0, color=(1, 1, 1, 0.85))
            retroLabelHeight = self.retroLabel.height
        self.additionalRetroLabel = None
        undisplayedRewards = max(0, len(additionalRewards) - 10)
        if undisplayedRewards:
            self.additionalRetroLabel = EveLabelMediumBold(parent=self, text=GetByLabel('UI/LoginRewards/RetroCount', count=undisplayedRewards), align=uiconst.CENTER, padTop=100, padBottom=-100, idx=0, color=(1, 1, 1, 0.85))
        self.itemsToRedeemHint = EveLabelSmall(parent=self, text=self.get_redeem_hint_text(reward, is_login_reward), align=uiconst.CENTER, padTop=120, padBottom=-150, idx=0, color=(1, 1, 1, 0.85))
        squeezeUpAmount = self.retroContainer.height / 2 + retroLabelHeight * 2
        if is_login_reward:
            self.todaysRewardLabel.padTop -= squeezeUpAmount
            self.todaysRewardLabel.padBottom += squeezeUpAmount
        self.rewardContainer.padTop -= squeezeUpAmount
        self.rewardContainer.padBottom += squeezeUpAmount
        self.splashLoop.padTop -= squeezeUpAmount
        self.splashLoop.padBottom += squeezeUpAmount
        squeezeDownAmount = self.retroContainer.height / 2
        self.itemsToRedeemHint.padTop += squeezeDownAmount
        self.itemsToRedeemHint.padBottom -= squeezeDownAmount
        if self.additionalRetroLabel is not None:
            self.additionalRetroLabel.padTop += squeezeDownAmount + self.additionalRetroLabel.height
            self.additionalRetroLabel.padBottom -= squeezeDownAmount + self.additionalRetroLabel.height
            self.itemsToRedeemHint.padTop += self.additionalRetroLabel.height
            self.itemsToRedeemHint.padBottom -= self.additionalRetroLabel.height

    def get_redeem_hint_text(self, reward, is_login_reward):
        if not is_login_reward:
            if get_redeem_data().is_skill_inserter(reward['typeID']):
                return GetByLabel('UI/Seasons/ChallengeRewardSkillPointClaim')
        if self.reward_count > 1:
            return GetByLabel('UI/LoginRewards/ItemsToRedeemHint')
        else:
            return GetByLabel('UI/LoginRewards/ItemToRedeemHint')

    def OnGlobalMouseUp(self, *args, **kwargs):
        self.AnimateClose()
        return 1

    def AnimateClose(self):
        if self and not self.destroyed:
            uicore.animations.FadeOut(self, duration=0.25, callback=self.Close)

    def _OnClose(self, *args, **kwargs):
        uicore.event.UnregisterForTriuiEvents(self.mouseCookie)


class RewardItem(Container):
    default_bgColor = (0.05, 0.05, 0.05, 0.65)
    default_frameColor = (0.3, 0.3, 0.3)
    default_clipChildren = True
    default_name = 'RewardFanfare'
    default_windowID = 'RewardFanfare'
    default_width = 1000
    default_height = 610
    default_minSize = (1000, 610)
    default_maxSize = (1000, 610)
    default_isStackable = False
    default_captionLabelPath = 'UI/LoginRewards/WindowCaption'
    default_descriptionLabelPath = 'UI/LoginRewards/WindowDescription'
    default_showOmegaFrame = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.reward = attributes.reward
        frameColor = attributes.get('frameColor', self.default_frameColor)
        showOmegaFrame = attributes.get('showOmegaFrame', self.default_showOmegaFrame)
        frameResPath = attributes.frame
        Frame(frameConst=uiconst.FRAME_BORDER1_SHADOW_CORNER0, parent=self, color=frameColor, state=uiconst.UI_DISABLED, idx=0, cornerSize=50)
        if showOmegaFrame:
            OmegaCloneOverlayIcon(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, origin=ORIGIN_SEASONALREWARDS, reason=self.reward.typeID, idx=0)
        self.icon = Sprite(parent=self, name='reward_icon', width=76, height=76, padBottom=15, padTop=-15, align=uiconst.CENTER)
        sm.GetService('photo').GetIconByType(self.icon, self.reward.typeID)
        if self.reward.quantity > 1:
            self.quantityContainer = Container(parent=self, name='quantityContainer', idx=0, pos=(1, 52, 60, 24), align=uiconst.BOTTOMRIGHT, state=uiconst.UI_DISABLED, bgColor=(0, 0, 0, 0.95))
            self.quantityLabel = Label(parent=self.quantityContainer, left=10, maxLines=1, fontsize=14, color=(0.9, 0.9, 0.9), text=FmtAmt(self.reward.quantity), align=uiconst.CENTERLEFT)
            if self.quantityLabel.width + 20 > self.quantityContainer.width:
                self.quantityContainer.width = self.quantityLabel.width + 20
        spriteSize = 148
        spritePad = 15
        Sprite(parent=self, texturePath=frameResPath, width=spriteSize, height=spriteSize, padBottom=spritePad, padTop=-spritePad, align=uiconst.CENTER)
        Sprite(parent=self, texturePath=CENTER_HEXAGON_PATH, width=spriteSize, height=spriteSize, padBottom=spritePad, padTop=-spritePad, align=uiconst.CENTER)
        Sprite(parent=self, texturePath=CENTER_CIRCLE_PATH, width=spriteSize, height=spriteSize, padBottom=spritePad, padTop=-spritePad, align=uiconst.CENTER)
        self.footerContainer = Container(parent=self, height=REWARD_FOOTER_HEIGHT + 10, align=uiconst.TOBOTTOM)
        self.nameLabel = EveLabelMediumBold(parent=self.footerContainer, text='<center>%s</center>' % evetypes.GetName(self.reward.typeID), align=uiconst.CENTER, width=REWARD_CONTAINER_WIDTH - 15, idx=0)
