#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dailygoals\client\goal.py
import gametime
from localization import GetByMessageID, GetByLabel
from carbon.common.script.util.format import DateToBlue
import eveformat
import evetypes
from fsdBuiltData.common.iconIDs import GetIconFile
from goals.client.contributionMethods import get_contribution_method
from dailygoals.client.const import DailyGoalCategory, RewardType, ICON_BY_REWARD_TYPE, REWARD_SORT_ORDER, TRACK_SIZE, SPECIFIC_ITEM_TYPE_TEXT, OVER_WRITE_ITEM_ICON, REWARD_TYPE_TO_TYPE_ID
from dailygoals.client.utils import find_skill_icon_from_amount, find_type_id_from_amount

class DailyGoal(object):

    def __init__(self, goal_id):
        self._goal_id = goal_id
        self._category = DailyGoalCategory.CATEGORY_UNSPECIFIED
        self._name_id = None
        self._description_id = None
        self._help_text_id = None
        self._target_progress = None
        self._current_progress = None
        self._assigner_id = None
        self._assignee_id = None
        self._contribution_method = None
        self._career_path = None
        self._active_after = None
        self._active_until = None
        self._has_earnings = False
        self._rewards = []
        self._is_omega = False
        self._omega_restricted_earnings = False
        self._paid_completion = False
        self._has_set_data = False
        self._fetching = False

    def set_data(self, data):
        self._category = data.get('category', DailyGoalCategory.CATEGORY_UNSPECIFIED)
        self._name_id = data.get('name_id', None)
        self._description_id = data.get('desc_id', None)
        self._help_text_id = data.get('help_text_id', None)
        self._target_progress = data.get('target', None)
        self._current_progress = data.get('progress', None)
        self._assigner_id = data.get('assigner_id', None)
        self._assignee_id = data.get('assignee_organization_id', None)
        self._contribution_method = get_contribution_method(data.get('contribution_method_id', None), data.get('contribution_fields', None))
        self._career_path = data.get('career_id', None)
        self._active_after = data.get('active_after', None)
        self._active_until = data.get('active_until', None)
        self._is_omega = data.get('is_omega', False)
        self.rewards = data.get('rewards', [])
        self._has_earnings = data.get('has_earnings')
        self._omega_restricted_earnings = data.get('omega_restricted_earnings', self._is_omega)
        self._paid_completion = data.get('paid_completion', False)
        self._has_set_data = True

    def has_data(self):
        return self._has_set_data

    @property
    def fetching(self):
        return self._fetching

    @fetching.setter
    def fetching(self, value):
        self._fetching = value

    @property
    def rewards(self):
        return self._rewards

    @rewards.setter
    def rewards(self, reward_dict_list):
        result = []
        for reward_info in reward_dict_list:
            if reward_info.get('reward_type') not in RewardType:
                continue
            reward = DailyGoalReward(**reward_info)
            result.append(reward)

        self._rewards = sorted(result, key=lambda reward: REWARD_SORT_ORDER.get(reward.reward_type))

    @property
    def is_omega_restricted(self):
        return self._is_omega

    @property
    def is_last_milestone(self):
        return self.get_target_progress() == TRACK_SIZE

    def mark_as_redeemed(self):
        self._has_earnings = False

    def get_id(self):
        return self._goal_id

    def get_category(self):
        return self._category

    def get_due_datetime(self):
        if self._active_until:
            return self._active_until

    def get_name(self):
        return GetByMessageID(self._name_id)

    def get_description(self):
        return GetByMessageID(self._description_id)

    def get_help_text(self):
        return GetByMessageID(self._help_text_id)

    def get_target_progress(self):
        return self._target_progress

    def get_current_progress(self):
        if self._paid_completion:
            return self._target_progress
        return self._current_progress

    def get_contribution_method(self):
        return self._contribution_method

    def set_current_progress(self, progress):
        self._current_progress = progress
        if self.is_completed():
            self._has_earnings = True
            self._omega_restricted_earnings = self._is_omega and not sm.GetService('cloneGradeSvc').IsOmega()

    def is_completed(self):
        return self._current_progress == self._target_progress or self._paid_completion

    def paid_completion(self):
        return self._paid_completion

    def set_paid_completion(self, is_paid):
        self._paid_completion = is_paid

    def get_assigner_id(self):
        return self._assigner_id

    def get_career_path(self):
        return self._career_path

    def has_unclaimed_rewards(self):
        return bool(self.rewards) and self._has_earnings and self.is_completed()

    def get_claimable_rewards(self):
        if self.has_unclaimed_rewards():
            return self.rewards
        else:
            return []

    def are_rewards_omega_restricted(self):
        return self._omega_restricted_earnings

    @property
    def expiration_time(self):
        return DateToBlue(self.get_due_datetime())

    @property
    def is_expired(self):
        return self.expiration_time < gametime.GetWallclockTime()


class DailyGoalReward(object):

    def __init__(self, reward_type, amount, asset_id = None, item_type_id = None, **kwargs):
        self._reward_type = reward_type
        self._amount = amount
        self._asset_id = asset_id
        self._item_type_id = item_type_id

    @property
    def reward_type(self):
        return self._reward_type

    @property
    def total_amount(self):
        return self._amount

    @property
    def claimable_amount(self):
        return self._amount

    @property
    def item_type_id(self):
        return self._item_type_id

    @property
    def asset_id(self):
        return self._asset_id

    @property
    def icon(self):
        if self.reward_type == RewardType.SKILL_POINTS:
            return find_skill_icon_from_amount(self._amount)
        if self.reward_type == RewardType.ITEM:
            if self._item_type_id in OVER_WRITE_ITEM_ICON:
                return OVER_WRITE_ITEM_ICON[self._item_type_id]
            return GetIconFile(evetypes.GetIconID(self._item_type_id))
        return ICON_BY_REWARD_TYPE.get(self._reward_type, None)

    @property
    def amount_text(self):
        if self.reward_type == RewardType.ITEM:
            if self._item_type_id in SPECIFIC_ITEM_TYPE_TEXT:
                return GetByMessageID(SPECIFIC_ITEM_TYPE_TEXT[self._item_type_id])
            return GetByMessageID(evetypes.GetNameID(self._item_type_id))
        return eveformat.number(self._amount)

    @property
    def type_id(self):
        if self.reward_type == RewardType.ITEM:
            return self.item_type_id
        if self.reward_type == RewardType.SKILL_POINTS:
            return find_type_id_from_amount(self._amount)
        if self.reward_type in REWARD_TYPE_TO_TYPE_ID:
            return REWARD_TYPE_TO_TYPE_ID[self.reward_type]
        raise TypeError('Unable to find reward type id for reward type %s', self.reward_type)

    @property
    def name(self):
        if self.reward_type == RewardType.ITEM:
            return GetByMessageID(evetypes.GetNameID(self._item_type_id))
        if self.reward_type == RewardType.ISK:
            return eveformat.isk(self._amount)
        if self.reward_type == RewardType.PLEX:
            return eveformat.plex(self._amount)
        if self.reward_type == RewardType.LOYALTY_POINTS:
            return GetByLabel('UI/Wallet/WalletWindow/EvermarkAmount', everMarkAmount=self._amount)
        if self.reward_type == RewardType.SKILL_POINTS:
            return GetByMessageID(evetypes.GetNameID(self.type_id))

    def on_click(self):
        if self.reward_type == RewardType.SKILL_POINTS:
            return
        sm.GetService('info').ShowInfo(self.type_id)
