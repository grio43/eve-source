#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\page.py
import evetypes
from carbonui import Align, TextBody, TextColor, TextHeader, uiconst, TextDetail
from carbonui.primitives.cardsContainer import CardsContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from goals.common.goalConst import ContributionMethodTypes, GoalParameterTypes
from dailygoals.client.const import DailyGoalCategory
from jobboard.client.features.daily_goals.aura import AuraDailyGoalPanel
from jobboard.client.ui.pages.details_page import DetailsSection, JobPage
from jobboard.client.ui.parameter_container import ParameterContainer
from jobboard.client.ui.time_remaining import TimeRemaining
from jobboard.client.ui.util import get_career_path_bg
from jobboard.client.ui.progress_bar import ProgressGauge
from localization import GetByLabel
from localization.formatters import FormatNumeric

class DailyGoalPage(JobPage):
    FLAIR_BG_SIZE = 600
    FLAIR_BG_OFFSET = 35

    def __init__(self, job, show_related = True, **kwargs):
        self._progress_gauge = None
        self._progress_icon = None
        self._progress_value_label = None
        self._target_value_label = None
        self._progress_ratio_label = None
        self._progress_description_label = None
        super(DailyGoalPage, self).__init__(job, show_related, **kwargs)

    @property
    def _header_bg_color(self):
        bg_color = list(eveColor.BLACK)
        bg_color[3] = 0.1
        return bg_color

    @property
    def _header_overlay_color(self):
        bg_color = list(eveColor.SMOKE_BLUE)
        bg_color[3] = 0.2
        return bg_color

    def _construct_top_container(self, parent):
        top_container = Container(name='top_container', parent=parent, align=Align.TOTOP, height=30)
        return top_container

    def _construct_career_tag(self, parent):
        TextHeader(name='title_label', parent=parent, align=Align.TOPLEFT, text=GetByLabel('UI/DailyGoals/DetailPageHeader'), padLeft=46, color=TextColor.HIGHLIGHT, padTop=4)
        Sprite(name='title_icon_glow', parent=parent, align=Align.CENTERLEFT, texturePath='res:/UI/Texture/classes/SkillPlan/airLogo.png', color=eveColor.AIR_TURQUOISE, outputMode=uiconst.OUTPUT_GLOW, glowBrightness=0.5, height=14, width=36)
        Sprite(name='title_icon', parent=parent, align=Align.CENTERLEFT, texturePath='res:/UI/Texture/classes/SkillPlan/airLogo.png', height=14, width=36)

    def _construct_bg_flair(self, parent):
        self._bg_flair = Sprite(name='bg_flair', parent=parent, align=Align.TOPLEFT, texturePath=get_career_path_bg(self.job.career_id), color=eveColor.SMOKE_BLUE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0, opacity=1.0, pos=self._get_flair_bg_pos)

    @property
    def _get_flair_bg_pos(self):
        x = -self.FLAIR_BG_SIZE / 2 + self.FLAIR_BG_OFFSET
        y = -self.FLAIR_BG_SIZE / 2 + self.FLAIR_BG_OFFSET
        w = self.FLAIR_BG_SIZE
        h = self.FLAIR_BG_SIZE
        return (x,
         y,
         w,
         h)

    def _construct_header_caption(self, parent):
        TextHeader(name='header_caption', parent=parent, align=Align.TOTOP, text=self.job.title, bold=True, padTop=24, padBottom=16)

    def _construct_body(self, parent_container):
        self._construct_time_remaining(parent_container)
        self._construct_progress(parent_container)
        self._construct_operational_intel(parent_container)
        self._construct_description(parent_container)
        self._construct_aura_panel(parent_container)

    def _construct_time_remaining(self, parent):
        if self.job.is_expired or self.job.is_completed:
            return
        TimeRemaining(name='time_remaining', parent=parent, align=Align.TOTOP, job=self.job, padBottom=24)

    def _construct_progress(self, parent):
        progress_container = ContainerAutoSize(name='progress_container', parent=parent, align=Align.TOTOP, padBottom=24)
        cards_container = CardsContainer(name='cards_container', parent=progress_container, align=Align.TOTOP, autoHeight=True, cardHeight=112, contentSpacing=(16, 24), cardMaxWidth=550, maxColumnCount=2)
        total_progress_container = ContainerAutoSize(name='total_progress_container', parent=cards_container, align=Align.TOLEFT)
        reward_summary_container = ContainerAutoSize(name='reward_summary_container', parent=cards_container, align=Align.TOLEFT)
        self._construct_total_progress(parent=total_progress_container)
        self._construct_reward_summary(parent=reward_summary_container)
        progress_container.height = total_progress_container.height

    def _construct_total_progress(self, parent):
        details_section = DetailsSection(name='total_progress_section', parent=parent, title=GetByLabel('UI/Corporations/Goals/Progress'), padding=0)
        content_container = ContainerAutoSize(name='content_container', parent=details_section.content_container, align=Align.TOTOP, alignMode=Align.TOPLEFT, padTop=10)
        self._progress_gauge = ProgressGauge(parent=content_container, align=Align.TOPLEFT, radius=40, show_label=False, value=self.job.progress_percentage)
        self._progress_icon = Sprite(parent=self._progress_gauge, align=Align.CENTER, pos=(0, 0, 16, 16), color=TextColor.SECONDARY)
        Sprite(name='progress_icon', parent=self._progress_gauge, align=Align.CENTER, color=TextColor.SECONDARY, icon=self.job.contribution_method.icon, pos=(0, 0, 16, 16))
        text_container = ContainerAutoSize(name='text_container', parent=content_container, align=Align.VERTICALLY_CENTERED, padLeft=98)
        self._progress_value_label = TextHeader(name='progress_value_label', parent=text_container, align=Align.TOTOP, text='-', bold=True, padBottom=1)
        self._target_value_label = TextDetail(name='target_value_label', parent=text_container, align=Align.TOTOP, text='-', padBottom=4)
        self._progress_ratio_label = TextDetail(name='progress_ratio_label', parent=text_container, align=Align.TOTOP, text='-', padBottom=1)

    def _construct_reward_summary(self, parent):
        details_section = DetailsSection(name='reward_summary_section', parent=parent, title=GetByLabel('UI/DailyGoals/DetailsPageRewardsTitle'), padding=0)
        content_container = ContainerAutoSize(name='content_container', parent=details_section.content_container, align=Align.TOTOP, padTop=10)
        for reward in self.job.rewards:
            ParameterContainer(parent=content_container, align=Align.TOTOP, text=reward.amount_text, icon=reward.icon, displayTextBackground=False, padBottom=8)

    def _construct_operational_intel(self, parent):
        details_section = DetailsSection(name='operational_intel_section', parent=parent, title=GetByLabel('UI/DailyGoals/DetailsPageOperationalIntelTitle'), padBottom=24)
        contribution_container = CardsContainer(name='contribution_container', parent=details_section.content_container, align=Align.TOTOP, autoHeight=False, contentSpacing=(16, 8), cardHeight=55, maxColumnCount=4, allow_stretch=True, padBottom=8)
        contribution_method = self.job.contribution_method
        ParameterContainer(name='contribution_method', parent=contribution_container, caption=GetByLabel('UI/Corporations/Goals/ContributionMethod'), hint=contribution_method.info, text=contribution_method.title, icon=contribution_method.icon)
        ore_container = CardsContainer(name='ore_container', parent=details_section.content_container, align=Align.TOTOP, autoHeight=False, contentSpacing=(16, 8), cardHeight=55, maxColumnCount=4, allow_stretch=False, padBottom=8)
        remaining_params_container = CardsContainer(name='remaining_params_container', parent=details_section.content_container, align=Align.TOTOP, autoHeight=False, contentSpacing=(16, 8), cardHeight=55, maxColumnCount=4, allow_stretch=True)
        if contribution_method.parameters:
            for param in contribution_method.parameters:
                if contribution_method.method_id == ContributionMethodTypes.MANUFACTURE_ITEM and param.parameter_id == GoalParameterTypes.ON_BEHALF_OF:
                    continue
                ParameterContainer(parent=remaining_params_container, caption=param.title, text=param.get_value_text(), icon=param.icon, get_menu=param.get_menu)

    def _construct_description(self, parent_container):
        if self.job.description:
            details_section = DetailsSection(name='description_section', parent=parent_container, title=GetByLabel('UI/DailyGoals/DetailsPageDescriptionTitle'), padBottom=24)
            TextBody(name='description_label', parent=details_section.content_container, align=Align.TOTOP, text=self.job.description)

    def _construct_aura_panel(self, parent):
        if self.job.category != DailyGoalCategory.CATEGORY_DAILY:
            return
        AuraDailyGoalPanel(name='aura_panel', parent=parent, align=Align.TOTOP, bgColor=eveColor.Color(eveColor.AURA_PURPLE).SetBrightness(1.0).SetOpacity(0.1).GetRGBA(), job=self.job)

    def _update(self):
        self._update_state(animate=True)

    def _update_state(self, animate = False):
        super(DailyGoalPage, self)._update_state()
        self._update_gauge(animate)
        self._progress_icon.SetTexturePath(self.job.contribution_method.icon)
        self._progress_value_label.text = FormatNumeric(self.job.current_progress, useGrouping=True)
        self._target_value_label.text = u'/ {}'.format(self.job.desired_progress)
        self._progress_ratio_label.text = u'{ratio:.0f}% <color={descColor}>{desc}</color>'.format(ratio=self.job.progress_percentage * 100.0, desc=self.job.contribution_method.target_value_description, descColor=TextColor.SECONDARY)

    def _update_gauge(self, animate = True):
        self._progress_gauge.set_state_info(self.job.get_state_info())
        self._progress_gauge.set_value(self.job.progress_percentage, animate=animate)
