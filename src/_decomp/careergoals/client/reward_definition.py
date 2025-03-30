#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\careergoals\client\reward_definition.py
import logging
from careergoals.client.const import RewardType, RewardLabel
from utillib import KeyVal
logger = logging.getLogger(__name__)
VGS_ENTIRE_STORE_CATALOGUE = 5
VGS_GLOBAL_OFFER = 'globalCcpOfferId'
VGS_TAG = 'CareerPortal'

class RewardDefinition(object):

    def __init__(self, reward_type, reward_label, quantity):
        self._reward_type = reward_type
        self._quantity = quantity
        self._reward_label = reward_label

    @property
    def reward_type(self):
        return self._reward_type

    @property
    def reward_label(self):
        return self._reward_label

    @property
    def is_omega(self):
        return self._reward_label == RewardLabel.OMEGA

    @property
    def quantity(self):
        return self._quantity

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.reward_label == other.reward_label and self.reward_type == other.reward_type and self.quantity == other.quantity

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return 'Type %s, Quantity %s, Label %s' % (self._reward_type, self._quantity, self._reward_label)


class RewardDefinitionTypeID(RewardDefinition):

    def __init__(self, reward_type, reward_label, quantity, type_id):
        super(RewardDefinitionTypeID, self).__init__(reward_type, reward_label, quantity)
        self._type_id = type_id

    @property
    def type_id(self):
        return self._type_id

    def __eq__(self, other):
        return super(RewardDefinitionTypeID, self).__eq__(other) and self.type_id == other.type_id

    def __str__(self):
        return '%s, Type ID %s' % (super(RewardDefinitionTypeID, self).__str__(), self.type_id)

    @staticmethod
    def build_from_legacy_reward(legacy_rewards, legacy_reward_id):
        offer = legacy_rewards.get_reward(legacy_reward_id)
        if offer is not None:
            rewards = [ KeyVal(x) for x in offer['products'] ]
        else:
            logger.error('could not find legacy reward id %s for career goal reward definitions' % legacy_reward_id)
            rewards = []
        return [ RewardDefinitionTypeID(RewardType.TYPE_ID, RewardLabel.ALPHA, r.quantity, r.typeId) for r in rewards ]


class LegacyRewards(object):

    def __init__(self):
        self._career_portal_rewards = {}

    def get_rewards_from_server(self):
        store_catalogue = sm.RemoteSvc('storeManager').get_offers(VGS_ENTIRE_STORE_CATALOGUE, VGS_TAG)
        if not store_catalogue:
            return
        for offer_json in store_catalogue:
            legacy_reward_id = str(offer_json.get(VGS_GLOBAL_OFFER, None))
            if not legacy_reward_id:
                continue
            self._career_portal_rewards[legacy_reward_id] = offer_json

    def get_reward(self, legacy_reward_id):
        return self._career_portal_rewards.get(legacy_reward_id, None)

    def has_rewards(self):
        return len(self._career_portal_rewards) > 0
