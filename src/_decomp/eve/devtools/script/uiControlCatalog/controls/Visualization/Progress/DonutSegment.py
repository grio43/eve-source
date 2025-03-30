#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Progress\DonutSegment.py
from eve.client.script.ui import eveColor
import math
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):

    def sample_code(self, parent):
        from eve.client.script.ui.control.donutSegment import DonutSegment
        donutSegment = DonutSegment(parent=parent, colorStart=eveColor.SILVER_GREY, colorEnd=eveColor.LIME_GREEN, lineWidth=10, radius=50)
        while not donutSegment.destroyed:
            donutSegment.SetValue(0.0, duration=1.2, sleep=True)
            donutSegment.SetValue(1.0, duration=1.2, sleep=True)


class Sample2(Sample):

    def sample_code(self, parent):
        from eve.client.script.ui.control.donutSegment import DonutSegment
        from carbonui.uiconst import SpriteEffect
        donutSegment = DonutSegment(parent=parent, colorStart=eveColor.HOT_RED, colorEnd=eveColor.DUSKY_ORANGE, lineWidth=20, radius=100, isClockwise=False, startAngle=math.pi, spriteEffect=SpriteEffect.COPY, textureWidth=20.0, texturePath='res:/UI/Texture/classes/shipTree/lines/unlocked.png')
        while not donutSegment.destroyed:
            donutSegment.SetValue(0.5, duration=1.2, sleep=True)
            donutSegment.SetValue(1.0, duration=1.2, sleep=True)


class Sample3(Sample):

    def sample_code(self, parent):
        from eve.client.script.ui.control.donutSegment import DonutSegment
        DonutSegment(parent=parent, colorStart=eveColor.AQUA_BLUE, colorEnd=eveColor.PRIMARY_BLUE, lineWidth=20, radius=100, isClockwise=False, angle=math.pi / 3, textureWidth=20.0)
