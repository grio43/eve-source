#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Vector\VectorLineTrace.py
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from carbonui import uiconst
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = VectorLineTrace.__doc__

    def sample_code(self, parent):
        from carbonui.primitives.vectorlinetrace import VectorLineTrace
        line = VectorLineTrace(name='line', parent=parent, lineWidth=4.0, width=250, height=250)
        line.AddPoint((0, 0), eveColor.SAND_YELLOW)
        line.AddPoint((250, 0), eveColor.CHERRY_RED)
        line.AddPoint((250, 250), eveColor.LEAFY_GREEN)
        line.AddPoint((0, 250), eveColor.CRYO_BLUE)


class Sample2(Sample):
    name = 'Textured'

    def sample_code(self, parent):
        from carbonui.primitives.vectorlinetrace import VectorLineTrace
        from carbonui.uiconst import SpriteEffect
        line = VectorLineTrace(name='line', parent=parent, spriteEffect=SpriteEffect.COPY, textureWidth=10.0, texturePath='res:/UI/Texture/classes/shipTree/lines/unlocked.png', lineWidth=10.0, width=250, height=250)
        line.AddPoint((0, 0))
        line.AddPoint((250, 0))
        line.AddPoint((250, 250))
        line.AddPoint((0, 250))


class Sample3(Sample):
    name = 'Animated'

    def sample_code(self, parent):
        from carbonui.primitives.vectorlinetrace import VectorLineTrace
        from carbonui.uiconst import SpriteEffect
        line = VectorLineTrace(name='line', parent=parent, spriteEffect=SpriteEffect.COPY, textureWidth=10.0, texturePath='res:/UI/Texture/classes/shipTree/lines/unlocked.png', lineWidth=10.0, width=250, height=250)
        line.AddPoint((0, 0))
        line.AddPoint((125, 0))
        line.AddPoint((125, 250))
        line.AddPoint((250, 250))
        uicore.animations.MorphScalar(line, 'start', 0.0, 0.5, duration=2.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        uicore.animations.MorphScalar(line, 'end', 1.0, 0.5, duration=2.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
