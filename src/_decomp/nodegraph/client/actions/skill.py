#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\skill.py
from nodegraph.client.util import get_item_name
from .base import Action

class AddToSkillQueue(Action):
    atom_id = 585

    def __init__(self, type_id = None, **kwargs):
        super(AddToSkillQueue, self).__init__(**kwargs)
        self.type_id = type_id

    def start(self, **kwargs):
        super(AddToSkillQueue, self).start(**kwargs)
        sm.GetService('skillqueue').AddSkillToQueue(self.type_id)

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        return get_item_name(type_id=type_id)
