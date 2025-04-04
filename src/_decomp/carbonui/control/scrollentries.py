#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\scrollentries.py
import carbonui.const as uiconst
import localization
import log
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.control.inlines import get_inline_deco_class
from carbonui.control.label import LabelCore
from carbonui.control.link import Link
from carbonui.fontconst import DEFAULT_FONTSIZE
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from carbonui.util.stringManip import GetAsUnicode
from carbonui.util.various_unsorted import GetBrowser, MapIcon
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from menu import MenuLabel

class SE_BaseClassCore(Container):
    labelLeftDefault = uiconst.LABELTABMARGIN
    __guid__ = 'uicontrols.SE_BaseClassCore'
    default_name = 'scrollentry'
    default_align = uiconst.TOTOP
    default_className = 'SE_Generic'
    default_showHilite = True
    default_highlightClass = ListEntryUnderlay
    sound_hover = uiconst.SOUND_ENTRY_HOVER
    sound_select = uiconst.SOUND_ENTRY_SELECT

    def ApplyAttributes(self, attributes):
        if 'className' not in attributes:
            attributes.className = self.default_className
        Container.ApplyAttributes(self, attributes)
        self._hiliteFill = None
        self._isSelected = False
        self._showHilite = attributes.get('showHilite', self.default_showHilite)
        self._highlightClass = attributes.get('highlightClass', self.default_highlightClass)

    def GetTooltipPanelClassInfo(self):
        if self.sr.node and self.sr.node.tooltipPanelClassInfo:
            return self.sr.node.tooltipPanelClassInfo

    def GetTooltipPointer(self):
        if self.sr.node and self.sr.node.tooltipPanelClassInfo:
            return getattr(self.sr.node.tooltipPanelClassInfo, 'tooltipPointer', None)
        return uiconst.POINT_RIGHT_2

    def ConstructHiliteFill(self):
        if not self._hiliteFill:
            self._hiliteFill = self._highlightClass(name='selectionHighlight', bgParent=self)

    def ShowHilite(self, animate = True):
        if not self._showHilite:
            return
        self.ConstructHiliteFill()
        self._hiliteFill.set_hovered(True, animate)

    def OnMouseEnter(self, *args):
        if self.sound_hover and self._showHilite:
            PlaySound(self.sound_hover)
        self.ShowHilite()

    def HideHilite(self, animate = True):
        if self._hiliteFill:
            self._hiliteFill.set_hovered(False, animate)

    def OnMouseExit(self, *args):
        self.HideHilite()

    def Select(self, animate = True):
        if self._isSelected:
            return
        self.ConstructHiliteFill()
        self._isSelected = True
        self._hiliteFill.Select(animate)

    def Deselect(self, animate = True):
        if not self._isSelected:
            return
        if self._hiliteFill:
            self._hiliteFill.Deselect(animate)
        self._isSelected = False

    def IsMouseInsideEntry(self):
        if uicore.uilib.mouseOver != self and not uicore.uilib.mouseOver.IsUnder(self):
            return False
        return True

    @classmethod
    def GetCopyData(cls, node):
        return ''


class SE_SpaceCore(SE_BaseClassCore):
    __params__ = ['height']
    default_showHilite = False

    def Load(self, node):
        self.sr.node = node

    def GetDynamicHeight(node, width):
        return node.height


