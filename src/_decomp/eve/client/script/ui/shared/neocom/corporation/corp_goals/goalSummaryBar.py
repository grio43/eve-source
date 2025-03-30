#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_goals\goalSummaryBar.py
import eveui
from carbonui import uiconst, Align, TextColor, TextDetail, TextHeader
from carbonui.decorative.selectionIndicatorLine import SelectionIndicatorLine
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uiconst import PickState
from eveformat import currency
from corporation.client.goals import goalSignals
from corporation.client.goals import goalsUtil
from corporation.client.goals.goalsController import CorpGoalsController
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from localization import GetByLabel
import threadutils
import uthread2
import gametime

class GoalSummaryStat(ContainerAutoSize):
    default_alignMode = Align.TOPLEFT

    def ApplyAttributes(self, attributes):
        super(GoalSummaryStat, self).ApplyAttributes(attributes)
        label = attributes.label
        self.active_color = attributes.color
        opacity_active = attributes.opacity_active or 1.0
        self._initialized = False
        self.content = ContainerAutoSize(name='content', parent=self, opacity=0.0, align=Align.TOPLEFT, alignMode=Align.TOPLEFT)
        self.indicatorLine = SelectionIndicatorLine(parent=self.content, align=Align.TOLEFT, selected=True, opacity_active=opacity_active)
        self.valueLabel = eveLabel.EveCaptionLarge(name='valueLabel', parent=self.content, align=Align.TOPLEFT, top=-2, left=20)
        eveLabel.EveLabelLarge(parent=self.content, align=Align.TOPLEFT, left=20, top=26, text=label, color=TextColor.SECONDARY)

    def SetValue(self, value, maxValue = None):
        self.valueLabel.text = self.GetValueText(value, maxValue)
        if not self._initialized:
            eveui.animation.fade_in(self.content, duration=1.0)
            self._initialized = True
        if self.active_color:
            color = self.active_color if value else eveColor.SILVER_GREY
            self.indicatorLine.SetActiveColor(color)

    def GetValueText(self, value, maxValue = None):
        if maxValue:
            return u'{value}<fontSize=14><color={color}>/{maxValue}</color></fontsize>'.format(value=value, color=TextColor.SECONDARY.hex_argb, maxValue=maxValue)
        else:
            return str(value)


class GoalSummaryStatISK(GoalSummaryStat):

    def ApplyAttributes(self, attributes):
        self.value = 0
        super(GoalSummaryStatISK, self).ApplyAttributes(attributes)

    def GetValueText(self, value, maxValue = None):
        return currency.isk_readable_short(value)

    def SetValue(self, value, maxValue = None):
        self.value = value
        super(GoalSummaryStatISK, self).SetValue(value, maxValue)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.SetSpacing(cellSpacing=(0, 0))
        tooltipPanel.AddCell(TextHeader(text=currency.isk(self.value), color=TextColor.NORMAL))
        tooltipPanel.AddCell(TextDetail(text=currency.isk_readable(self.value), color=TextColor.SECONDARY))


