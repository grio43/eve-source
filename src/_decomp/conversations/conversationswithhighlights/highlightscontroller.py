#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\conversations\conversationswithhighlights\highlightscontroller.py
from collections import defaultdict
from localization import GetByLabel
from uthread2 import start_tasklet, sleep

class ConversationHighlightsController(object):
    __notifyevents__ = ['OnConversationStarted', 'OnConversationEnded', 'OnConversationMinimized']

    def __init__(self, conversation_service):
        self.conversation_service = conversation_service
        self._ui_highlighting_service = None
        self._ui_blinks_service = None
        self._active_ui_highlights_by_conversation = defaultdict(list)
        self._active_space_highlights_by_conversation = defaultdict(list)
        self._active_ui_blinks_by_conversation = defaultdict(list)
        sm.RegisterNotify(self)

    @property
    def ui_highlighting_service(self):
        if self._ui_highlighting_service is None:
            self._ui_highlighting_service = sm.GetService('uiHighlightingService')
        return self._ui_highlighting_service

    @property
    def ui_blinks_service(self):
        if not self._ui_blinks_service:
            from uiblinker import get_service
            self._ui_blinks_service = get_service()
        return self._ui_blinks_service

    def OnConversationStarted(self, conversation_id):
        self._clear_highlighting_for_conversation(conversation_id)
        start_tasklet(self._process_conversation_started, conversation_id)

    def OnConversationEnded(self, conversation_id):
        self._clear_highlighting_for_conversation(conversation_id)

    def OnConversationMinimized(self, _conversation_id):
        if not settings.char.ui.Get('hasSeenAuraHighlight', False):
            sleep(0.5)
            self._highlight_aura()
            settings.char.ui.Set('hasSeenAuraHighlight', True)

    def _highlight_aura(self):
        self.ui_highlighting_service.highlight_ui_element_by_name('neocom.InstructionsConversationWindow', GetByLabel('UI/Conversations/HighlightAuraOnFirstMinimize'), fadeout_seconds=5, title='')

    def _process_conversation_started(self, conversation_id):
        if self.conversation_service.get_active_conversation_id() != conversation_id:
            return
        self._reveal_ui_highlights(conversation_id)
        self._reveal_space_object_highlights(conversation_id)
        self._reveal_menu_highlights(conversation_id)
        self._reveal_ui_blinks(conversation_id)

    def _reveal_menu_highlights(self, conversation_id):
        menu_highlight_ids = self.conversation_service.get_active_menu_highlights_by_conversation_id(conversation_id)
        if menu_highlight_ids:
            self.ui_highlighting_service.highlight_menu_by_ids(menu_highlight_ids)

    def _reveal_space_object_highlights(self, conversation_id):
        space_object_highlight_ids = self.conversation_service.get_active_space_object_highlights_by_conversation_id(conversation_id)
        if space_object_highlight_ids:
            for space_object_highlight_id in space_object_highlight_ids:
                self.ui_highlighting_service.highlight_space_object(space_object_highlight_id)

            self._active_space_highlights_by_conversation[conversation_id] += space_object_highlight_ids

    def _reveal_ui_highlights(self, conversation_id):
        ui_highlight_ids = self.conversation_service.get_active_ui_highlights_by_conversation_id(conversation_id)
        if ui_highlight_ids:
            self.ui_highlighting_service.highlight_ui_elements(ui_highlight_ids)
            self._active_ui_highlights_by_conversation[conversation_id] += ui_highlight_ids

    def _reveal_ui_blinks(self, conversation_id):
        ui_blinks = self.conversation_service.get_active_ui_blinks_by_conversation_id(conversation_id)
        if ui_blinks:
            self.ui_blinks_service.start_blinkers_by_id(ui_blinks)
            self._active_ui_blinks_by_conversation[conversation_id] += ui_blinks

    def _clear_highlighting_for_conversation(self, conversation_id):
        self.ui_highlighting_service.clear_menu_highlighting()
        for space_highlight_id in self._active_space_highlights_by_conversation[conversation_id]:
            self.ui_highlighting_service.clear_space_object_highlight(space_highlight_id)

        self._active_space_highlights_by_conversation[conversation_id] = []
        for ui_highlight_id in self._active_ui_highlights_by_conversation[conversation_id]:
            self.ui_highlighting_service.remove_highlight_from_ui_element_by_id(ui_highlight_id)

        self._active_ui_highlights_by_conversation[conversation_id] = []
        blink_ids = self._active_ui_blinks_by_conversation[conversation_id]
        if blink_ids:
            self.ui_blinks_service.stop_blinkers_by_id(blink_ids)
            self._active_ui_blinks_by_conversation[conversation_id] = []
