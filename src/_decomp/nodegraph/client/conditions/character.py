#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\character.py
from .base import Condition

class IsRace(Condition):
    atom_id = 383

    def __init__(self, race_id = None, **kwargs):
        super(IsRace, self).__init__(**kwargs)
        self.race_id = self.get_atom_parameter_value('race_id', race_id)

    def validate(self, **kwargs):
        return session.raceID == self.race_id

    @classmethod
    def get_subtitle(cls, race_id = None, **kwargs):
        from characterdata.races import get_race_name
        race_id = cls.get_atom_parameter_value('race_id', race_id)
        race_name = get_race_name(race_id) if race_id else ''
        if race_name:
            return u'{} ({})'.format(race_name, race_id)
        return u'{}'.format(race_id)
