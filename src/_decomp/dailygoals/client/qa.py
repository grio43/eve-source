#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dailygoals\client\qa.py
from carbonui.control.contextMenu.menuEntryData import MenuEntryDataSlider, MenuEntryDataCheckbox
from carbonui.services.setting import UserSettingNumeric
from dailygoals.client.goalsController import DailyGoalsController
from dailygoals.client.qa_settings import daily_goals_get_goals_force_errors, daily_goals_get_goals_force_delay, daily_goals_get_goals_randomize_errors, daily_goals_use_mock
import blue

def get_insider_qa_menu():
    menu = ('Daily Goals', (('Flush cache', _flush), ('Regenerate', _regenerate), ('Loading & Failure', (('Reset All', _reset_all_settings), ('Get Goals', (MenuEntryDataCheckbox('Use Mock Data', setting=daily_goals_use_mock, hint='When on we mock out data we are unable to fetch'),
          MenuEntryDataCheckbox('Force Errors', setting=daily_goals_get_goals_force_errors, hint='Errors when fetching daily goals of today. If this is used once AO has been opened the cache must be flushed for this to have a noticable effect'),
          MenuEntryDataCheckbox('Randomize Errors', setting=daily_goals_get_goals_randomize_errors, hint='If raising errors this will raise them 50% of the time instead of always'),
          MenuEntryDataSlider('Force Delays', setting=daily_goals_get_goals_force_delay, min_label='0', max_label='5')))))))
    return menu


def get_job_qa_menu_entries(goal_id, current_progress, max_progress):
    setting = UserSettingNumeric('qa_set_daily_goal_progress_setting', default_value=current_progress, min_value=current_progress, max_value=max_progress)
    setting.set(current_progress)
    menu_entries = (('QA - Copy Goal ID {goal_id}'.format(goal_id=goal_id), lambda : blue.pyos.SetClipboardData(str(goal_id))), ('QA - Complete Goal', lambda : _request_set_progress(goal_id, max_progress)), MenuEntryDataSlider('QA - Progress Goal', setting, min_label=str(setting.min_value), max_label=str(setting.max_value)))
    return (menu_entries, setting)


def get_reward_qa_menu_entries(goal_id):
    menu_entries = (('QA - Expire Entitlement', lambda : _expire_goal(goal_id)), ('QA - Copy Goal ID {goal_id}'.format(goal_id=goal_id), lambda : blue.pyos.SetClipboardData(str(goal_id))))
    return menu_entries


def _expire_goal(goal_id):
    command = '/dailygoals expire {goal_id}'.format(goal_id=goal_id)
    sm.RemoteSvc('slash').SlashCmd(command)


def _request_set_progress(goal_id, progress_to_set):
    DailyGoalsController.get_instance().admin_set_progress(goal_id, progress_to_set)


def _flush():
    DailyGoalsController.get_instance().flush_cache()


def _regenerate():
    sm.GetService('slash').SlashCmd('/dailygoals regen')
    _flush()


def _reset_all_settings():
    daily_goals_get_goals_force_errors.set(False)
    daily_goals_get_goals_force_delay.set(0)
