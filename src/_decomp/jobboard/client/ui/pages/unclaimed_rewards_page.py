#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\pages\unclaimed_rewards_page.py
import carbonui
from carbonui.uicore import uicore
import eveui
import eveformat
import localization
import threadutils
import uthread2
import evetypes
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.cloneGrade import ORIGIN_OPPORTUNITIES
from eve.client.script.ui.shared.cloneGrade.upgradeButton import UpgradeIconButton
from eve.client.script.ui.control.tooltips import TooltipPanel
from dailygoals.client import goalSignals as dailyGoalSignals
from dailygoals.client.const import RewardType
from jobboard.client import get_job_board_service, ProviderType
from jobboard.client.ui.reward_list_entry import JobRewardListEntry
from jobboard.client.ui.util import get_rewards_by_type, select_redeem_location
from .filtered_page import FilteredPage

class UnclaimedRewardsPage(FilteredPage):
    __notifyevents__ = FilteredPage.__notifyevents__ + ['OnSubscriptionChanged']
    _show_as_rewards = True

    def _register(self):
        super(UnclaimedRewardsPage, self)._register()
        dailyGoalSignals.on_goal_payment_earned.connect(self._on_reward_earned)
        dailyGoalSignals.on_goal_payment_redeemed.connect(self._on_reward_redeemed)

    def _unregister(self):
        super(UnclaimedRewardsPage, self)._unregister()
        dailyGoalSignals.on_goal_payment_earned.disconnect(self._on_reward_earned)
        dailyGoalSignals.on_goal_payment_redeemed.disconnect(self._on_reward_redeemed)

    def OnSubscriptionChanged(self, *args, **kwargs):
        self._reconstruct_content()

    def _on_reward_earned(self, _):
        uthread2.start_tasklet(self._refresh_list)

    def _on_reward_redeemed(self, _):
        self._update_job_count()

    def _get_jobs(self):
        return self._service.get_jobs_with_unclaimed_rewards()

    def _get_sorted_jobs(self):
        return sorted(self._jobs, key=lambda job: (not bool(job.get_state_info()), job.title))

    def _validate_job(self, job):
        return job.has_claimable_rewards

    def _refresh_list(self):
        for job in self._service.get_jobs_with_unclaimed_rewards():
            if job.job_id not in self._job_cards:
                self._on_job_added(job)

        self._update_job_count()

    def _claim_all(self):
        jobs = self._get_sorted_jobs()
        jobs_with_item_rewards = [ job for job in jobs if job.has_claimable_item_reward ]
        if jobs_with_item_rewards:
            should_claim_items = select_redeem_location(jobs_with_item_rewards)
        else:
            should_claim_items = True
        for job in jobs:
            if not should_claim_items and job.has_claimable_item_reward:
                continue
            jobCard = self._job_cards.get(job.job_id)
            if not jobCard:
                continue
            uthread2.start_tasklet(jobCard.start_claim_sequence)

    @property
    def display_as_list(self):
        return True

    @eveui.skip_if_destroyed
    def _on_job_state_changed(self, job):
        if job.job_id not in self._job_cards:
            self._on_job_added(job)
        self._update_job_count()

    def _update_job_count(self):
        count = 0
        for job in self._jobs:
            if job.has_claimable_rewards:
                count += 1

        self._filters_section.set_job_count(count)

    def _update_available_content_tags(self):
        pass

    def _construct_content(self):
        super(UnclaimedRewardsPage, self)._construct_content()
        OmegaRestrictedRewards(parent=self._content_container, align=carbonui.Align.TOTOP)

    def _construct_filters(self):
        self._filters_section = UnclaimedRewardsTopBar(parent=self._filters_container, padBottom=16, claim_all_func=self._claim_all)

    def _construct_job_card(self, job):
        if self._cards_container and not self._cards_container.destroyed and job.job_id not in self._job_cards:
            entry = job.construct_reward_entry(parent=self._cards_container, show_feature=self._show_feature)
            self._job_cards[job.job_id] = entry


class UnclaimedRewardsTopBar(eveui.Container):
    default_align = carbonui.Align.TOTOP
    default_height = 24

    def __init__(self, claim_all_func, *args, **kwargs):
        super(UnclaimedRewardsTopBar, self).__init__(*args, **kwargs)
        self._claim_all_func = claim_all_func
        self._layout()

    def set_job_count(self, count):
        self._label.text = localization.GetByLabel('UI/Opportunities/OpportunitiesAmount', amount=count)
        self._claim_all_button.display = count > 1

    def _layout(self):
        self._label = carbonui.TextHeader(parent=self, align=carbonui.Align.TOLEFT, width=150)
        self._claim_all_button = eveui.Button(parent=self, align=carbonui.Align.TORIGHT, func=self._claim_all_clicked, label=localization.GetByLabel('UI/Opportunities/ClaimAll'), display=False, pickState=carbonui.PickState.ON, padRight=8)
        self._claim_all_button.ConstructTooltipPanel = ClaimAllTooltip

    @threadutils.threaded
    def _claim_all_clicked(self, *args, **kwargs):
        if self._claim_all_button.busy:
            return
        self._claim_all_button.busy = True
        self._claim_all_button.disabled = True
        self._claim_all_func()
        uthread2.sleep(2)
        self._claim_all_button.busy = False
        self._claim_all_button.disabled = False


