#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\milestones.py
import eveui
import eveicon
import carbonui
import signals
import uthread2
import threadutils
from carbonui import Align, TextColor, PickState, TextDetail, TextCustom
from eve.client.script.ui import eveColor
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.cloneGrade import ORIGIN_OPPORTUNITIES
from carbon.client.script.environment.AudioUtil import PlaySound
from localization import GetByLabel, GetByMessageID
from eve.client.script.ui.control.tooltips import TooltipPanel
from itertoolsext.Enum import Enum
from carbonui.uianimations import animations
from jobboard.client import get_job_board_service
from metadata import ContentTags

@Enum

class MilestoneState(object):
    DEFAULT = 'DEFAULT'
    COMPLETED = 'COMPLETED'
    CLAIMED = 'CLAIMED'
    CLAIMING = 'CLAIMING'
    FINAL_DEFAULT = 'FINAL_DEFAULT'
    FINAL_COMPLETED = 'FINAL_COMPLETED'
    OMEGA_LOCKED = 'OMEGA_LOCKED'
    FINAL_OMEGA_LOCKED = 'FINAL_OMEGA_LOCKED'


MILESTONE_THEMES = {MilestoneState.DEFAULT: {'color': eveColor.AIR_TURQUOISE,
                          'outer_glow_opacity': 0,
                          'outer_glow_color': eveColor.AIR_TURQUOISE,
                          'inner_glow_color': eveColor.AIR_TURQUOISE,
                          'frame_color': eveColor.Color(eveColor.AIR_TURQUOISE).SetOpacity(0.1).GetRGBA(),
                          'background_color': eveColor.Color(eveColor.AIR_TURQUOISE).SetOpacity(0.2).GetRGBA(),
                          'outer_glow_hover': 0.3,
                          'inner_glow_opacity': 0.2,
                          'text_color': TextColor.NORMAL,
                          'text_color_hover': TextColor.HIGHLIGHT,
                          'icon_color': TextColor.NORMAL,
                          'icon_color_hover': TextColor.HIGHLIGHT,
                          'icon_size': 32,
                          'duration': 0.1},
 MilestoneState.COMPLETED: {'outer_glow_color': eveColor.LEAFY_GREEN,
                            'inner_glow_color': eveColor.LEAFY_GREEN,
                            'frame_color': eveColor.Color(eveColor.LEAFY_GREEN).SetOpacity(0.1).GetRGBA(),
                            'background_color': eveColor.Color(eveColor.LEAFY_GREEN).SetOpacity(0.2).GetRGBA(),
                            'outer_glow_opacity': 0.8,
                            'outer_glow_hover': 1,
                            'inner_glow_opacity': 0.2,
                            'text_color': TextColor.HIGHLIGHT,
                            'text_color_hover': TextColor.HIGHLIGHT,
                            'icon_color': TextColor.HIGHLIGHT,
                            'icon_color_hover': TextColor.HIGHLIGHT,
                            'icon_size': 32,
                            'duration': 0.1},
 MilestoneState.CLAIMING: {'outer_glow_color': eveColor.Color(eveColor.WHITE).SetOpacity(0.1).GetRGBA(),
                           'inner_glow_color': eveColor.Color(eveColor.LEAFY_GREEN).SetOpacity(0.2).GetRGBA(),
                           'frame_color': eveColor.Color(eveColor.LEAFY_GREEN).SetOpacity(0.1).GetRGBA(),
                           'background_color': eveColor.Color(eveColor.WHITE).SetOpacity(0.9).GetRGBA(),
                           'outer_glow_opacity': 1,
                           'outer_glow_hover': 1,
                           'inner_glow_opacity': 0.0,
                           'text_color': eveColor.Color(eveColor.BLACK).SetOpacity(0.9).GetRGBA(),
                           'text_color_hover': eveColor.Color(eveColor.BLACK).SetOpacity(0.9).GetRGBA(),
                           'icon_color': eveColor.Color(eveColor.BLACK).SetOpacity(0.9).GetRGBA(),
                           'icon_color_hover': eveColor.Color(eveColor.BLACK).SetOpacity(0.9).GetRGBA(),
                           'icon_size': 32,
                           'duration': 0.1},
 MilestoneState.CLAIMED: {'outer_glow_color': eveColor.LEAFY_GREEN,
                          'inner_glow_color': eveColor.LEAFY_GREEN,
                          'frame_color': eveColor.Color(eveColor.LEAFY_GREEN).SetOpacity(0.1).GetRGBA(),
                          'background_color': eveColor.Color(eveColor.LEAFY_GREEN).SetOpacity(0.2).GetRGBA(),
                          'outer_glow_opacity': 0.0,
                          'outer_glow_hover': 0.6,
                          'inner_glow_opacity': 0.2,
                          'text_color': TextColor.DISABLED,
                          'text_color_hover': TextColor.SECONDARY,
                          'icon_color': eveColor.Color(eveColor.SUCCESS_GREEN).SetOpacity(0.25).GetRGBA(),
                          'icon_color_hover': eveColor.Color(TextColor.HIGHLIGHT).SetOpacity(0.25).GetRGBA(),
                          'icon_size': 32,
                          'duration': 0.5},
 MilestoneState.FINAL_DEFAULT: {'color': eveColor.AIR_TURQUOISE,
                                'outer_glow_opacity': 0.8,
                                'outer_glow_color': eveColor.AIR_TURQUOISE,
                                'inner_glow_color': eveColor.AIR_TURQUOISE,
                                'frame_color': eveColor.Color(eveColor.AIR_TURQUOISE).SetOpacity(0.1).GetRGBA(),
                                'background_color': eveColor.Color(eveColor.AIR_TURQUOISE).SetOpacity(0.3).GetRGBA(),
                                'outer_glow_hover': 1,
                                'inner_glow_opacity': 0.6,
                                'text_color': TextColor.HIGHLIGHT,
                                'text_color_hover': TextColor.HIGHLIGHT,
                                'icon_color': None,
                                'icon_color_hover': None,
                                'icon_size': 32,
                                'duration': 0.1},
 MilestoneState.FINAL_COMPLETED: {'outer_glow_color': eveColor.LEAFY_GREEN,
                                  'inner_glow_color': eveColor.LEAFY_GREEN,
                                  'frame_color': eveColor.Color(eveColor.LEAFY_GREEN).SetOpacity(0.1).GetRGBA(),
                                  'background_color': eveColor.Color(eveColor.LEAFY_GREEN).SetOpacity(0.3).GetRGBA(),
                                  'outer_glow_opacity': 0.6,
                                  'outer_glow_hover': 0.8,
                                  'inner_glow_opacity': 0.6,
                                  'text_color': TextColor.HIGHLIGHT,
                                  'text_color_hover': TextColor.HIGHLIGHT,
                                  'icon_color': None,
                                  'icon_color_hover': None,
                                  'icon_size': 32,
                                  'duration': 0.1},
 MilestoneState.OMEGA_LOCKED: {'outer_glow_color': eveColor.OMEGA_YELLOW,
                               'inner_glow_color': eveColor.SAND_YELLOW,
                               'frame_color': eveColor.Color(eveColor.SAND_YELLOW).SetOpacity(0.1).GetRGBA(),
                               'background_color': eveColor.Color(eveColor.SAND_YELLOW).SetOpacity(0.2).GetRGBA(),
                               'outer_glow_opacity': 0.4,
                               'outer_glow_hover': 0.6,
                               'inner_glow_opacity': 0.1,
                               'text_color': eveColor.OMEGA_YELLOW,
                               'text_color_hover': eveColor.OMEGA_YELLOW,
                               'icon_color': eveColor.OMEGA_YELLOW,
                               'icon_color_hover': eveColor.OMEGA_YELLOW,
                               'icon_size': 32,
                               'duration': 0.1},
 MilestoneState.FINAL_OMEGA_LOCKED: {'outer_glow_color': eveColor.OMEGA_YELLOW,
                                     'inner_glow_color': eveColor.SAND_YELLOW,
                                     'frame_color': eveColor.Color(eveColor.SAND_YELLOW).SetOpacity(0.1).GetRGBA(),
                                     'background_color': eveColor.Color(eveColor.SAND_YELLOW).SetOpacity(0.3).GetRGBA(),
                                     'outer_glow_opacity': 0.6,
                                     'outer_glow_hover': 0.8,
                                     'inner_glow_opacity': 0.6,
                                     'text_color': eveColor.OMEGA_YELLOW,
                                     'text_color_hover': eveColor.OMEGA_YELLOW,
                                     'icon_color': None,
                                     'icon_color_hover': None,
                                     'icon_size': 32,
                                     'duration': 0.1}}
