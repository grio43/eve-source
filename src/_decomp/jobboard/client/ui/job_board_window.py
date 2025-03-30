#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\job_board_window.py
from carbonui.control.sideNavigation import SideNavigationSplitView
from carbonui.uiconst import PickState, IdealSize
from carbonui.control.window import Window
from carbonui.primitives.split_view import SplitView, PanelMode
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from eve.client.script.ui import eveColor
import eveui
import localization
import uthread2
import dailygoals.client.goalSignals as dailyGoalSignals
from jobboard.client import qa_tools, job_board_signals, get_job_board_service
from jobboard.client.job_board_settings import open_opportunities_on_startup_setting, guidance_highlighting_disabled_setting, fixed_expanded_side_navigation_setting
from .controller import WindowController
from .pages.details_page import DetailsPage
from .history_bar import HistoryBar
from .side_navigation import JobBoardSideNavigation
from .tab_with_count import TabWithCount
from eve.client.script.ui.shared.pointerTool import pointerToolConst as pConst
JOB_BOARD_WINDOW_ID = 'job_board'

class JobBoardWindow(Window):
    default_name = 'JobBoardWindow'
    default_windowID = JOB_BOARD_WINDOW_ID
    default_width = IdealSize.SIZE_720
    default_height = IdealSize.SIZE_960
    default_minSize = (IdealSize.SIZE_480, IdealSize.SIZE_480)
    default_apply_content_padding = False
    default_captionLabelPath = 'UI/Opportunities/WindowTitle'
    default_descriptionLabelPath = 'UI/Opportunities/WindowDescription'
    default_iconNum = 'res:/ui/Texture/WindowIcons/opportunities.png'

    def __init__(self, **kwargs):
        super(JobBoardWindow, self).__init__(**kwargs)
        self._controller = WindowController()
        job_board_signals.on_job_window_initializing()
        self.OnBack = self._controller.go_back
        self.OnForward = self._controller.go_forward
        self._expand_thread = None
        self._layout()
        self._register_generic()
        uthread2.start_tasklet(self._initialize_counters)

    def _initialize_counters(self):
        self._update_counters()
        self._register_counters()

    @classmethod
    def Open(cls, *args, **kwargs):
        window = super(JobBoardWindow, cls).Open(*args, **kwargs)
        if not hasattr(window, '_controller'):
            return window
        window._controller.open_page(**kwargs)
        return window

    def Close(self, *args, **kwds):
        try:
            self._unregister()
            if hasattr(self, '_controller'):
                self._controller.close()
        finally:
            super(JobBoardWindow, self).Close(*args, **kwds)

    def _register_generic(self):
        self._controller.on_page_change.connect(self._on_page_change)
        self.on_content_padding_changed.connect(self._on_content_padding_changed)

    def _register_counters(self):
        job_board_signals.on_job_state_changed.connect(self._update_counters_debounced)
        job_board_signals.on_job_added.connect(self._update_counters_debounced)
        job_board_signals.on_job_removed.connect(self._update_counters_debounced)
        job_board_signals.on_tracked_jobs_changed.connect(self._update_counters_debounced)
        dailyGoalSignals.on_goal_payment_redeemed.connect(self._update_counters_debounced)

    def _unregister(self):
        self.on_content_padding_changed.disconnect(self._on_content_padding_changed)
        job_board_signals.on_job_state_changed.disconnect(self._update_counters_debounced)
        job_board_signals.on_job_added.disconnect(self._update_counters_debounced)
        job_board_signals.on_job_removed.disconnect(self._update_counters_debounced)
        job_board_signals.on_tracked_jobs_changed.disconnect(self._update_counters_debounced)
        dailyGoalSignals.on_goal_payment_redeemed.disconnect(self._update_counters_debounced)
        if hasattr(self, '_controller'):
            self._controller.on_page_change.disconnect(self._on_page_change)

    def is_job_open(self, job_id):
        if self._controller.page_id != 'details':
            return False
        return self._controller.page_controller.job_id == job_id

    def _NotifyOfMaximized(self, wasMinimized):
        super(JobBoardWindow, self)._NotifyOfMaximized(wasMinimized)
        if wasMinimized:
            job_board_signals.on_job_window_maximized()

    def _layout(self):
        self.header.tab_group.AddTab(label=localization.GetByLabel('UI/Opportunities/WindowTitle'), tabID='browse')
        self._active_tab = self.header.tab_group.AddTab(label=localization.GetByLabel('UI/Opportunities/TabNameActive'), tabID='active', tabClass=TabWithCount, uniqueName=pConst.UNIQUE_NAME_ACTIVE_OPPORTUNITIES)
        self._rewards_tab = self.header.tab_group.AddTab(label=localization.GetByLabel('UI/Opportunities/TabNameUnclaimedRewards'), tabID='unclaimed_rewards', tabClass=TabWithCount, count_bg_color=eveColor.WARNING_ORANGE, uniqueName=pConst.UNIQUE_NAME_OPPORTUNITY_REWARDS)
        self._split_view = SideNavigationSplitView(is_always_expanded_setting=fixed_expanded_side_navigation_setting, parent=self.content, expanded_panel_width=240)
        self._side_navigation = JobBoardSideNavigation(parent=self._split_view.panel, controller=self._controller, is_expanded_func=self._split_view.is_expanded, expand_func=self._split_view.expand_panel, is_always_expanded_setting=fixed_expanded_side_navigation_setting, uniqueUiName=pConst.UNIQUE_NAME_OPPORTUNITY_BROWSER)
        self._split_view.on_expanded_changed.connect(self._side_navigation.on_expanded_changed)
        self._history_bar = HistoryBar(parent=self._split_view.content, align=eveui.Align.to_top, controller=self._controller)
        self._content_container = eveui.Container(name='content_container', parent=self._split_view.content, align=eveui.Align.to_all)
        self._on_content_padding_changed()

    def _on_content_padding_changed(self, *args, **kwargs):
        padding = self.content_padding
        self._content_container.padding = (padding[0],
         0,
         padding[2],
         padding[3])
        self._history_bar.padding = (padding[0],
         8,
         padding[2],
         8)

    def _on_page_change(self, page_id):
        page_controller = self._controller.page_controller
        tab_id = page_controller.window_tab_id
        if not tab_id and not self.header.tab_group.GetSelectedID():
            tab_id = 'browse'
        self.header.tab_group.SelectByID(tab_id, useCallback=False)
        self._content_container.Flush()
        page = page_controller.construct_page(parent=self._content_container, window_controller=self._controller)
        eveui.fade(self._split_view.content, start_value=0.0, end_value=1.0, duration=0.5, on_complete=lambda : self._on_faded_in(page))

    def _on_faded_in(self, page):
        if hasattr(page, 'on_faded_in'):
            page.on_faded_in(light_background_enabled=self.light_background_enabled)

    def _tab_selected(self, tabID, oldTabID):
        self._controller.open_page(tabID)

    def GetMenuMoreOptions(self):
        menu_data = super(JobBoardWindow, self).GetMenuMoreOptions()
        menu_data.AddCheckbox(localization.GetByLabel('UI/Opportunities/OpenOnStartup'), setting=open_opportunities_on_startup_setting)
        menu_data.AddCheckbox(localization.GetByLabel('UI/Opportunities/DisableGuidanceHighlightingSetting'), setting=guidance_highlighting_disabled_setting)
        if self._controller.page_id == 'details':
            job = get_job_board_service().get_job(self._controller.page_controller.job_id, wait=False)
            job_menu = job.get_menu() if job else None
            if job_menu:
                menu_data.AddSeparator()
                menu_data.AddEntry(localization.GetByLabel('UI/Opportunities/Opportunity'), subMenuData=job_menu)
        if qa_tools.is_qa():
            qa_tools.add_window_context_menu(menu_data)
        return menu_data

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader(on_tab_selected=self._tab_selected)

    def _UpdateContentPadding(self):
        if self.closing:
            return
        super(JobBoardWindow, self)._UpdateContentPadding()
        self.content.padTop = 0

    @uthread2.debounce(0.2)
    def _update_counters_debounced(self, *args, **kwargs):
        self._update_counters()

    def _update_counters(self):
        service = get_job_board_service()
        self._active_tab.count = len(service.get_active_jobs())
        self._rewards_tab.count = len(service.get_jobs_with_unclaimed_rewards())


