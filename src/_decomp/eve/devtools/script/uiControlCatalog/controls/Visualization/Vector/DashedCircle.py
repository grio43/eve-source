#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Vector\DashedCircle.py
import math
from carbonui import uiconst
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor, eveThemeColor
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from carbonui.primitives.vectorlinetrace import DashedCircle
        DashedCircle(parent=parent, radius=100)


class Sample2(Sample):
    name = 'As a gauge'

    def sample_code(self, parent):
        from carbonui.primitives.vectorlinetrace import DashedCircle
        circle = DashedCircle(parent=parent, radius=100, dashCount=20, dashSizeFactor=4.0, startAngle=math.radians(-90), range=math.radians(360), lineWidth=4)
        circle.end = 0.75
        DashedCircle(parent=parent, radius=100, dashCount=20, dashSizeFactor=4.0, startAngle=math.radians(-90), range=math.radians(360), lineWidth=3, startColor=eveThemeColor.THEME_TINT, endColor=eveThemeColor.THEME_TINT)


class Sample3(Sample):
    name = 'Animated with color'

    def sample_code(self, parent):
        from carbonui.primitives.vectorlinetrace import DashedCircle
        circle = DashedCircle(parent=parent, radius=100, dashCount=20, dashSizeFactor=4.0, startAngle=math.radians(-90), range=math.radians(360), lineWidth=4, startColor=eveColor.PRIMARY_BLUE, endColor=eveColor.LEAFY_GREEN)
        animations.MorphScalar(circle, 'end', 0.0, 1.0, duration=5.0, loops=-1, curveType=uiconst.ANIM_WAVE)
        DashedCircle(parent=parent, radius=100, dashCount=20, dashSizeFactor=4.0, startAngle=math.radians(-90), range=math.radians(360), lineWidth=3, startColor=eveThemeColor.THEME_TINT, endColor=eveThemeColor.THEME_TINT)