class SE_GenericCore(SE_BaseClassCore):
    __guid__ = 'uicontrols.SE_GenericCore'
    __params__ = ['label']

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        if uicore.fontHandler:
            labelClass = uicore.fontHandler.defaultLabelClass
        else:
            labelClass = LabelCore
        self.sr.label = labelClass(name='text', text='', parent=self, pos=(self.labelLeftDefault,
         0,
         0,
         0), state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, maxLines=1)

    def Load(self, node):
        self.hint = node.get('hint', '')
        self.confirmOnDblClick = node.get('confirmOnDblClick', 0)
        if node.get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        self.sr.label.busy = True
        self.sr.label.left = 5 + 16 * node.get('sublevel', 0)
        self.sr.label.maxLines = node.get('maxLines', 1)
        self.sr.label.letterspace = node.get('letterspace', 0)
        self.sr.label.shadow = node.get('letterspace', None)
        if node.fontStyle:
            self.sr.label.fontStyle = node.fontStyle
        if node.fontsize:
            self.sr.label.fontsize = node.fontsize
        if node.fontcolor:
            self.sr.label.SetRGBA(*node.fontcolor)
        self.sr.label.busy = False
        self.sr.label.text = node.label
        if node.get('disabled', None):
            self.opacity = 0.5
            self.state = uiconst.UI_DISABLED
        else:
            self.opacity = 1.0
            self.state = uiconst.UI_NORMAL
        if node.get('OnDblClick', None) or getattr(self, 'confirmOnDblClick', None):
            self.EnableDblClick()
        else:
            self.DisableDblClick()

    def GetDynamicHeight(node, width):
        height = uicore.font.GetTextHeight(node.label, width=width - 5 + 16 * node.get('sublevel', 0), fontStyle=node.get('fontStyle', None), fontsize=node.get('fontsize', DEFAULT_FONTSIZE), letterspace=node.get('letterspace', 0), maxLines=node.get('maxLines', 1)) + 4
        return height

    def OnMouseHover(self, *args):
        if self.sr.get('node', None) and self.sr.node.get('OnMouseHover', None):
            self.sr.node.OnMouseHover(self)

    def OnMouseEnter(self, *args):
        SE_BaseClassCore.OnMouseEnter(self, *args)
        if self.sr.get('node', None) and self.sr.node.get('OnMouseEnter', None):
            self.sr.node.OnMouseEnter(self)

    def OnMouseExit(self, *args):
        SE_BaseClassCore.OnMouseExit(self, *args)
        if self.sr.get('node', None) and self.sr.node.get('OnMouseExit', None):
            self.sr.node.OnMouseExit(self)

    def OnClick(self, *args):
        if self.sr.get('node', None):
            if self.sr.node.get('OnClick', None):
                self.sr.node.OnClick(self)

    def EnableDblClick(self):
        self.OnDblClick = self.DblClick

    def DisableDblClick(self):
        self.OnDblClick = None

    def DblClick(self, *args):
        if self.sr.node:
            self.sr.node.scroll.SelectNode(self.sr.node)
            if self.sr.node.get('OnDblClick', None):
                self.sr.node.OnDblClick(self)
            elif getattr(self, 'confirmOnDblClick', None):
                uicore.registry.Confirm(self)

    def OnMouseDown(self, *args):
        SE_BaseClassCore.OnMouseDown(self, *args)
        self.sr.node.scroll.SelectNode(self.sr.node)
        uicore.Message('ListEntryClick')
        if self.sr.get('node', None) and self.sr.node.get('OnMouseDown', None):
            self.sr.node.OnMouseDown(self)

    def OnMouseUp(self, *args):
        SE_BaseClassCore.OnMouseUp(self, *args)
        if self.sr.get('node', None) and self.sr.node.get('OnMouseUp', None):
            self.sr.node.OnMouseUp(self)

    def GetMenu(self):
        if self.sr.get('node', None) and self.sr.node.get('OnGetMenu', None):
            return self.sr.node.OnGetMenu(self)
        return []


