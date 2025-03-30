#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\oneTrackRewardPanel.py
import copy
from carbonui.primitives.container import Container
from carbonui import uiconst
from carbonui.primitives.fill import Fill
from carbonui.util.color import Color
from crates import CratesStaticData
from eve.client.script.ui.control.eveLabel import EveLabelMedium
import eve.client.script.ui.shared.loginRewards.rewardUiConst as rewardUiConst
from eve.client.script.ui.shared.loginRewards.bottomCont import OneTrackRewardBottomCont
from eve.client.script.ui.shared.loginRewards.browseControls import BrowseControls
from eve.client.script.ui.shared.loginRewards.rewardItemsGrid import RewardItemsGrid, RewardItemsGridCycle
from eve.client.script.ui.shared.loginRewards.rewardEntry import RewardEntryWithDay, RewardEntryWithTodayAndNextText
from eve.client.script.ui.shared.loginRewards.rewardInfo import RewardInfo
from eve.client.script.ui.shared.loginRewards.rewardPreviewCont import OneTrackRewardPreviewCont, TodaysItemTop
from eve.client.script.ui.shared.loginRewards.twoTrackRewardPanel import trackBgColor
from eve.client.script.ui.eveColor import WHITE
from localization import GetByLabel
from loginrewards.common.const import CLAIM_STATE_CLAIMED
from loginrewards.common.rewardUtils import GetClaimState
from utillib import KeyVal

