#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\home_page_section.py
import carbonui
import uthread2
from carbonui import Align, TextColor, uiconst
from carbonui.primitives.cardsContainer import CardsContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from carbonui.uiconst import OutputMode, BlendMode
from carbonui.control.button import Button
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from localization import GetByLabel
from metadata import get_content_tag_as_object, ContentTags
import dailygoals.client.goalSignals as daily_goal_signals
from jobboard.client import get_job_board_service, ProviderType
from .reward_track_home import RewardTrackHome
from .home_page_card import DailyGoalHomePageEntry

class DailyGoalsHomePageSection(ContainerAutoSize):
    default_alignMode = Align.TOTOP_NOPUSH
    default_minHeight = 220

    def __init__(self, **kw):
        super(DailyGoalsHomePageSection, self).__init__(**kw)
        self._reconstructing = False
        self.provider = get_job_board_service().get_provider(ProviderType.DAILY_GOALS)
        self.content = ContainerAutoSize(name='content', parent=self, align=Align.TOTOP_NOPUSH, alignMode=Align.TOTOP, minHeight=220)
        self.underlay = Container(name='underlay', parent=self, align=uiconst.TOTOP)
        self.reconstruct_layout()
        self.construct_underlay()
        self._register()

    def Close(self):
        super(DailyGoalsHomePageSection, self).Close()
        self._unregister()

    def construct_underlay(self):
        bottom = Container(name='bottom', parent=self.underlay, align=Align.TOBOTTOM, height=8)
        self.right_underlay_fill = Fill(parent=bottom, color=eveColor.AIR_TURQUOISE, opacity=0.15, align=Align.TORIGHT, width=62, blendMode=BlendMode.ADD)
        StretchSpriteHorizontal(parent=bottom, align=Align.TORIGHT, texturePath='res:/UI/Texture/Shared/panel_cutout.png', color=eveColor.AIR_TURQUOISE, opacity=0.15, width=120, leftEdgeSize=8, rightEdgeSize=8, blendMode=BlendMode.ADD)
        Fill(parent=bottom, color=eveColor.AIR_TURQUOISE, opacity=0.15, blendMode=BlendMode.ADD)
        Sprite(parent=self.underlay, align=Align.TOALL, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/home_page_bg.png', color=eveColor.AIR_TURQUOISE, opacity=0.15, blendMode=BlendMode.ADD)

    def _register(self):
        daily_goal_signals.on_cache_invalidated.connect(self._on_cache_invalidated)
        self.on_size_changed.connect(self._on_size_changed)

    def _unregister(self):
        daily_goal_signals.on_cache_invalidated.disconnect(self._on_cache_invalidated)
        self.on_size_changed.disconnect(self._on_size_changed)

    def _on_cache_invalidated(self):
        self.reconstruct_layout()

    def reconstruct_layout(self):
        if self._reconstructing:
            return
        self.content.Flush()
        self.construct_layout()

    def _on_size_changed(self, width, height):
        if width > 600:
            self.bonus_cont.align = Align.TORIGHT
            self.bonus_cont.padBottom = 0
            self.bonus_cont.SetOrder(0)
            self.goals_cont.cardMaxWidth = 350
            self.right_underlay_fill.width = 62
            self.bonus_cont.padRight = 32
        else:
            self.bonus_cont.align = Align.TOTOP
            self.bonus_cont.padBottom = 16
            self.bonus_cont.SetOrder(-1)
            self.goals_cont.cardMaxWidth = 410
            self.right_underlay_fill.width = width / 2 - 62
            self.bonus_cont.padRight = 0
        self.underlay.height = height

    def construct_layout(self):
        self.construct_error_state()
        self.bonus_cont = ContainerAutoSize(name='bonus_cont', parent=self.content, align=Align.TORIGHT, alignMode=Align.CENTER, padRight=20)
        self.top_cont = ContainerAutoSize(name='top_cont', align=Align.TOTOP, alignMode=Align.TOLEFT, parent=self.content, padding=(32, 32, 0, 0), height=24)
        self.goals_cont = CardsContainer(parent=self.content, align=Align.TOTOP, padding=(16, 32, 16, 32), contentSpacing=(16, 16), cardHeight=56, cardMaxWidth=400)
        self.construct_top_cont()
        self._loading_wheel = LoadingWheel(parent=self, align=Align.CENTER)
        uthread2.start_tasklet(self._construct_layout_thread)

    def _construct_layout_thread(self):
        if self._reconstructing:
            return
        jobs_installed = 0
        try:
            self._reconstructing = True
            if self.provider.has_unclaimed_rewards():
                self._view_button.label = GetByLabel('UI/Generic/ViewRewards')
                self._view_button.variant = carbonui.ButtonVariant.NORMAL
            else:
                self._view_button.label = GetByLabel('UI/Generic/ViewAll')
                self._view_button.variant = carbonui.ButtonVariant.GHOST
            animations.FadeIn(self._loading_wheel, endVal=1.0, duration=0.1)
            animations.FadeOut(self.content, duration=0.1)
            animations.FadeOut(self._error_label, duration=0.1)
            jobs_installed += self.construct_bonus_cont()
            jobs_installed += self.construct_goals_cont()
        except Exception as e:
            animations.FadeIn(self._error_label, endVal=0.1, duration=0.1)
            raise e
        finally:
            self._reconstructing = False
            animations.FadeOut(self._loading_wheel, duration=0.1)
            animations.FadeIn(self.content, endVal=1.0, duration=0.1)
            if jobs_installed == 0:
                animations.FadeIn(self._error_label, endVal=1, duration=0.1)

    def construct_top_cont(self):
        Sprite(name='air_logo', parent=self.top_cont, align=Align.CENTERLEFT, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/air_logo.png', pos=(0, 0, 44, 18), color=eveColor.AIR_TURQUOISE, outputMode=OutputMode.COLOR_AND_GLOW, glowBrightness=0.3)
        carbonui.TextHeader(parent=self.top_cont, align=Align.TOLEFT, left=56, color=TextColor.HIGHLIGHT, text=get_content_tag_as_object(ContentTags.feature_daily_goals).title)
        self._view_button = Button(parent=self.top_cont, align=Align.TOLEFT, variant=carbonui.ButtonVariant.GHOST, density=carbonui.Density.COMPACT, label=GetByLabel('UI/Generic/ViewAll'), padLeft=12, func=self._open_daily_goals)

    def construct_error_state(self):
        self._error_label = carbonui.TextBody(parent=self.content, name='error_label', align=Align.CENTER, text=GetByLabel('UI/DailyGoals/NoDailyGoalsFound'))

    def construct_bonus_cont(self):
        bonus_job = self.provider.get_bonus_job_of_the_day()
        if not bonus_job:
            return 0
        RewardTrackHome(parent=self.bonus_cont, daily_job=bonus_job, alpha_jobs=self.provider.get_alpha_milestones_of_the_month(), omega_jobs=self.provider.get_omega_milestones_of_the_month())
        return 1

    def construct_goals_cont(self):
        daily_jobs = self.provider.get_jobs_of_the_day()
        sorted_jobs = sorted(daily_jobs, key=lambda x: x.sort_value)
        for job in sorted_jobs:
            DailyGoalHomePageEntry(parent=self.goals_cont, job=job)

        return len(daily_jobs)

    def _open_daily_goals(self, *args, **kwargs):
        get_job_board_service().open_browse_page(content_tag_id=ContentTags.feature_daily_goals)
