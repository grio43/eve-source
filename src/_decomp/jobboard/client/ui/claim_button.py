#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\claim_button.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.control.button import Button
from localization import GetByLabel
from jobboard.client import job_board_signals

class JobRewardClaimButton(Button):
    default_display = False
    _has_error = False

    def __init__(self, job, *args, **kwargs):
        self._job = job
        super(JobRewardClaimButton, self).__init__(*args, **kwargs)
        self._update()
        self._register()

    def Close(self):
        self._unregister()
        super(JobRewardClaimButton, self).Close()

    def _register(self):
        job_board_signals.on_job_state_changed.connect(self._on_job_state_changed)

    def _unregister(self):
        job_board_signals.on_job_state_changed.disconnect(self._on_job_state_changed)

    def _on_job_state_changed(self, job):
        if job == self._job:
            self._update()

    def _update(self):
        self.busy = False
        if self._has_error:
            self.label = GetByLabel('UI/Inflight/JumpThroughError')
            self.disable()
            return
        if self._job.has_claimable_rewards:
            self.hint = None
            self.enable()
            self.label = GetByLabel('UI/Generic/Claim')
        else:
            self.set_claimed()

    def set_claimed(self):
        self.disable()
        self.busy = False
        self.label = GetByLabel('UI/Generic/Claimed')

    def start_claim_sequence(self):
        if not self._job.has_claimable_rewards:
            return
        self.busy = True
        self.label = GetByLabel('UI/Insurance/QuoteWindow/InsuringCancelled')

    def flag_error(self):
        self._has_error = True
        self._update()

    def _on_goal_updated(self, goal_id, *args, **kwargs):
        if goal_id != self._job.goal_id:
            return
        self._update()

    def _on_payment_redeemed(self, goal_id, *args, **kwargs):
        if goal_id != self._job.goal_id:
            return
        self.set_claimed()

    def _on_payment_failed(self, goal_id, *args, **kwargs):
        if goal_id != self._job.goal_id:
            return
        self.flag_error()

    def _on_payment_complete(self, goal_id, *args, **kwargs):
        if goal_id != self._job.goal_id:
            return
        PlaySound('claim_button3_play')
