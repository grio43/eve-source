#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\reminderCont.py
import gametime
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelMediumBold
from eve.client.script.ui.shared.loginRewards.panelControllers import SeasonalPanelController, LoginCampaignController
from eve.client.script.ui.shared.loginRewards.rewardItemsGrid import RewardItemsGrid
from eve.client.script.ui.shared.loginRewards.rewardPreviewItemEntry import TwoTrackPreviewItemEntryOmega, TwoTrackPreviewItemEntryAlpha, ReminderPreviewItemEntry
from carbonui import uiconst
from eve.client.script.ui.shared.loginRewards.rewardUiConst import ALPHA_SEASONAL_ENTRY, OMEGA_SEASONAL_ENTRY, BLUE_TEXT_COLOR, ReminderRewardPanelConst
from eve.client.script.ui.shared.loginRewards.twoTrackRewardPanel import GetGiftsReceivedConst
from eveui import ButtonIcon
from localization import GetByLabel, GetByMessageID
import eve.client.script.ui.shared.loginRewards.rewardUiConst as rewardUiConst
from loginrewards.common.const import CLAIM_STATE_CLAIMABLE
from utillib import KeyVal
ENTRY_WIDTH = 270
ENTRY_DIVIDER = 18
animationDelay = 2.0

class ReminderCont(ContainerAutoSize):
    default_alignMode = uiconst.TOTOP
    default_height = 350
    __notifyevents__ = ['OnRewardReminderClaimed', 'OnDailyRewardClaimed']

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        animations.FadeTo(self, duration=0.3)
        parentWidth = attributes.parentWidth
        self.loginRewardSvc = sm.GetService('loginCampaignService')
        self.grid = None
        self.currentIdx = 0
        sidePadding = 10
        self.headerText = EveLabelMedium(parent=self, align=uiconst.TOTOP)
        self.entryCont = ContainerAutoSize(name='entryCont', parent=self, align=uiconst.TOTOP, height=250, clipChildren=True, padding=4, alignMode=uiconst.TOTOP)
        self.breadcrumbsParent = Container(name='breadcrumbsParent', parent=self.entryCont, align=uiconst.TOTOP, height=20)
        self.fullWidth = parentWidth - self.entryCont.padLeft - self.entryCont.padRight
        self.AddBrowseBtns()
        self.Load()
        sm.RegisterNotify(self)

    def Load(self):
        self.UpdateHeaderText()
        rewardsData = self.loginRewardSvc.get_next_rewards_to_claim_both_campaigns()
        rewardDataWithRewardInfo = [ x for x in rewardsData if x.rewardInfo is not None ]
        numToDisplay = len(rewardDataWithRewardInfo)
        gridParent = ContainerAutoSize(name='gridParent', parent=self.entryCont, align=uiconst.TOTOP, height=180)
        self.breadcrumbsParent.display = len(rewardDataWithRewardInfo) > 1
        self.breadcrumbsParent.Flush()
        breadcrumbsPadding = (self.fullWidth - ReminderRewardPanelConst.ENTRY_WIDTH) / 2 + ReminderRewardPanelConst.ENTRY_SIDE_PADDING
        self.breadcrumbsCont = BreadcrumbCont(parent=self.breadcrumbsParent, align=uiconst.TOBOTTOM, numRewards=len(rewardDataWithRewardInfo), padLeft=breadcrumbsPadding)
        self.grid = RewardItemsGrid(name='rewardGrid', parent=gridParent, align=uiconst.CENTERLEFT, columns=numToDisplay, numAllEntries=numToDisplay, panelConst=ReminderRewardPanelConst, offset=int((self.fullWidth - ReminderRewardPanelConst.ENTRY_WIDTH) / 2.0))
        entryInfoForGrid = []
        firstClaimable = None
        for i, eachReward in enumerate(rewardDataWithRewardInfo):
            if eachReward.rewardInfo.claimState == CLAIM_STATE_CLAIMABLE and firstClaimable is None:
                firstClaimable = i
            contClass, _ = GetContAndEntryClassFromType(eachReward.entryType)
            entryInfoForGrid.append({'entryClass': contClass,
             'rewardData': eachReward,
             'contIdx': i})

        self.grid.LoadEntries(entryInfoForGrid)
        self.SetCurrentSelectedAndUpdateUI(firstClaimable or 0, 0)
        self.grid.UpdateEntryState(self.currentIdx, KeyVal(fadeTime=0))

    def UpdateHeaderText(self):
        rewardsData = self.loginRewardSvc.get_next_rewards_to_claim_both_campaigns()
        rewardInfos = [ x.rewardInfo for x in rewardsData if x.rewardInfo is not None ]
        numCanClaimNow = len([ x for x in rewardInfos if x.claimState == CLAIM_STATE_CLAIMABLE ])
        if not numCanClaimNow:
            self.headerText.opacity = 0.0
        else:
            self.headerText.opacity = 1.0
            self.headerText.display = True
            text = GetByLabel('UI/LoginRewards/NumUnclaimedItems', numItems=numCanClaimNow)
            self.headerText.text = '<center><b>%s</b></center>' % text

    def MoveToNextClaimable(self):
        nextClaimable = None
        entries = self.grid.entries.items()
        entries = sorted(entries, key=lambda x: x[0])
        for i, entry in entries:
            if entry.rewardItemCont.currentRewardInfo is None:
                continue
            if entry.rewardItemCont.currentRewardInfo.claimState == CLAIM_STATE_CLAIMABLE:
                nextClaimable = i
                break

        nextClaimable = nextClaimable or self.currentIdx
        self.SetCurrentSelectedAndUpdateUI(nextClaimable, 0.5)

    def SetCurrentSelectedAndUpdateUI(self, newCurrentIdx, animateTime):
        self.currentIdx = newCurrentIdx
        self.grid.GoToEntry(self.currentIdx, animateTime=animateTime)
        self.grid.UpdateEntryState(self.currentIdx, KeyVal(fadeTime=animateTime))
        self.breadcrumbsCont.SetDotSelectionState(self.currentIdx, bool(animateTime))
        self.UpdateBrowseBtns()

    def UpdateBrowseBtns(self):
        self.backBtn.display = self.currentIdx > 0
        if not self.grid:
            return
        maxIdx = self.grid.columns - 1
        if maxIdx > 0 and maxIdx > self.currentIdx:
            self.fwdBtn.display = True
        else:
            self.fwdBtn.display = False

    def AddBrowseBtns(self):
        self.backBtn = ButtonIcon(parent=self, align=uiconst.CENTERLEFT, left=20, top=-12, texture_path='res:/UI/Texture/Shared/DarkStyle/backward.png', size=16, on_click=self.GoBack, opacity_enabled=0.6, opacity_disabled=0.2)
        self.fwdBtn = ButtonIcon(parent=self, align=uiconst.CENTERRIGHT, left=20, top=-12, texture_path='res:/UI/Texture/Shared/DarkStyle/forward.png', size=16, on_click=self.GoFwd, opacity_enabled=0.6, opacity_disabled=0.2)

    def GoBack(self, *args):
        self.OnBrowse(-1)

    def GoFwd(self, *args):
        self.OnBrowse(1)

    def OnBrowse(self, direction, *args):
        newDay = self.grid.OnBrowse(direction, self.currentIdx)
        if newDay is not None:
            self.currentIdx = newDay
            self.breadcrumbsCont.SetDotSelectionState(newDay, True)
            self.grid.UpdateEntryState(newDay, KeyVal(fadeTime=0.2))
        self.UpdateBrowseBtns()

    def OnDailyRewardClaimed(self, todays_alpha_rewards, todays_omega_rewards, retroactive_rewards):
        giftsReceivedConst = GetGiftsReceivedConst(todays_alpha_rewards, todays_omega_rewards, retroactive_rewards)
        triggerIdx = self.currentIdx
        sm.ScatterEvent('OnDailyRewardClaimedLocal', triggerIdx)
        if giftsReceivedConst in (rewardUiConst.ONLY_ALPHA_GIFT_REWARDED, rewardUiConst.ONLY_OMEGA_GIFT_REWARDED):
            PlaySound('daily_login_gift_single_play')
            uthread2.call_after_wallclocktime_delay(self.UpdateInfo, animationDelay)
        else:
            PlaySound('daily_login_gift_play')
            nextIdx = max([ i for i, x in self.grid.entries.iteritems() if getattr(x, 'OnDailyRewardClaimedLocal', None) and i != triggerIdx ] or [0])
            uthread2.call_after_wallclocktime_delay(self.SetCurrentSelectedAndUpdateUI, animationDelay, nextIdx, 0.5)
            uthread2.call_after_wallclocktime_delay(self.UpdateInfo, 2 * animationDelay)

    def OnRewardReminderClaimed(self, *args, **kwargs):
        self.UpdateInfo()

    def UpdateInfo(self):
        self.UpdateHeaderText()
        self.MoveToNextClaimable()


