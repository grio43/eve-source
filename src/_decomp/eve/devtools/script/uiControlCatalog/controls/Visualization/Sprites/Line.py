#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Sprites\Line.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = Line.__doc__

    def construct_sample(self, parent):
        mainCont = Container(name='mainCont', parent=parent, align=uiconst.TOPLEFT, width=200, height=100)
        self.sample_code(mainCont)

    def sample_code(self, parent):
        from carbonui.primitives.line import Line
        Line(parent=parent, align=uiconst.TOTOP, weight=1, padBottom=20, opacity=1.0)
        Line(parent=parent, align=uiconst.TOTOP, weight=2, padBottom=20, opacity=0.8)
        Line(parent=parent, align=uiconst.TOTOP, weight=3, padBottom=20, opacity=0.6)
        Line(parent=parent, align=uiconst.TOTOP, weight=4, padBottom=20, opacity=0.4)
        Line(parent=parent, align=uiconst.TOTOP, weight=5, opacity=0.2)
