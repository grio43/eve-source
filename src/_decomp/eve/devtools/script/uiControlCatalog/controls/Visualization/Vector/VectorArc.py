#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Vector\VectorArc.py
import math
import carbonui.const as uiconst
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from carbonui.primitives.vectorarc import VectorArc
        VectorArc(parent=parent, pos=(100, 100, 200, 200), align=uiconst.CENTER, radius=100, fill=False, lineWidth=4, color=eveColor.LEAFY_GREEN, endAngle=3 * math.pi / 2)


class Sample2(Sample):
    name = 'Multiple segments'

    def sample_code(self, parent):
        from carbonui.primitives.vectorarc import VectorArc
        VectorArc(parent=parent, pos=(100, 100, 200, 200), align=uiconst.CENTER, radius=100, fill=False, lineWidth=8, color=eveColor.SMOKE_BLUE, endAngle=2.5 * math.pi / 2)
        VectorArc(parent=parent, pos=(100, 100, 200, 200), radius=100, align=uiconst.CENTER, fill=False, lineWidth=8, color=eveColor.CRYO_BLUE, endAngle=3 * math.pi / 2)


class Sample3(Sample):
    name = 'Animated'

    def sample_code(self, parent):
        from carbonui.primitives.vectorarc import VectorArc
        arc = VectorArc(parent=parent, pos=(100, 100, 200, 200), state=uiconst.UI_NORMAL, align=uiconst.CENTER, radius=100, fill=False, lineWidth=8, color=eveColor.CRYO_BLUE, endAngle=0.0)
        animations.MorphScalar(arc, 'endAngle', 0.0, 2 * math.pi, duration=3.0, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
