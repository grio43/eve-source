#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\circleView\innerCircles.py
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations

class InnerCircles(Sprite):
    default_name = 'InnerCircles'
    default_startScale = (1.0, 1.0)
    default_endScale = (2.0, 2.0)
    default_animDuration = 0.5

    def ApplyAttributes(self, attributes):
        super(InnerCircles, self).ApplyAttributes(attributes)
        self.isScaled = False
        self.startScale = attributes.get('startScale', self.default_startScale)
        self.endScale = attributes.get('endScale', self.default_endScale)
        self.animDuration = attributes.get('animDuration', self.default_animDuration)

    def ScaleDown(self):
        if self.isScaled:
            return
        animations.Tr2DScaleTo(self, startScale=self.startScale, endScale=self.endScale, duration=self.animDuration)
        animations.FadeOut(self, duration=self.animDuration)
        self.isScaled = True

    def ScaleUp(self):
        if not self.isScaled:
            return
        animations.Tr2DScaleTo(self, startScale=self.endScale, endScale=self.startScale, duration=self.animDuration)
        animations.FadeIn(self, duration=self.animDuration)
        self.isScaled = False