class BaseRewardReminderCont(ContainerAutoSize):
    default_align = uiconst.TOPLEFT
    default_alignMode = uiconst.TOTOP
    default_height = 500
    default_name = 'RewardReminderCont'

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.panelController = self.GetPanelController()
        self.rewardData = attributes.rewardData
        self.oldRewardData = self.rewardData
        self.contIdx = attributes.contIdx
        self.entryType = self.rewardData.entryType
        self.countdownThread = None
        labelPadding = ReminderRewardPanelConst.ENTRY_SIDE_PADDING
        labelTop = 6
        campaignName = GetByMessageID(self.rewardData.campaignNameID)
        self.campaignNameLabel = EveLabelMedium(name='campaignNameLabel', parent=self, align=uiconst.TOTOP, top=labelTop, left=labelPadding, text=campaignName)
        self.campaignProgressLabel = EveLabelMedium(name='campaignProgressLabel', parent=self, align=uiconst.TOPRIGHT, left=labelPadding, top=labelTop)
        self.SetProgressText()
        self.campaignNameLabel.padRight = self.campaignProgressLabel.left + self.campaignProgressLabel.width + 20
        self.ConstructRewardItemCont(self.rewardData)
        self.bottomCont = Container(name='bottomCont', parent=self, align=uiconst.TOTOP, height=70)
        self.rewardItemCont.LoadRewardInfo(self.rewardData.rewardInfo)
        self.width = ReminderRewardPanelConst.ENTRY_WIDTH
        self.height = self.rewardItemCont.height + self.rewardItemCont.top + self.bottomCont.height
        self.ConstructClaimBtnAndLabel()
        sm.RegisterNotify(self)

    def GetPanelController(self):
        raise NotImplementedError('panel controller not specified for BaseRewardReminderCont')

    def SetProgressText(self, addToNumClaimed = False):
        if self.rewardData:
            numClaimed = self.rewardData.numClaimed
            totalRewards = self.rewardData.totalRewards
            progressText = GetProgressText(numClaimed, totalRewards)
        elif self.oldRewardData and addToNumClaimed:
            numClaimed = self.oldRewardData.numClaimed + 1
            totalRewards = self.oldRewardData.totalRewards
            progressText = GetProgressText(numClaimed, totalRewards)
        else:
            progressText = ''
        self.campaignProgressLabel.text = progressText

    def ConstructRewardItemCont(self, rewardData):
        itemParent = Container(name='itemParent', parent=self, align=uiconst.TOTOP)
        _, entryClass = GetContAndEntryClassFromType(rewardData.entryType)
        self.rewardItemCont = entryClass(parent=itemParent, align=uiconst.CENTERTOP, panelController=self.panelController, width=ReminderRewardPanelConst.DAY_WIDTH, bgColor=(1.0, 1.0, 1.0, 0.05))
        self.rewardItemCont.GetMenu = None
        itemParent.height = self.rewardItemCont.height

    def ConstructClaimBtnAndLabel(self):
        self.claimBtn = Button(parent=self.bottomCont, align=uiconst.CENTERTOP, label=GetByLabel('UI/LoginRewards/ClaimButtonText'), func=self.OnClaimBtnClicked, top=16)
        self.nextAvailableLabel = EveLabelMediumBold(name='nextAvailableLabel', parent=self.bottomCont, align=uiconst.TOTOP_NOPUSH, top=10, color=BLUE_TEXT_COLOR)
        redeemText = '<center>%s</center>' % GetByLabel('UI/LoginRewards/ClaimExplanationText', linkStart='<color=%s><b>' % Color.RGBtoHex(*BLUE_TEXT_COLOR), linkEnd='</b></color>')
        redeemPadding = (ReminderRewardPanelConst.ENTRY_SIDE_PADDING,
         0,
         ReminderRewardPanelConst.ENTRY_SIDE_PADDING,
         0)
        self.redeemLabel = EveLabelMedium(name='redeemLabel', parent=self.bottomCont, align=uiconst.TOTOP_NOPUSH, top=30, text=redeemText, padding=redeemPadding)
        self.redeemLabel.display = False
        self.UpdateBottom()

    def UpdateEntryState(self, entryIdx, selectedIdx, updateKeyVal):
        fadeTime = getattr(updateKeyVal, 'fadeTime', 0)
        isCurrent = entryIdx == selectedIdx
        if fadeTime:
            self.campaignNameLabel.display = True
            self.campaignProgressLabel.display = True
            if isCurrent:
                animations.FadeTo(self.campaignNameLabel, self.campaignNameLabel.opacity, 1.0, duration=fadeTime)
                animations.FadeTo(self.campaignProgressLabel, self.campaignNameLabel.opacity, 1.0, duration=fadeTime)
            else:
                animations.FadeTo(self.campaignNameLabel, self.campaignNameLabel.opacity, 0.0, duration=fadeTime / 2.0)
                animations.FadeTo(self.campaignProgressLabel, self.campaignNameLabel.opacity, 0.0, duration=fadeTime / 2.0)
        else:
            self.campaignNameLabel.opacity = 1.0 if isCurrent else 0.0
            self.campaignProgressLabel.opacity = 1.0 if isCurrent else 0.0

    def OnClaimBtnClicked(self, *args):
        self.panelController.ClaimReward()

    def UpdateBottom(self, withTransition = False):
        pass

    def _UpdateBottom(self, nextTime, withTransition = False):
        if self.countdownThread:
            self.countdownThread.KillTimer()
            self.countdownThread = None
        canClaimNow = nextTime < gametime.GetWallclockTime() if nextTime is not None else False
        if canClaimNow or nextTime is None:
            self.nextAvailableLabel.text = ''
        else:
            self.StartCountDown(nextTime)
        if withTransition:
            if canClaimNow:
                self.claimBtn.display = True
                animations.FadeOut(self.nextAvailableLabel, duration=0.1)
                animations.FadeOut(self.redeemLabel, duration=0.1)
                animations.FadeTo(self.claimBtn, startVal=0.0, duration=0.5)
            else:
                self.nextAvailableLabel.display = True
                self.redeemLabel.display = True
                animations.FadeOut(self.claimBtn, duration=0.1)
                animations.FadeTo(self.nextAvailableLabel, startVal=0.0, duration=0.5)
                animations.FadeTo(self.redeemLabel, startVal=0.0, duration=0.5)
        else:
            self.claimBtn.display = canClaimNow
            self.nextAvailableLabel.display = not canClaimNow
            self.redeemLabel.display = not canClaimNow

    def StartCountDown(self, nextRewardTime):
        self.UpdateCountDown_thread(nextRewardTime)
        self.countdownThread = AutoTimer(500, self.UpdateCountDown_thread, nextRewardTime)

    def UpdateCountDown_thread(self, nextRewardTime):
        if not self or self.destroyed:
            self.countdownThread = None
            return
        text = GetCountdownTextToDisplay('UI/LoginRewards/NextGiftWithTimer', nextRewardTime)
        self.nextAvailableLabel.text = text


