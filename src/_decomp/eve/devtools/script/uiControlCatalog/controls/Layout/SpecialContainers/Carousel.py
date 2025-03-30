#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\SpecialContainers\Carousel.py
import appConst
from carbonui import uiconst
from eve.devtools.script.uiControlCatalog.sample import Sample
from eveui import Sprite
from inventorycommon import typeHelpers

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from carbonui.control.carousel import Carousel
        carousel = Carousel(parent=parent, align=uiconst.TOPLEFT, height=64, width=64)
        for typeID in [appConst.typeCredits,
         appConst.typeLoyaltyPoints,
         appConst.typeJaspet,
         appConst.typeVexor]:
            Sprite(parent=carousel, align=uiconst.TOLEFT, width=64, height=64, texturePath=typeHelpers.GetIconFile(typeID))

        carousel.InitializeButtons()


class Sample2(Sample):
    name = 'Faster'

    def sample_code(self, parent):
        from carbonui.control.carousel import Carousel
        carousel = Carousel(parent=parent, align=uiconst.TOPLEFT, height=64, width=64, scrollSpeed=0.5, interval=1.0)
        for typeID in [appConst.typeCredits, appConst.typeLoyaltyPoints, appConst.typeJaspet]:
            Sprite(parent=carousel, align=uiconst.TOLEFT, width=64, height=64, texturePath=typeHelpers.GetIconFile(typeID))

        carousel.InitializeButtons()
