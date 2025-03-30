#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Vector\VectorLine.py
from carbonui import uiconst
from carbonui.primitives.vectorline import VectorLine
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = VectorLine.__doc__

    def sample_code(self, parent):
        from carbonui.primitives.vectorline import VectorLine
        VectorLine(name='line', parent=parent, translationFrom=(0, 0), translationTo=(250, 250), width=250, height=250)


class Sample2(Sample):
    name = 'Color'

    def sample_code(self, parent):
        from carbonui.primitives.vectorline import VectorLine
        VectorLine(name='line', parent=parent, translationFrom=(0, 0), translationTo=(250, 250), colorFrom=eveColor.CRYO_BLUE, colorTo=eveColor.CHERRY_RED, widthFrom=0.0, widthTo=20.0, width=250, height=250)


class Sample3(Sample):
    name = 'Textured'

    def sample_code(self, parent):
        from carbonui.primitives.vectorline import VectorLine
        from carbonui.uiconst import SpriteEffect
        VectorLine(name='line', parent=parent, spriteEffect=SpriteEffect.COPY, texturePath='res:/UI/Texture/classes/shipTree/lines/inProgress.png', textureWidth=6.0, translationFrom=(0, 0), translationTo=(250, 250), widthFrom=10.0, widthTo=10.0, width=250, height=250)


class Sample4(Sample):
    name = 'Animated'

    def sample_code(self, parent):
        from carbonui.primitives.vectorline import VectorLine
        from carbonui.uiconst import SpriteEffect
        line = VectorLine(name='line', parent=parent, spriteEffect=SpriteEffect.COPY, texturePath='res:/UI/Texture/classes/shipTree/lines/inProgress.png', textureWidth=6.0, translationFrom=(0, 0), translationTo=(250, 250), widthFrom=10.0, widthTo=10.0, width=250, height=250)
        uicore.animations.MorphScalar(line, 'textureOffset', 0.0, 6.0, duration=2.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
