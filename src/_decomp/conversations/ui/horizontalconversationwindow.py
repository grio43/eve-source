#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\conversations\ui\horizontalconversationwindow.py
import carbonui.const as uiconst
from conversations.ui.conversationwindow import ConversationWindow, MAIN_CONTAINER_PADDING_WINDOW
TOTAL_CONTENT_WIDTH = 280
CONTENT_WIDTH = TOTAL_CONTENT_WIDTH - 2 * MAIN_CONTAINER_PADDING_WINDOW
CONTENT_HORIZONTAL_PADDING = 16
CONTENT_TOP_PADDING = 0
CONTENT_BOTTOM_PADDING = 0
AGENT_PORTRAIT_HEIGHT = 200
AGENT_PORTRAIT_WIDTH = 150
AGENT_PORTRAIT_HORIZONTAL_PADDING = 16
AGENT_PORTRAIT_VERTICAL_PADDING = 1
EXTRA_PORTRAIT_BOT_PADDING = 8
MAIN_CONTAINER_WIDTH = TOTAL_CONTENT_WIDTH + AGENT_PORTRAIT_WIDTH + 0
DEFAULT_WIDTH = MAIN_CONTAINER_WIDTH
DEFAULT_HEIGHT = 168

class HorizontalConversationWindow(ConversationWindow):
    default_minSize = (DEFAULT_WIDTH, DEFAULT_HEIGHT)
    default_maxSize = (DEFAULT_WIDTH, DEFAULT_HEIGHT)
    default_width = DEFAULT_WIDTH
    default_height = DEFAULT_HEIGHT
    default_is_decoration_on_sides = False

    def _get_content_container_alignment(self):
        return uiconst.TOLEFT

    def _get_main_container_width(self):
        return MAIN_CONTAINER_WIDTH

    def _get_main_container_height(self):
        content_container_height_with_padding = self.content_container.height + self.content_container.padTop + self.content_container.padBottom
        horizontal_height = max(self.portrait_container.height, content_container_height_with_padding)
        return horizontal_height

    def _get_content_width(self):
        return CONTENT_WIDTH

    def _get_content_horizontal_padding(self):
        return CONTENT_HORIZONTAL_PADDING

    def _get_content_top_padding(self):
        return CONTENT_TOP_PADDING

    def _get_content_bottom_padding(self):
        return CONTENT_BOTTOM_PADDING

    def _get_portrait_container_width(self):
        return AGENT_PORTRAIT_WIDTH

    def _get_portrait_container_height(self):
        return AGENT_PORTRAIT_HEIGHT

    def _get_portrait_container_alignment(self):
        return uiconst.TOLEFT

    def _get_agent_portrait_size(self):
        return (AGENT_PORTRAIT_WIDTH, AGENT_PORTRAIT_HEIGHT)
