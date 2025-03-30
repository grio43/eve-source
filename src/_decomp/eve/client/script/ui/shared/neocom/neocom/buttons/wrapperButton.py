#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\wrapperButton.py
import trinity
import localization
import blue
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.neocom.neocom import neocomConst, neocomSignals
OPACITY_HOVER = 0.05
GLOW_IDLE = 0.0
GLOW_HOVER = 0.6
GLOW_MOUSEDOWN = 0.9

class WrapperButton(Container):
    default_name = 'WrapperButton'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(WrapperButton, self).ApplyAttributes(attributes)
        self._openNeocomPanel = None
        self.blinkThread = None
        self.isBlinking = False
        self._ConstructBlinkSprite()
        self.ConstructNevActivityFill()
        self._ConstructHoverSprite()
        neocomSignals.on_blink_pulse.connect(self.ProcessNeocomBlinkPulse)

    def ConstructNevActivityFill(self):
        self.newActivityFill = Fill(name='newActivityFill', bgParent=self, color=eveColor.DUSKY_ORANGE, opacity=0.0, state=uiconst.UI_HIDDEN, padding=(1, 1, 0, 0))

    def _ConstructHoverSprite(self):
        self.mouseHoverSprite = Fill(bgParent=self, name='mouseHoverSprite', align=uiconst.TOALL, blendMode=trinity.TR2_SBM_ADD, opacity=0.0, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)

    def _ConstructBlinkSprite(self):
        self.blinkSprite = Fill(bgParent=self, name='blinkSprite', align=uiconst.TOALL, opacity=0.0, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, color=eveColor.DUSKY_ORANGE)

    def OnDblClick(self, *args):
        pass

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        animations.FadeTo(self.mouseHoverSprite, self.mouseHoverSprite.opacity, OPACITY_HOVER, duration=uiconst.TIME_ENTRY)
        animations.MorphScalar(self.mouseHoverSprite, 'glowBrightness', self.mouseHoverSprite.glowBrightness, GLOW_HOVER, duration=uiconst.TIME_ENTRY)
        if self.newActivityFill.display:
            animations.FadeTo(self.newActivityFill, self.newActivityFill.opacity, 0.0, duration=0.6, callback=self.newActivityFill.Hide)

    def OnMouseExit(self, *args):
        self.SetBlinkingOff()
        animations.FadeTo(self.mouseHoverSprite, self.mouseHoverSprite.opacity, 0.0, duration=uiconst.TIME_ENTRY)
        animations.MorphScalar(self.mouseHoverSprite, 'glowBrightness', self.mouseHoverSprite.glowBrightness, GLOW_IDLE, duration=uiconst.TIME_ENTRY)

    def OnMouseDown(self, btn):
        if btn != uiconst.MOUSELEFT:
            return
        animations.MorphScalar(self.mouseHoverSprite, 'glowBrightness', self.mouseHoverSprite.glowBrightness, GLOW_MOUSEDOWN, duration=uiconst.TIME_ENTRY)

    def OnMouseUp(self, btn):
        if btn != uiconst.MOUSELEFT:
            return
        animations.MorphScalar(self.mouseHoverSprite, 'glowBrightness', self.mouseHoverSprite.glowBrightness, GLOW_HOVER, duration=uiconst.TIME_ENTRY)

    def SetBlinkingOn(self, hint = None):
        self.isBlinking = True

    def SetBlinkingOff(self):
        self.isBlinking = False

    def BlinkOnce(self):
        if not self.newActivityFill.display:
            self.ShowNewActivityFill()
        animations.FadeTo(self.blinkSprite, 0.0, 0.5, duration=neocomConst.BLINK_INTERVAL, curveType=uiconst.ANIM_WAVE)
        uicore.animations.MorphScalar(self.blinkSprite, 'glowBrightness', 0.0, 1.0, duration=neocomConst.BLINK_INTERVAL, curveType=uiconst.ANIM_WAVE)

    def ShowNewActivityFill(self):
        self.newActivityFill.state = uiconst.UI_DISABLED
        animations.FadeTo(self.newActivityFill, self.newActivityFill.opacity, 0.6, duration=0.6)

    def ProcessNeocomBlinkPulse(self):
        if self.isBlinking:
            self.BlinkOnce()

    def GetMenu(self):
        return sm.GetService('neocom').GetMenu()
