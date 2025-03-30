#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\client\message_list_entry.py
import logging
import re
import sys
import types
import blue
import evelink.client
import evetypes
import eveicon
from carbonui import Align, TextColor
import carbonui.const as uiconst
from carbonui.primitives.fill import Fill
from chatutil.filter import CleanText
from eve.client.script.ui import eveColor
from menu import MenuLabel
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import GetTimeParts
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.control.link import Link
from carbonui.primitives.container import Container
from carbonui.primitives.gradientSprite import Gradient2DSprite
from carbonui.control.buttonIcon import ButtonIcon
from chatutil import LinkURLs
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import Label
from eve.common.script.sys.idCheckers import IsCharacter
from eve.common.lib import appConst as const
from eveservices.menu import StartMenuService, GetMenuService
from chat.client.const import SLASH_EMOTE_STRING, ChatMessageMode
logger = logging.getLogger(__name__)
PICTURE_SIZE = {ChatMessageMode.TEXT_ONLY: 0,
 ChatMessageMode.SMALL_PORTRAIT: 32,
 ChatMessageMode.LARGE_PORTRAIT: 64}

class ChatMessageListEntry(SE_BaseClassCore):
    default_clipChildren = True
    defaultTextProps = {'autoDetectCharset': True,
     'linkStyle': uiconst.LINKSTYLE_REGULAR,
     'state': uiconst.UI_NORMAL,
     'align': uiconst.TOTOP,
     'padRight': 4,
     'padLeft': 4}

    def ApplyAttributes(self, attributes):
        self._highlight_background = None
        super(ChatMessageListEntry, self).ApplyAttributes(attributes)

    def Startup(self, *args):
        self.text = None
        self.backgroundGradient = None
        self._expander = None
        self.picParent = Container(parent=self, align=uiconst.TOPLEFT, width=32, height=32)
        self.pic = Icon(parent=self.picParent, align=uiconst.TOALL)

    def Load(self, node):
        self.picloaded = 0
        textProps = self.GetTextProperties(node)
        if not self.text:
            mouseOverWordCallback = node.mouseOverWordCallback
            collectWordsInStack = node.collectWordsInStack
            self.text = Label(parent=self, idx=0, mouseOverWordCallback=mouseOverWordCallback, collectWordsInStack=collectWordsInStack, **textProps)
            self.text.GetMenu = self.GetMenu
        charname, text = ChatMessageListEntry.GetCharacterAndTextForNode(node)
        self.text.text = text
        if node.mode and charname:
            self.picParent.width = self.picParent.height = PICTURE_SIZE[node.mode]
            self.picParent.state = uiconst.UI_NORMAL
            self.LoadPortrait()
        else:
            self.picParent.state = uiconst.UI_HIDDEN
        self.AddEntryBackground(node.charid)

    @staticmethod
    def GetCharacterAndTextForNode(node):
        if node.sender is None or type(node.sender) in types.StringTypes:
            return (None, node.text)
        nodetext = LinkURLs(node.text)
        try:
            charname = cfg.eveowners.Get(node.sender).name
        except ValueError:
            charname = None

        if nodetext.startswith('/slash'):
            color = '0xb200dddd'
            nodetext = nodetext[1:]
            showCharname = False
        else:
            color = node.color
            showCharname = True
        isEmote = False
        if nodetext.startswith(SLASH_EMOTE_STRING):
            nodetext = nodetext.replace(SLASH_EMOTE_STRING, '', 1)
            isEmote = True
        timestr = ''
        if settings.user.ui.Get('timestampchat', 0):
            year, month, wd, day, hour, min, sec, ms = GetTimeParts(node.timestamp)
            timestr = '<color=%s>[%02d:%02d:%02d]</color> ' % (color,
             hour,
             min,
             sec)
        if charname:
            if node.sender == const.ownerSystem:
                info = 'showinfo:5//%s' % (session.solarsystemid or session.solarsystemid2)
            else:
                info = 'showinfo:1373//%d' % node.charid
            if showCharname:
                linkStyle = uiconst.LINKSTYLE_UNBOLD
                if isEmote:
                    prefix = '<url:%s linkStyle=%s><color=%s>* %s</color></url>' % (info,
                     linkStyle,
                     color,
                     charname)
                else:
                    prefix = '<url:%s linkStyle=%s><color=%s>%s</color></url> &gt; ' % (info,
                     linkStyle,
                     color,
                     charname)
            else:
                prefix = '<url:%s/></url>' % info
        else:
            prefix = '<color=%s>%s</color> &gt; ' % (color, node.sender)
        if node.undelivered:
            color = '0xb2505050'
            nodetext += ' - undelivered'
        text = '%s<color=%s>%s%s</color>' % (timestr,
         color,
         prefix,
         nodetext)
        return (charname, text)

    def LoadHighlightedText(self, text, *args):
        if self.sr.node.text.lower().find(text.lower()) >= 0:
            self.isHighlighted = True
            strippedText = StripTags(self.text.text)
            pattern = re.compile(text, re.IGNORECASE)
            textWithEffect = '<b><color=red>' + text + '</color></b>'
            newText = pattern.sub(textWithEffect, strippedText)
            self.text.text = newText

    def RemoveHighlightedText(self, *args):
        if getattr(self, 'isHighlighted', False):
            self.Load(self.sr.node)

    def LoadPortrait(self, orderIfMissing = True):
        if self is None or self.destroyed:
            return
        if self.sr.node.charid == const.ownerSystem:
            self.pic.LoadIcon('ui_6_64_7')
            return
        size = PICTURE_SIZE[self.sr.node.mode]
        if sm.GetService('photo').GetPortrait(self.sr.node.charid, size, self.pic, orderIfMissing, callback=True):
            self.picloaded = 1

    @staticmethod
    def GetDynamicHeight(node, width):
        props = ChatMessageListEntry.GetTextProperties(node)
        width = width - props['padLeft'] - props['padRight']
        maxLines = getattr(node, 'maxLines', None)
        _, text = ChatMessageListEntry.GetCharacterAndTextForNode(node)
        _, textHeight = Label.MeasureTextSize(text, width=width, **props)
        if maxLines:
            maxText = '\n'.join((str(x) for x in range(maxLines)))
            _, maxTextHeight = Label.MeasureTextSize(maxText, width=width, **props)
            if textHeight > maxTextHeight:
                if maxLines == 2:
                    textHeight = maxTextHeight
                else:
                    textHeight = Label.MeasureTextSize('\n.', width=width, **props)[1]
                node.showExpander = True
            else:
                node.showExpander = False
        if node.mode == ChatMessageMode.TEXT_ONLY:
            return textHeight
        elif node.mode == ChatMessageMode.SMALL_PORTRAIT:
            return max(PICTURE_SIZE[node.mode], textHeight + props['padTop'] * 2)
        else:
            return max(PICTURE_SIZE[node.mode], textHeight + props['padTop'] * 2)

    def GetMenu(self):
        m = []
        mouseOverUrl = self.text.GetMouseOverUrl()
        characterMenuAdded = False
        if mouseOverUrl:
            try:
                parsed = evelink.parse_show_info_url(mouseOverUrl)
            except Exception:
                logger.debug('failed to parse show info link %s', mouseOverUrl, exc_info=True)
                sys.exc_clear()
                m = Link().GetLinkMenu(self.text, mouseOverUrl.replace('&amp;', '&'))
            else:
                if parsed.item_id:
                    m = StartMenuService().GetMenuFromItemIDTypeID(parsed.item_id, parsed.type_id, includeMarketDetails=True)
                    if evetypes.GetGroupID(parsed.type_id) == const.groupCharacter:
                        characterMenuAdded = True
                        if not parsed.item_id != session.charid:
                            m += [None, (MenuLabel('UI/Chat/ReportIskSpammer'), lambda *args: sm.GetService('chat').report_isk_spammer(parsed.item_id, self.sr.node.channelid))]
                else:
                    m = Link().GetLinkMenu(self.text, mouseOverUrl.replace('&amp;', '&'))
        m += [None, (MenuLabel('UI/Common/Copy'), self.CopyText)]
        if self.sr.node.channelMenu:
            m += self.sr.node.channelMenu()
        senderID = self.sr.node.sender
        if not characterMenuAdded and senderID and IsCharacter(senderID):
            m += [None, (MenuLabel('UI/Common/Pilot', {'character': senderID}), ('isDynamic', GetMenuService().CharacterMenu, (senderID,)))]
        return m

    def CopyText(self):
        node = self.sr.node
        timestr = ''
        if settings.user.ui.Get('timestampchat', 0):
            year, month, wd, day, hour, min, sec, ms = GetTimeParts(node.timestamp)
            timestr = '[%02d:%02d:%02d] ' % (hour, min, sec)
        who = node.sender
        try:
            who = cfg.eveowners.Get(who).name
        except ValueError:
            pass

        text = node.text.replace('&gt;', '>').replace('&amp;', '&')
        text = CleanText(text)
        t = '%s%s > %s\r\n' % (timestr, who, text)
        blue.pyos.SetClipboardData(t)

    def AddEntryBackground(self, charid):
        if charid == session.charid and settings.user.ui.Get('myMsgHighlighted', 0):
            if self._highlight_background is None:
                self._highlight_background = Fill(bgParent=self, color=eveColor.CRYO_BLUE[:3] + (0.1,), idx=0)

    def AddBackgroundGradient(self, color):
        self.backgroundGradient = Gradient2DSprite(bgParent=self, idx=0, name='gradient2d', rgbHorizontal=[0, 1], rgbVertical=[0, 1], rgbDataHorizontal=[color, color], rgbDataVertical=[color, color], rgbInterp='bezier', alphaHorizontal=[0, 1], alphaDataHorizontal=[1.0, 0.2], alphaVertical=[0, 0.5, 1], alphaDataVertical=[0.35, 0.05, 0.0], textureSize=16)
        return self.backgroundGradient

    def AddFrameGradient(self, color):
        frameGradient = Gradient2DSprite(parent=None, idx=0, name='frameGradient2d', rgbHorizontal=[0, 1], rgbVertical=[0, 1], rgbDataHorizontal=[color, color], rgbDataVertical=[color, color], rgbInterp='linear', alphaHorizontal=[0, 0.5, 1], alphaDataHorizontal=[1.0, 0.8, 0.15], alphaVertical=[0, 0.5, 1], alphaDataVertical=[1.0, 0.8, 0.15], textureSize=16)
        self.picParent.background.insert(0, frameGradient)

    def _OnSizeChange_NoBlock(self, width, height):
        super(ChatMessageListEntry, self)._OnSizeChange_NoBlock(width, height)
        self._UpdateExpander()

    def _UpdateExpander(self):
        if self.sr.node.showExpander:
            if self._expander is None:
                self._expander = ButtonIcon(parent=self, align=Align.TORIGHT, idx=0, texturePath=eveicon.expand, height=32, width=32, iconSize=16, iconColor=TextColor.SECONDARY, func=self._ExpandEntry)
        elif self._expander is not None:
            self._expander.Close()
            self._expander = None

    def _ExpandEntry(self, *args, **kwargs):
        if self.sr.node.maxLines:
            self.sr.node.maxLines = None
            self.sr.node.showExpander = False
            if self._expander is not None:
                self._expander.Close()
                self._expander = None
        self.sr.node.scroll.UpdateNodesWidthAndPosition(forceUpdate=True)
        self.sr.node.scroll.UpdatePosition()

    @classmethod
    def GetTextProperties(cls, node):
        textProps = cls.defaultTextProps
        textProps['fontsize'] = node.fontsize
        textProps['letterspace'] = node.letterspace
        if node.mode == ChatMessageMode.TEXT_ONLY:
            textProps['padTop'] = 0
            textProps['padLeft'] = 0
            textProps['specialIndent'] = 8
        else:
            textProps['padTop'] = 4
            textProps['specialIndent'] = 0
            portrait_size = PICTURE_SIZE[node.mode]
            if node.mode == ChatMessageMode.SMALL_PORTRAIT:
                textProps['padLeft'] = portrait_size + 4
            else:
                textProps['padLeft'] = portrait_size + 4
        return textProps

    @classmethod
    def MarkMessageUndelivered(cls, node):
        node.undelivered = True
        if node.panel:
            node.panel.Load(node)
