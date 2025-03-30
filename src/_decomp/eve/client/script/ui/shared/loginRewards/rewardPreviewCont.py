#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\rewardPreviewCont.py
import gametime
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLargeBold
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.eveColor import WHITE
from eve.client.script.ui.shared.loginRewards.congratsCont import TwoTrackCongratsScreen
from eve.client.script.ui.shared.loginRewards.rewardPreviewItemEntry import PreviewItemEntry, TwoTrackPreviewItemEntryAlpha, TwoTrackPreviewItemEntryOmega
from eve.client.script.ui.shared.loginRewards.rewardUiConst import TODAYS_SIDE_PADDING, BLUE_TEXT_COLOR, ONLY_ALPHA_GIFT_REWARDED, ONLY_OMEGA_GIFT_REWARDED
from localization import GetByLabel
from loginrewards.client.tooltips import TooltipButtonTooltip
from loginrewards.common.rewardUtils import GetAnimationTime

class OneTrackRewardPreviewCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.panelController = attributes.panelController
        pConst = self.panelController.GetPanelConstants()
        self.rewardInfo = None
        self.nextRewardTime = None
        self.todaysItem = Container(name='todaysItem', parent=self, align=uiconst.TOALL)
        self.ConstructCountdownCont()
        todaysItemMain = Container(name='todaysItemMain', parent=self.todaysItem, align=uiconst.TOALL, clipChildren=True)
        todaysItemMainWidth = todaysItemMain.absoluteRight - todaysItemMain.absoluteLeft
        self.rewardItemCont = PreviewItemEntry(parent=todaysItemMain, align=uiconst.CENTER, panelController=self.panelController, width=todaysItemMainWidth, top=-20)
        self.countdownThread = AutoTimer(500, self.UpdateCountDown_thread)
        redeemOffset = pConst.VERTICAL_OFFSET + pConst.TODAY_HEIGHT / 2 + 35
        redeemMaxWidth = todaysItemMainWidth - 2 * TODAYS_SIDE_PADDING
        self.redeemingLabel = EveLabelMedium(name='redeemingLabel', parent=todaysItemMain, align=uiconst.CENTER, opacity=0.75, state=uiconst.UI_NORMAL, top=redeemOffset, maxWidth=redeemMaxWidth)
        self.redeemingLabel.display = False
        self.fullOpacity = 0.75

    def ConstructCountdownCont(self):
        pConst = self.panelController.GetPanelConstants()
        if pConst.SHOW_NEXT_GIFT:
            self.countdownCont = Container(name='countdownCont', parent=self.todaysItem, align=uiconst.TOTOP_NOPUSH, height=20)
            self.countdownLabel = EveLabelMedium(parent=self.countdownCont, align=uiconst.TOTOP, top=6, padLeft=TODAYS_SIDE_PADDING + 4, padRight=TODAYS_SIDE_PADDING + 4)
        else:
            self.countdownCont = Container(name='countdownCont', parent=self.todaysItem, align=uiconst.TOTOP_NOPUSH, height=20)
            self.countdownLabel = EveLabelMedium(parent=self.countdownCont, align=uiconst.CENTERTOP, top=6, padLeft=TODAYS_SIDE_PADDING + 4, padRight=TODAYS_SIDE_PADDING + 4)

    def UpdateCountDown_thread(self):
        if not self or self.destroyed:
            self.countdownThread = None
            return
        self._UpdateCountDown()

    def _UpdateCountDown(self):
        now = gametime.GetWallclockTime()
        if not self.nextRewardTime:
            return
        pConst = self.panelController.GetPanelConstants()
        if pConst.SHOW_NEXT_GIFT:
            text = FmtDate(self.nextRewardTime - now, 'ss') if now < self.nextRewardTime else ''
            text = '<center>%s</center>' % text
        else:
            endTime = max(0, self.nextRewardTime - now)
            text = GetByLabel('UI/LoginRewards/NextGiftWithTimer', endTime=endTime, formattingStart='', formattingEnd='')
        self.countdownLabel.text = text
        self.countdownCont.display = bool(now < self.nextRewardTime)

    def LoadRewardInfo(self, rewardInfo, next_reward_time, withTransition = False):
        if withTransition:
            currentTier = self.rewardInfo.tier if self.rewardInfo else None
            sleepTimeSec = GetAnimationTime(currentTier)
            self.FadeElements(fadeIn=False)
            self.rewardItemCont.LoadNewReward(rewardInfo, sleepTimeSec=sleepTimeSec)
            self.FadeElements(fadeIn=True)
        else:
            self.rewardItemCont.LoadRewardInfo(rewardInfo)
        self.rewardInfo = rewardInfo
        self.nextRewardTime = next_reward_time
        self._UpdateCountDown()
        self.UpdateReemLabel()

    def OnClaimBtnClicked(self, *args):
        self.panelController.ClaimReward()

    def Close(self):
        self.countdownThread = None
        Container.Close(self)

    def FadeElements(self, fadeIn = True):
        elementsToFade = [self.redeemingLabel, self.countdownCont]
        for eachElement in elementsToFade:
            if fadeIn:
                endValue = getattr(eachElement, 'fullOpacity', 1.0)
            else:
                endValue = 0
            animations.FadeTo(eachElement, eachElement.opacity, endValue, duration=0.3)

    def UpdateReemLabel(self):
        posInGrid = self.panelController.GetPositionInGridTrack()
        claimedReward = self.panelController.GetClaimedRewardForDay(posInGrid)
        if claimedReward:
            pConst = self.panelController.GetPanelConstants()
            if session.charid:
                linkStart = '<url=localsvc:method=ShowRedeemUI>'
                linkEnd = '</url>'
            else:
                hexColor = Color.RGBtoHex(*BLUE_TEXT_COLOR)
                linkStart = '<color=%s><b>' % hexColor
                linkEnd = '</b></color>'
            text = GetByLabel('UI/LoginRewards/ClaimExplanationText', linkStart=linkStart, linkEnd=linkEnd)
            self.redeemingLabel.text = '<center>%s</center>' % text
            self.redeemingLabel.display = True
            textOffset = self.rewardItemCont.typeText.height + 6 + self.redeemingLabel.height / 2
            redeemOffset = pConst.VERTICAL_OFFSET + pConst.TODAY_HEIGHT / 2 + textOffset + 4
            self.redeemingLabel.top = redeemOffset
        else:
            self.redeemingLabel.display = False


