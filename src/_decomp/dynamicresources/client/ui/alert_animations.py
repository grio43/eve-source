#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ui\alert_animations.py
import locks
import trinity
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.util.color import Color
from uthread2 import StartTasklet

class TimerDissapearAnimation(Transform):
    CIRCLE_TEXTURE_PATH = 'res:/UI/Texture/circle_with_border_blurred.png'
    MASK_TEXTURE_PATH = 'res:/UI/Texture/circle_with_border_inverted.png'
    default_endRadius = 50
    default_width = 258
    default_height = 258
    default_gaugeLineWidth = 20
    default_scalingCenter = (0.5, 0.5)
    default_scaleUpDuration = 0.25
    default_scaleOutDuration = 0.5

    def ApplyAttributes(self, attributes):
        Transform.ApplyAttributes(self, attributes)
        self.endRadius = attributes.get('endRadius', self.default_endRadius)
        self.gaugeLineWidth = attributes.get('gaugeLineWidth', self.default_gaugeLineWidth)
        self.scaleUpDuration = attributes.get('scaleUpDuration', self.default_scaleUpDuration)
        self.scaleOutDuration = attributes.get('scaleOutDuration', self.default_scaleOutDuration)
        self.transitionLock = attributes.get('transitionLock')
        StartTasklet(self.ConstructLayout)

    def ConstructLayout(self):
        with locks.TempLock(self.transitionLock):
            self.sprite = Sprite(parent=self, align=uiconst.CENTER, width=self.endRadius * 2 + self.gaugeLineWidth / 2, height=self.endRadius * 2 + self.gaugeLineWidth / 2, texturePath=self.CIRCLE_TEXTURE_PATH, textureSecondaryPath=self.MASK_TEXTURE_PATH, spriteEffect=trinity.TR2_SFX_MODULATE, idx=0, opacity=0.7)
            self.sprite.scalingCenterSecondary = (0.5, 0.5)
            self.sprite.scaleSecondary = (4, 4)
            animations.Tr2DScaleTo(self, startScale=(0, 0), endScale=(1, 1), duration=self.scaleUpDuration)
            animations.MorphVector2(self.sprite, 'scaleSecondary', startVal=(4, 4), endVal=(1.0, 1.0), loops=1, curveType=uiconst.ANIM_LINEAR, duration=self.scaleOutDuration, sleep=True)
            self.sprite.display = False


class TimerAppearAnimation(Transform):
    CIRCLE_TEXTURE_PATH = 'res:/UI/Texture/circle_with_border_blurred.png'
    MASK_TEXTURE_PATH = 'res:/UI/Texture/circle_with_border_inverted.png'
    default_startRadius = 5
    default_endRadius = 50
    default_width = 258
    default_height = 258
    default_gaugeLineWidth = 20
    default_dashCount = 6
    default_scalingCenter = (0.5, 0.5)
    default_timerColor = Color.GRAY
    default_dashSizeFactor = 8.0
    default_gaugeFillDuration = 1
    default_scaleUpDuration = 0.25
    default_gaugeFadeInDuration = 1
    default_scaleOutDuration = 0.5

    def ApplyAttributes(self, attributes):
        Transform.ApplyAttributes(self, attributes)
        self.startRadius = attributes.get('startRadius', self.default_startRadius)
        self.endRadius = attributes.get('endRadius', self.default_endRadius)
        self.gaugeLineWidth = attributes.get('gaugeLineWidth', self.default_gaugeLineWidth)
        self.dashCount = attributes.get('dashCount', self.default_dashCount)
        self.timerColor = attributes.get('timerColor', self.default_timerColor)
        self.dashSizeFactor = attributes.get('dashSizeFactor', self.default_dashSizeFactor)
        self.gaugeFillDuration = attributes.get('gaugeFillDuration', self.default_gaugeFillDuration)
        self.scaleUpDuration = attributes.get('scaleUpDuration', self.default_scaleUpDuration)
        self.gaugeFadeInDuration = attributes.get('gaugeFadeInDuration', self.default_gaugeFadeInDuration)
        self.scaleOutDuration = attributes.get('scaleOutDuration', self.default_scaleOutDuration)
        self.transitionLock = attributes.get('transitionLock')
        StartTasklet(self.ConstructLayout)

    def ConstructLayout(self):
        with locks.TempLock(self.transitionLock):
            self.sprite = Sprite(parent=self, align=uiconst.CENTER, width=self.endRadius * 2 + self.gaugeLineWidth / 2, height=self.endRadius * 2 + self.gaugeLineWidth / 2, texturePath=self.CIRCLE_TEXTURE_PATH, textureSecondaryPath=self.MASK_TEXTURE_PATH, spriteEffect=trinity.TR2_SFX_MODULATE, idx=0, opacity=0.7)
            self.sprite.scalingCenterSecondary = (0.5, 0.5)
            self.sprite.scaleSecondary = (4, 4)
            self.BeginAnimations()

    def BeginAnimations(self):
        animations.Tr2DScaleTo(self, startScale=(0, 0), endScale=(1, 1), duration=self.scaleUpDuration)

        def hide_sprite():
            self.sprite.display = False

        animations.MorphVector2(self.sprite, 'scaleSecondary', startVal=(4, 4), endVal=(1.0, 1.0), loops=1, curveType=uiconst.ANIM_LINEAR, duration=self.scaleOutDuration, callback=hide_sprite)
