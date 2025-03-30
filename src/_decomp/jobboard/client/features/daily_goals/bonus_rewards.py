#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\bonus_rewards.py
import eveui
import math
import logging
import threadutils
import uthread2
import carbonui
import eveformat
import evetypes
import eveicon
from localization import GetByLabel
from carbonui import Align, Density, PickState, uiconst
from carbonui import TextBody, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.control.tooltips import TooltipPanel
from carbon.client.script.environment.AudioUtil import PlaySound
from dailygoals.client.const import RewardType, DailyGoalCategory
from jobboard.client import get_job_board_service, ProviderType
from jobboard.client.ui.util import select_redeem_location, get_rewards_by_category, get_rewards_by_type
logger = logging.getLogger(__name__)

class BonusGoalContainer(Container):
    default_width = 267
    default_height = 265

    def __init__(self, job, claim_all_func, has_rewards, *args, **kwargs):
        super(BonusGoalContainer, self).__init__(*args, **kwargs)
        self._job = job
        rewards = self._job.rewards
        if rewards and rewards[0].reward_type == RewardType.SKILL_POINTS:
            self._reward = rewards[0]
        else:
            self._reward = None
        self._progress_gauge = None
        self._reward_container = None
        self._claim_all_button = None
        self._claim_checkmark = None
        self._claim_all_text = None
        self._claim_all_func = claim_all_func
        self._right_bracket = None
        self._left_bracket = None
        self._layout()
        self._update()
        self.update_claim_all_button(has_rewards)
        self._job.on_job_updated.connect(self._on_job_updated)

    def start_claim_all_animation(self):
        eveui.fade_out(self._reward_container, duration=0.5)
        eveui.fade_out(self._progress_gauge, duration=0.5)
        eveui.fade_out(self._claim_all_button, duration=0.5, on_complete=lambda : self._claim_all_button.Hide())
        eveui.animate(self._right_bracket, 'left', end_value=10, duration=0.5)
        eveui.animate(self._left_bracket, 'left', end_value=-10, duration=0.5)
        eveui.fade_in(self._claim_all_text, duration=0.5)
        animations.Tr2DRotateTo(self.bracket_container, endAngle=-2, duration=0.5)
        PlaySound('monthly_progress_dial_move_play')
        uthread2.sleep(0.6)
        animations.Tr2DRotateTo(self.bracket_container, startAngle=-2, endAngle=-1.58, duration=0.2)
        uthread2.sleep(2)
        eveui.fade_out(self._claim_all_text, duration=0.1)
        eveui.animate(self._right_bracket, 'left', end_value=0, duration=0.1)
        eveui.animate(self._left_bracket, 'left', end_value=0, duration=0.1)
        eveui.fade_in(self._claim_checkmark, duration=0.1)

    def start_claim_all_cleanup_animation(self):
        eveui.fade_out(self._claim_checkmark, duration=0.1)
        animations.Tr2DRotateTo(self.bracket_container, startAngle=-1.58, endAngle=0, duration=0.5)
        eveui.fade_in(self._reward_container, duration=0.5)
        eveui.fade_in(self._progress_gauge, duration=0.5)

    def Close(self):
        if self._job:
            self._job.on_job_updated.disconnect(self._on_job_updated)
        super(BonusGoalContainer, self).Close()

    def _layout(self):
        self._construct_content()
        self._construct_background()
        self._construct_reward()
        self._construct_progress()
        self._construct_animation_components()
        self._construct_claim_all_button()

    def _construct_background(self):
        Sprite(name='circular_flare', parent=self, align=Align.CENTER, pickState=PickState.OFF, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/circle_track_framed_feature_page.png', width=280, height=265)

    def _construct_content(self):
        self.content_container = Container(parent=self, align=Align.CENTER, width=182, height=172)

    def _construct_reward(self):
        self.bracket_content_container = Container(name='over_bracket_container', parent=self.content_container, align=Align.CENTER, padRight=14, width=141, height=135)
        self.bracket_container = Transform(name='bracket_container', parent=self.content_container, align=Align.CENTER, padRight=12)
        self._left_bracket = Transform(parent=self.bracket_container, name='left_bracket_transform', align=Align.CENTER, width=141, height=135)
        Sprite(name='left_bracket', parent=self._left_bracket, align=Align.CENTER, pickState=PickState.OFF, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/circle_bracket.png', width=141, height=135)
        self._right_bracket = Transform(parent=self.bracket_container, name='right_bracket_transform', align=Align.CENTER, width=141, height=135)
        Sprite(name='right_bracket', parent=self._right_bracket, align=Align.CENTER, pickState=PickState.OFF, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/circle_bracket.png', width=141, height=135, rotation=math.pi)
        self._reward_container = ContainerAutoSize(name='reward_container', parent=self.content_container, align=Align.CENTERTOP, height=32, padRight=16)
        Sprite(name='icon', parent=self._reward_container, align=Align.TOLEFT, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/bonus_reward_sp.png', width=32, height=32)
        self._amount_text = TextBody(name='item_amount', parent=self._reward_container, align=Align.TOLEFT, padTop=8)
        self._update_reward_amount()

    def _construct_progress(self):
        self._progress_gauge = DailyBonusGauge(parent=self.bracket_content_container, align=Align.CENTER)

    def _construct_animation_components(self):
        self._claim_all_text = TextBody(parent=self.bracket_content_container, align=Align.CENTER, text='All Rewards Claimed', opacity=0)
        self._claim_checkmark = Sprite(parent=self.bracket_content_container, texturePath='res:/UI/Texture/classes/SkillPlan/completedIcon.png', align=Align.CENTER, width=34, height=34, opacity=0, Left=-6)

    def _construct_claim_all_button(self):
        self._claim_all_button = eveui.Button(name='claim_button', parent=self.content_container, label=GetByLabel('UI/Opportunities/ClaimAll'), align=Align.CENTERBOTTOM, func=self._claim_all_clicked, density=Density.COMPACT, pickState=PickState.ON, padBottom=8, padRight=12, display=False)
        self._claim_all_button.ConstructTooltipPanel = ClaimAllDailyGoalsTooltip

    @threadutils.threaded
    def _claim_all_clicked(self, *args, **kwargs):
        if self._claim_all_button.busy:
            return
        self._claim_all_button.busy = True
        self._claim_all_button.disabled = True
        should_claim = self._select_claim_location()
        if should_claim:
            self._claim_all_func()
            uthread2.sleep(2)
        self._claim_all_button.busy = False
        self._claim_all_button.disabled = False

    def _select_claim_location(self):
        provider = get_job_board_service().get_provider(ProviderType.DAILY_GOALS)
        jobs_with_item_rewards = [ job for job in provider.get_jobs().itervalues() if job.has_claimable_item_reward ]
        return select_redeem_location(jobs_with_item_rewards)

    @eveui.skip_if_destroyed
    def _update(self):
        self.display = bool(self._reward)
        self._progress_gauge.update(self._job)
        self._update_reward_amount()

    def update_claim_all_button(self, display):
        if display:
            self._claim_all_button.display = True
            eveui.fade_in(self._claim_all_button, duration=0.5)
        else:
            eveui.fade_out(self._claim_all_button, duration=0.5, on_complete=lambda : self._claim_all_button.Hide())

    def _update_reward_amount(self):
        self._amount_text.text = self._reward.amount_text if self._reward else ''

    def _on_job_updated(self):
        self._update()


class DailyBonusGauge(Container):
    default_align = Align.CENTER
    default_state = uiconst.UI_NORMAL

    def __init__(self, radius = 32, *args, **kwargs):
        kwargs['height'] = kwargs['width'] = radius * 2
        super(DailyBonusGauge, self).__init__(*args, **kwargs)
        self._progress_gauge = GaugeCircular(name='progress_gauge', parent=self, align=Align.CENTER, pickState=PickState.ON, radius=radius, showMarker=False, glow=True, glowBrightness=0.3, colorBg=(0, 0, 0, 0.15), lineWidth=2.0)
        self._progress_label = TextBody(name='progress_label', parent=self._progress_gauge, align=Align.CENTER)
        self._claim_checkmark = Sprite(name='claim_checkmark', parent=self._progress_gauge, align=Align.CENTER, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/checkmark.png', color=eveColor.SUCCESS_GREEN, width=90, height=90, padRight=4)

    def update(self, daily_bonus_job, animate = True):
        if not daily_bonus_job:
            self.display = False
            return
        gauge_color = eveColor.SUCCESS_GREEN if daily_bonus_job.is_completed else eveColor.AIR_TURQUOISE
        self._progress_gauge.SetColor(colorStart=gauge_color, colorEnd=gauge_color)
        self._progress_gauge.SetValue(daily_bonus_job.progress_percentage, animate=animate)
        if daily_bonus_job.is_completed and not daily_bonus_job.has_claimable_rewards:
            progress_text = ''
            self._claim_checkmark.display = True
        else:
            progress_text = '%s/%s' % (daily_bonus_job.current_progress, daily_bonus_job.desired_progress)
            self._claim_checkmark.display = False
        self._progress_label.text = progress_text
        self._progress_label.color = TextColor.SUCCESS if daily_bonus_job.is_completed else TextColor.NORMAL
        self._progress_gauge.hint = daily_bonus_job.help_text
        self.display = True


class ClaimAllDailyGoalsTooltip(TooltipPanel):

    def _has_omega_reward(self, rewards_by_category):
        if DailyGoalCategory.CATEGORY_MONTHLY_BONUS in rewards_by_category:
            if 'omega' in rewards_by_category[DailyGoalCategory.CATEGORY_MONTHLY_BONUS]:
                return True
        return False

    def _has_alpha_reward(self, rewards_by_category):
        if DailyGoalCategory.CATEGORY_MONTHLY_BONUS in rewards_by_category:
            if 'alpha' in rewards_by_category[DailyGoalCategory.CATEGORY_MONTHLY_BONUS]:
                return True
        return False

    def _add_milestone_reward(self, reward_type, icon, amount, key):
        text_color = carbonui.TextColor.HIGHLIGHT
        icon_color = carbonui.TextColor.NORMAL
        if reward_type == RewardType.ITEM:
            text = GetByLabel('UI/InfoWindow/FittingItemLabelWithQuantity', quantity=amount, itemName=evetypes.GetName(key))
        else:
            text = eveformat.number(amount)
        self._construct_icon_entry(icon=icon, text=text, icon_color=icon_color, text_color=text_color)

    def ApplyAttributes(self, attributes):
        super(ClaimAllDailyGoalsTooltip, self).ApplyAttributes(attributes)
        self.LoadGeneric1ColumnTemplate()
        unclaimed_omega_restricted_jobs = get_job_board_service().get_provider(ProviderType.DAILY_GOALS).get_unclaimed_omega_restricted_jobs()
        daily_goals = get_job_board_service().get_jobs_with_unclaimed_rewards(ProviderType.DAILY_GOALS)
        rewards_by_category = get_rewards_by_category(daily_goals)
        if not rewards_by_category:
            return
        restricted_rewards_by_type = get_rewards_by_type(unclaimed_omega_restricted_jobs)
        feature_tag = daily_goals[0].feature_tag
        self._construct_icon_entry(icon=feature_tag.icon, text=GetByLabel('UI/Seasons/AllRewardsUnlockedFirstLine'), text_color=carbonui.TextColor.HIGHLIGHT, icon_color=carbonui.TextColor.NORMAL)
        if restricted_rewards_by_type and not sm.GetService('cloneGradeSvc').IsOmega():
            self._add_omega_milestones_header(is_locked=True)
            for key, reward_info in restricted_rewards_by_type.iteritems():
                self._add_milestone_reward(reward_type=reward_info['reward_type'], icon=reward_info['icon'], amount=reward_info['amount'], key=key)

        if self._has_omega_reward(rewards_by_category):
            self._add_omega_milestones_header(is_locked=False)
            for key, reward_info in rewards_by_category[DailyGoalCategory.CATEGORY_MONTHLY_BONUS]['omega'].iteritems():
                self._add_milestone_reward(reward_type=reward_info['reward_type'], icon=reward_info['icon'], amount=reward_info['amount'], key=key)

        if self._has_alpha_reward(rewards_by_category):
            self._construct_entry(text=GetByLabel('UI/DailyGoals/AlphaMilestones'), text_color=carbonui.TextColor.SECONDARY)
            for key, reward_info in rewards_by_category[DailyGoalCategory.CATEGORY_MONTHLY_BONUS]['alpha'].iteritems():
                self._add_milestone_reward(reward_type=reward_info['reward_type'], icon=reward_info['icon'], amount=reward_info['amount'], key=key)

        if DailyGoalCategory.CATEGORY_DAILY_BONUS in rewards_by_category:
            self._construct_entry(text=GetByLabel('UI/DailyGoals/DailyBonus'), text_color=carbonui.TextColor.SECONDARY)
            amount = rewards_by_category[DailyGoalCategory.CATEGORY_DAILY_BONUS][RewardType.SKILL_POINTS]['amount']
            self._construct_icon_entry(text=eveformat.number(amount), icon=rewards_by_category[DailyGoalCategory.CATEGORY_DAILY_BONUS][RewardType.SKILL_POINTS]['icon'], icon_color=carbonui.TextColor.NORMAL, text_color=eveColor.FOCUS_BLUE)
        if DailyGoalCategory.CATEGORY_DAILY in rewards_by_category:
            self._construct_entry(text=feature_tag.title, text_color=carbonui.TextColor.SECONDARY)
            for key, reward_info in rewards_by_category[DailyGoalCategory.CATEGORY_DAILY].iteritems():
                text = eveformat.number(reward_info['amount'])
                icon = reward_info['icon']
                text_color = carbonui.TextColor.SUCCESS
                icon_color = carbonui.TextColor.SECONDARY
                self._construct_icon_entry(icon=icon, text=text, text_color=text_color, icon_color=icon_color)

    def _add_omega_milestones_header(self, is_locked):
        if is_locked:
            self._construct_icon_entry(icon=eveicon.locked, text=GetByLabel('UI/DailyGoals/OmegaMilestones'), icon_color=eveColor.OMEGA_YELLOW, text_color=eveColor.OMEGA_YELLOW)
            return
        self._construct_entry(text=GetByLabel('UI/DailyGoals/OmegaMilestones'), text_color=carbonui.TextColor.SECONDARY)

    def _construct_icon_entry(self, icon, text, text_color, icon_color, **kwargs):
        container = eveui.ContainerAutoSize(**kwargs)
        eveui.Sprite(parent=container, align=carbonui.Align.CENTERLEFT, width=16, height=16, texturePath=icon, color=icon_color)
        carbonui.TextBody(parent=container, align=carbonui.Align.CENTERLEFT, left=20, text=text, color=text_color)
        self.AddCell(container)

    def _construct_entry(self, text, text_color, **kwargs):
        container = eveui.ContainerAutoSize(**kwargs)
        carbonui.TextBody(parent=container, align=carbonui.Align.CENTERLEFT, text=text, color=text_color)
        self.AddCell(container)