class RewardReminderContRookie(BaseRewardReminderCont):
    __notifyevents__ = ['OnDailyCampaignAwardClaimed']

    def GetPanelController(self):
        return LoginCampaignController(sm.GetService('loginCampaignService'), rewardUiConst.ReminderRewardPanelConst)

    def UpdateBottom(self, withTransition = False):
        nextRewardData = self.panelController.GetNextRewardData()
        nextTime = self.panelController.GetTimestampWhenRewardCanBeClaimed() if nextRewardData and nextRewardData.rewardInfo else None
        self._UpdateBottom(nextTime, withTransition)

    def SetProgressText(self, addToNumClaimed = False):
        pConst = self.panelController.GetPanelConstants()
        if pConst.SHOW_REWARD_COUNTER and self.panelController.IsRookieCampaign():
            BaseRewardReminderCont.SetProgressText(self, addToNumClaimed)

    def OnDailyCampaignAwardClaimed(self, itemReward, updatedItemProgress, receivedBucketTypeID, updatedBucketInfo):
        if updatedItemProgress or updatedBucketInfo:
            PlaySound('daily_login_rewards_play')
            self.UpdateBottom(withTransition=True)
            nextRewardData = self.panelController.GetNextRewardData()
            self.oldRewardData = self.rewardData
            self.rewardData = nextRewardData
            self.SetProgressText(addToNumClaimed=True)
            rewardInfo = self.rewardData.rewardInfo if self.rewardData else None
            self.rewardItemCont.LoadNewReward(rewardInfo)
            sm.ScatterEvent('OnRewardReminderClaimed')


