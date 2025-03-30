#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\SpecialContainers\FlowContainer.py
import random
from carbonui import AxisAlignment, uiconst, TextBody
from carbonui.primitives.container import Container
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.combo import Combo
from eve.client.script.ui import eveColor
from eve.devtools.script.uiControlCatalog.sample import Sample
from eve.devtools.script.uiControlCatalog.sampleUtil import GetHorizCollapsableCont

class Sample1(Sample):
    name = 'Basic'
    description = 'Flow containers automatically align their children in lines, starting from top-left corner. All children must use the NOALIGN align mode.'

    def construct_sample(self, parent):
        cont = GetHorizCollapsableCont(parent, width=300, height=200)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.flowcontainer import FlowContainer
        myFlowCont = FlowContainer(name='myFlowCont', parent=parent, align=uiconst.TOTOP)
        for i in xrange(15):
            opacity = 0.2 + i * 0.1
            Container(parent=myFlowCont, padding=1, bgColor=(0.8,
             0.2,
             0.4,
             opacity), align=uiconst.NOALIGN, state=uiconst.UI_NORMAL, pos=(0, 0, 40, 40))


class Sample2(Sample):
    name = 'Playground'

    def construct_sample(self, parent):
        from carbonui.primitives.flowcontainer import FlowContainer
        main_cont = LayoutGrid(parent=parent, align=uiconst.CENTER, columns=2, cellSpacing=(32, 32))
        cont = GetHorizCollapsableCont(main_cont, width=300, height=200)
        flow_container = FlowContainer(name='flow_container', parent=cont, align=uiconst.TOTOP, contentSpacing=(5, 5), contentAlignment=AxisAlignment.CENTER, crossAxisAlignment=AxisAlignment.CENTER)
        for i in xrange(15):
            alpha = 0.2 + i * 0.1
            size = random.choice([10,
             15,
             20,
             25,
             30,
             35,
             40,
             45,
             50])
            Container(parent=flow_container, padding=1, bgColor=(0.8,
             0.2,
             0.4,
             alpha), align=uiconst.NOALIGN, state=uiconst.UI_NORMAL, pos=(0,
             0,
             size,
             size))

        control_cont = ContainerAutoSize(parent=main_cont, align=uiconst.TOPLEFT, width=160)

        def on_content_alignment_changed(combo, key, value):
            flow_container.contentAlignment = value

        TextBody(parent=control_cont, align=uiconst.TOTOP, padding=(0, 0, 0, 4), text='Content Alignment')
        Combo(parent=control_cont, align=uiconst.TOTOP, options=[('Start', AxisAlignment.START), ('CENTER', AxisAlignment.CENTER), ('END', AxisAlignment.END)], select=flow_container.contentAlignment, callback=on_content_alignment_changed)

        def on_cross_axis_alignment_changed(combo, key, value):
            flow_container.crossAxisAlignment = value

        TextBody(parent=control_cont, align=uiconst.TOTOP, padding=(0, 8, 0, 4), text='Cross Axis Alignment')
        Combo(parent=control_cont, align=uiconst.TOTOP, options=[('Start', AxisAlignment.START), ('CENTER', AxisAlignment.CENTER), ('END', AxisAlignment.END)], select=flow_container.crossAxisAlignment, callback=on_cross_axis_alignment_changed)


class Sample3(Sample):
    name = 'Auto height'
    description = "Passing in 'autoHeight=True' will automatically set the height of the FlowContainer to fit it's content like a ContainerAutoSize"

    def construct_sample(self, parent):
        cont = GetHorizCollapsableCont(parent, width=300, height=200)
        self.sample_code(cont)

    def sample_code(self, parent):
        from carbonui.primitives.flowcontainer import FlowContainer
        myFlowCont = FlowContainer(name='myFlowCont', parent=parent, align=uiconst.TOTOP, contentSpacing=(5, 5), autoHeight=True, bgColor=eveColor.SMOKE_BLUE)
        for i in xrange(20):
            alpha = 0.2 + i * 0.1
            size = random.choice([10, 20, 30])
            Container(parent=myFlowCont, padding=1, bgColor=(0.8,
             0.2,
             0.4,
             alpha), align=uiconst.NOALIGN, state=uiconst.UI_NORMAL, pos=(0,
             0,
             size,
             size))
