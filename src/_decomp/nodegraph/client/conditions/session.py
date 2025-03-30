#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\session.py
from .base import Condition

class GameLoaded(Condition):
    atom_id = 241

    def validate(self, **kwargs):
        return sm.GetService('cc').IsGameLoaded()
