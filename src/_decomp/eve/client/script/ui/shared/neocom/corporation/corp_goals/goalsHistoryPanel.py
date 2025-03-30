#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_goals\goalsHistoryPanel.py
import eveicon
import logging
import datetime
import eveui
import uthread2
import threadutils
from carbonui import Align
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.scroll import Scroll
from carbonui.primitives.container import Container
from corporation.client.goals import goalSignals
from corporation.client.goals import goalsUtil
from corporation.client.goals.goalsController import CorpGoalsController
from goals.common.goalConst import GoalState
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.neocom.corporation.corp_goals.forms import goalForms
from eve.client.script.ui.shared.neocom.corporation.corp_goals.goalBrowserSettings import career_path_filter_setting, have_participated_in_filter_setting, sort_by_setting, have_unclaimed_rewards_for_filter_setting
from localization import GetByLabel
from jobboard.client import open_corporation_goal, get_corporation_goal_job
logger = logging.getLogger(__name__)

class GoalHistoryEntry(Generic):
    isDragObject = True

    def Load(self, node):
        super(GoalHistoryEntry, self).Load(node)
        self.goal = node.goal

    def GetDragData(self):
        return self.goal.get_drag_data()

    def OnDblClick(self, *args):
        if goalsUtil.CanAuthorGoals():
            self._ViewDetails()
        else:
            self._OpenOpportunity()

    def _ViewDetails(self):
        job = get_corporation_goal_job(self.goal.get_id())
        if job:
            goalSignals.on_view_details(job.id)

    def _OpenOpportunity(self):
        open_corporation_goal(self.goal.get_id())

    def _Clone(self):
        goalForms.OpenDuplicateGoalFormWindow(original=self.goal)

    def GetMenu(self):
        m = MenuData()
        if goalsUtil.CanAuthorGoals():
            m.AddEntry(GetByLabel('UI/Corporations/Goals/CloneProject'), self._Clone, texturePath=eveicon.copy)
            m.AddEntry(GetByLabel('UI/Corporations/Goals/ViewAdminDetails'), self._ViewDetails)
            m.AddSeparator()
        m.AddEntry(self.goal.get_creator_name(), subMenuData=lambda : sm.GetService('menu').GetMenuForOwner(self.goal.get_creator()))
        return m


