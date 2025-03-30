#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmppchatclient\xmppchannelfield.py
import logging
import localization
from carbonui.fontconst import EVE_SMALL_FONTSIZE
from eve.client.script.ui.control.entries.generic import Generic
from menu import MenuLabel
import carbonui.const as uiconst
import uthread2
from carbon.common.script.sys import service
from chatutil import GetChannelCategory
from carbonui.control.button import Button
from eve.client.script.ui.util.uix import GetTextHeight
from eveservices.xmppchat import GetChatService
from globalConfig.getFunctions import GetUpdateChannelCountIntervalSeconds
from xmppchatclient.const import CATEGORY_PLAYER
from xmppchatclient.xmppchannelsettings import ChannelSettingsDlg
REFRESH_COUNT_INTERVAL = 300
logger = logging.getLogger('xmppchat')

class XmppChannelField(Generic):
    __guid__ = 'listentry.XmppChannelField'
    __nonpersistvars__ = ['groupID',
     'status',
     'active',
     'selection',
     'channel']
    isDragObject = True

    def Startup(self, *args):
        Generic.Startup(self, *args)
        self.joinleaveBtn = Button(parent=self, label=localization.GetByLabel('UI/Chat/ChannelWindow/Join'), func=self.JoinLeaveChannelFromBtn, idx=0, left=4, align=uiconst.CENTERRIGHT)

    def _OnClose(self):
        if self.updateTasklet:
            self.updateTasklet.kill()
            self.updateTasklet = None

    def Load(self, node):
        Generic.Load(self, node)
        channelId = self.sr.node.channel
        if GetChatService().IsJoined(channelId):
            self.joinleaveBtn.SetLabel(localization.GetByLabel('UI/Chat/ChannelWindow/Leave'))
        else:
            self.joinleaveBtn.SetLabel(localization.GetByLabel('UI/Chat/ChannelWindow/Join'))
        self.updateTasklet = uthread2.start_tasklet(self._UpdateCount)

    def _UpdateCount(self):
        channelId = self.sr.node.channel
        displayName = self.sr.node.genericDisplayLabel
        while not self.destroyed:
            interval = GetUpdateChannelCountIntervalSeconds(sm.GetService('machoNet'))
            if interval > 0:
                count = GetChatService().GetNumChannelOccupants(channelId)
                if count:
                    formattedCount = localization.formatters.FormatNumeric(count)
                    text = '%s<t>%s' % (displayName, formattedCount)
                    self.sr.label.text = text
                    self.sr.node.label = text
                else:
                    self.sr.label.text = '%s<t>' % displayName
                uthread2.sleep(interval)
            else:
                self.sr.label.text = '%s<t>' % displayName
                uthread2.sleep(REFRESH_COUNT_INTERVAL)

    def GetHeight(self, *args):
        node, width = args
        return Button.default_height + 8

    def OnDblClick(self, *args):
        pass

    def GetMenu(self):
        self.OnClick()
        channelId = self.sr.node.channel
        isOwner = GetChatService().IsOwnerOfChannel(channelId)
        isOperator = GetChatService().IsOperatorOfChannel(channelId)
        category = GetChannelCategory(channelId)
        menu = []
        if GetChatService().IsJoined(channelId):
            menu.append((MenuLabel('UI/Chat/ChannelWindow/LeaveChannel'), self.LeaveChannel, (channelId,)))
            if isOwner or isOperator or session.role & (service.ROLE_CHTADMINISTRATOR | service.ROLE_GML):
                menu.append((MenuLabel('UI/Chat/Settings'), self.Settings))
        else:
            menu.append((MenuLabel('UI/Chat/ChannelWindow/JoinChannel'), self.JoinChannel, (channelId,)))
            if category == CATEGORY_PLAYER and not isOwner:
                menu.append((MenuLabel('UI/Chat/ChannelWindow/ForgetChannel'), self.ForgetChannel))
        if category == CATEGORY_PLAYER and isOwner:
            menu.append((MenuLabel('UI/Chat/ChannelWindow/DeleteChannel'), self.DeleteChannel))
        if len(menu):
            return menu

    def Settings(self):
        ChannelSettingsDlg.Open(channel=self.sr.node.channel, windowID='ChannelSettingsDlg_%s' % self.sr.node.channel)

    def JoinChannel(self, channel):
        uthread2.start_tasklet(GetChatService().JoinChannel, channel)

    def LeaveChannel(self, channel):
        GetChatService().LeaveChannel(channel)

    def JoinLeaveChannelFromBtn(self, *args):
        self.JoinLeaveChannel()

    def JoinLeaveChannel(self):
        channelId = self.sr.node.channel
        self.state = uiconst.UI_DISABLED
        if GetChatService().IsJoined(channelId):
            GetChatService().LeaveChannel(channelId)
        else:
            uthread2.start_tasklet(GetChatService().JoinChannel, channelId)
        self.state = uiconst.UI_NORMAL

    def DeleteChannel(self):
        GetChatService().DeleteChannel(self.sr.node.channel)

    def ForgetChannel(self):
        GetChatService().ForgetChannel(self.sr.node.channel)

    def GetDragData(self):
        return [self.sr.node]
