#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\buttonCharacterIcon.py
import trinity
from carbonui import const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.control.themeColored import SpriteThemeColored, FrameThemeColored
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.buttons.baseNeocomButton import BaseNeocomButton

class ButtonCharacterIcon(BaseNeocomButton):
    default_isDraggable = False

    def ApplyAttributes(self, attributes):
        super(ButtonCharacterIcon, self).ApplyAttributes(attributes)
        self.btnData.btnUI = self

    def ConstructIcon(self):
        self.icon = Sprite(parent=self, name='charPic', ignoreSize=True, align=uiconst.TOALL, state=uiconst.UI_DISABLED, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0, spriteEffect=trinity.TR2_SFX_SOFTLIGHT, effectOpacity=0.0)

    def UpdateIcon(self):
        for icon in (self.icon, self.blinkSprite):
            sm.GetService('photo').GetPortrait(session.charid, 256, icon)

    def BlinkOnce(self):
        self.blinkSprite.state = uiconst.UI_DISABLED
        uicore.animations.MorphScalar(self.icon, 'effectOpacity', 0.0, 1.0, duration=neocomConst.BLINK_INTERVAL, curveType=uiconst.ANIM_WAVE)
        uicore.animations.MorphScalar(self.icon, 'saturation', 1.0, 0.0, duration=neocomConst.BLINK_INTERVAL, curveType=uiconst.ANIM_WAVE)
        uicore.animations.MorphScalar(self.blinkSprite, 'glowBrightness', 0.0, 1.5, duration=neocomConst.BLINK_INTERVAL, curveType=uiconst.ANIM_WAVE, timeOffset=0.1)

    def ConstructBlinkSprite(self):
        self.blinkSprite = Sprite(parent=self, name='blinkSprite', state=uiconst.UI_HIDDEN, align=uiconst.TOALL, texturePath=self.icon.texturePath, outputMode=uiconst.OUTPUT_GLOW, blendMode=trinity.TR2_SBM_ADD, idx=0)

    def _AnimMouseEnter(self):
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, 0.1, duration=uiconst.TIME_ENTRY)

    def _AnimMouseExit(self):
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, 0.0, duration=uiconst.TIME_EXIT)

    def _AnimMouseDown(self):
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, 0.2, duration=uiconst.TIME_ENTRY)

    def _AnimMouseUp(self):
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, 0.1, duration=uiconst.TIME_ENTRY)

    def GetMenu(self):
        m = super(ButtonCharacterIcon, self).GetMenu()
        wnd = self.btnData.wndCls.GetIfOpen()
        if wnd:
            m += wnd.GetMenu()
        return m
