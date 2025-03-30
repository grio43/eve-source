#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\rookieRewardPanel.py
from carbon.client.script.environment.AudioUtil import PlaySound
from eve.client.script.ui.shared.loginRewards.oneTrackRewardPanel import BaseOneTrackRewardPanel
from eve.client.script.ui.shared.loginRewards.panelControllers import RookieLoginCampaignController
from eve.client.script.ui.shared.loginRewards.rewardUiConst import RookieRewardPanelConst
import eve.client.script.ui.shared.loginRewards.rewardUiConst as rewardUiConst
import mathext

class RookieRewardPanel(BaseOneTrackRewardPanel):
    default_name = 'rookieRewardPanel'
    __notifyevents__ = ['OnDailyCampaignAwardClaimed']

    def GetPanelController(self):
        return RookieLoginCampaignController(sm.GetService('loginCampaignService'), RookieRewardPanelConst)

    def OnDailyCampaignAwardClaimed(self, itemReward, updatedItemProgress, receivedBucketTypeID, updatedBucketInfo):
        if updatedItemProgress or updatedBucketInfo:
            PlaySound('daily_login_rewards_play')
            posInTrack = self.panelController.GetPositionInGridTrack()
            self.SetDayAsCurrent(posInTrack, True)
            daysScrolling = abs(self.currentFirstVisibleDay - 1 - updatedItemProgress.num_claimed_rewards)
            scrollTime = mathext.clamp(daysScrolling * rewardUiConst.SCROLL_ANIMATION_AUTO_STEP, 0.5, 1.5)
            self.GoToDay(posInTrack, animationTime=scrollTime)
