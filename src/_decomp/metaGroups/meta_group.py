#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\metaGroups\meta_group.py
from .data import exists, get_name, get_description, get_icon_id, iter_meta_group_ids

class MetaGroup(int):

    def __new__(cls, meta_group_id, validate = True):
        if validate and not exists(meta_group_id):
            raise ValueError('Meta group with id {} does not exist'.format(meta_group_id))
        return int.__new__(cls, meta_group_id)

    @property
    def id(self):
        return int(self)

    @property
    def name(self):
        return get_name(self.id)

    @property
    def description(self):
        return get_description(self.id)

    @property
    def icon_id(self):
        return get_icon_id(self.id)

    def __repr__(self):
        for attribute_name in dir(self):
            if attribute_name.startswith('_'):
                continue
            attribute = getattr(self, attribute_name)
            if getattr(attribute, 'id', None) == self.id:
                return 'MetaGroup.{}(meta_group_id={})'.format(attribute_name, self.id)

        return 'MetaGroup(meta_group_id={})'.format(self.id)


MetaGroup.abyssal = MetaGroup(15, validate=False)
MetaGroup.deadspace = MetaGroup(6, validate=False)
MetaGroup.faction = MetaGroup(4, validate=False)
MetaGroup.limited_time = MetaGroup(19, validate=False)
MetaGroup.officer = MetaGroup(5, validate=False)
MetaGroup.premium = MetaGroup(17, validate=False)
MetaGroup.storyline = MetaGroup(3, validate=False)
MetaGroup.structure_faction = MetaGroup(52, validate=False)
MetaGroup.structure_tech_1 = MetaGroup(54, validate=False)
MetaGroup.structure_tech_2 = MetaGroup(53, validate=False)
MetaGroup.tech_1 = MetaGroup(1, validate=False)
MetaGroup.tech_2 = MetaGroup(2, validate=False)
MetaGroup.tech_3 = MetaGroup(14, validate=False)

def iter_meta_groups():
    for meta_group_id in iter_meta_group_ids():
        yield MetaGroup(meta_group_id)
