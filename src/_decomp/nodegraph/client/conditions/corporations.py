#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\corporations.py
from nodegraph.client.conditions.base import Condition

class IsPlayerRunCorporation(Condition):
    atom_id = 619

    def __init__(self, corporation_id = None, **kwargs):
        super(IsPlayerRunCorporation, self).__init__(**kwargs)
        self.corporation_id = self.get_atom_parameter_value('corporation_id', corporation_id)

    def validate(self, **kwargs):
        from eve.common.script.sys.idCheckers import IsPlayerCorporation
        return IsPlayerCorporation(self.corporation_id)
