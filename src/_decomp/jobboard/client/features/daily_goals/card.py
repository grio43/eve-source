#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\card.py
import eveicon
import eveui
import threadutils
from carbonui import Align, Density, PickState, uiconst
from carbonui import TextBody, TextColor, TextDetail, TextHeader
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.gauge import Gauge
from jobboard.client.features.daily_goals.claim_button import DailyGoalClaimButton
from jobboard.client.features.daily_goals.completion_convenience.ui.button import CompletionConvenienceButton
from jobboard.client.features.daily_goals.completion_convenience.ui.icon_button import CompletionConvenienceIcon
from jobboard.client.features.daily_goals.completion_convenience.util import can_pay_for_completion
from jobboard.client.ui.card import JobCard
from jobboard.client.ui.list_entry import JobListEntry
from jobboard.client.ui.reward_list_entry import JobRewardListEntry
from jobboard.client.ui.tag_icon import TagIcon
from jobboard.client.ui.time_remaining import TimeRemainingIcon
from jobboard.client.ui.util import get_career_path_bg
from localization import GetByLabel
from dailygoals.client import goalSignals as dailyGoalSignals

class DailyGoalCard(JobCard):
    FLAIR_BG_PATTERN_SIZE = 450
    FLAIR_BG_OFFSET = 40
    FLAIR_TAG_SIZE = 64
    FLAIR_ICON_SIZE = 58
    FLAIR_ICON_COLOR = TextColor.HIGHLIGHT

    def __init__(self, controller, show_feature = False, *args, **kwargs):
        self._top_title = None
        self._gauge = None
        self._tag_claimed = None
        self._tag_icon = None
        self._claim_button = None
        self._show_remaining_time = kwargs.get('show_remaining_time', True)
        super(DailyGoalCard, self).__init__(controller, show_feature, *args, **kwargs)

    def _on_job_updated(self):
        self._update_gauge()
        self._update_tag()
        self._update_state()

    def _construct_top(self):
        self.top_cont.height = 12
        self._header_row = Container(name='headerRow', parent=self.top_cont, align=Align.TOTOP, height=12)
        title_icon_cont = ContainerAutoSize(name='iconCont', parent=self._header_row, align=Align.TOLEFT, padRight=2)
        title_icon_cont_content = ContainerAutoSize(name='icon_cont_content', parent=title_icon_cont, align=Align.TOPLEFT, height=12)
        title_icon = Sprite(name='icon', parent=title_icon_cont_content, align=Align.TOLEFT, texturePath='res:/UI/Texture/classes/SkillPlan/airLogo.png', color=eveColor.AIR_TURQUOISE, opacity=0.4, pickState=PickState.ON, width=31, height=12, padRight=4)
        title_icon.OnClick = self.OnClick
        title_cont = Container(name='titleCont', parent=self._header_row)
        self._top_title = TextDetail(parent=title_cont, align=Align.TOPLEFT, color=eveColor.AIR_TURQUOISE, autoFadeSides=16, opacity=0.4)

    def _update_top_title(self):
        if self._top_title is None:
            return
        self._top_title.text = self._get_top_title()

    def _get_top_title(self):
        return GetByLabel('UI/DailyGoals/CardTitle')

    def _construct_middle(self):
        self._construct_tag(parent=self)
        gauge_container = Container(name='gauge_container', parent=self.middle, align=Align.TOTOP, width=300, height=19, padTop=5)
        self._gauge = Gauge(name='gauge', parent=gauge_container, align=Align.TOLEFT, gaugeHeight=2, labelClass=GaugeLabel, textPadding=(0, 0, 0, 5), pickState=PickState.OFF)
        self._update_gauge(animate=False)
        TextHeader(name='title_header', parent=self.middle, align=Align.TOTOP, maxLines=2, text=self.job.title, bold=True, padTop=15)

    def _construct_underlay(self):
        super(JobCard, self)._construct_underlay()
        flair_container = Container(name='flair_container', parent=self, pickState=PickState.OFF, clipChildren=True)
        self._bg_flair = Sprite(name='bgFlair', parent=flair_container, align=Align.TOPRIGHT, texturePath=get_career_path_bg(self.job.career_id), color=self._bg_flair_color, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0, opacity=0.7, pos=self._get_flair_bg_pos())

    def _construct_tag(self, parent):
        tag_container = Container(name='tag_container', parent=parent, align=Align.TOPRIGHT, width=self.FLAIR_TAG_SIZE, height=self.FLAIR_TAG_SIZE, padding=(0, 16, 16, 0))
        self._tag_claimed = Sprite(name='tag_claimed', parent=tag_container, align=Align.CENTER, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/checkmark.png', color=eveColor.SUCCESS_GREEN, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3, width=80, height=80, padRight=4)
        self._tag_icon = TagIcon(name='tag_icon', parent=tag_container, align=Align.CENTER, texturePath=self.job.career_icon, underlayTexturePath=TagIcon.CIRCLE_LARGE, underlayColor=eveColor.SMOKE_BLUE, iconOutputMode=uiconst.OUTPUT_COLOR_AND_GLOW, iconGlowBrightness=0.3, width=self.FLAIR_TAG_SIZE, height=self.FLAIR_TAG_SIZE, iconWidth=self.FLAIR_ICON_SIZE, iconHeight=self.FLAIR_ICON_SIZE, iconColor=self.FLAIR_ICON_COLOR)

    def _get_flair_bg_pos(self):
        x = -self.FLAIR_BG_PATTERN_SIZE / 2 + self.FLAIR_BG_OFFSET
        y = -self.FLAIR_BG_PATTERN_SIZE / 2 + self.FLAIR_BG_OFFSET
        w = self.FLAIR_BG_PATTERN_SIZE
        h = self.FLAIR_BG_PATTERN_SIZE
        return (x,
         y,
         w,
         h)

    def _construct_attention_icons(self, parent):
        self._construct_claim_button(parent)
        self._construct_completion_convenience_button(parent)
        super(DailyGoalCard, self)._construct_attention_icons(parent)
        self._construct_bottom_rewards(parent)
        if self._show_remaining_time:
            self._construct_time_remaining(parent)

    @threadutils.threaded
    def _construct_bottom_rewards(self, parent):
        for reward in self.job.rewards:
            RewardEntry(parent=parent, align=Align.TOLEFT, icon=reward.icon, text=reward.amount_text, padRight=8)

    def _construct_claim_button(self, parent):
        self._claim_button = DailyGoalClaimButton(name='claim_button', parent=parent, align=Align.TORIGHT, density=Density.COMPACT, job=self.job)

    def _construct_completion_convenience_button(self, parent):
        self._cc_button = CompletionConvenienceButton(name='cc_button', parent=parent, align=Align.TORIGHT, density=Density.COMPACT, job=self.job, padLeft=4)

    def _construct_time_remaining(self, parent):
        if self.job.is_expired or self.job.is_completed:
            return
        time_remaining_icon = TimeRemainingIcon(name='time_remaining_icon', parent=parent, align=Align.TORIGHT, job=self.job, padLeft=4)
        time_remaining_icon.OnClick = self.OnClick
        time_remaining_icon.GetMenu = self.GetMenu
        time_remaining_icon.GetDragData = self.GetDragData
        time_remaining_icon.PrepareDrag = self.PrepareDrag

    @eveui.skip_if_destroyed
    def _update_tag(self):
        is_completed_and_claimed = self.job.is_completed and not self.job.has_claimable_rewards
        self._tag_claimed.state = uiconst.UI_DISABLED if is_completed_and_claimed else uiconst.UI_HIDDEN
        self._tag_icon.opacity = 0.1 if is_completed_and_claimed else 1.0

    @eveui.skip_if_destroyed
    def _update_gauge(self, animate = True):
        self._gauge.SetColor(eveColor.SUCCESS_GREEN if self.job.is_completed else eveColor.AIR_TURQUOISE)
        self._gauge.SetValue(self.job.progress_percentage, animate=animate)
        self._gauge.SetText('%s / %s' % (self.job.current_progress, self.job.desired_progress))
        self._gauge.SetLabelColor(eveColor.SUCCESS_GREEN if self.job.is_completed else TextColor.SECONDARY)

    @property
    def _left_line_color(self):
        return eveColor.AIR_TURQUOISE

    @property
    def _hover_frame_color(self):
        return eveColor.AIR_TURQUOISE

    @property
    def _bg_flair_color(self):
        return eveColor.SMOKE_BLUE


class GaugeLabel(EveLabelSmall):
    default_color = eveColor.AIR_TURQUOISE
    default_padBottom = 10


class RewardEntry(ContainerAutoSize):
    default_height = 16

    def __init__(self, icon, text, **kwargs):
        super(RewardEntry, self).__init__(**kwargs)
        self._icon = icon
        self._text = text
        self._layout()

    def _layout(self):
        icon_container = Container(name='icon_container', parent=self, align=Align.TOLEFT, width=16, padRight=4)
        Sprite(name='icon', parent=icon_container, align=Align.CENTERLEFT, texturePath=self._icon, color=TextColor.SECONDARY, width=16, height=16)
        TextBody(name='label', parent=self, align=Align.TOLEFT, text=self._text, autoFadeSides=16, maxLines=1, padTop=3)


class DailyGoalListEntry(JobListEntry):

    def __init__(self, controller, show_feature = False, *args, **kwargs):
        self._gauge = None
        self._gauge_label = None
        self._expanded = True
        self.cc_button_expanded = None
        self.cc_button_minimized = None
        super(DailyGoalListEntry, self).__init__(controller, show_feature, *args, **kwargs)
        self.on_size_changed.connect(self._on_size_changed)

    @property
    def left_line_rgb(self):
        return self._air_theme_rgb

    @property
    def hover_frame_rgb(self):
        return self._air_theme_rgb

    @property
    def bg_flair_rgb(self):
        return self._air_theme_rgb

    @property
    def _air_theme_rgb(self):
        if self.job.is_completed:
            return eveColor.SUCCESS_GREEN[:3]
        return eveColor.AIR_TURQUOISE[:3]

    def _construct_right_content(self, parent):
        self._construct_claimable_assets()

    @threadutils.threaded
    def _construct_claimable_assets(self):
        for reward in self.job.rewards:
            self._construct_reward_icon_and_label(icon=reward.icon, value_text=reward.amount_text)

    def _construct_attention_icons(self, parent):
        self._construct_completion_convenience(parent)
        self._construct_time_remaining(parent)

    def _on_size_changed(self, newWidth, newHeight):
        if not self.cc_button_expanded and not self.cc_button_minimized:
            return
        right_limit = 250
        right_width = newWidth * self.get_right_wrapper_ratio()
        if right_width > right_limit and not self._expanded:
            self._expanded = True
            self.cc_button_expanded.Show()
            self.cc_button_minimized.Hide()
        elif right_width <= right_limit and self._expanded:
            self._expanded = False
            self.cc_button_expanded.Hide()
            self.cc_button_minimized.Show()

    def _construct_completion_convenience(self, parent):
        if not can_pay_for_completion(self.job):
            return
        buttonCnt = ContainerAutoSize(parent=parent, align=Align.TORIGHT, padLeft=4)
        self.cc_button_expanded = CompletionConvenienceButton(parent=buttonCnt, align=Align.CENTERRIGHT, density=Density.COMPACT, job=self.job)
        self.cc_button_minimized = CompletionConvenienceIcon(parent=buttonCnt, align=Align.CENTERRIGHT, job=self.job, icon_size=20)
        self.cc_button_minimized.Hide()

    def _construct_time_remaining(self, parent):
        if self.job.is_expired or self.job.is_completed:
            return
        time_remaining_icon = TimeRemainingIcon(name='time_remaining_icon', parent=parent, align=Align.TORIGHT, job=self.job, padLeft=4)
        time_remaining_icon.OnClick = self.OnClick
        time_remaining_icon.GetMenu = self.GetMenu
        time_remaining_icon.GetDragData = self.GetDragData
        time_remaining_icon.PrepareDrag = self.PrepareDrag

    def _construct_left_content(self, parent):
        self._construct_gauge(parent)

    def _construct_gauge(self, parent):
        gauge_container = ContainerAutoSize(name='gauge_container', parent=parent, align=Align.TORIGHT, height=self.height)
        self._gauge = Gauge(name='gauge', parent=gauge_container, align=Align.CENTERRIGHT, gaugeHeight=2, width=37)
        self._gauge_label = TextBody(name='gauge_label', parent=gauge_container, align=Align.CENTERRIGHT, padRight=45)
        self._update_gauge()

    @eveui.skip_if_destroyed
    def _update_gauge(self):
        color = eveColor.SUCCESS_GREEN if self.job.is_completed else eveColor.CRYO_BLUE
        self._gauge.SetColor(color)
        self._gauge.SetValueTimed(self.job.progress_percentage, duration=0.7)
        self._gauge_label.text = '{:.0%}'.format(self.job.progress_percentage)
        self._gauge_label.color = color


class DailyGoalRewardListEntry(JobRewardListEntry):

    def __init__(self, controller, show_feature = False, *args, **kwargs):
        self._gauge = None
        self._gauge_label = None
        super(DailyGoalRewardListEntry, self).__init__(controller, show_feature, *args, **kwargs)

    def _register(self):
        super(DailyGoalRewardListEntry, self)._register()
        dailyGoalSignals.on_goal_payment_failed.connect(self._on_payment_failed)
        dailyGoalSignals.on_goal_payment_complete.connect(self._on_payment_complete)

    def _unregister(self):
        super(DailyGoalRewardListEntry, self)._unregister()
        dailyGoalSignals.on_goal_payment_failed.disconnect(self._on_payment_failed)
        dailyGoalSignals.on_goal_payment_complete.disconnect(self._on_payment_complete)

    @property
    def left_line_rgb(self):
        return self._air_theme_rgb

    @property
    def hover_frame_rgb(self):
        return self._air_theme_rgb

    @property
    def bg_flair_rgb(self):
        return self._air_theme_rgb

    @property
    def _air_theme_rgb(self):
        if self.job.is_completed:
            return eveColor.SUCCESS_GREEN[:3]
        return eveColor.AIR_TURQUOISE[:3]

    def _construct_right_content(self, parent):
        self._construct_claimable_assets()

    def _construct_claimable_assets(self):
        self.rewardIcons = []
        self.rewardLabels = []
        for reward in self.job.rewards:
            self._construct_reward_icon_and_label(icon=reward.icon, value_text=reward.amount_text)

    def _construct_claim_button(self, parent):
        return DailyGoalClaimButton(name='claim_button', parent=parent, align=Align.CENTERLEFT, density=Density.COMPACT, job=self.job, func=self.OnClaimButton)

    def _construct_attention_icons(self, parent):
        self._construct_time_remaining(parent)

    def _construct_time_remaining(self, parent):
        if self.job.is_expired or self.job.is_completed:
            return
        time_remaining_icon = TimeRemainingIcon(name='time_remaining_icon', parent=parent, align=Align.TORIGHT, job=self.job, padLeft=4)
        time_remaining_icon.OnClick = self.OnClick
        time_remaining_icon.GetMenu = self.GetMenu
        time_remaining_icon.GetDragData = self.GetDragData
        time_remaining_icon.PrepareDrag = self.PrepareDrag

    def _construct_left_content(self, parent):
        self._construct_gauge(parent)

    def _construct_gauge(self, parent):
        gauge_container = ContainerAutoSize(name='gauge_container', parent=parent, align=Align.TORIGHT, height=self.height)
        self._gauge = Gauge(name='gauge', parent=gauge_container, align=Align.CENTERRIGHT, gaugeHeight=2, width=37)
        self._gauge_label = TextBody(name='gauge_label', parent=gauge_container, align=Align.CENTERRIGHT, padRight=45)
        self._update_gauge()

    @eveui.skip_if_destroyed
    def _update_gauge(self, animate = True):
        color = eveColor.SUCCESS_GREEN if self.job.is_completed else eveColor.CRYO_BLUE
        self._gauge.SetColor(color)
        self._gauge.SetValue(self.job.progress_percentage, animate=animate)
        self._gauge_label.text = '{:.0%}'.format(self.job.progress_percentage)
        self._gauge_label.color = color

    def OnClaimButton(self, *args):
        super(DailyGoalRewardListEntry, self).OnClaimButton(*args)
        if self.job.is_trackable and self.job.is_tracked:
            self.job.remove_tracked()
