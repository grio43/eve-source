#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\feature_page.py
import logging
import eveui
import math
import gametime
import uthread2
import threadutils
import localization
from carbonui import Align, TextBody, TextColor, TextHeader, TextHeadline, uiconst
from carbonui.primitives.cardsContainer import CardsContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.message import ShowQuickMessage
from gametime import GetWallclockTimeNow, MIN
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShortWritten
from metadata import get_content_tag_as_object
from jobboard.client import job_board_signals
from jobboard.client.provider_type import ProviderType
from jobboard.client.features.daily_goals.reward_track_feature_page import RewardTrackFeaturePage
from jobboard.client.ui.time_remaining import TimeRemaining, _get_time_color_time
from eve.client.script.ui.control.infoIcon import InfoGlyphIcon
from jobboard.client.ui.card import JobCard
from jobboard.client.ui.const import CARD_MAX_WIDTH
from jobboard.client.ui.pages.base_page import BasePage
logger = logging.getLogger(__name__)

class DailyGoalsFeaturePage(BasePage):
    CARDS_GRADIENT_COLOR = eveColor.AIR_TURQUOISE
    CARDS_GRADIENT_OPACITY = 0.15
    CONTENT_PADDING_OFFSET = 16
    MIN_SIZE_TO_SHOW_STRETCH_SPRITES = 1000
    __notifyevents__ = ['OnSubscriptionChanged']

    def __init__(self, content_tag_id, **kwargs):
        self._content_tag = get_content_tag_as_object(content_tag_id)
        self._daily_goals_of_the_day_job_cards = {}
        self._reconstructing_goals_of_the_day = False
        self._reconstructing_time_remaining_widget = False
        self._reconstructing_daily_goal_time_remaining = False
        self._reconstructing_reward_track = False
        self._reward_track = None
        self.daily_cards_container = None
        self.left_container = None
        self.right_container = None
        super(DailyGoalsFeaturePage, self).__init__(**kwargs)

    @threadutils.throttled(0.2)
    def update_all(self):
        if self.destroyed:
            return
        uthread2.start_tasklet(self.reconstruct_goals_of_the_day)
        uthread2.start_tasklet(self.reconstruct_time_remaining_widget)
        uthread2.start_tasklet(self.reconstruct_daily_goals_time_remaining_widget)
        uthread2.start_tasklet(self.reconstruct_reward_track)

    def _init_services(self):
        super(DailyGoalsFeaturePage, self)._init_services()
        self._provider = self._service.get_provider(ProviderType.DAILY_GOALS)

    def _get_jobs(self):
        return self._service.get_jobs_with_unclaimed_rewards(ProviderType.DAILY_GOALS)

    def OnSubscriptionChanged(self):
        uthread2.start_tasklet(self.reconstruct_reward_track)

    @property
    def primary_content_tag_id(self):
        return self._content_tag.id

    def _register(self):
        job_board_signals.on_job_added.connect(self._on_job_added)
        job_board_signals.on_job_removed.connect(self._on_job_removed)
        sm.RegisterNotify(self)
        super(DailyGoalsFeaturePage, self)._register()

    def _unregister(self):
        job_board_signals.on_job_added.disconnect(self._on_job_added)
        job_board_signals.on_job_removed.disconnect(self._on_job_removed)
        sm.UnregisterNotify(self)
        super(DailyGoalsFeaturePage, self)._unregister()

    @property
    def _page_title(self):
        return self._content_tag.title

    @property
    def _page_description(self):
        return self._content_tag.description

    @property
    def _page_icon(self):
        return 'res:/UI/Texture/classes/SkillPlan/airLogo.png'

    def _is_relevant_job(self, job):
        return job.provider_id == ProviderType.DAILY_GOALS and not job.is_expired

    @eveui.skip_if_destroyed
    def _on_job_added(self, job):
        if self._is_relevant_job(job):
            self.update_all()

    @eveui.skip_if_destroyed
    def _on_job_removed(self, job):
        if self._is_relevant_job(job):
            self.update_all()

    def _construct_base_containers(self):
        super(DailyGoalsFeaturePage, self)._construct_base_containers()
        self._no_jobs_container = ContainerAutoSize(name='no_jobs_container', parent=self._content_container, align=Align.TOTOP, display=False)
        TextHeader(name='no_jobs_container_header', parent=self._no_jobs_container, align=Align.CENTER, text=GetByLabel('UI/DailyGoals/NoDailyGoalsFound'))

    def _claim_all(self):
        jobs = self._get_jobs()
        for job in jobs:
            if not job.has_claimable_rewards:
                continue
            job.claim_rewards()

    def _construct_header(self):
        offset = self.CONTENT_PADDING_OFFSET
        self.header = ContainerAutoSize(parent=self._header_container, align=Align.TOTOP, padding=(offset,
         16,
         offset,
         8))
        self.title_container = ContainerAutoSize(parent=self.header, align=Align.TOTOP, alignMode=Align.TOPLEFT)
        icon = self._page_icon
        headline = TextHeadline(parent=self.title_container, align=Align.TOPLEFT, text=GetByLabel('UI/DailyGoals/MonthlyTrack'), padLeft=56 if icon else 0, color=TextColor.HIGHLIGHT)
        InfoGlyphIcon(parent=self.title_container, align=Align.CENTERLEFT, left=headline.width + 8, hint=localization.GetByLabel('UI/DailyGoals/RewardTrackInfo'))
        if icon:
            Sprite(parent=self.title_container, align=Align.CENTERLEFT, texturePath=icon, color=eveColor.AIR_TURQUOISE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.5, height=16, width=40)
        description = self._page_description
        if description:
            subtitle_container = ContainerAutoSize(parent=self.header, align=Align.TOTOP, padTop=8)
            TextBody(parent=subtitle_container, align=Align.TOPLEFT, text=description, maxWidth=400)
        self._time_remaining_cont = Container(name='time_remaining_cont', parent=self.title_container, align=Align.TOALL)

    def reconstruct_time_remaining_widget(self):
        if self._reconstructing_time_remaining_widget:
            return
        self._reconstructing_time_remaining_widget = True
        self._time_remaining_cont.Flush()
        lowest_expiration_job = None
        for job in self._provider.get_alpha_milestones_of_the_month():
            if job.is_expired:
                continue
            if lowest_expiration_job is None or job.expiration_time < lowest_expiration_job.expiration_time:
                lowest_expiration_job = job

        if lowest_expiration_job is not None:
            TimeRemaining(parent=self._time_remaining_cont, align=Align.CENTERRIGHT, job=lowest_expiration_job, get_text=self._get_montly_track_time_remaining)
        self._reconstructing_time_remaining_widget = False

    def reconstruct_daily_goals_time_remaining_widget(self):
        if self._reconstructing_daily_goal_time_remaining:
            return
        self._reconstructing_daily_goal_time_remaining = True
        self.daily_goal_time_remaining_container.Flush()
        first_daily_goal_job = None
        for job in self._provider.get_jobs_of_the_day():
            if job.is_expired:
                continue
            first_daily_goal_job = job

        if first_daily_goal_job is not None:
            TimeRemaining(parent=self.daily_goal_time_remaining_container, align=Align.CENTERRIGHT, job=first_daily_goal_job, get_text=self._get_daily_goal_time_remaining)
        self._reconstructing_daily_goal_time_remaining = False

    def _get_daily_goal_time_remaining(self, job):
        time_now = gametime.GetWallclockTime()
        time_remaining = job.expiration_time - time_now
        if time_remaining <= 0:
            return localization.GetByLabel('UI/Generic/Expired')
        else:
            return localization.GetByLabel('UI/DailyGoals/DailyGoalsExpireIn', color=_get_time_color_time(job.expiration_time), remaining=time_remaining)

    def _get_montly_track_time_remaining(self, job):
        time_now = gametime.GetWallclockTime()
        time_remaining = job.expiration_time - time_now
        if time_remaining <= 0:
            return GetByLabel('UI/Generic/Expired')
        else:
            return GetByLabel('UI/DailyGoals/MonthlyTrackExpiresIn', remaining=time_remaining)

    def _construct_content(self):
        self._construct_reward_track()
        self._construct_daily_goal_header()
        self.construct_top_container()
        self.update_all()

    def _show_container_sprites(self, width = None):
        if width is None:
            _, _, width, _ = self.displayRect
        return width > self.MIN_SIZE_TO_SHOW_STRETCH_SPRITES

    def _construct_daily_goal_header(self):
        offset = self.CONTENT_PADDING_OFFSET
        headerContainer = Container(name='daily_goals_header_cont', parent=self._content_container, align=Align.TOTOP, height=30, padding=(offset,
         4,
         offset,
         16))
        TextHeadline(parent=headerContainer, align=Align.TOLEFT, text=self._page_title, color=TextColor.HIGHLIGHT)
        self.daily_goal_time_remaining_container = Container(name='daily_goal_time_remaining_cont', parent=headerContainer, align=Align.TOALL, clipChildren=True)

    def _construct_reward_track(self):
        show_container_sprites = self._show_container_sprites()
        reward_track_section = ContainerAutoSize(name='reward_track_section', parent=self._content_container, align=Align.TOTOP, alignMode=Align.TOTOP, height=275)
        self.left_container = Container(name='left_container', parent=reward_track_section, align=Align.TOLEFT_PROP, height=89, width=0.17, display=show_container_sprites)
        StretchSpriteHorizontal(name='left_stretch_sprite', parent=self.left_container, align=Align.TOTOP, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/bonus_reward_side.png', height=89, rotation=math.radians(180), leftEdgeSize=57, rightEdgeSize=40, top=78)
        self.right_container = Container(name='right_container', parent=reward_track_section, align=Align.TORIGHT_PROP, height=89, width=0.17, display=show_container_sprites)
        StretchSpriteHorizontal(name='right_stretch_sprite', parent=self.right_container, align=Align.TOTOP, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/bonus_reward_side.png', height=89, leftEdgeSize=40, rightEdgeSize=57, top=78)
        self._reward_track = RewardTrackFeaturePage(name='reward_track_feature_page', parent=reward_track_section, align=Align.TOTOP, height=275, daily_bonus_job=self._provider.get_bonus_job_of_the_day(), alpha_jobs=self._provider.get_alpha_milestones_of_the_month(), omega_jobs=self._provider.get_omega_milestones_of_the_month(), claim_all_func=self._claim_all)

    def _OnSizeChange_NoBlock(self, width, _):
        show_sides = self._show_container_sprites(width)
        if self.left_container:
            self.left_container.display = show_sides
        if self.right_container:
            self.right_container.display = show_sides

    def construct_top_container(self):
        self.top_container = ContainerAutoSize(name='top_container', parent=self._content_container, align=Align.TOTOP)
        daily_cards_parent = ContainerAutoSize(name='daily_cards_parent', parent=self.top_container, align=Align.TOTOP)
        self.daily_cards_container = CardsContainer(parent=daily_cards_parent, name='daily_cards_container', align=Align.TOTOP, cardHeight=JobCard.default_height, cardMaxWidth=CARD_MAX_WIDTH, contentSpacing=(16, 16), padding=(self.CONTENT_PADDING_OFFSET,
         0,
         self.CONTENT_PADDING_OFFSET,
         0))
        GradientSprite(name='gradient_sprite', bgParent=daily_cards_parent, rgbData=((0.0, eveColor.BLACK[:3]), (1.0, self.CARDS_GRADIENT_COLOR[:3])), alphaData=((0.0, 0.0), (self.CARDS_GRADIENT_OPACITY, self.CARDS_GRADIENT_OPACITY)), rotation=-(math.pi / 2))
        self.construct_evermore_container()
        self.construct_cutout_container()

    def construct_evermore_container(self):
        evermore_container = ContainerAutoSize(name='evermore_container', parent=self.top_container, align=Align.TOTOP)
        Fill(bgParent=evermore_container, color=self.CARDS_GRADIENT_COLOR, opacity=self.CARDS_GRADIENT_OPACITY)
        content = ContainerAutoSize(name='content', parent=evermore_container, align=uiconst.TOTOP, padding=(16, 16, 16, 8))
        Sprite(parent=content, align=Align.CENTERRIGHT, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/evermore_brand.png', width=87, height=10)
        TextBody(parent=content, align=Align.CENTERRIGHT, text=GetByLabel('UI/DailyGoals/SponsoredBy'), color=TextColor.SECONDARY, left=93)

    def construct_cutout_container(self):
        cutout_container = Container(name='cutout_container', parent=self.top_container, align=Align.TOTOP, height=8)
        Fill(parent=cutout_container, align=Align.TOLEFT, color=self.CARDS_GRADIENT_COLOR, opacity=0.15, width=self.CONTENT_PADDING_OFFSET)
        StretchSpriteHorizontal(parent=cutout_container, align=Align.TOLEFT, texturePath='res:/UI/Texture/Shared/panel_cutout.png', color=self.CARDS_GRADIENT_COLOR, opacity=self.CARDS_GRADIENT_OPACITY, width=120, leftEdgeSize=8, rightEdgeSize=8)
        Fill(parent=cutout_container, align=Align.TOALL, color=self.CARDS_GRADIENT_COLOR, opacity=self.CARDS_GRADIENT_OPACITY)

    def reconstruct_goals_of_the_day(self):
        if self._reconstructing_goals_of_the_day:
            return
        self._reconstructing_goals_of_the_day = True
        if self.daily_cards_container:
            self.daily_cards_container.Flush()
        self._daily_goals_of_the_day_job_cards = {}
        try:
            jobs = self._provider.get_jobs_of_the_day()
        except Exception as e:
            logger.exception(e)
            ShowQuickMessage(GetByLabel('UI/Corporations/Goals/FailedToConnect'))
            jobs = []

        if jobs:
            self.top_container.display = True
            self._no_jobs_container.display = False
            sorted_jobs = sorted(jobs, key=lambda x: x.sort_value)
            for job in sorted_jobs:
                self._construct_job_card(job)

        else:
            self.top_container.display = False
            self._no_jobs_container.display = True
        self._reconstructing_goals_of_the_day = False

    def reconstruct_reward_track(self):
        if self._reconstructing_reward_track or not self._reward_track:
            return
        self._reconstructing_reward_track = True
        self._reward_track.reconstruct(self._provider.get_bonus_job_of_the_day())
        self._reconstructing_reward_track = False

    def _construct_job_card(self, job):
        if not self.daily_cards_container:
            return
        if self.daily_cards_container.destroyed:
            return
        if job.job_id in self._daily_goals_of_the_day_job_cards:
            return
        card = job.construct_entry(list_view=False, parent=self.daily_cards_container, show_feature=False, show_remaining_time=False)
        self._daily_goals_of_the_day_job_cards[job.job_id] = card
