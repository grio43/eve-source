#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\Containers\Transform.py
import carbonui.const as uiconst
import uthread2
from carbonui.primitives.sprite import Sprite
from math import pi
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Scaling'
    description = 'A Transform is a container that has the ability to transform all content within it'

    def sample_code(self, parent):
        from carbonui.primitives.transform import Transform
        myTransform = Transform(name='myTransform', parent=parent, align=uiconst.TOPLEFT, width=256, height=256, scalingCenter=(0.5, 0.5), scale=(0.5, 1.0), bgColor=eveColor.MATTE_BLACK)
        Sprite(name='Sprite1', parent=myTransform, texturePath='res:/UI/Texture/classes/ShipTree/factions/guristas.png', align=uiconst.TOPLEFT, width=128, height=128)
        Sprite(name='Sprite2', parent=myTransform, texturePath='res:/UI/Texture/classes/ShipTree/factions/minmatar.png', align=uiconst.BOTTOMRIGHT, width=128, height=128)


class Sample2(Sample):
    name = 'Rotation'

    def sample_code(self, parent):
        from carbonui.primitives.transform import Transform
        Transform(name='myTransform', parent=parent, align=uiconst.TOPLEFT, width=128, height=128, rotationCenter=(0.5, 0.5), rotation=pi / 4, bgTexturePath='res:/UI/Texture/classes/ShipTree/factions/guristas.png')


class Sample3(Sample):
    name = 'Animation'

    def sample_code(self, parent):
        from carbonui.primitives.transform import Transform
        transform = Transform(name='myTransform', parent=parent, align=uiconst.TOPLEFT, width=128, height=128, rotationCenter=(0.5, 0.5), scalingCenter=(0.5, 0.5), rotation=pi / 4, bgTexturePath='res:/UI/Texture/classes/ShipTree/factions/guristas.png')
        animations.Tr2DFlipIn(transform)
        uthread2.sleep(2.0)
        animations.Tr2DScaleOut(transform)
