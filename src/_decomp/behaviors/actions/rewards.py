#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\rewards.py
from behaviors.tasks import Task
from npcs.server.rewards.rewards import GroupRewardData
from npcs.server.rewards.rewardspayment import RewardsPayment

class RegisterPaymentOnExplosion(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        rewards_payment = self._get_rewards_payment()
        rewards_payment.register_payment_on_explosion()
        rewards_payment.register_wreck_loot_rights_on_explosion()

    def _get_rewards_payment(self):
        return RewardsPayment(self.context.myItemId, self.context.ballpark, self.context.myBall.newBubbleId, self.context.entityLocation.event_handler_registry, self._get_group_reward_data())

    def _get_group_reward_data(self):
        return GroupRewardData(self.context.ballpark.solarsystemID, reward_id=self.attributes.rewardId, tale_id=self._get_my_tale_id(), dungeon_id=self._get_my_dungeon_id())

    def _get_my_tale_id(self):
        return getattr(self.context, 'myTaleId', 0)

    def _get_my_dungeon_id(self):
        return getattr(self.context, 'dungeonID', 0)
