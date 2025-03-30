#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\tutorial.py
from storylines.client.airnpe import is_air_npe_focused
from .base import Condition

class AirNPEFocused(Condition):
    atom_id = 632

    def validate(self, **kwargs):
        return is_air_npe_focused()
