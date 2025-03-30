#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\attribute.py
from nodegraph.common.util import compare_values
from .base import Condition

class SlimItemAttribute(Condition):
    atom_id = 171

    def __init__(self, item_id = None, attribute_key = None, attribute_value = None, operator = None, flipped = None, **kwargs):
        super(SlimItemAttribute, self).__init__(**kwargs)
        self.item_id = item_id
        self.attribute_key = attribute_key
        self.attribute_value = attribute_value
        self.operator = self.get_atom_parameter_value('operator', operator)
        self.flipped = self.get_atom_parameter_value('flipped', flipped)

    def validate(self, **kwargs):
        item = sm.StartService('michelle').GetItem(self.item_id)
        if not item:
            return False
        return compare_values(value_a=getattr(item, self.attribute_key) or None, value_b=self.attribute_value, operator=self.operator, flipped=self.flipped)

    @classmethod
    def get_subtitle(cls, attribute_key = '', attribute_value = '', operator = None, flipped = None, **kwargs):
        if attribute_key:
            return u'{} {} {} {}'.format(attribute_key, cls.get_atom_parameter_value('operator', operator), attribute_value, '(flipped)' if cls.get_atom_parameter_value('flipped', flipped) else '')
        return ''
