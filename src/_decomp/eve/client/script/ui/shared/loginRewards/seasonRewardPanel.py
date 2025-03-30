#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\seasonRewardPanel.py
from carbon.client.script.environment.AudioUtil import PlaySound
from eve.client.script.ui.shared.loginRewards.panelControllers import SeasonalPanelController
from eve.client.script.ui.shared.loginRewards.twoTrackRewardPanel import GetGiftsReceivedConst, BaseTwoTrackRewardPanel
import eve.client.script.ui.shared.loginRewards.rewardUiConst as rewardUiConst
import mathext

class SeasonRewardPanel(BaseTwoTrackRewardPanel):
    __notifyevents__ = ['OnDailyRewardClaimed']

    def GetPanelController(self):
        seasonalLoginCampaignService = sm.GetService('seasonalLoginCampaignService')
        isOmega = seasonalLoginCampaignService.is_omega()
        return SeasonalPanelController(seasonalLoginCampaignService, rewardUiConst.SeasonRewardPanelConst, isOmega)

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