class RewardReminderContSeasons(BaseRewardReminderCont):
    default_align = uiconst.TOPLEFT
    __notifyevents__ = ['OnDailyRewardClaimedLocal']

    def GetPanelController(self):
        seasonalLoginCampaignService = sm.GetService('seasonalLoginCampaignService')
        isOmega = seasonalLoginCampaignService.is_omega()
        return SeasonalPanelController(seasonalLoginCampaignService, rewardUiConst.ReminderRewardPanelConst, isOmega)

    def UpdateBottom(self, withTransition = False):
        isEnding = self.panelController.IsCampaignEndingBeforeNextReward()
        campaingCompleted = self.panelController.HasActiveCampaignBeenCompleted()
        if isEnding or campaingCompleted:
            nextTime = None
        else:
            nextTime = self.panelController.GetTimestampWhenRewardCanBeClaimed()
        self._UpdateBottom(nextTime, withTransition)

    def OnDailyRewardClaimedLocal(self, claimedIdx):
        if claimedIdx != self.contIdx:
            uthread2.Sleep(animationDelay)
        isCampaignSuccessfullyCompleted = self.panelController.HasActiveCampaignBeenCompleted()
        isCampaignEnding = self.panelController.IsCampaignEndingBeforeNextReward()
        self.UpdateBottom(withTransition=True)
        if isCampaignSuccessfullyCompleted:
            campaignStatus = rewardUiConst.CAMPAIGN_STATUS_SUCCESSFULLY_COMPLETED
        elif isCampaignEnding:
            campaignStatus = rewardUiConst.CAMPAIGN_STATUS_ENDING
        else:
            campaignStatus = rewardUiConst.CAMPAIGN_STATUS_ONGOING
        entryType = self.entryType
        rewardData = self.panelController.GetNextRewardDataForEntryType(entryType)
        if not rewardData:
            return
        self.oldRewardData = self.rewardData
        self.rewardData = rewardData
        if campaignStatus in (rewardUiConst.CAMPAIGN_STATUS_ENDING, rewardUiConst.CAMPAIGN_STATUS_SUCCESSFULLY_COMPLETED):
            self.rewardItemCont.FadeOutAndPlayVideo()
            self.rewardItemCont.LoadCompletedScreen(False)
        else:
            rewardInfo = self.rewardData.rewardInfo if self.rewardData else None
            self.rewardItemCont.LoadNewReward(rewardInfo)
        self.SetProgressText(addToNumClaimed=True)