class OmegaRestrictedRewards(eveui.ContainerAutoSize):

    def __init__(self, *args, **kwargs):
        super(OmegaRestrictedRewards, self).__init__(*args, **kwargs)
        self._jobs = []
        self._layout()

    @threadutils.threaded
    def _layout(self):
        if sm.GetService('cloneGradeSvc').IsOmega():
            return
        daily_goals_provider = get_job_board_service().get_provider(ProviderType.DAILY_GOALS)
        self._jobs = daily_goals_provider.get_unclaimed_omega_restricted_jobs()
        if not self._jobs:
            return
        self._construct_header()
        self._construct_entries()

    def _construct_header(self):
        eveui.Line(parent=self, align=carbonui.Align.TOTOP, padTop=32, padBottom=32)
        container = eveui.Container(parent=self, align=carbonui.Align.TOTOP, height=32, padBottom=16)
        carbonui.TextHeader(parent=container, align=carbonui.Align.CENTERLEFT, text=localization.GetByLabel('UI/Opportunities/OmegaOpportunitiesAmount', amount=len(self._jobs)))
        UpgradeIconButton(parent=container, align=carbonui.Align.TORIGHT, glowBrightness=0.5, text=localization.GetByLabel('UI/CloneState/UpgradeToClaim'), onClick=self._on_omega_button)

    def _construct_entries(self):
        for job in self._jobs:
            OmegaRestrictedRewardListEntry(parent=self, controller=job, show_feature=False)

    def _on_omega_button(self, *args, **kwargs):
        uicore.cmd.OpenCloneUpgradeWindow(ORIGIN_OPPORTUNITIES)


class OmegaRestrictedRewardListEntry(JobRewardListEntry):
    OMEGA_RGB = eveColor.OMEGA_YELLOW[:3]

    def _update_left_line_color(self):
        pass

    @property
    def left_line_rgb(self):
        return self.OMEGA_RGB

    @property
    def hover_frame_rgb(self):
        return self.OMEGA_RGB

    @property
    def bg_flair_rgb(self):
        return self.OMEGA_RGB


class ClaimAllTooltip(TooltipPanel):

    def ApplyAttributes(self, attributes):
        super(ClaimAllTooltip, self).ApplyAttributes(attributes)
        self.LoadGeneric1ColumnTemplate()
        corp_projects = get_job_board_service().get_jobs_with_unclaimed_rewards(ProviderType.CORPORATION_GOALS)
        rewards_by_type = get_rewards_by_type(corp_projects)
        if rewards_by_type:
            feature_tag = corp_projects[0].feature_tag
            self._construct_entry(icon=feature_tag.icon, text=feature_tag.title, text_color=carbonui.TextColor.HIGHLIGHT, icon_color=carbonui.TextColor.NORMAL)
            for reward_type, reward_info in rewards_by_type.iteritems():
                self._construct_entry(icon=reward_info['icon'], text=eveformat.number(reward_info['amount']), text_color=carbonui.TextColor.SUCCESS, icon_color=carbonui.TextColor.SECONDARY)

        daily_goals = get_job_board_service().get_jobs_with_unclaimed_rewards(ProviderType.DAILY_GOALS)
        rewards_by_type = get_rewards_by_type(daily_goals)
        if rewards_by_type:
            if corp_projects:
                self.AddSpacer()
            feature_tag = daily_goals[0].feature_tag
            self._construct_entry(icon=feature_tag.icon, text=feature_tag.title, text_color=carbonui.TextColor.HIGHLIGHT, icon_color=carbonui.TextColor.NORMAL)
            for key, reward_info in rewards_by_type.iteritems():
                reward_type = reward_info['reward_type']
                text = eveformat.number(reward_info['amount'])
                icon = reward_info['icon']
                if reward_type == RewardType.SKILL_POINTS:
                    text_color = eveColor.FOCUS_BLUE
                    icon_color = carbonui.TextColor.NORMAL
                elif reward_type == RewardType.ITEM:
                    text_color = carbonui.TextColor.NORMAL
                    icon_color = carbonui.TextColor.NORMAL
                    text = localization.GetByLabel('UI/InfoWindow/FittingItemLabelWithQuantity', quantity=reward_info['amount'], itemName=evetypes.GetName(key))
                else:
                    text_color = carbonui.TextColor.SUCCESS
                    icon_color = carbonui.TextColor.SECONDARY
                self._construct_entry(icon=icon, text=text, text_color=text_color, icon_color=icon_color)

    def _construct_entry(self, icon, text, text_color, icon_color, **kwargs):
        container = eveui.ContainerAutoSize(**kwargs)
        eveui.Sprite(parent=container, align=carbonui.Align.CENTERLEFT, width=16, height=16, texturePath=icon, color=icon_color)
        carbonui.TextBody(parent=container, align=carbonui.Align.CENTERLEFT, left=20, text=text, color=text_color)
        self.AddCell(container)
