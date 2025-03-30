#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\evergreenRewardPanel.py
from carbon.client.script.environment.AudioUtil import PlaySound
from eve.client.script.ui.shared.loginRewards.oneTrackRewardPanel import BaseOneTrackRewardPanel
from eve.client.script.ui.shared.loginRewards.panelControllers import EvergreenLoginCampaignController
from eve.client.script.ui.shared.loginRewards.rewardUiConst import EvergreenPanelConst
import eve.client.script.ui.shared.loginRewards.rewardUiConst as rewardUiConst
import mathext

class EvergreenRewardPanel(BaseOneTrackRewardPanel):
    default_name = 'evergreenRewardPanel'
    __notifyevents__ = ['OnDailyCampaignAwardClaimed']

    def GetPanelController(self):
        return EvergreenLoginCampaignController(sm.GetService('loginCampaignService'), EvergreenPanelConst, sm.GetService('cloneGradeSvc').IsOmega())

    def OnDailyCampaignAwardClaimed(self, itemReward, updatedItemProgress, receivedBucketTypeID, updatedBucketInfo):
        if updatedItemProgress or updatedBucketInfo:
            PlaySound('daily_login_rewards_play')
            posInTrack = self.panelController.GetPositionInGridTrack(True)
            self.SetDayAsCurrent(posInTrack, True)
            daysScrolling = abs(self.currentFirstVisibleDay - 1 - updatedItemProgress.num_claimed_rewards)
            scrollTime = mathext.clamp(daysScrolling * rewardUiConst.SCROLL_ANIMATION_AUTO_STEP, 0.5, 1.5)
            self.GoToDay(posInTrack, animationTime=scrollTime)
