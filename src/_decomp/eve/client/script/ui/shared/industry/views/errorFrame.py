#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\views\errorFrame.py
from carbonui import const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore

class ErrorFrame(Sprite):
    default_name = 'ErrorFrame'
    default_opacity = 0.0
    default_opacityHigh = 0.35
    default_opacityLow = 0.3
    default_texturePath = 'res:/UI/Texture/Classes/Industry/Output/hatchPattern.png'
    default_tileX = True
    default_tileY = True
    default_color = (1.0, 0.275, 0.0, 1.0)

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        self.opacityHigh = attributes.get('opacityHigh', self.default_opacityHigh)
        self.opacityLow = attributes.get('opacityLow', self.default_opacityLow)

    def Show(self, *args):
        Sprite.Show(self, *args)
        uicore.animations.FadeTo(self, self.opacityLow, self.opacityHigh, duration=3.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)

    def Hide(self, *args):
        Sprite.Hide(self, *args)
        uicore.animations.FadeOut(self, duration=0.3)
