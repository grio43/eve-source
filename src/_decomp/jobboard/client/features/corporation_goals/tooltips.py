#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\corporation_goals\tooltips.py
from carbonui import TextColor
from corporation.client.goals.featureFlag import are_corporation_goal_payments_enabled
from eve.client.script.ui.control.tooltips import TooltipPanel
from eveformat import currency, number
from localization import GetByLabel

class GoalRewardToolTip(TooltipPanel):

    def ApplyAttributes(self, attributes):
        super(GoalRewardToolTip, self).ApplyAttributes(attributes)
        self._job = attributes.job
        self.LoadGeneric1ColumnTemplate()
        if are_corporation_goal_payments_enabled():
            self.first_label = self.AddTextDetailsLabel(color=TextColor.SECONDARY)
            self.first_value = self.AddTextBodyLabel()
            self.second_label = self.AddTextDetailsLabel(color=TextColor.SECONDARY)
            self.second_value = self.AddTextBodyLabel()
            self.AddDivider()
            self.third_label = self.AddTextDetailsLabel(color=TextColor.SECONDARY)
            self.third_value = self.AddTextBodyLabel()
        else:
            self.unclaimable_lable = self.AddTextBodyLabel()
        self.UpdateLabelText()
        self._job.on_job_updated.connect(self.UpdateLabelText)

    def Close(self, *args):
        if self._job:
            self._job.on_job_updated.disconnect(self.UpdateLabelText)
        super(GoalRewardToolTip, self).Close(*args)

    def UpdateLabelText(self):
        if not are_corporation_goal_payments_enabled():
            self.unclaimable_lable.text = GetByLabel('UI/Corporations/Goals/ClaimUnavailable')
        else:
            self.first_label.text = GetByLabel('UI/Corporations/Goals/ClaimedTooltipBreakdown')
            self.first_value.text = currency.isk(self._job.claimed_amount, fraction=True)
            self.second_label.text = GetByLabel('UI/Corporations/Goals/UnclaimedTooltipBreakdown')
            self.second_value.text = currency.isk(self._job.unclaimed_amount, fraction=True)
            is_ship_insurance = self._job.is_ship_insurance()
            third_label_path = 'UI/Corporations/Goals/TotalCompensationTooltipBreakdown' if is_ship_insurance else 'UI/Corporations/Goals/TotalEarnedTooltipBreakdown'
            self.third_label.text = GetByLabel(third_label_path)
            self.third_value.text = currency.isk(self._job.earned_amount, fraction=True)


class TotalRewardToolTip(GoalRewardToolTip):

    def ApplyAttributes(self, attributes):
        super(TotalRewardToolTip, self).ApplyAttributes(attributes)

    def UpdateLabelText(self):
        reward_amount_per_contribution = self._job.reward_amount_per_contribution
        self.first_label.text = GetByLabel('UI/Corporations/Goals/TotalRewardsTooltipBreakdown')
        self.first_value.text = currency.isk(self._job.target_progress * reward_amount_per_contribution, fraction=True)
        is_ship_insurance = self._job.is_ship_insurance()
        second_label_path = 'UI/Corporations/Goals/TotalCompensatedToAllTooltipBreakdown' if is_ship_insurance else 'UI/Corporations/Goals/TotalEarnedByAllTooltipBreakdown'
        self.second_label.text = GetByLabel(second_label_path)
        self.second_value.text = currency.isk(self._job.current_progress * reward_amount_per_contribution, fraction=True)
        third_label_path = 'UI/Corporations/Goals/TotalCompensationRemainingTooltipBreakdown' if is_ship_insurance else 'UI/Corporations/Goals/TotalISKRemainingTooltipBreakdown'
        self.third_label.text = GetByLabel(third_label_path)
        self.third_value.text = currency.isk(self._job.get_isk_payout_remaining(), fraction=True)


class AvailableRewardsTooltip(TooltipPanel):

    def ApplyAttributes(self, attributes):
        super(AvailableRewardsTooltip, self).ApplyAttributes(attributes)
        job = attributes.job
        self.LoadGeneric1ColumnTemplate()
        self.SetSpacing(cellSpacing=(0, 0))
        if job.participation_limit:
            self.AddTextBodyLabel(text=GetByLabel('UI/Corporations/Goals/AmountAvailableToYou'), color=TextColor.SECONDARY)
            self.AddTextHeaderLabel(text=currency.isk(job.get_my_isk_payout_remaining()))
            self.AddTextDetailsLabel(text=currency.isk_readable(job.get_my_isk_payout_remaining()), color=TextColor.DISABLED)
            self.AddSpacer(height=16)
        self.AddTextBodyLabel(text=GetByLabel('UI/Corporations/Goals/ISKAvailableInProject'), color=TextColor.SECONDARY)
        self.AddTextHeaderLabel(text=currency.isk(job.get_isk_payout_remaining()), color=TextColor.NORMAL)
        self.AddTextDetailsLabel(text=currency.isk_readable(job.get_isk_payout_remaining()), color=TextColor.DISABLED)


class ProgressTooltip(TooltipPanel):

    def ApplyAttributes(self, attributes):
        super(ProgressTooltip, self).ApplyAttributes(attributes)
        job = attributes.job
        self.LoadGeneric1ColumnTemplate()
        if job.participation_limit:
            self.AddTextBodyLabel(text=GetByLabel('UI/Corporations/Goals/ContributionLimitTooltip'), color=TextColor.DISABLED)
        self.AddTextBodyLabel(text=GetByLabel('UI/Corporations/Goals/OverallProgress' if not job.is_ship_insurance() else 'UI/Corporations/Goals/OverallCoverage', progress=number(job.current_progress, decimal_places=0), total=number(job.desired_progress, decimal_places=0), percentage=int(job.progress_percentage * 100), labelColor=TextColor.SECONDARY, percentageColor=TextColor.DISABLED))
        self.AddTextBodyLabel(text=GetByLabel('UI/Corporations/Goals/YourProgress' if not job.is_ship_insurance() else 'UI/Corporations/Goals/YourCompensation', progress=number(job.personal_progress, decimal_places=0), total=number(job.personal_progress_limit, decimal_places=0), percentage=int(job.personal_progress_percentage * 100), labelColor=TextColor.SECONDARY, percentageColor=TextColor.DISABLED))


class ClaimableRewardsTooltip(TooltipPanel):

    def __init__(self, job):
        self._job = job
        super(ClaimableRewardsTooltip, self).__init__()

    def ApplyAttributes(self, attributes):
        super(ClaimableRewardsTooltip, self).ApplyAttributes(attributes)
        self.LoadGeneric1ColumnTemplate()
        self.AddTextBodyLabel(text=GetByLabel('UI/Common/UnclaimedRewardShort'), color=TextColor.SECONDARY)
        self.AddTextHeaderLabel(text=currency.isk(self._job.unclaimed_amount), color=TextColor.SUCCESS)
        self.AddTextDetailsLabel(text=currency.isk_readable(self._job.unclaimed_amount), color=TextColor.DISABLED)


class CoverageRatioTooltip(TooltipPanel):

    def __init__(self, job):
        self._job = job
        super(CoverageRatioTooltip, self).__init__()

    def ApplyAttributes(self, attributes):
        super(CoverageRatioTooltip, self).ApplyAttributes(attributes)
        self.LoadGeneric1ColumnTemplate()
        self.AddTextBodyLabel(text=GetByLabel('UI/Corporations/Goals/ShipInsuranceCoverageRatioShort'))