class SE_TextlineCore(SE_BaseClassCore, Link):
    __guid__ = 'uicontrols.SE_TextlineCore'
    default_showHilite = False
    USECACHE = False

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.gotSurface = False
        self.selectingtext = 0
        self.sr.textcursor = None
        self.sr.cursortimer = None
        self.sr.textselection = None
        self.Prepare_()

    def Prepare_(self, *args):
        self.sr.sprite = None
        self.sr.inlines = Container(name='inlines', parent=self)
        self.sr.links = Container(name='links', parent=self)
        self.sr.textselection = None

    def _OnClose(self):
        if self.destroyed:
            return
        self.Unload()
        if self.sr.node:
            for inline, x in self.sr.node.Get('inlines', []):
                control = inline.control
                if control and getattr(control, '__guid__', '').startswith('uicls.SE_'):
                    inline.control = None
                    control.Close()

        SE_BaseClassCore._OnClose(self)

    def Load(self, node):
        self.sr.links.Flush()
        self.leftM = 0
        self.sr.hiliteLinks = []
        self.RenderLine()
        self.LoadInlines()
        if not self or self.destroyed:
            return
        self.UpdateSelectionHilite()
        self.UpdateCursor()

    def OnChar(self, *args):
        pass

    def GetSprite(self):
        if self.sr.sprite is None:
            self.sr.sprite = Sprite(parent=self, state=uiconst.UI_PICKCHILDREN, spriteEffect=trinity.TR2_SFX_FONT, name='textSprite', idx=0)
            self.sr.sprite.OnCreate = self.OnCreate
            trinity.device.RegisterResource(self.sr.sprite)
            uicore.textObjects.add(self)
        return self.sr.sprite

    def OnCreate(self, dev):
        self.gotSurface = False
        if not self.destroyed and self.sr.node:
            self.Load(self.sr.node)

    def Unload(self):
        browser = GetBrowser(self)
        if browser and self.sr.inlines:
            for control in self.sr.inlines.children[:]:
                if not control:
                    continue
                if self.destroyed:
                    break
                control.state = uiconst.UI_HIDDEN
                control.SetParent(browser.sr.cacheContainer)
                if hasattr(control, 'Unload') and control.loaded:
                    control.Unload()

    def LoadInlines(self):
        self.Unload()
        if not self.sr.node.scroll:
            return
        scrollwidth = self.sr.node.scroll.GetContentWidth()
        linewidth = self.sr.node.Get('lineWidth', 0)
        lineHeight = self.sr.node.Get('maxBaseHeight', 12)
        leftMargin = self.sr.node.Get('lpush', self.sr.node.scroll.xmargin)
        rightMargin = self.sr.node.Get('rpush', self.sr.node.scroll.xmargin)
        self.sr.inlines.left = max(0, self.leftM)
        from carbonui.control.editutils import parser
        for inline, x in self.sr.node.Get('inlines', []):
            control = getattr(inline, 'control', None)
            if control and not control.destroyed:
                control.SetParent(self.sr.inlines)
            else:
                decoClass = get_inline_deco_class(inline.attrs.type)
                if not decoClass:
                    continue
                control = self.sr.node.scroll.GetInline(ScrollEntryNode(decoClass=decoClass, attrs=inline.attrs))
                if not self or self.destroyed:
                    return
                control.SetParent(self.sr.inlines)
                inline.control = control
            control.top = 0
            if inline.valign == parser.ALIGNMIDDLE:
                control.top = (self.height - inline.inlineHeight) / 2
            elif inline.valign in (parser.ALIGNBOTTOM, parser.ALIGNSUB):
                control.top = self.height - inline.inlineHeight
            elif inline.valign == parser.ALIGNBASELINE:
                control.top = self.sr.node.Get('maxBaseLine', 12) - inline.inlineHeight
            control.left = int(x)
            control.height = inline.inlineHeight
            control.width = inline.inlineWidth
            if self.IsCentered:
                control.SetAlign(uiconst.CENTER)
            if hasattr(control, 'Load') and not control.loaded:
                control.Load()
            control.state = uiconst.UI_NORMAL

    def RenderLine(self):
        if not self.sr.node.scroll:
            return
        scrollwidth = self.sr.node.scroll.GetContentWidth()
        if self.sr.node.glyphString:
            linewidth = self.ReverseScaleDpi(self.sr.node.glyphString.width)
        else:
            linewidth = 0
        self.IsCentered = False
        lineHeight = self.sr.node.Get('maxBaseHeight', 12)
        leftMargin = self.sr.node.Get('lpush', self.sr.node.scroll.xmargin)
        rightMargin = self.sr.node.Get('rpush', self.sr.node.scroll.xmargin)
        links = self.sr.node.Get('links', [])
        sprite = self.GetSprite()
        if self.sr.node.align == 'right':
            sprite.left = int(scrollwidth - rightMargin - linewidth)
        elif self.sr.node.align == 'center':
            self.IsCentered = True
        else:
            sprite.left = int(leftMargin)
        self.leftM = sprite.left
        if self.sr.node.glyphString:
            self.ApplyPixels(linewidth, lineHeight)
        else:
            sprite.state = uiconst.UI_HIDDEN
        for linkAttrs in links:
            self.StartLink(linkAttrs)

    class TexResBuf(object):
        __slots__ = ['width',
         'height',
         'data',
         'pitch']

        def __init__(self, tuple):
            self.data, self.width, self.height, self.pitch = tuple

    def ApplyPixels(self, linewidth, lineHeight):
        self.sr.xMin = 0
        if not self.sr.node.glyphString:
            return
        node = self.sr.node
        glyphstring = node.glyphString
        bBox = node.bBox
        sprite = self.GetSprite()
        if not bBox or bBox.Width() <= 0 or bBox.Height() <= 0:
            sprite.state = uiconst.UI_HIDDEN
            return
        surfaceWidth = bBox.Width()
        surfaceHeight = glyphstring.baseHeight
        sprite.left += bBox.xMin
        if glyphstring.shadow:
            sx, sy, scol = glyphstring.shadow[-1]
            surfaceWidth += sx
            surfaceHeight -= sy
        sprite.texture = None
        texturePrimary = trinity.Tr2Sprite2dTexture()
        texturePrimary.atlasTexture = uicore.uilib.CreateTexture(surfaceWidth, surfaceHeight)
        sprite.texture = texturePrimary
        sprite.useSizeFromTexture = True
        try:
            bufferData = texturePrimary.atlasTexture.LockBuffer()
        except AttributeError:
            if texturePrimary and texturePrimary.atlasTexture:
                texturePrimary.atlasTexture.UnlockBuffer()
                bufferData = texturePrimary.atlasTexture.LockBuffer()
            else:
                self.display = False
                return

        try:
            buf = SE_TextlineCore.TexResBuf(bufferData)
            trinity.fontMan.ClearBuffer(buf.data, buf.width, buf.height, buf.pitch)
            glyphstring.DrawToBuf(buf, -bBox.xMin, glyphstring.baseHeight - glyphstring.baseLine)
        finally:
            texturePrimary.atlasTexture.UnlockBuffer()

        sprite.top = 0
        self.sr.xMin = bBox.xMin
        sprite.state = uiconst.UI_PICKCHILDREN

    def StartLink(self, attrs):
        link = Link(parent=self.sr.links)
        link.left = self.GetSprite().left + attrs.left
        link.top = self.GetSprite().top
        link.height = self.height - self.GetSprite().top + 1
        link.width = attrs.width
        link.state = uiconst.UI_NORMAL
        link.SetAlign(uiconst.RELATIVE)
        link.hint = unicode(attrs.hint)
        link.OnMouseMove = self.OnMouseMove
        link.OnDblClick = self.OnDblClick
        link.OnMouseEnter = (self.OnLinkMouseEnter, link)
        link.OnMouseExit = (self.LinkExit, link)
        link.OnMouseDown = (self.LinkDown, link)
        link.OnMouseUp = (self.LinkUp, link)
        link.cursor = uiconst.UICORSOR_FINGER
        link.url = attrs.url
        link.sr.attrs = attrs
        link.name = 'textlink'
        link.URLHandler = self.sr.node.Get('URLHandler', None)
        link.linkText = attrs.linkText
        if not attrs.Get('draggable', True):
            link.DisableDrag()
        return link

    def OnLinkMouseEnter(self, link, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        return self.LinkEnter(link)

    def LinkDown(self, link, *args):
        for each in self.sr.hiliteLinks:
            each.Flush()

    def LinkUp(self, link, *args):
        if uicore.uilib.mouseOver == link:
            self.LinkEnter(link)

    def LinkEnter(self, link, *args):
        browser = GetBrowser(self)
        if browser and browser.sr.window and hasattr(browser.sr.window, 'ShowHint'):
            browser.sr.window.ShowHint(link.hint or link.url)
        self.sr.hiliteLinks = []
        for entry in self.sr.node.scroll.GetNodes():
            if not entry.panel:
                continue
            if entry.panel.sr.Get('links', None):
                for item in entry.panel.sr.links.children:
                    if item.name == 'textlink' and item.url == link.url:
                        self.HiliteLink(item)
                        self.sr.hiliteLinks.append(item)

    def HiliteLink(self, link):
        if link.sr.attrs.alink_color:
            c = link.sr.attrs.alink_color
            Fill(parent=link, color=(c[0],
             c[1],
             c[2],
             c[3] * 0.5), pos=(-2, 0, -2, 0))

    def LinkExit(self, link, *args):
        browser = GetBrowser(self)
        if browser and browser.sr.window and hasattr(browser.sr.window, 'ShowHint'):
            browser.sr.window.ShowHint('')
        for each in self.sr.hiliteLinks:
            each.Flush()

    def SelectionHandlerDelegate(self, funcName, args):
        handler = self.sr.node.Get('SelectionHandler', None)
        if handler:
            func = getattr(handler, funcName, None)
            if func:
                return apply(func, args)

    def GetMenu(self):
        self.sr.node.scroll.ShowHint('')
        return self.SelectionHandlerDelegate('GetMenuDelegate', (self.sr.node,))

    def OnMouseMove(self, *args):
        self.SelectionHandlerDelegate('OnMouseMoveDelegate', (self.sr.node,))

    def OnMouseDown(self, button, *args):
        if button == 0:
            self.SelectionHandlerDelegate('OnMouseDownDelegate', (self.sr.node,))

    def OnMouseUp(self, button, *args):
        if button == 0:
            self.SelectionHandlerDelegate('OnMouseUpDelegate', (self.sr.node,))

    def OnDropData(self, dragObj, nodes):
        self.SelectionHandlerDelegate('OnDropDataDelegate', (self.sr.node, nodes))

    def OnDragMove(self, nodes, *args):
        self.SelectionHandlerDelegate('OnDragMoveDelegate', (self.sr.node, nodes))

    def OnDragEnter(self, dragObj, nodes):
        self.SelectionHandlerDelegate('OnDragEnterDelegate', (self.sr.node, nodes))

    def OnDragExit(self, dragObj, nodes):
        self.SelectionHandlerDelegate('OnDragExitDelegate', (self.sr.node, nodes))

    def OnClick(self, *args):
        pass

    def OnDblClick(self, *args):
        self.SelectionHandlerDelegate('SelectWordUnderCursor', ())

    def OnTripleClick(self, *args):
        self.SelectionHandlerDelegate('SelectLineUnderCursor', ())

    def GetScrollAbove(self):
        from carbonui.control.scroll import Scroll
        item = self.parent
        while item:
            if isinstance(item, Scroll):
                return item
            item = item.parent

    def UpdateSelectionHilite(self):
        if not self.sr.node:
            return
        scrollAbove = self.GetScrollAbove()
        f = uicore.registry.GetFocus()
        if not scrollAbove or scrollAbove is not f or not trinity.app.IsActive():
            selectionAlpha = 0.125
        else:
            selectionAlpha = 0.25
        if self.sr.node.selectionStartIndex is not None:
            if self.sr.textselection is None:
                self.sr.textselection = Fill(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
            self.sr.textselection.SetAlpha(selectionAlpha)
            if self.sr.node.inlines:
                left = 0
                width = 0
                for inline, x in self.sr.node.inlines:
                    width = max(width, inline.width)

            else:
                left = uicore.font.GetWidthToIdx(self.sr.node, self.sr.node.selectionStartIndex)
                right = uicore.font.GetWidthToIdx(self.sr.node, self.sr.node.selectionEndIndex)
                width = uicore.ReverseScaleDpi(right - left)
                left = uicore.ReverseScaleDpi(left)
            self.sr.textselection.left = self.leftM + left
            self.sr.textselection.width = width
            self.sr.textselection.height = self.height
            self.sr.textselection.top = 0
            self.sr.textselection.state = uiconst.UI_DISABLED
        elif self.sr.textselection:
            self.sr.textselection.state = uiconst.UI_HIDDEN

    def UpdateCursor(self):
        if self.sr.node.cursorPos is not None:
            sprite = self.GetSprite()
            if self.sr.textcursor is None:
                self.sr.textcursor = Fill(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 1.0))
                self.sr.textcursor.top = 0
                self.sr.textcursor.width = 1
            left = uicore.font.GetWidthToIdx(self.sr.node, self.sr.node.cursorPos)
            self.sr.textcursor.left = self.sr.inlines.left + uicore.ReverseScaleDpi(left)
            self.sr.textcursor.height = self.height
            if self.sr.cursortimer is None:
                self.CursorBlink()
        elif self.sr.textcursor:
            self.sr.cursortimer = None
            self.sr.textcursor.state = uiconst.UI_HIDDEN

    def GetCursorOffset(self):
        if self.sr.textcursor:
            return self.sr.textcursor.left

    def CursorBlink(self):
        f = uicore.registry.GetFocus()
        if f is uicore.desktop or not trinity.app.IsActive():
            if self.sr.textcursor:
                self.sr.textcursor.state = uiconst.UI_HIDDEN
            self.sr.cursortimer = None
            return
        if f and self.IsUnder(f) and self.sr.node.cursorPos is not None and self.sr.textcursor is not None:
            self.sr.textcursor.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][self.sr.textcursor.state == uiconst.UI_HIDDEN]
            if self.sr.cursortimer is None:
                self.sr.cursortimer = AutoTimer(250, self.CursorBlink)
        else:
            self.sr.cursortimer = None
            self.sr.textcursor.state = uiconst.UI_HIDDEN

    def GetCopyData(self, fromIdx, toIdx):
        return uicore.font.GetNodeCopyData(self.sr.node, fromIdx, toIdx)

    def GetText(self, node):
        if node.rawText:
            return node.rawText
        text = ''.join([ glyphData[4] for glyphData in self.sr.node.glyphString if glyphData[4] != None ])
        node.rawText = text
        return text

    def GetDynamicHeight(node, width):
        return node.maxBaseHeight


