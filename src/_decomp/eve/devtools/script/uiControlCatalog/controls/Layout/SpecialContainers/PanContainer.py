#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\SpecialContainers\PanContainer.py
from eve.client.script.ui import eveColor
from carbonui.primitives.frame import Frame
from carbonui import uiconst
from eve.devtools.script.uiControlCatalog.sample import Sample
from eveui import Sprite

class Sample1(Sample):
    name = 'Basic'
    description = 'PanContainer allows for left-dragging content around IF content exceeds horizontal and/or vertical boundaries.'

    def sample_code(self, parent):
        from eve.client.script.ui.control.panContainer import PanContainer
        panCont = PanContainer(parent=parent, align=uiconst.TOPLEFT, width=300, height=300, panSpeed=15, panAmount=4)
        Frame(bgParent=panCont, color=eveColor.MATTE_BLACK)
        Sprite(name='MySprite', parent=panCont.mainCont, texturePath='res:/ui/Texture/classes/ShipTree/factionBG/SOE.png', align=uiconst.CENTER, width=700, height=800)


class Sample2(Sample):
    name = 'Vertical only'

    def sample_code(self, parent):
        from eve.client.script.ui.control.panContainer import PanContainer
        panCont = PanContainer(parent=parent, align=uiconst.TOPLEFT, width=400, height=300, panSpeed=15, panAmount=4)
        Frame(bgParent=panCont, color=eveColor.MATTE_BLACK)
        Sprite(name='MySprite', parent=panCont.mainCont, texturePath='res:/ui/Texture/classes/ShipTree/factionBG/SOE.png', align=uiconst.CENTER, width=350, height=400)
