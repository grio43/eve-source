#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\inrange.py
from carbon.common.script.util.format import FmtDist
from nodegraph.client.util import get_item_name
from .base import Condition

class InRange(Condition):
    atom_id = 18

    def __init__(self, distance = None, item_id = None, **kwargs):
        super(InRange, self).__init__(**kwargs)
        self.distance = self.get_atom_parameter_value('distance', distance)
        self.item_id = item_id

    def validate(self, **kwargs):
        try:
            distance = sm.GetService('target').GetDistanceToTarget(self.item_id)
            return distance <= self.distance
        except:
            return False

    @classmethod
    def get_subtitle(cls, distance = None, **kwargs):
        return FmtDist(cls.get_atom_parameter_value('distance', distance))


class InTargetingRange(InRange):
    atom_id = 19

    def __init__(self, item_id = None, **kwargs):
        super(InTargetingRange, self).__init__(**kwargs)
        self.item_id = item_id

    def validate(self, **kwargs):
        self.distance = sm.GetService('target').GetMaxTargetRange()
        if self.distance is None:
            return False
        return super(InTargetingRange, self).validate(**kwargs)

    @classmethod
    def get_subtitle(cls, **kwargs):
        return ''
