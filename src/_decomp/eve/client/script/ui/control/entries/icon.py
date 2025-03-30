#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\icon.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.glowSprite import GlowSprite

class IconEntry(SE_BaseClassCore):
    __guid__ = 'listentry.IconEntry'
    __params__ = ['label']

    def Startup(self, *etc):
        self.labelleft = 32
        self.ConstructLabel()
        self.ConstructIcon()

    def ConstructLabel(self):
        self.sr.label = EveLabelMedium(text='', parent=self, left=self.labelleft, top=0, width=512, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)

    def ConstructIcon(self):
        self.icon = GlowSprite(icon='ui_5_64_10', parent=self, pos=(0, 0, 0, 0), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)

    def Load(self, node):
        self.sr.node = node
        data = node
        self.sr.label.width = data.Get('maxLabelWidth', 512)
        self.sr.label.text = data.label
        if data.Get('icon', None) is not None:
            self.icon.LoadIcon(data.icon, ignoreSize=True)
        iconoffset = node.Get('iconoffset', 0)
        self.icon.left = iconoffset
        iconsize = node.Get('iconsize', 32)
        labeloffset = node.Get('labeloffset', 0)
        self.icon.width = self.icon.height = iconsize
        self.sr.label.left = iconsize + iconoffset + labeloffset
        if node.Get('selectable', 1) and node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        if node.Get('hint', None):
            self.hint = data.hint

    def OnClick(self, *args):
        if self.sr.node and self.sr.node.Get('selectable', 1):
            self.BlinkOff()
            self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)

    def GetHeight(self, *args):
        node, width = args
        iconsize = node.Get('height', node.Get('iconsize', 32))
        node.height = iconsize
        return node.height

    def Blink(self, hint = None, force = 1, blinkcount = 3, frequency = 750, bright = 0):
        blink = self.GetBlink()
        blink.state = uiconst.UI_DISABLED
        sm.GetService('ui').BlinkSpriteRGB(blink, min(1.0, self.r * (1.0 + bright * 0.25)), min(1.0, self.g * (1.0 + bright * 0.25)), min(1.0, self.b * (1.0 + bright * 0.25)), frequency, blinkcount, passColor=1)

    def BlinkOff(self):
        if self.sr.Get('blink', None) is not None:
            self.sr.blink.state = uiconst.UI_HIDDEN

    def GetBlink(self):
        if self.sr.Get('blink', None):
            return self.sr.blink
        blink = Fill(bgParent=self, name='hiliteFrame', state=uiconst.UI_HIDDEN, color=(0.28, 0.3, 0.35, 1.0), align=uiconst.TOALL)
        self.sr.blink = blink
        self.r = 0.28
        self.g = 0.3
        self.b = 0.35
        return self.sr.blink

    @classmethod
    def GetCopyData(cls, node):
        return node.label

    def OnMouseEnter(self, *args):
        super(IconEntry, self).OnMouseExit(*args)
        self.icon.OnMouseEnter()

    def OnMouseExit(self, *args):
        super(IconEntry, self).OnMouseExit(*args)
        self.icon.OnMouseExit()


class Icons(SE_BaseClassCore):
    __guid__ = 'listentry.Icons'
    __params__ = ['icons']
    default_showHilite = False

    def Load(self, node):
        i = 0
        for each in node.icons:
            icon, color, identifier, click = each
            if i >= len(self.children):
                newicon = Container(parent=self, pos=(0,
                 0,
                 self.height,
                 self.height), name='glassicon', state=uiconst.UI_NORMAL, align=uiconst.RELATIVE)
                newicon.sr.icon = Sprite(parent=newicon, name='picture', state=uiconst.UI_NORMAL, align=uiconst.TOALL)
                newicon.sr.color = Fill(parent=newicon, name='color', state=uiconst.UI_DISABLED, color=(0.45, 0.5, 1.0, 1.0))
                newicon.left = i * self.height
            else:
                newicon = self.children[i]
            if icon:
                newicon.sr.icon.LoadTexture(icon)
                newicon.sr.icon.state = uiconst.UI_DISABLED
            else:
                newicon.sr.icon.state = uiconst.UI_HIDDEN
            if color:
                newicon.sr.color.SetRGBA(*color)
                newicon.sr.color.state = uiconst.UI_DISABLED
            else:
                newicon.sr.color.state = uiconst.UI_HIDDEN
            newicon.OnClick = (click, newicon)
            newicon.OnMouseEnter = self.OnIconMouseEnter
            newicon.sr.identifier = identifier
            i += 1

    def OnIconMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
