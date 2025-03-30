#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\tutorial.py
from .base import Event

class AirNPEFocusChanged(Event):
    atom_id = 631
    __notifyevents__ = ['OnAirNPEFocusChanged']

    def OnAirNPEFocusChanged(self):
        self.invoke()
