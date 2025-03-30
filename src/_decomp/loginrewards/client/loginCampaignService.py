#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\loginrewards\client\loginCampaignService.py
import gametime
import uthread2
from brennivin.itertoolsext import Bundle
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from crates import CratesStaticData
from eve.common.lib.appConst import DAY
from eve.client.script.ui.shared.loginRewards.neocomBtn import UnseenRewardsItemsExtension, RewardsBtnData
from eve.client.script.ui.shared.loginRewards.rewardInfo import RewardInfo
from eve.client.script.ui.shared.loginRewards.rewardUiConst import DLI_ENTRY, REWARD_EVERGREEN_BTN, REWARD_ROOKIE_BTN, REWARD_SEASONAL_BTN, REWARD_WND_OPEN_ON_LOGIN_SETTING
from neocom2.btnIDs import LOGIN_REWARDS_ID
from eve.client.script.ui.shared.neocom.neocom.fixedButtonExtension import SeenItemStorage
from eve.client.script.ui.shared.pointerTool.pointerToolConst import GetUniqueNeocomPointerName
from eveexceptions import ExceptionEater
from localization import GetByLabel
from loginrewards.client.commands import BlinkLoginRewardWindowOnDock
from loginrewards.client.util import open_vgs_to_buy_omega_time
from loginrewards.common.rewardUtils import GetClaimState
from uthread import CriticalSection
STATE_UNKOWN = 'UNKOWN'
POINTER_SETTING_NAME = 'hasShownPointerToLoginRewardWnd'
CLAIMED_BY_IDX = 'DLI_claimedRewardsByIdx3'

