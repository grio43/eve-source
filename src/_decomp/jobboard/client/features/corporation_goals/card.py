#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\corporation_goals\card.py
import carbonui
import eveicon
import eveui
from carbonui import Align, TextColor, Density, ButtonStyle, uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.uiconst import PickState
from corporation.client.goals import goalSignals
from corporation.client.goals import goalsUtil
from eve.client.script.ui import eveThemeColor, eveColor
from eve.client.script.ui.shared.neocom.corporation.corp_goals.forms import goalForms
from eveformat import currency, number_readable_short
from localization import GetByLabel
from jobboard.client.features.corporation_goals.claim_button import CorporationGoalClaimButton
from jobboard.client.features.corporation_goals.tooltips import AvailableRewardsTooltip, ProgressTooltip
from jobboard.client.ui.card import JobCard
from jobboard.client.ui.list_entry import JobListEntry
from jobboard.client.ui.personal_progress_bar import PersonalProgressGauge
from jobboard.client.ui.progress_bar import ProgressGauge
from jobboard.client.ui.reward_list_entry import JobRewardListEntry
from jobboard.client.ui.tag_icon import TagIcon
from jobboard.client.ui.time_remaining import TimeRemainingIcon
from jobboard.client.ui.solar_system_chip import ClosestSolarSystemChip
from jobboard.client.features.corporation_goals.tooltips import ClaimableRewardsTooltip

class ClaimableRewardsIcon(eveui.ContainerAutoSize):
    default_align = carbonui.Align.TORIGHT
    default_state = eveui.State.normal
    default_pickState = PickState.ON

    def __init__(self, job, icon_size = 16, *args, **kwargs):
        super(ClaimableRewardsIcon, self).__init__(*args, **kwargs)
        self._job = job
        self._icon = eveui.Sprite(name='claimable_rewards_icon', parent=self, state=eveui.State.disabled, align=carbonui.Align.CENTER, width=icon_size, height=icon_size, texturePath=eveicon.contribution, color=carbonui.TextColor.SUCCESS, opacity=carbonui.TextColor.NORMAL.opacity)

    def ConstructTooltipPanel(self):
        return ClaimableRewardsTooltip(self._job)


