#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\client\seasonservice.py
import random
import blue
from carbon.common.script.sys.service import Service
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew import agencySignals
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
from eve.client.script.ui.shared.neocom.neocom.fixedButtonExtension import SeenItemStorage
from gametime import GetWallclockTime
from localization import GetByMessageID, GetByLabel
import logging
from loginrewards.client.rewardclaimfanfare import RewardFanfare
from seasons.client.neocombutton import SeasonsNeocomButton
from seasons.client.visibilityrestrictions import SeasonVisibilityRestrictions
from seasons.common.exceptions import ChallengeForCharacterNotFoundError
from seasons.common.util import get_multiple_seasons_fsd
import uthread2
from utillib import KeyVal
stdlog = logging.getLogger(__name__)
SETTINGS_KEY_SEASON_ID = 'SeenEventRewards_SeasonID'
SETTINGS_KEY_REWARDS = 'SeenEventRewards_Goals'
CHALLENGE_UPDATE_SLEEP_SECONDS = 1

class SeasonService(Service):
    __guid__ = 'svc.SeasonService'
    serviceName = 'svc.seasonService'
    __displayname__ = 'SeasonService'
    __servicename__ = 'SeasonService'
    __dependencies__ = ['audio',
     'cloneGradeSvc',
     'conversationService',
     'infoPanel',
     'michelle',
     'neocom',
     'cc']
    __notifyevents__ = ['OnChallengeCompleted',
     'OnChallengeRewardsGranted',
     'OnChallengeExpired',
     'OnSeasonalGoalsReset',
     'OnChallengeProgressUpdate',
     'OnSeasonalGoalCompleted',
     'OnSeasonalPointsUpdated',
     'ProcessSessionChange',
     'OnSeasonsFsdDataChanged',
     'OnSeasonStarted',
     'OnSeasonEnded',
     'OnSeasonOmegaRewardsClaimed',
     'OnSeasonSelected',
     'OnSeasonSelectionCleared']

    def __init__(self):
        self._initialized_for_character = None
        self.season_manager = None
        super(SeasonService, self).__init__()

    def ProcessSessionChange(self, _isRemote, _session, change):
        if 'charid' in change and change['charid'][1] is not None:
            self._initialize(character_id=change['charid'][1])

    def _initialize(self, character_id):
        if self._initialized_for_character == character_id:
            return
        self._initialized_for_character = character_id
        if self.season_manager is None:
            self.season_manager = sm.RemoteSvc('seasonManager')
        self._initialize_season()
        self._fetch_season_data()
        self._register_agency_button_in_neocom()
        self.visibility_restrictions = SeasonVisibilityRestrictions(self.cc, self._update_visibility)
        self._fetch_character_data(character_id)
        agencySignals.on_content_group_selected(contentGroupConst.contentGroupSeasons)

    def _initialize_season(self):
        self.current_season = None
        self.season_selection = None
        self.multiple_season_fsd = None
        self.current_user_progress = None
        self.update_challenge_thread = None
        self.notify_of_rewards_update_thread = None
        self._season_end_time_blue = None
        self._seen_rewards_storage_goals = None
        self.last_unclaimed_challenge_count = 0
        self.challenges_for_update = []
        self.challenges = {}

    def OnSeasonsFsdDataChanged(self):
        self.challenges = {}
        self.current_user_progress = self.season_manager.get_character_progress_by_character_id()

    def is_season_active(self):
        return self.current_season is not None

    def get_season_selection(self):
        return self.season_selection

    def select_season(self, season_id):
        self.season_manager.select_season(season_id)

    def get_challenge(self, challenge_id):
        if challenge_id is None:
            return
        try:
            if challenge_id not in self.challenges:
                self.challenges[challenge_id] = self.season_manager.get_challenge(challenge_id)
        except ChallengeForCharacterNotFoundError:
            self.challenges[challenge_id] = None

        return self.challenges[challenge_id]

    def get_active_challenges_by_character_id(self):
        self._fetch_character_data(session.charid)
        if self.current_user_progress:
            return self.current_user_progress.challenges.copy()
        return {}

    def get_max_active_challenges(self):
        return self.season_manager.get_max_active_challenges()

    def get_season_news(self):
        return GetByMessageID(self.current_season.news)

    def challenge_is_dormant(self, challenge_id):
        if challenge_id in self.current_user_progress.challenges:
            return self.current_user_progress.challenges[challenge_id].is_dormant
        return self.season_manager.challenge_is_dormant(challenge_id)

    def get_challenge_expiration_date(self, challenge_id):
        return self.season_manager.get_challenge_expiration_date(challenge_id)

    def get_season_end_time_blue(self):
        if not self._season_end_time_blue:
            self._season_end_time_blue = self.season_manager.get_season_end_time()
        return self._season_end_time_blue

    def get_season_remaining_time_text(self):
        remaining = self.get_season_end_time_blue() - blue.os.GetWallclockTime()
        return GetByLabel('UI/Seasons/TimeRemainingBlue', remaining=remaining)

    def get_points(self):
        return self.current_user_progress.seasonal_points

    def get_max_points(self):
        return self.current_user_progress.max_seasonal_points

    def get_rewards(self):
        return self.current_user_progress.seasonal_goals

    def get_next_reward(self):
        return self.current_user_progress.next_seasonal_goal

    def get_next_reward_loot(self):
        return self.season_manager.get_loot_table_by_typeID(self.current_user_progress.next_seasonal_goal['reward_type_id'])

    def get_last_reward(self):
        return self.current_user_progress.last_seasonal_goal

    def OnChallengeProgressUpdate(self, challenge_id, new_progress):
        func = self._update_challenge_progress
        args = (challenge_id, new_progress)
        self._add_to_update_challenges(func, args)

    def _ReplaceChallenge(self, challenge_id, new_challenge):
        if challenge_id not in self.current_user_progress.challenges:
            self.LogException('Replace challenge failed for challenge: %s - character: %s' % (str(challenge_id), str(session.charid)))
            return
        del self.current_user_progress.challenges[challenge_id]
        if new_challenge is not None:
            self.current_user_progress.challenges[new_challenge.challenge_id] = new_challenge

    def OnChallengeCompleted(self, challenge_id):
        func = self._complete_challenge
        args = (challenge_id,)
        self._add_to_update_challenges(func, args)
        self._notify_of_rewards_update()

    def OnChallengeRewardsGranted(self, challenge_id):
        self.current_user_progress.challenges[challenge_id].reward_date = GetWallclockTime()
        self._notify_of_rewards_update()
        sm.ScatterEvent('OnChallengeRewardsGrantedInClient', challenge_id)

    def have_required_clone_grade(self, goal_data):
        if not goal_data['omega_only']:
            return True
        return self.cloneGradeSvc.IsOmega()

    def _AdvanceSeasonalGoal(self):
        self.current_user_progress.next_seasonal_goal['completed'] = True
        if self.is_auto_claim_enabled() and self.have_required_clone_grade(self.current_user_progress.next_seasonal_goal):
            self.current_user_progress.next_seasonal_goal['claimed'] = True
        self._UpdateNextSeasonalGoal()

    def OnSeasonalGoalCompleted(self, goal_index, goal_data):
        self.current_user_progress.seasonal_goals[goal_index]['completed'] = True
        sm.GetService('neocom').Blink('agency', GetByLabel('Notifications/NotificationNames/SeasonalChallengeCompleted'))
        self._AdvanceSeasonalGoal()
        self._notify_of_rewards_update()
        sm.GetService('audio').SendUIEvent('scope_earn_rewards_play')
        sm.ScatterEvent('OnSeasonalGoalCompletedInClient', goal_index, goal_data)
        if self.is_auto_claim_enabled() and self.have_required_clone_grade(goal_data):
            self.mark_as_claimed(goal_index)

    def is_season_visible(self):
        return self.is_season_active() or self.is_selection_needed() and self.visibility_restrictions.is_season_visible()

    def is_season_visible_in_agency(self):
        return self.is_season_visible()

    def is_selection_needed(self):
        return self.season_selection is not None

    def multiple_seasons_running(self):
        return self.current_season.multiple_season_running

    def _update_visibility(self):
        self.infoPanel.UpdateChallengesPanel()
        self._agency_neocom_button.on_visible_changed(self._agency_neocom_button)

    def OnSeasonSelectionCleared(self):
        self._initialize_season()
        self._fetch_season_data()
        self._setup_neocom_extension()
        agencySignals.on_content_group_selected(contentGroupConst.contentGroupSeasons)
        sm.ScatterEvent('OnSeasonSelectionUpdated')

    def OnSeasonSelected(self, character_id, season_data, character_progress):
        self.season_selection = None
        self.update_current_season(season_data)
        if self.current_user_progress is None or self.current_user_progress.character_id != character_id:
            self.current_user_progress = character_progress
        self.last_unclaimed_challenge_count = self.get_number_of_unclaimed_challenge_rewards()
        self._setup_neocom_extension()
        agencySignals.on_content_group_selected(contentGroupConst.contentGroupSeasons)
        sm.ScatterEvent('OnSeasonSelectionUpdated')

    def update_current_season(self, season_data):
        self.current_season = season_data
        shortened_event_types = self.get_shortened_event_types(self.current_season.tracked_event_types)
        self.current_season.tracked_event_types = shortened_event_types

    def _fetch_season_data(self):
        season_data = self.season_manager.get_season_data_for_character()
        self.multiple_season_fsd = get_multiple_seasons_fsd()
        if season_data is None:
            return
        if isinstance(season_data, list):
            self.season_selection = season_data
            random.shuffle(self.season_selection)
        else:
            self.update_current_season(season_data)

    def _fetch_character_data(self, character_id):
        if character_id is None or not self.is_season_active():
            return
        if self.current_user_progress is None or self.current_user_progress.character_id != character_id:
            self.current_user_progress = self.season_manager.get_character_progress_by_character_id()
        self.last_unclaimed_challenge_count = self.get_number_of_unclaimed_challenge_rewards()
        self._setup_neocom_extension()

    def get_shortened_event_types(self, tracked_event_types):
        colon = ':'
        shortened_event_types = []
        for event_type in tracked_event_types:
            event_type = event_type[:event_type.find(colon)]
            shortened_event_types.append(event_type)

        return shortened_event_types

    def _UpdateNextSeasonalGoal(self):
        for goal in self.current_user_progress.seasonal_goals.values():
            if not goal['completed']:
                self.current_user_progress.next_seasonal_goal = goal
                return

        self.current_user_progress.next_seasonal_goal = None

    def OnSeasonalPointsUpdated(self, season_id, new_points):
        if season_id == self.current_season.season_id:
            self.current_user_progress.seasonal_points = new_points
            self._UpdateNextSeasonalGoal()
            sm.ScatterEvent('OnSeasonalPointsUpdatedInClient', new_points)
        else:
            self.LogWarn('Trying to update points for season %s which is not active' % season_id)

    def get_season_id(self):
        return self.current_season.season_id

    def OnChallengeExpired(self, challenge_id, new_challenge):
        func = self._expire_challenge
        args = (challenge_id, new_challenge)
        self._add_to_update_challenges(func, args)

    def OnSeasonalGoalsReset(self):
        sorted_goals = sorted(self.current_user_progress.seasonal_goals.keys())
        for goal_index in sorted_goals:
            self.current_user_progress.seasonal_goals[goal_index]['completed'] = False
            self.current_user_progress.seasonal_goals[goal_index]['claimed'] = False

        self.current_user_progress.seasonal_points = 0
        first_goal_key = sorted_goals[0]
        self.current_user_progress.next_seasonal_goal = self.current_user_progress.seasonal_goals[first_goal_key]
        self._notify_of_rewards_update()
        sm.ScatterEvent('OnSeasonalGoalsResetInClient')

    def _add_to_update_challenges(self, update_function, update_function_arguments):
        self.challenges_for_update.append((update_function, update_function_arguments))
        if self.update_challenge_thread is None or not self.update_challenge_thread.IsAlive():
            self.update_challenge_thread = uthread2.StartTasklet(self._update_challenges)

    def _update_challenges(self):
        while len(self.challenges_for_update):
            update_function, update_function_arguments = self.challenges_for_update.pop(0)
            update_function(*update_function_arguments)
            uthread2.sleep(CHALLENGE_UPDATE_SLEEP_SECONDS)

    def _expire_challenge(self, old_challenge_id, new_challenge):
        self._ReplaceChallenge(old_challenge_id, new_challenge)
        sm.ScatterEvent('OnChallengeExpiredInClient', old_challenge_id)

    def _complete_challenge(self, old_challenge_id):
        if old_challenge_id not in self.current_user_progress.challenges:
            stdlog.exception('Complete challenge failed for challenge: %s - character: %s.', old_challenge_id, session.charid)
            user_progress = self.season_manager.fill_up_and_return_challenges_for_character()
            self.current_user_progress.challenges = user_progress
        if old_challenge_id in self.current_user_progress.challenges:
            self.current_user_progress.challenges[old_challenge_id].is_dormant = True
            sm.GetService('audio').SendUIEvent('scope_complete_task_play')
            sm.ScatterEvent('OnChallengeCompletedInClient', old_challenge_id)

    def _update_challenge_progress(self, challenge_id, new_progress):
        try:
            self.current_user_progress.challenges[challenge_id].progress = new_progress
        except KeyError:
            stdlog.exception('Update progress failed for challenge: %s - character: %s.', challenge_id, session.charid)
            user_progress = self.season_manager.fill_up_and_return_challenges_for_character()
            self.current_user_progress.challenges = user_progress
            if challenge_id in user_progress:
                sm.ScatterEvent('OnChallengeProgressUpdateInClient', challenge_id, new_progress)
            return

        sm.ScatterEvent('OnChallengeProgressUpdateInClient', challenge_id, new_progress)

    def OnSeasonStarted(self):
        self._initialize_season()
        self._fetch_season_data()
        self._fetch_character_data(session.charid)
        self._setup_neocom_extension()
        self._update_visibility()
        agencySignals.on_content_group_selected(contentGroupConst.contentGroupSeasons)
        sm.ScatterEvent('OnSeasonSelectionUpdated')

    def OnSeasonEnded(self):
        self._initialize_season()
        self._setup_neocom_extension()
        self._update_visibility()
        self._clear_seen_rewards()
        agencySignals.on_content_group_selected(contentGroupConst.contentGroupSeasons)
        sm.ScatterEvent('OnSeasonSelectionUpdated')

    def claim_challenge_rewards(self, challenge, click_origin):
        if challenge.has_unclaimed_completion_rewards():
            self.season_manager.claim_challenge_rewards(challenge.challenge_id, click_origin)

    def get_challenges_with_unclaimed_rewards(self):
        if self.current_user_progress is None:
            return []
        challenges = self.current_user_progress.challenges.values()
        return [ challenge.challenge_id for challenge in challenges if challenge.has_unclaimed_completion_rewards() ]

    def get_number_of_unclaimed_challenge_rewards(self):
        return len(self.get_challenges_with_unclaimed_rewards())

    def ShowRewardFanfare(self, reward_data):
        rewards = [KeyVal(tier=3, typeID=reward_data['reward_type_id'], quantity=reward_data['reward_amount'], isOmegaOnly=reward_data['omega_only'])]
        agencyWnd = AgencyWndNew.GetIfOpen()
        if agencyWnd:
            isOmega = sm.GetService('cloneGradeSvc').IsOmega()
            RewardFanfare(parent=agencyWnd, align=uiconst.CENTER, state=uiconst.UI_NORMAL, padding=0, rewards=rewards, idx=0, width=agencyWnd.width, height=agencyWnd.height, isOmega=isOmega, isLoginReward=False)

    def is_client_event_interesting(self, event_type):
        return event_type in self.current_season.tracked_event_types

    def GetSeasonName(self):
        return GetByMessageID(self.current_season.title)

    def GetSeasonBanner(self):
        return self.current_season.background_no_logo

    def get_navigation_season_title(self):
        if self.is_selection_needed():
            return GetByMessageID(self.multiple_season_fsd.seasonSelectionTitleID)
        else:
            return GetByMessageID(self.current_season.title)

    def get_navigation_card_picture_path(self):
        if self.is_selection_needed() or self.multiple_seasons_running():
            return self.multiple_season_fsd.navigation_card_picture_path
        else:
            return self.current_season.navigation_card_picture_path

    def get_navigation_description(self):
        if self.is_selection_needed():
            return GetByMessageID(self.multiple_season_fsd.seasonSelectionDescriptionID)
        else:
            return GetByLabel('UI/Agency/ContentGroups/Descriptions/Seasons')

    def get_navigation_tooltip(self):
        if self.is_selection_needed():
            return GetByMessageID(self.multiple_season_fsd.seasonSelectionHintID)
        else:
            return GetByLabel('UI/Agency/Tooltips/NavigationCards/Seasons')

    def get_season_selection_large_title(self):
        return GetByMessageID(self.multiple_season_fsd.agencyLargeSeasonSelectionTitleID)

    def get_content_card_picture_path(self):
        return self.current_season.content_card_picture_path

    def get_start_time(self):
        return self.current_season.start_time

    def get_end_time(self):
        return self.current_season.end_time

    def _get_neocom_badge_count(self):
        if self._seen_rewards_storage_goals:
            return len(self._seen_rewards_storage_goals.get_items())
        return 0

    def _is_reward_claimable(self, goal):
        return goal['completed'] and not goal['claimed'] and (not goal['omega_only'] or self.cloneGradeSvc.IsOmega())

    def _get_claimable_rewards(self):
        if not self.is_season_active():
            return set()
        goal_rewards = {'g%d' % goal_index for goal_index in self.get_goals_with_unclaimed_rewards()}
        challenge_rewards = {'c%d' % challenge_id for challenge_id in self.get_challenges_with_unclaimed_rewards()}
        return goal_rewards.union(challenge_rewards)

    def get_goals_with_unclaimed_rewards(self):
        if self.current_user_progress is None:
            return []
        goals = self.current_user_progress.seasonal_goals
        return [ goal_index for goal_index, goal in goals.items() if self._is_reward_claimable(goal) ]

    def get_claimable_rewards_count(self):
        claimable_rewards = self._get_claimable_rewards()
        return len(claimable_rewards)

    def _setup_neocom_extension(self):
        if not self._seen_rewards_storage_goals:
            self._update_seen_rewards_for_season()
            self._seen_rewards_storage_goals = SeenItemStorage(get_items_function=self._get_claimable_rewards, settings_container=settings.user.ui, settings_key=SETTINGS_KEY_REWARDS)
            self._agency_neocom_button.connect_item_changes(self._seen_rewards_storage_goals.on_items_changed)
        if not self.is_season_active():
            self._clear_seen_rewards()

    def _notify_of_rewards_update(self):
        if self.is_season_active() and self._seen_rewards_storage_goals:
            self.notify_of_rewards_update_thread = AutoTimer(1000, self._notify_of_rewards_update_thread)

    def _notify_of_rewards_update_thread(self):
        try:
            if self._seen_rewards_storage_goals:
                self._seen_rewards_storage_goals.update_unseen_count()
                sm.ScatterEvent('OnEventRewardsUpdated')
        finally:
            self.notify_of_rewards_update_thread = None

    def _register_agency_button_in_neocom(self):
        self._agency_neocom_button = SeasonsNeocomButton(get_badge_count=self._get_neocom_badge_count)
        self.neocom.RegisterFixedButtonExtension(self._agency_neocom_button)

    def _update_seen_rewards_for_season(self):
        seen_rewards_season_id = settings.user.ui.Get(SETTINGS_KEY_SEASON_ID, None)
        current_season_id = self.get_season_id() if self.is_season_active() else None
        settings.user.ui.Set(SETTINGS_KEY_SEASON_ID, current_season_id)
        if seen_rewards_season_id != current_season_id:
            self._clear_seen_rewards()

    def _clear_seen_rewards(self):
        self.notify_of_rewards_update_thread = None
        settings.user.ui.Set(SETTINGS_KEY_REWARDS, set())
        sm.GetService('settings').SaveSettings()
        if self._seen_rewards_storage_goals:
            self._seen_rewards_storage_goals.on_items_changed()
        sm.ScatterEvent('OnEventRewardsUpdated')

    def claim_goal_reward(self, goal_index):
        if self.season_manager.claim_goal_reward(goal_index):
            self.mark_as_claimed(goal_index)
            return True
        return False

    def mark_as_claimed(self, goal_index):
        self.current_user_progress.seasonal_goals[goal_index]['claimed'] = True
        goal_reward_data = self.current_user_progress.seasonal_goals[goal_index]
        sm.ScatterEvent('OnSeasonalGoalClaimedInClient', goal_index, goal_reward_data)
        self._notify_of_rewards_update()
        self.ShowRewardFanfare(goal_reward_data)

    def has_goal_reward_been_claimed(self, goal_index):
        if goal_index not in self.current_user_progress.seasonal_goals:
            return False
        return self.current_user_progress.seasonal_goals[goal_index]['claimed']

    def has_goal_been_completed(self, goal_index):
        if goal_index not in self.current_user_progress.seasonal_goals:
            return False
        return self.current_user_progress.seasonal_goals[goal_index]['completed']

    def has_unclaimed_omega_rewards(self):
        goal_reward_list = self.current_user_progress.seasonal_goals.values()
        for goal in goal_reward_list:
            if goal['omega_only'] and goal['completed'] and not goal['claimed']:
                return True

        return False

    def is_auto_claim_enabled(self):
        return self.current_season.is_auto_claim_enabled

    def OnSeasonOmegaRewardsClaimed(self, claimed_goal_indexes):
        for index in claimed_goal_indexes:
            goal_reward_data = self.current_user_progress.seasonal_goals[index]
            goal_reward_data['claimed'] = True
            sm.ScatterEvent('OnSeasonalGoalClaimedInClient', index, goal_reward_data)

        self._notify_of_rewards_update()
