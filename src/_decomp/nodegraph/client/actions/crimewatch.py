#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\crimewatch.py
from __future__ import absolute_import
from .base import Action

class SetSafetyLevel(Action):
    atom_id = 331

    def __init__(self, safety_level = None, **kwargs):
        super(SetSafetyLevel, self).__init__(**kwargs)
        self.safety_level = self.get_atom_parameter_value('safety_level', safety_level)

    def start(self, **kwargs):
        from crimewatch.const import shipSafetyLevelNone, shipSafetyLevelPartial, shipSafetyLevelFull
        super(SetSafetyLevel, self).start(**kwargs)
        if self.safety_level in (shipSafetyLevelNone, shipSafetyLevelPartial, shipSafetyLevelFull):
            sm.GetService('crimewatchSvc').SetSafetyLevel(self.safety_level)

    @classmethod
    def get_subtitle(cls, safety_level = None, **kwargs):
        safety_level = cls.get_atom_parameter_value('safety_level', safety_level)
        from crimewatch.const import shipSafetyLevelNone, shipSafetyLevelPartial, shipSafetyLevelFull
        name_map = {shipSafetyLevelNone: 'Disabled',
         shipSafetyLevelPartial: 'Partial',
         shipSafetyLevelFull: 'Enabled'}
        return name_map.get(safety_level, 'Invalid safety level')
