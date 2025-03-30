#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\client\window_stack.py
import eveicon
import localization
import uthread2
from carbonui.window.stack import WindowStack
from carbonui.uicore import uicore
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from uihider import UiHiderMixin
from chat.client.util import get_chat_default_height, get_chat_default_width

class ChatWindowStack(UiHiderMixin, WindowStack):
    uniqueUiName = pConst.UNIQUE_NAME_CHAT_STACK
    default_left = 16

    def ApplyAttributes(self, attributes):
        super(ChatWindowStack, self).ApplyAttributes(attributes)
        self._AddTabButton()

    @staticmethod
    def default_top():
        return uicore.desktop.height - ChatWindowStack.default_height() - 16

    @staticmethod
    def default_width():
        return get_chat_default_width()

    @staticmethod
    def default_height():
        return get_chat_default_height()

    def _AddTabButton(self):
        tabs = self.GetTabGroup()
        if tabs is not None:
            join_channel_button = tabs.AddButton(icon=eveicon.add, func=self._open_channels_window, hint=localization.GetByLabel('UI/Chat/OpenChannelWindow'))
            join_channel_button.uniqueUiName = pConst.UNIQUE_NAME_CHANNEL_WND

    def RemoveWnd(self, wnd, grab, correctpos = 1, idx = 0, dragging = 0, check = 1):
        WindowStack.RemoveWnd(self, wnd, grab, correctpos, idx, dragging, check)
        if wnd.destroyed:
            return
        if not dragging:
            uthread2.start_tasklet(wnd.StackSelf)

    def _open_channels_window(self, *args, **kwargs):
        from xmppchatclient.xmppchatchannels import XmppChatChannels
        XmppChatChannels.Open()
