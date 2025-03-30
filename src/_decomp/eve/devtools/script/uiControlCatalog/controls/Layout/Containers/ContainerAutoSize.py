#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\Containers\ContainerAutoSize.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = ContainerAutoSize.__doc__

    def sample_code(self, parent):
        from carbonui.primitives.containerAutoSize import ContainerAutoSize
        COLORS = (eveColor.SAND_YELLOW,
         eveColor.CHERRY_RED,
         eveColor.SUCCESS_GREEN,
         eveColor.PRIMARY_BLUE)
        mainCont = ContainerAutoSize(name='mainCont', parent=parent, align=uiconst.TOPLEFT, bgColor=eveColor.MATTE_BLACK, width=300)
        for i, color in enumerate(COLORS):
            Container(parent=mainCont, align=uiconst.TOTOP, height=60, padding=8, bgColor=color)


class Sample2(Sample):
    name = 'Using alignMode'
    description = 'Passing in an alignMode argument will ignore any children not complying with that alignment in the context of auto-sizing'

    def sample_code(self, parent):
        from carbonui.primitives.containerAutoSize import ContainerAutoSize
        COLORS = (eveColor.SAND_YELLOW,
         eveColor.CHERRY_RED,
         eveColor.SUCCESS_GREEN,
         eveColor.PRIMARY_BLUE)
        mainCont = ContainerAutoSize(name='mainCont', parent=parent, align=uiconst.TOPLEFT, alignMode=uiconst.TOTOP, bgColor=eveColor.MATTE_BLACK, width=300)
        Container(name='centerCont', parent=mainCont, align=uiconst.CENTER, width=60, height=60, bgColor=eveColor.WARNING_ORANGE)
        for i, color in enumerate(COLORS):
            Container(parent=mainCont, align=uiconst.TOTOP, height=60, padding=8, bgColor=color)
