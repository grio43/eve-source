#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\conversation.py
from .base import Event

class ConversationStarted(Event):
    atom_id = 55
    __notifyevents__ = ['OnConversationStarted']

    def OnConversationStarted(self, conversation_id):
        self.invoke(conversation_id=conversation_id)


class ConversationEnded(Event):
    atom_id = 56
    __notifyevents__ = ['OnConversationEnded']

    def OnConversationEnded(self, conversation_id):
        self.invoke(conversation_id=conversation_id)


class ConversationMinimized(Event):
    atom_id = 57
    __notifyevents__ = ['OnConversationMinimized']

    def OnConversationMinimized(self, conversation_id):
        self.invoke(conversation_id=conversation_id)


class ConversationContinueButton(Event):
    atom_id = 58
    __notifyevents__ = ['OnClientEvent_ConversationContinueButtonClicked']

    def OnClientEvent_ConversationContinueButtonClicked(self, conversation_id):
        self.invoke(conversation_id=conversation_id)
