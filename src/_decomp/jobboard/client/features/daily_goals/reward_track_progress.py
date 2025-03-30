#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\reward_track_progress.py
import math
import eveui
import uthread2
import carbonui
from carbonui.uicore import uicore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from carbonui import Align, PickState, uiconst

class ProgressStates(object):
    INACTIVE = 'inactive'
    ACTIVE = 'active'
    COMPLETED = 'completed'


STATE_COLOR = {ProgressStates.INACTIVE: (0, 0, 0, 0),
 ProgressStates.ACTIVE: eveColor.Color(*eveColor.AIR_TURQUOISE).SetAlpha(0.9).GetRGBA(),
 ProgressStates.COMPLETED: eveColor.SUCCESS_GREEN}

class RewardTrackArrow(Container):
    default_width = 36
    default_height = 8

    def __init__(self, texture_path = 'res:/UI/Texture/classes/Opportunities/DailyGoals/progress_arrow.png', bg_color = (1, 1, 1, 0.2), *args, **kwargs):
        super(RewardTrackArrow, self).__init__(*args, **kwargs)
        self._texture_path = texture_path
        self._bg_color = bg_color
        self._state_arrow = None
        self._state = None
        self._layout()

    def _layout(self):
        self._sweep_arrow = Sprite(parent=self, align=carbonui.Align.TOALL, pickState=carbonui.PickState.OFF, texturePath=self._texture_path, outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.2, opacity=0)
        self._state_arrow = Sprite(parent=self, align=carbonui.Align.TOALL, pickState=carbonui.PickState.OFF, texturePath=self._texture_path, outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.4, opacity=0)
        Sprite(parent=self, align=carbonui.Align.TOALL, pickState=carbonui.PickState.OFF, texturePath=self._texture_path, color=self._bg_color)

    def set_state(self, state, animate = True):
        color = STATE_COLOR[state]
        eveui.animate(self._state_arrow, 'color', color, duration=0.5 if animate else 0)
        if animate and state != ProgressStates.INACTIVE:
            self._sweep()

    def _sweep(self):
        eveui.fade_in(self._sweep_arrow, end_value=0.7, duration=0.05)
        uicore.animations.SpSwoopBlink(self._sweep_arrow, startVal=(-1, 0.0), endVal=(1, 0.0), rotation=math.pi * 0.9, duration=0.8)


class FeaturePageProgressBar(eveui.Container):
    default_height = 32
    default_width = 424

    def __init__(self, progress, *args, **kwargs):
        super(FeaturePageProgressBar, self).__init__(*args, **kwargs)
        self._progress = progress
        self._progress_points = []
        self._daily_bonus_goal_progress = 0
        self._progress_bar = None
        self._animation_tasklet = None
        self._layout()

    def set_progress(self, track_progress, bonus_goal_progress):
        self._progress = track_progress
        self._daily_bonus_goal_progress = bonus_goal_progress
        if self._animation_tasklet:
            self._animation_tasklet.Kill()
        self._animation_tasklet = uthread2.start_tasklet(self._update_progress)

    def _has_daily_bonus_progress(self):
        return self._daily_bonus_goal_progress == 1

    def _update_progress(self):
        for index, progress_point in enumerate(self._progress_points):
            if self._progress > index:
                state = ProgressStates.COMPLETED
            elif self._progress == index and self._has_daily_bonus_progress():
                state = ProgressStates.ACTIVE
            else:
                state = ProgressStates.INACTIVE
            progress_point.set_state(state, animate=True)
            uthread2.sleep(0.1)

    def _set_background(self):
        Sprite(name='background', parent=self, align=Align.CENTER, pickState=PickState.OFF, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/ombre_bar.png', width=self.width, height=self.height)

    def _layout(self):
        self._progress_bar = ContainerAutoSize(parent=self, align=Align.CENTER, height=self.height, width=self.width)
        self._construct_marker()
        self._construct_arrow()
        self._construct_arrow()
        self._construct_marker()
        self._construct_arrow()
        self._construct_arrow()
        self._construct_marker()
        self._construct_arrow()
        self._construct_arrow()
        self._construct_marker()
        self._construct_arrow()
        self._construct_arrow()
        self._progress_points.reverse()
        self._set_background()

    def _construct_arrow(self):
        container = Container(name='arrow', parent=self._progress_bar, align=Align.TORIGHT, width=36, height=8)
        arrow = RewardTrackArrow(parent=container, align=Align.CENTER, width=36, height=8, texture_path='res:/UI/Texture/classes/Opportunities/DailyGoals/progress_arrow.png', bg_color=eveColor.Color(eveColor.WHITE).SetOpacity(0.2).GetRGBA())
        self._progress_points.append(arrow)

    def _construct_marker(self):
        marker = MilestoneMarker(parent=self._progress_bar, align=Align.TORIGHT, width=20, padLeft=2, is_completed=False)
        self._progress_points.append(marker)


class MilestoneMarker(eveui.Container):
    default_width = 20
    DEFAULT_MARKER_STATE_COLOR = {ProgressStates.INACTIVE: eveColor.Color(eveColor.WHITE).SetOpacity(0.3).GetRGBA(),
     ProgressStates.ACTIVE: eveColor.Color(*eveColor.AIR_TURQUOISE).SetAlpha(0.9).GetRGBA(),
     ProgressStates.COMPLETED: eveColor.SUCCESS_GREEN}

    def __init__(self, *args, **kwargs):
        super(MilestoneMarker, self).__init__(*args, **kwargs)
        self._construct_layout()

    def set_state(self, state, animate):
        duration = 0.3 if animate else 0
        eveui.animate(self._default_marker, 'color', end_value=self.DEFAULT_MARKER_STATE_COLOR[state], duration=duration)
        if state == ProgressStates.COMPLETED:
            eveui.fade_in(self._checkmark, duration=duration)
        else:
            self._default_marker.glowBrightness = 0.3
            eveui.fade_out(self._checkmark, duration=duration)

    def _construct_layout(self):
        self._checkmark = Sprite(parent=self, align=Align.CENTER, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/milestone_marker_complete.png', glowBrightness=0.5, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, width=20, height=20, opacity=0)
        self._default_marker = Sprite(parent=self, align=Align.CENTER, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/milestone_marker.png', outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0, color=eveColor.Color(eveColor.WHITE).SetOpacity(0.3).GetRGBA(), width=20, height=20)