class CorporationGoalCard(JobCard):

    def __init__(self, controller, show_feature = False, *args, **kwargs):
        self._isk_label = None
        self._isk_icon = None
        self._claimable_icon = None
        super(CorporationGoalCard, self).__init__(controller, show_feature, *args, **kwargs)

    def _on_job_updated(self):
        self._update_gauge()
        self._update_claimable_icon()
        self._update_isk_remaining_text()
        if self._solar_system_chip:
            self._solar_system_chip.set_solar_system_id(self.job.solar_system_id)

    def _update_state(self):
        super(CorporationGoalCard, self)._update_state()
        self._update_gauge(animate=False)
        self._update_claimable_icon()
        self._update_isk_remaining_text()

    def _construct_top_right(self):
        self.gauge = PersonalProgressGauge(parent=self._top_right_container, align=Align.CENTER, radius=25, state=uiconst.UI_NORMAL, state_info=self.job.get_detailed_state_info())
        self.gauge.ConstructTooltipPanel = self._construct_progress_tooltip

    def _construct_solar_system_chip(self):
        closest_solar_system_id = self.job.solar_system_id
        if closest_solar_system_id is None:
            return
        location_ids = self.job.location_ids
        if len(location_ids) == 1 and location_ids[0] == closest_solar_system_id:
            return super(CorporationGoalCard, self)._construct_solar_system_chip()
        container = eveui.Container(parent=self.top_cont, align=Align.TOTOP, height=20, padTop=8, clipChildren=True)
        self._solar_system_chip = ClosestSolarSystemChip(parent=container, align=Align.TOLEFT, solar_system_id=closest_solar_system_id, location_ids=location_ids)
        self._solar_system_chip.OnClick = self.OnClick

    def _update_gauge(self, animate = True):
        self.gauge.set_state_info(self.job.get_detailed_state_info())
        self.gauge.set_value(self.job.progress_percentage, animate=animate)
        self.gauge.set_inner_value(self.job.personal_progress_percentage, animate=animate)

    def _update_claimable_icon(self):
        if not self.job.has_claimable_rewards or not self._claimable_icon:
            return
        if not self._claimable_icon.display:
            self._claimable_icon.display = True

    def _update_isk_remaining_text(self):
        isk_remaining = self.job.get_isk_payout_remaining()
        if isk_remaining:
            if not self._isk_icon:
                self._isk_icon = eveui.Sprite(parent=self.bottom_content_cont, state=uiconst.UI_NORMAL, align=eveui.Align.center_left, pos=(0, 0, 16, 16), texturePath=eveicon.isk, color=TextColor.SECONDARY)
                self._isk_icon.OnClick = self.OnClick
                self._isk_icon.GetMenu = self.GetMenu
                self._isk_icon.GetDragData = self.GetDragData
                self._isk_icon.PrepareDrag = self.PrepareDrag
                self._isk_icon.ConstructTooltipPanel = self._construct_available_rewards_tooltip
            if not self._isk_label:
                self._isk_label = carbonui.TextBody(parent=self.bottom_content_cont, state=uiconst.UI_NORMAL, align=eveui.Align.center_left, left=24, maxLines=1, autoFadeSides=16)
                self._isk_label.OnClick = self.OnClick
                self._isk_label.GetMenu = self.GetMenu
                self._isk_label.GetDragData = self.GetDragData
                self._isk_label.PrepareDrag = self.PrepareDrag
                self._isk_label.ConstructTooltipPanel = self._construct_available_rewards_tooltip
            self._isk_label.text = _get_isk_reward_remaining_text(self.job, isk_remaining)

    def _construct_actions(self, parent):
        super(CorporationGoalCard, self)._construct_actions(parent)
        if goalsUtil.CanAuthorGoals():
            ButtonIcon(parent=parent, align=Align.TORIGHT, texturePath=eveicon.copy, hint=GetByLabel('UI/Corporations/Goals/CloneProject'), func=self.OnCloneBtn, pos=(0, 0, 24, 24))
            ButtonIcon(parent=parent, align=Align.TORIGHT, texturePath=eveicon.edit, hint=GetByLabel('UI/Corporations/Goals/ViewAdminDetails'), func=self.OnViewDetailsBtn, pos=(0, 0, 24, 24))

    def _construct_attention_icons(self, parent):
        if self.job.expiration_time:
            self._construct_time_remaining(parent)
        self._construct_claimable_rewards(parent)

    def _construct_time_remaining(self, parent):
        if self.job.is_expired or self.job.is_completed:
            return
        time_remaining_icon = TimeRemainingIcon(name='time_remaining_icon', parent=parent, align=Align.TORIGHT, job=self.job, padLeft=4)
        time_remaining_icon.OnClick = self.OnClick
        time_remaining_icon.GetMenu = self.GetMenu
        time_remaining_icon.GetDragData = self.GetDragData
        time_remaining_icon.PrepareDrag = self.PrepareDrag

    def _construct_claimable_rewards(self, parent):
        self._claimable_icon = ClaimableRewardsIcon(parent=parent, job=self.job, align=Align.TORIGHT, padLeft=4, pos=(0, 0, 24, 24), display=self.job.has_claimable_rewards)
        self._claimable_icon.OnClick = self.OnClick
        self._claimable_icon.GetMenu = self.GetMenu
        self._claimable_icon.GetDragData = self.GetDragData
        self._claimable_icon.PrepareDrag = self.PrepareDrag

    def _construct_title_icons(self, container):
        super(CorporationGoalCard, self)._construct_title_icons(container)
        tag_icon = TagIcon(parent=container, align=Align.TOLEFT, texturePath=self.job.contribution_method.icon, hint=self.job.contribution_method.info, pickState=PickState.ON, padRight=4)
        tag_icon.OnClick = self.OnClick

    def _get_top_title(self):
        if self._show_feature:
            return self.job.feature_title
        else:
            return self.job.progress_title

    def OnViewDetailsBtn(self, *args):
        goalSignals.on_view_details(self.job.job_id)

    def OnCloneBtn(self, *args):
        goalForms.OpenDuplicateGoalFormWindow(self.job.goal)

    def _construct_available_rewards_tooltip(self):
        return AvailableRewardsTooltip(job=self.job)

    def _construct_progress_tooltip(self):
        return ProgressTooltip(job=self.job)


