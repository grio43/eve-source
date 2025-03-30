#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\panelControllers.py
import gametime
import itertoolsext
from eve.client.script.ui.shared.loginRewards import rewardUiConst
from globalConfig.getFunctions import GetLoginCampaignIDs
from localization import GetByLabel

class BasePanelController(object):

    def __init__(self, panelConst, isOmega = None):
        self.panelConst = panelConst
        self.isOmega = isOmega

    def GetPanelConstants(self):
        return self.panelConst

    def GetCongratsHeaderText(self):
        return ''

    def GetCongratsBodyText(self):
        return ''

    def IsOmega(self):
        return self.isOmega

    def ClaimReward(self):
        raise NotImplemented('panel controller function needs to be overriden')

    def GetNumDaysClaimed(self):
        raise NotImplemented('panel controller function needs to be overriden')

    def CanSomethingBeClaimedNow(self):
        raise NotImplemented('panel controller function needs to be overriden')

    def IsUserInCampaign(self):
        raise NotImplemented('panel controller function needs to be overriden')

    def GetTimestampWhenRewardCanBeClaimed(self):
        raise NotImplemented('panel controller function needs to be overriden')

    def GetRewardIdx(self):
        raise NotImplemented('panel controller function needs to be overriden')

    def IsRookieCampaign(self):
        return False


class LoginCampaignController(BasePanelController):

    def __init__(self, loginCampaignService, panelConst, isOmega = None):
        BasePanelController.__init__(self, panelConst, isOmega)
        self.loginCampaignService = loginCampaignService

    def GetCongratsHeaderText(self):
        return GetByLabel('UI/LoginRewards/CampaignCompleted')

    def GetCongratsBodyText(self):
        return GetByLabel('UI/LoginRewards/Congratulations')

    def ClaimReward(self):
        self.loginCampaignService.claim_reward()

    def GetNumDaysClaimed(self):
        numRewardsClaimed = self.loginCampaignService.get_num_claimed_rewards()
        return numRewardsClaimed

    def CanSomethingBeClaimedNow(self):
        somethingCanBeClaimedNow = self.loginCampaignService.can_claim_now()
        return somethingCanBeClaimedNow

    def IsUserInCampaign(self):
        isInCampaign = self.loginCampaignService.is_user_enrolled_in_campaign()
        return isInCampaign

    def GetRewardsByDay(self):
        rewards_by_day = self.loginCampaignService.get_item_rewards_by_day()
        return rewards_by_day

    def GetTimestampWhenRewardCanBeClaimed(self):
        next_reward_time = self.loginCampaignService.get_next_reward_time()
        return next_reward_time

    def GetNextRewardData(self):
        return self.loginCampaignService.get_next_reward_data()

    def DoesCampaignHaveDuration(self):
        return self.loginCampaignService.does_campaign_have_duration()

    def IsRookieCampaign(self):
        return self.loginCampaignService.is_rookie_campaign()

    def GetRewardIdx(self):
        return self.loginCampaignService.get_campaign_reward_idx()

    def GetPositionInGridTrack(self, transitioning = False):
        numClaimed = self.GetNumDaysClaimed()
        numRewards = len(self.GetRewardsByDay())
        rewardIdx = self.GetRewardIdx()
        posInTrack = rewardIdx - 1
        if posInTrack < 0:
            posInTrack = numRewards
        if not self.DoesCampaignHaveDuration() and numClaimed >= numRewards:
            if posInTrack < self.panelConst.SELECTED_CELL + bool(transitioning):
                posInTrack += numRewards
        if not self.panelConst.SHOW_NEXT_GIFT and not self.CanSomethingBeClaimedNow():
            posInTrack -= 1
            if posInTrack < 0:
                posInTrack = numRewards - 1
        return posInTrack

    def GetClaimedRewardForDay(self, trackNum):
        rewardIdx = trackNum + 1
        campaign_id = self.loginCampaignService.get_current_campaign_id()
        if not campaign_id:
            return None
        rewardsByCampaign = self.loginCampaignService.get_claimed_reward_for_reward_idx_by_campaign(rewardIdx)
        if campaign_id in rewardsByCampaign:
            return rewardsByCampaign[campaign_id]
        return itertoolsext.first_or_default(rewardsByCampaign.values(), None)

    def ShouldShowAsClaimed(self, rewardIdx, day):
        return rewardIdx > day

    def GetDaysToMarksAsClaimed(self, trackNum):
        rewardIdx = trackNum + 1
        return [ x for x in range(trackNum) if self.ShouldShowAsClaimed(rewardIdx, x) ]

    def ShouldAddOffsetToSelectedDay(self):
        if not self.panelConst.SELECTED_OFFSET:
            return False
        if self.CanSomethingBeClaimedNow():
            return False
        return True


class RookieLoginCampaignController(LoginCampaignController):

    def GetCongratsBodyText(self):
        machoNet = sm.GetService('machoNet')
        if GetLoginCampaignIDs(machoNet)['alpha'] or self.IsOmega() and GetLoginCampaignIDs(machoNet)['omega']:
            return GetByLabel('UI/LoginRewards/CongratulationsStartNewCampaign')
        return LoginCampaignController.GetCongratsBodyText(self)