class TwoTrackRewardPreviewCont(Container):

    def ApplyAttributes(self, attributes):
        self.panelController = attributes.panelController
        self.rewardInfo = None
        self.nextRewardTime = None
        Container.ApplyAttributes(self, attributes)
        self.cloneCont = Container(name='cloneCont', parent=self)
        self.congratsCont = TwoTrackCongratsScreen(name='congratsCont', parent=self, panelController=self.panelController, opacity=0.0)
        alphaTrackPar = Container(name='alphaTrackPar', parent=self.cloneCont, align=uiconst.TOTOP_PROP, height=0.5, padding=(0, 4, 0, 4))
        omegaTrackPar = Container(name='omegaTrackPar', parent=self.cloneCont, align=uiconst.TOTOP_PROP, height=0.5, padding=(0, 4, 0, 4))
        self.alphaRewardItemCont = TwoTrackPreviewItemEntryAlpha(parent=alphaTrackPar, align=uiconst.TOALL, rewardInfo=self.rewardInfo, panelController=self.panelController)
        self.omegaRewardItemCont = TwoTrackPreviewItemEntryOmega(parent=omegaTrackPar, align=uiconst.TOALL, rewardInfo=self.rewardInfo, panelController=self.panelController)

    def LoadRewardInfo(self, alphaRewardInfo, omegaRewardInfo, next_reward_time = None, withTransition = False, giftsReceivedConst = None):
        if alphaRewardInfo is None:
            return
        self.nextRewardTime = next_reward_time
        if withTransition:
            if giftsReceivedConst == ONLY_ALPHA_GIFT_REWARDED:
                self.alphaRewardItemCont.LoadNewReward(alphaRewardInfo)
                self.omegaRewardItemCont.LoadNewReward(omegaRewardInfo, playVideo=False)
            elif giftsReceivedConst == ONLY_OMEGA_GIFT_REWARDED:
                self.alphaRewardItemCont.LoadNewReward(alphaRewardInfo, sleepTimeSec=0, playVideo=False)
                self.omegaRewardItemCont.LoadNewReward(omegaRewardInfo)
            else:
                self.alphaRewardItemCont.LoadNewReward(alphaRewardInfo, sleepTimeSec=1, delayedEndSec=1)
                self.omegaRewardItemCont.LoadNewReward(omegaRewardInfo)
        else:
            self.alphaRewardItemCont.LoadRewardInfo(alphaRewardInfo)
            self.omegaRewardItemCont.LoadRewardInfo(omegaRewardInfo)

    def PlayVideosAndFadeOut(self, next_reward_time, withTransition, giftsReceivedConst):
        self.nextRewardTime = next_reward_time
        if withTransition:
            if giftsReceivedConst == ONLY_ALPHA_GIFT_REWARDED:
                self.alphaRewardItemCont.FadeOutAndPlayVideo()
                self.omegaRewardItemCont.FadeOutAndPlayVideo(playVideo=False)
            elif giftsReceivedConst == ONLY_OMEGA_GIFT_REWARDED:
                self.alphaRewardItemCont.FadeOutAndPlayVideo(playVideo=False)
                self.omegaRewardItemCont.FadeOutAndPlayVideo()
            else:
                self.alphaRewardItemCont.FadeOutAndPlayVideo(sleepTimeSec=1)
                self.omegaRewardItemCont.FadeOutAndPlayVideo()
        else:
            self.cloneCont.display = False

    def LoadCompletedScreen(self, withTransition = False):
        if withTransition:
            animations.FadeOut(self.cloneCont, duration=0.2, callback=lambda *args: self.cloneCont.Hide())
        else:
            self.cloneCont.Hide()
        self.congratsCont.opacity = 1.0
        self.congratsCont.LoadCongratsScreen()


