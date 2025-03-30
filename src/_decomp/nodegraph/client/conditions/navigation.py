#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\navigation.py
import abc
from nodegraph.client.util import get_item_name
from .base import Condition

def get_navigation_service():
    return sm.GetService('tacticalNavigation')


class NavigationCondition(Condition):
    __metaclass__ = abc.ABCMeta
    atom_id = None

    def __init__(self, item_id = None, type_id = None, group_id = None, category_id = None, owner_id = None, dungeon_object_id = None, **kwargs):
        super(NavigationCondition, self).__init__(**kwargs)
        self.item_id = item_id
        self.type_id = type_id
        self.group_id = group_id
        self.category_id = category_id
        self.owner_id = owner_id
        self.dungeon_object_id = dungeon_object_id

    @abc.abstractmethod
    def _get_validation_check(self):
        pass

    def validate(self, **kwargs):
        validation_check = self._get_validation_check()
        return validation_check(item_id=self.item_id, type_id=self.type_id, group_id=self.group_id, category_id=self.category_id, owner_id=self.owner_id, dungeon_object_id=self.dungeon_object_id)

    @classmethod
    def get_subtitle(cls, **kwargs):
        if not kwargs:
            return ''
        if 'owner_id' in kwargs:
            try:
                owner = cfg.eveowners.Get(kwargs['owner_id'])
                return owner.name
            except KeyError:
                return u'Owner: {}'.format(kwargs['owner_id'])

        if 'dungeon_object_id' in kwargs:
            return u'Dungeon object: {}'.format(kwargs['dungeon_object_id'])
        return get_item_name(**kwargs)


class Approaching(NavigationCondition):
    atom_id = 112

    def _get_validation_check(self):
        return get_navigation_service().IsApproachingTarget


class KeepAtRange(NavigationCondition):
    atom_id = 414

    def _get_validation_check(self):
        return get_navigation_service().IsKeepingTargetAtRange


class Orbiting(NavigationCondition):
    atom_id = 113

    def _get_validation_check(self):
        return get_navigation_service().IsOrbitingTarget


class MovingTowards(NavigationCondition):
    atom_id = 114

    def _get_validation_check(self):
        return get_navigation_service().IsMovingTowardsTarget


class MovingTowardsPoint(Condition):
    atom_id = 115

    def validate(self, **kwargs):
        return get_navigation_service().IsMovingTowardsPoint()


class Aligning(Condition):
    atom_id = 356

    def validate(self, **kwargs):
        return get_navigation_service().IsAligning()


class ShipStopped(Condition):
    atom_id = 345

    def validate(self, **kwargs):
        return get_navigation_service().IsStopped()
