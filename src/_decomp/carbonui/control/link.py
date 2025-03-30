#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\link.py
import blue
import eveformat
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.mathUtil import LtoI
from carbonui.util.bunch import Bunch
from carbon.common.script.util import commonutils
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from chroma import Color

class Link(Container):
    isDragObject = True

    def GetDragData(self, *args):
        if getattr(self, 'url', None) and getattr(self, 'linkText', None):
            entry = Bunch()
            entry.__guid__ = 'TextLink'
            entry.url = self.url
            entry.displayText = self.linkText
            return [entry]

    @classmethod
    def PrepareDrag(cls, dragContainer, dragSource, *args):
        dragData = dragContainer.dragData[0]
        displayText = eveformat.truncate_text_ignoring_tags(dragData.displayText, 24, '...')
        from carbonui.control.label import LabelOverride as Label
        label = Label(parent=dragContainer, text=commonutils.StripTags(displayText), align=uiconst.TOPLEFT, bold=True)
        Fill(parent=dragContainer, color=(0, 0, 0, 0.3), padding=(-10, -2, -10, -2))
        dragContainer.width = label.textwidth
        dragContainer.height = label.textheight
        return (2, label.textheight)

    def OnClick(self, *args):
        if self.url:
            PlaySound(uiconst.SOUND_BUTTON_CLICK)
            self.ClickLink(self, self.url.replace('&amp;', '&'))

    def ClickLink(self, parent, URL):
        linkUsed = self.ResolveInGameLink(parent, URL)
        if not linkUsed:
            self.UrlHandlerDelegate(parent, 'GoTo', URL)

    def GetStandardLinkHint(self, url, **kwds):
        link_service = sm.GetService('link')
        if link_service.has_handler_for(url):
            return link_service.get_hint(url)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        pass

    def GetLinkFormat(self, url, linkState = None, linkStyle = None):
        linkState = linkState or uiconst.LINK_IDLE
        linkStyle = linkStyle or uiconst.LINKSTYLE_REGULAR
        color = sm.GetService('link').get_color(url, linkState, linkStyle)
        fmt = Bunch()
        fmt.color = LtoI(Color.from_any(color).as_argb_int32())
        fmt.underline = linkState in (uiconst.LINK_ACTIVE, uiconst.LINK_HOVER)
        fmt.bold = linkStyle != uiconst.LINKSTYLE_UNBOLD
        return fmt

    def FormatLinkParams(self, params, linkState = None, linkStyle = None):
        if 'priorUrlColor' not in params:
            params.priorUrlColor = params.color
        if 'priorUrlBold' not in params:
            params.priorUrlBold = params.bold
        if 'priorUrlItalic' not in params:
            params.priorUrlItalic = params.italic
        if 'priorUrlUnderline' not in params:
            params.priorUrlUnderline = params.underline
        linkFmt = self.GetLinkFormat(params.url, linkState, linkStyle)
        if linkFmt.color is not None:
            params.color = linkFmt.color
        if linkFmt.underline is not None:
            params.underline = linkFmt.underline
        if linkFmt.bold is not None:
            params.bold = linkFmt.bold
        if linkFmt.italic is not None:
            params.italic = linkFmt.italic

    def ResolveInGameLink(self, parent, URL):
        link_service = sm.GetService('link')
        if link_service.has_handler_for(URL):
            link_service.resolve(URL, self.GetLinkText(parent))
            return True
        return False

    def GetLinkText(self, parent):
        from carbonui.control.label import LabelCore
        if isinstance(parent, LabelCore):
            drag_link_data = getattr(parent, '_dragLinkData', None)
            link_text = drag_link_data[0] if drag_link_data is not None else None
        else:
            link_text = getattr(parent, 'linkText', None)
        return StripTags(link_text)

    def CanOpenBrowser(self, *args):
        return False

    def GetMenu(self):
        if getattr(self, 'url', None) is None:
            return []
        return self.GetLinkMenu(self, self.url)

    def GetLinkMenu(self, parent, url):
        link_service = sm.GetService('link')
        if link_service.has_handler_for(url):
            return link_service.get_menu(url) or []
        return []

    def ValidateURL(self, URL):
        badURLs = self.GetBadUrls()
        for badURL in badURLs:
            if URL.startswith(badURL):
                return False

        return True

    def GetBadUrls(self, *args):
        return ['shellexec:', 'cmd:/']

    def CopyUrl(self, url):
        blue.pyos.SetClipboardData(url)

    def UrlHandlerDelegate(self, parent, funcName, args):
        handler = getattr(self, 'URLHandler', None)
        if not handler and getattr(parent, 'sr', None) and getattr(parent.sr, 'node', None):
            handler = getattr(parent.sr.node, 'URLHandler', None)
        if handler:
            func = getattr(handler, funcName, None)
            if func:
                apply(func, (args,))
                return
        self.ResolveInGameLink(parent, args)
