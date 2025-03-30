#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\travel.py
from nodegraph.client.util import get_item_name
from .base import Condition

def get_navigation_service():
    return sm.GetService('tacticalNavigation')


class Jumping(Condition):
    atom_id = 117

    def validate(self, **kwargs):
        return get_navigation_service().IsJumping()


class Warping(Condition):
    atom_id = 116

    def __init__(self, item_id = None, type_id = None, group_id = None, category_id = None, **kwargs):
        super(Warping, self).__init__(**kwargs)
        self.item_id = item_id
        self.type_id = type_id
        self.group_id = group_id
        self.category_id = category_id

    def validate(self, **kwargs):
        return get_navigation_service().IsWarpingTo(item_id=self.item_id, type_id=self.type_id, group_id=self.group_id, category_id=self.category_id)

    @classmethod
    def get_subtitle(cls, **kwargs):
        return get_item_name(**kwargs)


class Undocking(Condition):
    atom_id = 159

    def validate(self, **kwargs):
        return get_navigation_service().IsUndocking()


class Docking(Condition):
    atom_id = 590

    def validate(self, **kwargs):
        return get_navigation_service().IsDocking()


class DestinationSetToCareerAgentStation(Condition):
    atom_id = 220

    def validate(self, **kwargs):
        return get_navigation_service().IsDestinationSetToCareerAgentStation()


class BallparkLoaded(Condition):
    atom_id = 242

    def validate(self, **kwargs):
        return get_navigation_service().IsBallparkLoaded()