class GoalSummaryBar(Container):
    default_clipChildren = True
    _activeTasklet = None
    _historicalTasklet = None

    def ApplyAttributes(self, attributes):
        super(GoalSummaryBar, self).ApplyAttributes(attributes)
        self.availablePayoutSummary = GoalSummaryStatISK(parent=self, align=uiconst.TOLEFT, width=164, padRight=32, label=GetByLabel('UI/Corporations/Goals/AmountAvailableToYou'), color=eveColor.SUCCESS_GREEN, opacity_active=0.5, pickState=PickState.ON)
        self.payoutSummary = GoalSummaryStatISK(parent=self, align=uiconst.TOLEFT, width=164, padRight=32, label=GetByLabel('UI/Corporations/Goals/ISKAvailableFromProjects'), color=eveColor.SUCCESS_GREEN, opacity_active=0.5, pickState=PickState.ON)
        if goalsUtil.CanAuthorGoals():
            self.activeSummary = GoalSummaryStat(parent=self, align=uiconst.TOLEFT, padLeft=2, padRight=32, label=GetByLabel('UI/Corporations/Goals/ActiveProjects'), pickState=PickState.ON)
        else:
            self.activeSummary = GoalSummaryStat(parent=self, align=uiconst.TOLEFT, padRight=32, label=GetByLabel('UI/Corporations/Goals/ActiveProjects'))
        self.todaySummary = GoalSummaryStat(parent=self, align=uiconst.TOLEFT, padRight=32, label=GetByLabel('UI/Corporations/Goals/CompletedToday'), pickState=PickState.ON, hint=GetByLabel('UI/Corporations/Goals/CompletedTodayHint'), color=eveColor.SUCCESS_GREEN)
        self.weekSummary = GoalSummaryStat(parent=self, align=uiconst.TOLEFT, width=164, label=GetByLabel('UI/Corporations/Goals/CompletedThisWeek'), color=eveColor.SUCCESS_GREEN, opacity_active=0.5, padRight=32)
        self.loadingWheel = LoadingWheel(parent=self, align=Align.CENTERLEFT, pos=(0, 0, 32, 32), opacity=0.0)
        goalSignals.on_created.connect(self.UpdateStats)
        goalSignals.on_closed.connect(self.UpdateStats)
        goalSignals.on_completed.connect(self.UpdateStats)
        goalSignals.on_deleted.connect(self.UpdateStats)
        goalSignals.on_expired.connect(self.UpdateStats)
        goalSignals.on_goal_data_fetched.connect(self.UpdateStats)

    def Close(self):
        super(GoalSummaryBar, self).Close()
        goalSignals.on_created.disconnect(self.UpdateStats)
        goalSignals.on_closed.disconnect(self.UpdateStats)
        goalSignals.on_completed.disconnect(self.UpdateStats)
        goalSignals.on_deleted.disconnect(self.UpdateStats)
        goalSignals.on_expired.disconnect(self.UpdateStats)
        goalSignals.on_goal_data_fetched.disconnect(self.UpdateStats)

    @threadutils.Throttled(0.5)
    def UpdateStats(self, *args):
        if not self._activeTasklet:
            self._activeTasklet = uthread2.start_tasklet(self._UpdateActiveStats)
        if not self._historicalTasklet:
            self._historicalTasklet = uthread2.start_tasklet(self._UpdateHistoricalStats)

    def _UpdateActiveStats(self):
        eveui.animation.fade_in(self.loadingWheel, time_offset=0.6)
        controller = CorpGoalsController.get_instance()
        controller.wait_for_active()
        active_goals = controller.get_cached_active_goals()
        num_active = len(active_goals)
        max_active = None
        if goalsUtil.CanAuthorGoals():
            max_active = controller.get_active_capacity()
        self.activeSummary.SetValue(num_active, max_active)
        self.activeSummary.hint = GetByLabel('UI/Corporations/Goals/MaxActiveProjectsHint', maxNum=max_active)
        isk_remaining_total = 0
        isk_remaining_for_me = 0
        for goal in active_goals:
            isk_remaining_total += goal.get_total_remaining_isk()
            isk_remaining_for_me += goal.get_my_remaining_isk()

        self.payoutSummary.SetValue(isk_remaining_total)
        self.availablePayoutSummary.SetValue(isk_remaining_for_me)
        eveui.animation.fade_out(self.loadingWheel)
        self._activeTasklet = None

    def _UpdateHistoricalStats(self):
        controller = CorpGoalsController.get_instance()
        controller.wait_for_inactive()
        inactive_goals = controller.get_cached_inactive_goals()
        now = gametime.now()
        completed_today = 0
        completed_last_week = 0
        for goal in inactive_goals:
            if not goal.is_completed():
                continue
            completed_time = goal.get_completed_datetime()
            if not completed_time:
                continue
            days_since = (now - completed_time).days
            if days_since < 1:
                completed_today += 1
                completed_last_week += 1
            elif days_since < 7:
                completed_last_week += 1

        self.todaySummary.SetValue(completed_today)
        self.weekSummary.SetValue(completed_last_week)
        self._historicalTasklet = None
