#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\atoms\getters\other.py
from nodegraph.common.util import get_object_value_by_path
from .base import GetterAtom

class GetValue(GetterAtom):
    atom_id = 333

    def __init__(self, key = None, object = None, default_value = None, **kwargs):
        self.key = key
        self.object = object
        self.default_value = default_value

    def get_values(self, **kwargs):
        if self.object is None or self.key is None:
            return {'value': self.default_value}
        return {'value': get_object_value_by_path(self.object, self.key, self.default_value)}

    @classmethod
    def get_subtitle(cls, key = None, default_value = None, **kwargs):
        return u'{} - default:{}'.format(key or '', default_value)
