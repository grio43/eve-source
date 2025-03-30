#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\atoms\conditions\compare.py
from nodegraph.common.util import compare_values
from .base import ConditionAtom

class CompareValues(ConditionAtom):
    atom_id = 308

    def __init__(self, value_a = None, value_b = None, operator = None, flipped = None, **kwargs):
        super(CompareValues, self).__init__(**kwargs)
        self.value_a = value_a
        self.value_b = value_b
        self.operator = self.get_atom_parameter_value('operator', operator)
        self.flipped = self.get_atom_parameter_value('flipped', flipped)

    def validate(self, **kwargs):
        return compare_values(value_a=self.value_a, value_b=self.value_b, operator=self.operator, flipped=self.flipped)

    @classmethod
    def get_subtitle(cls, value_a = '', value_b = '', operator = None, flipped = None, **kwargs):
        return u'{} {} {} {}'.format(value_a, cls.get_atom_parameter_value('operator', operator), value_b, '(flipped)' if cls.get_atom_parameter_value('flipped', flipped) else '')


class Parameter(ConditionAtom):
    atom_id = 34

    def __init__(self, parameter_key = None, parameter_value = None, operator = None, flipped = None, **kwargs):
        super(Parameter, self).__init__(**kwargs)
        self.parameter_key = parameter_key
        self.parameter_value = parameter_value
        self.operator = self.get_atom_parameter_value('operator', operator)
        self.flipped = self.get_atom_parameter_value('flipped', flipped)

    def validate(self, **kwargs):
        if self.parameter_key not in kwargs:
            return False
        value = kwargs.get(self.parameter_key, None)
        return compare_values(value_a=value, value_b=self.parameter_value, operator=self.operator, flipped=self.flipped)

    @classmethod
    def get_subtitle(cls, parameter_key = '', parameter_value = '', operator = None, **kwargs):
        if parameter_key:
            return u'{} {} {}'.format(parameter_key, cls.get_atom_parameter_value('operator', operator), parameter_value)
        return ''
