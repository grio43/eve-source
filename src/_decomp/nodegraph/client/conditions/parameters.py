#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\parameters.py
from .base import Condition
from nodegraph.client.util import get_item_type_kwargs, get_slim_item_kwargs, get_item_name

class ItemParameters(Condition):
    atom_id = None

    def __init__(self, item_id = None, type_id = None, group_id = None, category_id = None, **kwargs):
        super(ItemParameters, self).__init__(**kwargs)
        self.item_id = item_id
        self.type_id = type_id
        self.group_id = group_id
        self.category_id = category_id

    def validate(self, **kwargs):
        if self.item_id:
            return self.item_id == kwargs.get('item_id')
        item_type_kwargs = get_item_type_kwargs(type_id=kwargs.get('type_id'), item_id=kwargs.get('item_id'))
        return self._validate_item(item_type_kwargs)

    def _validate_item(self, params):
        if self.type_id:
            return self.type_id == params.get('type_id')
        if self.group_id:
            return self.group_id == params.get('group_id')
        if self.category_id:
            return self.category_id == params.get('category_id')
        return True

    @classmethod
    def get_subtitle(cls, **kwargs):
        return get_item_name(**kwargs)


class SlimItemParameters(ItemParameters):
    atom_id = 98

    def __init__(self, owner_id = None, dungeon_object_id = None, **kwargs):
        super(SlimItemParameters, self).__init__(**kwargs)
        self.owner_id = owner_id
        self.dungeon_object_id = dungeon_object_id

    def validate(self, **kwargs):
        if self.item_id:
            return self.item_id == kwargs.get('item_id')
        if self.owner_id:
            return self.owner_id == kwargs.get('owner_id')
        if self.dungeon_object_id:
            return self.dungeon_object_id == kwargs.get('dungeon_object_id')
        return self._validate_item(get_slim_item_kwargs(slim_item=kwargs.get('slim_item'), item_id=kwargs.get('item_id')))

    @classmethod
    def get_subtitle(cls, **kwargs):
        if not kwargs:
            return ''
        if 'owner_id' in kwargs:
            owner = cfg.eveowners.Get(kwargs['owner_id'])
            if owner:
                return owner.name
            else:
                return u'Owner: {}'.format(kwargs['owner_id'])
        if 'dungeon_object_id' in kwargs:
            return u'Dungeon object: {}'.format(kwargs['dungeon_object_id'])
        return super(SlimItemParameters, cls).get_subtitle(**kwargs)
