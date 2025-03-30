#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\btnData\btnDataNodeChat.py
import localization
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNode import BtnDataNode
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNodeDynamic import BtnDataNodeDynamic
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataRaw import BTNDATARAW_BY_ID
from xmppchatclient.xmppchatchannels import XmppChatChannels
from chat.client.window import BaseChatWindow

class BtnDataNodeChat(BtnDataNodeDynamic):
    __guid__ = 'neocom.BtnDataNodeChat'
    __notifyevents__ = ['OnChatWindowStartBlinking', 'OnChatWindowStopBlinking']

    def GetMenu(self):
        return [(localization.GetByLabel('UI/Commands/OpenChannels'), uicore.cmd.OpenChannels, [])]

    def GetItemCount(self):
        numBlinking = 0
        for wnd in self._GetOpenChatWindows():
            if getattr(wnd, 'isBlinking', False):
                if wnd.InStack() and wnd.GetStack().display:
                    continue
                numBlinking += 1

        return numBlinking

    def _GetOpenChatWindows(self):
        return [ wnd for wnd in uicore.registry.GetWindows() if isinstance(wnd, BaseChatWindow) ]

    def OnChatWindowStartBlinking(self, wnd):
        self.OnBadgeCountChanged()

    def OnChatWindowStopBlinking(self, wnd):
        self.OnBadgeCountChanged()

    def GetDataList(self):

        def GetKey(wnd):
            priority = ('chatchannel_solarsystemid2', 'chatchannel_corpid', 'chatchannel_allianceid', 'chatchannel_fleetid', 'chatchannel_squadid', 'chatchannel_wingid')
            if wnd.name in priority:
                return priority.index(wnd.name)
            else:
                return wnd.GetCaption()

        sortedData = sorted(self._GetOpenChatWindows(), key=GetKey)
        data = Bunch(addChatChannelWnd=1)
        sortedData.insert(0, data)
        return sortedData

    def GetNodeFromData(self, wnd, parent):
        if getattr(wnd, 'addChatChannelWnd', False):
            cmd = uicore.cmd.commandMap.GetCommandByName(BTNDATARAW_BY_ID['chatchannels'].cmdName)
            return BtnDataNode(parent=parent, children=None, iconPath=XmppChatChannels.default_iconNum, btnID='chatchannels', btnType=neocomConst.BTNTYPE_CMD, cmdName=BTNDATARAW_BY_ID['chatchannels'].cmdName, isRemovable=False, isDraggable=False, label=cmd.GetName())
        else:
            return BtnDataNode(parent=parent, iconPath=neocomConst.ICONPATH_CHAT, label=wnd.GetCaption(), btnID=wnd.windowID, btnType=neocomConst.BTNTYPE_CHATCHANNEL, wnd=wnd, isRemovable=False, isDraggable=False, isBlinking=getattr(wnd, 'isBlinking', False))

    def IsOpen(self):
        return True