class EvergreenLoginCampaignController(LoginCampaignController):

    def ShouldShowAsClaimed(self, rewardIdx, day):
        showAsClaimed = LoginCampaignController.ShouldShowAsClaimed(self, rewardIdx, day)
        if not showAsClaimed:
            return False
        campaign_id = self.loginCampaignService.get_current_campaign_id()
        rewardsByCampaign = self.loginCampaignService.get_claimed_reward_for_reward_idx_by_campaign(day + 1)
        if campaign_id not in rewardsByCampaign and rewardsByCampaign:
            return False
        return True


class SeasonalPanelController(BasePanelController):

    def __init__(self, seasonalLoginCampaignService, panelConst, isOmega):
        BasePanelController.__init__(self, panelConst, isOmega)
        self.seasonalLoginCampaignService = seasonalLoginCampaignService
        self.campaignDataByID = {}

    def CanRetroClaimNow(self):
        if not self.seasonalLoginCampaignService.can_retro_claim_now(self.isOmega):
            return False
        if self._HasClaimedToday():
            return True
        numRewardsClaimed = self.GetNumDaysClaimed()
        if numRewardsClaimed == self.GetRewardCount():
            return True
        return False

    def GetDayNumbersClaimedInOmegaTrack(self):
        return self.seasonalLoginCampaignService.get_day_numbers_claimed_in_omega_track()

    def GetDayNumbersClaimedInAlphaTrack(self):
        return self.seasonalLoginCampaignService.get_day_numbers_claimed_in_alpha_track()

    def CanSomethingBeClaimedNow(self):
        if not self._HasClaimedToday():
            return True
        return self.CanRetroClaimNow()

    def GetCampaignStatus(self):
        return self.seasonalLoginCampaignService.get_campaign_status(self.isOmega)

    def GetTimestampWhenRewardCanBeClaimed(self):
        return self.seasonalLoginCampaignService.get_timestamp_when_reward_can_be_claimed(self.isOmega)

    def GetNumberOfRewardsDaysRemainingAndAvailable(self):
        return self.seasonalLoginCampaignService.get_number_of_rewards_days_remaining_and_available()

    def GetNumDaysClaimed(self):
        return self.seasonalLoginCampaignService.get_number_of_claimed_rewards()

    def GetPositionInGridTrack(self):
        return self.seasonalLoginCampaignService.get_number_of_claimed_rewards()

    def GetCampaignData(self):
        campaignID = self.seasonalLoginCampaignService.get_active_login_campaign()
        campaignData = self.campaignDataByID.get(campaignID, None)
        if campaignData:
            return campaignData
        campaignData = self.seasonalLoginCampaignService.get_data_for_active_campaign()
        self.campaignDataByID[campaignID] = campaignData
        return campaignData

    def _GetDaysRemaining(self):
        return self.seasonalLoginCampaignService.get_days_remaining()

    def _GetEndTimestamp(self):
        return self.seasonalLoginCampaignService.get_end_time_timestamp()

    def GetCongratsHeaderText(self):
        campaignStatus = self.GetCampaignStatus()
        if campaignStatus == rewardUiConst.CAMPAIGN_STATUS_SUCCESSFULLY_COMPLETED:
            return GetByLabel('UI/LoginRewards/CampaignCompleted')
        return GetByLabel('UI/LoginRewards/CampaignEnding')

    def GetCongratsBodyText(self):
        campaignStatus = self.GetCampaignStatus()
        daysRemaining = self._GetDaysRemaining()
        if daysRemaining is None or campaignStatus == rewardUiConst.CAMPAIGN_STATUS_SUCCESSFULLY_COMPLETED:
            return ''
        else:
            campaignData = self.GetCampaignData()
            if daysRemaining > 1:
                return (GetByLabel('UI/LoginRewards/DaysRemaining', days=daysRemaining),)
            endTimestamp = self._GetEndTimestamp()
            endTime = max(0, endTimestamp - gametime.GetWallclockTime())
            campaignName = GetByLabel(campaignData.campaignName)
            text = GetByLabel('UI/LoginRewards/CampaignEndsIn', campaignName=campaignName, endTime=endTime)
            return text

    def ClaimReward(self):
        self.seasonalLoginCampaignService.claim_reward()

    def IsCampaignEndingBeforeNextReward(self):
        return self.seasonalLoginCampaignService.is_campaign_ending_before_next_reward(self.IsOmega())

    def HasActiveCampaignBeenCompleted(self):
        return self.seasonalLoginCampaignService.has_active_campaign_been_completed(self.IsOmega())

    def GetNextRewardDataForEntryType(self, entryType):
        return self.seasonalLoginCampaignService.get_next_reward_data_for_entry_type(entryType)

    def GetRewardCount(self):
        campaignData = self.GetCampaignData()
        rewardCount = min(len(campaignData.alphaRewards), len(campaignData.omegaRewards))
        return rewardCount

    def _HasClaimedToday(self):
        return self.seasonalLoginCampaignService.has_claimed_today()
