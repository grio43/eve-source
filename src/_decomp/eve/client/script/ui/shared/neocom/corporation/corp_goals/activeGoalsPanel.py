#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_goals\activeGoalsPanel.py
import logging
import blue
import eveui
import uthread2
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.cardsContainer import CardsContainer
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.neocom.corporation.corp_goals.goalBrowserSettings import have_participated_in_filter_setting, career_path_filter_setting, sort_by_setting, have_unclaimed_rewards_for_filter_setting, can_contribute_to_setting
from jobboard.client import get_job_board_service, ProviderType
from jobboard.client.features.corporation_goals.corporation_goal_job_signals import on_corporation_goal_job_added, on_corporation_goal_job_deleted
from localization import GetByLabel
import threadutils
logger = logging.getLogger(__name__)

class ActiveGoalsPanel(Container):

    def ApplyAttributes(self, attributes):
        super(ActiveGoalsPanel, self).ApplyAttributes(attributes)
        self.get_text_filter = attributes.get_text_filter
        self._initialized = False
        self._reconstruct_thread = None
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER, opacity=0.0)
        self.scrollCont = ScrollContainer(parent=self)
        self.cardsContainer = CardsContainer(name='cardsContainer', parent=self.scrollCont, align=uiconst.TOTOP, contentSpacing=(16, 16), cardHeight=186, cardMaxWidth=550)
        on_corporation_goal_job_added.connect(self.OnGoalAdded)
        on_corporation_goal_job_deleted.connect(self.OnGoalDeleted)
        career_path_filter_setting.on_change.connect(self.OnSettingChanged)
        have_participated_in_filter_setting.on_change.connect(self.OnSettingChanged)
        have_unclaimed_rewards_for_filter_setting.on_change.connect(self.OnSettingChanged)
        can_contribute_to_setting.on_change.connect(self.OnSettingChanged)
        sort_by_setting.on_change.connect(self.OnSettingChanged)

    def Close(self):
        on_corporation_goal_job_added.disconnect(self.OnGoalAdded)
        on_corporation_goal_job_deleted.disconnect(self.OnGoalDeleted)
        career_path_filter_setting.on_change.disconnect(self.OnSettingChanged)
        have_participated_in_filter_setting.on_change.disconnect(self.OnSettingChanged)
        have_unclaimed_rewards_for_filter_setting.on_change.disconnect(self.OnSettingChanged)
        can_contribute_to_setting.on_change.disconnect(self.OnSettingChanged)
        sort_by_setting.on_change.disconnect(self.OnSettingChanged)
        super(ActiveGoalsPanel, self).Close()

    def OnSettingChanged(self, *args):
        self.ReconstructScrollEntries()

    def LoadPanel(self):
        uthread2.start_tasklet(self.ReconstructScrollEntries)

    def OnGoalAdded(self, goal_id):
        self.ReconstructScrollEntries()

    def OnGoalDeleted(self, goal_id):
        self.ReconstructScrollEntries()

    def OnSearch(self):
        self.ReconstructScrollEntries()

    def OnTimespanCombo(self):
        pass

    @threadutils.throttled(0.5)
    def ReconstructScrollEntries(self, animate = True):
        if not self.display:
            return
        self.cardsContainer.Flush()
        if self._reconstruct_thread and self._reconstruct_thread.is_alive():
            self._reconstruct_thread.kill()
        self._reconstruct_thread = uthread2.start_tasklet(self._ConstructScrollEntries)

    def _ConstructScrollEntries(self):
        eveui.animation.fade_in(self.loadingWheel, time_offset=0.6)
        jobs, noContentHint = self._GetGoalsFilteredAndSorted()
        eveui.animation.fade_out(self.loadingWheel, duration=0.1)
        for controller in jobs:
            if self.destroyed:
                return
            controller.construct_card(parent=self.cardsContainer, width=0, height=0)
            blue.pyos.BeNice()

        if jobs:
            self.scrollCont.HideNoContentHint()
        else:
            self.scrollCont.ShowNoContentHint(noContentHint)

    def _GetGoalsFilteredAndSorted(self):
        try:
            jobs = [ job for job in get_job_board_service().get_jobs(provider_id=ProviderType.CORPORATION_GOALS) if job.is_active ]
        except Exception as e:
            logger.exception(e)
            return ([], GetByLabel('UI/Corporations/Goals/FailedToConnect'))

        jobs = self._GetGoalsSorted(self._GetGoalsFiltered(jobs))
        return (jobs, GetByLabel('UI/Corporations/Goals/NoProjectsCurrentlySet'))

    def _GetGoalsSorted(self, goals):
        sortBy = sort_by_setting.get()
        if sortBy == 'name':
            return sorted(goals, key=lambda g: g.title.lower())
        elif sortBy == 'name_reversed':
            return sorted(goals, key=lambda g: g.title.lower(), reverse=True)
        elif sortBy == 'date_created':
            return sorted(goals, key=lambda g: g.creation_date)
        elif sortBy == 'date_created_reversed':
            return sorted(goals, key=lambda g: g.creation_date, reverse=True)
        elif sortBy == 'progress':
            return sorted(goals, key=lambda g: g.progress_percentage)
        elif sortBy == 'progress_reversed':
            return sorted(goals, key=lambda g: g.progress_percentage, reverse=True)
        elif sortBy == 'num_jumps':
            return sorted(goals, key=lambda g: g.jumps)
        elif sortBy == 'num_jumps_reversed':
            return sorted(goals, key=lambda g: g.jumps, reverse=True)
        elif sortBy == 'time_remaining':
            return sorted(goals, key=lambda g: (g.expiration_time is None, g.expiration_time))
        elif sortBy == 'time_remaining_reversed':
            return sorted(goals, key=lambda g: (g.expiration_time is None, g.expiration_time), reverse=True)
        else:
            logger.warning(u'sort_by method not found: {}'.format(sortBy))
            return goals

    def _GetGoalsFiltered(self, goals):
        filterStr = self.get_text_filter()
        if filterStr:
            goals = [ goal for goal in goals if filterStr.lower() in goal.title.lower() ]
        career_path_filter = career_path_filter_setting.get()
        if career_path_filter is not None:
            goals = [ g for g in goals if g.career_path == career_path_filter ]
        if have_participated_in_filter_setting.is_enabled():
            goals = [ g for g in goals if g.personal_progress ]
        if have_unclaimed_rewards_for_filter_setting.is_enabled():
            goals = [ g for g in goals if g.has_claimable_rewards ]
        if can_contribute_to_setting.is_enabled():
            goals = [ g for g in goals if g.can_contribute_to() ]
        return goals
