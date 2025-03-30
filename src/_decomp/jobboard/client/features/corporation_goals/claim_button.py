#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\corporation_goals\claim_button.py
from corporation.client.goals import goalSignals
from jobboard.client.ui.claim_button import JobRewardClaimButton

class CorporationGoalClaimButton(JobRewardClaimButton):

    def _register(self):
        super(CorporationGoalClaimButton, self)._register()
        goalSignals.on_goal_reward_redeemed.connect(self._on_payment_redeemed)
        goalSignals.on_goal_reward_earned.connect(self._on_goal_updated)
        goalSignals.on_goal_redeem_failed.connect(self._on_payment_failed)

    def _unregister(self):
        super(CorporationGoalClaimButton, self)._unregister()
        goalSignals.on_goal_reward_redeemed.disconnect(self._on_payment_redeemed)
        goalSignals.on_goal_reward_earned.disconnect(self._on_goal_updated)
        goalSignals.on_goal_redeem_failed.disconnect(self._on_payment_failed)
