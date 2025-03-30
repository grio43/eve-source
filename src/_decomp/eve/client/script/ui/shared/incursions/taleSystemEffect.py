#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\incursions\taleSystemEffect.py
from carbonui.primitives.sprite import Sprite

class TaleSystemEffect(Sprite):
    defult_opacity = 0.75

    def ApplyAttributes(self, attributes):
        super(TaleSystemEffect, self).ApplyAttributes(attributes)
        self.isScalable = attributes.isScalable

    def IsEffectScalable(self):
        return self.isScalable

    def SetInfluence(self, influence):
        if not self.IsEffectScalable() or influence < 1.0:
            self.opacity = 0.75
        else:
            self.opacity = 0.25
