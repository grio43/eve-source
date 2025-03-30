#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\util.py
from collections import defaultdict
from eve.client.script.ui.shared.careerPortal import careerConst
from metadata.common.content_tags.const import CONTENT_TAG_TO_CAREER_PATH
from jobboard.client.ui.claim_location_prompt import prompt_select_claim_location
from dailygoals.client.const import DailyGoalCategory

def get_career_path_bg(career_path_id):
    career_path_int_id = CONTENT_TAG_TO_CAREER_PATH.get(career_path_id, None)
    return get_career_path_by_career(career_path_int_id)


def get_career_path_by_career(career_path_int_id):
    return careerConst.CAREERS_BG_FLAIR.get(career_path_int_id, 'res:/UI/Texture/Shared/CareerPaths/unclassified_flair.png')


def get_rewards_by_type(jobs):
    rewards_by_type = {}
    for job in jobs:
        for reward in job.claimable_rewards:
            reward_type = reward.reward_type
            if reward.reward_type == 'ITEM':
                reward_type = reward.item_type_id
            if reward_type not in rewards_by_type:
                rewards_by_type[reward_type] = {'icon': reward.icon,
                 'amount': 0,
                 'reward_type': reward.reward_type}
            rewards_by_type[reward_type]['amount'] += reward.claimable_amount

    return rewards_by_type


def get_rewards_by_category(jobs):
    rewards_by_category = {}
    for job in jobs:
        category = job.category
        if category not in rewards_by_category:
            rewards_by_category[category] = {}
        for reward in job.claimable_rewards:
            reward_type = reward.reward_type
            if reward.reward_type == 'ITEM':
                reward_type = reward.item_type_id
            if category == DailyGoalCategory.CATEGORY_MONTHLY_BONUS:
                if job.is_omega_restricted:
                    key = 'omega'
                else:
                    key = 'alpha'
                if key not in rewards_by_category[category]:
                    rewards_by_category[category][key] = {}
                rewards_by_category[category][key][reward_type] = {'icon': reward.icon,
                 'amount': reward.claimable_amount,
                 'reward_type': reward.reward_type}
            else:
                if reward_type not in rewards_by_category[category]:
                    rewards_by_category[category][reward_type] = {'icon': reward.icon,
                     'amount': 0,
                     'reward_type': reward.reward_type}
                rewards_by_category[category][reward_type]['amount'] += reward.claimable_amount

    return rewards_by_category


def get_item_rewards_for_jobs(jobs):
    rewards = defaultdict(int)
    for job in jobs:
        for reward in job.claimable_rewards:
            if reward.reward_type != 'ITEM':
                continue
            rewards[reward.item_type_id] += 1

    return rewards


def select_redeem_location(jobs):
    item_rewards = get_item_rewards_for_jobs(jobs)
    if not item_rewards:
        return True
    location_id = prompt_select_claim_location(item_rewards)
    if not location_id:
        return False
    return True