class GoalsHistoryPanel(Container):

    def ApplyAttributes(self, attributes):
        super(GoalsHistoryPanel, self).ApplyAttributes(attributes)
        self.get_text_filter = attributes.get_text_filter
        self.get_timespan_option = attributes.get_timespan_option
        self.isConstructed = False
        self.currentTimeSpan = -1
        goalSignals.on_goal_data_fetched.connect(self.OnGoalDataFetched)
        have_participated_in_filter_setting.on_change.connect(self.OnHaveParticipatedSettingChanged)
        career_path_filter_setting.on_change.connect(self.OnSettingChanged)
        have_unclaimed_rewards_for_filter_setting.on_change.connect(self.OnSettingChanged)
        sort_by_setting.on_change.connect(self.OnSettingChanged)

    def Close(self):
        goalSignals.on_goal_data_fetched.disconnect(self.OnGoalDataFetched)
        have_participated_in_filter_setting.on_change.disconnect(self.OnHaveParticipatedSettingChanged)
        career_path_filter_setting.on_change.disconnect(self.OnSettingChanged)
        have_unclaimed_rewards_for_filter_setting.on_change.disconnect(self.OnSettingChanged)
        sort_by_setting.on_change.disconnect(self.OnSettingChanged)
        super(GoalsHistoryPanel, self).Close()

    def OnGoalDataFetched(self, goal):
        if CorpGoalsController.get_instance().is_inactive_goal(goal.goal_id, months_since=self.get_timespan_option()):
            self.ReconstructScrollEntries()

    def OnSettingChanged(self, *args):
        self.ReconstructScrollEntries()

    def OnHaveParticipatedSettingChanged(self, *args):
        self.currentTimeSpan = -1
        self.ReconstructScrollEntries()

    def OnSearch(self):
        self.ReconstructScrollEntries()

    def OnTimespanCombo(self):
        self.ReconstructScrollEntries()

    def LoadPanel(self):
        if not self.isConstructed:
            self.ConstructLayout()
            self.isConstructed = True
        uthread2.start_tasklet(self.ReconstructScrollEntries)

    def ConstructLayout(self):
        self.scroll = Scroll(parent=self, id='project_participants')
        self.loadingWheel = LoadingWheel(parent=self, opacity=0.0, align=Align.CENTER)

    @threadutils.throttled(0.5)
    def ReconstructScrollEntries(self):
        if not self.display or not self.isConstructed:
            return
        eveui.animation.fade_in(self.loadingWheel, time_offset=0.6)
        self.scroll.Clear()
        entries = []
        goals, noContentHint = self._GetGoalsFiltered()
        if goals is None:
            eveui.animation.fade_out(self.loadingWheel)
            return
        for goal in goals:
            completed_date = goal.get_completed_datetime()
            data = {'label': u'{}<t>{}<t>{}<t>{}<t>{}<t>{:.0f}%<t>{}'.format(goal.get_name(), goal.get_contribution_method().title, str(goal.get_creation_datetime().date()), str(completed_date.date()) if completed_date else '-', self._GetStateLabel(goal), goal.get_progress_ratio() * 100, goal.get_creator_name()),
             'sortValues': (goal.get_name(),
                            goal.get_contribution_method().title,
                            goal.get_creation_datetime(),
                            completed_date if completed_date else datetime.datetime(1900, 1, 1),
                            self._GetStateLabel(goal),
                            goal.get_progress_ratio() * 100,
                            goal.get_creator_name()),
             'height': 24,
             'goal': goal}
            entry = GetFromClass(GoalHistoryEntry, data)
            entries.append(entry)

        self.scroll.LoadContent(contentList=entries, headers=(GetByLabel('UI/Common/Name'),
         GetByLabel('UI/Corporations/Goals/ContributionMethod'),
         GetByLabel('UI/Corporations/Goals/Created'),
         GetByLabel('UI/Corporations/Goals/Ended'),
         GetByLabel('UI/Corporations/Goals/Resolution'),
         GetByLabel('UI/Corporations/Goals/Progress'),
         GetByLabel('UI/Calendar/EventWindow/Creator')), noContentHint=noContentHint)
        eveui.animation.fade_out(self.loadingWheel)

    def _GetGoalsFiltered(self):
        controller = CorpGoalsController.get_instance()
        timespan_option = self.get_timespan_option()
        if self.currentTimeSpan != timespan_option:
            self.currentTimeSpan = timespan_option
            controller.fetch_inactive_goals(months_since=timespan_option, fetch_contribution=have_participated_in_filter_setting.is_enabled())
            controller.wait_for_inactive(timespan_option)
        goals = controller.get_cached_inactive_goals(timespan_option)
        if timespan_option != self.get_timespan_option():
            return (None, None)
        filterStr = self.get_text_filter()
        if filterStr:
            goals = [ goal for goal in goals if filterStr.lower() in goal.get_name().lower() ]
        career_path_filter = career_path_filter_setting.get()
        if career_path_filter is not None:
            goals = [ g for g in goals if g.career_path == career_path_filter ]
        if have_participated_in_filter_setting.is_enabled():
            goals = [ g for g in goals if g.get_my_progress() ]
        if have_unclaimed_rewards_for_filter_setting.is_enabled():
            goals = [ g for g in goals if g.has_unclaimed_reward() ]
        return (goals, GetByLabel('UI/Corporations/Goals/NoProjectsCurrentlySet'))

    def _GetStateLabel(self, goal):
        color = eveColor.SUCCESS_GREEN_HEX if goal.get_state() == GoalState.COMPLETED else eveColor.DANGER_RED_HEX
        return u'<color={}>{}</color>'.format(color, GetByLabel(goal.get_state_label()))
