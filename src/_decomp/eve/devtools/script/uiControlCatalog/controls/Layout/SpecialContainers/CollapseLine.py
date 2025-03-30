#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\SpecialContainers\CollapseLine.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample
COLLAPSE_PANEL_SIZE = 25

class Sample1(Sample):
    name = 'Horizontal'

    def construct_sample(self, parent):
        mainCont = Container(name='mainCont', parent=parent, align=uiconst.TOPLEFT, width=200, height=200)
        self.sample_code(mainCont)

    def sample_code(self, parent):
        from eve.client.script.ui.control.collapseLine import CollapseLine
        rightCont = Container(name='rightCont', parent=parent, align=uiconst.TORIGHT, width=COLLAPSE_PANEL_SIZE, bgColor=eveColor.PRIMARY_BLUE)
        CollapseLine(parent=parent, align=uiconst.TORIGHT, collapsingSection=rightCont, collapsingSectionWidth=COLLAPSE_PANEL_SIZE, settingKey='UI_catalog_collapse_line1')
        Container(name='toAllCont', parent=parent, align=uiconst.TOALL, bgColor=eveColor.GUNMETAL_GREY)


class Sample2(Sample):
    name = 'Vertical'

    def construct_sample(self, parent):
        mainCont = Container(name='mainCont', parent=parent, align=uiconst.TOPLEFT, width=200, height=200)
        self.sample_code(mainCont)

    def sample_code(self, parent):
        from eve.client.script.ui.control.collapseLine import CollapseLine
        bottomCont = Container(name='bottomCont', parent=parent, align=uiconst.TOBOTTOM, height=COLLAPSE_PANEL_SIZE, bgColor=eveColor.PRIMARY_BLUE)
        CollapseLine(parent=parent, align=uiconst.TOBOTTOM, collapsingSection=bottomCont, collapsingSectionWidth=COLLAPSE_PANEL_SIZE, settingKey='UI_catalog_collapse_line2')
        Container(name='toAllCont', parent=parent, align=uiconst.TOALL, bgColor=eveColor.GUNMETAL_GREY)
