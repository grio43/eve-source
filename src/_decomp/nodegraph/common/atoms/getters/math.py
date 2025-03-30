#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\atoms\getters\math.py
import random
from ast import literal_eval
from .base import GetterAtom

class MathOperation(GetterAtom):

    def __init__(self, value_a = None, value_b = None, **kwargs):
        self.value_a = self.get_atom_parameter_value('value_a', value_a)
        self.value_b = self.get_atom_parameter_value('value_b', value_b)

    def get_values(self):
        return {'value': self.compute()}

    def compute(self):
        return None


class MathAddition(MathOperation):
    atom_id = 375

    def compute(self):
        return self.value_a + self.value_b

    @classmethod
    def get_subtitle(cls, value_a = None, value_b = None, **kwargs):
        return '{} + {}'.format(cls.get_atom_parameter_value('value_a', value_a), cls.get_atom_parameter_value('value_b', value_b))


class MathDivision(MathOperation):
    atom_id = 378

    def compute(self):
        return self.value_a / self.value_b

    @classmethod
    def get_subtitle(cls, value_a = None, value_b = None, **kwargs):
        return '{} / {}'.format(cls.get_atom_parameter_value('value_a', value_a), cls.get_atom_parameter_value('value_b', value_b))


class MathMultiplication(MathOperation):
    atom_id = 377

    def compute(self):
        return self.value_a * self.value_b

    @classmethod
    def get_subtitle(cls, value_a = None, value_b = None, **kwargs):
        return '{} * {}'.format(cls.get_atom_parameter_value('value_a', value_a), cls.get_atom_parameter_value('value_b', value_b))


class MathSubtraction(MathOperation):
    atom_id = 376

    def compute(self):
        return self.value_a - self.value_b

    @classmethod
    def get_subtitle(cls, value_a = None, value_b = None, **kwargs):
        return '{} - {}'.format(cls.get_atom_parameter_value('value_a', value_a), cls.get_atom_parameter_value('value_b', value_b))


class RandomItem(GetterAtom):
    atom_id = 381

    def __init__(self, list_of_things = None, **kwargs):
        self.list_of_things = list_of_things

    def get_values(self):
        if not self.list_of_things:
            return None
        return {'thing': random.choice(self.list_of_things)}

    @classmethod
    def get_subtitle(cls, list_of_things = None, **kwargs):
        return list_of_things or ''


class RandomFloat(GetterAtom):
    atom_id = 380

    def __init__(self, min_value = None, max_value = None, decimal_places = None, **kwargs):
        self.min_value = self.get_atom_parameter_value('min_value', min_value)
        self.max_value = self.get_atom_parameter_value('max_value', max_value)
        self.decimal_places = self.get_atom_parameter_value('decimal_places', decimal_places)

    def get_values(self):
        return {'value': round(random.uniform(self.min_value, self.max_value), self.decimal_places)}

    @classmethod
    def get_subtitle(cls, min_value = None, max_value = None, **kwargs):
        return '{} - {}'.format(cls.get_atom_parameter_value('min_value', min_value), cls.get_atom_parameter_value('max_value', max_value))


class RandomInt(GetterAtom):
    atom_id = 379

    def __init__(self, min_value = None, max_value = None, **kwargs):
        self.min_value = self.get_atom_parameter_value('min_value', min_value)
        self.max_value = self.get_atom_parameter_value('max_value', max_value)

    def get_values(self):
        return {'value': random.randint(self.min_value, self.max_value)}

    @classmethod
    def get_subtitle(cls, min_value = None, max_value = None, **kwargs):
        return '{} - {}'.format(cls.get_atom_parameter_value('min_value', min_value), cls.get_atom_parameter_value('max_value', max_value))


class CountInstancesOf(GetterAtom):
    atom_id = 405

    def __init__(self, elements = None, value = None, **kwargs):
        self.elements = elements
        self.value = self.get_atom_parameter_value('value', value)
        try:
            self.value = literal_eval(self.value)
        except ValueError:
            self.value = self.value

    def get_values(self):
        count = self.elements.count(self.value)
        return {'count': count}

    @classmethod
    def get_subtitle(cls, value = None, **kwargs):
        return value or ''


class Lerp(GetterAtom):
    atom_id = 435

    def __init__(self, a = None, b = None, t = None, **kwargs):
        self.a = self.get_atom_parameter_value('a', a)
        self.b = self.get_atom_parameter_value('b', b)
        self.t = self.get_atom_parameter_value('t', t)

    def get_values(self, **kwargs):
        if self.a is None or self.b is None or self.t is None:
            return
        import mathext
        return {'value': mathext.lerp(self.a, self.b, self.t)}

    @classmethod
    def get_subtitle(cls, a = None, b = None, t = None, **kwargs):
        return 'a:{} b:{} t:{}'.format(cls.get_atom_parameter_value('a', a), cls.get_atom_parameter_value('b', b), cls.get_atom_parameter_value('t', t))


class InverseLerp(GetterAtom):
    atom_id = 436

    def __init__(self, a = None, b = None, v = None, **kwargs):
        self.a = self.get_atom_parameter_value('a', a)
        self.b = self.get_atom_parameter_value('b', b)
        self.v = self.get_atom_parameter_value('v', v)

    def get_values(self, **kwargs):
        if self.a is None or self.b is None or self.v is None:
            return
        import mathext
        return {'value': mathext.inverse_lerp(self.a, self.b, self.v)}

    @classmethod
    def get_subtitle(cls, a = None, b = None, v = None, **kwargs):
        return 'a:{} b:{} v:{}'.format(cls.get_atom_parameter_value('a', a), cls.get_atom_parameter_value('b', b), cls.get_atom_parameter_value('v', v))
