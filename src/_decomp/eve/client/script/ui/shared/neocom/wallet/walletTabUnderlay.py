#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\walletTabUnderlay.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
MOUSE_UP_ALPHA = 0.1
MOUSE_OVER_ALPHA = 0.3
MOUSE_DOWN_ALPHA = 0.4
SELECTED_ALPHA = 0.5
ACCENT_MOUSE_OVER_ALPHA = 0.3
ACCENT_MOUSE_DOWN_ALPHA = 0.2

class WalletTabUnderlay(Container):
    default_fillColor = Color.GRAY

    def ApplyAttributes(self, attributes):
        super(WalletTabUnderlay, self).ApplyAttributes(attributes)
        self.isSelected = False
        self.isBlinking = False
        self.fillColor = attributes.get('fillColor', self.default_fillColor)
        self.ConstructBackground()
        self.ConstructSideAccent()

    def ConstructBackground(self):
        self.fillFrame = Frame(name='fillFrame', bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=self.fillColor, opacity=MOUSE_UP_ALPHA, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.5)

    def ConstructSideAccent(self):
        self.sideAccent = Sprite(name='sideAccent', parent=self, align=uiconst.TORIGHT_NOPUSH, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/DarkStyle/edgeDecoRight.png', width=11, opacity=MOUSE_UP_ALPHA)

    def SetFillColor(self, color):
        self.fillFrame.SetRGBA(*color)

    def OnMouseEnter(self, *args):
        if self.isSelected:
            return
        self.fillFrame.SetAlpha(MOUSE_OVER_ALPHA)
        self.sideAccent.SetAlpha(ACCENT_MOUSE_OVER_ALPHA)

    def OnMouseExit(self, *args):
        if self.isSelected:
            return
        self.fillFrame.SetAlpha(MOUSE_UP_ALPHA)
        self.sideAccent.SetAlpha(MOUSE_UP_ALPHA)

    def OnMouseDown(self, *args):
        if self.isSelected:
            return
        self.fillFrame.SetAlpha(MOUSE_DOWN_ALPHA)
        self.sideAccent.SetAlpha(ACCENT_MOUSE_DOWN_ALPHA)

    def OnMouseUp(self, *args):
        if self.isSelected:
            return
        self.fillFrame.SetAlpha(MOUSE_UP_ALPHA)

    def Blink(self, loops = 1):
        self.isBlinking = True

    def StopBlink(self):
        self.isBlinking = False

    def Select(self):
        if self.isSelected:
            return
        self.fillFrame.SetAlpha(SELECTED_ALPHA)
        self.sideAccent.SetAlpha(ACCENT_MOUSE_OVER_ALPHA)
        self.isSelected = True

    def Deselect(self):
        if not self.isSelected:
            return
        self.fillFrame.SetAlpha(MOUSE_UP_ALPHA)
        self.sideAccent.SetAlpha(MOUSE_UP_ALPHA)
        self.isSelected = False
