#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\object.py
from carbon.common.script.util.format import FmtDist
from npcs.client.entitystandings import is_hostile_npc_target
from inventorycommon.const import categoryEntity
from nodegraph.client.util import get_slim_item_kwargs, get_slim_item_by_dungeon_object_id, get_ball_ids_by_distance, get_item_name
from .base import GetterAtom

class GetDungeonObject(GetterAtom):
    atom_id = 183

    def __init__(self, dungeon_object_id = None, **kwargs):
        self.dungeon_object_id = dungeon_object_id

    def get_values(self):
        slim_item = get_slim_item_by_dungeon_object_id(self.dungeon_object_id)
        if slim_item:
            return get_slim_item_kwargs(slim_item=slim_item)

    @classmethod
    def get_subtitle(cls, dungeon_object_id = None, **kwargs):
        return str(cls.get_atom_parameter_value('dungeon_object_id', dungeon_object_id, ''))


class GetSlimItem(GetterAtom):
    atom_id = 309

    def __init__(self, item_id = None, **kwargs):
        self.item_id = item_id

    def get_values(self):
        return get_slim_item_kwargs(item_id=self.item_id)

    @classmethod
    def get_subtitle(cls, item_id = None, **kwargs):
        return str(item_id)


class GetSlimItems(GetterAtom):
    atom_id = 532

    def __init__(self, type_id = None, group_id = None, category_id = None, entity_group_id = None, **kwargs):
        self.type_id = type_id
        self.group_id = group_id
        self.category_id = category_id
        self.entity_group_id = entity_group_id

    def get_values(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            return None
        if self.type_id:
            predicate = ballpark.GetBallPredicate('typeID', self.type_id)
        elif self.group_id:
            predicate = ballpark.GetBallPredicate('groupID', self.group_id)
        elif self.category_id:
            predicate = ballpark.GetBallPredicate('categoryID', self.category_id)
        elif self.entity_group_id:
            predicate = ballpark.GetBallPredicate('entityGroupID', self.entity_group_id)
        else:
            return None
        slim_items = []
        item_ids = []
        for ball_id in ballpark.balls.iterkeys():
            if ball_id == session.shipid:
                continue
            if predicate and not predicate(ball_id):
                continue
            item_ids.append(ball_id)
            slim_items.append(ballpark.GetInvItem(ball_id))

        return {'slim_items': slim_items,
         'item_ids': item_ids}

    @classmethod
    def get_subtitle(cls, entity_group_id = None, **kwargs):
        if entity_group_id:
            return 'entity_group_id: {}'.format(entity_group_id)
        return get_item_name(**kwargs)


class GetHostileTargets(GetterAtom):
    atom_id = 540

    def get_values(self, **kwargs):
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            return
        slim_items = []
        item_ids = []
        for ball_id in ballpark.balls.iterkeys():
            if ball_id == session.shipid:
                continue
            slim_item = ballpark.GetInvItem(ball_id)
            if getattr(slim_item, 'categoryID', None) != categoryEntity:
                continue
            if not is_hostile_npc_target(slim_item):
                continue
            item_ids.append(ball_id)
            slim_items.append(slim_item)

        return {'slim_items': slim_items,
         'item_ids': item_ids}


class GetBall(GetterAtom):
    atom_id = 417

    def __init__(self, item_id = None, wait_for_model = None, **kwargs):
        self.item_id = item_id
        self.wait_for_model = self.get_atom_parameter_value('wait_for_model', wait_for_model)

    def get_values(self):
        if not self.item_id:
            return None
        if self.wait_for_model:
            ball = sm.GetService('michelle').GetBallAndWaitForModel(self.item_id)
        else:
            ball = sm.GetService('michelle').GetBall(self.item_id)
        return {'ball': ball}

    @classmethod
    def get_subtitle(cls, wait_for_model = None, **kwargs):
        if cls.get_atom_parameter_value('wait_for_model', wait_for_model):
            return 'Wait for model'
        return ''


class FindClosestObject(GetterAtom):
    atom_id = 182

    def __init__(self, distance = None, type_id = None, group_id = None, category_id = None, **kwargs):
        self.distance = self.get_atom_parameter_value('distance', distance)
        self.type_id = type_id
        self.group_id = group_id
        self.category_id = category_id

    def get_values(self):
        ball_ids_by_distance = get_ball_ids_by_distance(distance=self.distance, type_id=self.type_id, group_id=self.group_id, category_id=self.category_id)
        if ball_ids_by_distance:
            _, ball_id = ball_ids_by_distance[0]
            return get_slim_item_kwargs(item_id=ball_id)

    @classmethod
    def get_subtitle(cls, distance = None, **kwargs):
        name = get_item_name(**kwargs)
        if name:
            return u'{} - {}'.format(FmtDist(cls.get_atom_parameter_value('distance', distance, 0)), name)
        else:
            return ''


class GetDogmaAttribute(GetterAtom):
    atom_id = 373

    def __init__(self, attribute_id = None, item_id = None, type_id = None, **kwargs):
        self.attribute_id = attribute_id
        self.item_id = item_id
        self.type_id = type_id

    def get_values(self, **kwargs):
        import dogma.data as dogma_data
        if self.item_id:
            attribute_name = dogma_data.get_attribute_name(self.attribute_id)
            value = sm.GetService('godma').GetStateManager().GetAttribute(self.item_id, attribute_name)
        elif self.type_id:
            value = dogma_data.get_type_attribute_or_default(self.type_id, self.attribute_id)
        else:
            return
        return {'value': value}

    @classmethod
    def get_subtitle(cls, attribute_id = None, **kwargs):
        if not attribute_id:
            return ''
        import dogma.data as dogma_data
        return u'{} ({})'.format(dogma_data.get_attribute_name(attribute_id), dogma_data.get_attribute_display_name(attribute_id))


class GetDogmaEffects(GetterAtom):
    atom_id = 518

    def __init__(self, type_id = None, **kwargs):
        self.type_id = type_id

    def get_values(self, **kwargs):
        if not self.type_id:
            return
        import dogma.data as dogma_data
        return {'effect_ids': dogma_data.get_type_effect_ids(self.type_id)}

    @classmethod
    def get_subtitle(cls, **kwargs):
        return get_item_name(**kwargs)
