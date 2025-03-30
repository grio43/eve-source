#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\careerPortalWnd.py
import math
import telemetry
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import Align, uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.uianimations import animations
from careergoals.client.career_goal_svc import get_career_goals_svc
from careergoals.client.feature_flag import is_air_career_program_enabled
from careergoals.client.signal import on_states_loaded, on_air_career_program_availability_changed
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.shared.careerPortal import careerConst, cpSignals
from eve.client.script.ui.shared.careerPortal.careerControllerUI import get_career_portal_controller_svc
from eve.client.script.ui.shared.careerPortal.careerPortalBackground import CareerPortalBackground
from eve.client.script.ui.shared.careerPortal.careerPortalTitle import CareerPortalTitle
from eve.client.script.ui.shared.careerPortal.circleView.activityView import ActivityView
from eve.client.script.ui.shared.careerPortal.circleView.careerView import CareerView
from eve.client.script.ui.shared.careerPortal.circleView.goalView import GoalView
from eve.client.script.ui.shared.careerPortal.failStates.noGoalsScreen import NoGoalsScreen
from eve.client.script.ui.shared.careerPortal.panels.panelConts import ActivityViewPanels, GoalViewPanels, GoalDetailPanels
from eve.client.script.ui.shared.careerPortal.progressBar import ProgressBar
from eve.client.script.ui.shared.careerPortal.rewards.rewardsCont import RewardsCont
from eve.client.script.ui.shared.mapView.dockPanel import DockablePanel
from eve.client.script.ui.view.viewStateConst import ViewState
from localization import GetByLabel
from stackless_response_router.exceptions import TimeoutException
SIDE_PADDING_WINDOWED = 24
SIDE_PADDING_FULLSCREEN = 48
SOUND_OPEN_PLAY = 'career_portal_open_play'
SOUND_BACKGROUND_LOOP_PLAY = 'career_portal_background_loop_play'
SOUND_BACKGROUND_LOOP_STOP = 'career_portal_background_loop_stop'

class CareerPortalDockablePanel(DockablePanel):
    default_windowID = 'careerPortal'
    default_captionLabelPath = 'UI/CareerPortal/CareerPortalWnd'
    default_descriptionLabelPath = 'UI/CareerPortal/CareerPortalWndDescription'
    default_iconNum = 'res:/ui/texture/windowIcons/airCareerProgram.png'
    default_width = 900
    default_height = 750
    default_minSize = (default_width, default_height)
    default_clipChildren = True
    panelID = default_windowID
    viewState = ViewState.CareerPortal
    hasImmersiveAudioOverlay = True

    def __init__(self, *args, **kwargs):
        super(CareerPortalDockablePanel, self).__init__(*args, **kwargs)
        self.infoPanelContainer.topCont.display = False
        self._load_data_thread = None
        self.construct_loading_wheel()
        self.load_data()
        PlaySound(SOUND_OPEN_PLAY)
        PlaySound(SOUND_BACKGROUND_LOOP_PLAY)

    @classmethod
    def Open(cls, *args, **kwds):
        if not is_air_career_program_enabled():
            ShowQuickMessage(GetByLabel('UI/CareerPortal/FeatureUnavailable'))
            return
        return super(CareerPortalDockablePanel, cls).Open(*args, **kwds)

    def Close(self, setClosed = False, *args, **kwds):
        try:
            PlaySound(SOUND_BACKGROUND_LOOP_STOP)
            self.kill_load_data_thread()
            self.disconnect_signals()
        finally:
            super(CareerPortalDockablePanel, self).Close(setClosed, *args, **kwds)

    def kill_load_data_thread(self):
        if self._load_data_thread is not None:
            self._load_data_thread.kill()
            self._load_data_thread = None

    def connect_signals(self):
        on_states_loaded.connect(self.on_states_loaded)
        on_air_career_program_availability_changed.connect(self.on_air_career_program_availability_changed)

    def disconnect_signals(self):
        on_states_loaded.disconnect(self.on_states_loaded)
        on_air_career_program_availability_changed.disconnect(self.on_air_career_program_availability_changed)

    def construct_loading_wheel(self):
        self.loading_wheel = LoadingWheel(name='loading_wheel', parent=self, align=Align.CENTER, idx=0)

    def load_data(self):
        self.content.Flush()
        self.loading_wheel.Show()
        self.kill_load_data_thread()
        self._load_data_thread = uthread2.start_tasklet(self.load_data_async)

    def load_data_async(self):
        try:
            get_career_goals_svc().get_goal_data_controller().prime_definitions_and_states()
            self.on_data_load_success()
        except TimeoutException:
            self.on_data_load_fail()
        finally:
            self.loading_wheel.Hide()

    def on_data_load_success(self):
        self.construct_career_portal()
        self.update()
        self.connect_signals()

    def on_data_load_fail(self):
        no_goals_screen = NoGoalsScreen(name='no_goals_screen', parent=self.content)
        no_goals_screen.on_retry.connect(self.on_retry)

    def on_retry(self, no_goals_screen):
        try:
            no_goals_screen.on_retry.disconnect(self.on_retry)
        finally:
            self.load_data()

    def construct_career_portal(self):
        self.career_portal = CareerPortal(name='career_portal', parent=self.content, padTop=self.toolbarContainer.height)

    def update(self):
        is_fullscreen = self.IsFullscreen()
        self.career_portal.is_fullscreen = is_fullscreen
        self.career_portal.padTop = 0 if is_fullscreen else self.toolbarContainer.height

    def on_states_loaded(self, *args):
        self.reload_window()

    def on_air_career_program_availability_changed(self, *args):
        if not is_air_career_program_enabled():
            ShowQuickMessage(GetByLabel('UI/CareerPortal/FeatureUnavailable'))
            self.Close()

    def on_reload_button(self, *args):
        self.reload_window()

    def reload_window(self, *args):
        self.Reload(self)

    def navigate_to_node(self, career_id = None, activity_id = None, goal_id = None):
        self.career_portal.navigate_to_node(career_id, activity_id, goal_id)

    def OnBack(self):
        current_state = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        if current_state == careerConst.CareerWindowState.GOALS_VIEW:
            new_state = careerConst.CareerWindowState.ACTIVITIES_VIEW
        else:
            new_state = careerConst.CareerWindowState.CAREERS_VIEW
        careerConst.CAREER_WINDOW_STATE_SETTING.set(new_state)


