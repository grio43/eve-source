#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\atoms\conditions\string.py
from .base import ConditionAtom

class IsSubstring(ConditionAtom):
    atom_id = 496

    def __init__(self, string_a = None, string_b = None, **kwargs):
        super(IsSubstring, self).__init__(**kwargs)
        self.string_a = self.get_atom_parameter_value('string_a', string_a)
        self.string_b = self.get_atom_parameter_value('string_b', string_b)

    def validate(self, **kwargs):
        if not all([self.string_a, self.string_b]):
            return False
        return self.string_a in self.string_b

    @classmethod
    def get_subtitle(cls, string_a = None, string_b = None, **kwargs):
        return u'{} in {}'.format(string_a or '-', string_b or '-')
