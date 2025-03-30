#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmppchatclient\xmppchatchannels.py
import functools
import logging
import carbonui.const as uiconst
import localization
import uthread2
from carbon.common.script.util.commonutils import StripTags
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from chatutil import GetChannelCategory, StripBreaks
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eveservices.xmppchat import GetChatService
from xmppchatclient.const import CATEGORY_PLAYER, CATEGORY_SYSTEM, CATEGORY_LOCAL, CATEGORY_CORP, CATEGORY_OWNED
from xmppchatclient.link import channel_link
from xmppchatclient.xmppchannelfield import XmppChannelField
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
logger = logging.getLogger('xmppchat')

def GetSubContent(nodedata, newitems = 0):
    nodes = []
    channels = nodedata.groupItems
    for channelId, displayName in channels:
        strippedDisplayName = StripTags(displayName)
        nodes.append(GetFromClass(XmppChannelField, {'channel': channelId,
         'label': '%s<t>' % strippedDisplayName,
         'sublevel': 1,
         'genericDisplayLabel': strippedDisplayName,
         'get_link': functools.partial(channel_link, channelId, strippedDisplayName)}))

    return nodes


class XmppChatChannels(Window):
    default_windowID = 'XmppChatChannels'
    default_captionLabelPath = 'UI/Neocom/ChatChannelsBtn'
    default_descriptionLabelPath = 'Tooltips/Neocom/ChatChannels_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/chatchannels.png'
    default_height = 560
    __notifyevents__ = ['OnChannelJoined',
     'OnChannelLeft',
     'OnChannelDeleted',
     'OnRefreshChannels']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetMinSize([400, 250])
        grid = LayoutGrid(parent=ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, padBottom=16), align=uiconst.TOPLEFT, columns=3, cellSpacing=(8, 8))
        self.input = SingleLineEditText(name='input', parent=grid, align=uiconst.CENTER, maxLength=60, width=160, hintText=localization.GetByLabel('UI/Chat/ChannelName'))
        Button(parent=grid, align=uiconst.CENTER, label=localization.GetByLabel('UI/Chat/ChannelWindow/Join'), func=self.JoinChannelFromBtn, args='self', btn_default=1)
        Button(parent=grid, align=uiconst.CENTER, label=localization.GetByLabel('UI/Chat/ChannelWindow/Create'), func=self.CreateChannelFromBtn, args='self', uniqueUiName=pConst.UNIQUE_NAME_CREATE_CHANNEL_BTN)
        self.channelsScroll = Scroll(parent=self.sr.main, id='xmppchatchannelsscroll', align=uiconst.TOALL)
        self.channelsByDisplayName = {}
        self.isRefreshInProgress = False
        uthread2.start_tasklet(self.Refresh)

    def _OnClose(self, *args, **kw):
        sm.UnregisterNotify(self)

    def OnChannelJoined(self, channel):
        category = GetChannelCategory(channel)
        if category in [CATEGORY_PLAYER, CATEGORY_SYSTEM]:
            self.Refresh()

    def OnChannelLeft(self, channel):
        category = GetChannelCategory(channel)
        if category in [CATEGORY_PLAYER, CATEGORY_SYSTEM]:
            self.Refresh()

    def OnChannelDeleted(self, channel):
        category = GetChannelCategory(channel)
        if category in [CATEGORY_PLAYER, CATEGORY_SYSTEM]:
            self.Refresh()

    def OnRefreshChannels(self):
        self.Refresh()

    def Refresh(self):
        if self.isRefreshInProgress:
            return
        self.isRefreshInProgress = True
        try:
            channels = GetChatService().GetChannels()
            self.SetChannels(channels)
        finally:
            self.isRefreshInProgress = False

    def SetChannels(self, channels):
        self.channelsByDisplayName = {}
        channelsByCategory = {}
        for channelInfo in channels:
            if len(channelInfo) == 3:
                channelId, displayName, affiliation = channelInfo
            else:
                channelId, displayName = channelInfo
                affiliation = None
            category = GetChannelCategory(channelId)
            if category == CATEGORY_SYSTEM:
                _, groupMessageId, channelMessageId = channelId.split('_', 3)
                categoryDisplayName = localization.GetByMessageID(int(groupMessageId))
                category = groupMessageId
                if displayName != '':
                    displayName = localization.GetByLabel('UI/Chat/ChannelWindow/ChannelWithForienDisplay', msgID=int(channelMessageId), displayName=displayName)
                else:
                    displayName = localization.GetByMessageID(int(channelMessageId))
            elif category == CATEGORY_PLAYER:
                if affiliation == 'owner':
                    categoryDisplayName = localization.GetByLabel('UI/Chat/ChannelWindow/MyChannels')
                    category = CATEGORY_OWNED
                else:
                    categoryDisplayName = localization.GetByLabel('UI/Chat/ChannelWindow/PlayerChannels')
            else:
                categoryDisplayName = category
            if displayName in self.channelsByDisplayName:
                if category == CATEGORY_SYSTEM:
                    self.channelsByDisplayName[displayName] = channelId
            else:
                self.channelsByDisplayName[displayName] = channelId
            if category in (CATEGORY_LOCAL, CATEGORY_CORP):
                category = CATEGORY_SYSTEM
            _, channelsInCategory = channelsByCategory.get(category, ('', []))
            channelsInCategory.append((channelId, displayName))
            channelsByCategory[category] = (categoryDisplayName, channelsInCategory)

        headers = [localization.GetByLabel('UI/Chat/ChannelWindow/Name'), localization.GetByLabel('UI/Chat/ChannelWindow/Members')]
        nodeList = []
        for category, (categoryDisplayName, channels) in channelsByCategory.iteritems():
            nodeList.append((categoryDisplayName, GetFromClass(ListGroup, {'GetSubContent': GetSubContent,
              'label': categoryDisplayName,
              'sublevel': 0,
              'id': ('CHANNELSchannels', category),
              'groupItems': channels,
              'headers': headers,
              'iconMargin': 18,
              'showlen': 0,
              'state': 'locked',
              'allowCopy': 0,
              'showicon': 'res:/UI/Texture/WindowIcons/member.png',
              'posttext': localization.GetByLabel('UI/Chat/NumChannels', numChannels=len(channels)),
              'allowGuids': ['listentry.Group', 'listentry.XmppChannelField']})))

        nodeList.sort()
        contentList = [ item[1] for item in nodeList ]
        self.channelsScroll.Load(contentList=contentList, fixedEntryHeight=24, headers=headers)

    def JoinChannelFromBtn(self, _):
        displayName = self.input.GetValue()
        if displayName.strip() == '':
            eve.Message('LookupStringMinimum', {'minimum': 1})
            return
        eve.Message('ChannelTryingToJoin')
        channelName = self.channelsByDisplayName.get(displayName, None)
        if not channelName:
            reply = GetChatService().GetChannelByDisplayName(displayName)
            if reply:
                channelName = reply[0][0]
        if channelName:
            windowId = 'chatchannel_%s' % channelName
            wnd = Window.GetIfOpen(windowId)
            if wnd and not wnd.destroyed:
                wnd.Maximize()
                eve.Message('LSCChannelIsJoined', {'displayName': displayName})
                return
            GetChatService().JoinChannel(channelName)
        elif eve.Message('LSCChannelDoesNotExistCreate', {'displayName': displayName}, uiconst.YESNO) == uiconst.ID_YES:
            eve.Message('ChannelTryingToCreate')
            self.CreateChannelFromBtn()

    def CreateChannelFromBtn(self, *args):
        displayName = self.input.GetValue()
        displayName = StripBreaks(displayName)
        displayName = StripTags(displayName)
        displayName = displayName.strip()
        self.input.SetValue(displayName)
        if displayName == '':
            eve.Message('LookupStringMinimum', {'minimum': 1})
            return
        channelName = self.channelsByDisplayName.get(displayName, None)
        if not channelName:
            reply = GetChatService().GetChannelByDisplayName(displayName)
            if reply:
                channelName = reply[0][0]
        if channelName:
            windowId = 'chatchannel_%s' % channelName
            wnd = Window.GetIfOpen(windowId)
            if wnd and not wnd.destroyed:
                wnd.Maximize()
                eve.Message('LSCChannelIsJoined', {'displayName': displayName})
                return
            if eve.Message('LSCJoinInstead', {'displayName': displayName}, uiconst.YESNO) == uiconst.ID_YES:
                eve.Message('ChannelTryingToJoin')
                GetChatService().JoinChannel(channelName)
        else:
            eve.Message('ChannelTryingToCreate')
            channelName = GetChatService().CreateChannel(displayName)
            GetChatService().JoinChannel(channelName)
