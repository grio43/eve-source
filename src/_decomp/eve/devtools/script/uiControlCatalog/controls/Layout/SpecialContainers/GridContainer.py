#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\SpecialContainers\GridContainer.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from eve.devtools.script.uiControlCatalog.sample import Sample
from eve.devtools.script.uiControlCatalog.sampleUtil import GetCollapsableCont

class Sample1(Sample):
    name = 'TOTOP aligned'
    description = "GridContainer will share it's available space evenly between it's lines and columns"

    def construct_sample(self, parent):
        cont = GetCollapsableCont(parent, width=300, height=200)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.gridcontainer import GridContainer
        myGridCont = GridContainer(name='myGridCont', parent=parent, align=uiconst.TOTOP, height=100, contentSpacing=(4, 4), columns=2)
        for i in xrange(6):
            alpha = 0.2 + i * 0.1
            Container(parent=myGridCont, bgColor=(0.8,
             0.2,
             0.4,
             alpha), state=uiconst.UI_NORMAL)


class Sample2(Sample):
    name = 'TOLEFT_PROP aligned'

    def construct_sample(self, parent):
        cont = GetCollapsableCont(parent, width=300, height=200)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.gridcontainer import GridContainer
        myGridCont = GridContainer(name='myGridCont', parent=parent, align=uiconst.TOLEFT_PROP, width=0.66, contentSpacing=(4, 4), columns=2)
        for i in xrange(9):
            alpha = 0.2 + i * 0.1
            Container(parent=myGridCont, bgColor=(0.8,
             0.2,
             0.4,
             alpha), state=uiconst.UI_NORMAL)


class Sample3(Sample):
    name = 'TOALL aligned'

    def construct_sample(self, parent):
        cont = GetCollapsableCont(parent, width=300, height=200)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.gridcontainer import GridContainer
        myGridCont = GridContainer(name='myGridCont', parent=parent, align=uiconst.TOALL, contentSpacing=(4, 4), lines=3)
        for i in xrange(6):
            alpha = 0.2 + i * 0.1
            Container(parent=myGridCont, bgColor=(0.8,
             0.2,
             0.4,
             alpha), state=uiconst.UI_NORMAL)
