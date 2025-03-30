#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\language.py
from .base import Condition

class IsInLanguage(Condition):
    atom_id = 594

    def __init__(self, language_id = None, **kwargs):
        super(IsInLanguage, self).__init__(**kwargs)
        self.language_id = language_id

    def validate(self, **kwargs):
        from langutils.client.utils import is_in_language
        return is_in_language(self.language_id)

    @classmethod
    def get_subtitle(cls, language_id = None, **kwargs):
        if language_id:
            from langutils.client.utils import get_language_name_from_code
            return '{}'.format(get_language_name_from_code(language_id))
        return ''
