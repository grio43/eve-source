#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\corporation_goals\claimable_reward_button.py
import uthread
import uthread2
import inspect
from eveformat import currency
from carbonui import ButtonStyle, ButtonVariant
from carbonui.control.button import Button
import localization
from corporation.client.goals.featureFlag import are_corporation_goal_payments_enabled
from corporation.client.goals.goalSignals import on_payment_availability_changed

class ClaimableRewardControllerStub(object):

    def claim_reward(self, job):
        job.claim_rewards()


class ClaimableRewardButton(Button):

    def __init__(self, job, controller, tooltipCls, *args, **kwargs):
        self._job = job
        self._controller = controller
        self._tooltipCls = tooltipCls
        self.default_func = self._on_click
        self.default_variant = ButtonVariant.PRIMARY
        self.default_style = ButtonStyle.SUCCESS
        self.claim_thread = None
        super(ClaimableRewardButton, self).__init__(*args, **kwargs)
        self._update()
        self._job.on_job_updated.connect(self._update)
        on_payment_availability_changed.connect(self._on_payment_changed)

    def Close(self):
        if self._job:
            self._job.on_job_updated.disconnect(self._update)
        super(ClaimableRewardButton, self).Close()

    def _on_payment_changed(self, *args, **kwargs):
        self._update()

    def _update(self):
        if self.busy:
            return
        if self._job.has_claimable_rewards:
            if self._job.is_completed:
                self.style = ButtonStyle.SUCCESS
            else:
                self.style = ButtonStyle.NORMAL
            self.label = localization.GetByLabel('UI/Corporations/Goals/ClaimValue', rewardValue=currency.isk(self._job.unclaimed_amount))
            if not are_corporation_goal_payments_enabled():
                self.disable()
            elif self.disabled:
                self.enable()
            self.Show()
        else:
            self.Hide()

    def _on_click(self, *args, **kwargs):
        if self.busy:
            return
        self.busy = True
        self.disabled = True
        self.claim_thread = uthread2.start_tasklet(self._claim_sequence)

    def _claim_sequence(self):
        uthread.parallel([(self._controller.claim_reward, (self._job,)), (uthread2.sleep, (1.5,))])
        self.busy = False
        self.disabled = False
        self._update()

    def ConstructTooltipPanel(self):
        return self._tooltipCls(job=self._job)
