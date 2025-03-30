#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\chat.py
from .base import Event

class ChatMessageSent(Event):
    atom_id = 47
    __notifyevents__ = ['OnClientEvent_ChatMessageSent']

    def OnClientEvent_ChatMessageSent(self):
        self.invoke()
