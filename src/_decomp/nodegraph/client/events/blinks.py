#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\blinks.py
from .base import Event

class BlinkUiElementUpdated(Event):
    atom_id = 492
    __notifyevents__ = ['OnBlinkerUpdated']

    def OnBlinkerUpdated(self, unique_ui_name):
        self.invoke(focused=unique_ui_name)
