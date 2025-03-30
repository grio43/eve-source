#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Sprites\Sprite.py
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = Sprite.__doc__

    def sample_code(self, parent):
        from carbonui.primitives.sprite import Sprite
        Sprite(name='MySprite', parent=parent, texturePath='res:/ui/Texture/corpLogoLibs/large/465.png', width=256, height=256)


class Sample2(Sample):
    name = 'Color'
    description = 'Whenever possible, we should color assets in code rather than baking it into the asset to maintain flexibility'

    def sample_code(self, parent):
        from carbonui.primitives.sprite import Sprite
        Sprite(name='MySprite', parent=parent, texturePath='res:/ui/Texture/corpLogoLibs/large/465.png', width=256, height=256, color=eveColor.CRYO_BLUE)


class Sample3(Sample):
    name = 'Color overlay'
    description = 'Applies color to grayscale pixels, so that 50% gray picks up color fully, but 0% (black) and 100% (white) gray pixels pick up no color'

    def sample_code(self, parent):
        from carbonui.primitives.sprite import Sprite
        from carbonui.uiconst import SpriteEffect
        Sprite(name='MySprite', parent=parent, texturePath='res:/ui/Texture/corpLogoLibs/large/465.png', spriteEffect=SpriteEffect.COLOROVERLAY, effectOpacity=1.0, color=eveColor.HOT_RED, width=256, height=256)


class Sample4(Sample):
    name = 'Soft Light effect'
    description = "Desaturates and applies color, such that grey pixels pick up color, but black and white pixels don't"

    def sample_code(self, parent):
        from carbonui.primitives.sprite import Sprite
        from carbonui.uiconst import SpriteEffect
        Sprite(name='MySprite', parent=parent, texturePath='res:/ui/Texture/corpLogoLibs/large/465.png', spriteEffect=SpriteEffect.SOFTLIGHT, color=eveColor.HOT_RED, saturation=1.0, effectOpacity=1.0, width=256, height=256)


class Sample5(Sample):
    name = 'Tiling'

    def sample_code(self, parent):
        from carbonui.primitives.sprite import Sprite
        Sprite(name='MySprite', parent=parent, texturePath='res:/ui/Texture/corpLogoLibs/465.png', width=512, height=512, tileX=True, tileY=True)


class Sample6(Sample):
    name = 'Masking'

    def sample_code(self, parent):
        from carbonui.primitives.sprite import Sprite
        from carbonui.uiconst import SpriteEffect
        Sprite(name='MySprite', parent=parent, texturePath='res:/ui/Texture/corpLogoLibs/large/465.png', textureSecondaryPath='res:/UI/Texture/classes/Animations/radialGradient.png', spriteEffect=SpriteEffect.MODULATE, width=256, height=256)


class Sample7(Sample):
    name = 'Glow'

    def sample_code(self, parent):
        from carbonui.primitives.sprite import Sprite
        Sprite(name='MySprite', parent=parent, texturePath='res:/ui/Texture/corpLogoLibs/large/465.png', outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.7, width=256, height=256)


class Sample8(Sample):
    name = 'Addative Blending'
    description = 'Often useful to achieve effects like burned out glow, or to make achieve readibility with dynamic backgrounds'

    def sample_code(self, parent):
        from carbonui.primitives.sprite import Sprite
        from carbonui.uiconst import BlendMode
        Sprite(name='MySprite', parent=parent, texturePath='res:/ui/Texture/corpLogoLibs/large/465.png', blendMode=BlendMode.ADD, width=256, height=256)
