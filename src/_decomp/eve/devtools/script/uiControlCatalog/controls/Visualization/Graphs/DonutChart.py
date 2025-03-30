#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Graphs\DonutChart.py
from eve.client.script.ui import eveColor
from carbonui import uiconst
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from eve.client.script.ui.control.donutChart import DonutChart
        donutChart = DonutChart(align=uiconst.CENTER, parent=parent, lineWidth=20, radius=100, gapSize=0.0)
        for i, value in enumerate((0.1, 0.1, 0.2, 1, 2, 3, 4, 5)):
            donutChart.AddSegment(value=value, segmentID=i)

        donutChart.Construct(animate=True, animDuration=0.6)


class Sample2(Sample):
    name = 'With gaps'

    def sample_code(self, parent):
        from eve.client.script.ui.control.donutChart import DonutChart
        donutChart = DonutChart(align=uiconst.CENTER, parent=parent, lineWidth=10, radius=100, color=eveColor.DANGER_RED, gapSize=0.02)
        for i, value in enumerate((1, 2, 3, 4, 5)):
            donutChart.AddSegment(value=value, segmentID=i)

        donutChart.Construct(animate=True, animDuration=0.6)
