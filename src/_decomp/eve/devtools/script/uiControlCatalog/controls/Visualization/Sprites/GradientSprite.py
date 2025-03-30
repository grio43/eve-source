#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Sprites\GradientSprite.py
import carbonui.const as uiconst
import math
import eveicon
from carbonui import SpriteEffect
from carbonui.primitives.gradientSprite import GradientSprite
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = GradientSprite.__doc__

    def sample_code(self, parent):
        from carbonui.primitives.gradientSprite import GradientSprite
        GradientSprite(name='MyGradientSprite', align=uiconst.TOPLEFT, parent=parent, width=250, height=250, rgbData=((0, (1.0, 1.0, 1.0)), (0.2, eveColor.CRYO_BLUE[:3]), (1.0, eveColor.LIME_GREEN[:3])), alphaData=((0.0, 0.0), (1.0, 0.75)))


class Sample2(Sample):
    name = 'Rotated'

    def sample_code(self, parent):
        from carbonui.primitives.gradientSprite import GradientSprite
        GradientSprite(name='MyGradientSprite', align=uiconst.TOPLEFT, parent=parent, width=250, height=250, rgbData=((0.0, eveColor.CRYO_BLUE[:3]), (1.0, eveColor.CHERRY_RED[:3])), alphaData=((0.0, 0.0), (1.0, 1.0)), rotation=math.pi / 4)


class Sample3(Sample):
    name = 'Masked'

    def sample_code(self, parent):
        from carbonui.primitives.gradientSprite import GradientSprite
        GradientSprite(name='MyGradientSprite', align=uiconst.TOPLEFT, parent=parent, width=250, height=250, textureSecondaryPath=eveicon.minmatar_logo.resolve(256), spriteEffect=SpriteEffect.MODULATE, rgbData=((0.0, eveColor.CRYO_BLUE[:3]), (1.0, eveColor.CHERRY_RED[:3])), alphaData=((0.0, 0.3), (1.0, 1.0)), rotation=math.pi / 4)
