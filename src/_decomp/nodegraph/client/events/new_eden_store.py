#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\new_eden_store.py
from .base import Event

class NewEdenStorePageLoaded(Event):
    atom_id = 553
    __notifyevents__ = ['OnNESPageLoaded']

    def OnNESPageLoaded(self, page_ui_name):
        self.invoke(page_ui_name=page_ui_name)
