#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_goals\goalsBrowser.py
import eveicon
import logging
import uthread2
from carbonui import uiconst, Align
from carbonui.button.group import ButtonGroup
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from characterdata import careerpath
from corporation.client.goals import goalsUtil
from corporation.client.goals.goalsController import CorpGoalsController
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.neocom.corporation.corp_goals.forms import goalForms
from eve.client.script.ui.shared.neocom.corporation.corp_goals.activeGoalsPanel import ActiveGoalsPanel
from eve.client.script.ui.shared.neocom.corporation.corp_goals.goalBrowserSettings import have_participated_in_filter_setting, career_path_filter_setting, sort_by_setting, have_unclaimed_rewards_for_filter_setting, can_contribute_to_setting
from eve.client.script.ui.shared.neocom.corporation.corp_goals.goalSummaryBar import GoalSummaryBar
from eve.client.script.ui.shared.neocom.corporation.corp_goals.goalsHistoryPanel import GoalsHistoryPanel
from localization import GetByLabel, GetByMessageID
PROJECTS_HISTORY = 'history'
PROJECTS_ACTIVE = 'active'
logger = logging.getLogger(__name__)

class GoalsBrowser(Container):

    def __init__(self, *args, **kwargs):
        controller = CorpGoalsController.get_instance()
        controller.fetch_active_goals()
        controller.fetch_unclaimed_goals()
        controller.fetch_inactive_goals(fetch_contribution=have_participated_in_filter_setting.is_enabled())
        super(GoalsBrowser, self).__init__(*args, **kwargs)

    def ApplyAttributes(self, attributes):
        super(GoalsBrowser, self).ApplyAttributes(attributes)
        self.goalSummaryBar = GoalSummaryBar(parent=self, align=Align.TOTOP, height=48, padTop=8)
        self.topCont = Container(name='topCont', parent=self, align=uiconst.TOTOP, height=32, padTop=8)
        self.ConstructTopCont()
        self.panels = Container(name='panels', parent=self, padTop=16)
        self.panelActiveGoals = ActiveGoalsPanel(name=PROJECTS_ACTIVE, parent=self.panels, get_text_filter=self.quickFilter.GetValue)
        self.panelHistory = GoalsHistoryPanel(name=PROJECTS_HISTORY, parent=self.panels, get_text_filter=self.quickFilter.GetValue, get_timespan_option=self.timespanCombo.GetValue, display=False)
        if goalsUtil.CanAuthorGoals():
            buttonGroup = ButtonGroup(parent=self, idx=0, align=uiconst.TOBOTTOM, padTop=8)
            buttonGroup.AddButton(GetByLabel('UI/Corporations/Goals/CreateNew'), self.OnCreateBtn)
        uthread2.start_tasklet(self.toggleBtnGroup.SelectByID, PROJECTS_ACTIVE, animate=False)
        uthread2.start_tasklet(self.goalSummaryBar.UpdateStats)

    def ConstructTopCont(self):
        self.toggleBtnGroup = ToggleButtonGroup(parent=self.topCont, align=uiconst.TOLEFT, callback=self.OnToggleButtonGroup, width=300)
        self.toggleBtnGroup.AddButton(PROJECTS_ACTIVE, GetByLabel('UI/Corporations/Goals/Active'))
        self.toggleBtnGroup.AddButton(PROJECTS_HISTORY, GetByLabel('UI/Common/History'))
        self.timespanCombo = Combo(parent=self.topCont, align=uiconst.TORIGHT, width=130, callback=self.OnTimespanCombo, options=goalsUtil.get_timespan_options(), padLeft=8)
        self.quickFilter = QuickFilterEdit(parent=self.topCont, align=uiconst.TORIGHT, width=120)
        self.quickFilter.ReloadFunction = self.OnSearch
        self.filterButton = ProjectFilterMenuButtonIcon(parent=self.topCont, align=uiconst.TORIGHT, padRight=8)
        self.sortByButton = ProjectSortByMenuButtonIcon(parent=self.topCont, align=uiconst.TORIGHT)

    def OnToggleButtonGroup(self, *args):
        self.quickFilter.Clear(docallback=False)
        selected_id = self.toggleBtnGroup.GetValue()
        for panel in self.panels.children:
            visible = panel.name == selected_id
            if visible:
                panel.Show()
                panel.LoadPanel()
            else:
                panel.Hide()

        self.filterButton.SetSelectedPage(selected_id)
        if selected_id == PROJECTS_ACTIVE:
            self.sortByButton.Show()
            self.timespanCombo.Hide()
        else:
            self.sortByButton.Hide()
            self.timespanCombo.Show()

    def OnTimespanCombo(self, *args):
        self.GetActivePanel().OnTimespanCombo()

    def OnSearch(self):
        self.GetActivePanel().OnSearch()

    def GetActivePanel(self):
        for panel in self.panels.children:
            if panel.display:
                return panel

    def OnCreateBtn(self, *args):
        goalForms.OpenCreateGoalFormWindow()


