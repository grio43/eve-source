#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\language.py
from .base import GetterAtom

class GetLanguage(GetterAtom):
    atom_id = 592

    def get_values(self, **kwargs):
        from langutils.client.utils import get_language
        return {'language_id': get_language()}