STATE_TO_STATUS_TEXT = {MilestoneState.DEFAULT: 'UI/DailyGoals/notEarned',
 MilestoneState.FINAL_DEFAULT: 'UI/DailyGoals/notEarned',
 MilestoneState.COMPLETED: 'UI/DailyGoals/claimable',
 MilestoneState.FINAL_COMPLETED: 'UI/DailyGoals/claimable'}

class Milestone(eveui.ContainerAutoSize):
    default_height = 95
    default_width = 82

    def __init__(self, job, is_final, is_omega_restricted = False, scale = 1, *args, **kwargs):
        self._scale = scale
        self.default_width = self.default_width * scale
        self.default_height = self.default_height * scale
        kwargs['pickState'] = PickState.ON
        super(Milestone, self).__init__(*args, **kwargs)
        self._job = job
        self.is_final = is_final
        self._is_omega_restricted = is_omega_restricted
        self._state = self._find_milestone_state()
        self._theme = MILESTONE_THEMES[self._state]
        self.on_mouse_enter = signals.Signal('on_mouse_enter_milestone')
        self.on_mouse_exit = signals.Signal('on_mouse_exit_milestone')
        self._layout()

    @property
    def is_omega_locked(self):
        if self._state in [MilestoneState.OMEGA_LOCKED, MilestoneState.FINAL_OMEGA_LOCKED]:
            return True
        return False

    def set_state(self, state):
        self._on_state_changed(state)

    @threadutils.threaded
    def update_state(self):
        new_state = self._find_milestone_state()
        if new_state == self.state:
            return
        uthread2.sleep(self._job.target_progress * 0.1)
        if not self.destroyed:
            self._on_state_changed(new_state)

    def _find_milestone_state(self):
        if self._job.is_completed and not self._job.has_claimable_rewards and not self._job.has_unclaimed_omega_restricted_rewards:
            return MilestoneState.CLAIMED
        if self._is_omega_restricted:
            if self.is_final:
                return MilestoneState.FINAL_OMEGA_LOCKED
            return MilestoneState.OMEGA_LOCKED
        if not self.is_final:
            if not self._job.is_completed:
                return MilestoneState.DEFAULT
            if self._job.has_claimable_rewards:
                return MilestoneState.COMPLETED
        if not self._job.is_completed:
            return MilestoneState.FINAL_DEFAULT
        if self._job.has_claimable_rewards:
            return MilestoneState.FINAL_COMPLETED

    def _layout(self):
        self._construct_content()
        self._construct_omega_lock()
        self._construct_background()

    def _construct_content(self):
        self.main_container = eveui.Container(parent=self, align=Align.CENTER, height=self.height, width=self.width)
        reward_info_container = eveui.ContainerAutoSize(name='reward_info_container', parent=self.main_container, align=Align.CENTER, width=72 * self._scale)
        icon_container = eveui.Container(name='icon_container', parent=reward_info_container, align=Align.TOTOP, height=32 * self._scale)
        self.icon = Sprite(name='icon', parent=icon_container, align=Align.CENTER, pickState=PickState.OFF, texturePath=self._job.rewards[0].icon, color=self._theme['icon_color'], width=32 * self._scale, height=32 * self._scale, glowBrightness=0.2)
        self.label_container = eveui.Container(name='label_container', parent=reward_info_container, align=Align.TOTOP, height=16 * self._scale, padTop=4)
        self._construct_text()

    def _construct_text(self):
        self.text = TextDetail(parent=self.label_container, align=Align.CENTER, text=self._job.rewards[0].amount_text, color=self._theme['text_color'], shadowOffset=(0, 0))

    def _construct_omega_lock(self):
        omega_lock_container = eveui.ContainerAutoSize(name='omega_lock_container', parent=self.main_container, align=Align.TOTOP, height=24 * self._scale, display=self.is_omega_locked, padTop=-9)
        Sprite(name='lock', parent=omega_lock_container, align=Align.CENTER, pickState=PickState.OFF, texturePath=eveicon.locked, height=16 * self._scale, width=16 * self._scale, color=eveColor.OMEGA_YELLOW)
        Sprite(name='circle', parent=omega_lock_container, align=Align.CENTER, pickState=PickState.OFF, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/circle.png', height=24 * self._scale, width=24 * self._scale, color=eveColor.Color(eveColor.SAND_YELLOW).SetOpacity(0.1).GetRGBA())
        Sprite(name='circle_background', parent=omega_lock_container, align=Align.CENTER, pickState=PickState.OFF, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/circle.png', height=24 * self._scale, width=24 * self._scale, color=eveColor.Color(eveColor.BLACK).SetOpacity(0.9).GetRGBA())

    def _construct_background(self):
        self.inner_glow_hexagon = Sprite(name='inner_hexagon_glow', parent=self.main_container, align=Align.CENTER, pickState=PickState.OFF, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/inner_glow_hexagon.png', height=83 * self._scale, width=72 * self._scale, color=self._theme['inner_glow_color'], opacity=self._theme['inner_glow_opacity'])
        self.inner_hexagon = Sprite(name='inner_hexagon', parent=self.main_container, align=Align.CENTER, pickState=PickState.OFF, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/hexagon_inner.png', height=84 * self._scale, width=73 * self._scale, color=self._theme['background_color'])
        Sprite(parent=self.main_container, align=Align.CENTER, pickState=PickState.OFF, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/hexagon_inner.png', height=84 * self._scale, width=73 * self._scale, color=eveColor.Color(eveColor.BLACK).SetOpacity(0.9).GetRGBA())
        self.outer_hexagon = Sprite(name='outer_hexagon', pickState=PickState.OFF, parent=self.main_container, align=Align.CENTER, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/hexagon.png', height=95 * self._scale, width=83 * self._scale, color=self._theme['frame_color'])
        Sprite(parent=self.main_container, align=Align.CENTER, pickState=PickState.OFF, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/hexagon.png', height=95 * self._scale, width=83 * self._scale, color=eveColor.Color(eveColor.BLACK).SetOpacity(0.9).GetRGBA())
        self.outer_hex_glow = Sprite(name='outer_hexagon_glow', parent=self.main_container, align=Align.CENTER, pickState=PickState.OFF, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/outer_glow_hexagon.png', height=135 * self._scale, width=123 * self._scale, color=self._theme['outer_glow_color'], opacity=self._theme['outer_glow_opacity'])
        self._start_omega_pulse()

    @threadutils.threaded
    def _start_omega_pulse(self):
        if not self.is_omega_locked:
            return
        animations.MorphScalar(self.outer_hex_glow, 'opacity', duration=3, startVal=self.outer_hexagon.opacity, endVal=1, loops=carbonui.uiconst.ANIM_REPEAT, curveType=carbonui.uiconst.ANIM_BOUNCE)

    def OnMouseEnter(self, *args):
        super(Milestone, self).OnMouseEnter(*args)
        self.on_mouse_enter()
        PlaySound('monthly_progress_hover_milestone2_on_play')
        theme = MILESTONE_THEMES[self._state]
        eveui.animate(self.outer_hex_glow, 'opacity', theme['outer_glow_hover'], duration=0.1)
        if theme['icon_color_hover']:
            eveui.animate(self.icon, 'color', theme['icon_color_hover'], duration=0.1)
        if theme['text_color_hover']:
            eveui.animate(self.text, 'color', theme['text_color_hover'], duration=0.1)
        eveui.animate(self.icon, 'glowBrightness', 0, duration=0.1)

    def OnMouseExit(self, *args):
        self.on_mouse_exit()
        super(Milestone, self).OnMouseExit(*args)
        self._reset_milestone()

    def _reset_milestone(self):
        theme = MILESTONE_THEMES[self._state]
        eveui.animate(self.outer_hex_glow, 'opacity', theme['outer_glow_opacity'], duration=0.1)
        if theme['icon_color']:
            eveui.animate(self.icon, 'color', theme['icon_color'], duration=0.1)
        if theme['text_color']:
            eveui.animate(self.text, 'color', theme['text_color'], duration=0.1)
        eveui.animate(self.icon, 'glowBrightness', 0.2, duration=0.1)

    def OnClick(self, *args):
        super(Milestone, self).OnClick(*args)
        self._on_click()

    def _on_click(self):
        self._job.on_click_reward()

    def _on_state_changed(self, state):
        self._state = state
        self._theme = MILESTONE_THEMES[self._state]
        eveui.animate(self.outer_hex_glow, 'color', self._theme['outer_glow_color'], duration=self._theme['duration'])
        eveui.animate(self.outer_hexagon, 'color', self._theme['frame_color'], duration=self._theme['duration'])
        eveui.animate(self.inner_hexagon, 'color', self._theme['background_color'], duration=self._theme['duration'])
        eveui.animate(self.inner_glow_hexagon, 'color', self._theme['inner_glow_color'], duration=self._theme['duration'])
        eveui.animate(self.outer_hex_glow, 'opacity', self._theme['outer_glow_opacity'], duration=self._theme['duration'])
        eveui.animate(self.inner_glow_hexagon, 'opacity', self._theme['inner_glow_opacity'], duration=self._theme['duration'])
        if self._theme['icon_color']:
            eveui.animate(self.icon, 'color', self._theme['icon_color'], duration=self._theme['duration'])
        eveui.animate(self.text, 'color', self._theme['text_color'], duration=self._theme['duration'])

    def ConstructTooltipPanel(self):
        return MilestoneInfoTooltip(reward_name=self._job.rewards[0].name, milestone_state=self._state, omega_locked=self.is_omega_locked)

    def GetMenu(self):
        data = self._job.get_qa_menu()
        return data

    def start_animation(self):
        self._start_omega_pulse()

    @threadutils.threaded
    def stop_animation(self):
        animations.StopAnimation(self.outer_hex_glow, 'opacity')
        self._reset_milestone()


class HomePageMilestone(Milestone):

    def __init__(self, *args, **kwargs):
        super(HomePageMilestone, self).__init__(*args, **kwargs)

    def _on_click(self):
        get_job_board_service().open_browse_page(content_tag_id=ContentTags.feature_daily_goals)

    def _construct_text(self):
        self.text = TextCustom(parent=self.label_container, align=Align.CENTER, text=self._job.rewards[0].amount_text, color=self._theme['text_color'], fontsize=12, shadowOffset=(0, 0))

    def _construct_content(self):
        super(HomePageMilestone, self)._construct_content()
        if self._job.is_omega_restricted:
            texturePath = 'res:/UI/Texture/classes/CloneGrade/Omega_32.png'
        else:
            texturePath = 'res:/UI/Texture/classes/CloneGrade/Alpha_32.png'
        Sprite(parent=self.main_container, align=Align.CENTERBOTTOM, pickState=PickState.OFF, texturePath=texturePath, top=-16, height=32, width=32)


class MilestoneInfoTooltip(TooltipPanel):

    def _get_status_text(self, status):
        status_label = 'UI/DailyGoals/claimed'
        if status in STATE_TO_STATUS_TEXT:
            status_label = STATE_TO_STATUS_TEXT[status]
        status_text = GetByLabel(status_label)
        return GetByLabel('UI/DailyGoals/milestoneStatus', status=status_text)

    def ApplyAttributes(self, attributes):
        super(MilestoneInfoTooltip, self).ApplyAttributes(attributes)
        self.LoadGeneric1ColumnTemplate()
        self.AddLabelMedium(text=attributes.reward_name, color=TextColor.HIGHLIGHT)
        if attributes.omega_locked:
            self.AddLabelMedium(wrapWidth=200, text=GetByMessageID(711523, color=eveColor.OMEGA_YELLOW_HEX))
        else:
            self.AddLabelMedium(text=self._get_status_text(attributes.milestone_state))
