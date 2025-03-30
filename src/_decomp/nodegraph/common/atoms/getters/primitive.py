#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\atoms\getters\primitive.py
from ast import literal_eval
from .base import GetterAtom

class PrimitiveGetterAtom(GetterAtom):
    type_cast = None

    def __init__(self, value = None, **kwargs):
        super(PrimitiveGetterAtom, self).__init__(**kwargs)
        self.value = self.get_atom_parameter_value('value', value)

    def get_values(self, **kwargs):
        return {'value': self.type_cast(self.value)}

    @classmethod
    def get_subtitle(cls, value = None, **kwargs):
        return str(cls.get_atom_parameter_value('value', value))


class Boolean(PrimitiveGetterAtom):
    atom_id = 298
    type_cast = bool


class Float(PrimitiveGetterAtom):
    atom_id = 301
    type_cast = float


class Integer(PrimitiveGetterAtom):
    atom_id = 302
    type_cast = long


class String(PrimitiveGetterAtom):
    atom_id = 303
    type_cast = str


class StringEval(PrimitiveGetterAtom):
    atom_id = 307

    def get_values(self, **kwargs):
        try:
            value = literal_eval(self.value)
        except ValueError:
            value = self.value

        return {'value': value}


class NoneConstant(GetterAtom):
    atom_id = 446

    def get_values(self, **kwargs):
        return {'value': None}
