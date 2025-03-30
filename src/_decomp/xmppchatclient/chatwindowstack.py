#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmppchatclient\chatwindowstack.py
import eveicon
import localization
import trinity
import uthread2
from carbon.common.script.sys import service
import carbonui.const as uiconst
from carbonui.window.stack import WindowStack
from carbonui.uicore import uicore
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from uihider import UiHiderMixin
from xmppchatclient.xmppchatchannels import XmppChatChannels

def HasChatKillingRoles():
    return session.role & (service.ROLE_CHTADMINISTRATOR | service.ROLE_GML)


class ChatWindowStack(UiHiderMixin, WindowStack):
    uniqueUiName = pConst.UNIQUE_NAME_CHAT_STACK
    default_left = 16
    default_width_large = 450
    default_width_medium = 360
    default_width_small = 260
    default_height_large = 350
    default_height_medium = 320
    default_height_small = 260

    def ApplyAttributes(self, attributes):
        super(ChatWindowStack, self).ApplyAttributes(attributes)
        self._AddTabButton()

    @staticmethod
    def default_top():
        return uicore.desktop.height - ChatWindowStack.default_height() - 16

    @staticmethod
    def default_width():
        deviceWidth = trinity.device.width
        if deviceWidth >= uiconst.UI_DEFAULT_WIDTH_THRESHOLD_LARGE:
            return ChatWindowStack.default_width_large
        if deviceWidth >= uiconst.UI_DEFAULT_WIDTH_THRESHOLD_MEDIUM:
            return ChatWindowStack.default_width_medium
        return ChatWindowStack.default_width_small

    @staticmethod
    def default_height():
        deviceHeight = trinity.device.height
        if deviceHeight >= uiconst.UI_DEFAULT_HEIGHT_THRESHOLD_LARGE:
            return ChatWindowStack.default_height_large
        if deviceHeight >= uiconst.UI_DEFAULT_HEIGHT_THRESHOLD_MEDIUM:
            return ChatWindowStack.default_height_medium
        return ChatWindowStack.default_height_small

    def _AddTabButton(self):
        tabs = self.GetTabGroup()
        if tabs is not None:
            join_channel_button = tabs.AddButton(icon=eveicon.add, func=XmppChatChannels.Open, hint=localization.GetByLabel('UI/Chat/OpenChannelWindow'))
            join_channel_button.uniqueUiName = pConst.UNIQUE_NAME_CHANNEL_WND

    def RemoveWnd(self, wnd, grab, correctpos = 1, idx = 0, dragging = 0, check = 1):
        WindowStack.RemoveWnd(self, wnd, grab, correctpos, idx, dragging, check)
        if wnd.destroyed:
            return
        if not dragging:
            uthread2.start_tasklet(wnd.StackSelf)
