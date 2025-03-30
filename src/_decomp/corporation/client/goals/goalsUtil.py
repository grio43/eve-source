#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\client\goals\goalsUtil.py
import eveicon
import blue
import datetime
import datetimeutils
from dateutil.relativedelta import relativedelta
from carbon.common.script.sys.serviceConst import ROLE_QA
from carbonui.control.contextMenu.menuData import MenuData
from corporation.common.goals.goalConst import CAN_AUTHOR_GOALS_ROLE_MASK
from localization import GetByLabel
from metadata import ContentTags
from metadata.common.content_tags.const import CAREER_PATH_TO_CONTENT_TAG_ID
from carbon.common.script.util.format import BlueToDate

def CanAuthorGoals():
    return session.corprole & CAN_AUTHOR_GOALS_ROLE_MASK > 0


def get_content_tags_for_corp_goal(goal):
    result = [ContentTags.feature_corporation_projects]
    if goal.career_path:
        result.append(CAREER_PATH_TO_CONTENT_TAG_ID.get(goal.career_path))
    result.extend([ content_tag_id for content_tag_id in goal.contribution_method.content_tags if content_tag_id not in (ContentTags.career_path_enforcer,
     ContentTags.career_path_explorer,
     ContentTags.career_path_industrialist,
     ContentTags.career_path_soldier_of_fortune) ])
    return result


def get_menu_for_corp_job(goal):
    m = MenuData()
    from corporation.client.goals.goalsController import CorpGoalsController
    from eve.client.script.ui.shared.neocom.corporation.corp_goals.forms import goalForms
    controller = CorpGoalsController.get_instance()
    if session.role & ROLE_QA:
        m.AddEntry('Goal ID: {goal_id}'.format(goal_id=goal.get_id()), lambda : blue.pyos.SetClipboardData(str(goal.get_id())))
    if CanAuthorGoals():
        m.AddSeparator()
        m.AddEntry(GetByLabel('UI/Corporations/Goals/CloneProject'), lambda : goalForms.OpenDuplicateGoalFormWindow(original=goal), texturePath=eveicon.copy)
        if goal.is_active():
            if goal.is_manual():
                m.AddEntry(GetByLabel('UI/Corporations/Goals/SetProgress'), lambda : goalForms.OpenSetGoalProgressFormWindow(goal))
                m.AddEntry(GetByLabel('UI/Corporations/Goals/CompleteProject'), lambda : controller.complete_goal(goal.get_id()), texturePath=eveicon.checkmark)
            m.AddEntry(GetByLabel('UI/Corporations/Goals/CloseProject'), lambda : controller.close_goal(goal.get_id()), texturePath=eveicon.close)
        if not goal.get_current_progress():
            m.AddSeparator()
            m.AddEntry(GetByLabel('UI/Corporations/Goals/DeleteProject'), lambda : controller.delete_goal(goal.get_id()), texturePath=eveicon.trashcan)
    location_id = goal.get_location_id()
    if location_id:
        m.AddSeparator()
        text = u'{}: {}'.format(GetByLabel('UI/Common/Location'), cfg.evelocations.Get(location_id).locationName)
        m.AddEntry(text, subMenuData=sm.GetService('menu').CelestialMenu(location_id))
    return m


def get_timespan_options():
    from timeDateHelpers.const import MONTHANDYEAR_NAME_TEXT
    options = []
    options.append((GetByLabel('UI/Wallet/WalletWindow/Last30Days'), None))
    today = datetime.date.today()
    for i in range(1, 6):
        option_date = today - relativedelta(months=i)
        options.append((GetByLabel(MONTHANDYEAR_NAME_TEXT[option_date.month - 1], year=option_date.year), i))

    return options


def get_timespan_by_option(months_since = None):
    if months_since is None:
        start_time = datetimeutils.datetime_to_timestamp(datetime.date.today() - relativedelta(days=30))
        end_time = datetimeutils.datetime_to_timestamp(datetime.datetime.now())
        duration = end_time - start_time
        return (start_time, duration)
    start_date = datetime.date.today().replace(day=1) - relativedelta(months=months_since)
    end_date = start_date + relativedelta(months=1)
    start_time = datetimeutils.datetime_to_timestamp(start_date)
    duration = datetimeutils.datetime_to_timestamp(end_date) - start_time
    return (start_time, duration)


def get_datetime_timestamp_from_blue(blue_timestamp):
    date_time_obj = BlueToDate(blue_timestamp)
    return datetimeutils.datetime_to_timestamp(date_time_obj)
