#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\npc.py
from .base import GetterAtom

class GetNpcCorporationData(GetterAtom):
    atom_id = 393

    def __init__(self, division_id = None, **kwargs):
        super(GetNpcCorporationData, self).__init__(**kwargs)
        self.division_id = self.get_atom_parameter_value('division_id', division_id)

    def get_values(self, **kwargs):
        if self.division_id:
            from npcs.divisions import get_division_internal_name
            return {'name': get_division_internal_name(self.division_id)}
        return {}

    @classmethod
    def get_subtitle(cls, division_id = None, **kwargs):
        if not division_id:
            return ''
        from npcs.divisions import get_division_internal_name
        name = get_division_internal_name(division_id)
        if name:
            return u'{} ({})'.format(name, division_id)
        return u'{}'.format(division_id)