class CorporationGoalListEntry(JobListEntry):

    def __init__(self, *args, **kwargs):
        self._isk_label = None
        self._isk_icon = None
        self._contributed_icon = None
        super(CorporationGoalListEntry, self).__init__(*args, **kwargs)

    def _construct_left_content(self, parent):
        super(CorporationGoalListEntry, self)._construct_left_content(parent)
        gauge_container = eveui.ContainerAutoSize(name='gauge_container', parent=parent, align=eveui.Align.to_right, padRight=8)
        self._gauge = ProgressGauge(parent=gauge_container, state=uiconst.UI_NORMAL, align=eveui.Align.center, radius=12, show_label=False)
        self._gauge.OnClick = self.OnClick
        self._gauge.GetMenu = self.GetMenu
        self._gauge.GetDragData = self.GetDragData
        self._gauge.PrepareDrag = self.PrepareDrag
        self._gauge.ConstructTooltipPanel = self._construct_progress_tooltip
        self._update_gauge(animate=False)

    def _construct_solar_system_chip(self):
        closest_solar_system_id = self.job.solar_system_id
        if closest_solar_system_id is None:
            return
        location_ids = self.job.location_ids
        if len(location_ids) == 1 and location_ids[0] == closest_solar_system_id:
            return super(CorporationGoalListEntry, self)._construct_solar_system_chip()
        container = eveui.ContainerAutoSize(parent=self.left_container, align=Align.TORIGHT)
        self._solar_system_chip = ClosestSolarSystemChip(parent=container, align=Align.CENTERRIGHT, align_content=Align.TOLEFT, solar_system_id=closest_solar_system_id, location_ids=location_ids, compact=True)
        self._solar_system_chip.OnClick = self.OnClick

    def _construct_right_content(self, parent):
        isk_remaining = self.job.get_isk_payout_remaining()
        if isk_remaining:
            self._isk_icon, self._isk_label = self._construct_reward_icon_and_label(eveicon.isk, _get_isk_reward_remaining_text(self.job, isk_remaining))
            self._isk_icon.OnClick = self.OnClick
            self._isk_icon.GetMenu = self.GetMenu
            self._isk_icon.GetDragData = self.GetDragData
            self._isk_icon.PrepareDrag = self.PrepareDrag
            self._isk_icon.ConstructTooltipPanel = self._construct_available_rewards_tooltip
            self._isk_icon.color = TextColor.SECONDARY
            self._isk_icon.state = uiconst.UI_NORMAL
            self._isk_label.OnClick = self.OnClick
            self._isk_label.GetMenu = self.GetMenu
            self._isk_label.GetDragData = self.GetDragData
            self._isk_label.PrepareDrag = self.PrepareDrag
            self._isk_label.ConstructTooltipPanel = self._construct_available_rewards_tooltip
            self._isk_label.state = uiconst.UI_NORMAL
        super(CorporationGoalListEntry, self)._construct_right_content(parent)

    def _construct_actions(self, parent):
        super(CorporationGoalListEntry, self)._construct_actions(parent)
        if goalsUtil.CanAuthorGoals():
            ButtonIcon(parent=parent, align=Align.TORIGHT, texturePath=eveicon.copy, hint=GetByLabel('UI/Corporations/Goals/CloneProject'), func=self.OnCloneBtn, pos=(0, 0, 24, 24))
            ButtonIcon(parent=parent, align=Align.TORIGHT, texturePath=eveicon.edit, hint=GetByLabel('UI/Corporations/Goals/ViewAdminDetails'), func=self.OnViewDetailsBtn, pos=(0, 0, 24, 24))

    def _construct_attention_icons(self, parent):
        container = eveui.ContainerAutoSize(name='attention_icon_cont', parent=parent, align=eveui.Align.to_right, padLeft=4)
        if self.job.expiration_time:
            self._construct_time_remaining(container)
        self._construct_claimable_rewards(container)

    def _construct_claimable_rewards(self, parent):
        icon_container = eveui.ContainerAutoSize(name='has_contributed_icon', parent=parent, align=eveui.Align.to_right)
        self._contributed_icon = eveui.Sprite(name='contributed_icon', parent=icon_container, texturePath=eveicon.contribution, align=eveui.Align.center, state=eveui.State.normal, width=16, height=16, hint=GetByLabel('UI/Corporations/Goals/YouHaveContributed'), color=eveThemeColor.THEME_FOCUS, display=bool(self.job.get_my_progress()))
        if self.job.has_claimable_rewards:
            self._contributed_icon.ConstructTooltipPanel = self._construct_claimable_tooltip
            self._contributed_icon.color = carbonui.TextColor.SUCCESS
        self._contributed_icon.OnClick = self.OnClick
        self._contributed_icon.GetMenu = self.GetMenu
        self._contributed_icon.GetDragData = self.GetDragData
        self._contributed_icon.PrepareDrag = self.PrepareDrag

    def _construct_time_remaining(self, parent):
        if self.job.is_expired or self.job.is_completed:
            return
        time_remaining_icon = TimeRemainingIcon(name='time_remaining_icon', parent=parent, align=eveui.Align.to_right, job=self.job, padLeft=4)
        time_remaining_icon.OnClick = self.OnClick
        time_remaining_icon.GetMenu = self.GetMenu
        time_remaining_icon.GetDragData = self.GetDragData
        time_remaining_icon.PrepareDrag = self.PrepareDrag

    def _construct_claimable_tooltip(self):
        return ClaimableRewardsTooltip(self.job)

    def _construct_title_icons(self, container):
        super(CorporationGoalListEntry, self)._construct_title_icons(container)
        container = eveui.Container(parent=container, align=Align.TOLEFT, padRight=8, width=16, height=16, pickState=PickState.ON, hint=self.job.contribution_method.info)
        eveui.Sprite(parent=container, texturePath=self.job.contribution_method.icon, align=Align.CENTER, width=16, height=16, color=carbonui.TextColor.SECONDARY, pickState=PickState.OFF)
        container.OnClick = self.OnClick

    def _update_state(self):
        super(CorporationGoalListEntry, self)._update_state()
        self._update_contributed_icon()

    def _update_contributed_icon(self):
        if self._contributed_icon:
            self._contributed_icon.parent.display = bool(self.job.get_my_progress())

    def OnViewDetailsBtn(self, *args):
        goalSignals.on_view_details(self.job.job_id)

    def OnCloneBtn(self, *args):
        goalForms.OpenDuplicateGoalFormWindow(self.job.goal)

    def OnColorThemeChanged(self):
        super(CorporationGoalListEntry, self).OnColorThemeChanged()
        if not self._contributed_icon:
            return
        if self.job.has_claimable_rewards:
            self._contributed_icon.ConstructTooltipPanel = self._construct_claimable_tooltip
            self._contributed_icon.color = carbonui.TextColor.SUCCESS
        else:
            self._contributed_icon.color = eveThemeColor.THEME_FOCUS

    def _update_gauge(self, animate = True):
        if self.job.is_active:
            self._gauge.Show()
            self._gauge.set_value(self.job.progress_percentage, animate=animate)
        else:
            self._gauge.Hide()

    def _construct_available_rewards_tooltip(self):
        return AvailableRewardsTooltip(job=self.job)

    def _construct_progress_tooltip(self):
        return ProgressTooltip(job=self.job)


