#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Sprites\StretchSprites.py
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from eve.devtools.script.uiControlCatalog import sampleUtil
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = StretchSpriteHorizontal.__doc__

    def construct_sample(self, parent):
        cont = sampleUtil.GetHorizCollapsableCont(parent, 300, 10, None)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
        StretchSpriteHorizontal(parent=parent, align=uiconst.TOTOP, texturePath='res:/UI/Texture/classes/ShipTree/InfoBubble/backBottom.png', height=6)


class Sample2(Sample):
    name = 'Configuring edge size'

    def construct_sample(self, parent):
        cont = sampleUtil.GetHorizCollapsableCont(parent, 300, 30, None)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
        StretchSpriteHorizontal(parent=parent, align=uiconst.TOBOTTOM, texturePath='res:/UI/Texture/classes/Notifications/newItemsBadge.png', height=30, leftEdgeSize=10, rightEdgeSize=14)


class Sample3(Sample):
    name = 'Vertical'

    def construct_sample(self, parent):
        cont = sampleUtil.GetVertCollapsableCont(parent, 64, 250, None)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.stretchspritevertical import StretchSpriteVertical
        StretchSpriteVertical(parent=parent, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/icons/1_64_3.png', width=64, topEdgeSize=32, bottomEdgeSize=32)