class LoginCampaignService(Service):
    __guid__ = 'svc.loginCampaignService'
    serviceName = 'svc.loginCampaignService'
    __displayname__ = 'loginCampaignService'
    __servicename__ = 'Login Campaign Service'
    __notifyevents__ = ['OnLoginRewardWindowOpened',
     'OnRedeemWndOpened',
     'OnUiHighlightDeleted',
     'OnCampaignEnrollmentChanged',
     'OnDailyRewardClaimed',
     'OnSubscriptionChanged',
     'OnSessionReset',
     'OnCharacterSessionChanged']
    __dependencies__ = []

    def __init__(self):
        super(LoginCampaignService, self).__init__()
        self._window_forced_closed = False
        self._campaignState = STATE_UNKOWN
        self._remote_campaign_manager = None
        self.campaign_lock = CriticalSection()
        self.last_claimed_reward_by_reward_idx = {}
        self._reward_notification_extension = None
        self._seen_rewards_storage = None
        self.pointersDisplayed = set()
        self._blink_on_dock = BlinkLoginRewardWindowOnDock()

    def Run(self, *args, **kwargs):
        Service.Run(self, *args, **kwargs)
        self.ReInitialize()
        self._remote_campaign_manager = sm.RemoteSvc('loginCampaignManager')
        uthread2.StartTasklet(self.CreateNotificationExtension)

    def ReInitialize(self):
        self._campaignState = STATE_UNKOWN
        self.pointersDisplayed = set()

    def OnSessionReset(self):
        self.ReInitialize()
        self.RegisterNotificationExtension()

    def OnCharacterSessionChanged(self, _oldCharacterID, newCharacterID):
        if newCharacterID is not None:
            self.RegisterNotificationExtension()

    def OnSubscriptionChanged(self):
        self._flush_campaign_state()
        sm.ScatterEvent('OnSubscriptionChanged_Local')

    def OnCampaignEnrollmentChanged(self):
        self._flush_campaign_state()
        self.last_claimed_reward_by_reward_idx.clear()
        settings.user.ui.Set(CLAIMED_BY_IDX, self.last_claimed_reward_by_reward_idx)

    def CreateNotificationExtension(self):
        self._seen_rewards_storage = SeenItemStorage(get_items_function=self.get_rewards_available, settings_container=settings.user.ui, settings_key='RewardsWindow_seen')
        self._reward_notification_extension = UnseenRewardsItemsExtension(button_data_class=RewardsBtnData, get_badge_count=lambda : len(self._seen_rewards_storage.get_items()), is_visible_function=self.should_reward_btn_be_visible)
        self._reward_notification_extension.connect_item_changes(self._seen_rewards_storage.on_items_changed)
        self.ClearSeenSettings()
        self.RegisterNotificationExtension()

    def RegisterNotificationExtension(self):
        try:
            sm.GetService('neocom').RegisterFixedButtonExtension(self._reward_notification_extension)
        except ValueError:
            pass

    def _get_campaign_state(self):
        try:
            if self._campaignState == STATE_UNKOWN:
                with self.campaign_lock:
                    if self._campaignState == STATE_UNKOWN:
                        self._campaignState = self._remote_campaign_manager.get_client_campaign_state()
                        claimed_reward_from_setting = settings.user.ui.Get(CLAIMED_BY_IDX, {})
                        self.last_claimed_reward_by_reward_idx.update(claimed_reward_from_setting)
        except IndexError:
            import log
            log.LogException()
            self._campaignState = None

        return self._campaignState

    def _flush_campaign_state(self):
        self._campaignState = STATE_UNKOWN

    def get_active_campaign(self):
        return self._get_campaign_state()

    def get_campaign_static_data(self):
        campaignState = self._get_campaign_state()
        if campaignState:
            return campaignState.static_data

    def get_current_campaign_id(self):
        static_data = self.get_campaign_static_data()
        if not static_data:
            return None
        return static_data.campaign_id

    def get_item_rewards_by_day(self):
        static_data = self.get_campaign_static_data()
        if static_data:
            return static_data.item_rewards_by_day

    def _get_campaign_item_progress(self):
        campaignState = self._get_campaign_state()
        if campaignState:
            return campaignState.item_progress

    def get_next_reward_time(self):
        campaignState = self._get_campaign_state()
        if campaignState:
            return campaignState.item_progress.next_reward_timestamp

    def get_num_claimed_rewards(self):
        campaignState = self._get_campaign_state()
        if campaignState:
            return campaignState.item_progress.num_claimed_rewards

    def get_next_reward_index(self):
        campaignState = self._get_campaign_state()
        if campaignState:
            return campaignState.item_progress.next_reward_index

    def does_campaign_have_duration(self):
        data = self.get_campaign_static_data()
        if not data or data.campaign_duration is None:
            return False
        return True

    def is_rookie_campaign(self):
        data = self.get_campaign_static_data()
        if not data or data.is_rookie_campaign is None:
            return False
        return data.is_rookie_campaign

    def get_campaign_reward_idx(self):
        campaignState = self._get_campaign_state()
        if campaignState:
            return campaignState.item_progress.next_reward_index
        return 1

    def can_claim_now(self):
        campaignState = self._get_campaign_state()
        if campaignState:
            now = gametime.GetWallclockTime()
            return campaignState.item_progress.next_reward_timestamp < now
        return False

    def claim_reward(self):
        reward_idx_before_claim = self._campaignState.item_progress.next_reward_index
        with self.campaign_lock:
            result = self._remote_campaign_manager.claim_reward()
        if result is None:
            return
        item_reward, updated_item_progress, received_bucket_typeID, updated_bucket_progress = result
        self._campaignState.item_progress = updated_item_progress
        self._campaignState.bucket_progress = updated_bucket_progress
        self.last_claimed_reward_by_reward_idx.clear()
        campaign_id = self.get_current_campaign_id()
        self.last_claimed_reward_by_reward_idx[campaign_id, reward_idx_before_claim, session.userid] = (item_reward, gametime.GetWallclockTime())
        settings.user.ui.Set(CLAIMED_BY_IDX, self.last_claimed_reward_by_reward_idx)
        self.ClearSeenSettings(tokensToClear={REWARD_ROOKIE_BTN})
        sm.ScatterEvent('OnDailyCampaignAwardClaimed', item_reward, updated_item_progress, received_bucket_typeID, updated_bucket_progress)

    def get_claimed_reward_for_reward_idx_by_campaign(self, reward_idx):
        try:
            oneDayAgo = gametime.GetWallclockTime() - DAY
            return {k[0]:v[0] for k, v in self.last_claimed_reward_by_reward_idx.iteritems() if k[2] == session.userid and k[1] == reward_idx and v[1] > oneDayAgo}
        except KeyError:
            import log
            log.LogException()
            return {}

    def should_open_reward_window_on_login(self):
        if not self.can_claim_now():
            return False
        if REWARD_WND_OPEN_ON_LOGIN_SETTING.is_enabled():
            return True
        return False

    def is_user_enrolled_in_campaign(self):
        if not session.userid:
            return False
        return bool(self._get_campaign_state())

    def try_displaying_rookie_reward_pointer(self):
        with ExceptionEater('try_displaying_rookie_reward_pointer'):
            if not self.is_user_enrolled_in_campaign():
                return
            if not self.can_claim_now():
                return
            if settings.user.ui.Get(POINTER_SETTING_NAME, False):
                return
            uthread2.call_after_wallclocktime_delay(self._show_ui_reward_wnd_pointer, 5)

    def _show_ui_reward_wnd_pointer(self):
        elementName = GetUniqueNeocomPointerName(LOGIN_REWARDS_ID)
        settings.user.ui.Set(POINTER_SETTING_NAME, True)
        self.pointersDisplayed.add(elementName)
        sm.GetService('uiHighlightingService').highlight_ui_element_by_name(ui_element_name=elementName, message=GetByLabel('UI/LoginRewards/WindowDescription'), title=GetByLabel('UI/LoginRewards/WindowCaption'))

    def OnLoginRewardWindowOpened(self):
        settings.user.ui.Set(POINTER_SETTING_NAME, True)
        elementName = GetUniqueNeocomPointerName(LOGIN_REWARDS_ID)
        self._kill_ui_pointer(elementName)

    def OnRedeemWndOpened(self):
        elementName = GetUniqueNeocomPointerName('newRedeemableItemsNotification')
        self._kill_ui_pointer(elementName)

    def OnUiHighlightDeleted(self, ui_highlight_name):
        self.pointersDisplayed.discard(ui_highlight_name)

    def _kill_ui_pointer(self, elementName):
        if elementName not in self.pointersDisplayed:
            return
        self.pointersDisplayed.discard(elementName)
        sm.GetService('uiHighlightingService').clear_ui_highlighting_for_element(elementName)

    def get_rewards_available(self):
        if not session.userid:
            return set()
        availableSet = set()
        if self.can_claim_now():
            if self.is_rookie_campaign():
                availableSet.add(REWARD_ROOKIE_BTN)
            else:
                availableSet.add(REWARD_EVERGREEN_BTN)
        if sm.GetService('seasonalLoginCampaignService').can_claim_now():
            availableSet.add(REWARD_SEASONAL_BTN)
        return availableSet

    def has_unseen_rewards(self):
        return self._seen_rewards_storage.has_unseen()

    def AddSeenSettingValue(self, value):
        self._seen_rewards_storage.mark_as_seen(value)

    def ClearSeenSettings(self, tokensToClear = None):
        self._seen_rewards_storage.mark_all_unseen()

    def should_reward_btn_be_visible(self):
        if self.is_user_enrolled_in_campaign():
            return True
        return sm.GetService('seasonalLoginCampaignService').is_login_campaign_active()

    def OnDailyRewardClaimed(self, *args, **kwargs):
        self.ClearSeenSettings(tokensToClear={REWARD_SEASONAL_BTN})

    def should_reopen_DLI_window(self):
        if not self.should_reward_btn_be_visible():
            return
        if self._window_forced_closed:
            self._window_forced_closed = False
            return True
        return False

    def get_next_rewards_to_claim_both_campaigns(self):
        rewards = []
        if not self.should_reward_btn_be_visible():
            return rewards
        rewards += self.get_next_rewards_to_claim()
        rewards += sm.GetService('seasonalLoginCampaignService').get_next_rewards_to_claim()
        return rewards

    def get_next_rewards_to_claim(self):
        reward_data_available = []
        if self.is_user_enrolled_in_campaign():
            next_reward_data = self.get_next_reward_data()
            reward_data_available.append(next_reward_data)
        return reward_data_available

    def get_next_reward_data(self):
        next_day = self.get_next_reward_index()
        next_reward = self.get_item_rewards_by_day().get(next_day)
        reward_data = Bundle(campaignNameID=self.get_campaign_static_data().titleMessageID, numClaimed=self.get_num_claimed_rewards(), totalRewards=len(self.get_item_rewards_by_day()), rewardInfo=None, entryType=DLI_ENTRY, nextRewardTime=self.get_next_reward_time())
        if next_reward:
            can_be_claimed = self.get_next_reward_time() < gametime.GetWallclockTime()
            claim_state = GetClaimState(isClaimed=False, isNextClaimable=True, somethingCanBeClaimedNow=can_be_claimed)
            displayNameID = CratesStaticData().get_crate_nameID(next_reward.typeID)
            reward_info = RewardInfo(next_day, next_reward, claimState=claim_state, messageID=next_reward.labelMessageID, displayNameID=displayNameID)
            reward_data.rewardInfo = reward_info
        return reward_data

    def open_vgs_to_buy_omega_time_from_DLI(self, *args):
        if session.charid is None:
            from eve.client.script.ui.shared.loginRewards.loginRewardsWnd import DailyLoginRewardsWnd
            wnd = DailyLoginRewardsWnd.GetIfOpen()
            if wnd and wnd.isModal:
                self._window_forced_closed = True
                wnd.SetModalResult(uiconst.ID_CLOSE)
        open_vgs_to_buy_omega_time()

    def blink_reward_window_on_dock(self):
        self._blink_on_dock.enable()