class TodaysItemTop(Container):
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.normalHeight = self.height
        self.panelController = attributes.panelController
        self.topDayLabel = EveLabelLargeBold(parent=self, align=uiconst.CENTER, color=WHITE)
        self.helpIcon = MoreInfoIcon(parent=self, align=uiconst.CENTERRIGHT, left=4)
        self.SetupHelpIcon()
        self.next_reward_time = None

    def SetupHelpIcon(self):
        self.helpIcon.hint = GetByLabel('UI/LoginRewards/ItemHelpIcon')

    def UpdateTextAndHelpIcon(self, next_reward_time):
        self.next_reward_time = next_reward_time
        if next_reward_time is None:
            text = GetByLabel('UI/LoginRewards/CampaignCompletedHeader')
            helpIconDisplayState = False
        else:
            helpIconDisplayState = True
            pConst = self.panelController.GetPanelConstants()
            now = gametime.GetWallclockTime()
            if not pConst.SHOW_NEXT_GIFT or now > next_reward_time:
                text = GetByLabel('UI/LoginRewards/TodaysGift')
            else:
                text = GetByLabel('UI/LoginRewards/NextGift')
        self.helpIcon.display = helpIconDisplayState
        self.SetTopDayLabel(text)

    def SetTopDayLabel(self, text):
        if '<br>' in text:
            self.topDayLabel.align = uiconst.TOTOP
            self.topDayLabel.text = '<center>%s</center>' % text
            self.topDayLabel.padTop = 2
            self.height = max(self.height, self.topDayLabel.textheight + 2 * self.topDayLabel.padTop)
        else:
            self.topDayLabel.aign = uiconst.CENTER
            self.topDayLabel.padTop = 0
            self.topDayLabel.text = text
            self.height = self.normalHeight


class TwoTrackTodaysItemTop(TodaysItemTop):

    def ApplyAttributes(self, attributes):
        TodaysItemTop.ApplyAttributes(self, attributes)
        self.countdownThread = None

    def SetupHelpIcon(self):
        self.helpIcon.GetTooltipHeader = lambda *args: GetByLabel('UI/LoginRewards/Tooltips/TooltipButtonTooltipHeader')
        self.helpIcon.GetTooltipDesc = lambda *args: GetByLabel('UI/LoginRewards/Tooltips/TooltipButtonTooltipBody')
        self.helpIcon.GetTooltipTexturePath = lambda *args: 'res:/UI/Texture/WindowIcons/gift.png'
        self.helpIcon.tooltipPanelClassInfo = TooltipButtonTooltip()

    def UpdateTextAndHelpIcon(self, nextRewardTime):
        now = gametime.GetWallclockTime()
        isCampaignEnding = self.panelController.IsCampaignEndingBeforeNextReward()
        isCampaignCompleted = self.panelController.HasActiveCampaignBeenCompleted()
        if isCampaignCompleted:
            self.SetTopDayLabel(GetByLabel('UI/LoginRewards/CampaignCompletedHeader'))
            self.helpIcon.display = False
        elif isCampaignEnding:
            self.helpIcon.display = False
            self.StartCountDown('UI/LoginRewards/CampaignEndsHeader', nextRewardTime)
        else:
            if nextRewardTime is None or now > nextRewardTime:
                return TodaysItemTop.UpdateTextAndHelpIcon(self, nextRewardTime)
            self.StartCountDown('UI/LoginRewards/NextGiftWithTimer', nextRewardTime)
            self.helpIcon.display = True

    def StartCountDown(self, labelPath, nextRewardTime):
        text = self.GetCountdownTextToDisplay(labelPath, nextRewardTime)
        self.SetTopDayLabel(text)
        self.countdownThread = AutoTimer(500, self.UpdateCountDown_thread, labelPath, nextRewardTime)

    def UpdateCountDown_thread(self, labelPath, nextRewardTime):
        if not self or self.destroyed:
            self.countdownThread = None
            return
        self._UpdateCountDown(labelPath, nextRewardTime)

    def _UpdateCountDown(self, labelPath, nextRewardTime):
        text = self.GetCountdownTextToDisplay(labelPath, nextRewardTime)
        self.SetTopDayLabel(text)

    def GetCountdownTextToDisplay(self, labelPath, nextRewardTime):
        if nextRewardTime is None:
            return ''
        endTime = max(0, nextRewardTime - gametime.GetWallclockTime())
        text = GetByLabel(labelPath, endTime=endTime, formattingStart='<color=white>', formattingEnd='</color>')
        w, h = self.topDayLabel.MeasureTextSize(text, maxlines=1)
        if w > self.absoluteRight - self.absoluteLeft:
            text = GetByLabel(labelPath, endTime=endTime, formattingStart='<color=white>', formattingEnd='</color>', optionalLinebreak='<br>')
        return text

    def Close(self):
        self.countdownThread = None
        Container.Close(self)