class CareerPortal(Container):
    default_state = uiconst.UI_NORMAL
    default_opacity = 0

    def __init__(self, *args, **kwargs):
        super(CareerPortal, self).__init__(*args, **kwargs)
        self._is_fullscreen = True
        self._is_ui_constructed = False
        self.construct_layout()

    @telemetry.ZONE_METHOD
    def construct_layout(self):
        self.content = Container(name='content', parent=self)
        self.clip_container = Container(name='clip_container', parent=self.content, clipChildren=True)
        initialState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        self.construct_central_container(initialState)
        self.construct_header()
        self.construct_footer()
        self.construct_left_side_panels()
        self.construct_right_side_panels(initialState)
        self.backgroundContainer = CareerPortalBackground(parent=self, name='background', align=Align.TOALL)
        self.backgroundContainer.OnCareerWindowStateChanged(initialState)
        self._is_ui_constructed = True
        self.update()
        animations.FadeIn(self, duration=1.5)

    def construct_header(self):
        CareerPortalTitle(name='career_portal_title', parent=self.clip_container, align=Align.TOTOP_PROP, height=0.1)

    def construct_footer(self):
        footer = Container(name='footer', parent=self.clip_container, align=Align.TOBOTTOM_NOPUSH, height=30, top=24)
        ProgressBar(name='progress_bar', parent=Container(parent=footer, align=Align.TOALL), align=Align.TOTOP, label=GetByLabel('UI/CareerPortal/OverallProgress'))
        GradientSprite(name='progress_bar_gradient', parent=self.clip_container, align=Align.TOBOTTOM_PROP, state=uiconst.UI_DISABLED, rgbData=((0, (0.0, 0.0, 0.0)), (0.55, (0.0, 0.0, 0.0)), (1.0, (0.0, 0.0, 0.0))), alphaData=((0.0, 1.0), (0.55, 1.0), (1.0, 0.0)), rotation=math.pi / 2, height=0.1)

    def construct_central_container(self, initialState):
        central_container = Container(name='central_container', parent=self, align=Align.TOALL)
        CareerView(parent=central_container, initialState=initialState)
        ActivityView(parent=central_container, initialState=initialState)
        GoalView(parent=central_container, initialState=initialState)

    def construct_right_side_panels(self, initialState):
        self.right_side_panel = ScrollContainer(name='right_side_panel', parent=self.clip_container, align=Align.TORIGHT_PROP, width=0.2)
        GoalDetailPanels(parent=self.right_side_panel, initialState=initialState)
        ActivityViewPanels(parent=self.right_side_panel, initialState=initialState)
        GoalViewPanels(parent=self.right_side_panel, initialState=initialState)

    def construct_left_side_panels(self):
        self.left_side_panel = Container(name='left_side_panel', parent=self.clip_container, align=Align.TOLEFT_PROP, width=0.2)
        self.rewards = RewardsCont(name='rewards', parent=self.left_side_panel, align=Align.TOTOP)

    def update(self):
        if self._is_fullscreen:
            self.content.padLeft = SIDE_PADDING_FULLSCREEN
            self.content.padRight = SIDE_PADDING_FULLSCREEN
        else:
            self.content.padLeft = SIDE_PADDING_WINDOWED
            self.content.padRight = SIDE_PADDING_WINDOWED

    def navigate_to_node(self, career_id = None, activity_id = None, goal_id = None):
        animations.FadeOut(obj=self.clip_container, duration=0.2, callback=lambda : self.make_selection(career_id, activity_id, goal_id))

    def make_selection(self, career_id = None, activity_id = None, goal_id = None):
        if career_id:
            get_career_portal_controller_svc().select_career(career_id, goal_id)
        if activity_id:
            activity_name = careerConst.GetCareerPathGroupName(career_id, activity_id)
            get_career_portal_controller_svc().select_activity(activity_id, activity_name, career_id)
        if goal_id:
            get_career_portal_controller_svc().select_goal(goal_id)

    @property
    def is_fullscreen(self):
        return self._is_fullscreen

    @is_fullscreen.setter
    def is_fullscreen(self, value):
        self._is_fullscreen = value
        self.update()

    def _OnSizeChange_NoBlock(self, width, height):
        super(CareerPortal, self)._OnSizeChange_NoBlock(width, height)
        if not self._is_ui_constructed:
            return
        self.backgroundContainer.SetSize(width, height)
        if width >= 1860:
            self.left_side_panel.width = self.right_side_panel.width = 0.2
        else:
            self.left_side_panel.width = self.right_side_panel.width = 0.25

    def OnClick(self, *args):
        cpSignals.on_clicked_outside()
        self.right_side_panel.Disable()
