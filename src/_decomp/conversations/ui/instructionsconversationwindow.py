#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\conversations\ui\instructionsconversationwindow.py
from conversations.ui.conversationwindowstyle import AuraConversationWindowStyle
from conversations.ui.horizontalconversationwindow import HorizontalConversationWindow
from eve.client.script.ui.shared.pointerTool import pointerToolConst as pConst

class InstructionsConversationWindow(HorizontalConversationWindow):
    __guid__ = 'InstructionsConversationWindow'
    uniqueUiName = pConst.UNIQUE_NAME_INSTRUCTIONS_CONVO
    default_windowID = 'TaskConversationWindow'
    default_is_content_expandable = False
    default_is_decoration_on_sides = False
    default_are_hints_visible = True
    default_are_navigation_buttons_enabled = True
    default_style = AuraConversationWindowStyle
    default_show_warning_on_first_close_setting = 'have_instructions_conversations_ever_been_minimized'
    default_show_warning_on_first_close_dialog = 'AuraConversationDismissed'
    default_close_on_audio_end = False
    default_is_close_button_visible = False
    default_delay_seconds_between_audio_ended_and_show_next = 3
    _transmission_sound_effect = 'npe_aura_incoming_transmission_play'
    default_isKillable = False


class InstructionsConversationWindowWithCloseButton(InstructionsConversationWindow):
    default_is_close_button_visible = True
