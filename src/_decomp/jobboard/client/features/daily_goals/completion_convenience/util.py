#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\completion_convenience\util.py
from dailygoals.client.const import PRICE_FIRST_COMPLETION, PRICE_SECOND_COMPLETION
from dailygoals.client.goalsController import DailyGoalsController
from jobboard.client import get_job_board_service, ProviderType
from jobboard.client.features.daily_goals.completion_convenience.button_blocker import get_button_blocker

def can_pay_for_completion(job):
    if job.is_completed:
        return False
    return get_remaining_completion_convenience_num() > 0


def pay_for_completion(job):
    get_button_blocker().process_started(job.goal_id)
    DailyGoalsController.get_instance().pay_for_completion(job.goal_id)


def get_remaining_completion_convenience_num():
    daily_bonus_job = get_job_board_service().get_provider(ProviderType.DAILY_GOALS).get_bonus_job_of_the_day()
    daily_bonus_progress = daily_bonus_job.current_progress
    paid_count = DailyGoalsController.get_instance().get_completion_convenience_counter()
    return max(0, 2 - max(daily_bonus_progress, paid_count))


def can_afford_completion_convenience(balance = None):
    if not balance:
        balance = sm.GetService('loyaltyPointsWalletSvc').GetCharacterEvermarkBalance()
    price = get_price_of_completion()
    if not price:
        return False
    return balance >= price


def get_price_of_completion():
    paid_count = DailyGoalsController.get_instance().get_completion_convenience_counter()
    if paid_count == 0:
        return PRICE_FIRST_COMPLETION
    if paid_count == 1:
        return PRICE_SECOND_COMPLETION
