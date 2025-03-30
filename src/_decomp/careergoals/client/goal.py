#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\careergoals\client\goal.py
from careergoals.client.goal_definition import GoalDefinition

class Goal(object):

    def __init__(self, definition, progress, completed, claim_state_per_reward_label):
        self._definition = definition
        self._progress = progress
        self._completed = completed
        self._claim_state_per_reward_label = claim_state_per_reward_label

    def mark_local_completed(self):
        self._progress = self.definition.target_value

    def mark_local_reward_label_claimed(self, reward_label):
        self._claim_state_per_reward_label[reward_label] = True

    def update_local_progress(self, progress):
        self._progress = progress

    def is_completed(self):
        return self._completed or self._progress >= self.definition.target_value

    def has_unclaimed_rewards(self):
        return self.is_completed() and any((x is False for x in self._claim_state_per_reward_label.itervalues()))

    def is_reward_claimed(self, reward):
        return self._claim_state_per_reward_label.get(reward.reward_label, True)

    def get_unclaimed_rewards(self):
        return [ x for x in self.definition.rewards if not self.is_reward_claimed(x) ]

    def get_unclaimed_reward_labels(self):
        return [ x for x, y in self._claim_state_per_reward_label.iteritems() if y is False ]

    @property
    def goal_id(self):
        return self.definition.goal_id

    @property
    def definition(self):
        return self._definition

    @property
    def progress(self):
        return self._progress

    @property
    def claim_state_per_reward_label(self):
        if not self.is_completed():
            return {}
        return self._claim_state_per_reward_label
