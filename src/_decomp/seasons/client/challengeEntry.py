#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\client\challengeEntry.py
import evetypes
import localization
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
import carbonui.const as uiconst
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbon.common.script.util.format import FmtAmt
from carbon.common.script.util.timerstuff import AutoTimer
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium, EveLabelMediumBold, EveLabelSmall
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.client.script.ui.control.eveIcon import Icon
from gametime import GetSimTime
from localization.formatters import FormatTimeIntervalShortWritten
from seasons.client.const import SEASONS_CLAIM_REWARD_LABEL
from seasons.client.challengetaskprogressbar import ChallengeTaskProgressBar
from seasons.client.uiutils import SEASON_THEME_TEXT_COLOR_REGULAR
from seasons.common.const import REWARD_FANFARE_SOUND
ENTRY_WIDTH = 290
PADDING_LEFT = 6
PROGRESS_BAR_TOP = 6
PROGRESS_BAR_BOTTOM = 12
REWARD_ICON_SIZE = 48
REWARD_CONTAINER_HEIGHT = 76
COLOR_EXPIRY_TIMER = (0.6, 0.6, 0.6, 1.0)
TOOLTIP_TEXT_WIDTH = 200
TOOLTIP_REWARD_ICON_SIZE = 64

class RewardTooltip(TooltipBaseWrapper):

    def __init__(self, typeID, amount):
        super(RewardTooltip, self).__init__()
        self.typeID = typeID
        self.amount = amount

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.state = uiconst.UI_NORMAL
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        iconContainer = ContainerAutoSize(parent=self.tooltipPanel)
        Icon(parent=iconContainer, name='categorySprite', icon=evetypes.GetIconID(self.typeID), width=TOOLTIP_REWARD_ICON_SIZE, height=TOOLTIP_REWARD_ICON_SIZE, align=uiconst.TOPLEFT)
        self.tooltipPanel.icon = iconContainer
        textContainer = Container(align=uiconst.TOPRIGHT)
        nameLabel = EveLabelMediumBold(parent=textContainer, text=evetypes.GetName(self.typeID), align=uiconst.TOTOP, wrapWidth=TOOLTIP_TEXT_WIDTH)
        descriptionLabel = EveLabelSmall(parent=textContainer, text=evetypes.GetDescription(self.typeID), align=uiconst.TOTOP, wrapWidth=TOOLTIP_TEXT_WIDTH)
        textContainer.width = TOOLTIP_TEXT_WIDTH
        descriptionLabel.ResolveAutoSizing()
        descriptionLabel.Layout()
        textContainer.height = nameLabel.height + descriptionLabel.height
        self.tooltipPanel.AddCell(cellObject=textContainer)
        self.tooltipPanel.icon.width = textContainer.height
        self.tooltipPanel.icon.height = textContainer.height
        return self.tooltipPanel


def OnMouseNoLongerInEntry(self):
    self.KillHilite()


