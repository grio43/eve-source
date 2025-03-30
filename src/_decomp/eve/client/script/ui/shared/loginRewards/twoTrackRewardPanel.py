#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\twoTrackRewardPanel.py
import math
import evetypes
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.container import Container
from carbonui import uiconst
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from carbonui.uianimations import animations
from carbonui.util.color import Color
from clonegrade import COLOR_OMEGA_ORANGE
from crates import CratesStaticData
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.eveColor import WHITE
from eve.client.script.ui.shared.loginRewards import rewardUiConst
from eve.client.script.ui.shared.loginRewards.bottomCont import TwoTrackRewardBottomCont
from eve.client.script.ui.shared.loginRewards.browseControls import BrowseControls
from eve.client.script.ui.shared.loginRewards.rewardEntry import OmegaRewardEntry, AlphaRewardEntry, DayEntry
from eve.client.script.ui.shared.loginRewards.rewardInfo import RewardInfo
from eve.client.script.ui.shared.loginRewards.rewardItemsGrid import RewardItemsGrid, DayGrid
from eve.client.script.ui.shared.loginRewards.rewardPreviewCont import TwoTrackRewardPreviewCont, TwoTrackTodaysItemTop
from localization import GetByLabel
from eve.client.script.ui.shared.loginRewards.rewardUiConst import SCROLL_ANIMATION, TODAYS_SIDE_PADDING
from loginrewards.client.tooltips import OmegaIconToolTip
from loginrewards.common.rewardUtils import GetClaimState
from utillib import KeyVal
import mathext
arrowPath = 'res:/UI/Texture/classes/LoginCampaign/rewardTrack_trackArrow.png'
trackBgColor = (0,
 0,
 0,
 0.6)

