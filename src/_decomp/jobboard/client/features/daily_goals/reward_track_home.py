#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\reward_track_home.py
import math
import uthread2
import carbonui
import eveui
from carbonui.control.contextMenu.menuEntryData import MenuEntryDataSlider
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from eve.client.script.ui import eveColor
from jobboard.client.features.daily_goals.milestones import HomePageMilestone
from jobboard.client.qa_tools import is_qa
from jobboard.client import get_job_board_service, ProviderType
from .reward_track_progress import RewardTrackArrow, ProgressStates
from .bonus_rewards import DailyBonusGauge
from localization import GetByLabel
MILESTONE_NUMBER_TO_TEXT = {1: GetByLabel('UI/Common/Count/First'),
 2: GetByLabel('UI/Common/Count/Second'),
 3: GetByLabel('UI/Common/Count/Third'),
 4: GetByLabel('UI/Common/Count/Fourth')}

class RewardTrackHome(Container):
    default_align = carbonui.Align.CENTER
    default_width = 220
    default_height = 220

    def __init__(self, daily_job = None, alpha_jobs = None, omega_jobs = None, *args, **kwargs):
        super(RewardTrackHome, self).__init__(*args, **kwargs)
        self._provider = get_job_board_service().get_provider(ProviderType.DAILY_GOALS)
        self._daily_job = daily_job
        self._alpha_jobs = alpha_jobs
        self._omega_jobs = omega_jobs
        self._hover_center = None
        self._progress_points = []
        self._lines = []
        self._progress = self._provider.get_reward_track_progress()
        self._animation_tasklet = None
        self._layout()
        self._progress_gauge.update(self._daily_job)
        self._on_reward_track_progressed()
        self._daily_job.on_job_updated.connect(self._on_daily_job_updated)
        self._provider.on_reward_track_progressed.connect(self._on_reward_track_progressed)

    def Close(self):
        super(RewardTrackHome, self).Close()
        self._daily_job.on_job_updated.disconnect(self._on_daily_job_updated)
        self._provider.on_reward_track_progressed.disconnect(self._on_reward_track_progressed)

    def _on_daily_job_updated(self):
        self._progress_gauge.update(self._daily_job)
        if self._daily_job.current_progress == 1:
            self._update_progress()

    def _on_reward_track_progressed(self):
        self._progress = self._provider.get_reward_track_progress()
        self._update_progress()

    def has_daily_bonus_progress(self):
        return self._daily_job.current_progress == 1

    def _update_progress(self):
        if self._animation_tasklet:
            self._animation_tasklet.Kill()
        self._animation_tasklet = uthread2.start_tasklet(self.__update_progress)

    def __update_progress(self):
        for index, progress_point in enumerate(self._progress_points):
            if self._progress > index:
                state = ProgressStates.COMPLETED
            elif self._progress == index and self.has_daily_bonus_progress():
                state = ProgressStates.ACTIVE
            else:
                state = ProgressStates.INACTIVE
            progress_point.set_state(state, animate=True)
            uthread2.sleep(0.1)

    def _layout(self):
        self._milestones_container = Container(name='milestones', parent=self, align=carbonui.Align.TOALL)
        self._main_view = Container(name='main_view', parent=self, align=carbonui.Align.TOALL)
        self._arrow_container = Container(name='arrows', parent=self._main_view, align=carbonui.Align.TOALL)
        self._hover_view = Container(name='hover_view', parent=self, align=carbonui.Align.TOALL, opacity=0)
        self._construct_progress_points()
        self._construct_daily_bonus()

    def _construct_progress_points(self):
        self._construct_arrow(rotation=-math.radians(30))
        self._construct_arrow(rotation=-math.radians(60))
        self._construct_milestone(align=carbonui.Align.CENTERRIGHT, milestone_number=1)
        self._construct_arrow(rotation=-math.radians(120))
        self._construct_arrow(rotation=-math.radians(150))
        self._construct_milestone(align=carbonui.Align.CENTERBOTTOM, milestone_number=2)
        self._construct_arrow(rotation=math.radians(150))
        self._construct_arrow(rotation=math.radians(120))
        self._construct_milestone(align=carbonui.Align.CENTERLEFT, milestone_number=3)
        self._construct_arrow(rotation=math.radians(60))
        self._construct_arrow(rotation=math.radians(30))
        self._construct_milestone(align=carbonui.Align.CENTERTOP, milestone_number=4)

    def _construct_daily_bonus(self):
        container = Container(name='daily_bonus', parent=self._main_view, align=carbonui.Align.CENTER, height=133, width=133)
        Sprite(parent=container, align=carbonui.Align.CENTERBOTTOM, pickState=carbonui.PickState.OFF, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/home_track_center_circle.png', width=133, height=122)
        reward_container = ContainerAutoSize(name='reward_container', parent=container, align=carbonui.Align.CENTERTOP, height=32, top=-4)
        Sprite(name='icon', parent=reward_container, align=carbonui.Align.TOLEFT, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/bonus_reward_sp.png', width=24, height=32)
        carbonui.TextDetail(name='item_amount', parent=reward_container, align=carbonui.Align.TOLEFT, padTop=8, text=self._daily_job.rewards[0].amount_text)
        self._progress_gauge = DailyBonusGauge(parent=container)

    def _construct_arrow(self, rotation):
        container = Transform(name='arrow', parent=self._arrow_container, align=carbonui.Align.TOALL, rotation=rotation)
        arrow = RewardTrackArrow(parent=container, align=carbonui.Align.CENTERTOP, top=12, width=47, height=12, texture_path='res:/UI/Texture/classes/Opportunities/DailyGoals/progress_arrow_home.png', bg_color=(0, 0, 0, 0.5))
        self._progress_points.append(arrow)

    def _construct_milestone(self, align, milestone_number):
        milestone_marker = RewardTrackMilestoneMarker(parent=self._milestones_container, align=align)
        milestone_marker.OnMouseEnter = (self._show_milestone, milestone_number)
        self._progress_points.append(milestone_marker)

    def _construct_hover_view(self):
        if self._hover_center:
            return
        self._hover_center = Container(parent=self._hover_view, pickState=carbonui.PickState.ON, align=carbonui.Align.CENTER, width=140, height=140)
        self._hover_center.OnMouseExit = self.OnMouseExit
        line_positions = (((12, 20), (94, 100)),
         ((-94, 100), (-12, 20)),
         ((-12, 200), (-94, 120)),
         ((94, 120), (12, 200)))
        for points in line_positions:
            line = VectorLineTrace(parent=self._hover_view, align=carbonui.Align.CENTERTOP, end=0)
            line.AddPoints(points, color=(1, 1, 1, 0.3))
            self._lines.append(line)

    @property
    def _in_main_view(self):
        return self._main_view.pickState == carbonui.PickState.ON

    def _is_omega(self):
        return sm.GetService('cloneGradeSvc').IsOmega()

    def _show_milestone(self, milestone_number):
        PlaySound('monthly_progress_hover_milestone_on_play')
        self._construct_hover_view()
        self._main_view.pickState = carbonui.PickState.OFF
        eveui.fade_out(self._main_view, duration=0.3)
        eveui.fade_in(self._hover_view, duration=0.3)
        for line in self._lines:
            eveui.animate(line, 'end', start_value=0, end_value=1, duration=0.6)

        self._hover_view.pickState = carbonui.PickState.ON
        self._hover_center.Flush()
        carbonui.TextDetail(parent=self._hover_center, align=carbonui.Align.CENTERTOP, text=MILESTONE_NUMBER_TO_TEXT[milestone_number])
        carbonui.TextDetail(parent=self._hover_center, align=carbonui.Align.CENTERTOP, text=GetByLabel('UI/DailyGoals/Milestone'), top=16)
        index = milestone_number - 1
        if self._omega_jobs:
            HomePageMilestone(parent=self._hover_center, name='omega_milestone', align=carbonui.Align.TOLEFT, job=self._omega_jobs[index], is_final=milestone_number == 4, is_omega_restricted=not self._is_omega() and self._omega_jobs[index].are_rewards_omega_restricted, scale=0.82)
        if self._alpha_jobs:
            HomePageMilestone(parent=self._hover_center, name='alpha_milestone', align=carbonui.Align.TORIGHT, job=self._alpha_jobs[index], is_final=milestone_number == 4, scale=0.82)

    def _show_main_view(self):
        if self._in_main_view:
            return
        self._hover_view.pickState = carbonui.PickState.OFF
        eveui.fade_out(self._hover_view, duration=0.3)
        eveui.fade_in(self._main_view, duration=0.3)
        self._main_view.pickState = carbonui.PickState.ON

    def OnMouseExit(self, *args):
        PlaySound('monthly_progress_hover_milestone_off_play')
        self._show_main_view()


class RewardTrackMilestoneMarker(Container):
    default_state = carbonui.uiconst.UI_NORMAL
    default_height = 40
    default_width = 40
    OUTER_STATE_COLOR = {ProgressStates.INACTIVE: (0, 0, 0, 0),
     ProgressStates.ACTIVE: eveColor.Color(*eveColor.AIR_TURQUOISE).SetAlpha(0.9).GetRGBA(),
     ProgressStates.COMPLETED: eveColor.SUCCESS_GREEN}
    INNER_STATE_COLOR = {ProgressStates.INACTIVE: eveColor.Color(*eveColor.AIR_TURQUOISE).SetAlpha(0.3).GetRGBA(),
     ProgressStates.ACTIVE: eveColor.Color(*eveColor.AIR_TURQUOISE).SetAlpha(0.3).GetRGBA(),
     ProgressStates.COMPLETED: eveColor.BLACK}

    def __init__(self, *args, **kwargs):
        super(RewardTrackMilestoneMarker, self).__init__(*args, **kwargs)
        self._layout()

    def _layout(self):
        self._checkmark = Sprite(parent=self, align=carbonui.Align.CENTER, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/milestone_checkmark_home.png', outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.5, height=8, width=10, opacity=0)
        self._inner = Sprite(parent=self, align=carbonui.Align.CENTER, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/milestone_marker_base_24.png', height=24, width=24, color=self.INNER_STATE_COLOR[ProgressStates.INACTIVE])
        self._outer = Sprite(parent=self, align=carbonui.Align.CENTER, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/milestone_marker_outer_30.png', height=30, width=30, outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.4, color=self.OUTER_STATE_COLOR[ProgressStates.INACTIVE])
        Sprite(parent=self, align=carbonui.Align.CENTER, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/milestone_marker_base_24.png', height=30, width=30, color=(0, 0, 0, 0.9))

    def set_state(self, state, animate = True):
        duration = 0.3 if animate else 0
        eveui.animate(self._outer, 'color', end_value=self.OUTER_STATE_COLOR[state], duration=duration)
        eveui.animate(self._inner, 'color', end_value=self.INNER_STATE_COLOR[state], duration=duration)
        if state == ProgressStates.COMPLETED:
            eveui.fade_in(self._checkmark, duration=duration)
        else:
            self._outer.glowBrightness = 0.3
            eveui.fade_out(self._checkmark, duration=duration)
        eveui.animate(self._outer, 'glowBrightness', end_value=2, curve_type=eveui.CurveType.wave, duration=duration)
