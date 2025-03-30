#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\loginrewards\client\seasonalLoginCampaignService.py
import logging
from datetime import date, datetime
import clonegrade
import evetypes
from brennivin.itertoolsext import Bundle
from caching import Memoize
from carbon.common.script.sys.service import Service
from crates import CratesStaticData
from eve.client.script.ui.shared.loginRewards import rewardUiConst
from eve.client.script.ui.shared.loginRewards.rewardInfo import RewardInfo
from eve.client.script.ui.shared.loginRewards.rewardUiConst import ALPHA_SEASONAL_ENTRY, OMEGA_SEASONAL_ENTRY, REWARD_WND_OPEN_ON_LOGIN_SETTING
from loginrewards.common.const import TIME_STRING_FORMAT
from loginrewards.common.fsdloaders import SeasonalCampaignsStaticData
from loginrewards.common.rewardUtils import GetClaimState
from loginrewards.common.timekeeper import TimeKeeper
stdlog = logging.getLogger(__name__)
CHALLENGE_UPDATE_SLEEP_SECONDS = 1

class SeasonalLoginCampaignService(Service):
    __guid__ = 'svc.seasonalLoginCampaignService'
    serviceName = 'svc.seasonalLoginCampaignService'
    __displayname__ = 'seasonalLoginCampaignService'
    __servicename__ = 'Seasonal Login Campaign Service'
    __notifyevents__ = []
    __dependencies__ = ['cloneGradeSvc']

    def Run(self, *args, **kwargs):
        self.seasonalCampaignsStaticData = SeasonalCampaignsStaticData()
        self.remote_reward_manager = sm.RemoteSvc('seasonalLoginCampaignManager')
        self.remote_reward_facilities = sm.RemoteSvc('loginRewardFacilities')
        self.prime_campaign_data()
        Service.Run(self, *args, **kwargs)

    def prime_campaign_data(self):
        self.active_login_reward_campaign_id = None
        self.end_date = None
        self.claim_history = None
        self.number_of_reward_days_remaining = None
        campaign_id, end_date_ordinal, turnover_time_str, num_remaining_rewards = self.remote_reward_manager.get_active_campaign()
        if campaign_id is not None:
            self.active_login_reward_campaign_id = campaign_id
            self.end_date = date.fromordinal(end_date_ordinal)
            turnover_time = datetime.strptime(turnover_time_str, TIME_STRING_FORMAT).time()
            self.number_of_reward_days_remaining = num_remaining_rewards
            self.time_keeper = TimeKeeper(utc_campaign_start_hours=turnover_time.hour, utc_campaign_start_minutes=turnover_time.minute)

    def is_login_campaign_active(self):
        return self.active_login_reward_campaign_id is not None

    def get_active_login_campaign(self):
        return self.active_login_reward_campaign_id

    def is_retroactive_claiming_enabled(self):
        if self.active_login_reward_campaign_id is None:
            return False
        campaign_data = self.seasonalCampaignsStaticData.get_campaign(self.active_login_reward_campaign_id)
        return campaign_data.retroClaim or False

    def _add_rewards_to_history(self):
        retroactive_count = 0
        clone_grade = self.get_my_clone_grade()
        self.claim_history[self.time_keeper.get_current_reward_date()] = clone_grade
        if clone_grade == clonegrade.CLONE_STATE_OMEGA:
            if self.is_retroactive_claiming_enabled():
                for day in self.claim_history:
                    if self.claim_history[day] == clonegrade.CLONE_STATE_ALPHA:
                        retroactive_count += 1
                    self.claim_history[day] = clone_grade

        self.number_of_reward_days_remaining -= 1
        return retroactive_count

    def claim_reward(self):
        if self.has_claimed_today() and not self.is_retroactive_claiming_enabled():
            return False
        todays_alpha_rewards, todays_omega_rewards, retroactive_rewards = self.get_available_rewards()
        success = self.remote_reward_manager.claim_reward()
        if success:
            self._add_rewards_to_history()
            sm.ScatterEvent('OnDailyRewardClaimed', todays_alpha_rewards, todays_omega_rewards, retroactive_rewards)
        return success

    def get_claim_history(self):
        if self.claim_history is None:
            self.claim_history = {}
            unconverted_claim_history = self.remote_reward_manager.get_claim_history()
            for date_ordinal, clone_grade in unconverted_claim_history.iteritems():
                self.claim_history[date.fromordinal(date_ordinal)] = clone_grade

        return self.claim_history

    def get_available_rewards(self):
        if self.active_login_reward_campaign_id is None:
            return ([], [])
        todays_alpha_rewards = []
        todays_omega_rewards = []
        retroactive_rewards = []
        campaign = self.seasonalCampaignsStaticData.get_campaign(self.active_login_reward_campaign_id)
        alpha_rewards = campaign.alphaRewards
        omega_rewards = campaign.omegaRewards
        claim_history = self.get_claim_history()
        is_omega = self.is_omega()
        is_retroactive_claiming_enabled = self.is_retroactive_claiming_enabled()
        current_reward_date = self.time_keeper.get_current_reward_date()
        previously_claimed_day_count = 0
        for day in sorted(claim_history.keys()):
            if day == current_reward_date:
                continue
            if claim_history[day] == clonegrade.CLONE_STATE_ALPHA:
                if is_omega and is_retroactive_claiming_enabled:
                    retroactive_rewards.append(omega_rewards[previously_claimed_day_count])
            previously_claimed_day_count += 1

        if self.has_claimed_today():
            if is_omega and claim_history[current_reward_date] == clonegrade.CLONE_STATE_ALPHA:
                todays_omega_rewards.append(omega_rewards[previously_claimed_day_count])
        else:
            if previously_claimed_day_count in alpha_rewards:
                todays_alpha_rewards.append(alpha_rewards[previously_claimed_day_count])
            if is_omega:
                if previously_claimed_day_count in omega_rewards:
                    todays_omega_rewards.append(omega_rewards[previously_claimed_day_count])
        return (todays_alpha_rewards, todays_omega_rewards, retroactive_rewards)

    def get_data_for_active_campaign(self):
        return self.seasonalCampaignsStaticData.get_campaign(self.active_login_reward_campaign_id)

    def has_claimed_today(self):
        return self.time_keeper.get_current_reward_date() in self.get_claim_history()

    def get_days_claimed_before_today(self):
        return self.get_number_of_claimed_rewards() - self.has_claimed_today()

    def get_days_remaining(self):
        return self.end_date.toordinal() - self.time_keeper.get_current_reward_date().toordinal()

    def get_number_of_reward_days_remaining(self):
        return self.number_of_reward_days_remaining

    def get_number_of_rewards_days_remaining_and_available(self):
        if self.has_claimed_today():
            num_days_left_in_campaign = self.end_date.toordinal() - self.time_keeper.get_next_reward_date().toordinal()
        else:
            num_days_left_in_campaign = self.get_days_remaining()
        return min(self.get_number_of_reward_days_remaining(), num_days_left_in_campaign)

    def get_hours_until_next_reward_date(self):
        return self.time_keeper.get_hours_until_next_reward_date()

    def get_next_reward_date(self):
        return self.time_keeper.get_next_reward_date()

    def get_timestamp_when_reward_can_be_claimed(self, isOmega):
        next_claim_date = self.get_date_when_reward_can_be_claimed(isOmega)
        from carbon.common.script.util.format import DateToBlue
        next_claim_timestamp = DateToBlue(next_claim_date)
        return next_claim_timestamp

    def get_date_when_reward_can_be_claimed(self, isOmega):
        if self.has_claimed_today() and not self.can_retro_claim_now(isOmega):
            next_claim_date = self.get_next_reward_date()
        else:
            current_date = self.time_keeper.get_current_reward_date()
            next_claim_date = datetime.combine(current_date, datetime.min.time())
        return next_claim_date

    def get_end_time_timestamp(self):
        from carbon.common.script.util.format import DateToBlue
        end = self.get_end_date_with_time()
        return DateToBlue(end)

    def get_end_date_with_time(self):
        return datetime.combine(self.end_date, self.time_keeper.dateline)

    def is_campaign_ending_before_next_reward(self, isOmega):
        can_be_claimed_date = self.get_date_when_reward_can_be_claimed(isOmega)
        end_date = self.get_end_date_with_time()
        return can_be_claimed_date >= end_date

    def has_active_campaign_been_completed(self, isOmega = None):
        campaignData = self.get_data_for_active_campaign()
        totalRewardCount = min(len(campaignData.alphaRewards), len(campaignData.omegaRewards))
        num_claimed = self.get_number_of_claimed_rewards()
        if num_claimed >= totalRewardCount:
            if self.can_retro_claim_now(isOmega):
                return False
            return True
        return False

    def get_number_of_claimed_rewards(self):
        return len(self.get_claim_history())

    def user_has_unclaimed_rewards(self):
        if self.is_login_campaign_active():
            if self.get_number_of_reward_days_remaining() > 0:
                return True
        todays_alpha_rewards, todays_omega_rewards, retro_rewards = self.get_available_rewards()
        return bool(todays_alpha_rewards or todays_omega_rewards or retro_rewards)

    def is_omega(self):
        return self.get_my_clone_grade() == clonegrade.CLONE_STATE_OMEGA

    def get_my_clone_grade(self):
        if session.charid:
            return self.cloneGradeSvc.GetCloneGrade()
        return self._get_my_clone_grade_from_sever()

    @Memoize(2)
    def _get_my_clone_grade_from_sever(self):
        return self.remote_reward_facilities.get_my_clone_grade()

    def get_clone_track_by_day_claimed(self):
        historyList = self.get_claim_history().items()
        orderedHistory = sorted(historyList, key=lambda z: z[0])
        claimingCloneGradeByDay = {day_num:dateAndGrade[1] for day_num, dateAndGrade in enumerate(orderedHistory)}
        return claimingCloneGradeByDay

    def get_day_numbers_claimed_in_alpha_track(self):
        track_by_day = self.get_clone_track_by_day_claimed()
        return sorted([ day_num for day_num, grade in track_by_day.iteritems() if grade >= clonegrade.CLONE_STATE_ALPHA ])

    def get_day_numbers_claimed_in_omega_track(self):
        track_by_day = self.get_clone_track_by_day_claimed()
        return sorted([ day_num for day_num, grade in track_by_day.iteritems() if grade >= clonegrade.CLONE_STATE_OMEGA ])

    def has_fewer_omega_rewards_than_total(self):
        num_omega_rewards = len(self.get_day_numbers_claimed_in_omega_track())
        num_rewards = self.get_number_of_claimed_rewards()
        return num_omega_rewards < num_rewards

    def can_retro_claim_now(self, isOmega):
        if not isOmega:
            return False
        if not self.is_retroactive_claiming_enabled():
            return False
        if self.has_fewer_omega_rewards_than_total():
            return True

    def should_open_reward_window_on_login(self):
        if not self.can_claim_now():
            return False
        if REWARD_WND_OPEN_ON_LOGIN_SETTING.is_enabled():
            return True
        return False

    def can_claim_now(self):
        if not self.is_login_campaign_active():
            return False
        if self.has_claimed_today():
            return False
        if self.user_has_unclaimed_rewards():
            return True
        return False

    def get_next_rewards_to_claim(self):
        if not self.is_login_campaign_active():
            return []
        reward_data_available = []
        data_for_alpha = self.get_next_reward_data_for_entry_type(ALPHA_SEASONAL_ENTRY)
        reward_data_available.append(data_for_alpha)
        if self.is_omega():
            data_for_omega = self.get_next_reward_data_for_entry_type(OMEGA_SEASONAL_ENTRY)
            reward_data_available.append(data_for_omega)
        return reward_data_available

    def get_next_reward_data_for_entry_type(self, entry_type):
        campaign_data = self.get_data_for_active_campaign()
        if entry_type == ALPHA_SEASONAL_ENTRY:
            r_collection = campaign_data.alphaRewards
        else:
            r_collection = campaign_data.omegaRewards
        numRewardsClaimed = self.get_number_of_claimed_rewards()
        reward_data = Bundle(campaignNameID=campaign_data.campaignName, numClaimed=numRewardsClaimed, totalRewards=len(r_collection), rewardInfo=None, entryType=entry_type)
        if self.has_active_campaign_been_completed():
            return reward_data
        if self.is_campaign_ending_before_next_reward(self.is_omega):
            return reward_data
        can_claim = self.can_claim_now()
        num_rewards_claimed = self.get_number_of_claimed_rewards()
        cratesStaticData = CratesStaticData()
        for day, info in r_collection.iteritems():
            is_next_claimable = num_rewards_claimed == day
            if is_next_claimable:
                claim_state = GetClaimState(False, True, can_claim)
                messageID = evetypes.GetDescriptionID(info.typeID)
                displayNameID = cratesStaticData.get_crate_nameID(info.typeID)
                rInfo = RewardInfo(day + 1, info, claim_state, messageID, displayNameID=displayNameID)
                reward_data.rewardInfo = rInfo

        return reward_data

    def get_campaign_status(self, isOmega):
        is_campaign_successfully_completed = self.has_active_campaign_been_completed(isOmega)
        if is_campaign_successfully_completed:
            return rewardUiConst.CAMPAIGN_STATUS_SUCCESSFULLY_COMPLETED
        is_campaign_ending = self.is_campaign_ending_before_next_reward(isOmega)
        if is_campaign_ending:
            return rewardUiConst.CAMPAIGN_STATUS_ENDING
        return rewardUiConst.CAMPAIGN_STATUS_ONGOING
