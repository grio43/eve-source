#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\job.py
import caching
import eveicon
import math
import uthread
from carbonui.control.contextMenu.menuUtil import CloseContextMenus
from carbonui.control.contextMenu.menuData import MenuData
from metadata import ContentTags, get_content_tag_as_object
from metadata.common.content_tags.const import CAREER_PATH_TO_CONTENT_TAG_ID
from utillib import KeyVal
from dailygoals.client.goalsController import DailyGoalsController
from dailygoals.client.qa import get_job_qa_menu_entries, get_reward_qa_menu_entries
from dailygoals.client.const import DailyGoalCategory, RewardType, CAREER_PATH_SORT_ORDER
from jobboard.client.job import BaseJob
from jobboard.client.qa_tools import is_qa
from jobboard.client.job_board_settings import redeem_to_current_location
from .claim_button import DailyGoalClaimButton
from .card import DailyGoalCard, DailyGoalListEntry, DailyGoalRewardListEntry
from .completion_convenience.ui.button import CompletionConvenienceButton
from .page import DailyGoalPage

class DailyGoalJob(BaseJob):
    CARD_CLASS = DailyGoalCard
    PAGE_CLASS = DailyGoalPage
    LIST_ENTRY_CLASS = DailyGoalListEntry
    REWARD_LIST_ENTRY_CLASS = DailyGoalRewardListEntry

    def __init__(self, job_id, provider, daily_goal):
        self._daily_goal = daily_goal
        self._objectives_context = None
        content_id = daily_goal.get_id()
        self._qa_progress_setting = None
        super(DailyGoalJob, self).__init__(job_id, content_id, provider)

    def __del__(self):
        if self._qa_progress_setting:
            self._qa_progress_setting.on_change.disconnect(self._on_qa_progress_setting_changed)
            self._qa_progress_setting = None

    @property
    def sort_value(self):
        if self.goal and self.goal.get_career_path():
            return CAREER_PATH_SORT_ORDER.get(self.goal.get_career_path(), 99)
        return 99

    def update(self, *args, **kwargs):
        self._update_context()
        super(DailyGoalJob, self).update(*args, **kwargs)

    @property
    def title(self):
        return self._daily_goal.get_name()

    @property
    def description(self):
        return self._daily_goal.get_description()

    @property
    def help_text(self):
        return self._daily_goal.get_help_text()

    @property
    def goal_id(self):
        return self._daily_goal.get_id()

    @property
    def contribution_method(self):
        return self._daily_goal.get_contribution_method()

    @property
    def current_progress(self):
        return self._daily_goal.get_current_progress()

    @property
    def desired_progress(self):
        return self._daily_goal.get_target_progress()

    @property
    def target_progress(self):
        return self.desired_progress

    @property
    def progress_percentage(self):
        return float(self.current_progress) / self.desired_progress

    @property
    def is_completed(self):
        return self._daily_goal.is_completed()

    @property
    def rewards(self):
        return self._daily_goal.rewards

    @property
    def has_claimable_rewards(self):
        has_claimable_rewards = self._daily_goal.has_unclaimed_rewards()
        if has_claimable_rewards and not sm.GetService('cloneGradeSvc').IsOmega():
            return not self._daily_goal.are_rewards_omega_restricted()
        return has_claimable_rewards

    @property
    def has_unclaimed_omega_restricted_rewards(self):
        return self.is_omega_restricted and self.are_rewards_omega_restricted and self._daily_goal.has_unclaimed_rewards()

    @property
    def claimable_rewards(self):
        return self._daily_goal.get_claimable_rewards()

    @property
    def has_claimable_item_reward(self):
        if not self.has_claimable_rewards:
            return False
        return any((reward.reward_type == RewardType.ITEM for reward in self.claimable_rewards))

    @property
    def are_rewards_omega_restricted(self):
        return self._daily_goal.are_rewards_omega_restricted()

    @property
    def expiration_time(self):
        return self._daily_goal.expiration_time

    @property
    def is_expired(self):
        return self._daily_goal.is_expired

    @property
    def is_omega_restricted(self):
        return self._daily_goal.is_omega_restricted

    @property
    def category(self):
        return self.goal.get_category()

    def _has_data(self):
        return self._daily_goal.has_data()

    @property
    def is_available_in_browse(self):
        if not self._has_data():
            return False
        if self.category != DailyGoalCategory.CATEGORY_DAILY:
            return False
        if self.is_expired:
            return False
        if self.is_completed and not self.has_claimable_rewards:
            return False
        return super(DailyGoalJob, self).is_available_in_browse

    @property
    def is_available_in_active(self):
        if not self._has_data():
            return False
        if self.category != DailyGoalCategory.CATEGORY_DAILY:
            return False
        return self.is_active or self.is_tracked

    @property
    def is_active(self):
        return self.current_progress and not self.is_completed

    @property
    def is_trackable(self):
        if self.category != DailyGoalCategory.CATEGORY_DAILY:
            return False
        return not self.is_completed and not self.is_removed

    @caching.lazy_property
    def objective_chain(self):
        from objectives.client.objective_chain import ObjectiveChain
        from objectives.common.objective_context import ObjectivesContext
        objective_chain_id = 54
        contribution_method = self.contribution_method
        if contribution_method.icon:
            icon_id = contribution_method.icon.icon_id
        else:
            icon_id = eveicon.more_horizontal.icon_id
        self._objectives_context = ObjectivesContext()
        self._update_context()
        objective_chain = ObjectiveChain(content_id=objective_chain_id, context=self._objectives_context, overrides={'progress': KeyVal(title=contribution_method.title_id, taskOverrides={'progress': KeyVal(icon=icon_id)})})
        objective_chain.start()
        return objective_chain

    def get_cta_buttons(self):
        return [DailyGoalClaimButton(name='claim_button', job=self), CompletionConvenienceButton(name='cc_button', job=self)]

    def _get_content_tag_ids(self):
        result = [ContentTags.feature_daily_goals]
        if self.goal.get_career_path():
            result.append(CAREER_PATH_TO_CONTENT_TAG_ID.get(self.goal.get_career_path()))
        result.extend([ content_tag_id for content_tag_id in self.contribution_method.content_tags if content_tag_id not in (ContentTags.career_path_enforcer,
         ContentTags.career_path_explorer,
         ContentTags.career_path_industrialist,
         ContentTags.career_path_soldier_of_fortune) ])
        return result

    def _update_context(self):
        if not self._objectives_context:
            return
        self._objectives_context.update_value(key='target_progress', value=self.target_progress)
        self._objectives_context.update_value(key='current_progress', value=self.current_progress)

    @property
    def goal(self):
        return self._daily_goal

    def claim_rewards(self):
        DailyGoalsController.get_instance().redeem_reward(self.goal_id, redeem_to_current_location=redeem_to_current_location.is_enabled())

    def on_click_reward(self):
        rewards = self.rewards
        if rewards:
            rewards[0].on_click()

    def _check_keywords(self, keywords):
        result = super(DailyGoalJob, self)._check_keywords(keywords)
        if not result:
            title = get_content_tag_as_object(ContentTags.feature_daily_goals).title.lower()
            for keyword in keywords:
                if keyword in title:
                    continue
                return False

            return True
        else:
            return True

    def _qa_menu(self, menu_data):
        if is_qa():
            menu_data.AddSeparator()
            if not self.is_completed:
                qa_entries, progress_setting = get_job_qa_menu_entries(self.goal_id, self.current_progress, self.target_progress)
                menu_data.extend(qa_entries)
                if self._qa_progress_setting:
                    self._qa_progress_setting.on_change.disconnect(self._on_qa_progress_setting_changed)
                self._qa_progress_setting = progress_setting
                self._qa_progress_setting.on_change.connect(self._on_qa_progress_setting_changed)
            else:
                qa_entitlement_entries = get_reward_qa_menu_entries(self.goal_id)
                menu_data.extend(qa_entitlement_entries)

    def get_menu(self):
        menu_data = super(DailyGoalJob, self).get_menu()
        self._qa_menu(menu_data)
        return menu_data

    def get_qa_menu(self):
        data = MenuData()
        self._qa_menu(data)
        return data

    def _on_qa_progress_setting_changed(self, value):
        CloseContextMenus()
        uthread.new(lambda : DailyGoalsController.get_instance().admin_set_progress(self.goal_id, int(math.ceil(value))))
