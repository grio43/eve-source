#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\atoms\conditions\primitive.py
from ast import literal_eval
from .base import ConditionAtom

class IsNone(ConditionAtom):
    atom_id = 368

    def __init__(self, value = None, **kwargs):
        super(IsNone, self).__init__(**kwargs)
        self.value = value

    def validate(self, **kwargs):
        try:
            return literal_eval(str(self.value)) is None
        except (SyntaxError, ValueError):
            return False
