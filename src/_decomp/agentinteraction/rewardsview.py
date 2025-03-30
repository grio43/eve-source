#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\agentinteraction\rewardsview.py
from agentinteraction.reward import RewardType, get_test_rewards
from agentinteraction.rewardcont import RewardTypeCont, BonusRewardTypeCont
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui import TextColor
REWARD_CLASS_BY_TYPE = {RewardType.NORMAL: RewardTypeCont,
 RewardType.BONUS: BonusRewardTypeCont}
REWARD_TYPES = [RewardType.NORMAL, RewardType.BONUS]

class RewardsView(ContainerAutoSize):
    USE_TEST_REWARDS = False

    def ApplyAttributes(self, attributes):
        super(RewardsView, self).ApplyAttributes(attributes)
        self.subcontainer_rewards_by_type = {}
        self.title_color = TextColor.HIGHLIGHT
        self.flow_cont = FlowContainer(name='flow_cont', parent=self, align=uiconst.TOTOP, contentSpacing=(25, 25))
        for reward_type in REWARD_TYPES:
            self.subcontainer_rewards_by_type[reward_type] = None

    def update_normal_rewards(self, rewards):
        if self.USE_TEST_REWARDS:
            rewards = get_test_rewards()
        self._update_rewards(rewards, RewardType.NORMAL)

    def update_bonus_rewards(self, rewards):
        if self.USE_TEST_REWARDS:
            rewards = get_test_rewards()
        self._update_rewards(rewards, RewardType.BONUS)

    def clear_rewards(self):
        for reward_type, cont in self.subcontainer_rewards_by_type.iteritems():
            if cont and not cont.destroyed:
                cont.clear_current_rewards()

    def _update_rewards(self, rewards, reward_type):
        reward_cont = self.subcontainer_rewards_by_type[reward_type]
        current_rewards = reward_cont.get_current_rewards() if reward_cont else set()
        new_rewards = set([ (reward.type_id, reward.reward_type) for reward in rewards ])
        if new_rewards != current_rewards:
            reward_cont = self._build_reward_type_container(reward_type)
            self._clear_container(container=reward_cont)
            reward_cont.add_rewards(rewards, reward_type)

    def _build_reward_type_container(self, reward_type):
        cont = self.subcontainer_rewards_by_type[reward_type]
        if not cont or cont.destroyed:
            reward_cont_class = REWARD_CLASS_BY_TYPE[reward_type]
            cont = reward_cont_class(name='subcontainer_%s_rewards' % reward_type, parent=self.flow_cont, align=uiconst.TOPLEFT, reward_type=reward_type, title_color=self.title_color)
        self.subcontainer_rewards_by_type[reward_type] = cont
        return cont

    def _clear_container(self, container):
        if isinstance(container, RewardTypeCont) and not getattr(container, 'destroyed', False):
            container.flush_content()