class BaseTwoTrackRewardPanel(Container):

    def ApplyAttributes(self, attributes):
        self.panelController = self.GetPanelController()
        pConst = self.panelController.GetPanelConstants()
        self.campaignDataByID = {}
        self.currentFirstVisibleDay = 0
        Container.ApplyAttributes(self, attributes)
        centerCont = Container(name='centerCont', parent=self, align=uiconst.TOALL, padding=(12, 5, 12, 5))
        Fill(bgParent=centerCont, color=trackBgColor)
        self.claimCont = TwoTrackRewardBottomCont(parent=centerCont, panelController=self.panelController, isOmega=self.panelController.IsOmega())
        self.topInfoCont = Container(name='topCont', parent=centerCont, align=uiconst.TOTOP, height=pConst.CENTER_TOP_HEIGHT)
        self.todaysItemTop = TwoTrackTodaysItemTop(name='todaysItemTop', parent=self.topInfoCont, align=uiconst.TORIGHT, height=pConst.CENTER_TOP_HEIGHT, panelController=self.panelController, padRight=4, width=290)
        Fill(bgParent=self.topInfoCont, color=trackBgColor)
        self.leftCont = Container(name='leftCont', parent=centerCont, align=uiconst.TOLEFT, width=pConst.LEFT_WIDTH, padTop=-6)
        self.cloneCont = Container(name='cloneCont', parent=self.leftCont)
        self.BuildAlphaTrack()
        self.BuildOmegaTrack()
        self.sideCont = TwoTrackRewardPreviewCont(name='sideCont', parent=centerCont, align=uiconst.TOALL, padding=(0, -8, 4, 0), panelController=self.panelController, isOmega=self.panelController.IsOmega())
        self.campaignProgressLabel = EveLabelMedium(parent=self.topInfoCont, align=uiconst.CENTER, color=WHITE)
        rewardCount = self.GetRewardCount()
        if pConst.SHOW_BROWSE_CONTROLS and rewardCount > pConst.NUM_VISIBLE_ITEMS:
            BrowseControls(parent=self.topInfoCont, browseFunc=self.OnBrowse, resetFunc=self.GoToToday, padLeft=3)
        self.LoadCampaign()
        sm.RegisterNotify(self)

    def GetPanelController(self):
        raise NotImplemented('panel controller needs to be overriden')

    def BuildAlphaTrack(self):
        pConst = self.panelController.GetPanelConstants()
        dayTrackPar = Container(name='dayTrackPar', parent=self.cloneCont, align=uiconst.TOTOP, height=30, padTop=2)
        alphaTrackPar = Container(name='alphaTrackPar', parent=self.cloneCont, align=uiconst.TOTOP, height=152, padding=(0, 2, 0, 2))
        Container(name='arrowCont', parent=alphaTrackPar, align=uiconst.TORIGHT, width=pConst.TRACK_ARROW_WIDTH, clipChildren=True)
        alphaSpriteCont = Container(name='alphaSpriteCont', parent=alphaTrackPar, align=uiconst.TOLEFT, width=pConst.CLONE_COLUMN_WIDTH, bgColor=(1, 1, 1, 0.1), padding=(0, 0, 0, 60))
        Sprite(name='alpha', parent=alphaSpriteCont, align=uiconst.CENTER, state=uiconst.UI_NORMAL, pos=(1, 0, 16, 16), texturePath='res:/UI/Texture/classes/LoginCampaign/alpha_Icon.png', hint=GetByLabel('UI/LoginRewards/Tooltips/AlphaTooltip'))
        self.dayTrackCont = Container(name='dayTrackCont', parent=dayTrackPar, align=uiconst.TOALL, clipChildren=True, padding=(pConst.SIDE_PADDING + pConst.CLONE_COLUMN_WIDTH,
         0,
         pConst.TRACK_ARROW_WIDTH,
         0))
        self.alphaTrackCont = Container(name='alphaTrackCont', parent=alphaTrackPar, align=uiconst.TOALL, clipChildren=True, padding=(pConst.SIDE_PADDING,
         0,
         0,
         0))

    def BuildOmegaTrack(self):
        pConst = self.panelController.GetPanelConstants()
        omegaTrackPar = Container(name='omegaTrackPar', parent=self.cloneCont, align=uiconst.TOTOP, height=152, padding=(0, 2, 0, 2))
        Container(name='arrowCont', parent=omegaTrackPar, align=uiconst.TORIGHT, width=pConst.TRACK_ARROW_WIDTH, clipChildren=True)
        omegaSpriteCont = Container(name='omegaSpriteCont', parent=omegaTrackPar, align=uiconst.TOLEFT, width=pConst.CLONE_COLUMN_WIDTH, bgColor=(0.988, 0.761, 0.027, 0.45), padding=(0, 0, 0, 60))
        omegaSprite = Sprite(name='omega', parent=omegaSpriteCont, align=uiconst.CENTER, state=uiconst.UI_NORMAL, pos=(1, 0, 16, 16), texturePath='res:/UI/Texture/classes/LoginCampaign/omega_Icon.png', color=COLOR_OMEGA_ORANGE)
        omegaSprite.tooltipPanelClassInfo = OmegaIconToolTip(sm.GetService('loginCampaignService').open_vgs_to_buy_omega_time_from_DLI)
        self.omegaTrackCont = Container(name='omegaTrackCont', parent=omegaTrackPar, align=uiconst.TOALL, clipChildren=True, padding=(pConst.SIDE_PADDING,
         0,
         0,
         0))

    def GoToToday(self, animationTime = rewardUiConst.SCROLL_ANIMATION, *args):
        posInTrack = self.panelController.GetPositionInGridTrack()
        self.GoToDay(posInTrack, animationTime=animationTime)

    def GoToDay(self, posInTrack, animationTime = SCROLL_ANIMATION, *args):
        if self.panelController.CanRetroClaimNow():
            posInTrack -= 1
        self.dayGrid.GoToSelectedEntry(posInTrack, animationTime)
        newDayAlpha = self.alphaGrid.GoToSelectedEntry(posInTrack, animationTime)
        newDayOmega = self.omegaGrid.GoToSelectedEntry(posInTrack, animationTime)
        if newDayAlpha is not None or newDayOmega is not None:
            self.currentFirstVisibleDay = newDayAlpha or newDayOmega

    def OnBrowse(self, direction, *args):
        self.dayGrid.OnBrowse(direction, self.currentFirstVisibleDay)
        newDayAlpha = self.alphaGrid.OnBrowse(direction, self.currentFirstVisibleDay)
        newDayOmega = self.omegaGrid.OnBrowse(direction, self.currentFirstVisibleDay)
        if newDayAlpha is not None or newDayOmega is not None:
            self.currentFirstVisibleDay = newDayAlpha or newDayOmega

    def GetCampaignData(self):
        return self.panelController.GetCampaignData()

    def LoadCampaign(self):
        self.LoadGrid()

    def LoadGrid(self):
        self.alphaTrackCont.Flush()
        self.omegaTrackCont.Flush()
        rewardCount = self.GetRewardCount()
        self.dayGrid = DayGrid(name='alphaDayGrid', parent=self.dayTrackCont, align=uiconst.CENTERLEFT, columns=rewardCount, numAllEntries=rewardCount, panelConst=self.panelController.GetPanelConstants())
        self.dayGridLineCont = self.GetLineCont(self.dayTrackCont)
        self.alphaGrid = RewardItemsGrid(name='alphaRewardGrid', parent=self.alphaTrackCont, align=uiconst.CENTERLEFT, columns=rewardCount, numAllEntries=rewardCount, panelConst=self.panelController.GetPanelConstants())
        self.alphaGridLineCont = self.GetLineCont(self.alphaTrackCont)
        self.omegaGrid = RewardItemsGrid(name='omegaRewardGrid', parent=self.omegaTrackCont, align=uiconst.CENTERLEFT, columns=rewardCount, numAllEntries=rewardCount, panelConst=self.panelController.GetPanelConstants())
        self.omegaGridLineCont = self.GetLineCont(self.omegaTrackCont)
        daysClaimedByAlpha = self.panelController.GetDayNumbersClaimedInAlphaTrack()
        daysClaimedByOmega = self.panelController.GetDayNumbersClaimedInOmegaTrack()
        numRewardsClaimed = self.panelController.GetNumDaysClaimed()
        somethingCanBeClaimedNow = self.panelController.CanSomethingBeClaimedNow()
        selectedDay = numRewardsClaimed
        if self.panelController.CanRetroClaimNow():
            selectedDay -= 1
        alphaEntryInfoForGrid = []
        dayEntryInfoForGrid = []
        cratesStaticData = CratesStaticData()
        campaignData = self.GetCampaignData()
        for day, info in campaignData.alphaRewards.iteritems():
            isClaimed = day in daysClaimedByAlpha
            isNextClaimable = numRewardsClaimed == day
            claimState = GetClaimState(isClaimed, isNextClaimable, somethingCanBeClaimedNow)
            messageID = evetypes.GetDescriptionID(info.typeID)
            displayNameID = cratesStaticData.get_crate_nameID(info.typeID)
            rewardInfo = RewardInfo(day + 1, info, claimState, messageID, displayNameID=displayNameID)
            dayEntryInfoForGrid.append({'entryClass': DayEntry,
             'rewardInfo': rewardInfo,
             'panelController': self.panelController})
            alphaEntryInfoForGrid.append({'entryClass': AlphaRewardEntry,
             'rewardInfo': rewardInfo,
             'panelController': self.panelController})

        dayEntryInfoForGrid.sort(key=lambda x: x['rewardInfo'].day)
        alphaEntryInfoForGrid.sort(key=lambda x: x['rewardInfo'].day)
        omegaEntryInfoForGrid = []
        for day, info in campaignData.omegaRewards.iteritems():
            isClaimed = day in daysClaimedByOmega
            isNextClaimable = selectedDay == day
            claimState = GetClaimState(isClaimed, isNextClaimable, somethingCanBeClaimedNow)
            messageID = evetypes.GetDescriptionID(info.typeID)
            displayNameID = cratesStaticData.get_crate_nameID(info.typeID)
            rewardInfo = RewardInfo(day + 1, info, claimState, messageID, displayNameID=displayNameID)
            omegaEntryInfoForGrid.append({'entryClass': OmegaRewardEntry,
             'rewardInfo': rewardInfo,
             'panelController': self.panelController})

        omegaEntryInfoForGrid.sort(key=lambda x: x['rewardInfo'].day)
        self.dayGrid.LoadEntries(dayEntryInfoForGrid)
        self.alphaGrid.LoadEntries(alphaEntryInfoForGrid)
        self.omegaGrid.LoadEntries(omegaEntryInfoForGrid)
        self.ShowLinesIfNeeded(self.dayGridLineCont, self.dayGrid)
        self.ShowLinesIfNeeded(self.alphaGridLineCont, self.alphaGrid)
        self.ShowLinesIfNeeded(self.omegaGridLineCont, self.omegaGrid)
        self.SetDayAsCurrent(selectedDay)
        self.GoToToday(animationTime=0)

    def ShowLinesIfNeeded(self, lineCont, grid):
        if grid.AreEntriesFewerThanMaxVisible():
            width = grid.GetEntriesWidth()
            lineCont.width = width
            lineCont.display = True
        else:
            lineCont.display = False

    def GetRewardCount(self):
        campaignData = self.GetCampaignData()
        rewardCount = min(len(campaignData.alphaRewards), len(campaignData.omegaRewards))
        return rewardCount

    def GetLineCont(self, parent):
        lineTexturePath = 'res:/UI/Texture/classes/LoginCampaign/todaysRewardContainerStroke.png'
        lineCont = Container(name='lineCont', parent=parent, align=uiconst.CENTER, pos=(0, 0, 0, 5))
        lineWidth = 150
        Sprite(name='leftSprite', parent=lineCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, texturePath=lineTexturePath, pos=(-lineWidth - 10,
         0,
         lineWidth,
         5), rotation=math.pi, opacity=0.4)
        Sprite(name='rightSprite', parent=lineCont, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, texturePath=lineTexturePath, pos=(-lineWidth - 10,
         0,
         lineWidth,
         5), opacity=0.4)
        lineCont.display = False
        return lineCont

    def SetDayAsCurrent(self, entryNum, withTransition = False, giftsReceivedConst = None):
        alphaEntry = self.alphaGrid.GetEntry(entryNum)
        omegaEntry = self.omegaGrid.GetEntry(entryNum)
        alphaRewardInfo = omegaRewardInfo = claimState = None
        campaignStatus = self.panelController.GetCampaignStatus()
        if campaignStatus == rewardUiConst.CAMPAIGN_STATUS_ONGOING:
            if alphaEntry:
                alphaRewardInfo = alphaEntry.rewardInfo
                omegaRewardInfo = omegaEntry.rewardInfo
                claimState = omegaRewardInfo.claimState
            else:
                return
        next_reward_time = self.panelController.GetTimestampWhenRewardCanBeClaimed()
        self.claimCont.LoadRewardInfo(claimState, next_reward_time)
        if campaignStatus in (rewardUiConst.CAMPAIGN_STATUS_ENDING, rewardUiConst.CAMPAIGN_STATUS_SUCCESSFULLY_COMPLETED):
            self.sideCont.PlayVideosAndFadeOut(next_reward_time, withTransition, giftsReceivedConst)
            self.todaysItemTop.UpdateTextAndHelpIcon(next_reward_time)
            self.sideCont.LoadCompletedScreen(withTransition)
            if withTransition:
                animations.MorphScalar(self.todaysItemTop, 'padLeft', self.todaysItemTop.padLeft, TODAYS_SIDE_PADDING, duration=0.2)
                animations.MorphScalar(self.todaysItemTop, 'padRight', self.todaysItemTop.padRight, TODAYS_SIDE_PADDING, duration=0.2)
            else:
                self.todaysItemTop.padLeft = TODAYS_SIDE_PADDING
                self.todaysItemTop.padRight = TODAYS_SIDE_PADDING
            self.todaysItemTop.UpdateTextAndHelpIcon(next_reward_time)
        elif alphaRewardInfo:
            self.sideCont.LoadRewardInfo(alphaRewardInfo, omegaRewardInfo, next_reward_time, withTransition, giftsReceivedConst)
            self.todaysItemTop.UpdateTextAndHelpIcon(next_reward_time)
        else:
            raise RuntimeError('Invalid two track campaign state and reward info')
        rewardDaysRemaining = self.panelController.GetNumberOfRewardsDaysRemainingAndAvailable()
        claimedDaysInAlphaTrack = self.panelController.GetDayNumbersClaimedInAlphaTrack()
        if claimedDaysInAlphaTrack:
            maxDayClaimed = max(claimedDaysInAlphaTrack)
        else:
            maxDayClaimed = -1
        availableRewardsDays = range(maxDayClaimed + 1, maxDayClaimed + 1 + rewardDaysRemaining)
        selectedDay = entryNum if campaignStatus == rewardUiConst.CAMPAIGN_STATUS_ONGOING else None
        self.dayGrid.UpdateEntryState(selectedDay, KeyVal(claimedDays=claimedDaysInAlphaTrack, availableRewardsDays=availableRewardsDays))
        self.alphaGrid.UpdateEntryState(selectedDay, KeyVal(claimedDays=claimedDaysInAlphaTrack, availableRewardsDays=availableRewardsDays))
        self.omegaGrid.UpdateEntryState(selectedDay, KeyVal(claimedDays=self.panelController.GetDayNumbersClaimedInOmegaTrack(), availableRewardsDays=availableRewardsDays))
        self.dayGrid.SetDayEntryAsSelected(selectedDay, withTransition)
        self.alphaGrid.SetEntryAsSelected(selectedDay, withTransition)
        self.omegaGrid.SetEntryAsSelected(selectedDay, withTransition)
        self.UpdateCampaignProgressLabel()

    def UpdateCampaignProgressLabel(self):
        numRewardsClaimed = self.panelController.GetNumDaysClaimed()
        numRewardsTotal = self.GetRewardCount()
        hexColor = Color.RGBtoHex(*rewardUiConst.BLUE_TEXT_COLOR)
        startTags = '<color=%s><b>' % hexColor
        endTags = '</b></color>'
        self.campaignProgressLabel.text = GetByLabel('UI/LoginRewards/CampaignProgress', numRewardsCollected=numRewardsClaimed, numRewardsTotal=numRewardsTotal, startTags=startTags, endTags=endTags)

    def OnDailyRewardClaimed(self, todays_alpha_rewards, todays_omega_rewards, retroactive_rewards):
        giftsReceivedConst = GetGiftsReceivedConst(todays_alpha_rewards, todays_omega_rewards, retroactive_rewards)
        if giftsReceivedConst in (rewardUiConst.ONLY_ALPHA_GIFT_REWARDED, rewardUiConst.ONLY_OMEGA_GIFT_REWARDED):
            PlaySound('daily_login_gift_single_play')
        else:
            PlaySound('daily_login_gift_play')
        selectedDay = self.panelController.GetNumDaysClaimed()
        if self.panelController.CanRetroClaimNow():
            selectedDay = max(selectedDay - 1, 0)
        self.SetDayAsCurrent(selectedDay, True, giftsReceivedConst=giftsReceivedConst)
        daysScrolling = abs(self.currentFirstVisibleDay - 1 - selectedDay)
        scrollTime = mathext.clamp(daysScrolling * rewardUiConst.SCROLL_ANIMATION_AUTO_STEP, 0.5, 1.5)
        self.GoToToday(animationTime=scrollTime)

    def BuildFrame(self, frameCont, arrowCont):
        pConst = self.panelController.GetPanelConstants()
        lineColor = (1.0, 1.0, 1.0, 0.25)
        height = arrowCont.absoluteBottom - arrowCont.absoluteTop
        lineArrow = VectorLineTrace(name='lineArrow', parent=arrowCont, lineWidth=0.35)
        posList = [(0, 0), (arrowCont.width, height / 2.0), (0, height)]
        lineArrow.AddPoints(posList, lineColor)
        lineBox = VectorLineTrace(name='lineBox', parent=frameCont, lineWidth=0.55)
        frameWidth = frameCont.absoluteRight - frameCont.absoluteLeft
        posList = [(frameWidth, 0),
         (0, 0),
         (0, height),
         (frameWidth, height)]
        lineBox.AddPoints(posList, lineColor)
        Sprite(parent=arrowCont, texturePath='res:/UI/Texture/classes/LoginCampaign/rewardTrack_circuitBoard.png', align=uiconst.CENTERRIGHT, pos=(2, 0, 771, 155), opacity=0.8)
        Sprite(parent=arrowCont, texturePath=arrowPath, align=uiconst.TORIGHT, color=trackBgColor, width=pConst.TRACK_ARROW_WIDTH, state=uiconst.UI_DISABLED)
        trackBgCont = Container(name='trackBgCont', parent=frameCont, align=uiconst.TOALL, clipChildren=True, left=pConst.CLONE_COLUMN_WIDTH)
        Fill(bgParent=trackBgCont, color=trackBgColor, padding=(0, 2, 0, 2))
        Sprite(parent=trackBgCont, texturePath='res:/UI/Texture/classes/LoginCampaign/rewardTrack_circuitBoard.png', align=uiconst.CENTERRIGHT, pos=(0, 0, 771, 155), padding=(0,
         2,
         -pConst.TRACK_ARROW_WIDTH,
         2), opacity=0.8, state=uiconst.UI_DISABLED)


def GetGiftsReceivedConst(todays_alpha_rewards, todays_omega_rewards, retroactive_rewards):
    if todays_alpha_rewards and not todays_omega_rewards and not retroactive_rewards:
        return rewardUiConst.ONLY_ALPHA_GIFT_REWARDED
    if (todays_omega_rewards or retroactive_rewards) and not todays_alpha_rewards:
        return rewardUiConst.ONLY_OMEGA_GIFT_REWARDED
    return rewardUiConst.ALPHA_OMEGA_GIFTS_REWARDED
