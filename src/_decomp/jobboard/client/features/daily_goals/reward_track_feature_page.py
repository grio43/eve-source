#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\reward_track_feature_page.py
import logging
import uthread2
import threadutils
from localization import GetByLabel
from carbonui import Align, PickState, uiconst
from carbonui.uicore import uicore
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.cloneGrade import ORIGIN_OPPORTUNITIES
from eve.client.script.ui.shared.cloneGrade.upgradeButton import UpgradeIconButton
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.scrollContainer import ScrollContainer
from jobboard.client import get_job_board_service, ProviderType, job_board_signals
from jobboard.client.features.daily_goals.milestones import Milestone
from jobboard.client.features.daily_goals.milestones import MilestoneState
from jobboard.client.features.daily_goals.bonus_rewards import BonusGoalContainer
from carbon.client.script.environment.AudioUtil import PlaySound
from .reward_track_progress import FeaturePageProgressBar
logger = logging.getLogger(__name__)

class RewardTrackFeaturePage(ScrollContainer):
    default_state = uiconst.UI_NORMAL

    def __init__(self, daily_bonus_job, alpha_jobs, omega_jobs, claim_all_func, *args, **kwargs):
        super(RewardTrackFeaturePage, self).__init__(*args, **kwargs)
        self._provider = get_job_board_service().get_provider(ProviderType.DAILY_GOALS)
        self._progress = self._provider.get_reward_track_progress()
        self._daily_bonus_job = daily_bonus_job
        self._alpha_jobs = alpha_jobs
        self._omega_jobs = omega_jobs
        self._is_playing = False
        self.track_container = None
        self._progress_bar = None
        self._bonus_goal_container = None
        self._upgrade_button = None
        self._milestones = []
        self._omega_restricted_milestones = []
        self._claim_all_func = claim_all_func
        self._is_claiming = False
        self._layout()
        self._daily_bonus_job.on_job_updated.connect(self._on_bonus_job_updated)
        self._provider.on_reward_track_progressed.connect(self._on_reward_track_progressed)
        job_board_signals.on_job_state_changed.connect(self._on_job_state_changed)

    def Close(self, *args):
        super(RewardTrackFeaturePage, self).Close(*args)
        self._daily_bonus_job.on_job_updated.disconnect(self._on_bonus_job_updated)
        self._provider.on_reward_track_progressed.disconnect(self._on_reward_track_progressed)
        job_board_signals.on_job_state_changed.disconnect(self._on_job_state_changed)
        if self._upgrade_button:
            self._upgrade_button.on_mouse_enter.disconnect(self._on_mouse_enter_milestone)
            self._upgrade_button.on_mouse_exit.disconnect(self._on_mouse_exit_milestone)
        for milestone in self._omega_restricted_milestones:
            milestone.on_mouse_exit.disconnect(self._on_mouse_exit_milestone)
            milestone.on_mouse_enter.disconnect(self._on_mouse_enter_milestone)

    def _on_bonus_job_updated(self):
        if self._daily_bonus_job.current_progress == 1:
            self._on_reward_track_progressed()

    def _on_reward_track_progressed(self):
        if not self._progress_bar:
            return
        self._progress = self._provider.get_reward_track_progress()
        self._progress_bar.set_progress(self._progress, self._daily_bonus_job.current_progress)
        for item in self._milestones:
            milestone = item['milestone']
            milestone.update_state()

    def _on_job_state_changed(self, job):
        if job.provider_id != self._provider.PROVIDER_ID:
            return
        if self._bonus_goal_container:
            self._bonus_goal_container.update_claim_all_button(self._provider.has_claimable_rewards())

    def reconstruct(self, job):
        if self._daily_bonus_job:
            self._daily_bonus_job.on_job_updated.disconnect(self._on_bonus_job_updated)
        self._daily_bonus_job = job
        self._daily_bonus_job.on_job_updated.connect(self._on_bonus_job_updated)
        self.Flush()
        self._layout()
        self._on_reward_track_progressed()

    def _layout(self):
        if not self._alpha_jobs or not self._omega_jobs:
            logger.warning('Unable to display reward track due to missing data')
            self.display = False
            return
        self._main_container = Container(parent=self, align=Align.CENTERTOP, height=275, width=650)
        self._construct_content()
        self.display = self._daily_bonus_job is not None

    def _construct_bonus_goal(self):
        self._bonus_goal_container = BonusGoalContainer(name='bonus_goal', parent=self.track_container, align=Align.TOLEFT, job=self._daily_bonus_job, has_rewards=self._provider.has_claimable_rewards(), claim_all_func=self._claim_all_daily_goals)

    def _is_omega(self):
        return sm.GetService('cloneGradeSvc').IsOmega()

    def _add_omega_alpha_icons(self):
        container = Container(parent=self.track_container, name='alpha_omega_container', align=Align.TOLEFT, width=100, padLeft=-90)
        button_container = Container(parent=container, name='upgrade_button_container', align=Align.TOTOP, padTop=8, height=32, width=100, display=not self._is_omega())
        self._upgrade_button = UpgradeIconButton(parent=button_container, align=Align.TOLEFT, height=32, text=GetByLabel('UI/CloneState/Upgrade'), glowBrightness=0.5, onClick=self._on_omega_button, animate=True)
        self._upgrade_button.on_mouse_enter.connect(self._on_mouse_enter_milestone)
        self._upgrade_button.on_mouse_exit.connect(self._on_mouse_exit_milestone)
        omega_container = Container(parent=container, name='omega_container', align=Align.TOTOP_NOPUSH, height=32, padTop=5, display=self._is_omega())
        Sprite(name='omega_small_icon', parent=omega_container, align=Align.TOLEFT, texturePath='res:/UI/Texture/classes/CloneGrade/Omega_32.png', pickState=PickState.OFF, height=32, width=32)
        alpha_container = Container(parent=container, name='alpha_container', align=Align.TOBOTTOM_NOPUSH, height=32, padBottom=6)
        Sprite(name='alpha_icon', parent=alpha_container, align=Align.TOLEFT, texturePath='res:/UI/Texture/classes/CloneGrade/Alpha_32.png', pickState=PickState.OFF, height=32, width=32)

    def _construct_progress_bar(self):
        progress_container = Container(name='progress_container', parent=self.track_container, align=Align.TOLEFT, padLeft=-84, padBottom=2, width=447)
        self._construct_rewards(progress_container)
        Sprite(name='omega_track_line', parent=progress_container, align=Align.TOTOP, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/track_line.png', color=eveColor.Color(eveColor.OMEGA_YELLOW).SetOpacity(0.3).GetRGBA(), pickState=PickState.OFF, padTop=9, height=49)
        self._progress_bar = FeaturePageProgressBar(name='progress_bar', parent=progress_container, align=Align.CENTERLEFT, progress=self._progress, padLeft=31)
        Sprite(name='alpha_track_line', parent=progress_container, align=Align.TOTOP, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/track_line.png', color=eveColor.Color(eveColor.WHITE).SetOpacity(0.2).GetRGBA(), pickState=PickState.OFF, padTop=156, height=-49)

    def _construct_rewards(self, progress_container):
        rewards_container = ContainerAutoSize(parent=progress_container, align=Align.TOTOP_NOPUSH, height=225, padTop=0, padLeft=77)
        for index in range(0, 4):
            container = Container(parent=rewards_container, align=Align.TOLEFT, width=94, height=100)
            omega_milestone = Milestone(parent=container, align=Align.TOTOP, job=self._omega_jobs[index], is_final=index == 3, is_omega_restricted=not self._is_omega() and self._omega_jobs[index].are_rewards_omega_restricted)
            alpha_milestone = Milestone(parent=container, align=Align.TOBOTTOM, job=self._alpha_jobs[index], is_final=index == 3)
            self._milestones.append({'job': self._omega_jobs[index],
             'milestone': omega_milestone})
            self._milestones.append({'job': self._alpha_jobs[index],
             'milestone': alpha_milestone})
            if omega_milestone.is_omega_locked:
                self._omega_restricted_milestones.append(omega_milestone)
                omega_milestone.on_mouse_enter.connect(self._on_mouse_enter_milestone)
                omega_milestone.on_mouse_exit.connect(self._on_mouse_exit_milestone)

    def _on_mouse_enter_milestone(self):
        if self._is_omega():
            return
        self._upgrade_button.stop_pulse_glow()
        for milestone in self._omega_restricted_milestones:
            milestone.stop_animation()

    def _on_mouse_exit_milestone(self):
        if self._is_omega():
            return
        self._upgrade_button.start_pulse_glow()
        for milestone in self._omega_restricted_milestones:
            milestone.start_animation()

    def _construct_content(self):
        content_container = Container(name='content_container', parent=self._main_container, align=Align.TOTOP, height=250)
        self.track_container = ContainerAutoSize(name='track_content', parent=content_container, align=Align.CENTER, height=225)
        self._construct_bonus_goal()
        self._add_omega_alpha_icons()
        self._construct_progress_bar()

    def _set_progress(self, value):
        self._progress = int(value)
        self._progress_bar.set_progress(self._progress, self._daily_bonus_job.current_progress)

    def _on_omega_button(self, *args, **kwargs):
        uicore.cmd.OpenCloneUpgradeWindow(ORIGIN_OPPORTUNITIES)

    def _can_claim(self, job):
        if not job.has_claimable_rewards:
            return False
        return True

    @threadutils.threaded
    def _claim_all_daily_goals(self):
        if self._is_claiming:
            return
        PlaySound('monthly_progress_claim_all_button_play')
        self._start_claim_animation()
        self._claim_all_func()
        self._is_claiming = False

    def _start_claim_animation(self):
        if self._is_playing:
            return
        self._is_playing = True
        self._bonus_goal_container.start_claim_all_animation()
        for item in self._milestones:
            job = item['job']
            milestone = item['milestone']
            if self._can_claim(job):
                if milestone.is_final:
                    PlaySound('monthly_progress_hexagon_highlight_final_play')
                else:
                    PlaySound('monthly_progress_hexagon_highlight_play')
                milestone.set_state(MilestoneState.CLAIMING)

        uthread2.Sleep(2)
        for item in self._milestones:
            job = item['job']
            milestone = item['milestone']
            if self._can_claim(job):
                milestone.set_state(MilestoneState.CLAIMED)

        self._bonus_goal_container.start_claim_all_cleanup_animation()
        self._is_playing = False

    def GetMenu(self):
        from jobboard.client.qa_tools import is_qa
        from carbonui.control.contextMenu.menuEntryData import MenuEntryDataSlider
        if is_qa():
            from carbonui.services.setting import SessionSettingNumeric
            setting = SessionSettingNumeric(default_value=0, min_value=0, max_value=12)
            setting.on_change.connect(self._set_progress)
            return [('QA', [MenuEntryDataSlider('Set Progress', setting, min_label=str(setting.min_value), max_label=str(setting.max_value)), ('Start claim all animation', lambda : self._start_claim_animation())])]