class ChallengeEntry(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    onMouseEnterThread = None

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.seasonService = sm.GetService('seasonService')
        self.challenge = attributes.challenge
        self.challengeWidth = attributes.challengeWidth
        reward_count = self.get_challenge_reward_type_count()
        self.challengeExpiryLabel = None
        self.claim_button_container = None
        self.leftCont = ContainerAutoSize(name='dataContainer', parent=self, align=uiconst.TOPLEFT, width=475 + (3 - reward_count) * 64, padRight=0)
        self.rewardCont = Container(name='rewardCont', parent=self, align=uiconst.TOPLEFT, padLeft=self.leftCont.width + 20, width=64 * reward_count, height=REWARD_CONTAINER_HEIGHT, padRight=-self.leftCont.width - 20)
        self.DrawProgress()
        self.DrawClaimButton()
        self.DrawChallengeExpiry()
        self.DrawChallengeText()
        self.DrawRewards()
        self.CorrectLayout()
        animations.FadeIn(self)

    def DrawProgress(self):
        heightBar = 5
        self.progressContainer = Container(name='progress_bar_container', parent=self.leftCont, align=uiconst.TOBOTTOM, height=heightBar, padding=(PADDING_LEFT,
         PROGRESS_BAR_TOP,
         6,
         PROGRESS_BAR_BOTTOM))
        progressBarWidth = self.challengeWidth - 10
        progressFrameWidthOffset = 16
        self.progressBar = ChallengeTaskProgressBar(name='progress_bar', parent=self.progressContainer, align=uiconst.TOLEFT, challenge=self.challenge, progress_frame_width=progressBarWidth, height=heightBar, progress_frame_width_offset=progressFrameWidthOffset, animate_progress=True, width=progressBarWidth - progressFrameWidthOffset, label_type_function=EveLabelSmall, adapt_text_color_to_progress=True, bgColor=(1, 1, 1, 0.1), padRight=6)
        self.heightProgressBar = PROGRESS_BAR_TOP + heightBar + PROGRESS_BAR_BOTTOM

    def DrawClaimButton(self):
        if self.claim_button_container is None:
            self.claim_button_container = Container(name='claim_button_cont', parent=self.leftCont, width=150, height=0, align=uiconst.TOBOTTOM, left=PADDING_LEFT)
        if self.challenge.is_progress_complete():
            self.claim_button_container.height = 25
            self.claim_button = Button(name='claim_button', parent=self.claim_button_container, label=localization.GetByLabel(SEASONS_CLAIM_REWARD_LABEL), align=uiconst.CENTERLEFT, func=self.claim_button_clicked)
        self.heightClaimButton = self.claim_button_container.height

    def DrawChallengeExpiry(self):
        self.heightExpiry = 0
        if self.challenge.expiration_minutes > 0 and not self.challenge.is_progress_complete():
            top = 4
            challengeExpiryCont = ContainerAutoSize(name='challenge_expiry_container', parent=self.leftCont, align=uiconst.TOBOTTOM)
            self.expiration_date = self.seasonService.get_challenge_expiration_date(self.challenge.challenge_id)
            self.challengeExpiryLabel = EveLabelMedium(parent=challengeExpiryCont, align=uiconst.TOPLEFT, text='', top=top, maxLines=1, width=self.width, height=20, left=PADDING_LEFT)
            self.challengeExpiryLabel.SetTextColor(COLOR_EXPIRY_TIMER)
            self.expiryTimer = AutoTimer(500, self.UpdateTimerLabel)
            self.heightExpiry = top + self.challengeExpiryLabel.height

    def DrawChallengeText(self):
        top = 8
        challengeInfoCont = ContainerAutoSize(name='challenge_info_container', parent=self.leftCont, align=uiconst.TOBOTTOM)
        self.descriptionLabel = EveLabelLarge(name='challenge_description', parent=challengeInfoCont, state=uiconst.UI_NORMAL, left=PADDING_LEFT, align=uiconst.TOPLEFT, top=top, wrapMode=uiconst.WRAPMODE_FORCEWORD, maxWidth=self.leftCont.width)
        self.descriptionLabel.color = SEASON_THEME_TEXT_COLOR_REGULAR
        self.descriptionLabel.text = localization.GetByMessageID(self.challenge.message_text)
        self.heightDescription = top + self.descriptionLabel.height

    def UpdateTimerLabel(self):
        if not self.challengeExpiryLabel:
            return
        if self.challenge.is_progress_complete():
            self.challengeExpiryLabel.Hide()
            self.expiryTimer = None
            self.heightExpiry = 0
        if self.expiration_date is not None:
            nextChallengeTime = FormatTimeIntervalShortWritten(max(self.expiration_date - GetSimTime(), 0))
            self.challengeExpiryLabel.text = nextChallengeTime

    def UpdateClaimButton(self):
        self.UpdateTimerLabel()
        self.DrawClaimButton()
        self.CorrectLayout()

    def DrawRewards(self):
        if not self.challenge.has_completion_rewards():
            return
        if self.challenge.points_awarded > 0:
            self.create_point_reward()
        if self.challenge.isk_awarded > 0:
            self.create_isk_reward()
        if self.challenge.reward_type is not None:
            self.create_type_reward()

    def get_challenge_reward_type_count(self):
        count = 0
        if self.challenge.isk_awarded > 0:
            count += 1
        if self.challenge.points_awarded > 0:
            count += 1
        if self.challenge.reward_type and self.challenge.reward_amount:
            count += 1
        return count

    def create_isk_reward(self):
        iskCont = Container(name='reward_isk_container', parent=self.rewardCont, align=uiconst.TORIGHT, height=REWARD_ICON_SIZE, width=64, padTop=5)
        rewardIconContainer = self._create_reward_container(iskCont)
        isk_label_container = Container(name='reward_isk_label_container', parent=iskCont, align=uiconst.TOTOP, width=65, height=20, left=0)
        self.isk_label = EveLabelSmall(name='reward_isk_label', text='', parent=isk_label_container, align=uiconst.CENTER)
        Sprite(name='reward_isk_icon', parent=rewardIconContainer, align=uiconst.CENTER, width=REWARD_ICON_SIZE, height=REWARD_ICON_SIZE, texturePath='res:/ui/Texture/WindowIcons/wallet.png', hint=localization.GetByLabel('UI/Agency/Seasons/IskRewardToolTip', amount=self.challenge.isk_awarded))
        self.isk_label.text = FmtAmt(self.challenge.isk_awarded)

    def create_type_reward(self):
        rewardTypeCont = Container(name='reward_item_container', parent=self.rewardCont, align=uiconst.TORIGHT, width=64, padTop=5)
        rewardIconContainer = self._create_reward_container(rewardTypeCont)
        rewardTypeSprite = Sprite(parent=rewardIconContainer, align=uiconst.CENTER, width=REWARD_ICON_SIZE, height=REWARD_ICON_SIZE)
        sm.GetService('photo').GetIconByType(rewardTypeSprite, self.challenge.reward_type)
        labelCont = Container(name='reward_item_label', parent=rewardTypeCont, height=18, align=uiconst.TOTOP)
        label = EveLabelSmall(parent=labelCont, text=localization.GetByLabel('UI/Seasons/RewardAmount', rewardAmount=localization.formatters.FormatNumeric(self.challenge.reward_amount, useGrouping=True)), align=uiconst.CENTER)
        labelCont.width = label.width
        rewardTypeSprite.tooltipPanelClassInfo = RewardTooltip(typeID=self.challenge.reward_type, amount=self.challenge.reward_amount)

    def _create_reward_container(self, rewardTypeCont):
        rewardIconContainerParent = Container(parent=rewardTypeCont, align=uiconst.TOTOP, height=REWARD_ICON_SIZE)
        rewardIconContainer = Container(parent=rewardIconContainerParent, align=uiconst.CENTERTOP, width=REWARD_ICON_SIZE, height=REWARD_ICON_SIZE, bgColor=(0.0, 0.0, 0.0, 0.5))
        Frame(parent=rewardIconContainer, cornerSize=9, color=(1.0, 1.0, 1.0, 0.25))
        return rewardIconContainer

    def create_point_reward(self):
        pointsCont = Container(name='reward_points_container', parent=self.rewardCont, align=uiconst.TORIGHT, height=REWARD_ICON_SIZE, width=64, padTop=5)
        rewardIconContainer = self._create_reward_container(pointsCont)
        points = self.challenge.points_awarded
        Sprite(parent=rewardIconContainer, align=uiconst.CENTER, width=REWARD_ICON_SIZE, height=REWARD_ICON_SIZE, texturePath='res:/UI/Texture/classes/Seasons/eventIcon_64x64.png', hint=localization.GetByLabel('UI/Agency/Seasons/PointRewardTooltip', points=points))
        labelCont = Container(name='reward_points_label', parent=pointsCont, height=18, align=uiconst.TOTOP)
        EveLabelSmall(parent=labelCont, text=localization.formatters.FormatNumeric(self.challenge.points_awarded, useGrouping=True), align=uiconst.CENTER)

    def UpdateChallengeProgress(self, newProgress):
        if hasattr(self, 'progressBar'):
            self.progressBar.update_challenge(newProgress)

    def CompleteChallenge(self):
        if hasattr(self, 'progressBar'):
            self.progressBar.update_challenge(self.challenge.max_progress)

    def _OnClose(self, *args):
        self.expiryTimer = None

    def claim_button_clicked(self, *args):
        self.seasonService.claim_challenge_rewards(self.challenge, 'Challenge Card')
        PlaySound(REWARD_FANFARE_SOUND)

    def GetHeight(self):
        self.UpdateAlignment()
        return max(self.leftCont.height, REWARD_CONTAINER_HEIGHT)

    def CorrectLayout(self):
        left_height = self.heightDescription + self.heightExpiry + self.heightClaimButton + self.heightProgressBar
        excessHeight = REWARD_CONTAINER_HEIGHT - left_height
        self.progressContainer.padTop = max(excessHeight, PROGRESS_BAR_TOP)
