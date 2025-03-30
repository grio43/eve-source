#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\conversation.py
import threadutils
from conversations.fsdloaders import ConversationsLoader
from nodegraph.client.actions.base import Action
from nodegraph.client.events.conversation import ConversationEnded

class ShowConversation(Action):
    atom_id = 1

    def __init__(self, conversation_id = None, conversation_values = None, show_continue_button = None, should_autoprogress = None, show_only_once = None, **kwargs):
        super(ShowConversation, self).__init__(**kwargs)
        self.conversation_id = conversation_id
        self.conversation_values = conversation_values
        self.show_continue_button = self.get_atom_parameter_value('show_continue_button', show_continue_button)
        self.should_autoprogress = self.get_atom_parameter_value('should_autoprogress', should_autoprogress)
        self.show_only_once = self.get_atom_parameter_value('show_only_once', show_only_once)
        self._active_conversation_id = None
        self._conversation_event = None

    def start(self, **kwargs):
        super(ShowConversation, self).start(**kwargs)
        if not self.conversation_id:
            return
        self._subscribe(self.conversation_id)
        self._show_conversation()

    @threadutils.threaded
    def _show_conversation(self):
        sm.GetService('conversationService').show_conversation(conversation_id=self.conversation_id, show_continue_button=self.show_continue_button, should_close_on_continue=True, should_autoprogress=self.should_autoprogress, variables=self.conversation_values, show_only_once=self.show_only_once)

    def stop(self):
        if self._active_conversation_id:
            super(ShowConversation, self).stop()
            StopConversation(conversation_id=self._active_conversation_id).start()

    def _subscribe(self, conversation_id):
        if self._on_end_callback:
            self._active_conversation_id = conversation_id
            self._conversation_event = ConversationEnded(callback=self._conversation_ended, keep_listening=True)
            self._conversation_event.start()

    def _conversation_ended(self, conversation_id):
        if self._active_conversation_id == conversation_id:
            self._active_conversation_id = None
            if self._conversation_event:
                self._conversation_event.stop()
                self._conversation_event = None
            self._on_end()

    @classmethod
    def get_subtitle(cls, **kwargs):
        return _get_subtitle(**kwargs)


class StopConversation(Action):
    atom_id = 8

    def __init__(self, conversation_id = None, **kwargs):
        super(StopConversation, self).__init__(**kwargs)
        self.conversation_id = conversation_id

    def start(self, **kwargs):
        super(StopConversation, self).start(**kwargs)
        conversation_service = sm.GetService('conversationService')
        if self.conversation_id is None or conversation_service.get_active_conversation_id() == self.conversation_id:
            conversation_service.hide_conversation()

    @classmethod
    def get_subtitle(cls, **kwargs):
        return _get_subtitle(**kwargs)


def _get_subtitle(conversation_id = None, **kwargs):
    if not conversation_id:
        return
    conversation = ConversationsLoader.GetByID(conversation_id)
    if conversation:
        return u'{} ({})'.format(conversation.name, conversation_id)


class PreloadConversationAgent(Action):
    atom_id = 313

    def __init__(self, **kwargs):
        super(PreloadConversationAgent, self).__init__(**kwargs)

    def start(self, **kwargs):
        super(PreloadConversationAgent, self).start(**kwargs)
        sm.GetService('conversationService').preload_air_npe_agents()


class PreloadIdleConversationAgent(Action):
    atom_id = 588

    def __init__(self, agent_id = None, **kwargs):
        super(PreloadIdleConversationAgent, self).__init__(**kwargs)
        self.agent_id = self.get_atom_parameter_value('agent_id', agent_id)

    def start(self, **kwargs):
        super(PreloadIdleConversationAgent, self).start(**kwargs)
        if not self.agent_id:
            return
        conversation_service = sm.GetService('conversationService')
        conversation_service.preload_agent(self.agent_id)

    @classmethod
    def get_subtitle(cls, agent_id = None, **kwargs):
        return cls.get_atom_parameter_value('agent_id', agent_id)
