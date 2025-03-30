#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ui\main_bank_hacking_timer.py
import math
import trinity
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.util.color import Color
from dynamicresources.client.ui.alert_animations import TimerDissapearAnimation, TimerAppearAnimation
from dynamicresources.client.ui.ess_info_panel_ui_const import TRANSITION_LOCK, MAIN_BANK_ACTIVE_BAR_COLOR
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eveservices.menu import GetMenuService
from eveui import Sprite

class MainBankHackingTimer(ContainerAutoSize):
    default_alignMode = uiconst.TOPLEFT
    default_radius = 20
    default_lineWidth = 5
    default_value = 0
    default_animate = True
    PORTRAIT_SIZE = 28

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.radius = attributes.get('radius', MainBankHackingTimer.default_radius)
        self.lineWidth = attributes.get('lineWidth', MainBankHackingTimer.default_lineWidth)
        self.animate = attributes.get('animate', MainBankHackingTimer.default_animate)
        self.characterID = attributes.characterID
        self.value = attributes.get('value', MainBankHackingTimer.default_value)
        self.startAngle = -math.pi / 2
        if self.animate:
            self.ConstructLayout()
            self.AnimateIn()
        else:
            self.ConstructLayout()

    def AnimateIn(self):
        self.animatedGaugeBackground = TimerAppearAnimation(parent=self, width=self.radius * 2, height=self.radius * 2, endRadius=self.radius, gaugeLineWidth=self.lineWidth, align=uiconst.TOPLEFT, timerColor=Color(*Color.WHITE).SetAlpha(0.2).GetRGBA(), left=2, top=2, transitionLock=TRANSITION_LOCK, value=0, idx=0)
        self.ConstructPortrait()

    def AnimateOut(self, sleep = False):
        animations.FadeOut(self.linkedCharSpriteCont, duration=0.25)
        animations.Tr2DScaleTo(self.gauge, startScale=(1, 1), endScale=(1.1, 1.1), duration=0.25, sleep=sleep)
        animations.FadeOut(self.gauge, duration=0.25, sleep=sleep)
        TimerDissapearAnimation(parent=self, align=uiconst.TOPLEFT, width=self.radius * 2, height=self.radius * 2, endRadius=self.radius, left=3, top=3, idx=0, transitionLock=TRANSITION_LOCK)

    def ConstructLayout(self):
        startingOpacity = 0.0 if self.animate else 1.0
        self.gauge = GaugeCircular(parent=self, radius=self.radius + 2, lineWidth=self.lineWidth, startAngle=self.startAngle, align=uiconst.TOPLEFT, colorStart=Color(*MAIN_BANK_ACTIVE_BAR_COLOR).GetRGBA(), colorEnd=Color(*MAIN_BANK_ACTIVE_BAR_COLOR).GetRGBA(), colorBg=Color(*Color.WHITE).SetAlpha(0.2).GetRGBA(), idx=0, showMarker=False, state=uiconst.UI_DISABLED, value=0, opacity=startingOpacity)
        self.SetValue(self.value)
        if not self.animate:
            self.ConstructPortrait(animate=False)

    def ConstructPortrait(self, animate = True):
        self.linkedCharSpriteCont = Transform(parent=self, align=uiconst.TOPLEFT, width=self.PORTRAIT_SIZE, height=self.PORTRAIT_SIZE, top=8, left=8, opacity=0)
        self.smallCircleSprite = Sprite(name='smallCircleSprite', parent=self.linkedCharSpriteCont, opacity=0.0, width=self.PORTRAIT_SIZE + 3, height=self.PORTRAIT_SIZE + 3, texturePath='res:/UI/Texture/classes/ess/linkedPortraitFrame/smallCircle.png')
        self.linkedCharacterSprite = Sprite(name='linkedCharacterSprite', parent=self.linkedCharSpriteCont, width=self.PORTRAIT_SIZE, height=self.PORTRAIT_SIZE, idx=0, textureSecondaryPath='res:/UI/Texture/classes/ess/circleMask.png', spriteEffect=trinity.TR2_SFX_MASK, state=uiconst.UI_NORMAL)
        menuSvc = GetMenuService()
        self.linkedCharacterSprite.GetMenu = lambda *args: menuSvc.GetMenuForOwner(self.characterID)
        self.photoSvc = sm.StartService('photo')
        self.photoSvc.GetPortrait(self.characterID, size=32, sprite=self.linkedCharacterSprite)
        if animate:
            animations.FadeIn(self.linkedCharSpriteCont, timeOffset=0.25, duration=0.25)
        else:
            self.linkedCharSpriteCont.opacity = 1

    def SetValue(self, value):
        self.value = value
        self.gauge.SetValue(value)
