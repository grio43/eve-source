#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipModuleButton\extraBtnShipSlot.py
import carbonui.uiconst as uiconst
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.inflight.shipModuleButton.ramps import ShipModuleButtonRamps
GLOWCOLOR = (0.24, 0.67, 0.16, 0.75)

class ExtraBtnShipSlot(Container):
    default_pickRadius = 24
    default_width = 64
    default_height = 64
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.func = attributes.func
        self.btnDisabled = False
        self.buttonSprite = Sprite(name='buttonSprite', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 42, 42))
        self.ramps = ShipModuleButtonRamps(parent=self)
        self.hilite = Sprite(parent=self, name='hilite', padding=(10, 10, 10, 10), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotHilite.png', blendMode=trinity.TR2_SBM_ADDX2)
        self.hilite.display = False
        self.mainShape = Sprite(parent=self, name='mainshape', pos=(0, 0, 0, 0), align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotMainFull.png')
        self.glow = Sprite(parent=self, name='glow', padding=2, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/slotGlow.png', color=GLOWCOLOR)

    def OnClick(self, *args):
        if not self.btnDisabled and self.func:
            self.func()

    def OnMouseDown(self, *args):
        if self.btnDisabled:
            return
        Container.OnMouseDown(self, *args)
        self.top += 2

    def OnMouseUp(self, *args):
        if self.btnDisabled:
            return
        Container.OnMouseUp(self, *args)
        if self.destroyed:
            return
        self.top = 0

    def OnMouseEnter(self, *args):
        if self.destroyed:
            return
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self.SetHilite()

    def OnMouseExit(self, *args):
        self.RemoveHilite()
        self.OnMouseUp(None)

    def SetHilite(self):
        self.hilite.display = True

    def RemoveHilite(self):
        self.hilite.display = False

    def ShowGlow(self, glowColor):
        self.glow.SetRGBA(*glowColor)
        self.glow.display = True

    def HideGlow(self):
        self.glow.display = False

    def SetRampValue(self, value):
        if value > 0:
            self.ramps.display = True
        else:
            self.ramps.display = False
        self.ramps.SetRampValues(value)

    def SetButtonIcon(self, texturePath):
        self.buttonSprite.SetTexturePath(texturePath)

    def BlinkGlow(self, glowColor):
        self.glow.SetRGBA(*glowColor)
        uicore.animations.BlinkIn(self.glow, startVal=0, endVal=0.75, duration=1.0, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
        self.glow.display = True

    def StopBlinkGlow(self):
        uicore.animations.StopAnimation(self.glow, 'opacity')
        self.glow.display = False

    def DisableBtn(self):
        self.btnDisabled = True

    def EnableBtn(self):
        self.btnDisabled = False
