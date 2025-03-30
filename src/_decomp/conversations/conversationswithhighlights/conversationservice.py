#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\conversations\conversationswithhighlights\conversationservice.py
from avatardisplay.avatardisplay import AvatarDisplay as ad
from carbon.common.script.sys.service import Service
from conversations.conversationswithhighlights.conversationwithuihighlights import ConversationWithUiHighlights
from conversations.conversationswithhighlights.highlightscontroller import ConversationHighlightsController
from conversations.conversationcontroller import ConversationController, BaseConversationManager
from conversations.fsdloaders import ConversationsLoader

class ConversationService(Service):
    __guid__ = 'svc.ConversationService'
    serviceName = 'svc.ConversationService'
    __displayname__ = 'ConversationService'
    __servicename__ = 'ConversationService'
    __notifyevents__ = ['OnStartConversation', 'OnSessionReset']

    def Run(self, *args, **kwargs):
        conversation_manager = ConversationManager()
        self.conversation_controller = ConversationController(conversation_manager)
        self.show_conversation = self.conversation_controller.show_conversation
        self.hide_conversation = self.conversation_controller.hide_conversation
        self.force_hiding_active_conversation = self.conversation_controller.force_hiding_active_conversation
        self.notify_of_conversation_start = self.conversation_controller.notify_of_conversation_start
        self.notify_of_conversation_minimized = self.conversation_controller.notify_of_conversation_minimized
        self.notify_of_conversation_maximized = self.conversation_controller.notify_of_conversation_maximized
        self.clear_conversation = self.conversation_controller.clear_conversation
        self.get_active_conversation_id = self.conversation_controller.get_active_conversation_id
        self.are_any_conversation_lines_left = self.conversation_controller.are_any_conversation_lines_left
        self.get_next_conversation_line = self.conversation_controller.get_next_conversation_line
        self.are_any_previous_conversation_lines_available = self.conversation_controller.are_any_previous_conversation_lines_available
        self.get_previous_conversation_line = self.conversation_controller.get_previous_conversation_line
        self.get_active_conversation_line = self.conversation_controller.get_active_conversation_line
        self.get_agent = self.conversation_controller.get_agent
        self.get_line_hint_image = self.conversation_controller.get_line_hint_image
        self.get_play_event = self.conversation_controller.get_play_event
        self.get_stop_event = self.conversation_controller.get_stop_event
        self.is_conversation_active = self.conversation_controller.is_conversation_active
        self.get_music_trigger = self.conversation_controller.get_music_trigger
        self.preload_air_npe_agents = self.conversation_controller.preload_air_npe_agents
        self.preload_agent = self.conversation_controller.preload_agent
        self.highlights_controller = ConversationHighlightsController(conversation_service=self)
        Service.Run(self, *args, **kwargs)

    def get_active_ui_highlights_by_conversation_id(self, conversation_id):
        ui_highlights = []
        active_conversation_line = self.conversation_controller.get_active_conversation_line()
        if active_conversation_line:
            try:
                ui_highlights = active_conversation_line.ui_highlights
            except AttributeError:
                self.LogError('Failed to get UI highlights for conversation wth id: %s' % conversation_id)

        return ui_highlights

    def get_active_space_object_highlights_by_conversation_id(self, conversation_id):
        space_object_highlights = []
        active_conversation_line = self.conversation_controller.get_active_conversation_line()
        if active_conversation_line:
            try:
                space_object_highlights = active_conversation_line.space_object_highlights
            except AttributeError:
                self.LogError('Failed to get space object highlights for conversation wth id: %s' % conversation_id)

        return space_object_highlights

    def get_active_menu_highlights_by_conversation_id(self, conversation_id):
        menu_highlights = []
        active_conversation_line = self.conversation_controller.get_active_conversation_line()
        if active_conversation_line:
            try:
                menu_highlights = active_conversation_line.menu_highlights
            except AttributeError:
                self.LogError('Failed to get menu highlights for conversation wth id: %s' % conversation_id)

        return menu_highlights

    def get_active_ui_blinks_by_conversation_id(self, conversation_id):
        ui_blinks = []
        active_conversation_line = self.conversation_controller.get_active_conversation_line()
        if active_conversation_line:
            try:
                ui_blinks = active_conversation_line.ui_blinks
            except AttributeError:
                self.LogError('Failed to get UI blinks for conversation wth id: %s' % conversation_id)

        return ui_blinks

    def OnStartConversation(self, conversation_id, show_continue_button):
        self.show_conversation(conversation_id, show_continue_button=show_continue_button, should_close_on_continue=True)

    def OnSessionReset(self):
        import logging
        logging.info('Conversation Manager:  OnSessionReset triggered.')
        self.conversation_controller._are_air_npe_agents_preloaded = False
        self.conversation_controller._agents_preloaded = set()
        ad.ClearAvatarDisplayGlobals()


class ConversationManager(BaseConversationManager):

    def get_conversation(self, conversation_id, variables = None):
        conversation = ConversationsLoader.GetByID(conversation_id)
        if conversation is None:
            raise ValueError('No conversation found with id {id}'.format(id=conversation_id))
        name = conversation.name
        lines = conversation.lines
        return ConversationWithUiHighlights(conversation_id, name, lines, variables)