class BaseOneTrackRewardPanel(Container):

    def ApplyAttributes(self, attributes):
        self.panelController = self.GetPanelController()
        pConst = self.panelController.GetPanelConstants()
        self.isScrolling = False
        self.currentFirstVisibleDay = 0
        Container.ApplyAttributes(self, attributes)
        leftPad = 12
        centerCont = Container(name='centerCont', parent=self, align=uiconst.TOALL, bgColor=(0, 0, 0, 0.75), padding=(leftPad,
         5,
         leftPad,
         0))
        self.claimAndBucketCont = OneTrackRewardBottomCont(parent=centerCont, panelController=self.panelController)
        leftContWidth = pConst.LEFT_WIDTH
        bracketPadding = 16
        contTop = Container(name='contTop', parent=centerCont, align=uiconst.TOTOP, height=pConst.CENTER_TOP_HEIGHT)
        Fill(bgParent=contTop, color=trackBgColor)
        self.leftCont = Container(name='leftCont', parent=centerCont, align=uiconst.TOLEFT, width=leftContWidth)
        itemsPar = Container(name='itemsPar', parent=self.leftCont, align=uiconst.TOALL)
        itemsParInner = Container(name='itemsParInner', parent=itemsPar, align=uiconst.TOALL, padding=(0,
         bracketPadding + 6,
         0,
         bracketPadding + 6), clipChildren=True)
        itemsContPos = (leftPad,
         0,
         pConst.ALL_VISIBLE_DAYS_WIDTH,
         pConst.ENTRY_HEIGHT)
        self.itemsCont = Container(name='itemsCont', parent=itemsParInner, align=uiconst.TOLEFT, pos=itemsContPos, clipChildren=True)
        sideContPadding = (pConst.SECTION_DIVIDER,
         0,
         4,
         0)
        self.sideCont = OneTrackRewardPreviewCont(name='sideCont', parent=centerCont, align=uiconst.TOALL, padding=sideContPadding, panelController=self.panelController)
        self.campaignProgressLabel = EveLabelMedium(parent=contTop, align=uiconst.CENTER, left=pConst.SIDE_PADDING, color=WHITE)
        self.todaysItemTop = TodaysItemTop(name='oneTrackTodaysItemTop', parent=contTop, align=uiconst.TORIGHT, height=pConst.CENTER_TOP_HEIGHT, panelController=self.panelController, padRight=4, width=290)
        if pConst.SHOW_BROWSE_CONTROLS:
            BrowseControls(parent=contTop, browseFunc=self.OnBrowse, resetFunc=self.GoToToday, padLeft=3)
        self.LoadInfo()
        sm.RegisterNotify(self)

    def GetPanelController(self):
        raise NotImplemented('panel controller needs to be overriden')

    def GoToToday(self, animationTime = rewardUiConst.SCROLL_ANIMATION, *args):
        posInTrack = self.panelController.GetPositionInGridTrack()
        self.GoToDay(posInTrack, animationTime=animationTime)

    def GoToDay(self, posInTrack, animationTime = rewardUiConst.SCROLL_ANIMATION):
        newDay = self.rewardGrid.GoToSelectedEntry(posInTrack, animationTime)
        if newDay is not None:
            self.currentFirstVisibleDay = newDay

    def OnBrowse(self, direction, *args):
        newDay = self.rewardGrid.OnBrowse(direction, self.currentFirstVisibleDay)
        if newDay is not None:
            self.currentFirstVisibleDay = newDay

    def LoadInfo(self):
        self.LoadGrid()

    def LoadGrid(self):
        pConst = self.panelController.GetPanelConstants()
        self.itemsCont.Flush()
        if not self.panelController.IsUserInCampaign():
            return
        rewards_by_day = self.panelController.GetRewardsByDay()
        rewardIdx = self.panelController.GetRewardIdx()
        posInTrack = self.panelController.GetPositionInGridTrack()
        somethingCanBeClaimedNow = self.panelController.CanSomethingBeClaimedNow()
        numDays = len(rewards_by_day)
        if self.panelController.DoesCampaignHaveDuration():
            gridClass = RewardItemsGrid
        else:
            gridClass = RewardItemsGridCycle
        self.rewardGrid = gridClass(name='rewardGrid', parent=self.itemsCont, align=uiconst.CENTERLEFT, columns=numDays, numAllEntries=numDays, panelConst=pConst, top=pConst.VERTICAL_OFFSET)
        entryClass = RewardEntryWithDay if pConst.SHOW_NEXT_GIFT else RewardEntryWithTodayAndNextText
        entryInfoForGrid = []
        cratesStaticData = CratesStaticData()
        for day, reward in rewards_by_day.iteritems():
            isClaimed = self.panelController.ShouldShowAsClaimed(rewardIdx, day)
            isNextClaimable = rewardIdx == day
            claimState = GetClaimState(isClaimed, isNextClaimable, somethingCanBeClaimedNow)
            displayNameID = cratesStaticData.get_crate_nameID(reward.typeID)
            rewardInfo = RewardInfo(day, reward, claimState=claimState, messageID=reward.labelMessageID, displayNameID=displayNameID)
            entryInfoForGrid.append({'entryClass': entryClass,
             'rewardInfo': rewardInfo,
             'panelController': self.panelController})

        self.rewardGrid.LoadEntries(entryInfoForGrid)
        self.SetDayAsCurrent(posInTrack)
        self.GoToDay(posInTrack, animationTime=0)

    def SetDayAsCurrent(self, entryNum, withTransition = False):
        entry = self.rewardGrid.GetEntry(entryNum)
        if entry:
            rewardInfo = entry.rewardInfo
            next_reward_time = self.panelController.GetTimestampWhenRewardCanBeClaimed()
        elif entryNum >= self.rewardGrid.GetNumEntries():
            rewardInfo = None
            next_reward_time = None
        else:
            return
        pConst = self.panelController.GetPanelConstants()
        itemReward = self.panelController.GetClaimedRewardForDay(entryNum)
        if itemReward and rewardInfo:
            if itemReward.typeID != rewardInfo.typeID or itemReward.quantity != rewardInfo.qty:
                displayNameID = CratesStaticData().get_crate_nameID(itemReward.typeID)
                itemRewardCopy = itemReward.copy()
                bpInfo = getattr(itemRewardCopy, 'bpInfo', {})
                itemRewardCopy.blueprintMaterialLevel = bpInfo.get('blueprintMaterialLevel', 0)
                itemRewardCopy.blueprintProductivityLevel = bpInfo.get('blueprintProductivityLevel', 0)
                itemRewardCopy.quantity = bpInfo.get('qtyOrRuns', itemRewardCopy.quantity)
                rewardInfo = RewardInfo(rewardInfo.day, itemRewardCopy, CLAIM_STATE_CLAIMED, displayNameID=displayNameID, iconSize=pConst.ICON_SIZE_NEW_ITEM, tier=rewardInfo.tier)
            elif rewardInfo.claimState != CLAIM_STATE_CLAIMED:
                rewardInfo = copy.copy(rewardInfo)
                rewardInfo.claimState = CLAIM_STATE_CLAIMED
        self.claimAndBucketCont.LoadRewardInfo(rewardInfo, next_reward_time, withTransition)
        self.sideCont.LoadRewardInfo(rewardInfo, next_reward_time, withTransition)
        selectedInGrid = entryNum
        if self.panelController.ShouldAddOffsetToSelectedDay():
            selectedInGrid += 1
        claimedDays = self.panelController.GetDaysToMarksAsClaimed(selectedInGrid)
        self.rewardGrid.UpdateEntryState(selectedInGrid, KeyVal(claimedDays=claimedDays))
        self.rewardGrid.SetEntryAsSelected(selectedInGrid, withTransition)
        self.todaysItemTop.UpdateTextAndHelpIcon(self.panelController.GetTimestampWhenRewardCanBeClaimed())
        self.UpdateCampaignProgressLabel()

    def UpdateCampaignProgressLabel(self):
        pConst = self.panelController.GetPanelConstants()
        if not pConst.SHOW_REWARD_COUNTER:
            return
        rewards_by_day = self.panelController.GetRewardsByDay()
        numRewardsClaimed = self.panelController.GetNumDaysClaimed()
        hexColor = Color.RGBtoHex(*rewardUiConst.BLUE_TEXT_COLOR)
        startTags = '<color=%s><b>' % hexColor
        endTags = '</b></color>'
        self.campaignProgressLabel.text = GetByLabel('UI/LoginRewards/CampaignProgress', numRewardsCollected=numRewardsClaimed, numRewardsTotal=len(rewards_by_day), startTags=startTags, endTags=endTags)