class ProjectFilterMenuButtonIcon(MenuButtonIcon):
    hint = GetByLabel('UI/Inventory/Filter')
    default_texturePath = eveicon.filter

    def ApplyAttributes(self, attributes):
        self._selectedPage = None
        super(ProjectFilterMenuButtonIcon, self).ApplyAttributes(attributes)
        have_participated_in_filter_setting.on_change.connect(self.OnFilterChanged)
        have_unclaimed_rewards_for_filter_setting.on_change.connect(self.OnFilterChanged)
        can_contribute_to_setting.on_change.connect(self.OnFilterChanged)
        career_path_filter_setting.on_change.connect(self.OnFilterChanged)

    @property
    def _isViewingActivePage(self):
        return self._selectedPage == PROJECTS_ACTIVE

    def SetSelectedPage(self, pageID):
        self._selectedPage = pageID
        self.OnFilterChanged()

    def OnFilterChanged(self, *args):
        self.UpdateIconState()

    def IsFilterActive(self):
        return have_participated_in_filter_setting.is_enabled() or have_unclaimed_rewards_for_filter_setting.is_enabled() or self._isViewingActivePage and can_contribute_to_setting.is_enabled() or career_path_filter_setting.get() is not None

    def _GetIconColor(self):
        if self.IsFilterActive():
            return eveThemeColor.THEME_FOCUS
        else:
            return super(ProjectFilterMenuButtonIcon, self)._GetIconColor()

    def GetMenu(self):
        m = MenuData()
        m.AddCaption(self.hint)
        if self._isViewingActivePage:
            m.AddCheckbox(GetByLabel('UI/Corporations/Goals/CanContributeToProjectSetting'), setting=can_contribute_to_setting)
        m.AddCheckbox(GetByLabel('UI/Corporations/Goals/HaveParticipatedIn'), setting=have_participated_in_filter_setting)
        m.AddCheckbox(GetByLabel('UI/Corporations/Goals/HaveUnclaimedRewardsFor'), setting=have_unclaimed_rewards_for_filter_setting)
        m.AddSeparator()
        m.AddCaption(GetByLabel('Character/CareerPaths/CareerPath'))
        m.AddRadioButton(GetByLabel('UI/Common/Any'), None, career_path_filter_setting)
        for c_id, c in careerpath.get_career_paths().iteritems():
            m.AddRadioButton(GetByMessageID(c.nameID), c_id, career_path_filter_setting)

        return m


class ProjectSortByMenuButtonIcon(MenuButtonIcon):
    hint = GetByLabel('UI/Common/SortBy')
    default_texturePath = eveicon.bars_sort_ascending

    def GetMenu(self):
        m = MenuData()
        m.AddCaption(self.hint)
        m.AddRadioButton(GetByLabel('UI/Common/Name'), 'name', sort_by_setting)
        m.AddRadioButton(GetByLabel('UI/Inventory/NameReversed'), 'name_reversed', sort_by_setting)
        m.AddSeparator()
        m.AddRadioButton(GetByLabel('UI/Corporations/Goals/DateCreated'), 'date_created', sort_by_setting)
        m.AddRadioButton(GetByLabel('UI/Corporations/Goals/DateCreatedReversed'), 'date_created_reversed', sort_by_setting)
        m.AddSeparator()
        m.AddRadioButton(GetByLabel('UI/Common/TimeRemainingFilter'), 'time_remaining', sort_by_setting)
        m.AddRadioButton(GetByLabel('UI/Common/TimeRemainingReversedFilter'), 'time_remaining_reversed', sort_by_setting)
        m.AddSeparator()
        m.AddRadioButton(GetByLabel('UI/Corporations/Goals/Progress'), 'progress', sort_by_setting)
        m.AddRadioButton(GetByLabel('UI/Corporations/Goals/ProgressReversed'), 'progress_reversed', sort_by_setting)
        m.AddSeparator()
        m.AddRadioButton(GetByLabel('UI/Corporations/Goals/NumJumps'), 'num_jumps', sort_by_setting)
        m.AddRadioButton(GetByLabel('UI/Corporations/Goals/NumJumpsReversed'), 'num_jumps_reversed', sort_by_setting)
        return m
