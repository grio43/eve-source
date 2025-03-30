#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\conversations\conversationswithhighlights\conversationwithuihighlights.py
from conversations.conversation import LineOfDialogue, Conversation

class LineOfDialogueWithUiHighlights(LineOfDialogue):

    def __init__(self, agent_id, text_message_id, sound_id, hints, ui_highlights, space_object_highlights, menu_highlights, ui_blinks, music_trigger, scene_path = None, variables = None):
        self.ui_highlights = ui_highlights
        self.space_object_highlights = space_object_highlights
        self.menu_highlights = menu_highlights
        self.ui_blinks = ui_blinks
        LineOfDialogue.__init__(self, agent_id, text_message_id, sound_id, hints, music_trigger, scene_path=scene_path, variables=variables)


class ConversationWithUiHighlights(Conversation):

    def __init__(self, *args, **kwargs):
        Conversation.__init__(self, *args, **kwargs)

    def next(self):
        line = self._line_iterator.next()
        ui_highlights = line.uiHighlights
        ui_blinks = getattr(line, 'uiBlinks', [])
        space_object_highlights = line.spaceObjectHighlights
        menu_highlights = line.menuHighlights
        hints = line.lineHints
        sound = line.sound or ''
        scene_path = line.scenePath or None
        music_trigger = line.musicTrigger or ''
        return LineOfDialogueWithUiHighlights(line.agentID, line.text, sound, hints, ui_highlights, space_object_highlights, menu_highlights, ui_blinks, music_trigger, scene_path=scene_path, variables=self.variables)