class CorporationGoalRewardListEntry(JobRewardListEntry):

    def _register(self):
        super(CorporationGoalRewardListEntry, self)._register()
        goalSignals.on_goal_reward_earned.connect(self._on_payment_earned)
        goalSignals.on_goal_reward_redeemed.connect(self._on_payment_complete)
        goalSignals.on_goal_redeem_failed.connect(self._on_payment_failed)

    def _unregister(self):
        super(CorporationGoalRewardListEntry, self)._unregister()
        goalSignals.on_goal_reward_earned.disconnect(self._on_payment_earned)
        goalSignals.on_goal_reward_redeemed.disconnect(self._on_payment_complete)
        goalSignals.on_goal_redeem_failed.disconnect(self._on_payment_failed)

    def _on_job_updated(self):
        super(CorporationGoalRewardListEntry, self)._on_job_updated()
        self._update_gauge()

    def _construct_left_content(self, parent):
        super(CorporationGoalRewardListEntry, self)._construct_left_content(parent)
        gauge_container = eveui.ContainerAutoSize(name='gauge_container', parent=parent, align=eveui.Align.to_right, padRight=8)
        self._gauge = ProgressGauge(parent=gauge_container, align=eveui.Align.center, radius=12, show_label=False)
        self._update_gauge(animate=False)

    def _construct_claim_button(self, parent):
        return CorporationGoalClaimButton(name='claim_button', parent=parent, align=Align.CENTERLEFT, density=Density.COMPACT, style=ButtonStyle.SUCCESS if self.job.is_completed else ButtonStyle.NORMAL, job=self.job, func=self.OnClaimButton)

    def _update_gauge(self, animate = True):
        if self.job.is_active:
            self._gauge.Show()
            self._gauge.set_value(self.job.progress_percentage, animate=animate)
        else:
            self._gauge.Hide()

    @property
    def hover_frame_rgb(self):
        if self.job.is_completed:
            return eveColor.SUCCESS_GREEN[:3]
        return super(CorporationGoalRewardListEntry, self).hover_frame_rgb

    @property
    def bg_flair_rgb(self):
        if self.job.is_completed:
            return eveColor.SUCCESS_GREEN[:3]
        return eveThemeColor.THEME_FOCUSDARK[:3]


def _get_isk_reward_remaining_text(job, total_isk_remaining):
    if job.participation_limit:
        return u'{myRemaining} <color={totalColor}>({totalRemaining})</color>'.format(myRemaining=currency.isk(job.get_my_isk_payout_remaining(), fraction=False), totalRemaining=number_readable_short(total_isk_remaining), totalColor=TextColor.SECONDARY)
    else:
        return currency.isk(total_isk_remaining, fraction=False)
