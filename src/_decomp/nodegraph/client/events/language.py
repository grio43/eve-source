#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\language.py
from .base import Event

class LanguageChanged(Event):
    atom_id = 593
    __notifyevents__ = ['OnLanguageChanged']

    def OnLanguageChanged(self, language_id):
        self.invoke(language_id=language_id)