class JobDetailsWindow(Window):
    default_name = 'JobDetailsWindow'
    default_windowID = 'job_details'
    default_captionLabelPath = 'UI/Opportunities/WindowTitle'
    default_width = 730
    default_height = 880
    default_minSize = (500, 500)
    default_isCompact = True
    default_clipChildren = True

    def __init__(self, job = None, job_id = None, **kwargs):
        if job:
            kwargs['caption'] = self._get_job_caption(job)
        else:
            self._register()
        self.job_id = job_id
        super(JobDetailsWindow, self).__init__(**kwargs)
        self._content_container = eveui.Container(name='content_container', parent=self.content, align=eveui.Align.to_all, padding=(8, 0, 8, 0))
        self._update()

    def _register(self):
        job_board_signals.on_job_added.connect(self._on_job_added)

    def _unregister(self):
        job_board_signals.on_job_added.disconnect(self._on_job_added)

    def _on_job_added(self, job):
        if job.job_id == self.job_id:
            self._unregister()
            self.caption = self._get_job_caption(job)

    def _get_job_caption(self, job):
        return u'{} - {}'.format(job.title, job.feature_title)

    def _update(self):
        self._content_container.Flush()
        DetailsPage(parent=self._content_container, job_id=self.job_id)
        eveui.fade(self.content, start_value=0.0, end_value=1.0, duration=0.5)

    def GetMenuMoreOptions(self):
        menu_data = super(JobDetailsWindow, self).GetMenuMoreOptions()
        job = get_job_board_service().get_job(self.job_id, wait=False)
        job_menu = job.get_menu() if job else None
        if job_menu:
            menu_data.AddSeparator()
            menu_data.entrylist.extend(job_menu)
        return menu_data
