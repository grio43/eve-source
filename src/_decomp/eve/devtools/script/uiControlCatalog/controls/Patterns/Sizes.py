#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Patterns\Sizes.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Sizes'
    description = 'To maintain consistency in our layouts, we should strive to use ONLY the following values for margins/padding and container widths/heights wherever possible'

    def construct_sample(self, parent):
        cont = ContainerAutoSize(parent=parent, height=128)
        for size, color in ((4, eveColor.WHITE),
         (8, eveColor.CHERRY_RED),
         (16, eveColor.WARNING_ORANGE),
         (24, eveColor.LIME_GREEN),
         (32, eveColor.WARNING_ORANGE),
         (48, eveColor.PRIMARY_BLUE),
         (64, eveColor.LEAFY_GREEN),
         (96, eveColor.BURNISHED_GOLD),
         (128, eveColor.GUNMETAL_GREY)):
            c = Container(parent=cont, align=uiconst.TOLEFT, width=size, padRight=24)
            Fill(parent=c, align=uiconst.TOBOTTOM, height=size, color=color)
            eveLabel.EveLabelMedium(parent=c, align=uiconst.CENTERBOTTOM, top=-24, text=str(size))
