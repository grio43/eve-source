#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\language.py
from .base import Action

class SetLanguage(Action):
    atom_id = 591

    def __init__(self, language_id = None, **kwargs):
        super(SetLanguage, self).__init__(**kwargs)
        self.language_id = language_id

    def start(self, **kwargs):
        super(SetLanguage, self).start(**kwargs)
        from langutils.client.utils import set_language
        set_language(self.language_id)

    @classmethod
    def get_subtitle(cls, language_id = None, **kwargs):
        if language_id:
            from langutils.client.utils import get_language_name_from_code
            return '{}'.format(get_language_name_from_code(language_id))
        return ''
