#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\other.py
from .base import GetterAtom

class GetClientSettings(GetterAtom):
    atom_id = 294

    def __init__(self, settings_section = None, settings_group = None, settings_id = None, **kwargs):
        super(GetClientSettings, self).__init__(**kwargs)
        self.settings_section = self.get_atom_parameter_value('settings_section', settings_section)
        self.settings_group = self.get_atom_parameter_value('settings_group', settings_group)
        self.settings_id = settings_id

    def get_values(self):
        try:
            if self.settings_group not in settings[self.settings_section].datastore:
                return {'settings_value': None}
            return {'settings_value': settings[self.settings_section].Get(self.settings_group, self.settings_id)}
        except:
            return {'settings_value': None}

    @classmethod
    def get_subtitle(cls, settings_section = None, settings_group = None, settings_id = None, **kwargs):
        return u'{}.{}.{}'.format(cls.get_atom_parameter_value('settings_section', settings_section), cls.get_atom_parameter_value('settings_group', settings_group), settings_id or 'MISSING')