class SE_ListGroupCore(SE_BaseClassCore):
    __guid__ = 'uicontrols.SE_ListGroupCore'
    ENTRYHEIGHT = 18

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.sr.entries = []
        self.dblclick = 0
        self.sr.expander = None
        self.sr.icon = None

    def _OnClose(self):
        SE_BaseClassCore._OnClose(self)
        self.sr.entries = None

    def Startup(self, *etc):
        self.Prepare_ExpanderIcon_()
        self.Prepare_Icon_()
        self.Prepare_Label_()
        self.Prepare_Selection_()
        self.Prepare_Background_()

    def Prepare_Label_(self):
        self.sr.labelClipper = Container(parent=self, pos=(0, 0, 0, 0), clipChildren=1)
        if uicore.fontHandler:
            labelClass = uicore.fontHandler.defaultLabelClass
        else:
            labelClass = LabelCore
        self.sr.label = labelClass(text='', parent=self.sr.labelClipper, pos=(self.labelLeftDefault,
         0,
         0,
         0), state=uiconst.UI_DISABLED, maxLines=1, idx=0, align=uiconst.CENTERLEFT, fontsize=12)

    def Prepare_Background_(self):
        self.sr.background = Fill(parent=self, color=(0.0, 0.0, 0.0, 0.5), pos=(0, 1, 0, 1))

    def Prepare_ExpanderIcon_(self):
        self.sr.expander = Sprite(align=uiconst.CENTERRIGHT, pos=(3, 0, 16, 16), parent=self, name='expander', idx=0)
        self.sr.expander.LoadIcon('ui_1_16_97')
        self.sr.expander.OnClick = self.Toggle

    def Prepare_Icon_(self):
        self.sr.icon = Sprite(align=uiconst.CENTERLEFT, pos=(0, 0, 16, 16), parent=self, idx=0, name='icon')

    def Load(self, node):
        self.sr.node = node
        self.sr.id = node.id
        self.sr.subitems = node.get('subitems', [])
        self.UpdateLabel()
        self.hint = node.get('hint', '')
        sublevel = node.get('sublevel', 0)
        self.sr.label.left = 20 + 16 * sublevel
        if self.sr.icon:
            self.sr.icon.left = 16 * sublevel
        if node.get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        if self.sr.expander:
            self.sr.expander.state = [uiconst.UI_NORMAL, uiconst.UI_HIDDEN][node.get('hideExpander', 0)]
        for k, v in node.get('labelstyle', {}).iteritems():
            setattr(self.sr.label, k, v)

        if self.sr.icon:
            icon = node.get('showicon', '')
            graphicID = node.get('graphicID', None)
            if graphicID:
                self.sr.icon.LoadIconByIconID(graphicID)
                self.sr.icon.SetSize(64, 64)
                self.sr.icon.state = uiconst.UI_DISABLED
            elif icon == 'hide':
                if self.sr.icon:
                    self.sr.icon.state = uiconst.UI_HIDDEN
                self.sr.label.left -= 12
            else:
                MapIcon(self.sr.icon, icon or 'ui_2_32_1')
                self.sr.icon.state = uiconst.UI_DISABLED
            self.sr.icon.width = self.sr.icon.height = 16
        if node.panel is not self or self is None:
            return
        self.ShowOpenState(uicore.registry.GetListGroupOpenState(self.sr.id, default=node.get('openByDefault', False)))

    def OnDropData(self, dragObj, nodes):
        if self == dragObj:
            return
        if self.sr.node.get('DropData', None):
            self.sr.node.DropData(self.sr.node.id, nodes)
            return
        ids = []
        myListGroupID = self.sr.node.id
        for node in nodes:
            guid = getattr(node, '__guid__', None)
            if guid not in self.sr.node.get('allowGuids', []):
                log.LogWarn('dropnode.__guid__ has to be listed in group.node.allowGuids', guid, self.sr.node.get('allowGuids', []))
                continue
            if not node.get('itemID', None):
                log.LogWarn('dropitem data has to have itemID')
                continue
            currentListGroupID = node.get('listGroupID', None)
            ids.append((node.itemID, currentListGroupID, myListGroupID))

        for itemID, currentListGroupID, myListGroupID in ids:
            if currentListGroupID and itemID:
                uicore.registry.RemoveFromListGroup(currentListGroupID, itemID)
            uicore.registry.AddToListGroup(myListGroupID, itemID)

        if self.sr.node.get('RefreshScroll', None):
            self.sr.node.RefreshScroll()
        else:
            self.RefreshScroll()

    def Clear(self):
        self.sr.node.panel = None

    def OnClick(self, *args, **kwargs):
        if not self.dblclick and not self.sr.node.get('disableToggle', 0):
            self.Toggle()
        if self.sr.node and self.sr.node.scroll and self.sr.node.selectGroup:
            self.sr.node.scroll.SelectNode(self.sr.node)
        if not self.destroyed and self.sr.get('node', None) and self.sr.node.get('OnClick', None):
            self.sr.node.OnClick(self, *args, **kwargs)

    def OnMouseDown(self, *args):
        SE_BaseClassCore.OnMouseDown(self, *args)
        if self.sr.get('node', None) and self.sr.node.get('OnMouseDown', None):
            self.sr.node.OnMouseDown(self)

    def RefreshScroll(self):
        node = self.sr.node
        if node.open:
            if not node.get('GetContentIDList', None) or not node.get('CreateEntry', None):
                return
            entries = node.subEntries
            if not entries:
                self.LoadContent()
                return
            addlist = []
            rmlist = []
            entryIDs = []
            self.sr.subitems = newcontent = self.sr.node.GetContentIDList(node.id)
            for entry in entries:
                if not entry.get('id', None):
                    if len(newcontent):
                        rmlist.append(entry)
                    continue
                if entry.id not in newcontent:
                    rmlist.append(entry)
                else:
                    entryIDs.append(entry.id)

            for id in newcontent:
                if id not in entryIDs:
                    newEntry = node.CreateEntry(id, node.sublevel + 1)
                    if newEntry is not None:
                        addlist.append(newEntry)

            if not len(newcontent) and len(node.subEntries) and node.subEntries[0].label != localization.GetByLabel('/Carbon/UI/Controls/Common/NoItem'):
                noItem = self.GetNoItemEntry()
                if noItem:
                    addlist.append(noItem)
            if self.sr.node:
                node.scroll.RemoveNodes(rmlist)
                entries += node.scroll.AddNodes(node.idx + 1, addlist)
                for entry in rmlist:
                    entries.remove(entry)

                node.subEntries = entries
        self.UpdateLabel()

    def GetNoItemEntry(self):
        return None

    def GetMenu(self):
        m = []
        node = self.sr.node
        if not node.get('showmenu', True):
            return m
        if not node.open:
            m += [(MenuLabel('/Carbon/UI/Common/Expand'), self.Toggle, ())]
        else:
            m += [(MenuLabel('/Carbon/UI/Common/Collapse'), self.Toggle, ())]
        if node.get('state', None) != 'locked':
            m += [(MenuLabel('/Carbon/UI/Controls/ScrollEntries/ChangeLabel'), self.ChangeLabel)]
            m += [(MenuLabel('/Carbon/UI/Controls/ScrollEntries/DeleteFolder'), self.DeleteFolder)]
        if node.get('MenuFunction', None):
            cm = node.MenuFunction(node)
            m += cm
        return m

    def ChangeLabel(self):
        newgroupName = self.GetNewGroupName()
        if not newgroupName or not self or self.destroyed:
            return
        if isinstance(newgroupName, dict):
            newgroupName = newgroupName['name']
        self.sr.node.label = newgroupName
        if self.sr.node.get('ChangeLabel', None):
            self.sr.node.ChangeLabel(self.sr.node.id, newgroupName)
        uicore.registry.ChangeListGroupLabel(self.sr.node.id, newgroupName)
        wnd = uicore.registry.GetWindow(unicode(self.sr.node.id))
        if wnd:
            wnd.SetCaption('     ' + newgroupName)
        if self.sr.node.get('DropCallback', None):
            self.sr.node.DropCallback(self.sr.node.id, None)
        if self.sr.node.get('RefreshScroll', None):
            self.sr.node.RefreshScroll()
        else:
            self.RefreshScroll()

    def GetNewGroupName(self):
        from eve.client.script.ui.util.utilWindows import NamePopup
        return NamePopup(localization.GetByLabel('/Carbon/UI/Controls/ScrollEntries/TypeInNewName'), localization.GetByLabel('/Carbon/UI/Controls/ScrollEntries/TypeInNewFolderName'))

    def DeleteFolder(self):
        id = self.sr.id
        if uicore.Message('ConfirmDeleteFolder', {}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
            if self.sr.node.get('DeleteCallback', None):
                self.sr.node.DeleteCallback(self.sr.subitems)
            if self.sr.node.get('DeleteFolder', None):
                self.sr.node.DeleteFolder(id)
            uicore.registry.DeleteListGroup(id)
            if not self or self.destroyed:
                return
            self.CloseWindow(unicode(id))
            if self.sr.node.get('DropCallback', None):
                self.sr.node.DropCallback(id, None)
            if self.sr.node.get('RefreshScroll', None):
                self.sr.node.RefreshScroll()

    def CloseWindow(self, windowID):
        wnd = uicore.registry.GetWindow(windowID)
        if wnd:
            wnd.Close()

    def OnDragEnter(self, dragObj, nodes):
        if self.sr.node.get('DragEnterCallback', None):
            self.sr.node.DragEnterCallback(self, dragObj)
        elif getattr(nodes[0], '__guid__', None) in self.sr.node.get('allowGuids', []):
            self.Select()

    def OnDragExit(self, dragObj, nodes):
        self.Deselect()

    def Toggle(self, *args):
        node = self.sr.node
        if not node or node.get('toggling', 0):
            return
        node.toggling = 1
        w = node.panel
        if not w:
            node.toggling = 0
            return
        node.open = not node.open
        if node.open:
            self.CloseWindow(unicode(node.id))
        if node.open:
            PlaySound(uiconst.SOUND_EXPAND)
        else:
            PlaySound(uiconst.SOUND_COLLAPSE)
        self.ShowOpenState(node.open)
        self.UpdateLabel()
        uicore.registry.SetListGroupOpenState(node.id, node.open)
        node.scroll.PrepareSubContent(node)
        if node.get('onToggle', None):
            node.onToggle()
        node.toggling = 0

    def ShowOpenState(self, open_):
        if self.sr.expander:
            if open_:
                MapIcon(self.sr.expander, 'ui_1_16_98')
            else:
                MapIcon(self.sr.expander, 'ui_1_16_97')

    def UpdateLabel(self):
        node = self.sr.node
        if 'cleanLabel' not in node:
            node.cleanLabel = node.label
        text = node.cleanLabel
        if self.sr.subitems is not None and node.get('showlen', 1):
            text = localization.GetByLabel('/Carbon/UI/Controls/ScrollEntries/LabelWithLength', label=text, length=len(self.sr.subitems))
        posttext = node.get('posttext', '')
        if posttext:
            text = localization.GetByLabel('/Carbon/UI/Controls/ScrollEntries/LabelWithPostfix', label=text, postfix=posttext)
        self.sr.label.text = text
        node.label = text


def ScrollEntryNode(**kw):
    data = Bunch(**kw)
    decoClass = data.get('decoClass', SE_GenericCore)
    data.decoClass = decoClass
    data.GetHeightFunction = getattr(decoClass, 'GetHeight', None)
    data.GetColumnWidthFunction = getattr(decoClass, 'GetColumnWidth', None)
    data.PreLoadFunction = getattr(decoClass, 'PreLoad', None)
    data.allowDynamicResize = getattr(decoClass, 'allowDynamicResize', False)
    if data.GetHeightFunction:
        data.GetHeightFunction = data.GetHeightFunction.im_func
    if data.PreLoadFunction:
        data.PreLoadFunction = data.PreLoadFunction.im_func
    if data.GetColumnWidthFunction:
        data.GetColumnWidthFunction = data.GetColumnWidthFunction.im_func
    if not data.charIndex and data.label:
        data.charIndex = GetAsUnicode(data.label).split('<t>')[0]
    if data.charIndex:
        data.charIndex = data.charIndex.lower()
    return data
