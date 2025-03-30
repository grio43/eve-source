#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\client\goals\goalReward.py
import eveicon
import eveformat

class CorpGoalReward(object):

    def __init__(self, asset_id, amount_per_unit):
        self._asset_id = asset_id
        self._amount_per_unit = amount_per_unit
        self.earned_capacity = 0
        self.unclaimed_capacity = 0

    @property
    def claimable_amount(self):
        return self.unclaimed_capacity * self._amount_per_unit

    @property
    def earned_amount(self):
        return self.earned_capacity * self._amount_per_unit

    @property
    def redeemed_amount(self):
        return max(0, (self.earned_capacity - self.unclaimed_capacity) * self._amount_per_unit)

    @property
    def amount_per_unit(self):
        return self._amount_per_unit

    @property
    def icon(self):
        return eveicon.isk

    @property
    def asset_id(self):
        return self._asset_id

    @property
    def reward_type(self):
        return 'ISK'

    @property
    def amount_text(self):
        return eveformat.number(self.claimable_amount)
