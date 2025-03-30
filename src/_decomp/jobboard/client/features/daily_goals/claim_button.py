#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\claim_button.py
from carbonui import ButtonStyle
from localization import GetByLabel
from dailygoals.client import goalSignals
from dailygoals.client.featureFlag import are_daily_goal_payments_enabled
from dailygoals.client.goalSignals import on_payment_availability_changed
from jobboard.client.ui.claim_button import JobRewardClaimButton
from jobboard.client.ui.util import select_redeem_location

class DailyGoalClaimButton(JobRewardClaimButton):
    default_display = False
    default_style = ButtonStyle.SUCCESS

    def __init__(self, job, *args, **kwargs):
        self.default_func = self._on_click
        super(DailyGoalClaimButton, self).__init__(job, *args, **kwargs)

    def _register(self):
        super(DailyGoalClaimButton, self)._register()
        on_payment_availability_changed.connect(self._on_flag_changed)
        goalSignals.on_goal_payment_redeemed.connect(self._on_payment_redeemed)
        goalSignals.on_goal_payment_earned.connect(self._on_goal_updated)
        goalSignals.on_goal_payment_failed.connect(self._on_payment_failed)
        goalSignals.on_goal_payment_complete.connect(self._on_payment_complete)

    def _unregister(self):
        super(DailyGoalClaimButton, self)._unregister()
        on_payment_availability_changed.disconnect(self._on_flag_changed)
        goalSignals.on_goal_payment_redeemed.disconnect(self._on_payment_redeemed)
        goalSignals.on_goal_payment_earned.disconnect(self._on_goal_updated)
        goalSignals.on_goal_payment_failed.disconnect(self._on_payment_failed)
        goalSignals.on_goal_payment_complete.disconnect(self._on_payment_complete)

    def _update(self):
        self.busy = False
        if self._has_error:
            self.label = GetByLabel('UI/Inflight/JumpThroughError')
            self.disable()
            return
        if self._job.is_completed:
            self.Show()
        else:
            self.Hide()
        if not are_daily_goal_payments_enabled():
            self.hint = GetByLabel('UI/Corporations/Goals/ClaimUnavailable')
            self.disable()
            return
        self.hint = None
        self.enable()
        if not self._job.has_claimable_rewards:
            self.set_claimed()
        else:
            self.label = GetByLabel('UI/Generic/Claim')
            self.enable()

    def _on_click(self, *args):
        if self._job.has_claimable_item_reward:
            should_claim = select_redeem_location([self._job])
            if not should_claim:
                return
        if self._job.is_trackable and self._job.is_tracked:
            self._job.remove_tracked()
        self.start_claim_sequence()
        self._job.claim_rewards()

    def _on_flag_changed(self, *args):
        self._update()