def GetCountdownTextToDisplay(labelPath, nextRewardTime):
    if nextRewardTime is None:
        return ''
    endTime = max(0, nextRewardTime - gametime.GetWallclockTime())
    text = '<center>%s</center>' % GetByLabel(labelPath, endTime=endTime, formattingStart='<color=white>', formattingEnd='</color>')
    return text


def GetContAndEntryClassFromType(entryType):
    if entryType == ALPHA_SEASONAL_ENTRY:
        return (RewardReminderContSeasons, TwoTrackPreviewItemEntryAlpha)
    if entryType == OMEGA_SEASONAL_ENTRY:
        return (RewardReminderContSeasons, TwoTrackPreviewItemEntryOmega)
    return (RewardReminderContRookie, ReminderPreviewItemEntry)


def GetProgressText(numRewardsClaimed, numRewardsTotal):
    hexColor = Color.RGBtoHex(*BLUE_TEXT_COLOR)
    startTags = '<color=%s><b>' % hexColor
    endTags = '</b></color>'
    return GetByLabel('UI/LoginRewards/CampaignProgress', numRewardsCollected=numRewardsClaimed, numRewardsTotal=numRewardsTotal, startTags=startTags, endTags=endTags)


class BreadcrumbCont(Container):
    default_height = 10
    IDLE_COLOR = (0.75, 0.75, 0.75, 0.3)
    SELECTED_COLOR = (1, 1, 1, 1)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        numRewards = attributes.numRewards
        self.dots = []
        for i in xrange(numRewards):
            c = Container(parent=self, align=uiconst.TOLEFT, width=10)
            f = Fill(parent=c, align=uiconst.CENTERLEFT, pos=(0, 0, 6, 6))
            self.dots.append(f)

    def SetDotSelectionState(self, idx, animate = False):
        for i, dot in enumerate(self.dots):
            if i == idx:
                color = self.SELECTED_COLOR
                animations.SpColorMorphTo(dot, endColor=self.SELECTED_COLOR)
            else:
                color = self.IDLE_COLOR
            if animate:
                animations.SpColorMorphTo(dot, endColor=color, duration=0.2)
                animations.FadeTo(dot, dot.opacity, color[3], duration=0.2)
            else:
                dot.SetRGBA(*self.IDLE_COLOR)
