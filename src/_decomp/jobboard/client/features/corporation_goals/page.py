#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\corporation_goals\page.py
import eveicon
import eveui
import trinity
import carbonui
from carbonui import Align, TextColor
from carbonui.primitives.cardsContainer import CardsContainer
from carbonui.uiconst import PickState
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveIcon import CorpIcon
from eve.client.script.ui.shared.neocom.corporation.corp_goals.goalCircularGauge import GoalCircularGauge
from eveformat import currency
from evelink.client import character_link, corporation_link
from eveui import Sprite
from jobboard.client.ui.pages.details_page import JobPage, DetailsSection
from jobboard.client.ui.parameter_container import ParameterContainer, GoalParameterContainer
from jobboard.client.ui.reward_info_container import RewardInfoContainer
from localization import GetByLabel
from localization.formatters import FormatNumeric
from jobboard.client.ui.time_remaining import TimeRemaining
from jobboard.client.ui.end_time import EndTime
from carbonui.primitives.line import Line
from .tooltips import GoalRewardToolTip, TotalRewardToolTip, CoverageRatioTooltip

class CorporationGoalPage(JobPage):

    def _update(self):
        has_rewards = self.job.has_rewards
        if self.job.goal.has_personal_progress():
            self._personal_progress_ratio.text = self._get_ratio_label(self.job.goal.get_my_progress_ratio() * 100.0)
            self._personal_progress_value.text = self._progress_label_formatted(self.job.goal.get_my_progress())
            self._project_progress_total.text = u'/ {}'.format(self._progress_label_formatted(self.job.get_my_total_progress()))
            self._personal_progress_bar.SetValue(self.job.personal_progress_percentage, self.job.goal_state)
            if has_rewards:
                if self.job.participation_limit:
                    self._personal_limit.Show()
                    self._personal_limit.text = currency.isk(self.job.get_my_isk_payout_remaining())
                    if self.job.is_ship_insurance():
                        self._personal_limit.caption = GetByLabel('UI/Corporations/Goals/RemainingCompensation')
                    else:
                        self._personal_limit.caption = GetByLabel('UI/Corporations/Goals/AvailableToEarn')
                else:
                    self._personal_limit.Hide()
                self._personal_earned_rewards_value.Show()
                self._personal_earned_rewards_value.text = currency.isk(self.job.earned_amount)
            else:
                self._personal_limit.Hide()
                self._personal_earned_rewards_value.Hide()
        if self.job.is_ship_insurance():
            self._personal_earned_rewards_value.Hide()
        self._total_progress_bar.SetValue(self.job.progress_percentage, self.job.goal_state)
        self._total_progress_icon.SetTexturePath(self.job.goal.contribution_method.icon)
        self._total_progress_value.text = self._progress_label_formatted(self.job.goal.get_current_progress())
        self._total_target_value.text = u'/ {}'.format(self._progress_label_formatted(self.job.goal.get_desired_progress()))
        self._total_progress_ratio.text = self._get_ratio_label(self.job.goal.get_progress_ratio() * 100.0)
        if has_rewards:
            if self.job.is_ship_insurance() and self.job.get_coverage_per_loss():
                self._remaining_reward.text = currency.isk(self.job.get_coverage_per_loss())
                self._remaining_reward.caption = GetByLabel('UI/Corporations/Goals/CoverageLimitPerLoss')
                self._remaining_reward.icon = eveicon.spaceship_command
            else:
                self._remaining_reward.text = currency.isk(self.job.get_isk_payout_remaining())
                self._remaining_reward.caption = GetByLabel('UI/Corporations/Goals/RemainingISKReward')
                self._remaining_reward.icon = eveicon.isk
        self._update_state()
        self._top_buttons_container.Flush()
        self._construct_top_buttons(parent=self._top_buttons_container)
        if self._solar_system_chip:
            self._solar_system_chip.set_solar_system_id(self.job.solar_system_id)

    def _get_ratio_label(self, ratio):
        return u'{ratio:.0f}% <color={descColor}>{desc}</color>'.format(ratio=ratio, descColor=TextColor.SECONDARY, desc=self.job.goal.contribution_method.progress_description)

    def _progress_label_formatted(self, base_label):
        if self.job.is_ship_insurance():
            return currency.isk(base_label)
        return FormatNumeric(base_label, useGrouping=True)

    def _construct_body(self, parent_container):
        self._construct_time(parent_container)
        self._construct_progress(parent_container)
        self._construct_objectives(parent_container)
        self._construct_description(parent_container)
        self._construct_character(parent_container)
        self._update()

    def _construct_description(self, parent_container):
        if self.job.description:
            description_card = DetailsSection(parent=parent_container, title='Details', max_content_height=100, padding=(0, 0, 0, 24))
            container = description_card.content_container
            job_description = u'{}'.format(self.job.description)
            text = u'<color={}>{}</color>'.format(TextColor.NORMAL.hex_argb, job_description)
            carbonui.TextBody(parent=container, align=eveui.Align.to_top, text=text, pickState=PickState.ON, color=eveColor.WHITE)

    def _construct_time(self, parent_container):
        end_time = self.job.end_time
        if not end_time:
            return
        expiration_container = eveui.Container(parent=parent_container, align=Align.TOTOP, height=16)
        if self.job.is_active and self.job.expiration_time:
            TimeRemaining(parent=expiration_container, align=Align.TOLEFT, job=self.job)
            Line(parent=expiration_container, align=Align.TOLEFT, padRight=8, padLeft=8)
        EndTime(parent=expiration_container, align=Align.TOLEFT, end_time=end_time)

    def _construct_progress(self, parent_container):
        progress_container = eveui.ContainerAutoSize(name='progressContainer', parent=parent_container, align=eveui.Align.to_top)
        self._construct_total_progress(progress_container)
        if self.job.goal.has_personal_progress():
            personal_progress_container = eveui.ContainerAutoSize(parent=parent_container, name='personalProgress', align=Align.TOTOP)
            self._construct_personal_progress(personal_progress_container)

    def _construct_personal_progress(self, parent_container):
        headerHint = None
        if self.job.participation_limit:
            headerHint = GetByLabel('UI/Corporations/Goals/ParticipationLimitExplanationTooltip')
        personal_card = DetailsSection(parent=parent_container, title=GetByLabel('UI/Corporations/Goals/YourContribution'), hint=headerHint, padding=0)
        flow_cont = CardsContainer(name='personal_flow_cont', parent=personal_card.content_container, align=Align.TOTOP, autoHeight=True, cardHeight=112, contentSpacing=(16, 8), cardMaxWidth=500, maxColumnCount=2)
        container = eveui.ContainerAutoSize(name='personal_prog_cont', parent=flow_cont, align=Align.TOTOP, alignMode=Align.TOPLEFT)
        self._personal_progress_bar = GoalCircularGauge(parent=container, align=Align.TOPLEFT, radius=40, showLabel=False)
        eveui.CharacterPortrait(parent=self._personal_progress_bar, align=eveui.Align.center, size=56, character_id=session.charid, textureSecondaryPath='res:/UI/Texture/circle-64.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        text_container = eveui.ContainerAutoSize(name='personal_prog_value_cont', parent=container, align=carbonui.Align.TOALL, padLeft=96)
        self._personal_progress_value = carbonui.TextHeader(name='personal_prog_value', parent=text_container, align=eveui.Align.to_top, text='-', bold=True, padBottom=1)
        self._project_progress_total = carbonui.TextDetail(name='personal_prog_total', parent=text_container, align=eveui.Align.to_top, text='-', padBottom=4)
        self._personal_progress_ratio = carbonui.TextDetail(name='personal_prog_ratio', parent=text_container, align=eveui.Align.to_top, text='-')
        isk_summary_section = eveui.ContainerAutoSize(parent=flow_cont, name='total_earnings', align=eveui.Align.to_top, alignMode=Align.TOPRIGHT)
        self._personal_limit = RewardInfoContainer(parent=isk_summary_section, align=Align.TOTOP, caption=GetByLabel('UI/Corporations/Goals/AvailableToEarn'), icon=eveicon.isk, text='-', job=self.job, tooltip=GoalRewardToolTip)
        self._personal_earned_rewards_value = RewardInfoContainer(parent=isk_summary_section, align=Align.TOTOP, caption=GetByLabel('UI/Corporations/Goals/TotalEarned'), icon=eveicon.checkmark, text='-', job=self.job, tooltip=GoalRewardToolTip)

    def _construct_total_progress_overview(self, parent_container):
        container = eveui.ContainerAutoSize(name='total_prog_wrapper', parent=parent_container, align=eveui.Align.to_top, alignMode=Align.TOPLEFT)
        self._total_progress_bar = GoalCircularGauge(parent=container, align=Align.TOPLEFT, radius=40, showLabel=False)
        self._total_progress_icon = Sprite(name='total_prog_icon', parent=self._total_progress_bar, align=Align.CENTER, pos=(0, 0, 16, 16), color=TextColor.SECONDARY)
        text_container = eveui.ContainerAutoSize(parent=container, align=carbonui.Align.TOALL, padLeft=96)
        self._total_progress_value = carbonui.TextHeader(name='total_prog_progress', parent=text_container, align=eveui.Align.to_top, text='-', bold=True, padBottom=1)
        self._total_target_value = carbonui.TextDetail(name='total_prog_target', parent=text_container, align=eveui.Align.to_top, text='-', padBottom=4)
        self._total_progress_ratio = carbonui.TextDetail(name='total_prog_ratio', parent=text_container, align=eveui.Align.to_top, text='-')

    def _construct_total_progress(self, parent_container):
        personal_card = DetailsSection(parent=parent_container, title=GetByLabel('UI/Corporations/Goals/Progress'))
        flow_cont = CardsContainer(name='total_prog_flow_cont', parent=personal_card.content_container, align=Align.TOTOP, autoHeight=True, cardHeight=112, contentSpacing=(16, 8), cardMaxWidth=500, maxColumnCount=2)
        self._construct_total_progress_overview(flow_cont)
        if self.job.reward_amount_per_contribution:
            isk_summary_section = eveui.ContainerAutoSize(parent=flow_cont, name='isk_summary_section', align=eveui.Align.to_top, alignMode=Align.TOPRIGHT)
            self._remaining_reward = RewardInfoContainer(parent=isk_summary_section, align=Align.TOTOP, caption=GetByLabel('UI/Corporations/Goals/RemainingISKReward'), icon=eveicon.isk, text=currency.isk(self.job.get_isk_payout_remaining()), padBottom=16, job=self.job, tooltip=TotalRewardToolTip)
            is_ship_insurance = self.job.is_ship_insurance()
            if self.job.is_ship_insurance():
                self._reward_per_contribution = RewardInfoContainer(parent=isk_summary_section, align=Align.TOTOP, caption=self.job.contribution_method.rewarding_description, icon=eveicon.ratio if is_ship_insurance else eveicon.contribution, text=self.job.get_formatted_coverage_ratio(), job=self.job, tooltip=CoverageRatioTooltip)
            else:
                self._reward_per_contribution = RewardInfoContainer(parent=isk_summary_section, align=Align.TOTOP, caption=self.job.contribution_method.rewarding_description, icon=eveicon.ratio if is_ship_insurance else eveicon.contribution, text=currency.isk(self.job.reward_amount_per_contribution))

    def _construct_objectives(self, parent_container):
        progress_card = DetailsSection(parent=parent_container, title=GetByLabel('UI/Agents/StandardMission/Objectives'), padding=(0, 0, 0, 24))
        container = progress_card.content_container
        contribution_method = self.job.goal.contribution_method
        ParameterContainer(parent=container, align=Align.TOTOP, caption=GetByLabel('UI/Corporations/Goals/ContributionMethod'), hint=self.job.goal.contribution_method.info, text=contribution_method.title, icon=contribution_method.icon)
        if self.job.is_ship_insurance():
            self._add_ship_insurance_params(container, contribution_method)
        else:
            for param in contribution_method.parameters:
                self._add_parameter(container, param)

    def _add_ship_insurance_params(self, parent, method):
        for param in method.parameters:
            if param.key == 'cover_implants':
                continue
            if param.key == 'ship':
                param.set_includes_capsules(method.get_parameter('cover_implants').value)
            self._add_parameter(parent, param)

    def _add_parameter(self, parent, param):
        GoalParameterContainer(parent=parent, align=Align.TOTOP, controller=param, padTop=16)

    def _construct_character(self, parent_container):
        dateString = str(self.job.creation_date.date())
        creator_card = DetailsSection(parent=parent_container, title=GetByLabel('UI/Corporations/Goals/CreatedOn', dateString=dateString), padding=0)
        container = eveui.Container(parent=creator_card.content_container, align=eveui.Align.to_top, height=64)
        character_container = eveui.Container(parent=container, align=eveui.Align.to_left_prop, width=0.5)
        corporation_container = eveui.Container(parent=container, align=eveui.Align.to_all)
        eveui.CharacterPortrait(parent=character_container, align=eveui.Align.to_left, size=64, padRight=16, character_id=self.job.creator_id, textureSecondaryPath='res:/UI/Texture/circle_full.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        text_container = eveui.ContainerAutoSize(parent=character_container, align=carbonui.Align.VERTICALLY_CENTERED, padLeft=8)
        carbonui.TextBody(parent=text_container, align=Align.TOTOP, text=GetByLabel('UI/Corporations/Goals/Creator'), color=TextColor.SECONDARY)
        carbonui.TextBody(parent=text_container, state=eveui.State.normal, align=Align.TOTOP, text=character_link(self.job.creator_id))
        CorpIcon(parent=corporation_container, state=eveui.State.normal, align=eveui.Align.to_left, size=64, padRight=16, corpID=self.job.corporation_id)
        text_container = eveui.ContainerAutoSize(parent=corporation_container, align=carbonui.Align.VERTICALLY_CENTERED, padLeft=8)
        carbonui.TextBody(parent=text_container, state=eveui.State.normal, align=eveui.Align.to_top, text=corporation_link(self.job.corporation_id), maxLines=3)
